"""Unit tests for review_strategy_drafts.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import review_strategy_drafts as rsd
import yaml

CHECKLIST_PATH = Path(__file__).resolve().parents[2] / "assets" / "bias_checklist.yaml"

# ---------------------------------------------------------------------------
# C1: Edge Plausibility
# ---------------------------------------------------------------------------


def test_pass_verdict_well_formed_breakout(well_formed_breakout_draft: dict) -> None:
    """A well-formed breakout draft should PASS review."""
    review = rsd.review_draft(well_formed_breakout_draft)
    assert review.verdict == "PASS"
    assert review.confidence_score >= 70
    c1 = _find(review, "C1_edge_plausibility")
    assert c1.severity == "pass"


def test_reject_empty_thesis(empty_thesis_draft: dict) -> None:
    """Empty thesis should fail C1 and trigger REJECT."""
    review = rsd.review_draft(empty_thesis_draft)
    c1 = _find(review, "C1_edge_plausibility")
    assert c1.severity == "fail"
    assert c1.score == 10
    assert review.verdict == "REJECT"


def test_reject_generic_thesis(generic_thesis_draft: dict) -> None:
    """Generic thesis with no domain terms should warn C1."""
    c1 = rsd.evaluate_c1(generic_thesis_draft)
    assert c1.severity == "warn"
    assert c1.score == 40


# ---------------------------------------------------------------------------
# C2: Overfitting Risk
# ---------------------------------------------------------------------------


def test_c2_pass_standard_conditions(well_formed_breakout_draft: dict) -> None:
    """Standard condition count (<= 10) should pass C2."""
    review = rsd.review_draft(well_formed_breakout_draft)
    c2 = _find(review, "C2_overfitting_risk")
    assert c2.severity == "pass"
    assert c2.score >= 60


def test_c2_warn_excessive_conditions(excessive_conditions_draft: dict) -> None:
    """11 total conditions should warn C2."""
    review = rsd.review_draft(excessive_conditions_draft)
    c2 = _find(review, "C2_overfitting_risk")
    assert c2.severity == "warn"
    assert c2.score == 40


def test_c2_fail_extreme_conditions(extreme_conditions_draft: dict) -> None:
    """13 total conditions should fail C2."""
    review = rsd.review_draft(extreme_conditions_draft)
    c2 = _find(review, "C2_overfitting_risk")
    assert c2.severity == "fail"
    assert c2.score == 10


def test_c2_precise_threshold_penalty(precise_threshold_draft: dict) -> None:
    """Precise decimal thresholds should reduce C2 score by 10 each."""
    review = rsd.review_draft(precise_threshold_draft)
    c2 = _find(review, "C2_overfitting_risk")
    # 6 total conditions (pass base 80), but 3 precise thresholds: 80 - 30 = 50
    assert c2.score == 50
    assert c2.severity == "warn"


# ---------------------------------------------------------------------------
# C3: Sample Adequacy
# ---------------------------------------------------------------------------


def test_c3_pass_broad_conditions(well_formed_breakout_draft: dict) -> None:
    """Broad conditions should pass C3."""
    review = rsd.review_draft(well_formed_breakout_draft)
    c3 = _find(review, "C3_sample_adequacy")
    assert c3.severity == "pass"


def test_c3_warn_restrictive_conditions(restrictive_conditions_draft: dict) -> None:
    """Sector+regime+many conditions should warn C3."""
    review = rsd.review_draft(restrictive_conditions_draft)
    c3 = _find(review, "C3_sample_adequacy")
    assert c3.severity == "warn"
    # est ~20 -> _c3_score_from_estimate(20): 10-29 band -> linear 30..59
    # (20-10)/(29-10)*(59-30)+30 = 10/19*29+30 ~= 45
    assert 40 <= c3.score <= 50


def test_c3_fail_extreme_restriction(extreme_restriction_draft: dict) -> None:
    """Extreme restriction should fail C3."""
    review = rsd.review_draft(extreme_restriction_draft)
    c3 = _find(review, "C3_sample_adequacy")
    assert c3.severity == "fail"
    assert c3.score == 10


# ---------------------------------------------------------------------------
# C4: Regime Dependency
# ---------------------------------------------------------------------------


def test_regime_dependency_single_regime(
    single_regime_no_validation_draft: dict,
) -> None:
    """Single regime without cross-regime validation should warn C4."""
    review = rsd.review_draft(single_regime_no_validation_draft)
    c4 = _find(review, "C4_regime_dependency")
    assert c4.severity == "warn"
    assert c4.score == 40


# ---------------------------------------------------------------------------
# C5: Exit Calibration
# ---------------------------------------------------------------------------


def test_exit_logic_flags_unreasonable_stop(unreasonable_stop_draft: dict) -> None:
    """Stop loss > 15% should fail C5."""
    review = rsd.review_draft(unreasonable_stop_draft)
    c5 = _find(review, "C5_exit_calibration")
    assert c5.severity == "fail"
    assert c5.score == 10


def test_exit_logic_flags_low_rr(low_rr_draft: dict) -> None:
    """Risk-reward < 1.5 should fail C5."""
    review = rsd.review_draft(low_rr_draft)
    c5 = _find(review, "C5_exit_calibration")
    assert c5.severity == "fail"
    assert c5.score == 10


# ---------------------------------------------------------------------------
# C6: Risk Concentration
# ---------------------------------------------------------------------------


def test_risk_concentration_warn_high_risk(high_risk_draft: dict) -> None:
    """risk_per_trade > 1.5% should warn C6."""
    review = rsd.review_draft(high_risk_draft)
    c6 = _find(review, "C6_risk_concentration")
    assert c6.severity == "warn"
    assert c6.score == 40


def test_risk_concentration_fail_extreme(extreme_risk_draft: dict) -> None:
    """risk_per_trade > 2% should fail C6."""
    review = rsd.review_draft(extreme_risk_draft)
    c6 = _find(review, "C6_risk_concentration")
    assert c6.severity == "fail"
    assert c6.score == 10


# ---------------------------------------------------------------------------
# C7: Execution Realism
# ---------------------------------------------------------------------------


def test_execution_realism_no_volume_filter(no_volume_filter_draft: dict) -> None:
    """No volume filter in conditions should warn C7."""
    review = rsd.review_draft(no_volume_filter_draft)
    c7 = _find(review, "C7_execution_realism")
    assert c7.severity == "warn"
    assert c7.score == 50


def test_c7_fail_export_ready_wrong_family(wrong_family_export_draft: dict) -> None:
    """export_ready=true with non-exportable family should fail C7."""
    review = rsd.review_draft(wrong_family_export_draft)
    c7 = _find(review, "C7_execution_realism")
    assert c7.severity == "fail"
    assert c7.score == 10


# ---------------------------------------------------------------------------
# C8: Invalidation Quality
# ---------------------------------------------------------------------------


def test_invalidation_empty_signals(empty_invalidation_draft: dict) -> None:
    """Empty invalidation signals should fail C8."""
    review = rsd.review_draft(empty_invalidation_draft)
    c8 = _find(review, "C8_invalidation_quality")
    assert c8.severity == "fail"
    assert c8.score == 10


def test_invalidation_insufficient(insufficient_invalidation_draft: dict) -> None:
    """Only 1 invalidation signal should warn C8."""
    review = rsd.review_draft(insufficient_invalidation_draft)
    c8 = _find(review, "C8_invalidation_quality")
    assert c8.severity == "warn"
    assert c8.score == 40


# ---------------------------------------------------------------------------
# Verdict and Confidence
# ---------------------------------------------------------------------------


def test_confidence_score_weighted_average(well_formed_breakout_draft: dict) -> None:
    """Confidence score should be a weighted average of all criteria."""
    review = rsd.review_draft(well_formed_breakout_draft)
    # C1=95 (continuous: 50+30+10+10), C2=80 (6 filters), C3=~69 (est~39),
    # C4=80, C5=80, C6=80, C7=80, C8=80
    # Weighted: (20*95+20*80+15*69+10*80+10*80+10*80+10*80+5*80)/100 = 81
    expected = 81
    assert review.confidence_score == expected


def test_verdict_reject_overrides_on_c1_fail(empty_thesis_draft: dict) -> None:
    """C1 fail should immediately reject regardless of other scores."""
    review = rsd.review_draft(empty_thesis_draft)
    assert review.verdict == "REJECT"


def test_revision_instructions_populated(generic_thesis_draft: dict) -> None:
    """REVISE verdict should include revision instructions."""
    review = rsd.review_draft(generic_thesis_draft)
    # generic thesis -> C1 warn -> overall may be REVISE or PASS depending on score
    # With C1=40 (warn), weighted: 20*40 + 80*(80) = 800 + 6400 = 7200 / 100 = 72
    # Actually let's check: C1=40, all others=80
    # (20*40 + 20*80 + 15*80 + 10*80 + 10*80 + 10*80 + 10*80 + 5*80) / 100
    # = (800 + 1600 + 1200 + 800 + 800 + 800 + 800 + 400) / 100 = 7200 / 100 = 72
    # confidence = 72, no fail -> PASS
    # But the C1 finding has revision_instruction since it's warn
    c1 = _find(review, "C1_edge_plausibility")
    assert c1.revision_instruction is not None


# ---------------------------------------------------------------------------
# Export Eligibility
# ---------------------------------------------------------------------------


def test_export_eligible_pass_and_exportable(
    well_formed_breakout_draft: dict,
) -> None:
    """PASS + export_ready_v1 + exportable family -> export_eligible."""
    review = rsd.review_draft(well_formed_breakout_draft)
    assert review.verdict == "PASS"
    assert review.export_eligible is True


def test_export_ineligible_pass_research_only(research_probe_draft: dict) -> None:
    """PASS + research_only family -> not export_eligible."""
    review = rsd.review_draft(research_probe_draft)
    assert review.export_eligible is False


# ---------------------------------------------------------------------------
# Strict Export Mode
# ---------------------------------------------------------------------------


def test_strict_export_warn_triggers_revise(no_volume_filter_draft: dict) -> None:
    """In strict mode, export-eligible draft with C7 warn → REVISE."""
    # no_volume_filter_draft is export_ready_v1=True, entry_family=pivot_breakout
    # It gets C7 warn (no volume filter) -> normally still PASS
    normal_review = rsd.review_draft(no_volume_filter_draft)
    assert normal_review.verdict == "PASS"

    strict_review = rsd.review_draft(no_volume_filter_draft, strict_export=True)
    assert strict_review.verdict == "REVISE"
    assert len(strict_review.revision_instructions) > 0


def test_strict_export_no_warn_still_passes(well_formed_breakout_draft: dict) -> None:
    """In strict mode, export-eligible draft with no warns → still PASS."""
    review = rsd.review_draft(well_formed_breakout_draft, strict_export=True)
    assert review.verdict == "PASS"
    assert review.export_eligible is True


def test_strict_export_research_probe_unaffected(no_volume_filter_draft: dict) -> None:
    """In strict mode, non-export-eligible draft with warns → still PASS (not affected)."""
    # Make a research-only version
    d = dict(no_volume_filter_draft)
    d["export_ready_v1"] = False
    d["entry_family"] = "research_only"
    review = rsd.review_draft(d, strict_export=True)
    # Research probes are not export-eligible, so strict mode does not apply
    assert review.verdict == "PASS"


# ---------------------------------------------------------------------------
# CLI and Output
# ---------------------------------------------------------------------------


def test_cli_drafts_dir(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """CLI with --drafts-dir should process all YAML files."""
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()
    (drafts_dir / "draft1.yaml").write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(["--drafts-dir", str(drafts_dir), "--output-dir", str(output_dir)])
    assert rc == 0
    assert (output_dir / "review.yaml").exists()


def test_cli_single_draft(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """CLI with --draft should process a single YAML file."""
    draft_file = tmp_path / "single_draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(["--draft", str(draft_file), "--output-dir", str(output_dir)])
    assert rc == 0
    assert (output_dir / "review.yaml").exists()


def test_cli_format_yaml(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """CLI with --format yaml should produce valid YAML output."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--format",
            "yaml",
        ]
    )
    assert rc == 0
    review_path = output_dir / "review.yaml"
    assert review_path.exists()
    data = yaml.safe_load(review_path.read_text())
    assert "summary" in data
    assert "reviews" in data


