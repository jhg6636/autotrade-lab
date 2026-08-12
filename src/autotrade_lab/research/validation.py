from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class StrategyRecordError(ValueError):
    """A strategy record violates the source-neutral research contract."""


_ID = re.compile(r"^[a-z0-9][a-z0-9_]{2,63}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MARKETS = {"kr_equity", "kr_etf", "crypto_spot", "crypto_perp", "us_equity", "multi_asset"}
_DIRECTIONS = {"long_only", "long_short", "delta_neutral", "market_making", "directionless"}
_STATUS = {"hypothesis", "baseline_ready", "planned", "implemented", "blocked", "out_of_scope"}
_SOURCE_TYPES = {
    "academic_paper",
    "book",
    "institutional_research",
    "broker_material",
    "exchange_documentation",
    "code",
    "community_post",
    "video",
    "blog",
    "interview",
    "original_observation",
    "other",
}
_REQUIRED = (
    "id",
    "canonical_name",
    "aliases",
    "family",
    "markets",
    "asset_direction",
    "timeframes",
    "sources",
    "hypothesis",
    "entry_rule",
    "exit_rule",
    "sizing_rule",
    "required_data",
    "execution_assumptions",
    "variants",
    "ambiguities",
    "status",
)


def _fail(path: str, message: str) -> None:
    raise StrategyRecordError(f"{path}: {message}")


def _string(value: Any, path: str, *, nonempty: bool = True) -> None:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        _fail(path, "must be a non-empty string")


def _list(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (nonempty and not value):
        _fail(path, "must be a non-empty array" if nonempty else "must be an array")
    return value


def _unique_strings(value: Any, path: str, *, nonempty: bool = False) -> None:
    values = _list(value, path, nonempty=nonempty)
    for index, item in enumerate(values):
        _string(item, f"{path}[{index}]")
    if len(values) != len(set(values)):
        _fail(path, "must not contain duplicates")


def validate_strategy_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a record, with field paths in errors.

    This intentionally has no third-party runtime dependency. The JSON Schema remains the
    interchange contract; this validator enforces the subset needed by the repository and the
    domain rule that Korean equity/ETF records are long-only.
    """
    if not isinstance(record, dict):
        _fail("$", "must be an object")
    missing = [key for key in _REQUIRED if key not in record]
    if missing:
        _fail("$", f"missing required field(s): {', '.join(missing)}")
    allowed = set(_REQUIRED) | {"implementation", "target_exposure"}
    unknown = sorted(set(record) - allowed)
    if unknown:
        _fail("$", f"unexpected field(s): {', '.join(unknown)}")

    _string(record["id"], "id")
    if not _ID.fullmatch(record["id"]):
        _fail("id", "must match ^[a-z0-9][a-z0-9_]{2,63}$")
    _string(record["canonical_name"], "canonical_name")
    _unique_strings(record["aliases"], "aliases")
    _string(record["family"], "family")
    markets = _list(record["markets"], "markets", nonempty=True)
    for index, market in enumerate(markets):
        if market not in _MARKETS:
            _fail(f"markets[{index}]", f"unsupported market {market!r}")
    if len(markets) != len(set(markets)):
        _fail("markets", "must not contain duplicates")
    direction = record["asset_direction"]
    if direction not in _DIRECTIONS:
        _fail("asset_direction", f"unsupported direction {direction!r}")
    _unique_strings(record["timeframes"], "timeframes", nonempty=True)
    _string(record["hypothesis"], "hypothesis")
    for field in ("entry_rule", "exit_rule", "sizing_rule"):
        _string(record[field], field)
    _unique_strings(record["required_data"], "required_data", nonempty=True)
    _unique_strings(record["execution_assumptions"], "execution_assumptions")
    _unique_strings(record["ambiguities"], "ambiguities")
    if record["status"] not in _STATUS:
        _fail("status", f"unsupported status {record['status']!r}")

    for index, source in enumerate(_list(record["sources"], "sources", nonempty=True)):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            _fail(path, "must be an object")
        required = (
            "source_type",
            "title",
            "author_or_handle",
            "url",
            "accessed_at",
            "language",
            "claim_summary",
        )
        missing_source = [key for key in required if key not in source]
        if missing_source:
            _fail(path, f"missing required field(s): {', '.join(missing_source)}")
        if set(source) - set(required) - {"published_at", "verbatim_excerpt"}:
            _fail(path, "contains an unexpected field")
        if source["source_type"] not in _SOURCE_TYPES:
            _fail(f"{path}.source_type", f"unsupported source type {source['source_type']!r}")
        for field in ("title", "author_or_handle", "url", "language", "claim_summary"):
            _string(source[field], f"{path}.{field}")
        _string(source["accessed_at"], f"{path}.accessed_at")
        if not _DATE.fullmatch(source["accessed_at"]):
            _fail(f"{path}.accessed_at", "must use YYYY-MM-DD")
        for field in ("published_at", "verbatim_excerpt"):
            if field in source and source[field] is not None:
                _string(source[field], f"{path}.{field}")

    for index, variant in enumerate(_list(record["variants"], "variants")):
        path = f"variants[{index}]"
        if not isinstance(variant, dict) or set(variant) != {"id", "description"}:
            _fail(path, "must contain exactly id and description")
        _string(variant["id"], f"{path}.id")
        _string(variant["description"], f"{path}.description")

    if "implementation" in record:
        implementation = record["implementation"]
        if not isinstance(implementation, dict) or set(implementation) != {"path", "symbol"}:
            _fail("implementation", "must contain exactly path and symbol")
        _string(implementation["path"], "implementation.path")
        _string(implementation["symbol"], "implementation.symbol")

    if "target_exposure" in record:
        exposure = record["target_exposure"]
        if not isinstance(exposure, dict) or set(exposure) != {"minimum", "maximum"}:
            _fail("target_exposure", "must contain exactly minimum and maximum")
        for field in ("minimum", "maximum"):
            if not isinstance(exposure[field], (int, float)) or isinstance(exposure[field], bool):
                _fail(f"target_exposure.{field}", "must be a number")
            if not -1 <= exposure[field] <= 1:
                _fail(f"target_exposure.{field}", "must be between -1 and 1")
        if exposure["minimum"] > exposure["maximum"]:
            _fail("target_exposure", "minimum cannot exceed maximum")

    if set(markets) & {"kr_equity", "kr_etf"} and direction != "long_only":
        _fail("asset_direction", "Korean equity/ETF executable records must be long_only")
    if (
        set(markets) & {"kr_equity", "kr_etf"}
        and "target_exposure" in record
        and record["target_exposure"]["minimum"] < 0
    ):
        _fail(
            "target_exposure.minimum",
            "Korean equity/ETF executable records cannot target negative exposure",
        )
    return record


def load_strategy_record(path: str | Path) -> dict[str, Any]:
    record_path = Path(path)
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StrategyRecordError(f"{record_path}: invalid JSON: {exc.msg}") from exc
    return validate_strategy_record(record)
