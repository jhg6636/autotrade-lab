"""Fail-closed Gate E1 Korean daily-data eligibility packet.

The packet is a fresh, goal-authorized successor to the exhausted Gate E1-DATA run. It performs at
most the immutable 24 public GET slots, never retries, writes a canonical terminal manifest even on
partial failure, and evaluates only bounded E2 feasibility—not strategy profitability.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .gate_e1_prep import (
    _SELECTED_HEADERS,
    HTTP_TIMEOUT_SECONDS,
    MAX_RAW_BYTES,
    MAX_REQUESTS,
    MAX_ROWS,
    MAX_SLOT_BYTES,
    GateE1Stop,
    RequestSlot,
    Transport,
    _canonical_json_bytes,
    _PublicTransport,
    _secret_variants,
    _selected_headers,
    _transport_category,
    _validate_final_url,
    _validate_service_key,
    _write_new,
    gate_e1_plan_sha256,
    gate_e1_request_plan,
    load_public_data_service_key,
    validate_gate_e1_plan,
)

PACKET_ID = "gate-e1-eligibility-20260828-v1"
PROBE = "gate-e1-korean-daily-eligibility"
OUTPUT_DIR = Path("research/probes/gate-e1-eligibility-20260828-v1")
PACKET_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1
PARSER_VERSION = 2
SEMANTIC_VALIDATOR_VERSION = 1
FAILURE_MANIFEST_VERSION = 1
CONCURRENCY = 1

RUNTIME_ENVELOPE_EVIDENCE_SHA256 = (
    "661ec92a32a8c54f05f3286335aee6a57076867696a4d1c0e7ad41df6ee989f4"
)
OFFICIAL_EVIDENCE_FINGERPRINTS = {
    "dividend_guide": "9dda440fbdcb69fda4f485ed39733d114bec9933a2c5a84024b86b01de26a9b3",
    "dividend_page": "d4e44b8db7a390d9da97b2ad3c393f4146680b14e6ff9d05cc39f23d6ad15623",
    "issuance_guide": "cddc6e38241bf55705395ba0fa70c10b8c24de3439a84829d3fb297e8aaff5f4",
    "issuance_page": "e35561455b704f2d588f7c704ac19bd597d260d88e9915d1faefaf11fa937a8a",
    "listing_guide": "f5c34871d834daea234cfdb4d8975ff934d057cd79a3496ab47219f01869bb09",
    "listing_page": "de6c3c9ad3c61cd9619dda344a28044e088f4dcda6ce410919e85ae7d1265b5d",
    "price_guide": "5d9b2259b37e1bf92bdbb3f3bd76b0ec9d499fb43758a67aa9bf62d2d4a256f4",
    "price_page": "779ca314214e44a17b4d59f3bbcbd77d6471c781dcc923761dbd0dcda0ed7f11",
}

OPERATION_CONTRACTS: dict[str, dict[str, tuple[str, ...]]] = {
    "/getItemInfo": {
        "required": ("basDt", "srtnCd", "isinCd", "mrktCtg", "itmsNm", "crno", "corpNm"),
        "identity": ("basDt", "isinCd"),
        "nonempty": ("basDt", "srtnCd", "isinCd", "mrktCtg", "itmsNm", "corpNm"),
    },
    "/getStockPriceInfo": {
        "required": (
            "basDt",
            "srtnCd",
            "isinCd",
            "itmsNm",
            "mrktCtg",
            "clpr",
            "vs",
            "fltRt",
            "mkp",
            "hipr",
            "lopr",
            "trqu",
            "trPrc",
            "lstgStCnt",
            "mrktTotAmt",
        ),
        "identity": ("basDt", "isinCd"),
        "nonempty": ("basDt", "srtnCd", "isinCd", "itmsNm", "mrktCtg"),
    },
    "/getSecuritiesPriceInfo": {
        "required": (
            "basDt",
            "srtnCd",
            "isinCd",
            "itmsNm",
            "clpr",
            "vs",
            "fltRt",
            "mkp",
            "hipr",
            "lopr",
            "trqu",
            "trPrc",
            "stLstgCnt",
            "mrktTotAmt",
        ),
        "identity": ("basDt", "isinCd"),
        "nonempty": ("basDt", "srtnCd", "isinCd", "itmsNm"),
    },
    "/getItemBasiInfo_V3": {
        "required": (
            "basDt",
            "crno",
            "isinCd",
            "stckIssuCmpyNm",
            "isinCdNm",
            "stckParPrc",
            "issuStckCnt",
            "lstgDt",
            "lstgAbolDt",
            "dpsgRegDt",
            "dpsgCanDt",
            "issuFrmtClsfNm",
            "scrsItmsKcd",
            "scrsItmsKcdNm",
            "itmsShrtnCd",
        ),
        "identity": ("basDt", "isinCd"),
        "nonempty": ("basDt", "crno", "isinCd", "stckIssuCmpyNm", "isinCdNm"),
    },
    "/getStocIssuInfo_V3": {
        "required": (
            "basDt",
            "crno",
            "isinCd",
            "isinCdNm",
            "stckIssuCmpyNm",
            "scrsDcd",
            "stckIssuSqno",
            "stckIssuDt",
            "stckIssuDcnt",
            "scrsItmsKcd",
            "scrsItmsKcdNm",
            "stckIssuRcd",
            "stckIssuRcdNm",
            "issuStckCnt",
            "lstgDt",
        ),
        "identity": ("basDt", "isinCd", "stckIssuDt", "stckIssuDcnt", "stckIssuRcd"),
        "nonempty": ("basDt", "crno", "isinCd", "isinCdNm", "stckIssuCmpyNm"),
    },
    "/getDiviInfo_V2": {
        "required": (
            "basDt",
            "crno",
            "isinCd",
            "isinCdNm",
            "stckIssuCmpyNm",
            "dvdnBasDt",
            "cashDvdnPayDt",
            "stckHndvDt",
            "stckDvdnRcd",
            "stckDvdnRcdNm",
            "trsnmDptyDcd",
            "trsnmDptyDcdNm",
            "scrsItmsKcd",
            "scrsItmsKcdNm",
            "stckGenrDvdnAmt",
            "stckGrdnDvdnAmt",
            "stckGenrCashDvdnRt",
            "stckGenrDvdnRt",
            "cashGrdnDvdnRt",
            "stckGrdnDvdnRt",
            "stckParPrc",
            "stckStacMd",
        ),
        "identity": (
            "basDt",
            "isinCd",
            "dvdnBasDt",
            "cashDvdnPayDt",
            "stckHndvDt",
            "scrsItmsKcd",
            "stckDvdnRcd",
        ),
        "nonempty": ("basDt", "crno", "isinCd", "isinCdNm", "stckIssuCmpyNm"),
    },
}


def field_contract_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(OPERATION_CONTRACTS)).hexdigest()


def gate_e1_eligibility_packet() -> dict[str, Any]:
    slots = gate_e1_request_plan()
    validate_gate_e1_plan(slots)
    return {
        "credential_source": {
            "environment_key": "PUBLIC_DATA_SERVICE_KEY_DECODED",
            "file": ".env.public-data",
        },
        "evidence": {
            "official": OFFICIAL_EVIDENCE_FINGERPRINTS,
            "runtime_envelope_response_sha256": RUNTIME_ENVELOPE_EVIDENCE_SHA256,
        },
        "field_contract_sha256": field_contract_sha256(),
        "limits": {
            "concurrency": CONCURRENCY,
            "per_slot_raw_bytes": MAX_SLOT_BYTES,
            "raw_bytes": MAX_RAW_BYTES,
            "requests": MAX_REQUESTS,
            "retries": 0,
            "rows": MAX_ROWS,
            "timeout_seconds": HTTP_TIMEOUT_SECONDS,
        },
        "output_dir": OUTPUT_DIR.as_posix(),
        "packet_id": PACKET_ID,
        "packet_schema_version": PACKET_SCHEMA_VERSION,
        "probe": PROBE,
        "request_plan_sha256": gate_e1_plan_sha256(slots),
        "requests": [slot.safe_record for slot in slots],
        "response_contract": {
            "ambiguous_envelope_rejected": True,
            "envelopes": ["documented_top_level", "observed_response_wrapper"],
            "failure_manifest_version": FAILURE_MANIFEST_VERSION,
            "parser_version": PARSER_VERSION,
            "runtime_wrapper_sibling_keys_rejected": True,
            "semantic_validator_version": SEMANTIC_VALIDATOR_VERSION,
        },
        "stop_policy": {
            "empty_success_continues": True,
            "hard_failure_stops_globally": True,
            "replacement_requests": False,
            "unused_budget_reuse": False,
        },
        "transport": {
            "content_type": "application/json",
            "method": "GET",
            "redirects": False,
            "scheme": "https",
        },
    }


def gate_e1_eligibility_packet_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(gate_e1_eligibility_packet())).hexdigest()


class AttemptFailure(RuntimeError):
    def __init__(
        self,
        category: str,
        *,
        http_status: int | None = None,
        headers: dict[str, str] | None = None,
        response_bytes: int = 0,
        response_sha256: str | None = None,
        provider_result_code: str | None = None,
        envelope: str | None = None,
        transport_category: str | None = None,
    ) -> None:
        super().__init__(category)
        self.category = category
        self.http_status = http_status
        self.headers = headers or {}
        self.response_bytes = response_bytes
        self.response_sha256 = response_sha256
        self.provider_result_code = provider_result_code
        self.envelope = envelope
        self.transport_category = transport_category


@dataclass(frozen=True, slots=True)
class ParsedResponse:
    envelope: str
    rows: tuple[dict[str, Any], ...]
    total_count: int


def _read_eligibility_bounded(response: Any, *, slot_limit: int, remaining: int) -> bytes:
    """Read retained bytes plus at most one overflow-detection byte."""

    allowed = min(slot_limit, remaining)
    raw_length = response.headers.get("Content-Length")
    if raw_length is not None:
        try:
            declared = int(raw_length)
        except ValueError as error:
            raise AttemptFailure("byte_budget") from error
        if declared < 0 or declared > allowed:
            raise AttemptFailure("byte_budget")
    chunks: list[bytes] = []
    read_bytes = 0
    while read_bytes < allowed:
        requested = min(65_536, allowed - read_bytes)
        chunk = response.read(requested)
        if not chunk:
            break
        if len(chunk) > requested:
            raise AttemptFailure("byte_budget", response_bytes=read_bytes + len(chunk))
        chunks.append(chunk)
        read_bytes += len(chunk)
    overflow = response.read(1)
    if overflow:
        raise AttemptFailure("byte_budget", response_bytes=read_bytes + len(overflow))
    return b"".join(chunks)


def _response_root(payload: Any) -> tuple[dict[str, Any], str]:
    if not isinstance(payload, dict):
        raise AttemptFailure("schema")
    documented = "header" in payload or "body" in payload
    wrapped = "response" in payload
    if documented and wrapped:
        raise AttemptFailure("ambiguous_envelope")
    if wrapped:
        if set(payload) != {"response"} or not isinstance(payload["response"], dict):
            raise AttemptFailure("runtime_envelope")
        return payload["response"], "observed_response_wrapper"
    return payload, "documented_top_level"


def _parse_response(payload: Any, slot: RequestSlot) -> ParsedResponse:
    root, envelope = _response_root(payload)
    header = root.get("header")
    body = root.get("body")
    if not isinstance(header, dict):
        raise AttemptFailure("schema", envelope=envelope)
    code = header.get("resultCode")
    safe_code = (
        code
        if isinstance(code, str) and len(code) == 2 and code.isascii() and code.isdigit()
        else None
    )
    if safe_code is None:
        raise AttemptFailure("schema", envelope=envelope)
    if safe_code != "00":
        raise AttemptFailure(
            "provider_result_code",
            provider_result_code=safe_code,
            envelope=envelope,
        )
    if not isinstance(body, dict):
        raise AttemptFailure("schema", provider_result_code="00", envelope=envelope)
    if str(body.get("pageNo")) != str(slot.page_no) or str(body.get("numOfRows")) != str(
        slot.max_rows
    ):
        raise AttemptFailure("paging", provider_result_code="00", envelope=envelope)
    try:
        total_count = int(body.get("totalCount"))
    except (TypeError, ValueError, OverflowError) as error:
        raise AttemptFailure("total_count", provider_result_code="00", envelope=envelope) from error
    if total_count < 0:
        raise AttemptFailure("total_count", provider_result_code="00", envelope=envelope)
    items = body.get("items")
    if items in (None, ""):
        rows: list[dict[str, Any]] = []
    elif isinstance(items, dict) and isinstance(items.get("item"), dict):
        rows = [items["item"]]
    elif (
        isinstance(items, dict)
        and isinstance(items.get("item"), list)
        and all(isinstance(row, dict) for row in items["item"])
    ):
        rows = items["item"]
    else:
        raise AttemptFailure("items", provider_result_code="00", envelope=envelope)
    if len(rows) > slot.max_rows:
        raise AttemptFailure("row_budget", provider_result_code="00", envelope=envelope)
    if len(rows) > total_count:
        raise AttemptFailure("total_count", provider_result_code="00", envelope=envelope)
    return ParsedResponse(envelope=envelope, rows=tuple(rows), total_count=total_count)


def _decimal(value: Any) -> Decimal:
    if not isinstance(value, str) or not value:
        raise AttemptFailure("semantic_numeric")
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise AttemptFailure("semantic_numeric") from error
    if not result.is_finite():
        raise AttemptFailure("semantic_numeric")
    return result


def _semantic_rows(slot: RequestSlot, parsed: ParsedResponse) -> tuple[tuple[str, ...], ...]:
    contract = OPERATION_CONTRACTS.get(slot.operation)
    if contract is None:
        raise AttemptFailure("semantic_contract")
    identities: list[tuple[str, ...]] = []
    filters = dict(slot.filters)
    for row in parsed.rows:
        if any(key not in row or not isinstance(row[key], str) for key in contract["required"]):
            raise AttemptFailure("semantic_required_fields")
        if any(not row[key] for key in contract["nonempty"]):
            raise AttemptFailure("semantic_required_fields")
        if "basDt" in filters and row["basDt"] != filters["basDt"]:
            raise AttemptFailure("semantic_filter")
        if "isinCd" in filters and row["isinCd"] != filters["isinCd"]:
            raise AttemptFailure("semantic_filter")
        if "crno" in filters and row["crno"] != filters["crno"]:
            raise AttemptFailure("semantic_filter")
        if "stckIssuCmpyNm" in filters and row["stckIssuCmpyNm"] != filters["stckIssuCmpyNm"]:
            raise AttemptFailure("semantic_filter")
        if "likeSrtnCd" in filters:
            actual = row.get("srtnCd", "")
            normalized = actual.removeprefix("A")
            if normalized != filters["likeSrtnCd"]:
                raise AttemptFailure("semantic_filter")
        if slot.operation in {"/getStockPriceInfo", "/getSecuritiesPriceInfo"}:
            open_price = _decimal(row["mkp"])
            high = _decimal(row["hipr"])
            low = _decimal(row["lopr"])
            close = _decimal(row["clpr"])
            volume = _decimal(row["trqu"])
            if min(open_price, high, low, close, volume) < 0:
                raise AttemptFailure("semantic_ohlcv")
            if high < max(open_price, close, low) or low > min(open_price, close, high):
                raise AttemptFailure("semantic_ohlcv")
        if slot.request_id == "listing_kosdaq_sentinel" and row["mrktCtg"] != "KOSDAQ":
            raise AttemptFailure("semantic_sentinel")
        if slot.request_id == "issuance_basic_hanjin_delist" and row["lstgAbolDt"] != "20170307":
            raise AttemptFailure("semantic_sentinel")
        identity = tuple(row[key] for key in contract["identity"])
        identities.append(identity)
    if len(identities) != len(set(identities)):
        raise AttemptFailure("semantic_duplicate")
    return tuple(identities)


PAGE_PAIRS = {
    "listing": ("listing_probe_page_1", "listing_probe_page_2"),
    "stock_price": ("stock_price_probe_page_1", "stock_price_probe_page_2"),
}


def _pagination_checks(
    parsed_by_id: dict[str, ParsedResponse],
    identities_by_id: dict[str, tuple[tuple[str, ...], ...]],
) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    for name, (first_id, second_id) in PAGE_PAIRS.items():
        first = parsed_by_id.get(first_id)
        second = parsed_by_id.get(second_id)
        if first is None or second is None:
            checks[name] = {
                "first_page_rows": len(first.rows) if first else None,
                "overlap": None,
                "second_page_rows": len(second.rows) if second else None,
                "status": "not_reached",
                "total_count": first.total_count if first else None,
            }
            continue
        if first.total_count != second.total_count:
            raise AttemptFailure("pagination_total_mismatch")
        total = first.total_count
        expected_first = min(50, total)
        expected_second = min(50, max(total - 50, 0))
        if len(first.rows) != expected_first or len(second.rows) != expected_second:
            raise AttemptFailure("pagination_row_count")
        overlap = len(set(identities_by_id[first_id]) & set(identities_by_id[second_id]))
        if overlap:
            raise AttemptFailure("pagination_duplicate")
        checks[name] = {
            "first_page_rows": len(first.rows),
            "overlap": overlap,
            "second_page_rows": len(second.rows),
            "status": "passed" if total > 50 else "not_exercised",
            "total_count": total,
        }
    return checks


UNKNOWN_LIMITATIONS = [
    "complete_delisted_population",
    "correction_and_revision_policy",
    "deterministic_sort_beyond_observed_pages",
    "earliest_retention_guarantee",
    "etf_point_in_time_universe",
    "full_dividend_history_ordering",
    "full_page_completeness_beyond_first_100_rows",
    "price_adjustment_factor_semantics",
    "suspension_and_zero_volume_semantics",
]


def _row_isins(parsed_by_id: dict[str, ParsedResponse], request_id: str) -> set[str]:
    parsed = parsed_by_id.get(request_id)
    if parsed is None:
        return set()
    return {row["isinCd"] for row in parsed.rows if isinstance(row.get("isinCd"), str)}


def _has_rows(parsed_by_id: dict[str, ParsedResponse], request_id: str) -> bool:
    parsed = parsed_by_id.get(request_id)
    return parsed is not None and bool(parsed.rows)


def _has_samsung_split_event(parsed_by_id: dict[str, ParsedResponse]) -> bool:
    parsed = parsed_by_id.get("issuance_history_samsung_post_split")
    return parsed is not None and any(
        row.get("isinCd") == "KR7005930003" and "분할" in row.get("stckIssuRcdNm", "")
        for row in parsed.rows
    )


def _has_dividend_event_identity(parsed_by_id: dict[str, ParsedResponse]) -> bool:
    parsed = parsed_by_id.get("dividend_samsung_history")
    return parsed is not None and any(
        row.get("isinCd") == "KR7005930003"
        and bool(row.get("dvdnBasDt"))
        and bool(row.get("cashDvdnPayDt") or row.get("stckHndvDt"))
        for row in parsed.rows
    )


def _aliases_match(
    parsed_by_id: dict[str, ParsedResponse], request_ids: tuple[str, ...], isin: str
) -> bool:
    aliases: set[tuple[str, str]] = set()
    for request_id in request_ids:
        parsed = parsed_by_id.get(request_id)
        if parsed is None:
            return False
        matching = [row for row in parsed.rows if row.get("isinCd") == isin]
        if not matching:
            return False
        aliases.update((row.get("srtnCd", ""), row.get("itmsNm", "")) for row in matching)
    return len(aliases) == 1


def evaluate_gate_e1_eligibility(
    *,
    terminal_state: str,
    parsed_by_id: dict[str, ParsedResponse],
    pagination_checks: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return a deterministic, conservative bounded-E2 decision matrix."""

    complete = terminal_state == "complete"
    current_stock = bool(
        _row_isins(parsed_by_id, "listing_probe_page_1")
        & _row_isins(parsed_by_id, "stock_price_probe_page_1")
    )
    samsung_isin = "KR7005930003"
    samsung_join = _has_samsung_split_event(parsed_by_id) and all(
        samsung_isin in _row_isins(parsed_by_id, request_id)
        for request_id in (
            "stock_price_samsung_pre_split",
            "stock_price_samsung_post_split",
            "issuance_basic_samsung_pre_split",
            "issuance_basic_samsung_post_split",
            "issuance_history_samsung_post_split",
        )
    )
    hanjin_join = bool(
        _row_isins(parsed_by_id, "stock_price_hanjin_last_trading_day")
        & _row_isins(parsed_by_id, "issuance_basic_hanjin_delist")
    )
    stock_criteria = {
        "complete_packet": complete,
        "current_listing_and_price": current_stock,
        "dividend_share_class_evidence": _has_dividend_event_identity(parsed_by_id),
        "hanjin_delisted_identity_join": hanjin_join,
        "historical_2010_listing": _has_rows(parsed_by_id, "listing_2010_boundary"),
        "historical_2010_price": _has_rows(parsed_by_id, "stock_price_2010_boundary"),
        "kosdaq_sentinel": _has_rows(parsed_by_id, "listing_kosdaq_sentinel"),
        "listing_pagination": pagination_checks["listing"]["status"] == "passed",
        "samsung_corporate_action_join": samsung_join,
        "stock_price_pagination": pagination_checks["stock_price"]["status"] == "passed",
    }
    if not complete or not current_stock:
        stock_status = "failed"
    elif all(stock_criteria.values()):
        stock_status = "feasible_for_e2"
    else:
        stock_status = "limited"
    stock_blockers = sorted(key for key, passed in stock_criteria.items() if not passed)

    kodex_isin = "KR7069500007"
    kodex_criteria = {
        "alias_consistency": _aliases_match(
            parsed_by_id,
            ("listing_etf_sentinel", "etf_price_2010_boundary", "etf_price_probe_date"),
            kodex_isin,
        ),
        "complete_packet": complete,
        "listing_identity": kodex_isin in _row_isins(parsed_by_id, "listing_etf_sentinel"),
        "price_2010_identity": kodex_isin in _row_isins(parsed_by_id, "etf_price_2010_boundary"),
        "price_probe_identity": kodex_isin in _row_isins(parsed_by_id, "etf_price_probe_date"),
    }
    kodex_status = "feasible_for_e2" if all(kodex_criteria.values()) else "failed"
    etf_status = "limited" if kodex_status == "feasible_for_e2" else "failed"
    etf_blockers = ["no_delisted_etf_or_point_in_time_universe_sample"]
    if kodex_status != "feasible_for_e2":
        etf_blockers.extend(sorted(key for key, passed in kodex_criteria.items() if not passed))

    return {
        "backtest_decision": "no_go",
        "backtest_reason": "bounded_gate_e1_does_not_establish_point_in_time_dataset_quality",
        "etf_daily": {
            "blockers": sorted(etf_blockers),
            "status": etf_status,
        },
        "kodex200_single_instrument": {
            "criteria": kodex_criteria,
            "status": kodex_status,
        },
        "stock_daily": {
            "blockers": stock_blockers,
            "criteria": stock_criteria,
            "status": stock_status,
        },
        "unknown_limitations": UNKNOWN_LIMITATIONS,
    }