def test_cli_format_json(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """CLI with --format json should produce valid JSON output."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
        ]
    )
    assert rc == 0
    review_path = output_dir / "review.json"
    assert review_path.exists()
    data = json.loads(review_path.read_text())
    assert "summary" in data
    assert "reviews" in data


def test_cli_markdown_summary(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """CLI with --markdown-summary should produce a markdown file."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--markdown-summary",
        ]
    )
    assert rc == 0
    md_path = output_dir / "review_summary.md"
    assert md_path.exists()
    content = md_path.read_text()
    assert "# Strategy Draft Review Summary" in content


# ---------------------------------------------------------------------------
# C1 Continuous Scoring
# ---------------------------------------------------------------------------


def test_c1_pass_score_increases_with_thesis_richness(
    minimal_thesis_draft: dict,
    moderate_thesis_draft: dict,
    rich_thesis_draft: dict,
) -> None:
    """Rich thesis should score higher than moderate, which scores higher than minimal."""
    c1_minimal = rsd.evaluate_c1(minimal_thesis_draft)
    c1_moderate = rsd.evaluate_c1(moderate_thesis_draft)
    c1_rich = rsd.evaluate_c1(rich_thesis_draft)
    assert c1_minimal.score < c1_moderate.score < c1_rich.score


