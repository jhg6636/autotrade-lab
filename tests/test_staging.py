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


def public_lane_path(lane: str, root: Path = ROOT) -> Path:
    collection = root / "research" / "staging" / "collection" / lane
    if collection.exists():
        return collection
    return root / "research" / "staging" / "pilot" / lane


PUBLIC101 = public_lane_path("luna-101")
PUBLIC104 = public_lane_path("luna-104")


def test_synthetic_lanes_have_five_source_and_candidate_records():
    assert len(load_jsonl(LUNA101 / "sources.jsonl", "sources")) == 5
    assert len(load_jsonl(LUNA101 / "hypotheses.jsonl", "hypotheses")) == 5
    assert len(load_jsonl(LUNA104 / "sources.jsonl", "sources")) == 5
    assert len(load_jsonl(LUNA104 / "hypotheses.jsonl", "hypotheses")) == 5


def test_public_lane_prefers_collection_after_integration_initialization(tmp_path):
    pilot = tmp_path / "research" / "staging" / "pilot" / "luna-101"
    pilot.mkdir(parents=True)
    assert public_lane_path("luna-101", tmp_path) == pilot

    collection = tmp_path / "research" / "staging" / "collection" / "luna-101"
    collection.mkdir(parents=True)
    assert public_lane_path("luna-101", tmp_path) == collection


def test_aggregate_is_deterministic_and_non_mutating(tmp_path):
    before = {path: path.read_bytes() for path in LUNA101.glob("*.jsonl")}
    first = aggregate(LUNA101)
    second = aggregate(LUNA101)
    assert first == second
    assert first["counts"] == {
        "sources": {"total": 5, "usable": 4, "incomplete": 0, "inaccessible": 1, "other": 0},
        "hypotheses": {"total": 5, "usable": 4, "incomplete": 0, "inaccessible": 1, "other": 0},
        "inaccessible": {"total": 0, "usable": 0, "incomplete": 0, "inaccessible": 0, "other": 0},
        "relations": {"total": 0, "usable": 0, "incomplete": 0, "inaccessible": 0, "other": 0},
        "execution_audit": {
            "total": 0,
            "usable": 0,
            "incomplete": 0,
            "inaccessible": 0,
            "other": 0,
        },
        "suggestions": len(first["suggestions"]),
    }
    assert first["completion"]["usable_sources"] == 4
    assert first["completion"]["usable_hypotheses"] == 4
    assert first["automatic_merge"] is False
    assert first["canonical_records_modified"] is False
    assert before == {path: path.read_bytes() for path in LUNA101.glob("*.jsonl")}


def test_korean_pilot_passes_long_only_and_timeframe_rules():
    report = aggregate(LUNA104)
    assert report["counts"]["sources"]["total"] == 5
    assert report["counts"]["hypotheses"]["total"] == 5


def test_public_source_baseline_preserves_arxiv_scenario_and_krx_delisting_inputs():
    academic = next(
        item
        for item in load_jsonl(PUBLIC101 / "hypotheses.jsonl", "hypotheses")
        if item["hypothesis_id"] == "academic_hypothesis_cointegration_pairs_210910662"
    )
    assert academic["markets"] == ["crypto_perp"]
    assert academic["asset_direction"] == "long_short"
    assert "three-month formation" in academic["entry_rule"]
    assert "lambda=theta_hat" in academic["entry_rule"]
    assert "N_SMA=2/lambda-1" in academic["entry_rule"]
    assert "Z[t-2] < -2 and Z[t-1] > -2" in academic["entry_rule"]
    assert "Z[t-2] > +2 and Z[t-1] < +2" in academic["entry_rule"]
    assert "Z[t-2] > -1 and Z[t-1] < -1" in academic["exit_rule"]
    assert "Z[t-2] < +1 and Z[t-1] > +1" in academic["exit_rule"]
    korean = next(
        item
        for item in load_jsonl(PUBLIC104 / "hypotheses.jsonl", "hypotheses")
        if item["hypothesis_id"] == "korean_hypothesis_etf_disclosure"
    )
    assert korean["required_data"] == [
        "ETF 1좌당 NAV 일간수익률",
        "기초지수 일간수익률",
        "3개월 상관계수",
    ]


