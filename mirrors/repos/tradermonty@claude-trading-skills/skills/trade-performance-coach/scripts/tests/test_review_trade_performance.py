from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPT_DIR))

import review_trade_performance as rpc  # noqa: E402


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_clean_process_loss_is_ok_or_warn_without_behavior_tag():
    report = rpc.build_review(load("single_trade_clean_loss.json"), ["fixture"])
    assert report["overall_verdict"] == "OK"
    assert report["summary"]["primary_root_cause"] == "randomness"
    assert report["scores"]["risk_score"] == 100
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert tags == {"no_pattern_detected"}
    assert "financial advice" in report["disclaimer"].lower()


def test_rule_violation_loss_detects_fomo_size_creep_and_stop_moved():
    report = rpc.build_review(load("single_trade_rule_violation_loss.json"), ["fixture"])
    assert report["overall_verdict"] == "COOL_DOWN"
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert {"fomo_entry", "size_creep", "stop_moved"}.issubset(tags)
    process_rules = {f["rule"]: f for f in report["process_adherence_findings"]}
    assert process_rules["setup_confirmation"]["severity"] == "critical"
    assert process_rules["market_regime_gate"]["severity"] == "critical"
    assert any(
        n["topic"] == "position_size" and n["severity"] == "critical"
        for n in report["risk_manager_notes"]
    )
    assert any("0.5R" in r["rule"] for r in report["next_session_operating_rules"])


def test_partial_close_stop_moved_detects_stop_pattern():
    report = rpc.build_review(load("partial_close_stop_moved.json"), ["fixture"])
    assert report["review_type"] == "partial_close"
    # Note (2026-05-24 PR-F Blocker 1 fix): execution_quality_assessment now contributes
    # to determine_verdict. An unplanned stop move surfaces as critical in both the
    # process_adherence (stop_change_rule) and execution_quality (stop phase) axes,
    # so critical_count reaches 2 and the verdict escalates to COOL_DOWN. This is
    # conservative-side correct — stop_moved without a pre-defined rule is materially
    # serious — so COOL_DOWN is included alongside RULE_VIOLATION / REVIEW_REQUIRED here.
    assert report["overall_verdict"] in {"RULE_VIOLATION", "REVIEW_REQUIRED", "COOL_DOWN"}
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert "stop_moved" in tags
    assert any(e["phase"] == "stop" for e in report["execution_quality_assessment"])


def test_monthly_aggregate_revenge_pattern_cool_down():
    report = rpc.build_review(load("monthly_aggregate_revenge_pattern.json"), ["fixture"])
    assert report["review_type"] == "monthly_aggregate"
    assert report["overall_verdict"] == "COOL_DOWN"
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert "revenge_trade" in tags
    assert any("review-only" in r["rule"].lower() for r in report["next_session_operating_rules"])


def test_incomplete_record_degrades_without_crashing():
    report = rpc.build_review(load("incomplete_record.json"), ["fixture"])
    assert report["overall_verdict"] in {"REVIEW_REQUIRED", "WARN"}
    assert report["scores"]["review_quality_score"] < 80
    assert any(f["status"] == "unclear" for f in report["process_adherence_findings"])
    assert report["human_decision_gate"]["default_action"] == "journal_only"


def test_premature_exit_is_not_verdict_ok():
    """Blocker 1 regression (2026-05-24 PR-F review):
    actual.premature_exit=true must escalate the verdict beyond OK
    (execution warnings now contribute to determine_verdict).
    """
    report = rpc.build_review(load("single_trade_premature_exit.json"), ["fixture"])
    assert report["overall_verdict"] != "OK"
    assert report["overall_verdict"] in {"REVIEW_REQUIRED", "WARN", "RULE_VIOLATION", "COOL_DOWN"}
    assert any(
        e["phase"] == "exit" and e["severity"] == "warning"
        for e in report["execution_quality_assessment"]
    )
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert "premature_exit" in tags


def test_missing_risk_data_does_not_tag_size_creep():
    """Blocker 2 regression (2026-05-24 PR-F review):
    size_creep must require explicit evidence that actual.risk_r > reference_r.
    A missing-risk-data position_size warning must NOT be tagged as size_creep;
    instead it should surface as unknown_size_discipline. The next-session rule
    must NOT claim "actual risk exceeded the plan" (which would contradict the
    missing-data state); it must ask the trader to record planned/actual risk
    next time.
    """
    report = rpc.build_review(load("risk_data_missing_no_size_creep.json"), ["fixture"])
    tags = {t["tag"] for t in report["behavioral_pattern_tags"]}
    assert "size_creep" not in tags
    assert "unknown_size_discipline" in tags
    assert any(
        n["topic"] == "position_size" and n["severity"] == "warning"
        for n in report["risk_manager_notes"]
    )
    # The Cap-risk-at-0.5R rule (which states "Actual risk exceeded the stated
    # risk plan") must NOT fire when risk discipline is unverifiable.
    rules = report["next_session_operating_rules"]
    assert all("0.5R" not in r["rule"] for r in rules), (
        "Cap-risk-at-0.5R rule must only fire for size_creep, not unknown_size_discipline"
    )
    assert all("exceeded" not in r["reason"].lower() for r in rules), (
        "next-session rule reason must not claim risk exceeded when data is missing"
    )
    # Instead, a rule asking the trader to record planned/actual risk must fire.
    assert any("record" in r["rule"].lower() and "risk" in r["rule"].lower() for r in rules), (
        "unknown_size_discipline must produce a record-planned/actual-risk rule"
    )