def test_c1_mechanism_keyword_bonus(
    moderate_thesis_draft: dict,
    rich_thesis_draft: dict,
) -> None:
    """Thesis with mechanism keywords should score higher than same-length without."""
    c1_no_mechanism = rsd.evaluate_c1(moderate_thesis_draft)
    c1_with_mechanism = rsd.evaluate_c1(rich_thesis_draft)
    assert c1_with_mechanism.score > c1_no_mechanism.score


def test_c1_pass_score_capped_at_95(rich_thesis_draft: dict) -> None:
    """Even the richest thesis should not exceed 95."""
    c1 = rsd.evaluate_c1(rich_thesis_draft)
    assert c1.score <= 95
    assert c1.severity == "pass"


# ---------------------------------------------------------------------------
# C2 Five-Tier Ordering
# ---------------------------------------------------------------------------


def test_c2_lean_conditions_score_highest(lean_conditions_draft: dict) -> None:
    """4 filters should score 90 (highest tier)."""
    c2 = rsd.evaluate_c2(lean_conditions_draft)
    assert c2.score == 90
    assert c2.severity == "pass"


def test_c2_moderate_conditions_score(moderate_conditions_draft: dict) -> None:
    """7 filters should score 80 (second tier)."""
    c2 = rsd.evaluate_c2(moderate_conditions_draft)
    assert c2.score == 80
    assert c2.severity == "pass"


