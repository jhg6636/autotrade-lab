"""Validation and deterministic aggregation for pre-canonical discovery JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from autotrade_lab.research.discovery import discover

ROOT = Path(__file__).parents[3]
SCHEMA_DIR = ROOT / "research" / "schema"
KINDS = ("sources", "hypotheses", "inaccessible", "relations", "execution_audit")
SCHEMAS = {
    kind: SCHEMA_DIR / f"{kind[:-1] if kind != 'execution_audit' else kind}.schema.json"
    for kind in KINDS
}
SCHEMAS["sources"] = SCHEMA_DIR / "source_capture.schema.json"
SCHEMAS["hypotheses"] = SCHEMA_DIR / "hypothesis_candidate.schema.json"


class StagingValidationError(ValueError):
    """A JSONL staging record or cross-reference is invalid."""


def _validator(kind: str) -> Draft202012Validator:
    schema = json.loads(SCHEMAS[kind].read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _path(error: Any) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def _id_field(kind: str) -> str:
    return {
        "sources": "source_id",
        "hypotheses": "hypothesis_id",
        "inaccessible": "source_id",
        "relations": "relation_id",
        "execution_audit": "audit_id",
    }[kind]


def _unknown(value: Any) -> bool:
    return isinstance(value, str) and (value == "unknown" or value.startswith("unknown:"))


def validate_record(kind: str, record: dict[str, Any], line: int = 1) -> dict[str, Any]:
    if kind not in KINDS:
        raise StagingValidationError(f"unknown JSONL kind: {kind}")
    errors = sorted(
        _validator(kind).iter_errors(record), key=lambda error: list(error.absolute_path)
    )
    if errors:
        error = errors[0]
        raise StagingValidationError(f"{kind}:{line}:{_path(error)}: {error.message}")
    if kind in {"sources", "hypotheses"} and record["status"] == "usable":
        fields = (
            ("entry_rule", "exit_rule", "sizing_rule", "universe")
            if kind == "sources"
            else ("entry_rule", "exit_rule", "sizing_rule", "hypothesis")
        )
        missing = [field for field in fields if _unknown(record[field])]
        if missing:
            raise StagingValidationError(
                f"{kind}:{line}:$.status: usable record has unknown fields: {', '.join(missing)}"
            )
    if (
        kind == "sources"
        and record["status"] == "inaccessible"
        and not record.get("inaccessible_reason")
    ):
        raise StagingValidationError(
            f"{kind}:{line}:$.inaccessible_reason: required for inaccessible source"
        )
    if kind == "hypotheses":
        markets = {application["market"] for application in record["applications"]}
        if markets != set(record["markets"]):
            raise StagingValidationError(
                f"{kind}:{line}:$.applications: markets must match markets"
            )
        if any(
            application["target_exposure"]["minimum"] > application["target_exposure"]["maximum"]
            for application in record["applications"]
        ):
            raise StagingValidationError(
                f"{kind}:{line}:$.applications: minimum exposure exceeds maximum"
            )
        for application in record["applications"]:
            if (
                application["market"] in {"kr_equity", "kr_etf"}
                and application["execution_scope"] == "executable"
                and (
                    application["asset_direction"] != "long_only"
                    or application["target_exposure"]["minimum"] < 0
                )
            ):
                raise StagingValidationError(
                    f"{kind}:{line}:$.applications: Korean executable application must be long_only with nonnegative exposure"
                )
        if record["execution_scope"] == "executable" and markets & {"kr_equity", "kr_etf"}:
            invalid = set(record["timeframes"]) - {"daily", "one_minute"}
            if invalid:
                raise StagingValidationError(
                    f"{kind}:{line}:$.timeframes: Korean executable timeframe not allowed: {sorted(invalid)}"
                )
    if kind == "execution_audit":
        exposure = record["target_exposure"]
        if exposure["minimum"] > exposure["maximum"]:
            raise StagingValidationError(
                f"{kind}:{line}:$.target_exposure: minimum exceeds maximum"
            )
        if record["execution_scope"] == "executable" and (
            record["asset_direction"] != "long_only" or exposure["minimum"] < 0
        ):
            raise StagingValidationError(
                f"{kind}:{line}:$.execution_scope: Korean executable audit must be long_only with nonnegative exposure"
            )
    return record


def load_jsonl(path: str | Path, kind: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    record_path = Path(path)
    if not record_path.exists():
        return records
    for line_number, raw in enumerate(record_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StagingValidationError(f"{kind}:{line_number}: invalid JSON: {exc.msg}") from exc
        validate_record(kind, record, line_number)
        key = record[_id_field(kind)]
        if key in seen:
            raise StagingValidationError(f"{kind}:{line_number}: duplicate ID {key!r}")
        seen.add(key)
        records.append(record)
    return records


def candidate_to_strategy_record(candidate: dict[str, Any], source_ids: set[str]) -> dict[str, Any]:
    """Adapt a validated staging candidate to the discovery comparator shape."""
    if not set(candidate["source_ids"]).issubset(source_ids):
        missing = sorted(set(candidate["source_ids"]) - source_ids)
        raise StagingValidationError(f"hypotheses: dangling source_ids: {', '.join(missing)}")
    return {
        "id": candidate["hypothesis_id"],
        "canonical_name": candidate["canonical_name"],
        "family": candidate["family"],
        "markets": candidate["markets"],
        "asset_direction": candidate["asset_direction"],
        "execution_scope": candidate["execution_scope"],
        "applications": candidate["applications"],
        "timeframes": candidate["timeframes"],
        "entry_rule": candidate["entry_rule"],
        "exit_rule": candidate["exit_rule"],
        "sizing_rule": candidate["sizing_rule"],
        "required_data": candidate["required_data"],
        "execution_assumptions": candidate.get("execution_assumptions", []),
    }


def aggregate(staging_dir: str | Path) -> dict[str, Any]:
    directory = Path(staging_dir)
    sources = load_jsonl(directory / "sources.jsonl", "sources")
    hypotheses = load_jsonl(directory / "hypotheses.jsonl", "hypotheses")
    inaccessible = load_jsonl(directory / "inaccessible.jsonl", "inaccessible")
    relations = load_jsonl(directory / "relations.jsonl", "relations")
    audits = load_jsonl(directory / "execution_audit.jsonl", "execution_audit")
    source_ids = {item["source_id"] for item in sources}
    hypothesis_ids = {item["hypothesis_id"] for item in hypotheses}
    for item in inaccessible:
        if item["source_id"] not in source_ids:
            raise StagingValidationError(f"inaccessible: dangling source_id {item['source_id']!r}")
    for item in relations:
        if (
            item["left_hypothesis_id"] not in hypothesis_ids
            or item["right_hypothesis_id"] not in hypothesis_ids
        ):
            raise StagingValidationError(
                f"relations: dangling hypothesis reference in {item['relation_id']!r}"
            )
    for item in audits:
        if item["hypothesis_id"] not in hypothesis_ids:
            raise StagingValidationError(
                f"execution_audit: dangling hypothesis_id {item['hypothesis_id']!r}"
            )
    adapted = [candidate_to_strategy_record(item, source_ids) for item in hypotheses]
    suggestions = discover(adapted)
    return {
        "mode": "staging_dry_run",
        "staging_dir": str(directory),
        "counts": {
            "sources": len(sources),
            "hypotheses": len(hypotheses),
            "inaccessible": len(inaccessible),
            "relations": len(relations),
            "execution_audit": len(audits),
            "suggestions": len(suggestions),
        },
        "suggestions": suggestions,
        "automatic_merge": False,
        "canonical_records_modified": False,
    }
