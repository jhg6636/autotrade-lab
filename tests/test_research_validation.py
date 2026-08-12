import json
from pathlib import Path

import pytest

from autotrade_lab.research.validation import (
    StrategyRecordError,
    load_strategy_record,
    validate_strategy_record,
)

FIXTURES = Path(__file__).parents[1] / "research" / "fixtures" / "strategies"


def read(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_all_luna_001_fixtures_validate():
    for path in FIXTURES.glob("*.json"):
        assert load_strategy_record(path)["id"]


def test_missing_entry_rule_has_field_path():
    record = read("academic_momentum.json")
    del record["entry_rule"]
    with pytest.raises(StrategyRecordError, match=r"\$\.entry_rule: is a required property"):
        validate_strategy_record(record)


def test_source_type_does_not_change_validation():
    community = read("community_rsi.json")
    community["sources"][0]["source_type"] = "academic_paper"
    validate_strategy_record(community)
    community["sources"][0]["source_type"] = "community_post"
    validate_strategy_record(community)


def test_korean_stock_negative_direction_is_rejected():
    record = read("original_gap_fade.json")
    record["applications"][0]["asset_direction"] = "long_short"
    with pytest.raises(StrategyRecordError, match="asset_direction"):
        validate_strategy_record(record)


def test_korean_stock_negative_target_exposure_is_rejected():
    record = read("original_gap_fade.json")
    record["applications"][0]["target_exposure"] = {"minimum": -1, "maximum": 1}
    with pytest.raises(StrategyRecordError, match="target_exposure.minimum"):
        validate_strategy_record(record)


def test_korean_short_is_allowed_as_context_only():
    record = read("original_gap_fade.json")
    record["execution_scope"] = "context_only"
    record["applications"][0]["execution_scope"] = "context_only"
    record["applications"][0]["asset_direction"] = "long_short"
    record["applications"][0]["target_exposure"] = {"minimum": -1, "maximum": 1}
    assert validate_strategy_record(record)["execution_scope"] == "context_only"


def test_invalid_calendar_date_is_rejected():
    record = read("community_rsi.json")
    record["sources"][0]["accessed_at"] = "2026-02-31"
    with pytest.raises(StrategyRecordError, match=r"sources\[0\].accessed_at"):
        validate_strategy_record(record)


def test_malformed_source_has_field_path():
    record = read("community_rsi.json")
    del record["sources"][0]["accessed_at"]
    with pytest.raises(StrategyRecordError, match=r"sources\[0\].*accessed_at"):
        validate_strategy_record(record)