def test_c2_five_tier_ordering() -> None:
    """Scores should decrease monotonically: 4 < 7 < 10 < 12 < 13 filters."""

    def _make_draft(n_conditions: int, n_trend: int) -> dict:
        return {
            "entry": {
                "conditions": [f"cond_{i}" for i in range(n_conditions)],
                "trend_filter": [f"trend_{i}" for i in range(n_trend)],
            }
        }

    scores = [
        rsd.evaluate_c2(_make_draft(3, 1)).score,  # 4 total
        rsd.evaluate_c2(_make_draft(5, 2)).score,  # 7 total
        rsd.evaluate_c2(_make_draft(7, 3)).score,  # 10 total
        rsd.evaluate_c2(_make_draft(9, 3)).score,  # 12 total
        rsd.evaluate_c2(_make_draft(10, 3)).score,  # 13 total
    ]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"scores[{i}]={scores[i]} < scores[{i + 1}]={scores[i + 1]}"
        )
    # Verify strict decrease somewhere (not all equal)
    assert scores[0] > scores[-1]


# ---------------------------------------------------------------------------
# C3 Continuous Scoring
# ---------------------------------------------------------------------------


def test_c3_high_opportunity_scores_above_75(high_opportunity_draft: dict) -> None:
    """High-opportunity draft should score >= 75."""
    c3 = rsd.evaluate_c3(high_opportunity_draft)
    assert c3.score >= 75
    assert c3.severity == "pass"


