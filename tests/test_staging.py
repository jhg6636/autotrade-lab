import json
from pathlib import Path

import pytest

from autotrade_lab.research.staging import (
    StagingValidationError,
    aggregate,
    candidate_to_strategy_record,
    load_jsonl,
)

ROOT = Path(__file__).parents[1]
LUNA101 = ROOT / "research" / "staging" / "fixtures" / "luna-101"
LUNA104 = ROOT / "research" / "staging" / "fixtures" / "luna-104"


def test_synthetic_lanes_have_five_source_and_candidate_records():
    assert len(load_jsonl(LUNA101 / "sources.jsonl", "sources")) == 5
    assert len(load_jsonl(LUNA101 / "hypotheses.jsonl", "hypotheses")) == 5
    assert len(load_jsonl(LUNA104 / "sources.jsonl", "sources")) == 5
    assert len(load_jsonl(LUNA104 / "hypotheses.jsonl", "hypotheses")) == 5


def test_aggregate_is_deterministic_and_non_mutating(tmp_path):
    before = {path: path.read_bytes() for path in LUNA101.glob("*.jsonl")}
    first = aggregate(LUNA101)
    second = aggregate(LUNA101)
    assert first == second
    assert first["counts"] == {
        "sources": 5,
        "hypotheses": 5,
        "inaccessible": 0,
        "relations": 0,
        "execution_audit": 0,
        "suggestions": len(first["suggestions"]),
    }
    assert first["automatic_merge"] is False
    assert first["canonical_records_modified"] is False
    assert before == {path: path.read_bytes() for path in LUNA101.glob("*.jsonl")}


def test_korean_pilot_passes_long_only_and_timeframe_rules():
    report = aggregate(LUNA104)
    assert report["counts"]["sources"] == 5
    assert report["counts"]["hypotheses"] == 5


def test_malformed_source_has_line_number_and_field_path():
    with pytest.raises(StagingValidationError, match=r"sources:1:\$\.accessed_at"):
        load_jsonl(LUNA101 / "malformed.jsonl", "sources")


def test_malformed_korean_audit_is_rejected():
    with pytest.raises(StagingValidationError, match=r"execution_audit:1"):
        load_jsonl(LUNA104 / "malformed.jsonl", "execution_audit")


def test_duplicate_and_dangling_references_are_rejected(tmp_path):
    source = {
        "source_id": "synthetic_source",
        "title": "Synthetic",
        "author_or_handle": "Synthetic",
        "url": "https://example.org/source",
        "published_at": None,
        "accessed_at": "2026-08-20",
        "language": "en",
        "source_type": "other",
        "claim_summary": "Synthetic; unverified.",
        "status": "incomplete",
        "entry_rule": "unknown",
        "exit_rule": "unknown",
        "sizing_rule": "unknown",
        "universe": "unknown",
        "timeframes": ["daily"],
        "required_data": ["unknown"],
        "ambiguities": ["incomplete"],
        "claimed_results": ["unverified"],
    }
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n" + json.dumps(source) + "\n")
    with pytest.raises(StagingValidationError, match="duplicate ID"):
        load_jsonl(tmp_path / "sources.jsonl", "sources")


def test_adapter_rejects_dangling_source_reference():
    candidate = load_jsonl(LUNA101 / "hypotheses.jsonl", "hypotheses")[0]
    with pytest.raises(StagingValidationError, match="dangling source_ids"):
        candidate_to_strategy_record(candidate, set())
