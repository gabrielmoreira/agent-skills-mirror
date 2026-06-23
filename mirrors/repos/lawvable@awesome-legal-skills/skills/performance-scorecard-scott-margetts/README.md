# performance-scorecard

**OCM Skills Plugin** — Skill 7 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Performance scorecard design, post-matter feedback collection, QBR preparation, and firm comparison for in-house legal ops teams evaluating outside counsel.

Encodes the methodology for collecting, aggregating, and acting on firm performance data across the relationship lifecycle — from building the initial evaluation framework through to the comparative analysis that informs panel retention and exit decisions.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Scorecard Design | "Build us a scorecard" / "How do we evaluate our firms" / "Design a performance scorecard" | Performance Scorecard Framework + GC Implementation Note |
| 2 — Post-Matter Feedback | "Post-matter feedback form" / "Collect feedback on the firm" / "Feedback at matter close" | Matter Feedback Form + Feedback Collection Note |
| 3 — QBR Preparation | "Prep for the firm review" / "QBR with [firm]" / "Quarterly business review" | QBR Pack (agenda + data summary + talking points) + Internal Briefing Note |
| 4 — Firm Comparison | "Compare the firms" / "Which firm is performing better" / "Rank our panel" | Comparative Scorecard Table + Selection Recommendation Note |

---

## Key design decisions

**Maturity calibration as the primary design variable.** All four modes calibrate to maturity level (Early / Intermediate / Advanced per ACC framework). Mode 1 applied to an Early-stage team produces a 5-criterion Excel-ready scorecard; applied to an Advanced team it produces a dashboard-integrated framework with competitive benchmarking.

**Mode 4 works with partial data.** Firm comparison input is reliably sparse — full scorecard data rarely exists for all firms simultaneously. The mode uses [Data gap] markers rather than declining to produce the comparison.

**Two-layer output.** Every mode produces an operational document (the tool the user runs the process with) and a decision-maker document (the GC/leadership summary that drives action).

**QBR standing structure.** Mode 3 encodes a standard QBR agenda: performance review, billing compliance, matters in progress, upcoming pipeline, relationship and team issues, action items. Talking points are calibrated to address known issues rather than generic check-ins.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| Panel design | panel-design-selection (Skill 2) |
| Firm selection | rfp-pitch-management (Skill 3) |
| Fee arrangements | fee-arrangement-structuring (Skill 4) |
| Matter instruction | matter-allocation-instruction (Skill 5) |
| Invoice review | invoice-review-compliance (Skill 6) |
| **Performance management** | **performance-scorecard (Skill 7) ← this skill** |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| invoice-review-compliance (Skill 6) | Billing compliance rate and rejection records feed quantitative scorecard criteria. Direct input to Modes 1, 3, and 4. |
| matter-allocation-instruction (Skill 5) | Matter close triggers Mode 2 post-matter feedback. |
| panel-review-rationalisation (Skill 8) | Accumulated scorecard data feeds the periodic formal panel review. This skill collects; Skill 8 assesses. |
| rfp-pitch-management (Skill 3) | Historical scorecard data informs RFP evaluation criteria and shortlisting. |
| panel-design-selection (Skill 2) | Scorecard output (particularly Mode 4 comparative data) informs panel retention and exit decisions. |
| engagement-terms-billing-guidelines (Skill 1) | OCG compliance rate is a scorecard metric. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `performance-scorecard/SKILL.md` — skill instructions
- `performance-scorecard-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
