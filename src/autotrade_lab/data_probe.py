"""Fail-closed, bounded market-data capability probes.

This module intentionally knows only the public endpoints approved by the Gate C contract. It has
no account, credential, or order support and performs no retries.
"""

from __future__ import annotations

import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any, Protocol, Self

MAX_REQUESTS = 29
MAX_ROWS = 10_600
MAX_ARTIFACT_BYTES = 25 * 1024 * 1024
CRYPTO_REQUESTS = 12
CRYPTO_MAX_ROWS = 8_800
SCHEMA_VERSION = 1

_SELECTED_HEADERS = {
    "content-length",
    "content-type",
    "date",
    "remaining-req",
    "retry-after",
    "x-mbx-used-weight-1m",
    "x-response-time",
}


@dataclass(frozen=True, slots=True)
class ProbeRequest:
    request_id: str
    provider: str
    venue: str
    instrument_type: str
    symbol: str
    interval: str
    base_url: str
    params: tuple[tuple[str, str], ...]
    max_rows: int

    @property
    def url(self) -> str:
        return f"{self.base_url}?{urllib.parse.urlencode(self.params)}"


def crypto_probe_requests() -> tuple[ProbeRequest, ...]:
    requests: list[ProbeRequest] = []
    for symbol in ("KRW-BTC", "KRW-ETH"):
        for interval, path in (("1h", "minutes/60"), ("1d", "days")):
            requests.append(
                ProbeRequest(
                    request_id=f"upbit_spot_{symbol.lower().replace('-', '_')}_{interval}",
                    provider="upbit",
                    venue="upbit_kr",
                    instrument_type="spot",
                    symbol=symbol,
                    interval=interval,
                    base_url=f"https://api.upbit.com/v1/candles/{path}",
                    params=(("market", symbol), ("count", "200")),
                    max_rows=200,
                )
            )
    for instrument_type, venue, base_url in (
        ("spot", "binance_spot", "https://data-api.binance.vision/api/v3/klines"),
        ("perpetual", "binance_usdm", "https://fapi.binance.com/fapi/v1/klines"),
    ):
        for symbol in ("BTCUSDT", "ETHUSDT"):
            for interval in ("1h", "1d"):
                requests.append(
                    ProbeRequest(
                        request_id=f"binance_{instrument_type}_{symbol.lower()}_{interval}",
                        provider="binance",
                        venue=venue,
                        instrument_type=instrument_type,
                        symbol=symbol,
                        interval=interval,
                        base_url=base_url,
                        params=(("symbol", symbol), ("interval", interval), ("limit", "1000")),
                        max_rows=1000,
                    )
                )
    result = tuple(requests)
    validate_crypto_plan(result)
    return result


def validate_crypto_plan(requests: tuple[ProbeRequest, ...]) -> None:
    if len(requests) != CRYPTO_REQUESTS:
        raise ValueError(f"crypto probe must contain exactly {CRYPTO_REQUESTS} requests")
    if sum(item.max_rows for item in requests) > CRYPTO_MAX_ROWS:
        raise ValueError("crypto row budget exceeded")
    if len({item.request_id for item in requests}) != len(requests):
        raise ValueError("request IDs must be unique")
    for item in requests:
        parsed = urllib.parse.urlparse(item.base_url)
        allowed = {
            ("api.upbit.com", "/v1/candles/minutes/60"),
            ("api.upbit.com", "/v1/candles/days"),
            ("data-api.binance.vision", "/api/v3/klines"),
            ("fapi.binance.com", "/fapi/v1/klines"),
        }
        if parsed.scheme != "https" or (parsed.hostname, parsed.path) not in allowed:
            raise ValueError(f"endpoint is not allowlisted: {item.base_url}")
        if parsed.username or parsed.password or parsed.fragment:
            raise ValueError("endpoint must not contain credentials or fragments")


