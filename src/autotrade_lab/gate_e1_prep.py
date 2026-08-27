"""Fail-closed Gate E1 Korean daily-data feasibility collector.

This module defines the exact user-reviewable E1-DATA request table. It has no CLI and performs no
request unless ``collect_gate_e1_data`` is called with the current plan hash and a private service
key. It never accesses brokerage, account, order, or trading endpoints and performs no retries.
"""

from __future__ import annotations

import hashlib
import json
import socket
import ssl
import stat
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path
from typing import Any, Protocol, Self

MAX_REQUESTS = 24
MAX_ROWS = 1_200
MAX_RAW_BYTES = 5 * 1024 * 1024
MAX_SLOT_BYTES = 218_000
RECOVERY_MAX_RAW_BYTES = 65_536
ROWS_PER_REQUEST = 50
HTTP_TIMEOUT_SECONDS = 30.0
PROBE_DATE = "20260821"
SAMSUNG_ISIN = "KR7005930003"
SAMSUNG_CRNO = "1301110006246"
KOSDAQ_SENTINEL = "196170"
KODEX_200_ISIN = "KR7069500007"
HANJIN_SHIPPING_SHORT_CODE = "117930"

LISTED_BASE = "https://apis.data.go.kr/1160100/service/GetKrxListedInfoService"
PRICE_BASE = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService"
ISSUANCE_BASE = "https://apis.data.go.kr/1160100/GetStocIssuInfoService_V3"
DIVIDEND_BASE = "https://apis.data.go.kr/1160100/GetStocDiviInfoService_V2"

_ALLOWED_OPERATIONS = {
    ("apis.data.go.kr", "/1160100/service/GetKrxListedInfoService/getItemInfo"),
    ("apis.data.go.kr", "/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"),
    ("apis.data.go.kr", "/1160100/service/GetStockSecuritiesInfoService/getSecuritiesPriceInfo"),
    ("apis.data.go.kr", "/1160100/GetStocIssuInfoService_V3/getItemBasiInfo_V3"),
    ("apis.data.go.kr", "/1160100/GetStocIssuInfoService_V3/getStocIssuInfo_V3"),
    ("apis.data.go.kr", "/1160100/GetStocDiviInfoService_V2/getDiviInfo_V2"),
}
_SELECTED_HEADERS = {
    "content-length",
    "content-type",
    "date",
    "remaining-req",
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
}


class GateE1Stop(RuntimeError):
    """A fail-closed condition that forbids retries or further calls."""


@dataclass(frozen=True, slots=True)
class RequestSlot:
    request_id: str
    service: str
    base_url: str
    operation: str
    page_no: int
    filters: tuple[tuple[str, str], ...]
    max_rows: int = ROWS_PER_REQUEST
    max_response_bytes: int = MAX_SLOT_BYTES

    @property
    def safe_params(self) -> tuple[tuple[str, str], ...]:
        return (
            ("pageNo", str(self.page_no)),
            ("numOfRows", str(self.max_rows)),
            ("resultType", "json"),
            *self.filters,
        )

    @property
    def safe_record(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "service": self.service,
            "base_url": self.base_url,
            "operation": self.operation,
            "page_no": self.page_no,
            "num_of_rows": self.max_rows,
            "filters": dict(self.filters),
            "max_response_bytes": self.max_response_bytes,
        }

    def request(self, decoded_service_key: str) -> urllib.request.Request:
        _validate_service_key(decoded_service_key)
        query = urllib.parse.urlencode(
            (("serviceKey", decoded_service_key), *self.safe_params),
            quote_via=urllib.parse.quote,
        )
        return urllib.request.Request(
            f"{self.base_url}{self.operation}?{query}",
            headers={
                "Accept": "application/json",
                "User-Agent": "autotrade-lab-gate-e1/1",
            },
            method="GET",
        )


def _slot(
    request_id: str,
    service: str,
    base_url: str,
    operation: str,
    *,
    page_no: int = 1,
    **filters: str,
) -> RequestSlot:
    return RequestSlot(
        request_id=request_id,
        service=service,
        base_url=base_url,
        operation=operation,
        page_no=page_no,
        filters=tuple(filters.items()),
    )


