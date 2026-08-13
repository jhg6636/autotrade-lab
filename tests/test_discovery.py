import copy
import json
from pathlib import Path

from autotrade_lab.research.discovery import compare_records, discover, fingerprint
from autotrade_lab.research.validation import load_strategy_record

FIXTURES = Path(__file__).parents[1] / "research" / "fixtures" / "strategies"


def record(name: str) -> dict:
    return load_strategy_record(FIXTURES / name)


def test_exact_repost_is_duplicate_source_candidate():
    left = record("academic_momentum.json")
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_repost"
    right["sources"][0]["title"] = "Reposted claim"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "duplicate"
    assert suggestion["action"] == "source_candidate"
    assert {reason["field"] for reason in suggestion["reasons"]} == set(fingerprint(left))


def test_parameter_change_is_preserved_as_variant():
    left = record("academic_momentum.json")
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_variant"
    right["sizing_rule"] = "equal risk"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert suggestion["action"] == "preserve_variant"
    assert suggestion["reasons"] == [{"field": "sizing_rule", "reason": "normalized value differs"}]


def test_execution_change_is_preserved_as_variant():
    left = record("academic_momentum.json")
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_execution_variant"
    right["execution_assumptions"] = ["paper execution only"]
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert suggestion["action"] == "preserve_variant"
    assert suggestion["reasons"] == [
        {"field": "execution_assumptions", "reason": "normalized value differs"}
    ]


def test_market_execution_scope_swap_is_preserved_as_variant():
    left = record("academic_momentum.json")
    left["markets"] = ["crypto_spot", "crypto_perp"]
    left["applications"].append(
        {
            "market": "crypto_perp",
            "asset_direction": "long_short",
            "execution_scope": "context_only",
            "target_exposure": {"minimum": -1, "maximum": 1},
        }
    )
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_scope_swap"
    right["applications"][0]["execution_scope"] = "context_only"
    right["applications"][1]["execution_scope"] = "executable"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert {reason["field"] for reason in suggestion["reasons"]} == {"application_execution_scope"}


def test_merely_related_strategy_is_not_mergeable():
    left = record("academic_momentum.json")
    right = record("community_rsi.json")
    right["markets"] = ["crypto_spot"]
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "related_to"
    assert suggestion["action"] == "no_merge"
    assert suggestion["reasons"]


def test_dry_run_report_does_not_modify_records(tmp_path):
    from autotrade_lab.research.discovery import run_dry_run

    before = {path.name: path.read_text(encoding="utf-8") for path in FIXTURES.glob("*.json")}
    report = run_dry_run(FIXTURES, tmp_path / "report.json")
    assert report["automatic_merge"] is False
    assert json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))["mode"] == "dry_run"
    assert before == {
        path.name: path.read_text(encoding="utf-8") for path in FIXTURES.glob("*.json")
    }


def test_discovery_order_is_deterministic():
    records = [record("community_rsi.json"), record("academic_momentum.json")]
    assert discover(records) == discover(list(reversed(records)))
