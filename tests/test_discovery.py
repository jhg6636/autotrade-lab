import copy
import json
from pathlib import Path

from autotrade_lab.research.discovery import compare_records, discover, fingerprint, run_dry_run
from autotrade_lab.research.validation import load_strategy_record

FIXTURES = Path(__file__).parents[1] / "research" / "fixtures" / "strategies"


def record(name: str) -> dict:
    return load_strategy_record(FIXTURES / name)


def test_exact_repost_is_duplicate_source_candidate():
    left = record("academic_momentum.json")
    left["required_data"] = ["close", "volume"]
    left["entry_rule"] = "enter when momentum exceeds threshold"
    left["exit_rule"] = "exit when momentum reverses"
    left["sizing_rule"] = "equal risk"
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_repost"
    right["sources"][0]["title"] = "Reposted claim"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "duplicate"
    assert suggestion["action"] == "source_candidate"
    assert {reason["field"] for reason in suggestion["reasons"]} == set(fingerprint(left))


def test_parameter_change_is_preserved_as_variant():
    left = record("academic_momentum.json")
    left["required_data"] = ["close", "volume"]
    left["entry_rule"] = "enter when momentum exceeds threshold"
    left["exit_rule"] = "exit when momentum reverses"
    left["sizing_rule"] = "equal risk"
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_variant"
    right["sizing_rule"] = "volatility target"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert suggestion["action"] == "preserve_variant"
    assert suggestion["reasons"] == [{"field": "sizing_rule", "reason": "normalized value differs"}]


def test_execution_change_is_preserved_as_variant():
    left = record("academic_momentum.json")
    left["required_data"] = ["close", "volume"]
    left["entry_rule"] = "enter when momentum exceeds threshold"
    left["exit_rule"] = "exit when momentum reverses"
    left["sizing_rule"] = "equal risk"
    right = copy.deepcopy(left)
    right["id"] = "academic_momentum_execution_variant"
    right["execution_assumptions"] = ["paper execution only"]
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert suggestion["action"] == "preserve_variant"
    assert suggestion["reasons"] == [
        {"field": "execution_assumptions", "reason": "normalized value differs"}
    ]


def test_different_entry_exit_mechanism_is_not_variant():
    left = record("academic_momentum.json")
    left["required_data"] = ["close", "volume"]
    left["entry_rule"] = "enter on moving average crossover"
    left["exit_rule"] = "exit on moving average crossover"
    right = copy.deepcopy(left)
    right["id"] = "academic_rsi_mechanism"
    right["entry_rule"] = "enter when RSI crosses threshold"
    right["exit_rule"] = "exit when RSI crosses threshold"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "related_to"
    assert suggestion["relation"] != "variant_of"
    assert {reason["field"] for reason in suggestion["reasons"]} >= {
        "entry_rule",
        "exit_rule",
    }


def test_sma_parameter_change_is_variant():
    left = record("academic_momentum.json")
    left["family"] = "trend"
    left["required_data"] = ["close"]
    left["entry_rule"] = "enter on SMA(20) crossing above SMA(50)"
    left["exit_rule"] = "exit on SMA(20) crossing below SMA(50)"
    right = copy.deepcopy(left)
    right["id"] = "sma_50_200_variant"
    right["entry_rule"] = "enter on SMA(50) crossing above SMA(200)"
    right["exit_rule"] = "exit on SMA(50) crossing below SMA(200)"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "variant_of"
    assert {reason["field"] for reason in suggestion["reasons"]} >= {
        "entry_rule",
        "exit_rule",
    }


def test_sma_vs_rsi_mechanism_is_not_variant():
    left = record("academic_momentum.json")
    left["family"] = "trend"
    left["required_data"] = ["close"]
    left["entry_rule"] = "enter on SMA(20) crossing above SMA(50)"
    left["exit_rule"] = "exit on SMA(20) crossing below SMA(50)"
    right = copy.deepcopy(left)
    right["id"] = "rsi_threshold_mechanism"
    right["entry_rule"] = "enter when RSI crosses above 70 threshold"
    right["exit_rule"] = "exit when RSI crosses below 30 threshold"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "related_to"
    assert suggestion["relation"] != "variant_of"


def test_inverted_sma_polarity_is_not_variant():
    left = record("academic_momentum.json")
    left["family"] = "trend"
    left["required_data"] = ["close"]
    left["entry_rule"] = "enter on SMA(20) crossing above SMA(50)"
    left["exit_rule"] = "exit on SMA(20) crossing below SMA(50)"
    right = copy.deepcopy(left)
    right["id"] = "sma_inverted_polarity"
    right["entry_rule"] = "enter on SMA(20) crossing below SMA(50)"
    right["exit_rule"] = "exit on SMA(20) crossing above SMA(50)"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "related_to"


def test_rsi_direction_reversal_is_not_variant():
    left = record("community_rsi.json")
    left["family"] = "mean_reversion"
    left["required_data"] = ["close"]
    left["entry_rule"] = "enter long when RSI is below oversold threshold"
    left["exit_rule"] = "exit when RSI is above overbought threshold"
    right = copy.deepcopy(left)
    right["id"] = "rsi_direction_reversal"
    right["entry_rule"] = "enter short when RSI is above overbought threshold"
    right["exit_rule"] = "exit when RSI is below oversold threshold"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "related_to"


def test_market_execution_scope_swap_is_preserved_as_variant():
    left = record("academic_momentum.json")
    left["required_data"] = ["close", "volume"]
    left["entry_rule"] = "enter when momentum exceeds threshold"
    left["exit_rule"] = "exit when momentum reverses"
    left["sizing_rule"] = "equal risk"
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


def test_unknown_placeholders_are_insufficient_not_duplicates():
    canonical = Path(__file__).parents[1] / "research" / "strategies"
    left = load_strategy_record(canonical / "cash_and_carry.json")
    right = copy.deepcopy(left)
    right["id"] = "cash_and_carry_unknown_repost"
    suggestion = compare_records(left, right)
    assert suggestion["relation"] == "insufficient_information"
    assert suggestion["action"] == "no_merge"
    assert {reason["field"] for reason in suggestion["reasons"]} == {
        "signal_inputs",
        "entry_rule",
        "exit_rule",
        "sizing_rule",
    }


def test_disjoint_placeholder_records_are_not_candidates():
    canonical = Path(__file__).parents[1] / "research" / "strategies"
    left = load_strategy_record(canonical / "cash_and_carry.json")
    right = load_strategy_record(canonical / "buy_hold.json")
    assert compare_records(left, right) is None


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


def test_canonical_report_uses_repo_relative_input_dir():
    canonical = Path(__file__).parents[1] / "research" / "strategies"
    report = run_dry_run(canonical)
    assert report["input_dir"] == "research/strategies"
    assert len(report["record_ids"]) == 35


def test_discovery_order_is_deterministic():
    records = [record("community_rsi.json"), record("academic_momentum.json")]
    assert discover(records) == discover(list(reversed(records)))
