#!/usr/bin/env python3
"""Critically review strategy drafts for edge plausibility, overfitting risk,
sample size adequacy, and execution realism.

Outputs PASS / REVISE / REJECT verdicts with confidence scores.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_EXPORTABLE_FAMILIES = {
    "pivot_breakout",
    "gap_up_continuation",
    "panic_reversal",
    "news_reaction",
}

WEIGHTS: dict[str, int] = {
    "C1_edge_plausibility": 20,
    "C2_overfitting_risk": 20,
    "C3_sample_adequacy": 15,
    "C4_regime_dependency": 10,
    "C5_exit_calibration": 10,
    "C6_risk_concentration": 10,
    "C7_execution_realism": 10,
    "C8_invalidation_quality": 5,
}

DOMAIN_TERMS = {
    "momentum",
    "reversion",
    "drift",
    "earnings",
    "breakout",
    "gap",
    "volume",
    "sentiment",
    "mean",
    "reversal",
    "trend",
    "liquidity",
    "participation",
    "institutional",
    "continuation",
    "contraction",
    "expansion",
    "pivot",
    "vcp",
    "base",
}

MECHANISM_KEYWORDS = {
    "participation",
    "drift",
    "overreaction",
    "accumulation",
    "exhaustion",
    "imbalance",
    "herding",
    "continuation",
    "underreaction",
    "institutional",
}

_PRECISE_THRESHOLD_RE = re.compile(r"(?:\b\d{2,}\.\d+\b|\b\d+\.\d{2,}\b)")


class ReviewError(Exception):
    """Raised when review cannot proceed."""


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ReviewFinding:
    criterion: str
    score: int
    severity: str  # "pass" / "warn" / "fail"
    reason: str
    revision_instruction: str | None = None


@dataclass
class DraftReview:
    draft_id: str
    verdict: str  # PASS / REVISE / REJECT
    confidence_score: int
    export_eligible: bool
    findings: list[ReviewFinding] = field(default_factory=list)
    revision_instructions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Criterion evaluators  (C1 – C8)
# ---------------------------------------------------------------------------


def _severity_from_score(score: int) -> str:
    if score < 30:
        return "fail"
    if score < 60:
        return "warn"
    return "pass"


def evaluate_c1(draft: dict) -> ReviewFinding:
    """C1: Edge Plausibility."""
    thesis = str(draft.get("thesis", "")).strip()
    words = thesis.split()
    if not thesis or len(words) < 3:
        return ReviewFinding(
            criterion="C1_edge_plausibility",
            score=10,
            severity="fail",
            reason=f"Thesis too short ({len(words)} words). Must articulate a causal edge hypothesis.",
            revision_instruction="Expand thesis to describe the causal mechanism behind the expected edge.",
        )
    lower = thesis.lower()
    has_domain = any(term in lower for term in DOMAIN_TERMS)
    if len(words) < 10 and not has_domain:
        return ReviewFinding(
            criterion="C1_edge_plausibility",
            score=40,
            severity="warn",
            reason="Thesis is generic with no domain-specific causal reasoning.",
            revision_instruction="Add specific causal mechanism (e.g., institutional participation, earnings drift).",
        )
    # Continuous scoring for the pass path
    domain_count = sum(1 for term in DOMAIN_TERMS if term in lower)
    score = 50 + min(domain_count * 10, 30)
    if len(words) >= 10:
        score += 10
    if len(words) > 20:
        score += 10
    has_mechanism = any(kw in lower for kw in MECHANISM_KEYWORDS)
    if has_mechanism:
        score += 10
    score = min(score, 95)
    return ReviewFinding(
        criterion="C1_edge_plausibility",
        score=score,
        severity="pass",
        reason="Thesis contains specific causal reasoning.",
    )


def evaluate_c2(draft: dict) -> ReviewFinding:
    """C2: Overfitting Risk."""
    entry = draft.get("entry", {})
    conditions = entry.get("conditions", []) if isinstance(entry.get("conditions"), list) else []
    trend_filter = (
        entry.get("trend_filter", []) if isinstance(entry.get("trend_filter"), list) else []
    )
    total = len(conditions) + len(trend_filter)

    if total >= 13:
        score = 10
    elif total >= 11:
        score = 40
    elif total >= 8:
        score = 60
    elif total >= 5:
        score = 80
    else:
        score = 90

    # Precise threshold penalty
    precise_count = 0
    for c in conditions:
        if isinstance(c, str):
            precise_count += len(_PRECISE_THRESHOLD_RE.findall(c))
    score = max(score - 10 * precise_count, 0)

    severity = _severity_from_score(score)
    parts = []
    if total > 10:
        parts.append(
            f"{total} combined filters ({len(conditions)} conditions + {len(trend_filter)} trend)"
        )
    if precise_count:
        parts.append(f"{precise_count} precise threshold(s) detected")
    reason = "; ".join(parts) if parts else f"{total} filters within acceptable range."

    instruction = None
    if severity != "pass":
        instructions = []
        if total > 10:
            instructions.append("Reduce entry conditions to 5 most predictive")
        if precise_count:
            instructions.append("Round precise thresholds to standard increments")
        instruction = "; ".join(instructions)

    return ReviewFinding(
        criterion="C2_overfitting_risk",
        score=score,
        severity=severity,
        reason=reason,
        revision_instruction=instruction,
    )


def estimate_annual_opportunities(draft: dict) -> int:
    """Estimate yearly trading signals from condition restrictiveness."""
    entry = draft.get("entry", {})
    conditions = entry.get("conditions", []) if isinstance(entry.get("conditions"), list) else []
    trend_filter = (
        entry.get("trend_filter", []) if isinstance(entry.get("trend_filter"), list) else []
    )

    base = 252
    if any("sector" in str(c).lower() for c in conditions):
        base //= 3
    regime = str(draft.get("regime", ""))
    if regime not in ("", "Unknown", "Neutral"):
        base //= 2

    base = int(base * (0.8 ** len(conditions)))
    base = int(base * (0.85 ** len(trend_filter)))
    return max(base, 1)


def _c3_score_from_estimate(est: int) -> int:
    """Map estimated annual opportunities to a continuous score."""
    if est < 10:
        return 10
    if est <= 29:
        # Linear interpolation 30..59 over est 10..29
        return 30 + int(round((est - 10) / (29 - 10) * (59 - 30)))
    if est <= 49:
        # Linear interpolation 65..74 over est 30..49
        return 65 + int(round((est - 30) / (49 - 30) * (74 - 65)))
    if est <= 99:
        # Linear interpolation 75..85 over est 50..99
        return 75 + int(round((est - 50) / (99 - 50) * (85 - 75)))
    # est >= 100: linear interpolation 85..95 capped at 95 for est>=200
    capped = min(est, 200)
    return 85 + int(round((capped - 100) / (200 - 100) * (95 - 85)))


def evaluate_c3(draft: dict) -> ReviewFinding:
    """C3: Sample Adequacy."""
    est = estimate_annual_opportunities(draft)
    score = _c3_score_from_estimate(est)
    severity = _severity_from_score(score)

    reason = f"Estimated {est} annual opportunities."
    instruction = None
    if severity != "pass":
        instruction = (
            "Relax conditions or remove sector/regime restrictions to increase sample size."
        )
    return ReviewFinding(
        criterion="C3_sample_adequacy",
        score=score,
        severity=severity,
        reason=reason,
        revision_instruction=instruction,
    )


def evaluate_c4(draft: dict) -> ReviewFinding:
    """C4: Regime Dependency."""
    regime = str(draft.get("regime", ""))
    is_single = regime not in ("", "Unknown", "Neutral")
    if not is_single:
        return ReviewFinding(
            criterion="C4_regime_dependency",
            score=80,
            severity="pass",
            reason="Strategy not restricted to single regime.",
        )

    # Check for cross-regime validation
    vp = draft.get("validation_plan", {})
    if isinstance(vp, dict):
        vp_text = json.dumps(vp).lower()
        if "regime" in vp_text:
            return ReviewFinding(
                criterion="C4_regime_dependency",
                score=80,
                severity="pass",
                reason=f"Single regime ({regime}) but cross-regime validation planned.",
            )

    return ReviewFinding(
        criterion="C4_regime_dependency",
        score=40,
        severity="warn",
        reason=f"Restricted to {regime} with no cross-regime validation plan.",
        revision_instruction="Add cross-regime validation to success criteria.",
    )


def evaluate_c5(draft: dict) -> ReviewFinding:
    """C5: Exit Calibration."""
    exit_conf = draft.get("exit", {})
    stop = float(exit_conf.get("stop_loss_pct", 0))
    rr = float(exit_conf.get("take_profit_rr", 0))

    problems = []
    if stop > 0.15:
        problems.append(f"stop_loss_pct={stop:.0%} exceeds 15%")
    if rr < 1.5:
        problems.append(f"take_profit_rr={rr:.1f} below 1.5")

    if problems:
        score = 10
        severity = "fail"
        reason = "; ".join(problems)
        instruction = "Tighten stop-loss to <=15% and ensure reward-to-risk >= 1.5."
    else:
        score, severity = 80, "pass"
        reason = f"Exit parameters acceptable (stop={stop:.0%}, RR={rr:.1f})."
        instruction = None

    return ReviewFinding(
        criterion="C5_exit_calibration",
        score=score,
        severity=severity,
        reason=reason,
        revision_instruction=instruction,
    )


def evaluate_c6(draft: dict) -> ReviewFinding:
    """C6: Risk Concentration."""
    risk = draft.get("risk", {})
    rpt = float(risk.get("risk_per_trade", 0))
    mp = int(risk.get("max_positions", 0))

    problems = []
    worst_score = 80
    if rpt > 0.02:
        problems.append(f"risk_per_trade={rpt:.1%} exceeds 2%")
        worst_score = min(worst_score, 10)
    elif rpt > 0.015:
        problems.append(f"risk_per_trade={rpt:.1%} exceeds 1.5%")
        worst_score = min(worst_score, 40)
    if mp > 10:
        problems.append(f"max_positions={mp} exceeds 10")
        worst_score = min(worst_score, 10)

    severity = _severity_from_score(worst_score)
    reason = "; ".join(problems) if problems else "Risk parameters within acceptable range."
    instruction = None
    if severity != "pass":
        instruction = "Reduce risk_per_trade to <=1.5% and max_positions to <=10."

    return ReviewFinding(
        criterion="C6_risk_concentration",
        score=worst_score,
        severity=severity,
        reason=reason,
        revision_instruction=instruction,
    )


def evaluate_c7(draft: dict, exportable_families: set[str] | None = None) -> ReviewFinding:
    """C7: Execution Realism."""
    families = (
        exportable_families if exportable_families is not None else DEFAULT_EXPORTABLE_FAMILIES
    )
    entry = draft.get("entry", {})
    conditions = entry.get("conditions", []) if isinstance(entry.get("conditions"), list) else []
    has_volume = any("volume" in str(c).lower() for c in conditions)

    export_ready = bool(draft.get("export_ready_v1", False))
    family = str(draft.get("entry_family", ""))
    bad_export = export_ready and family not in families

    if bad_export:
        return ReviewFinding(
            criterion="C7_execution_realism",
            score=10,
            severity="fail",
            reason=f"export_ready_v1=true but entry_family='{family}' not in exportable families.",
            revision_instruction=f"Set export_ready_v1=false or change entry_family to one of {sorted(families)}.",
        )
    if not has_volume:
        return ReviewFinding(
            criterion="C7_execution_realism",
            score=50,
            severity="warn",
            reason="No volume filter in entry conditions.",
            revision_instruction="Add volume filter (e.g., avg_volume > 500000) for execution realism.",
        )
    return ReviewFinding(
        criterion="C7_execution_realism",
        score=80,
        severity="pass",
        reason="Volume filter present and export settings consistent.",
    )


def evaluate_c8(draft: dict) -> ReviewFinding:
    """C8: Invalidation Quality."""
    signals = draft.get("invalidation_signals", [])
    if not isinstance(signals, list):
        signals = []

    if len(signals) == 0:
        score, severity = 10, "fail"
        reason = "No invalidation signals defined."
        instruction = "Add at least 2 concrete invalidation signals."
    elif len(signals) < 2:
        score, severity = 40, "warn"
        reason = f"Only {len(signals)} invalidation signal(s); minimum 2 recommended."
        instruction = "Add additional invalidation signal for robustness."
    else:
        score, severity = 80, "pass"
        reason = f"{len(signals)} invalidation signals defined."
        instruction = None

    return ReviewFinding(
        criterion="C8_invalidation_quality",
        score=score,
        severity=severity,
        reason=reason,
        revision_instruction=instruction,
    )


# ---------------------------------------------------------------------------
# Review engine
# ---------------------------------------------------------------------------

ALL_EVALUATORS = [
    evaluate_c1,
    evaluate_c2,
    evaluate_c3,
    evaluate_c4,
    evaluate_c5,
    evaluate_c6,
    evaluate_c7,
    evaluate_c8,
]


def compute_confidence_score(findings: list[ReviewFinding]) -> int:
    """Weighted average of finding scores."""
    total_weight = 0
    weighted_sum = 0
    for f in findings:
        w = WEIGHTS.get(f.criterion, 0)
        weighted_sum += f.score * w
        total_weight += w
    if total_weight == 0:
        return 0
    return int(round(weighted_sum / total_weight))


def determine_verdict(findings: list[ReviewFinding], confidence: int) -> str:
    """Determine PASS / REVISE / REJECT."""
    # C1 or C2 fail → immediate REJECT
    for f in findings:
        if f.criterion in ("C1_edge_plausibility", "C2_overfitting_risk") and f.severity == "fail":
            return "REJECT"
    has_fail = any(f.severity == "fail" for f in findings)
    if confidence >= 70 and not has_fail:
        return "PASS"
    if confidence < 35:
        return "REJECT"
    return "REVISE"


def is_export_eligible(
    draft: dict, verdict: str, exportable_families: set[str] | None = None
) -> bool:
    """Check if draft qualifies for pipeline export."""
    families = (
        exportable_families if exportable_families is not None else DEFAULT_EXPORTABLE_FAMILIES
    )
    return (
        verdict == "PASS"
        and bool(draft.get("export_ready_v1", False))
        and str(draft.get("entry_family", "")) in families
    )


BUNDLED_CHECKLIST = Path(__file__).resolve().parent.parent / "assets" / "bias_checklist.yaml"

BIAS_SCHEMA_VERSION = "1.0"


def load_bias_checklist(path: Path) -> list[dict]:
    """Load and validate bias checklist items from a YAML file.

    The checklist schema is ``{"schema_version": str, "items": [{id, title,
    required, coverage_hint}]}``. Items missing ``id`` or ``coverage_hint`` are
    rejected so the reviewer never silently skips a required rule.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ReviewError(f"Could not read bias checklist {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ReviewError(f"Bias checklist {path} must contain an 'items' list")
    declared = data.get("schema_version")
    if declared is not None and str(declared) != BIAS_SCHEMA_VERSION:
        raise ReviewError(
            f"Bias checklist {path} schema_version {declared!r} "
            f"does not match expected {BIAS_SCHEMA_VERSION!r}"
        )
    items: list[dict] = []
    for raw in data["items"]:
        if not isinstance(raw, dict) or not raw.get("id") or not raw.get("coverage_hint"):
            raise ReviewError(f"Invalid bias checklist item in {path}: {raw!r}")
        items.append(
            {
                "id": str(raw["id"]),
                "title": str(raw.get("title", raw["id"])),
                "required": bool(raw.get("required", True)),
                "coverage_hint": str(raw["coverage_hint"]),
            }
        )
    return items


def _draft_text(draft: dict) -> str:
    """Flatten all scalar text in a draft (excluding its bias block) for hint matching."""

    parts: list[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "bias_checklist":
                    continue
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
        elif isinstance(obj, (str, int, float, bool)):
            parts.append(str(obj))

    walk(draft)
    return " ".join(parts)


def evaluate_bias_checklist(draft: dict, items: list[dict]) -> list[dict]:
    """Score one draft against the bias checklist.

    An item is ``addressed`` iff the draft declares it in its ``bias_checklist``
    block with a truthy value (a dict with ``addressed`` truthy and defaulting to
    true when absent; a plain truthy scalar is also addressed). ``noted_in_draft``
    is an informational heuristic that reports whether the item's concept text
    appears anywhere in the draft, so an author can see that a rule is discussed
    but not yet declared. Escalation in :func:`apply_bias_gate` is driven solely
    by ``addressed``.
    """
    declared = draft.get("bias_checklist")
    declared_map = declared if isinstance(declared, dict) else {}
    text = _draft_text(draft)
    results: list[dict] = []
    for item in items:
        value = declared_map.get(item["id"])
        if isinstance(value, dict):
            addressed = bool(value.get("addressed", True))
            note = str(value.get("note", ""))
        else:
            addressed = bool(value)
            note = str(value) if value else ""
        try:
            notion = re.search(item["coverage_hint"], text, re.IGNORECASE)
        except re.error:
            notion = None
        results.append(
            {
                "item_id": item["id"],
                "title": item["title"],
                "required": item["required"],
                "addressed": addressed,
                "noted_in_draft": bool(notion),
                "note": note,
            }
        )
    return results


def apply_bias_gate(review: DraftReview, bias_results: list[dict]) -> bool:
    """Downgrade PASS -> REVISE when a required bias item is unaddressed.

    Returns True when the verdict was downgraded. This is non-scoring: it never
    changes the confidence score, C1-C8 weights, or a REJECT verdict. On
    downgrade, export eligibility is cleared to match the ``strict_export``
    behavior, so a REVISE draft is never export-eligible.
    """
    unaddressed = [r for r in bias_results if r["required"] and not r["addressed"]]
    if not unaddressed:
        return False
    if review.verdict == "PASS":
        review.verdict = "REVISE"
        review.export_eligible = False
        names = ", ".join(r["item_id"] for r in unaddressed)
        review.revision_instructions.append(
            f"Declare how {names} {('is' if len(unaddressed) == 1 else 'are')} "
            "addressed in the draft's bias_checklist block"
        )
        return True
    return False


def _review_bias_for_all(
    drafts: list[dict], reviews: list[DraftReview], bias_items: list[dict]
) -> dict[str, list[dict]]:
    """Evaluate the bias checklist for every draft and apply the verdict gate.

    Drafts and reviews are joined positionally (``review_draft`` preserves the
    ``load_drafts_from_dir`` ordering), so the ``bias_by_id`` map is keyed by
    each review's ``draft_id``.
    """
    bias_by_id: dict[str, list[dict]] = {}
    for draft, review in zip(drafts, reviews):
        results = evaluate_bias_checklist(draft, bias_items)
        apply_bias_gate(review, results)
        bias_by_id[review.draft_id] = results
    return bias_by_id


def review_draft(
    draft: dict, *, strict_export: bool = False, exportable_families: set[str] | None = None
) -> DraftReview:
    """Review a single strategy draft.

    When *strict_export* is True, export-eligible drafts that have any
    warn-level findings are downgraded from PASS to REVISE so that the
    warnings must be resolved before export.
    """
    draft_id = str(draft.get("id", "unknown"))
    findings = [
        ev(draft, exportable_families) if ev is evaluate_c7 else ev(draft) for ev in ALL_EVALUATORS
    ]
    confidence = compute_confidence_score(findings)
    verdict = determine_verdict(findings, confidence)
    export_ok = is_export_eligible(draft, verdict, exportable_families)

    # Strict export: export-eligible PASS with any warn → REVISE
    if strict_export and verdict == "PASS" and export_ok:
        has_warn = any(f.severity == "warn" for f in findings)
        if has_warn:
            verdict = "REVISE"
            export_ok = False

    instructions: list[str] = []
    if verdict == "REVISE":
        instructions = [
            f.revision_instruction
            for f in findings
            if f.revision_instruction and f.severity in ("warn", "fail")
        ]

    return DraftReview(
        draft_id=draft_id,
        verdict=verdict,
        confidence_score=confidence,
        export_eligible=export_ok,
        findings=findings,
        revision_instructions=instructions,
    )


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def load_draft_file(path: Path) -> dict:
    """Load a single draft YAML."""
    text = path.read_text()
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ReviewError(f"Invalid draft format in {path}: expected mapping")
    return data


def load_drafts_from_dir(drafts_dir: Path) -> list[dict]:
    """Load all YAML drafts from a directory."""
    files = sorted(drafts_dir.glob("*.yaml"))
    if not files:
        raise ReviewError(f"No .yaml files found in {drafts_dir}")
    drafts = []
    for f in files:
        # Skip manifest or non-draft files
        if f.name.startswith("run_manifest"):
            continue
        try:
            drafts.append(load_draft_file(f))
        except Exception as exc:
            print(f"[WARN] Skipping {f.name}: {exc}", file=sys.stderr)
    return drafts


def build_output(
    drafts_source: str,
    draft_count: int,
    reviews: list[DraftReview],
    bias_by_id: dict[str, list[dict]] | None = None,
) -> dict[str, Any]:
    """Build the output payload.

    When ``bias_by_id`` is supplied, each review that has a matching key gets a
    ``bias_review`` block merged into its serialized dict. When it is not
    supplied (checklist flag off) the key is omitted entirely so the output is
    byte-identical to before the bias feature.
    """
    summary = {"total": draft_count, "PASS": 0, "REVISE": 0, "REJECT": 0, "export_eligible": 0}  # nosec B105
    for r in reviews:
        summary[r.verdict] = summary.get(r.verdict, 0) + 1
        if r.export_eligible:
            summary["export_eligible"] += 1

    reviews_payload: list[dict[str, Any]] = []
    for r in reviews:
        payload = asdict(r)
        if bias_by_id and r.draft_id in bias_by_id:
            payload["bias_review"] = bias_by_id[r.draft_id]
        reviews_payload.append(payload)

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {
            "drafts_dir": drafts_source,
            "draft_count": draft_count,
        },
        "summary": summary,
        "reviews": reviews_payload,
    }


def build_markdown_summary(output: dict) -> str:
    """Generate a human-readable markdown summary."""
    lines = [
        "# Strategy Draft Review Summary",
        "",
        f"**Generated:** {output['generated_at_utc']}",
        f"**Source:** {output['source']['drafts_dir']}",
        f"**Drafts reviewed:** {output['source']['draft_count']}",
        "",
        "## Verdict Summary",
        "",
        "| Verdict | Count |",
        "|---------|-------|",
    ]
    s = output["summary"]
    for v in ("PASS", "REVISE", "REJECT"):
        lines.append(f"| {v} | {s.get(v, 0)} |")
    lines.append(f"| Export Eligible | {s.get('export_eligible', 0)} |")
    lines.append("")
    lines.append("## Individual Reviews")
    lines.append("")

    for r in output.get("reviews", []):
        verdict_icon = {"PASS": "PASS", "REVISE": "REVISE", "REJECT": "REJECT"}.get(  # nosec B105
            r["verdict"], r["verdict"]
        )
        lines.append(f"### {r['draft_id']} — {verdict_icon} (confidence: {r['confidence_score']})")
        if r.get("export_eligible"):
            lines.append("**Export eligible**")
        lines.append("")
        lines.append("| Criterion | Score | Severity | Reason |")
        lines.append("|-----------|-------|----------|--------|")
        for f in r.get("findings", []):
            lines.append(f"| {f['criterion']} | {f['score']} | {f['severity']} | {f['reason']} |")
        if r.get("bias_review"):
            unaddressed = [b for b in r["bias_review"] if b["required"] and not b["addressed"]]
            lines.append("")
            lines.append("**Bias Checklist:**")
            lines.append("")
            lines.append("| Item | Required | Addressed | Note |")
            lines.append("|------|----------|-----------|------|")
            for b in r["bias_review"]:
                lines.append(
                    f"| {b['item_id']} | {b['required']} | {b['addressed']} | {b.get('note', '')} |"
                )
            if unaddressed:
                lines.append("")
                lines.append(
                    "_Unaddressed required items: "
                    + ", ".join(b["item_id"] for b in unaddressed)
                    + "_"
                )
        if r.get("revision_instructions"):
            lines.append("")
            lines.append("**Revision Instructions:**")
            for inst in r["revision_instructions"]:
                lines.append(f"- {inst}")
        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Review strategy drafts for edge plausibility and quality.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--drafts-dir", help="Directory containing strategy draft YAML files")
    group.add_argument("--draft", help="Path to a single strategy draft YAML file")
    parser.add_argument(
        "--output-dir", default="reports/", help="Output directory (default: reports/)"
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )
    parser.add_argument(
        "--markdown-summary",
        action="store_true",
        help="Generate additional markdown summary file",
    )
    parser.add_argument(
        "--strict-export",
        action="store_true",
        default=False,
        help="Export-eligible drafts with any warn finding get REVISE instead of PASS",
    )
    parser.add_argument(
        "--exportable-families",
        default=None,
        help="Comma-separated list of exportable entry families (overrides module default)",
    )
    parser.add_argument(
        "--bias-checklist",
        nargs="?",
        const=BUNDLED_CHECKLIST,
        default=None,
        help=(
            "Enable the strategy-research bias checklist review against the bundled "
            "checklist (default) or a custom YAML path. Without this flag, the bias "
            "review is not applied and output matches prior behavior."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_args(argv)
    output_dir = Path(args.output_dir).resolve()

    ef_override: set[str] | None = None
    if args.exportable_families:
        ef_override = {f.strip() for f in args.exportable_families.split(",") if f.strip()}

    try:
        if args.drafts_dir:
            drafts_dir = Path(args.drafts_dir).resolve()
            if not drafts_dir.is_dir():
                raise ReviewError(f"Drafts directory not found: {drafts_dir}")
            drafts = load_drafts_from_dir(drafts_dir)
            source = str(drafts_dir)
        else:
            draft_path = Path(args.draft).resolve()
            if not draft_path.is_file():
                raise ReviewError(f"Draft file not found: {draft_path}")
            drafts = [load_draft_file(draft_path)]
            source = str(draft_path)

        if not drafts:
            raise ReviewError("No valid drafts to review.")

        reviews = [
            review_draft(d, strict_export=args.strict_export, exportable_families=ef_override)
            for d in drafts
        ]
        # When --bias-checklist is supplied without a path, the bundled checklist
        # under assets/ is used. Without the flag, bias is not applied and the
        # output matches prior behavior.
        bias_by_id: dict[str, list[dict]] | None = None
        if args.bias_checklist is not None:
            checklist_path = Path(args.bias_checklist).resolve()
            if not checklist_path.is_file():
                raise ReviewError(f"Bias checklist not found: {checklist_path}")
            bias_items = load_bias_checklist(checklist_path)
            bias_by_id = _review_bias_for_all(drafts, reviews, bias_items)

        output = build_output(source, len(drafts), reviews, bias_by_id)

        output_dir.mkdir(parents=True, exist_ok=True)
        ext = args.output_format
        out_path = output_dir / f"review.{ext}"
        if ext == "yaml":
            out_path.write_text(
                yaml.safe_dump(output, sort_keys=False, default_flow_style=False), encoding="utf-8"
            )
        else:
            out_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

        if args.markdown_summary:
            md_path = output_dir / "review_summary.md"
            md_path.write_text(build_markdown_summary(output), encoding="utf-8")

    except ReviewError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    s = output["summary"]
    print(
        f"[OK] Reviewed {s['total']} drafts: "
        f"PASS={s['PASS']} REVISE={s['REVISE']} REJECT={s['REJECT']} "
        f"export_eligible={s['export_eligible']} output={out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