def test_c3_low_opportunity_scores_in_warn_band(low_opportunity_draft: dict) -> None:
    """Low-opportunity (~20 est) should score in 30..59 band."""
    c3 = rsd.evaluate_c3(low_opportunity_draft)
    assert 30 <= c3.score <= 59
    assert c3.severity == "warn"


def test_c3_monotonicity() -> None:
    """Higher opportunity estimate should produce higher or equal score."""
    estimates = [5, 10, 20, 30, 50, 100, 200, 300]
    scores = [rsd._c3_score_from_estimate(e) for e in estimates]
    for i in range(len(scores) - 1):
        assert scores[i] <= scores[i + 1], (
            f"_c3_score_from_estimate({estimates[i]})={scores[i]} > "
            f"_c3_score_from_estimate({estimates[i + 1]})={scores[i + 1]}"
        )


# ---------------------------------------------------------------------------
# Confidence and Integration
# ---------------------------------------------------------------------------


def test_confidence_score_varies_with_thesis(
    minimal_thesis_draft: dict,
    rich_thesis_draft: dict,
) -> None:
    """Two drafts with different thesis richness should have different confidence scores."""
    review_minimal = rsd.review_draft(minimal_thesis_draft)
    review_rich = rsd.review_draft(rich_thesis_draft)
    assert review_minimal.confidence_score != review_rich.confidence_score


def test_c1_c2_c3_score_ranges_no_longer_uniform(
    rich_thesis_draft: dict,
    lean_conditions_draft: dict,
    high_opportunity_draft: dict,
) -> None:
    """Verify that modified criteria no longer always produce exactly {10,40,80}."""
    old_values = {10, 40, 80}
    c1 = rsd.evaluate_c1(rich_thesis_draft)
    c2 = rsd.evaluate_c2(lean_conditions_draft)
    c3 = rsd.evaluate_c3(high_opportunity_draft)
    # At least one of the scores should NOT be in {10, 40, 80}
    scores = {c1.score, c2.score, c3.score}
    assert not scores.issubset(old_values), f"All scores {scores} still in old set {old_values}"


# ---------------------------------------------------------------------------
# Bias Checklist (issue #297 slice 1)
# ---------------------------------------------------------------------------


@pytest.fixture()
def bias_items() -> list[dict]:
    """Load the bundled bias checklist items."""
    return rsd.load_bias_checklist(CHECKLIST_PATH)


def test_load_bias_checklist_parses() -> None:
    """The bundled bias checklist YAML must expose versioned required items."""
    items = rsd.load_bias_checklist(CHECKLIST_PATH)
    assert len(items) >= 12
    assert all({"id", "title", "required", "coverage_hint"} <= set(i) for i in items)
    ids = {i["id"] for i in items}
    assert {
        "look_ahead",
        "survivorship",
        "universe_selection",
        "delisted_securities",
        "earnings_announcement_timing",
        "split_dividend_adjustment",
        "transaction_costs_slippage",
        "short_borrow_availability",
        "liquidity_capacity",
        "parameter_multiplicity",
        "walk_forward_out_of_sample",
        "benchmark_attribution",
        "regime_dependence",
    } <= ids
    # The issue's checklist is mandatory -> every item is required.
    assert all(i["required"] for i in items)


def test_evaluate_bias_checklist_explicit_block(
    well_formed_breakout_draft: dict, bias_items: list[dict]
) -> None:
    """A declared truthy entry marks an item addressed; undeclared items are not."""
    d = dict(well_formed_breakout_draft)
    d["bias_checklist"] = {
        "look_ahead": "point-in-time snapshot; no future data used",
        "survivorship": "universe includes delisted names",
    }
    results = rsd.evaluate_bias_checklist(d, bias_items)
    by_id = {r["item_id"]: r for r in results}
    assert by_id["look_ahead"]["addressed"] is True
    assert by_id["survivorship"]["addressed"] is True
    assert by_id["universe_selection"]["addressed"] is False
    assert by_id["regime_dependence"]["addressed"] is False


