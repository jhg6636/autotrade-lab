"""Bounded Toss market-data observations for Gate D2.

The probe records provider behavior; it does not turn observations into documented contracts.
It never calls account, holdings, order, or trading endpoints and performs no retries.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from autotrade_lab.data_probe import (
    Transport,
    _canonical_json_bytes,
    _reject_echoed_secret,
    _selected_headers,
    _write_new,
    issue_toss_access_token,
    load_toss_client_credentials,
    public_transport,
)

MAX_MARKET_DATA_REQUESTS = 12
MAX_CANDLE_ROWS = 800
MAX_ARTIFACT_BYTES = 5 * 1024 * 1024
MASTER_WAIT_SECONDS = 1.1
CORPORATE_ACTION_SYMBOL = "005930"
CORPORATE_ACTION_BEFORE = "2018-05-10T00:00:00+09:00"
CALENDAR_DATE = "2018-05-04"
BASE_URL = "https://openapi.tossinvest.com"


@dataclass(frozen=True, slots=True)
class ObservationRequest:
    request_id: str
    path: str
    params: tuple[tuple[str, str], ...]
    max_candle_rows: int = 0

    @property
    def url(self) -> str:
        return f"{BASE_URL}{self.path}?{urllib.parse.urlencode(self.params)}"


def _request(
    item: ObservationRequest,
    access_token: str,
    *,
    transport: Transport,
    output_dir: Path,
    ordinal: int,
    raw_bytes: int,
    now: datetime,
) -> tuple[dict[str, Any], Any | None, int]:
    if item.path not in {
        "/api/v1/candles",
        "/api/v1/stocks/all",
        "/api/v1/stocks",
        "/api/v1/market-calendar/KR",
    }:
        raise ValueError(f"Gate D2 endpoint is not allowlisted: {item.path}")
    request = urllib.request.Request(
        item.url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "autotrade-lab-gate-d2/1",
        },
        method="GET",
    )
    if request.get_header("X-tossinvest-account") is not None:
        raise RuntimeError("account header is forbidden in Gate D2")
    record: dict[str, Any] = {
        "attempt_ordinal": ordinal,
        "request_id": item.request_id,
        "path": item.path,
        "params": dict(item.params),
        "requested_at": now.isoformat().replace("+00:00", "Z"),
        "status": None,
        "headers": {},
        "raw_path": None,
        "response_bytes": 0,
        "response_sha256": None,
        "observed_candle_rows": 0,
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
        raise RuntimeError("Gate D2 artifact byte budget exceeded")
    payload = None
    if body:
        _reject_echoed_secret(body, access_token)
        raw_path = Path("raw") / f"{ordinal:02d}_{item.request_id}.json"
        _write_new(output_dir / raw_path, body)
        record["raw_path"] = raw_path.as_posix()
        record["response_bytes"] = len(body)
        record["response_sha256"] = hashlib.sha256(body).hexdigest()
        raw_bytes += len(body)
        if record["status"] == 200:
            try:
                payload = json.loads(body)
                if item.path == "/api/v1/candles":
                    candles = payload["result"]["candles"]
                    if not isinstance(candles, list) or len(candles) > item.max_candle_rows:
                        raise RuntimeError(f"{item.request_id} exceeded its candle row budget")
                    record["observed_candle_rows"] = len(candles)
            except (KeyError, TypeError, json.JSONDecodeError) as error:
                record["error"] = f"parse error: {error}"
                payload = None
    return record, payload, raw_bytes


def _first_page(interval: str) -> ObservationRequest:
    return ObservationRequest(
        request_id=f"pagination_{interval}_page_1",
        path="/api/v1/candles",
        params=(
            ("symbol", "005930"),
            ("interval", interval),
            ("count", "100"),
            ("adjusted", "true"),
        ),
        max_candle_rows=100,
    )


def _second_page(interval: str, before: str) -> ObservationRequest:
    return ObservationRequest(
        request_id=f"pagination_{interval}_page_2",
        path="/api/v1/candles",
        params=(
            ("symbol", "005930"),
            ("interval", interval),
            ("count", "100"),
            ("adjusted", "true"),
            ("before", before),
        ),
        max_candle_rows=100,
    )


def _static_requests() -> tuple[ObservationRequest, ...]:
    result = [
        ObservationRequest(
            request_id=f"corporate_action_{adjustment}",
            path="/api/v1/candles",
            params=(
                ("symbol", CORPORATE_ACTION_SYMBOL),
                ("interval", "1d"),
                ("count", "200"),
                ("adjusted", adjusted),
                ("before", CORPORATE_ACTION_BEFORE),
            ),
            max_candle_rows=200,
        )
        for adjustment, adjusted in (("adjusted", "true"), ("unadjusted", "false"))
    ]
    result.extend(
        ObservationRequest(
            request_id=f"master_{market.lower()}_{status.lower()}",
            path="/api/v1/stocks/all",
            params=(("market", market), ("status", status)),
        )
        for market in ("KOSPI", "KOSDAQ")
        for status in ("ACTIVE", "DELISTED")
    )
    return tuple(result)


def collect_gate_d2(
    output_dir: Path,
    *,
    access_token: str,
    transport: Transport | None = None,
    wait=time.sleep,
    now=lambda: datetime.now(UTC),
    oauth_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the exact 12-request Gate D2 observation plan once."""

    if not access_token or "\r" in access_token or "\n" in access_token:
        raise ValueError("invalid Toss access token")
    output_dir.mkdir(parents=True, exist_ok=False)
    transport = transport or public_transport()
    records: list[dict[str, Any]] = []
    raw_bytes = 0
    candle_rows = 0
    delisted_symbols: list[str] = []

    def run(item: ObservationRequest) -> Any | None:
        nonlocal raw_bytes, candle_rows
        record, payload, raw_bytes = _request(
            item,
            access_token,
            transport=transport,
            output_dir=output_dir,
            ordinal=len(records) + 1,
            raw_bytes=raw_bytes,
            now=now(),
        )
        records.append(record)
        candle_rows += record["observed_candle_rows"]
        if candle_rows > MAX_CANDLE_ROWS or len(records) > MAX_MARKET_DATA_REQUESTS:
            raise RuntimeError("Gate D2 request or candle row budget exceeded")
        return payload

    for interval in ("1m", "1d"):
        first = run(_first_page(interval))
        cursor = first.get("result", {}).get("nextBefore") if isinstance(first, dict) else None
        if not isinstance(cursor, str) or not cursor:
            raise RuntimeError(f"{interval} first page did not provide a usable nextBefore cursor")
        run(_second_page(interval, cursor))

    for item in _static_requests():
        if item.path == "/api/v1/stocks/all" and any(
            record["path"] == "/api/v1/stocks/all" for record in records
        ):
            wait(MASTER_WAIT_SECONDS)
        payload = run(item)
        if item.path == "/api/v1/stocks/all" and item.params[-1][1] == "DELISTED":
            result = payload.get("result") if isinstance(payload, dict) else None
            if isinstance(result, list):
                delisted_symbols.extend(
                    row["symbol"]
                    for row in result
                    if isinstance(row, dict) and isinstance(row.get("symbol"), str)
                )

    selected_delisted = min(delisted_symbols) if delisted_symbols else None
    detail_symbols = ["005930"]
    if selected_delisted is not None:
        detail_symbols.append(selected_delisted)
    run(
        ObservationRequest(
            request_id="selected_stock_details",
            path="/api/v1/stocks",
            params=(("symbols", ",".join(detail_symbols)),),
        )
    )
    run(
        ObservationRequest(
            request_id="historical_market_calendar",
            path="/api/v1/market-calendar/KR",
            params=(("date", CALENDAR_DATE),),
        )
    )
    if len(records) != MAX_MARKET_DATA_REQUESTS:
        raise RuntimeError("Gate D2 did not attempt exactly 12 market-data requests")
    manifest = {
        "schema_version": 1,
        "probe": "gate-d2-toss-observed-contract",
        "created_at": now().isoformat().replace("+00:00", "Z"),
        "evidence_status": "observed",
        "authorization": "client credentials used locally; credentials and bearer token not retained",
        "oauth": oauth_metadata
        or {"attempted": False, "credentials_persisted": False, "token_persisted": False},
        "limits": {
            "market_data_requests": MAX_MARKET_DATA_REQUESTS,
            "candle_rows": MAX_CANDLE_ROWS,
            "artifact_bytes": MAX_ARTIFACT_BYTES,
            "retries": 0,
        },
        "preselected": {
            "pagination_symbol": "005930",
            "corporate_action_symbol": CORPORATE_ACTION_SYMBOL,
            "corporate_action": "Samsung Electronics 50-for-1 split; trading resumed 2018-05-04",
            "corporate_action_before": CORPORATE_ACTION_BEFORE,
            "calendar_date": CALENDAR_DATE,
        },
        "selected_delisted_symbol": selected_delisted,
        "observed": {
            "attempted_requests": len(records),
            "successful_requests": sum(
                record["status"] == 200 and record["error"] is None for record in records
            ),
            "candle_rows": candle_rows,
            "raw_response_bytes": raw_bytes,
        },
        "requests": records,
    }
    encoded = _canonical_json_bytes(manifest)
    if raw_bytes + len(encoded) > MAX_ARTIFACT_BYTES:
        raise RuntimeError("Gate D2 manifest exceeds artifact byte budget")
    _write_new(output_dir / "manifest.json", encoded)
    return manifest


