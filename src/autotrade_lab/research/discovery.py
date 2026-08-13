"""Deterministic discovery and deduplication suggestions for strategy records.

This module only compares records. It never mutates a record or adds a source automatically.
"""

from __future__ import annotations

import json
import re
from itertools import combinations
from pathlib import Path
from typing import Any

FINGERPRINT_FIELDS = (
    "markets",
    "timeframes",
    "signal_inputs",
    "entry_rule",
    "exit_rule",
    "sizing_rule",
)


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip().lower())
    if isinstance(value, list):
        return tuple(sorted((_normalize(item) for item in value), key=repr))
    if isinstance(value, dict):
        return tuple((key, _normalize(value[key])) for key in sorted(value))
    return value


def fingerprint(record: dict[str, Any]) -> dict[str, Any]:
    """Return the normalized mechanism fingerprint used for comparisons."""
    return {
        "markets": _normalize(record.get("markets", [])),
        "timeframes": _normalize(record.get("timeframes", [])),
        "signal_inputs": _normalize(record.get("signal_inputs", record.get("required_data", []))),
        "entry_rule": _normalize(record.get("entry_rule", "")),
        "exit_rule": _normalize(record.get("exit_rule", "")),
        "sizing_rule": _normalize(record.get("sizing_rule", "")),
    }


def _field_reasons(
    left: dict[str, Any], right: dict[str, Any], fields: tuple[str, ...]
) -> list[dict[str, Any]]:
    reasons = []
    for field in fields:
        if left[field] != right[field]:
            reasons.append({"field": field, "reason": "normalized value differs"})
    return reasons


def compare_records(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any] | None:
    """Classify one pair, returning a suggestion with field-level reasons when related."""
    left_fp, right_fp = fingerprint(left), fingerprint(right)
    ids = (left["id"], right["id"])
    if left_fp == right_fp:
        return {
            "left_id": ids[0],
            "right_id": ids[1],
            "relation": "duplicate",
            "action": "source_candidate",
            "reasons": [
                {"field": field, "reason": "normalized value matches"}
                for field in FINGERPRINT_FIELDS
            ],
        }
    stable = ("markets", "timeframes", "signal_inputs")
    if all(left_fp[field] == right_fp[field] for field in stable):
        return {
            "left_id": ids[0],
            "right_id": ids[1],
            "relation": "variant_of",
            "action": "preserve_variant",
            "reasons": _field_reasons(
                left_fp, right_fp, ("entry_rule", "exit_rule", "sizing_rule")
            ),
        }
    if set(left.get("markets", [])) & set(right.get("markets", [])):
        return {
            "left_id": ids[0],
            "right_id": ids[1],
            "relation": "related_to",
            "action": "no_merge",
            "reasons": _field_reasons(left_fp, right_fp, FINGERPRINT_FIELDS),
        }
    return None


def discover(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return deterministic pair suggestions without mutating ``records``."""
    return [
        suggestion
        for left, right in combinations(sorted(records, key=lambda item: item["id"]), 2)
        if (suggestion := compare_records(left, right)) is not None
    ]


def run_dry_run(input_dir: str | Path, report_path: str | Path | None = None) -> dict[str, Any]:
    """Load records and write an explicit non-mutating discovery report."""
    from autotrade_lab.research.validation import load_strategy_record

    directory = Path(input_dir)
    records = [load_strategy_record(path) for path in sorted(directory.glob("*.json"))]
    report = {
        "mode": "dry_run",
        "input_dir": str(directory),
        "record_ids": [record["id"] for record in records],
        "suggestions": discover(records),
        "automatic_merge": False,
    }
    if report_path is not None:
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