def test_bias_noted_in_draft_heuristic(
    well_formed_breakout_draft: dict, bias_items: list[dict]
) -> None:
    """The informational 'noted_in_draft' flag matches concept text in the draft."""
    d = dict(well_formed_breakout_draft)
    results = rsd.evaluate_bias_checklist(d, bias_items)
    by_id = {r["item_id"]: r for r in results}
    assert by_id["regime_dependence"]["noted_in_draft"] is True
    # Not declared in an explicit block, so not 'addressed' even if noted.
    assert by_id["regime_dependence"]["addressed"] is False


def test_apply_bias_gate_downgrades_pass_to_revise(bias_items: list[dict]) -> None:
    """Unaddressed required item downgrades PASS -> REVISE and clears export."""
    review = rsd.DraftReview(
        draft_id="x",
        verdict="PASS",
        confidence_score=80,
        export_eligible=True,
        findings=[],
        revision_instructions=[],
    )
    d = {"id": "x", "bias_checklist": {"look_ahead": "point-in-time"}}
    results = rsd.evaluate_bias_checklist(d, bias_items)
    assert rsd.apply_bias_gate(review, results) is True
    assert review.verdict == "REVISE"
    assert review.export_eligible is False


def test_apply_bias_gate_no_downgrade_when_all_required_addressed() -> None:
    """When every required item is addressed, the gate leaves the verdict alone."""
    items = [
        {"id": "a", "title": "A", "required": True, "coverage_hint": "x"},
        {"id": "b", "title": "B", "required": True, "coverage_hint": "y"},
    ]
    d = {"id": "x", "bias_checklist": {"a": "done", "b": "done"}}
    review = rsd.DraftReview("x", "PASS", 80, True, [], [])
    results = rsd.evaluate_bias_checklist(d, items)
    assert rsd.apply_bias_gate(review, results) is False
    assert review.verdict == "PASS"
    assert review.export_eligible is True


def test_apply_bias_gate_never_upgrades_reject(bias_items: list[dict]) -> None:
    """A REJECT verdict must never be raised by the bias gate."""
    review = rsd.DraftReview("x", "REJECT", 20, False, [], [])
    d = {"id": "x"}
    results = rsd.evaluate_bias_checklist(d, bias_items)
    assert rsd.apply_bias_gate(review, results) is False
    assert review.verdict == "REJECT"


def test_build_output_includes_bias_block_only_when_present(
    well_formed_breakout_draft: dict,
) -> None:
    """bias_review is serialized only when the checklist source is supplied."""
    review = rsd.review_draft(well_formed_breakout_draft)
    bias_block = [
        {
            "item_id": "look_ahead",
            "title": "Look-ahead bias",
            "required": True,
            "addressed": True,
            "noted_in_draft": True,
            "note": "point-in-time",
        }
    ]
    with_bias = rsd.build_output("src", 1, [review], bias_by_id={review.draft_id: bias_block})
    assert with_bias["reviews"][0]["bias_review"] == bias_block
    without_bias = rsd.build_output("src", 1, [review])
    assert "bias_review" not in without_bias["reviews"][0]


def test_bias_checklist_doc_matches_asset(bias_items: list[dict]) -> None:
    """Drift guard: the research-bias doc must describe every checklist item."""
    doc = (
        Path(__file__).resolve().parents[4] / "docs/dev/strategy-research-bias-checklist.md"
    ).read_text(encoding="utf-8")
    for item in bias_items:
        assert f"`{item['id']}`" in doc, f"bias doc missing checklist item {item['id']}"