def verify_gate_d2(run_dir: Path) -> dict[str, Any]:
    """Verify tracked metadata against the local ignored raw evidence."""

    manifest = json.loads((run_dir / "manifest.json").read_bytes())
    records = manifest.get("requests")
    if (
        manifest.get("probe") != "gate-d2-toss-observed-contract"
        or manifest.get("evidence_status") != "observed"
        or not isinstance(records, list)
        or len(records) != MAX_MARKET_DATA_REQUESTS
    ):
        raise ValueError("invalid Gate D2 manifest")
    expected_ids = [
        "pagination_1m_page_1",
        "pagination_1m_page_2",
        "pagination_1d_page_1",
        "pagination_1d_page_2",
        "corporate_action_adjusted",
        "corporate_action_unadjusted",
        "master_kospi_active",
        "master_kospi_delisted",
        "master_kosdaq_active",
        "master_kosdaq_delisted",
        "selected_stock_details",
        "historical_market_calendar",
    ]
    if [record.get("request_id") for record in records] != expected_ids:
        raise ValueError("Gate D2 request plan does not match the approved order")
    raw_bytes = 0
    candle_rows = 0
    for record in records:
        raw_path = record.get("raw_path")
        if not isinstance(raw_path, str) or not raw_path.startswith("raw/"):
            raise ValueError("Gate D2 request is missing an allowlisted raw path")
        path = run_dir / raw_path
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != record.get("response_sha256"):
            raise ValueError(f"Gate D2 raw checksum mismatch: {record.get('request_id')}")
        if len(body) != record.get("response_bytes"):
            raise ValueError(f"Gate D2 raw byte count mismatch: {record.get('request_id')}")
        if record.get("status") != 200 or record.get("error") is not None:
            raise ValueError(f"Gate D2 request was not successful: {record.get('request_id')}")
        payload = json.loads(body)
        observed_rows = record.get("observed_candle_rows")
        if record.get("path") == "/api/v1/candles":
            actual_rows = len(payload["result"]["candles"])
            if actual_rows != observed_rows:
                raise ValueError(f"Gate D2 candle row mismatch: {record.get('request_id')}")
        elif observed_rows != 0:
            raise ValueError(f"Gate D2 non-candle request reports rows: {record.get('request_id')}")
        raw_bytes += len(body)
        candle_rows += observed_rows
    observed = manifest.get("observed")
    if not isinstance(observed, dict) or observed != {
        "attempted_requests": MAX_MARKET_DATA_REQUESTS,
        "successful_requests": MAX_MARKET_DATA_REQUESTS,
        "candle_rows": candle_rows,
        "raw_response_bytes": raw_bytes,
    }:
        raise ValueError("Gate D2 observed summary is inconsistent")
    if candle_rows > MAX_CANDLE_ROWS or raw_bytes > MAX_ARTIFACT_BYTES:
        raise RuntimeError("Gate D2 evidence exceeds its recorded budget")
    return observed


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--credentials-file", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        if args.credentials_file is not None:
            parser.error("--credentials-file cannot be used with --verify")
        print(json.dumps(verify_gate_d2(args.output_dir), indent=2, sort_keys=True))
        return
    if args.credentials_file is None:
        parser.error("--credentials-file is required for collection")
    client_id, client_secret = load_toss_client_credentials(args.credentials_file)
    token, oauth_metadata = issue_toss_access_token(client_id, client_secret)
    result = collect_gate_d2(
        args.output_dir,
        access_token=token,
        oauth_metadata=oauth_metadata,
    )
    print(json.dumps(result["observed"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
