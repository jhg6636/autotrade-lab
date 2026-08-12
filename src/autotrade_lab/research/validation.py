from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class StrategyRecordError(ValueError):
    """A strategy record violates the source-neutral research contract."""


_SCHEMA_PATH = Path(__file__).parents[3] / "research" / "schema" / "strategy.schema.json"


def _fail(path: str, message: str) -> None:
    raise StrategyRecordError(f"{path}: {message}")


def _schema_validator() -> Draft202012Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _error_path(error: Any) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def _format_schema_error(error: Any) -> tuple[str, str]:
    path = _error_path(error)
    if error.validator == "required":
        missing = error.message.split("'")[1]
        return f"{path}.{missing}", "is a required property"
    return path, error.message


def validate_strategy_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a record, with field paths in errors.

    The JSON Schema is the single contract used at runtime and by external tooling. Additional
    Python checks are limited to invariants that JSON Schema cannot express clearly.
    """
    errors = sorted(
        _schema_validator().iter_errors(record), key=lambda item: list(item.absolute_path)
    )
    if errors:
        error = errors[0]
        path, message = _format_schema_error(error)
        _fail(path, message)
    exposure = record.get("target_exposure")
    if exposure and exposure["minimum"] > exposure["maximum"]:
        _fail("$.target_exposure", "minimum cannot exceed maximum")
    application_markets = [application["market"] for application in record["applications"]]
    if len(application_markets) != len(set(application_markets)):
        _fail("$.applications", "must contain at most one application per market")
    if set(application_markets) != set(record["markets"]):
        _fail("$.applications", "markets must exactly match the top-level markets summary")
    for index, application in enumerate(record["applications"]):
        exposure = application["target_exposure"]
        if exposure["minimum"] > exposure["maximum"]:
            _fail(f"$.applications[{index}].target_exposure", "minimum cannot exceed maximum")
    directions = {application["asset_direction"] for application in record["applications"]}
    expected_direction = directions.pop() if len(directions) == 1 else "mixed"
    if record["asset_direction"] != expected_direction:
        _fail(
            "$.asset_direction",
            f"must summarize applications as {expected_direction!r}",
        )
    scopes = {application["execution_scope"] for application in record["applications"]}
    expected_scope = "executable" if "executable" in scopes else "context_only"
    if record["execution_scope"] != expected_scope:
        _fail(
            "$.execution_scope",
            f"must summarize applications as {expected_scope!r}",
        )
    return record


def load_strategy_record(path: str | Path) -> dict[str, Any]:
    record_path = Path(path)
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StrategyRecordError(f"{record_path}: invalid JSON: {exc.msg}") from exc
    return validate_strategy_record(record)