def gate_e1_request_plan() -> tuple[RequestSlot, ...]:
    """Return the immutable 24-slot plan that requires a second user approval."""

    slots = (
        _slot(
            "listing_2009_boundary",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            basDt="20091231",
        ),
        _slot(
            "listing_2010_boundary",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            basDt="20100104",
        ),
        _slot(
            "listing_probe_page_1",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            basDt=PROBE_DATE,
        ),
        _slot(
            "listing_probe_page_2",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            page_no=2,
            basDt=PROBE_DATE,
        ),
        _slot(
            "listing_kosdaq_sentinel",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            basDt=PROBE_DATE,
            likeSrtnCd=KOSDAQ_SENTINEL,
        ),
        _slot(
            "listing_etf_sentinel",
            "listed_instruments",
            LISTED_BASE,
            "/getItemInfo",
            basDt=PROBE_DATE,
            isinCd=KODEX_200_ISIN,
        ),
        _slot(
            "stock_price_2009_boundary",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt="20091231",
        ),
        _slot(
            "stock_price_2010_boundary",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt="20100104",
        ),
        _slot(
            "stock_price_probe_page_1",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt=PROBE_DATE,
        ),
        _slot(
            "stock_price_probe_page_2",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            page_no=2,
            basDt=PROBE_DATE,
        ),
        _slot(
            "stock_price_samsung_pre_split",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt="20180427",
            isinCd=SAMSUNG_ISIN,
        ),
        _slot(
            "stock_price_samsung_post_split",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt="20180504",
            isinCd=SAMSUNG_ISIN,
        ),
        _slot(
            "stock_price_hanjin_last_trading_day",
            "stock_price",
            PRICE_BASE,
            "/getStockPriceInfo",
            basDt="20170306",
            likeSrtnCd=HANJIN_SHIPPING_SHORT_CODE,
        ),
        _slot(
            "etf_price_2010_boundary",
            "investment_security_price",
            PRICE_BASE,
            "/getSecuritiesPriceInfo",
            basDt="20100104",
            isinCd=KODEX_200_ISIN,
        ),
        _slot(
            "etf_price_probe_date",
            "investment_security_price",
            PRICE_BASE,
            "/getSecuritiesPriceInfo",
            basDt=PROBE_DATE,
            isinCd=KODEX_200_ISIN,
        ),
        _slot(
            "issuance_basic_probe_page",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getItemBasiInfo_V3",
            basDt=PROBE_DATE,
        ),
        _slot(
            "issuance_basic_2010_boundary",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getItemBasiInfo_V3",
            basDt="20100104",
        ),
        _slot(
            "issuance_basic_samsung_pre_split",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getItemBasiInfo_V3",
            basDt="20180427",
            crno=SAMSUNG_CRNO,
        ),
        _slot(
            "issuance_basic_samsung_post_split",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getItemBasiInfo_V3",
            basDt="20180504",
            crno=SAMSUNG_CRNO,
        ),
        _slot(
            "issuance_basic_hanjin_delist",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getItemBasiInfo_V3",
            basDt="20170307",
            stckIssuCmpyNm="(주)한진해운",
        ),
        _slot(
            "issuance_history_samsung_post_split",
            "stock_issuance",
            ISSUANCE_BASE,
            "/getStocIssuInfo_V3",
            basDt="20180504",
            crno=SAMSUNG_CRNO,
        ),
        _slot(
            "dividend_samsung_history",
            "stock_dividend",
            DIVIDEND_BASE,
            "/getDiviInfo_V2",
            crno=SAMSUNG_CRNO,
        ),
        _slot(
            "dividend_2010_boundary",
            "stock_dividend",
            DIVIDEND_BASE,
            "/getDiviInfo_V2",
            basDt="20100104",
        ),
        _slot(
            "dividend_probe_date",
            "stock_dividend",
            DIVIDEND_BASE,
            "/getDiviInfo_V2",
            basDt=PROBE_DATE,
        ),
    )
    validate_gate_e1_plan(slots)
    return slots