class ResponseLike(Protocol):
    headers: Any
    status: int

    def read(self, amount: int = -1) -> bytes: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, *args: object) -> None: ...


class Transport(Protocol):
    def open(self, request: urllib.request.Request, *, timeout: float) -> ResponseLike: ...


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def public_transport() -> Transport:
    return urllib.request.build_opener(_NoRedirect)


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _selected_headers(headers: Any) -> dict[str, str]:
    return {
        key.lower(): value for key, value in headers.items() if key.lower() in _SELECTED_HEADERS
    }


def _write_new(path: Path, body: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(body)


def collect_crypto(
    output_dir: Path,
    *,
    transport: Transport | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Attempt every approved public crypto request exactly once and persist immutable raw bytes."""

    requests = crypto_probe_requests()
    transport = transport or public_transport()
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest_items: list[dict[str, Any]] = []
    raw_bytes = 0
    observed_rows = 0

    for ordinal, item in enumerate(requests, start=1):
        requested_at = now().isoformat().replace("+00:00", "Z")
        request = urllib.request.Request(
            item.url,
            headers={"Accept": "application/json", "User-Agent": "autotrade-lab-gate-c/1"},
            method="GET",
        )
        record: dict[str, Any] = {
            **asdict(item),
            "params": dict(item.params),
            "attempt_ordinal": ordinal,
            "requested_at": requested_at,
            "url": item.url,
            "status": None,
            "headers": {},
            "raw_path": None,
            "response_bytes": 0,
            "response_sha256": None,
            "observed_rows": 0,
            "error": None,
        }
        body = b""
        try:
            with transport.open(request, timeout=30.0) as response:
                body = response.read(MAX_ARTIFACT_BYTES + 1)
                record["status"] = response.status
                record["headers"] = _selected_headers(response.headers)
        except urllib.error.HTTPError as error:
            body = error.read(MAX_ARTIFACT_BYTES + 1)
            record["status"] = error.code
            record["headers"] = _selected_headers(error.headers)
            record["error"] = f"HTTP {error.code}: {error.reason}"
        except urllib.error.URLError as error:
            record["error"] = f"network error: {error.reason}"

        if len(body) > MAX_ARTIFACT_BYTES or raw_bytes + len(body) > MAX_ARTIFACT_BYTES:
            raise RuntimeError("artifact byte budget exceeded while reading response")
        if body:
            raw_path = Path("raw") / f"{ordinal:02d}_{item.request_id}.json"
            _write_new(output_dir / raw_path, body)
            record["raw_path"] = raw_path.as_posix()
            record["response_bytes"] = len(body)
            record["response_sha256"] = _sha256(body)
            raw_bytes += len(body)
            if record["status"] == 200:
                try:
                    payload = json.loads(body)
                    if not isinstance(payload, list):
                        raise TypeError("response is not a list")
                except (json.JSONDecodeError, TypeError) as error:
                    record["error"] = f"parse error: {error}"
                else:
                    if len(payload) > item.max_rows:
                        raise RuntimeError(f"{item.request_id} exceeded its row budget")
                    record["observed_rows"] = len(payload)
                    observed_rows += len(payload)
        manifest_items.append(record)

    if len(manifest_items) != CRYPTO_REQUESTS or observed_rows > CRYPTO_MAX_ROWS:
        raise RuntimeError("crypto request or row budget invariant failed")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "probe": "gate-c-public-crypto",
        "created_at": now().isoformat().replace("+00:00", "Z"),
        "limits": {
            "gate_c_max_requests": MAX_REQUESTS,
            "gate_c_max_rows": MAX_ROWS,
            "gate_c_max_artifact_bytes": MAX_ARTIFACT_BYTES,
            "phase_max_requests": CRYPTO_REQUESTS,
            "phase_max_rows": CRYPTO_MAX_ROWS,
        },
        "observed": {
            "attempted_requests": len(manifest_items),
            "successful_requests": sum(
                item["status"] == 200 and item["error"] is None for item in manifest_items
            ),
            "rows": observed_rows,
            "raw_response_bytes": raw_bytes,
        },
        "requests": manifest_items,
    }
    encoded = _canonical_json_bytes(manifest)
    if raw_bytes + len(encoded) > MAX_ARTIFACT_BYTES:
        raise RuntimeError("artifact byte budget exceeded by manifest")
    _write_new(output_dir / "manifest.json", encoded)
    return manifest


def _interval_ms(interval: str) -> int:
    return {"1h": 3_600_000, "1d": 86_400_000}[interval]


def _iso_utc_ms(value: str) -> int:
    parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    return int(parsed.timestamp() * 1000)


def _upbit_rows(record: dict[str, Any], payload: list[Any]) -> list[dict[str, Any]]:
    step = _interval_ms(record["interval"])
    fetched_at = _iso_utc_ms(record["requested_at"])
    rows = []
    for item in payload:
        open_time = _iso_utc_ms(item["candle_date_time_utc"] + "Z")
        close_time = open_time + step - 1
        rows.append(
            {
                "provider": record["provider"],
                "venue": record["venue"],
                "instrument_type": record["instrument_type"],
                "symbol": record["symbol"],
                "interval": record["interval"],
                "open_time": open_time,
                "close_time": close_time,
                "open": float(item["opening_price"]),
                "high": float(item["high_price"]),
                "low": float(item["low_price"]),
                "close": float(item["trade_price"]),
                "volume": float(item["candle_acc_trade_volume"]),
                "quote_volume": float(item["candle_acc_trade_price"]),
                "trade_count": None,
                "complete": close_time <= fetched_at,
                "adjustment_state": "not_applicable",
                "raw_sha256": record["response_sha256"],
            }
        )
    return rows


def _binance_rows(record: dict[str, Any], payload: list[Any]) -> list[dict[str, Any]]:
    fetched_at = _iso_utc_ms(record["requested_at"])
    rows = []
    for item in payload:
        if not isinstance(item, list) or len(item) < 11:
            raise ValueError(f"invalid Binance kline in {record['request_id']}")
        rows.append(
            {
                "provider": record["provider"],
                "venue": record["venue"],
                "instrument_type": record["instrument_type"],
                "symbol": record["symbol"],
                "interval": record["interval"],
                "open_time": int(item[0]),
                "close_time": int(item[6]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
                "quote_volume": float(item[7]),
                "trade_count": int(item[8]),
                "complete": int(item[6]) <= fetched_at,
                "adjustment_state": "not_applicable",
                "raw_sha256": record["response_sha256"],
            }
        )
    return rows


def validate_manifest(manifest: dict[str, Any]) -> None:
    expected = crypto_probe_requests()
    records = manifest.get("requests")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("probe") != (
        "gate-c-public-crypto"
    ):
        raise ValueError("unsupported probe manifest")
    if not isinstance(records, list) or len(records) != CRYPTO_REQUESTS:
        raise ValueError("manifest must contain exactly 12 request records")
    observed_rows = 0
    for ordinal, (record, item) in enumerate(zip(records, expected, strict=True), start=1):
        expected_values = {
            "request_id": item.request_id,
            "provider": item.provider,
            "venue": item.venue,
            "instrument_type": item.instrument_type,
            "symbol": item.symbol,
            "interval": item.interval,
            "base_url": item.base_url,
            "params": dict(item.params),
            "max_rows": item.max_rows,
            "attempt_ordinal": ordinal,
            "url": item.url,
        }
        if any(record.get(key) != value for key, value in expected_values.items()):
            raise ValueError(f"manifest request does not match allowlist: {item.request_id}")
        expected_raw_path = f"raw/{ordinal:02d}_{item.request_id}.json"
        if record.get("raw_path") not in {None, expected_raw_path}:
            raise ValueError(f"unexpected raw path: {record.get('raw_path')}")
        row_count = record.get("observed_rows")
        if not isinstance(row_count, int) or not 0 <= row_count <= item.max_rows:
            raise ValueError(f"invalid observed row count: {item.request_id}")
        observed_rows += row_count
    if observed_rows > CRYPTO_MAX_ROWS:
        raise ValueError("manifest exceeds crypto row budget")
    observed = manifest.get("observed", {})
    if (
        observed.get("attempted_requests") != CRYPTO_REQUESTS
        or observed.get("rows") != observed_rows
    ):
        raise ValueError("manifest observed summary is inconsistent")


def load_normalized_rows(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_bytes = (run_dir / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    rows: list[dict[str, Any]] = []
    for record in manifest["requests"]:
        if record["status"] != 200 or record["error"] is not None or not record["raw_path"]:
            continue
        raw = (run_dir / record["raw_path"]).read_bytes()
        if _sha256(raw) != record["response_sha256"]:
            raise ValueError(f"raw checksum mismatch: {record['request_id']}")
        payload = json.loads(raw)
        if record["provider"] == "upbit":
            rows.extend(_upbit_rows(record, payload))
        elif record["provider"] == "binance":
            rows.extend(_binance_rows(record, payload))
        else:
            raise ValueError(f"unsupported provider: {record['provider']}")
    key = lambda item: (
        item["provider"],
        item["venue"],
        item["instrument_type"],
        item["symbol"],
        item["interval"],
        item["open_time"],
        item["adjustment_state"],
    )
    rows.sort(key=key)
    return manifest, rows


def _build_parquet(rows: list[dict[str, Any]]) -> tuple[bytes, str]:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as error:  # pragma: no cover - exercised by environment setup
        raise RuntimeError("install the 'data' extra to produce Parquet") from error

    schema = pa.schema(
        [
            ("provider", pa.string()),
            ("venue", pa.string()),
            ("instrument_type", pa.string()),
            ("symbol", pa.string()),
            ("interval", pa.string()),
            ("open_time", pa.timestamp("ms", tz="UTC")),
            ("close_time", pa.timestamp("ms", tz="UTC")),
            ("open", pa.float64()),
            ("high", pa.float64()),
            ("low", pa.float64()),
            ("close", pa.float64()),
            ("volume", pa.float64()),
            ("quote_volume", pa.float64()),
            ("trade_count", pa.int64()),
            ("complete", pa.bool_()),
            ("adjustment_state", pa.string()),
            ("raw_sha256", pa.string()),
        ]
    )
    columns = {field.name: [row[field.name] for row in rows] for field in schema}
    table = pa.Table.from_pydict(columns, schema=schema)
    sink = pa.BufferOutputStream()
    pq.write_table(
        table,
        sink,
        compression="zstd",
        version="2.6",
        use_dictionary=False,
        write_statistics=True,
        data_page_version="2.0",
    )
    return sink.getvalue().to_pybytes(), pa.__version__


def _quality_report(
    manifest: dict[str, Any], rows: list[dict[str, Any]], parquet: bytes, pyarrow_version: str
) -> dict[str, Any]:
    identity = lambda row: (
        row["provider"],
        row["venue"],
        row["instrument_type"],
        row["symbol"],
        row["interval"],
        row["open_time"],
        row["adjustment_state"],
    )
    duplicate_keys = len(rows) - len({identity(row) for row in rows})
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for row in rows:
        group_key = (
            row["provider"],
            row["venue"],
            row["instrument_type"],
            row["symbol"],
            row["interval"],
        )
        grouped.setdefault(group_key, []).append(row)
    datasets = []
    for group_key, items in sorted(grouped.items()):
        times = sorted({item["open_time"] for item in items})
        step = _interval_ms(group_key[-1])
        deltas = [right - left for left, right in pairwise(times)]
        missing = sum(max(math.floor(delta / step) - 1, 0) for delta in deltas)
        datasets.append(
            {
                "provider": group_key[0],
                "venue": group_key[1],
                "instrument_type": group_key[2],
                "symbol": group_key[3],
                "interval": group_key[4],
                "rows": len(items),
                "first_open_time": datetime.fromtimestamp(times[0] / 1000, UTC).isoformat(),
                "last_open_time": datetime.fromtimestamp(times[-1] / 1000, UTC).isoformat(),
                "duplicate_keys": len(items) - len(times),
                "missing_intervals": missing,
                "non_grid_deltas": sum(delta % step != 0 for delta in deltas),
                "incomplete_rows": sum(not item["complete"] for item in items),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "probe": manifest["probe"],
        "source_manifest_sha256": _sha256(_canonical_json_bytes(manifest)),
        "pyarrow_version": pyarrow_version,
        "parquet_sha256": _sha256(parquet),
        "attempted_requests": len(manifest["requests"]),
        "successful_requests": sum(
            item["status"] == 200 and item["error"] is None for item in manifest["requests"]
        ),
        "failed_requests": sum(
            item["status"] != 200 or item["error"] is not None for item in manifest["requests"]
        ),
        "normalized_rows": len(rows),
        "duplicate_keys": duplicate_keys,
        "within_request_budget": len(manifest["requests"]) <= CRYPTO_REQUESTS,
        "within_row_budget": len(rows) <= CRYPTO_MAX_ROWS,
        "datasets": datasets,
        "retention_statement": (
            "Coverage bounds describe only returned sample rows; deeper retention was not inferred."
        ),
        "licensing_statement": (
            "Public endpoint access does not establish redistribution rights; provider terms remain "
            "a Gate C review item."
        ),
    }


def build_normalized_artifacts(run_dir: Path) -> tuple[bytes, bytes]:
    manifest, rows = load_normalized_rows(run_dir)
    if len(rows) > CRYPTO_MAX_ROWS:
        raise RuntimeError("normalized rows exceed crypto phase budget")
    parquet, pyarrow_version = _build_parquet(rows)
    report = _quality_report(manifest, rows, parquet, pyarrow_version)
    return parquet, _canonical_json_bytes(report)


def normalize_crypto(run_dir: Path) -> dict[str, Any]:
    parquet, report = build_normalized_artifacts(run_dir)
    normalized = run_dir / "normalized"
    normalized.mkdir(exist_ok=False)
    _write_new(normalized / "candles.parquet", parquet)
    _write_new(run_dir / "quality_report.json", report)
    total = sum(path.stat().st_size for path in run_dir.rglob("*") if path.is_file())
    if total > MAX_ARTIFACT_BYTES:
        raise RuntimeError("normalized run exceeds artifact budget")
    return json.loads(report)


def verify_crypto(run_dir: Path) -> dict[str, Any]:
    parquet, report = build_normalized_artifacts(run_dir)
    if (run_dir / "normalized/candles.parquet").read_bytes() != parquet:
        raise ValueError("Parquet is not byte-identical to raw normalization")
    if (run_dir / "quality_report.json").read_bytes() != report:
        raise ValueError("quality report is not byte-identical to raw normalization")
    total = sum(path.stat().st_size for path in run_dir.rglob("*") if path.is_file())
    if total > MAX_ARTIFACT_BYTES:
        raise RuntimeError("verified run exceeds artifact budget")
    return {"artifact_bytes": total, **json.loads(report)}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("collect-crypto")
    collect.add_argument("output_dir", type=Path)
    normalize = commands.add_parser("normalize-crypto")
    normalize.add_argument("run_dir", type=Path)
    verify = commands.add_parser("verify-crypto")
    verify.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    if args.command == "collect-crypto":
        result = collect_crypto(args.output_dir)
    elif args.command == "normalize-crypto":
        result = normalize_crypto(args.run_dir)
    else:
        result = verify_crypto(args.run_dir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