def test_duplicate_source_urls_are_rejected_at_aggregate_boundary(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    duplicate = dict(source)
    duplicate["source_id"] = "synthetic_source_other"
    (tmp_path / "sources.jsonl").write_text(
        json.dumps(source) + "\n" + json.dumps(duplicate) + "\n"
    )
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["source_ids"] = [source["source_id"]]
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    with pytest.raises(StagingValidationError, match="duplicate URL"):
        aggregate(tmp_path)


def test_missing_required_jsonl_file_is_rejected(tmp_path):
    (tmp_path / "sources.jsonl").write_text("")
    with pytest.raises(StagingValidationError, match="required file missing: hypotheses.jsonl"):
        aggregate(tmp_path)


def test_recursive_placeholder_in_required_data_is_rejected(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    source["required_data"] = ["close", {"field": "unknown: provider"}]
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    with pytest.raises(StagingValidationError, match="required_data"):
        aggregate(tmp_path)


def test_claimed_results_must_be_unverified(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    source["claimed_results"] = ["measured return 10 percent"]
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    with pytest.raises(StagingValidationError, match="claimed_results"):
        aggregate(tmp_path)


def test_usable_hypothesis_without_optional_claimed_results_is_valid(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate.pop("claimed_results")
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    report = aggregate(tmp_path)
    assert report["counts"]["hypotheses"]["usable"] == 1


def test_application_summary_mismatch_is_rejected(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["asset_direction"] = "long_only"
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    with pytest.raises(StagingValidationError, match="asset_direction"):
        aggregate(tmp_path)


def test_korean_timeframe_uses_executable_application_not_top_level_scope(tmp_path):
    source = json.loads((LUNA104 / "sources.jsonl").read_text().splitlines()[0])
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    candidate = json.loads((LUNA104 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["execution_scope"] = "executable"
    candidate["applications"][0]["execution_scope"] = "executable"
    candidate["timeframes"] = ["hourly"]
    (tmp_path / "hypotheses.jsonl").write_text(json.dumps(candidate) + "\n")
    with pytest.raises(StagingValidationError, match="timeframe not allowed"):
        aggregate(tmp_path)


@pytest.mark.parametrize("maximum", [1.5, 2, 5])
def test_context_only_application_accepts_levered_target_exposure(maximum, tmp_path):
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["execution_scope"] = "context_only"
    application = candidate["applications"][0]
    application["execution_scope"] = "context_only"
    application["target_exposure"] = {"minimum": 0, "maximum": maximum}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    assert load_jsonl(path, "hypotheses")[0]["applications"][0]["target_exposure"] == {
        "minimum": 0,
        "maximum": maximum,
    }


@pytest.mark.parametrize(
    ("asset_direction", "minimum", "maximum"),
    [
        ("long_only", 0, None),
        ("long_short", None, None),
    ],
)
def test_context_only_application_accepts_unbounded_target_exposure(
    asset_direction, minimum, maximum, tmp_path
):
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["asset_direction"] = asset_direction
    candidate["execution_scope"] = "context_only"
    application = candidate["applications"][0]
    application["asset_direction"] = asset_direction
    application["execution_scope"] = "context_only"
    application["target_exposure"] = {"minimum": minimum, "maximum": maximum}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    assert load_jsonl(path, "hypotheses")[0]["applications"][0]["target_exposure"] == {
        "minimum": minimum,
        "maximum": maximum,
    }


def test_executable_application_rejects_unbounded_target_exposure(tmp_path):
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["applications"][0]["target_exposure"] = {"minimum": None, "maximum": 1}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    with pytest.raises(
        StagingValidationError, match="executable application target exposure bounds"
    ):
        load_jsonl(path, "hypotheses")


def test_finite_reversed_target_exposure_is_rejected(tmp_path):
    candidate = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["execution_scope"] = "context_only"
    application = candidate["applications"][0]
    application["execution_scope"] = "context_only"
    application["target_exposure"] = {"minimum": 1, "maximum": -1}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    with pytest.raises(StagingValidationError, match="minimum exposure exceeds maximum"):
        load_jsonl(path, "hypotheses")


def test_aggregate_preserves_unbounded_target_exposure_profile_difference(tmp_path):
    source = json.loads((LUNA101 / "sources.jsonl").read_text().splitlines()[0])
    (tmp_path / "sources.jsonl").write_text(json.dumps(source) + "\n")
    unbounded = json.loads((LUNA101 / "hypotheses.jsonl").read_text().splitlines()[0])
    unbounded["execution_scope"] = "context_only"
    unbounded_application = unbounded["applications"][0]
    unbounded_application["execution_scope"] = "context_only"
    unbounded_application["target_exposure"] = {"minimum": None, "maximum": None}
    bounded = json.loads(json.dumps(unbounded))
    bounded["hypothesis_id"] = "academic_candidate_bounded_exposure"
    bounded["applications"][0]["target_exposure"] = {"minimum": -1, "maximum": 1}
    (tmp_path / "hypotheses.jsonl").write_text(
        "\n".join(json.dumps(item) for item in (unbounded, bounded)) + "\n"
    )

    report = aggregate(tmp_path)
    assert report["counts"]["hypotheses"]["usable"] == 2
    assert len(report["suggestions"]) == 1
    assert report["suggestions"][0]["relation"] == "variant_of"
    assert {reason["field"] for reason in report["suggestions"][0]["reasons"]} == {
        "target_exposure_profile"
    }


@pytest.mark.parametrize(
    ("asset_direction", "minimum", "maximum"),
    [
        ("long_short", 0, 1),
        ("long_only", -0.1, 1),
    ],
)
def test_korean_executable_application_rejects_short_negative_or_levered_exposure(
    asset_direction, minimum, maximum, tmp_path
):
    candidate = json.loads((LUNA104 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["asset_direction"] = asset_direction
    application = candidate["applications"][0]
    application["asset_direction"] = asset_direction
    application["target_exposure"] = {"minimum": minimum, "maximum": maximum}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    with pytest.raises(
        StagingValidationError, match="long_only with nonnegative, unlevered exposure"
    ):
        load_jsonl(path, "hypotheses")


def test_korean_executable_application_rejects_maximum_above_one(tmp_path):
    candidate = json.loads((LUNA104 / "hypotheses.jsonl").read_text().splitlines()[0])
    candidate["applications"][0]["target_exposure"] = {"minimum": 0, "maximum": 1.01}
    path = tmp_path / "hypotheses.jsonl"
    path.write_text(json.dumps(candidate) + "\n")

    with pytest.raises(
        StagingValidationError, match="long_only with nonnegative, unlevered exposure"
    ):
        load_jsonl(path, "hypotheses")


def test_malformed_source_has_line_number_and_field_path():
    with pytest.raises(StagingValidationError, match=r"sources:1:\$\.accessed_at"):
        load_jsonl(LUNA101 / "malformed.jsonl", "sources")


def test_malformed_korean_audit_is_rejected():
    with pytest.raises(StagingValidationError, match=r"execution_audit:1"):
        load_jsonl(LUNA104 / "malformed.jsonl", "execution_audit")


def test_inaccessible_jsonl_uses_the_inaccessible_schema(tmp_path):
    record = {
        "source_id": "synthetic_inaccessible_source",
        "url": "https://example.org/inaccessible",
        "reason": "The publisher blocked the attempted public access.",
        "attempted_at": "2026-08-23",
        "status": "inaccessible",
    }
    path = tmp_path / "inaccessible.jsonl"
    path.write_text(json.dumps(record) + "\n")

    assert load_jsonl(path, "inaccessible") == [record]


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