def validate_gate_e1_plan(slots: tuple[RequestSlot, ...]) -> None:
    if len(slots) != MAX_REQUESTS:
        raise ValueError(f"Gate E1 plan must contain exactly {MAX_REQUESTS} slots")
    if len({slot.request_id for slot in slots}) != len(slots):
        raise ValueError("Gate E1 request IDs must be unique")
    if sum(slot.max_rows for slot in slots) != MAX_ROWS:
        raise ValueError("Gate E1 row budget must be exactly 1,200")
    if sum(slot.max_response_bytes for slot in slots) > MAX_RAW_BYTES:
        raise ValueError("Gate E1 declared response-byte budget exceeds 5 MiB")
    allowed_page_two = {"listing_probe_page_2", "stock_price_probe_page_2"}
    actual_page_two = {slot.request_id for slot in slots if slot.page_no == 2}
    if actual_page_two != allowed_page_two or any(slot.page_no not in {1, 2} for slot in slots):
        raise ValueError("Gate E1 page-2 slots do not match the approved pagination checks")
    for slot in slots:
        parsed = urllib.parse.urlparse(f"{slot.base_url}{slot.operation}")
        if (
            parsed.scheme != "https"
            or (parsed.hostname, parsed.path) not in _ALLOWED_OPERATIONS
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(f"Gate E1 endpoint is not allowlisted: {slot.request_id}")
        keys = [key for key, _ in slot.safe_params]
        if len(keys) != len(set(keys)) or "serviceKey" in keys:
            raise ValueError(f"unsafe or duplicate parameter in {slot.request_id}")
        if slot.max_rows != ROWS_PER_REQUEST or slot.max_response_bytes <= 0:
            raise ValueError(f"invalid slot budget in {slot.request_id}")
        if not slot.filters:
            raise ValueError(f"unbounded Gate E1 slot: {slot.request_id}")


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def gate_e1_plan_sha256(slots: tuple[RequestSlot, ...] | None = None) -> str:
    slots = slots or gate_e1_request_plan()
    return hashlib.sha256(_canonical_json_bytes([slot.safe_record for slot in slots])).hexdigest()


def _validate_service_key(value: str) -> None:
    if (
        not value
        or len(value) > 512
        or value.strip() != value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ValueError("invalid decoded Public Data Portal service key")


def _secret_variants(value: str) -> tuple[bytes, ...]:
    return tuple(
        variant.encode()
        for variant in {
            value,
            urllib.parse.quote(value, safe=""),
            urllib.parse.quote_plus(value, safe=""),
        }
    )


def load_public_data_service_key(path: Path) -> str:
    """Load exactly one decoded key from a private, non-symlink file."""

    if path.is_symlink() or not path.is_file():
        raise ValueError("service-key path must be a regular non-symlink file")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise PermissionError("service-key file must not be accessible by group or others")
    lines = [line for line in path.read_text().splitlines() if line and not line.startswith("#")]
    if len(lines) != 1 or not lines[0].startswith("PUBLIC_DATA_SERVICE_KEY_DECODED="):
        raise ValueError("service-key file must contain exactly PUBLIC_DATA_SERVICE_KEY_DECODED")
    key = lines[0].split("=", 1)[1]
    _validate_service_key(key)
    return key


class ResponseLike(Protocol):
    headers: Message
    status: int

    def read(self, amount: int = -1) -> bytes: ...

    def geturl(self) -> str: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, *args: object) -> None: ...


class Transport(Protocol):
    def open(self, request: urllib.request.Request, *, timeout: float) -> ResponseLike: ...


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


class _PublicTransport:
    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(_RejectRedirect())

    def open(self, request: urllib.request.Request, *, timeout: float) -> ResponseLike:
        return self._opener.open(request, timeout=timeout)


def _read_bounded(response: ResponseLike, *, slot_limit: int, remaining: int) -> bytes:
    allowed = min(slot_limit, remaining)
    raw_length = response.headers.get("Content-Length")
    if raw_length is not None:
        try:
            declared = int(raw_length)
        except ValueError as error:
            raise GateE1Stop("invalid Content-Length; stop without retry") from error
        if declared < 0 or declared > allowed:
            raise GateE1Stop("declared response exceeds byte budget; stop without retry")
    chunks: list[bytes] = []
    retained = 0
    while retained < allowed:
        requested = min(65_536, allowed - retained)
        chunk = response.read(requested)
        if not chunk:
            break
        if len(chunk) > requested:
            raise GateE1Stop("transport violated the bounded-read contract")
        chunks.append(chunk)
        retained += len(chunk)
    if response.read(1):
        raise GateE1Stop("response exceeds byte budget; stop without retry")
    return b"".join(chunks)


def _validate_final_url(request: urllib.request.Request, response: ResponseLike) -> None:
    expected = urllib.parse.urlparse(request.full_url)
    actual = urllib.parse.urlparse(response.geturl())
    if (actual.scheme, actual.hostname, actual.path) != (
        expected.scheme,
        expected.hostname,
        expected.path,
    ):
        raise GateE1Stop("response redirected outside its exact allowlisted endpoint")


def _response_items(payload: Any, slot: RequestSlot) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise GateE1Stop("response is not a JSON object")
    header = payload.get("header")
    body = payload.get("body")
    if (
        not isinstance(header, dict)
        or header.get("resultCode") != "00"
        or not isinstance(body, dict)
    ):
        raise GateE1Stop("provider response schema or result code is invalid")
    if str(body.get("pageNo")) != str(slot.page_no) or str(body.get("numOfRows")) != str(
        slot.max_rows
    ):
        raise GateE1Stop("provider paging metadata does not match the approved slot")
    total_count = body.get("totalCount")
    try:
        if int(total_count) < 0:
            raise ValueError
    except (TypeError, ValueError) as error:
        raise GateE1Stop("provider totalCount is invalid") from error
    items = body.get("items")
    if items in (None, ""):
        return []
    if not isinstance(items, dict) or "item" not in items:
        raise GateE1Stop("provider items envelope is invalid")
    rows = items["item"]
    if isinstance(rows, dict):
        result = [rows]
    elif isinstance(rows, list) and all(isinstance(row, dict) for row in rows):
        result = rows
    else:
        raise GateE1Stop("provider item rows are invalid")
    if len(result) > slot.max_rows:
        raise GateE1Stop("response exceeds its row budget")
    return result


def _write_new(path: Path, body: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(body)


def _selected_headers(headers: Message) -> dict[str, str]:
    return {
        key.lower(): value for key, value in headers.items() if key.lower() in _SELECTED_HEADERS
    }


def gate_e1_connectivity_recovery_plan() -> RequestSlot:
    """Return the single fresh slot for a separately approved connectivity recovery."""

    slot = RequestSlot(
        request_id="connectivity_listing_2010_boundary",
        service="listed_instruments",
        base_url=LISTED_BASE,
        operation="/getItemInfo",
        page_no=1,
        filters=(("basDt", "20100104"),),
        max_rows=1,
        max_response_bytes=RECOVERY_MAX_RAW_BYTES,
    )
    parsed = urllib.parse.urlparse(f"{slot.base_url}{slot.operation}")
    if (
        parsed.scheme != "https"
        or (parsed.hostname, parsed.path) not in _ALLOWED_OPERATIONS
        or len(slot.filters) != 1
        or slot.filters[0] != ("basDt", "20100104")
        or slot.page_no != 1
        or slot.max_rows != 1
        or slot.max_response_bytes != RECOVERY_MAX_RAW_BYTES
    ):
        raise ValueError("invalid Gate E1 connectivity-recovery plan")
    return slot


def gate_e1_connectivity_recovery_sha256(slot: RequestSlot | None = None) -> str:
    slot = slot or gate_e1_connectivity_recovery_plan()
    packet = {
        "limits": {
            "requests": 1,
            "rows": 1,
            "raw_bytes": RECOVERY_MAX_RAW_BYTES,
            "retries": 0,
        },
        "probe": "gate-e1-connectivity-recovery",
        "request": slot.safe_record,
    }
    return hashlib.sha256(_canonical_json_bytes(packet)).hexdigest()


def _transport_category(error: BaseException) -> str:
    reason = error.reason if isinstance(error, urllib.error.URLError) else error
    if isinstance(reason, socket.gaierror):
        return "dns"
    if isinstance(reason, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(reason, ssl.SSLError):
        return "tls"
    return "transport"


def collect_gate_e1_connectivity_recovery(
    output_dir: Path,
    *,
    decoded_service_key: str,
    approved_plan_sha256: str,
    transport: Transport | None = None,
    now=lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Attempt one fresh read-only slot and retain a redacted result even on failure."""

    slot = gate_e1_connectivity_recovery_plan()
    plan_sha256 = gate_e1_connectivity_recovery_sha256(slot)
    if approved_plan_sha256 != plan_sha256:
        raise PermissionError("connectivity-recovery plan has not been explicitly approved")
    _validate_service_key(decoded_service_key)
    output_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir()
    transport = transport or _PublicTransport()
    request = slot.request(decoded_service_key)
    result: dict[str, Any]
    try:
        with transport.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            _validate_final_url(request, response)
            if response.status != 200:
                result = {
                    "attempt_ordinal": 1,
                    "headers": _selected_headers(response.headers),
                    "http_status": response.status,
                    "observed_rows": 0,
                    "outcome": "http_error",
                    "raw_path": None,
                    "response_bytes": 0,
                    "response_sha256": None,
                    "transport_category": None,
                }
            elif response.headers.get_content_type() != "application/json":
                result = {
                    "attempt_ordinal": 1,
                    "headers": _selected_headers(response.headers),
                    "http_status": 200,
                    "observed_rows": 0,
                    "outcome": "schema_error",
                    "raw_path": None,
                    "response_bytes": 0,
                    "response_sha256": None,
                    "transport_category": None,
                }
            else:
                body = _read_bounded(
                    response,
                    slot_limit=slot.max_response_bytes,
                    remaining=RECOVERY_MAX_RAW_BYTES,
                )
                if any(secret in body for secret in _secret_variants(decoded_service_key)):
                    raise GateE1Stop("provider echoed the service key; response was not retained")
                try:
                    payload = json.loads(body)
                    rows = _response_items(payload, slot)
                except (json.JSONDecodeError, GateE1Stop):
                    result = {
                        "attempt_ordinal": 1,
                        "headers": _selected_headers(response.headers),
                        "http_status": 200,
                        "observed_rows": 0,
                        "outcome": "schema_error",
                        "raw_path": None,
                        "response_bytes": 0,
                        "response_sha256": None,
                        "transport_category": None,
                    }
                else:
                    raw_path = Path("raw") / "01_connectivity_listing_2010_boundary.json"
                    _write_new(output_dir / raw_path, body)
                    result = {
                        "attempt_ordinal": 1,
                        "headers": _selected_headers(response.headers),
                        "http_status": 200,
                        "observed_rows": len(rows),
                        "outcome": "success",
                        "raw_path": raw_path.as_posix(),
                        "response_bytes": len(body),
                        "response_sha256": hashlib.sha256(body).hexdigest(),
                        "transport_category": None,
                    }
    except urllib.error.HTTPError as error:
        result = {
            "attempt_ordinal": 1,
            "headers": _selected_headers(error.headers or Message()),
            "http_status": error.code,
            "observed_rows": 0,
            "outcome": "http_error",
            "raw_path": None,
            "response_bytes": 0,
            "response_sha256": None,
            "transport_category": None,
        }
        error.close()
    except (urllib.error.URLError, OSError) as error:
        result = {
            "attempt_ordinal": 1,
            "headers": {},
            "http_status": None,
            "observed_rows": 0,
            "outcome": "transport_error",
            "raw_path": None,
            "response_bytes": 0,
            "response_sha256": None,
            "transport_category": _transport_category(error),
        }
    report = {
        "created_at": now().astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "evidence_status": "observed",
        "limits": {
            "requests": 1,
            "rows": 1,
            "raw_bytes": RECOVERY_MAX_RAW_BYTES,
            "retries": 0,
        },
        "plan_sha256": plan_sha256,
        "probe": "gate-e1-connectivity-recovery",
        "request": slot.safe_record,
        "result": result,
        "schema_version": 1,
    }
    encoded = _canonical_json_bytes(report)
    if any(secret in encoded for secret in _secret_variants(decoded_service_key)) or (
        b"serviceKey" in encoded
    ):
        raise GateE1Stop("service key material reached the recovery-report boundary")
    _write_new(output_dir / "result.json", encoded)
    return report


def verify_gate_e1_connectivity_recovery(run_dir: Path) -> dict[str, Any]:
    """Verify the canonical one-attempt recovery report and optional successful raw body."""

    report_path = run_dir / "result.json"
    encoded = report_path.read_bytes()
    report = json.loads(encoded)
    if encoded != _canonical_json_bytes(report):
        raise ValueError("connectivity-recovery report is not canonical JSON")
    slot = gate_e1_connectivity_recovery_plan()
    created_at = report.get("created_at")
    expected_report_keys = {
        "created_at",
        "evidence_status",
        "limits",
        "plan_sha256",
        "probe",
        "request",
        "result",
        "schema_version",
    }
    try:
        parsed_created_at = datetime.fromisoformat(created_at)
    except (TypeError, ValueError) as error:
        raise ValueError("invalid connectivity-recovery timestamp") from error
    if (
        set(report) != expected_report_keys
        or not created_at.endswith("Z")
        or parsed_created_at.tzinfo != UTC
        or report.get("schema_version") != 1
        or report.get("probe") != "gate-e1-connectivity-recovery"
        or report.get("evidence_status") != "observed"
        or report.get("plan_sha256") != gate_e1_connectivity_recovery_sha256(slot)
        or report.get("request") != slot.safe_record
        or report.get("limits")
        != {"requests": 1, "rows": 1, "raw_bytes": RECOVERY_MAX_RAW_BYTES, "retries": 0}
    ):
        raise ValueError("invalid connectivity-recovery report")
    result = report.get("result")
    expected_result_keys = {
        "attempt_ordinal",
        "headers",
        "http_status",
        "observed_rows",
        "outcome",
        "raw_path",
        "response_bytes",
        "response_sha256",
        "transport_category",
    }
    if (
        not isinstance(result, dict)
        or set(result) != expected_result_keys
        or result.get("attempt_ordinal") != 1
        or result.get("outcome") not in {"success", "http_error", "schema_error", "transport_error"}
    ):
        raise ValueError("invalid connectivity-recovery result")
    headers = result.get("headers")
    if (
        not isinstance(headers, dict)
        or any(not isinstance(key, str) or key not in _SELECTED_HEADERS for key in headers)
        or any(not isinstance(value, str) for value in headers.values())
    ):
        raise ValueError("invalid connectivity-recovery headers")
    raw_dir = run_dir / "raw"
    if raw_dir.is_symlink() or not raw_dir.is_dir():
        raise ValueError("invalid connectivity-recovery raw directory")
    raw_entries = sorted(raw_dir.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in raw_entries):
        raise ValueError("invalid connectivity-recovery raw entry")
    if result.get("outcome") == "success":
        if (
            result.get("http_status") != 200
            or result.get("transport_category") is not None
            or not isinstance(result.get("observed_rows"), int)
            or not 0 <= result["observed_rows"] <= 1
        ):
            raise ValueError("invalid successful connectivity-recovery result")
        expected_path = Path("raw") / "01_connectivity_listing_2010_boundary.json"
        if result.get("raw_path") != expected_path.as_posix() or raw_entries != [
            run_dir / expected_path
        ]:
            raise ValueError("connectivity-recovery raw-file set mismatch")
        body = (run_dir / expected_path).read_bytes()
        rows = _response_items(json.loads(body), slot)
        if (
            len(body) != result.get("response_bytes")
            or hashlib.sha256(body).hexdigest() != result.get("response_sha256")
            or len(rows) != result.get("observed_rows")
        ):
            raise ValueError("connectivity-recovery raw evidence mismatch")
    else:
        if (
            raw_entries
            or result.get("raw_path") is not None
            or result.get("response_bytes") != 0
            or result.get("response_sha256") is not None
            or result.get("observed_rows") != 0
        ):
            raise ValueError("failed connectivity recovery retained invalid evidence")
        if result.get("outcome") == "transport_error":
            if result.get("http_status") is not None or result.get("transport_category") not in {
                "dns",
                "timeout",
                "tls",
                "transport",
            }:
                raise ValueError("invalid connectivity-recovery transport result")
        elif (
            result.get("transport_category") is not None
            or not isinstance(result.get("http_status"), int)
            or result.get("http_status") < 100
            or result.get("http_status") > 599
        ):
            raise ValueError("invalid connectivity-recovery provider result")
    return result


def collect_gate_e1_data(
    output_dir: Path,
    *,
    decoded_service_key: str,
    approved_plan_sha256: str,
    transport: Transport | None = None,
    now=lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Execute the exact plan once after a separate approval; never retry a failed slot."""

    slots = gate_e1_request_plan()
    plan_sha256 = gate_e1_plan_sha256(slots)
    if approved_plan_sha256 != plan_sha256:
        raise PermissionError("current Gate E1 request table has not been explicitly approved")
    _validate_service_key(decoded_service_key)
    output_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir()
    transport = transport or _PublicTransport()
    raw_bytes = 0
    row_count = 0
    records: list[dict[str, Any]] = []
    for ordinal, slot in enumerate(slots, start=1):
        request = slot.request(decoded_service_key)
        transport_failed = False
        try:
            with transport.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                _validate_final_url(request, response)
                if response.status != 200:
                    raise GateE1Stop(f"HTTP {response.status}; stop without retry")
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    raise GateE1Stop("unexpected response content type; stop without retry")
                body = _read_bounded(
                    response,
                    slot_limit=slot.max_response_bytes,
                    remaining=MAX_RAW_BYTES - raw_bytes,
                )
        except GateE1Stop:
            raise
        except (urllib.error.HTTPError, urllib.error.URLError, OSError):
            transport_failed = True
        if transport_failed:
            raise GateE1Stop("network or transport failure; stop without retry")
        if any(secret in body for secret in _secret_variants(decoded_service_key)):
            raise GateE1Stop("provider echoed the service key; response was not retained")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as error:
            raise GateE1Stop("response is not valid JSON") from error
        rows = _response_items(payload, slot)
        row_count += len(rows)
        raw_bytes += len(body)
        if row_count > MAX_ROWS or raw_bytes > MAX_RAW_BYTES:
            raise GateE1Stop("cumulative Gate E1 budget exceeded")
        raw_path = Path("raw") / f"{ordinal:02d}_{slot.request_id}.json"
        _write_new(output_dir / raw_path, body)
        records.append(
            {
                **slot.safe_record,
                "attempt_ordinal": ordinal,
                "status": response.status,
                "headers": _selected_headers(response.headers),
                "response_bytes": len(body),
                "response_sha256": hashlib.sha256(body).hexdigest(),
                "observed_rows": len(rows),
                "raw_path": raw_path.as_posix(),
            }
        )
    manifest = {
        "schema_version": 1,
        "probe": "gate-e1-korean-daily-feasibility",
        "created_at": now().isoformat().replace("+00:00", "Z"),
        "evidence_status": "observed",
        "plan_sha256": plan_sha256,
        "limits": {
            "requests": MAX_REQUESTS,
            "rows": MAX_ROWS,
            "raw_bytes": MAX_RAW_BYTES,
            "retries": 0,
        },
        "observed": {
            "attempted_requests": len(records),
            "rows": row_count,
            "raw_response_bytes": raw_bytes,
        },
        "requests": records,
    }
    encoded = _canonical_json_bytes(manifest)
    if any(secret in encoded for secret in _secret_variants(decoded_service_key)) or (
        b"serviceKey" in encoded
    ):
        raise GateE1Stop("service key material reached the manifest boundary")
    _write_new(output_dir / "manifest.json", encoded)
    return manifest


def verify_gate_e1_data(run_dir: Path) -> dict[str, Any]:
    """Recompute the bounded manifest from local raw evidence without a credential."""

    manifest_path = run_dir / "manifest.json"
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    if not isinstance(manifest, dict):
        raise TypeError("Gate E1 manifest is not a JSON object")
    if raw_manifest != _canonical_json_bytes(manifest):
        raise ValueError("Gate E1 manifest is not canonical JSON")
    slots = gate_e1_request_plan()
    records = manifest.get("requests")
    expected_manifest_keys = {
        "schema_version",
        "probe",
        "created_at",
        "evidence_status",
        "plan_sha256",
        "limits",
        "observed",
        "requests",
    }
    created_at = manifest.get("created_at")
    if not isinstance(created_at, str):
        raise TypeError("Gate E1 created_at is not a string")
    try:
        parsed_created_at = datetime.fromisoformat(created_at)
    except ValueError as error:
        raise ValueError("Gate E1 created_at is invalid") from error
    if (
        set(manifest) != expected_manifest_keys
        or not created_at.endswith("Z")
        or parsed_created_at.tzinfo != UTC
        or manifest.get("schema_version") != 1
        or manifest.get("probe") != "gate-e1-korean-daily-feasibility"
        or manifest.get("evidence_status") != "observed"
        or manifest.get("plan_sha256") != gate_e1_plan_sha256(slots)
        or manifest.get("limits")
        != {
            "requests": MAX_REQUESTS,
            "rows": MAX_ROWS,
            "raw_bytes": MAX_RAW_BYTES,
            "retries": 0,
        }
        or not isinstance(records, list)
        or len(records) != MAX_REQUESTS
    ):
        raise ValueError("invalid Gate E1 manifest")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("invalid Gate E1 request records")
    if [record.get("request_id") for record in records] != [slot.request_id for slot in slots]:
        raise ValueError("Gate E1 record order does not match the approved plan")
    expected_paths = {
        (Path("raw") / f"{ordinal:02d}_{slot.request_id}.json").as_posix()
        for ordinal, slot in enumerate(slots, start=1)
    }
    raw_dir = run_dir / "raw"
    if raw_dir.is_symlink() or not raw_dir.is_dir():
        raise ValueError("Gate E1 raw directory is invalid")
    raw_entries = list(raw_dir.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in raw_entries):
        raise ValueError("Gate E1 raw directory contains an unexpected entry")
    actual_paths = {path.relative_to(run_dir).as_posix() for path in raw_entries}
    if actual_paths != expected_paths:
        raise ValueError("Gate E1 raw-file set does not match the approved plan")
    raw_bytes = 0
    row_count = 0
    for ordinal, (slot, record) in enumerate(zip(slots, records, strict=True), start=1):
        expected_record_keys = set(slot.safe_record) | {
            "attempt_ordinal",
            "status",
            "headers",
            "response_bytes",
            "response_sha256",
            "observed_rows",
            "raw_path",
        }
        if set(record) != expected_record_keys:
            raise ValueError(f"Gate E1 request fields mismatch: {slot.request_id}")
        safe_metadata = {key: record.get(key) for key in slot.safe_record}
        if safe_metadata != slot.safe_record:
            raise ValueError(f"Gate E1 request metadata mismatch: {slot.request_id}")
        if record.get("attempt_ordinal") != ordinal or record.get("status") != 200:
            raise ValueError(f"Gate E1 request outcome mismatch: {slot.request_id}")
        headers = record.get("headers")
        if (
            not isinstance(headers, dict)
            or any(not isinstance(key, str) or key not in _SELECTED_HEADERS for key in headers)
            or any(not isinstance(value, str) for value in headers.values())
        ):
            raise ValueError(f"Gate E1 safe headers are invalid: {slot.request_id}")
        expected_path = Path("raw") / f"{ordinal:02d}_{slot.request_id}.json"
        if record.get("raw_path") != expected_path.as_posix():
            raise ValueError(f"Gate E1 raw path mismatch: {slot.request_id}")
        body = (run_dir / expected_path).read_bytes()
        if len(body) != record.get("response_bytes"):
            raise ValueError(f"Gate E1 raw byte count mismatch: {slot.request_id}")
        if len(body) > slot.max_response_bytes:
            raise GateE1Stop(f"Gate E1 slot byte budget exceeded: {slot.request_id}")
        if hashlib.sha256(body).hexdigest() != record.get("response_sha256"):
            raise ValueError(f"Gate E1 raw checksum mismatch: {slot.request_id}")
        rows = _response_items(json.loads(body), slot)
        if len(rows) != record.get("observed_rows"):
            raise ValueError(f"Gate E1 row count mismatch: {slot.request_id}")
        raw_bytes += len(body)
        row_count += len(rows)
    observed = manifest.get("observed")
    expected_observed = {
        "attempted_requests": MAX_REQUESTS,
        "rows": row_count,
        "raw_response_bytes": raw_bytes,
    }
    if observed != expected_observed:
        raise ValueError("Gate E1 observed totals are inconsistent")
    if row_count > MAX_ROWS or raw_bytes > MAX_RAW_BYTES:
        raise GateE1Stop("Gate E1 evidence exceeds its approved budget")
    return expected_observed
