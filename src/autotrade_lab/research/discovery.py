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
    "execution_assumptions",
    "application_execution_scope",
    "asset_direction",
    "target_exposure_profile",
    "mechanism_identity",
)
MECHANISM_FIELDS = (
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


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return value == "unknown" or value.startswith("unknown:")
    if isinstance(value, (list, tuple)):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def fingerprint(record: dict[str, Any]) -> dict[str, Any]:
    """Return the normalized mechanism fingerprint used for comparisons."""
    return {
        "markets": _normalize(record.get("markets", [])),
        "timeframes": _normalize(record.get("timeframes", [])),
        "signal_inputs": _normalize(record.get("signal_inputs", record.get("required_data", []))),
        "entry_rule": _normalize(record.get("entry_rule", "")),
        "exit_rule": _normalize(record.get("exit_rule", "")),
        "sizing_rule": _normalize(record.get("sizing_rule", "")),
        "mechanism_identity": _mechanism_identity(record),
        "execution_assumptions": _normalize(record.get("execution_assumptions", [])),
        "application_execution_scope": _normalize(
            sorted(
                (application.get("market"), application.get("execution_scope"))
                for application in record.get("applications", [])
            )
        ),
        "asset_direction": _normalize(record.get("asset_direction")),
        "target_exposure_profile": _normalize(
            {
                "top_level": record.get("target_exposure"),
                "applications": [
                    {
                        "market": application.get("market"),
                        "asset_direction": application.get("asset_direction"),
                        "target_exposure": application.get("target_exposure"),
                    }
                    for application in record.get("applications", [])
                ],
            }
        ),
    }


def _mechanism_identity(record: dict[str, Any]) -> str | None:
    """Recognize a small explicit template vocabulary; return None when unrecognized."""
    text = " ".join(_normalize(record.get(field, "")) for field in ("entry_rule", "exit_rule"))
    if re.search(r"\b(?:sma|moving average|moving-average)\b", text) and re.search(
        r"\bcross(?:es|over|ed|ing)?\b|crossover", text
    ):
        entry, exit_ = record.get("entry_rule", "").lower(), record.get("exit_rule", "").lower()
        entry_polarity = "above" if "above" in entry else "below" if "below" in entry else None
        exit_polarity = "above" if "above" in exit_ else "below" if "below" in exit_ else None

        def operand_relation(rule: str) -> str | None:
            operands = [
                int(value) for value in re.findall(r"(?:sma|moving average)[^0-9]*(\d+)", rule)
            ]
            if len(operands) < 2:
                return None
            return (
                "first_shorter"
                if operands[0] < operands[1]
                else "first_longer"
                if operands[0] > operands[1]
                else "equal"
            )

        entry_relation, exit_relation = operand_relation(entry), operand_relation(exit_)
        entry_side = (
            "long"
            if re.search(r"enter\s+long|go\s+long", entry)
            else "short"
            if re.search(r"enter\s+short|go\s+short", entry)
            else "unspecified"
        )
        return (
            f"moving_average_crossover:{entry_polarity}:{exit_polarity}:{entry_relation}:{exit_relation}:{entry_side}"
            if entry_polarity and exit_polarity and entry_relation and exit_relation
            else None
        )
    if re.search(r"\brsi\b", text) and re.search(r"threshold|cross", text):
        entry, exit_ = record.get("entry_rule", "").lower(), record.get("exit_rule", "").lower()
        entry_polarity = (
            "above"
            if re.search(r"overbought|above", entry)
            else "below"
            if re.search(r"oversold|below", entry)
            else None
        )
        exit_polarity = (
            "above"
            if re.search(r"overbought|above", exit_)
            else "below"
            if re.search(r"oversold|below", exit_)
            else None
        )
        entry_side = (
            "long"
            if re.search(r"enter\s+long|go\s+long", entry)
            else "short"
            if re.search(r"enter\s+short|go\s+short", entry)
            else "unspecified"
        )
        return (
            f"rsi_threshold:{entry_polarity}:{exit_polarity}:{entry_side}"
            if entry_polarity and exit_polarity
            else None
        )
    if "bollinger" in text and re.search(r"band|mean reversion|reversion", text):
        return None
    if "donchian" in text and re.search(r"breakout|channel", text):
        return None
    return None


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
    shared_markets = bool(set(left.get("markets", [])) & set(right.get("markets", [])))
    shared_family = bool(left.get("family")) and left.get("family") == right.get("family")
    if not shared_markets and not shared_family:
        return None
    incomplete_fields = [
        field
        for field in MECHANISM_FIELDS
        if _contains_placeholder(left_fp[field]) or _contains_placeholder(right_fp[field])
    ]
    if incomplete_fields:
        return {
            "left_id": ids[0],
            "right_id": ids[1],
            "relation": "insufficient_information",
            "action": "no_merge",
            "reasons": [
                {
                    "field": field,
                    "reason": "unknown or placeholder value prevents reliable comparison",
                }
                for field in incomplete_fields
            ],
        }
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
    same_mechanism = (
        shared_family
        and all(left_fp[field] == right_fp[field] for field in stable)
        and (
            left_fp["entry_rule"] == right_fp["entry_rule"]
            and left_fp["exit_rule"] == right_fp["exit_rule"]
            or (
                left_fp["mechanism_identity"] is not None
                and left_fp["mechanism_identity"] == right_fp["mechanism_identity"]
            )
        )
    )
    if same_mechanism:
        return {
            "left_id": ids[0],
            "right_id": ids[1],
            "relation": "variant_of",
            "action": "preserve_variant",
            "reasons": _field_reasons(
                left_fp,
                right_fp,
                tuple(field for field in FINGERPRINT_FIELDS if field not in stable),
            ),
        }
    if shared_markets or shared_family:
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
        "input_dir": "research/strategies"
        if directory == Path(__file__).parents[3] / "research" / "strategies"
        else str(directory),
        "record_ids": [record["id"] for record in records],
        "suggestions": discover(records),
        "automatic_merge": False,
    }
    if report_path is not None:
        target = Path(report_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