def test_report_validates_against_schema():
    """Schema enum coverage regression (2026-05-24 PR-F review):
    every behavior_tag the runtime can emit must be in the schema's enum,
    including unknown_size_discipline. Validate one report per fixture so
    that adding a new tag without updating the schema fails this test.
    """
    try:
        import jsonschema  # type: ignore
    except ImportError:  # pragma: no cover - environment dependent
        import pytest

        pytest.skip("jsonschema not installed")
    schema_path = SCRIPT_DIR.parent / "assets" / "performance_coach_report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    fixtures = [
        "single_trade_clean_loss.json",
        "single_trade_rule_violation_loss.json",
        "partial_close_stop_moved.json",
        "monthly_aggregate_revenge_pattern.json",
        "incomplete_record.json",
        "single_trade_premature_exit.json",
        "risk_data_missing_no_size_creep.json",
    ]
    for fixture in fixtures:
        report = rpc.build_review(load(fixture), [fixture])
        # schema_version is int per dataclass output; the asset schema uses 1.0
        # as illustrative — coerce to match the structural enum check below.
        jsonschema.Draft7Validator(schema).validate(report)


def test_cli_writes_json_and_markdown(tmp_path):
    fixture = FIXTURES / "single_trade_rule_violation_loss.json"
    rc = rpc.main(
        [
            "--input",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--json-name",
            "report.json",
            "--markdown",
        ]
    )
    assert rc == 0
    report_json = tmp_path / "report.json"
    report_md = tmp_path / "report.md"
    assert report_json.exists()
    assert report_md.exists()
    data = json.loads(report_json.read_text(encoding="utf-8"))
    assert data["overall_verdict"] == "COOL_DOWN"
    assert "Human Decision Gate" in report_md.read_text(encoding="utf-8")


NUMERIC_FIELDS = [
    ("planned", "risk_r"),
    ("actual", "risk_r"),
    ("risk_plan", "max_risk_per_trade_r"),
    ("actual", "portfolio_heat_r"),
    ("risk_plan", "max_portfolio_heat_r"),
    ("monthly", "consecutive_losses"),
]


@pytest.mark.parametrize("section,key", NUMERIC_FIELDS)
@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), -float("inf"), -1, True, "bad", "1e999", "-1e-999", 10**400],
)
def test_invalid_numeric_evidence_rejected(section, key, value):
    record = load("single_trade_clean_loss.json")
    record.setdefault(section, {})[key] = value
    with pytest.raises(ValueError, match=rf"{section}\.{key}"):
        rpc.build_review(record, ["fixture"])


@pytest.mark.parametrize("value", [0.5, "2.5", "2.0000000000000001"])
def test_fractional_loss_count_rejected(value):
    record = load("single_trade_clean_loss.json")
    record["monthly"] = {"consecutive_losses": value}
    with pytest.raises(ValueError, match="monthly.consecutive_losses"):
        rpc.build_review(record, ["fixture"])


@pytest.mark.parametrize("value", [0, "0", "1.0"])
def test_valid_nonnegative_numeric_evidence(value):
    record = load("single_trade_clean_loss.json")
    for section, key in NUMERIC_FIELDS:
        record.setdefault(section, {})[key] = value
    report = rpc.build_review(record, ["fixture"])
    assert report["overall_verdict"] in {"OK", "REVIEW_REQUIRED"}
    assert report["risk_manager_notes"][0]["severity"] == "info"


def test_null_optional_maximum_keeps_planned_risk_fallback():
    record = load("single_trade_clean_loss.json")
    record["risk_plan"]["max_risk_per_trade_r"] = None
    assert rpc.build_review(record, ["fixture"])["overall_verdict"] == "OK"


def test_extreme_finite_risk_comparison_remains_warning():
    record = load("single_trade_clean_loss.json")
    record["actual"]["risk_r"] = 1.7e308
    record["risk_plan"]["max_risk_per_trade_r"] = 1.5e308
    report = rpc.build_review(record, ["fixture"])
    assert report["overall_verdict"] == "REVIEW_REQUIRED"
    assert report["risk_manager_notes"][0]["severity"] == "warning"


@pytest.mark.parametrize("suffix", ["json", "yaml"])
@pytest.mark.parametrize("multiple", [False, True])
@pytest.mark.parametrize("existing", [False, True])
def test_invalid_cli_input_leaves_outputs_untouched(tmp_path, capsys, suffix, multiple, existing):
    record = load("single_trade_clean_loss.json")
    record["risk_plan"]["max_risk_per_trade_r"] = "NaN"
    source = tmp_path / f"invalid.{suffix}"
    if suffix == "yaml":
        import yaml

        source.write_text(yaml.safe_dump(record), encoding="utf-8")
    else:
        source.write_text(json.dumps(record), encoding="utf-8")
    out = tmp_path / "output"
    if existing:
        out.mkdir()
        (out / "report.json").write_text("existing report", encoding="utf-8")
    args = [
        "--input",
        str(source),
        "--output-dir",
        str(out),
        "--json-name",
        "report.json",
        "--markdown",
    ]
    if multiple:
        args[0:0] = ["--input", str(FIXTURES / "single_trade_clean_loss.json")]
    assert rpc.main(args) == 2
    assert "risk_plan.max_risk_per_trade_r" in capsys.readouterr().err
    if existing:
        assert list(out.iterdir()) == [out / "report.json"]
        assert (out / "report.json").read_text() == "existing report"
    else:
        assert not out.exists()


def test_exact_125_percent_risk_is_warning_not_critical():
    record = load("single_trade_clean_loss.json")
    record["actual"]["risk_r"] = 0.75
    record["risk_plan"]["max_risk_per_trade_r"] = 0.6
    report = rpc.build_review(record, ["fixture"])
    assert report["risk_manager_notes"][0]["severity"] == "warning"