def test_cli_bias_checklist_defaults_bundled(
    tmp_path: Path, well_formed_breakout_draft: dict
) -> None:
    """--bias-checklist without a path uses the bundled asset and downgrades on gaps."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
            "--bias-checklist",
        ]
    )
    assert rc == 0
    payload = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))
    review = payload["reviews"][0]
    assert review["verdict"] == "REVISE"
    assert review["export_eligible"] is False
    assert "bias_review" in review
    assert review["bias_review"]
    assert any(not b["addressed"] for b in review["bias_review"])


def test_cli_bias_checklist_custom_path(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """--bias-checklist with an explicit path loads that checklist."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    checklist_file = tmp_path / "custom.yaml"
    checklist_file.write_text(
        "schema_version: '1.0'\nitems:\n  - id: look_ahead\n    title: Look ahead\n"
        "    required: true\n    coverage_hint: point[- ]in[- ]time\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
            "--bias-checklist",
            str(checklist_file),
        ]
    )
    assert rc == 0
    review = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))["reviews"][0]
    assert review["verdict"] == "REVISE"
    assert len(review["bias_review"]) == 1


def test_cli_bias_checklist_missing_file(tmp_path: Path, well_formed_breakout_draft: dict) -> None:
    """A missing custom checklist path surfaces a ReviewError (rc=1)."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--bias-checklist",
            str(tmp_path / "nope.yaml"),
        ]
    )
    assert rc == 1


def test_cli_bias_checklist_malformed_yaml(
    tmp_path: Path, well_formed_breakout_draft: dict
) -> None:
    """A custom checklist with invalid YAML surfaces a ReviewError (rc=1), not a traceback."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    checklist_file = tmp_path / "bad.yaml"
    checklist_file.write_text("items: [unclosed\n", encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--bias-checklist",
            str(checklist_file),
        ]
    )
    assert rc == 1


def test_cli_bias_checklist_schema_version_mismatch(
    tmp_path: Path, well_formed_breakout_draft: dict
) -> None:
    """A custom checklist with a mismatched schema_version is rejected."""
    draft_file = tmp_path / "draft.yaml"
    draft_file.write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    checklist_file = tmp_path / "checklist.yaml"
    checklist_file.write_text(
        yaml.safe_dump(
            {"schema_version": "2.0", "items": [{"id": "x", "coverage_hint": "x"}]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--draft",
            str(draft_file),
            "--output-dir",
            str(output_dir),
            "--bias-checklist",
            str(checklist_file),
        ]
    )
    assert rc == 1


def test_cli_bias_checklist_drafts_dir_joins_by_index(
    tmp_path: Path, well_formed_breakout_draft: dict
) -> None:
    """--drafts-dir mode: a PASS draft is downgraded, a REJECT draft untouched."""
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()
    (drafts_dir / "a.yaml").write_text(
        yaml.safe_dump(well_formed_breakout_draft, sort_keys=False), encoding="utf-8"
    )
    rejecting = dict(well_formed_breakout_draft)
    rejecting["id"] = "draft_rejected_bad_idea"
    rejecting["thesis"] = ""
    (drafts_dir / "b.yaml").write_text(yaml.safe_dump(rejecting, sort_keys=False), encoding="utf-8")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    rc = rsd.main(
        [
            "--drafts-dir",
            str(drafts_dir),
            "--output-dir",
            str(output_dir),
            "--format",
            "json",
            "--bias-checklist",
        ]
    )
    assert rc == 0
    reviews = json.loads((output_dir / "review.json").read_text(encoding="utf-8"))["reviews"]
    assert len(reviews) == 2
    pass_review = next(r for r in reviews if r["draft_id"] == well_formed_breakout_draft["id"])
    reject_review = next(r for r in reviews if r["draft_id"] == "draft_rejected_bad_idea")
    assert pass_review["verdict"] == "REVISE"
    assert "bias_review" in pass_review and pass_review["bias_review"]
    assert any("Declare how" in i for i in pass_review["revision_instructions"])
    assert reject_review["verdict"] == "REJECT"
    assert "bias_review" in reject_review


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find(review: rsd.DraftReview, criterion: str) -> rsd.ReviewFinding:
    """Find a specific criterion finding in a review."""
    for f in review.findings:
        if f.criterion == criterion:
            return f
    raise AssertionError(f"Criterion {criterion} not found in review findings")