def _contains_secret(data: bytes, decoded_service_key: str) -> bool:
    def normalize_percent_hex(value: bytes) -> bytes:
        return re.sub(
            rb"%([0-9a-fA-F]{2})",
            lambda match: b"%" + match.group(1).upper(),
            value,
        )

    variants = _secret_variants(decoded_service_key)
    normalized = normalize_percent_hex(data)
    return any(secret in data for secret in variants) or any(
        normalize_percent_hex(secret) in normalized for secret in variants
    )


def _safe_headers(headers: Any, decoded_service_key: str) -> dict[str, str]:
    selected = _selected_headers(headers)
    encoded = _canonical_json_bytes(selected)
    if _contains_secret(encoded, decoded_service_key):
        raise AttemptFailure("secret_header")
    return selected


def _base_result(slot: RequestSlot, ordinal: int) -> dict[str, Any]:
    return {
        **slot.safe_record,
        "attempt_ordinal": ordinal,
        "envelope": None,
        "failure_category": None,
        "headers": {},
        "http_status": None,
        "observed_rows": 0,
        "outcome": "failure",
        "provider_result_code": None,
        "raw_path": None,
        "response_bytes": 0,
        "response_sha256": None,
        "total_count": None,
        "transport_category": None,
    }


def _apply_failure(result: dict[str, Any], failure: AttemptFailure) -> None:
    result.update(
        {
            "envelope": failure.envelope,
            "failure_category": failure.category,
            "headers": failure.headers,
            "http_status": failure.http_status,
            "provider_result_code": failure.provider_result_code,
            "response_bytes": failure.response_bytes,
            "response_sha256": failure.response_sha256,
            "transport_category": failure.transport_category,
        }
    )


def _success_result(
    slot: RequestSlot,
    ordinal: int,
    *,
    parsed: ParsedResponse,
    headers: dict[str, str],
    body: bytes,
    raw_path: Path,
) -> dict[str, Any]:
    result = _base_result(slot, ordinal)
    result.update(
        {
            "envelope": parsed.envelope,
            "headers": headers,
            "http_status": 200,
            "observed_rows": len(parsed.rows),
            "outcome": "success",
            "provider_result_code": "00",
            "raw_path": raw_path.as_posix(),
            "response_bytes": len(body),
            "response_sha256": hashlib.sha256(body).hexdigest(),
            "total_count": parsed.total_count,
        }
    )
    return result


def _preflight(output_dir: Path, approved_packet_sha256: str) -> None:
    if output_dir != OUTPUT_DIR:
        raise PermissionError("Gate E1 eligibility requires its exact fresh output directory")
    if approved_packet_sha256 != gate_e1_eligibility_packet_sha256():
        raise PermissionError("Gate E1 eligibility packet hash is not authorized")
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError("Gate E1 eligibility output already exists; never reuse it")


def collect_gate_e1_eligibility_from_key_file(
    output_dir: Path,
    *,
    key_file: Path,
    approved_packet_sha256: str,
    transport: Transport | None = None,
    now=lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Preflight before reading the private key, then execute the packet once."""

    _preflight(output_dir, approved_packet_sha256)
    key = load_public_data_service_key(key_file)
    try:
        return _collect_gate_e1_eligibility(
            output_dir,
            decoded_service_key=key,
            transport=transport,
            now=now,
        )
    finally:
        del key


def collect_gate_e1_eligibility(
    output_dir: Path,
    *,
    decoded_service_key: str,
    approved_packet_sha256: str,
    transport: Transport | None = None,
    now=lambda: datetime.now(UTC),
) -> dict[str, Any]:
    """Execute the exact 24-slot eligibility packet with a terminal manifest."""

    _preflight(output_dir, approved_packet_sha256)
    _validate_service_key(decoded_service_key)
    return _collect_gate_e1_eligibility(
        output_dir,
        decoded_service_key=decoded_service_key,
        transport=transport,
        now=now,
    )


def _collect_gate_e1_eligibility(
    output_dir: Path,
    *,
    decoded_service_key: str,
    transport: Transport | None,
    now,
) -> dict[str, Any]:
    slots = gate_e1_request_plan()
    output_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir()
    transport = transport or _PublicTransport()
    results: list[dict[str, Any]] = []
    parsed_by_id: dict[str, ParsedResponse] = {}
    identities_by_id: dict[str, tuple[tuple[str, ...], ...]] = {}
    retained_raw_bytes = 0
    response_bytes_read = 0
    row_count = 0
    stop: dict[str, Any] | None = None

    for ordinal, slot in enumerate(slots, start=1):
        request = slot.request(decoded_service_key)
        result = _base_result(slot, ordinal)
        body: bytes | None = None
        headers: dict[str, str] = {}
        try:
            try:
                with transport.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                    try:
                        _validate_final_url(request, response)
                    except GateE1Stop as error:
                        raise AttemptFailure("redirect") from error
                    headers = _safe_headers(response.headers, decoded_service_key)
                    if response.status != 200:
                        raise AttemptFailure(
                            "http_status",
                            http_status=response.status,
                            headers=headers,
                        )
                    if response.headers.get_content_type() != "application/json":
                        raise AttemptFailure(
                            "content_type",
                            http_status=200,
                            headers=headers,
                        )
                    try:
                        body = _read_eligibility_bounded(
                            response,
                            slot_limit=slot.max_response_bytes,
                            remaining=MAX_RAW_BYTES - response_bytes_read,
                        )
                    except AttemptFailure as failure:
                        raise AttemptFailure(
                            "byte_budget",
                            http_status=200,
                            headers=headers,
                            response_bytes=failure.response_bytes,
                        ) from None
            except urllib.error.HTTPError as error:
                try:
                    error_headers = _safe_headers(error.headers, decoded_service_key)
                finally:
                    error.close()
                raise AttemptFailure(
                    "http_status",
                    http_status=error.code,
                    headers=error_headers,
                ) from None
            except AttemptFailure:
                raise
            except (urllib.error.URLError, OSError) as error:
                raise AttemptFailure(
                    "transport",
                    transport_category=_transport_category(error),
                ) from None

            body_sha256 = hashlib.sha256(body).hexdigest()
            response_bytes_read += len(body)
            if _contains_secret(body, decoded_service_key):
                raise AttemptFailure(
                    "secret_body",
                    http_status=200,
                    headers=headers,
                    response_bytes=len(body),
                    response_sha256=body_sha256,
                )
            try:
                payload = json.loads(body)
            except (ValueError, RecursionError):
                raise AttemptFailure(
                    "invalid_json",
                    http_status=200,
                    headers=headers,
                    response_bytes=len(body),
                    response_sha256=body_sha256,
                ) from None
            try:
                parsed: ParsedResponse | None = None
                parsed = _parse_response(payload, slot)
                identities = _semantic_rows(slot, parsed)
                candidate_parsed = {**parsed_by_id, slot.request_id: parsed}
                candidate_identities = {**identities_by_id, slot.request_id: identities}
                _pagination_checks(candidate_parsed, candidate_identities)
            except AttemptFailure as failure:
                provider_result_code = failure.provider_result_code
                envelope = failure.envelope
                if parsed is not None:
                    provider_result_code = "00"
                    envelope = parsed.envelope
                raise AttemptFailure(
                    failure.category,
                    http_status=200,
                    headers=headers,
                    response_bytes=len(body),
                    response_sha256=body_sha256,
                    provider_result_code=provider_result_code,
                    envelope=envelope,
                ) from None

            if row_count + len(parsed.rows) > MAX_ROWS:
                raise AttemptFailure(
                    "row_budget",
                    http_status=200,
                    headers=headers,
                    response_bytes=len(body),
                    response_sha256=body_sha256,
                    provider_result_code="00",
                    envelope=parsed.envelope,
                )
            raw_path = Path("raw") / f"{ordinal:02d}_{slot.request_id}.json"
            _write_new(output_dir / raw_path, body)
            result = _success_result(
                slot,
                ordinal,
                parsed=parsed,
                headers=headers,
                body=body,
                raw_path=raw_path,
            )
            results.append(result)
            parsed_by_id[slot.request_id] = parsed
            identities_by_id[slot.request_id] = identities
            retained_raw_bytes += len(body)
            row_count += len(parsed.rows)
        except AttemptFailure as failure:
            if (
                body is not None
                and failure.response_bytes == 0
                and failure.category
                not in {
                    "byte_budget",
                    "secret_header",
                }
            ):
                failure.response_bytes = len(body)
                failure.response_sha256 = hashlib.sha256(body).hexdigest()
            _apply_failure(result, failure)
            if body is None:
                response_bytes_read += failure.response_bytes
            results.append(result)
            stop = {"category": failure.category, "ordinal": ordinal}
            break

    terminal_state = "complete" if len(results) == MAX_REQUESTS and stop is None else "stopped"
    pagination = _pagination_checks(parsed_by_id, identities_by_id)
    eligibility = evaluate_gate_e1_eligibility(
        terminal_state=terminal_state,
        parsed_by_id=parsed_by_id,
        pagination_checks=pagination,
    )
    manifest = {
        "created_at": now().astimezone(UTC).isoformat().replace("+00:00", "Z"),
        "eligibility": eligibility,
        "evidence_status": "observed",
        "field_contract_sha256": field_contract_sha256(),
        "limits": gate_e1_eligibility_packet()["limits"],
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "observed": {
            "attempted_requests": len(results),
            "retained_raw_bytes": retained_raw_bytes,
            "rows": row_count,
            "response_bytes_read": response_bytes_read,
            "retries": 0,
        },
        "packet_id": PACKET_ID,
        "packet_sha256": gate_e1_eligibility_packet_sha256(),
        "pagination_checks": pagination,
        "planned_requests": [slot.safe_record for slot in slots],
        "probe": PROBE,
        "request_plan_sha256": gate_e1_plan_sha256(slots),
        "results": results,
        "stop": stop,
        "terminal_state": terminal_state,
    }
    encoded = _canonical_json_bytes(manifest)
    if _contains_secret(encoded, decoded_service_key) or b"serviceKey" in encoded:
        raise GateE1Stop("service key material reached the eligibility manifest boundary")
    _write_new(output_dir / "manifest.json", encoded)
    return manifest


FAILURE_CATEGORIES = {
    "ambiguous_envelope",
    "byte_budget",
    "content_type",
    "http_status",
    "invalid_json",
    "items",
    "paging",
    "pagination_duplicate",
    "pagination_row_count",
    "pagination_total_mismatch",
    "provider_result_code",
    "redirect",
    "row_budget",
    "runtime_envelope",
    "schema",
    "secret_body",
    "secret_header",
    "semantic_duplicate",
    "semantic_filter",
    "semantic_numeric",
    "semantic_ohlcv",
    "semantic_required_fields",
    "semantic_sentinel",
    "total_count",
    "transport",
}

BODY_FAILURE_CATEGORIES = FAILURE_CATEGORIES - {
    "byte_budget",
    "content_type",
    "http_status",
    "provider_result_code",
    "redirect",
    "secret_header",
    "transport",
}
UNPARSED_BODY_FAILURE_CATEGORIES = {
    "ambiguous_envelope",
    "invalid_json",
    "runtime_envelope",
    "secret_body",
}
PARSED_BODY_FAILURE_CATEGORIES = BODY_FAILURE_CATEGORIES - {
    *UNPARSED_BODY_FAILURE_CATEGORIES,
    "schema",
}


def _allowed_failure_categories(slot: RequestSlot) -> set[str]:
    categories = {
        "ambiguous_envelope",
        "byte_budget",
        "content_type",
        "http_status",
        "invalid_json",
        "items",
        "paging",
        "provider_result_code",
        "redirect",
        "row_budget",
        "runtime_envelope",
        "schema",
        "secret_body",
        "secret_header",
        "semantic_duplicate",
        "semantic_filter",
        "semantic_required_fields",
        "total_count",
        "transport",
    }
    if slot.operation in {"/getStockPriceInfo", "/getSecuritiesPriceInfo"}:
        categories.update({"semantic_numeric", "semantic_ohlcv"})
    if slot.request_id in {"listing_kosdaq_sentinel", "issuance_basic_hanjin_delist"}:
        categories.add("semantic_sentinel")
    if slot.request_id in {"listing_probe_page_2", "stock_price_probe_page_2"}:
        categories.update(
            {"pagination_duplicate", "pagination_row_count", "pagination_total_mismatch"}
        )
    return categories


def verify_gate_e1_eligibility(run_dir: Path) -> dict[str, Any]:
    """Rebuild the terminal state, raw set, pagination, and eligibility without a key."""

    if run_dir != OUTPUT_DIR:
        raise ValueError("Gate E1 eligibility verifier requires the exact packet output directory")
    encoded = (run_dir / "manifest.json").read_bytes()
    manifest = json.loads(encoded)
    if encoded != _canonical_json_bytes(manifest):
        raise ValueError("Gate E1 eligibility manifest is not canonical JSON")
    expected_keys = {
        "created_at",
        "eligibility",
        "evidence_status",
        "field_contract_sha256",
        "limits",
        "manifest_schema_version",
        "observed",
        "packet_id",
        "packet_sha256",
        "pagination_checks",
        "planned_requests",
        "probe",
        "request_plan_sha256",
        "results",
        "stop",
        "terminal_state",
    }
    try:
        created_at = manifest["created_at"]
        parsed_created_at = datetime.fromisoformat(created_at)
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("invalid Gate E1 eligibility timestamp") from error
    slots = gate_e1_request_plan()
    if (
        not isinstance(manifest, dict)
        or set(manifest) != expected_keys
        or not isinstance(created_at, str)
        or not created_at.endswith("Z")
        or parsed_created_at.tzinfo != UTC
        or manifest.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION
        or manifest.get("probe") != PROBE
        or manifest.get("packet_id") != PACKET_ID
        or manifest.get("packet_sha256") != gate_e1_eligibility_packet_sha256()
        or manifest.get("request_plan_sha256") != gate_e1_plan_sha256(slots)
        or manifest.get("field_contract_sha256") != field_contract_sha256()
        or manifest.get("limits") != gate_e1_eligibility_packet()["limits"]
        or manifest.get("planned_requests") != [slot.safe_record for slot in slots]
        or manifest.get("evidence_status") != "observed"
    ):
        raise ValueError("invalid Gate E1 eligibility manifest")
    results = manifest.get("results")
    if not isinstance(results, list) or not 1 <= len(results) <= MAX_REQUESTS:
        raise ValueError("invalid Gate E1 eligibility result count")
    if [result.get("request_id") for result in results] != [
        slot.request_id for slot in slots[: len(results)]
    ]:
        raise ValueError("Gate E1 eligibility results are not a contiguous plan prefix")
    if any(not isinstance(result, dict) for result in results):
        raise ValueError("invalid Gate E1 eligibility result")

    raw_dir = run_dir / "raw"
    if raw_dir.is_symlink() or not raw_dir.is_dir():
        raise ValueError("invalid Gate E1 eligibility raw directory")
    raw_entries = list(raw_dir.iterdir())
    if any(path.is_symlink() or not path.is_file() for path in raw_entries):
        raise ValueError("invalid Gate E1 eligibility raw entry")
    expected_raw_paths: set[str] = set()
    parsed_by_id: dict[str, ParsedResponse] = {}
    identities_by_id: dict[str, tuple[tuple[str, ...], ...]] = {}
    retained_raw_bytes = 0
    response_bytes_read = 0
    row_count = 0
    expected_result_keys = set(_base_result(slots[0], 1))
    for ordinal, (slot, result) in enumerate(zip(slots, results, strict=False), start=1):
        if set(result) != expected_result_keys:
            raise ValueError(f"invalid result fields: {slot.request_id}")
        safe_metadata = {key: result.get(key) for key in slot.safe_record}
        if safe_metadata != slot.safe_record or result.get("attempt_ordinal") != ordinal:
            raise ValueError(f"invalid result metadata: {slot.request_id}")
        headers = result.get("headers")
        if (
            not isinstance(headers, dict)
            or any(key not in _SELECTED_HEADERS for key in headers)
            or any(not isinstance(value, str) for value in headers.values())
        ):
            raise ValueError(f"invalid safe headers: {slot.request_id}")
        response_bytes = result.get("response_bytes")
        response_sha256 = result.get("response_sha256")
        if (
            not isinstance(response_bytes, int)
            or not 0 <= response_bytes <= slot.max_response_bytes + 1
            or (
                response_sha256 is not None
                and (
                    not isinstance(response_sha256, str)
                    or len(response_sha256) != 64
                    or any(character not in "0123456789abcdef" for character in response_sha256)
                )
            )
        ):
            raise ValueError(f"invalid response fingerprint: {slot.request_id}")
        prior_response_bytes_read = response_bytes_read
        response_bytes_read += response_bytes
        if result.get("outcome") == "success":
            if (
                result.get("failure_category") is not None
                or result.get("http_status") != 200
                or result.get("provider_result_code") != "00"
                or result.get("transport_category") is not None
                or result.get("envelope")
                not in {"documented_top_level", "observed_response_wrapper"}
                or not isinstance(result.get("total_count"), int)
                or not isinstance(result.get("observed_rows"), int)
                or not isinstance(result.get("raw_path"), str)
                or response_sha256 is None
                or response_bytes > slot.max_response_bytes
            ):
                raise ValueError(f"invalid success result: {slot.request_id}")
            expected_path = Path("raw") / f"{ordinal:02d}_{slot.request_id}.json"
            if result["raw_path"] != expected_path.as_posix():
                raise ValueError(f"invalid raw path: {slot.request_id}")
            body = (run_dir / expected_path).read_bytes()
            if len(body) != response_bytes or hashlib.sha256(body).hexdigest() != response_sha256:
                raise ValueError(f"raw evidence mismatch: {slot.request_id}")
            parsed = _parse_response(json.loads(body), slot)
            identities = _semantic_rows(slot, parsed)
            if (
                parsed.envelope != result["envelope"]
                or parsed.total_count != result["total_count"]
                or len(parsed.rows) != result["observed_rows"]
            ):
                raise ValueError(f"parsed evidence mismatch: {slot.request_id}")
            parsed_by_id[slot.request_id] = parsed
            identities_by_id[slot.request_id] = identities
            expected_raw_paths.add(expected_path.as_posix())
            retained_raw_bytes += len(body)
            row_count += len(parsed.rows)
        else:
            if (
                result.get("outcome") != "failure"
                or result.get("failure_category") not in FAILURE_CATEGORIES
                or result.get("raw_path") is not None
                or result.get("observed_rows") != 0
                or result.get("total_count") is not None
                or ordinal != len(results)
            ):
                raise ValueError(f"invalid failure result: {slot.request_id}")
            category = result["failure_category"]
            if category not in _allowed_failure_categories(slot):
                raise ValueError(f"impossible failure category: {slot.request_id}")
            if category == "transport":
                if (
                    result.get("http_status") is not None
                    or result.get("transport_category")
                    not in {"dns", "timeout", "tls", "transport"}
                    or headers
                    or response_bytes != 0
                    or response_sha256 is not None
                ):
                    raise ValueError(f"invalid transport failure: {slot.request_id}")
            elif result.get("transport_category") is not None:
                raise ValueError(f"invalid non-transport failure: {slot.request_id}")
            if category in {"redirect", "secret_header"}:
                if (
                    result.get("http_status") is not None
                    or headers
                    or response_bytes != 0
                    or response_sha256 is not None
                    or result.get("provider_result_code") is not None
                    or result.get("envelope") is not None
                ):
                    raise ValueError(f"invalid pre-body failure: {slot.request_id}")
            elif category == "content_type":
                if (
                    result.get("http_status") != 200
                    or response_bytes != 0
                    or response_sha256 is not None
                    or result.get("provider_result_code") is not None
                    or result.get("envelope") is not None
                ):
                    raise ValueError(f"invalid content-type failure: {slot.request_id}")
            elif category == "byte_budget":
                overflow_boundary = (
                    min(slot.max_response_bytes, MAX_RAW_BYTES - prior_response_bytes_read) + 1
                )
                if (
                    result.get("http_status") != 200
                    or response_bytes not in {0, overflow_boundary}
                    or response_sha256 is not None
                    or result.get("provider_result_code") is not None
                    or result.get("envelope") is not None
                ):
                    raise ValueError(f"invalid byte-budget failure: {slot.request_id}")
            elif category == "http_status":
                if (
                    not isinstance(result.get("http_status"), int)
                    or result["http_status"] == 200
                    or not 100 <= result["http_status"] <= 599
                    or response_bytes != 0
                    or response_sha256 is not None
                    or result.get("provider_result_code") is not None
                    or result.get("envelope") is not None
                ):
                    raise ValueError(f"invalid HTTP failure: {slot.request_id}")
            elif category == "provider_result_code":
                code = result.get("provider_result_code")
                if (
                    result.get("http_status") != 200
                    or not isinstance(code, str)
                    or len(code) != 2
                    or not code.isascii()
                    or not code.isdigit()
                    or code == "00"
                    or result.get("envelope")
                    not in {"documented_top_level", "observed_response_wrapper"}
                    or response_bytes <= 0
                    or response_bytes > slot.max_response_bytes
                    or response_sha256 is None
                ):
                    raise ValueError(f"invalid provider failure: {slot.request_id}")
            elif category in UNPARSED_BODY_FAILURE_CATEGORIES and (
                result.get("http_status") != 200
                or response_bytes <= 0
                or response_bytes > slot.max_response_bytes
                or response_sha256 is None
                or result.get("provider_result_code") is not None
                or result.get("envelope") is not None
            ):
                raise ValueError(f"invalid unparsed-body failure: {slot.request_id}")
            elif category == "schema" and (
                (result.get("provider_result_code") == "00" and result.get("envelope") is None)
                or result.get("http_status") != 200
                or response_bytes <= 0
                or response_bytes > slot.max_response_bytes
                or response_sha256 is None
                or result.get("provider_result_code") not in {None, "00"}
                or result.get("envelope")
                not in {None, "documented_top_level", "observed_response_wrapper"}
            ):
                raise ValueError(f"invalid schema failure: {slot.request_id}")
            elif category in PARSED_BODY_FAILURE_CATEGORIES and (
                result.get("http_status") != 200
                or response_bytes <= 0
                or response_bytes > slot.max_response_bytes
                or response_sha256 is None
                or result.get("provider_result_code") != "00"
                or result.get("envelope")
                not in {"documented_top_level", "observed_response_wrapper"}
            ):
                raise ValueError(f"invalid parsed-body failure: {slot.request_id}")
    actual_raw_paths = {path.relative_to(run_dir).as_posix() for path in raw_entries}
    if actual_raw_paths != expected_raw_paths:
        raise ValueError("Gate E1 eligibility raw-file set mismatch")

    complete = len(results) == MAX_REQUESTS and all(
        result.get("outcome") == "success" for result in results
    )
    expected_terminal = "complete" if complete else "stopped"
    last = results[-1]
    expected_stop = (
        None
        if complete
        else {"category": last.get("failure_category"), "ordinal": last.get("attempt_ordinal")}
    )
    if manifest.get("terminal_state") != expected_terminal or manifest.get("stop") != expected_stop:
        raise ValueError("Gate E1 eligibility terminal state mismatch")
    pagination = _pagination_checks(parsed_by_id, identities_by_id)
    if manifest.get("pagination_checks") != pagination:
        raise ValueError("Gate E1 eligibility pagination evidence mismatch")
    eligibility = evaluate_gate_e1_eligibility(
        terminal_state=expected_terminal,
        parsed_by_id=parsed_by_id,
        pagination_checks=pagination,
    )
    if manifest.get("eligibility") != eligibility:
        raise ValueError("Gate E1 eligibility decision mismatch")
    expected_observed = {
        "attempted_requests": len(results),
        "retained_raw_bytes": retained_raw_bytes,
        "rows": row_count,
        "response_bytes_read": response_bytes_read,
        "retries": 0,
    }
    if manifest.get("observed") != expected_observed:
        raise ValueError("Gate E1 eligibility observed totals mismatch")
    if row_count > MAX_ROWS or response_bytes_read > MAX_RAW_BYTES:
        raise GateE1Stop("Gate E1 eligibility evidence exceeds packet budget")
    return {
        "eligibility": eligibility,
        "observed": expected_observed,
        "terminal_state": expected_terminal,
    }
