# panel-review-rationalisation

**OCM Skills Plugin** — Skill 8 of 8
**Status:** Complete — Phase 1 and Phase 2 tested. Modes 3 and 4 published with known failure modes (see below).

---

## What this skill does

Executes the annual panel review cycle and ongoing panel governance decisions. Synthesises performance scorecard data, billing compliance records, and step-out patterns into panel-level recommendations. Produces the documentation for firm exits, coverage gap assessment, and competitive refresh processes.

Covers the full panel governance workflow: annual health assessment through to firm exit and slot refresh.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Panel Health Assessment | "Review our panel" / "Annual panel review" / "Is our panel working" | Panel Health Report + GC Panel Review Note |
| 2 — Firm Exit Management | "Exit [firm] from the panel" / "Write the exit notice" / "Formal panel removal" | Firm Exit Notice and Transition Plan + Internal Exit Record |
| 3 — Coverage Gap Analysis | "We have a gap" / "We don't have anyone for [area]" / "Coverage gap" | Coverage Gap Report + Remediation Options Note |
| 4 — Panel Refresh Brief | "Refresh the panel" / "Fill the gap" / "Competitive process for [area]" | Panel Refresh Brief + RFP Scope Note |

---

## Key design decisions

**Improvement plan before exit.** The domain knowledge encodes the improvement plan requirement: exit on performance grounds without a prior improvement plan is harder to defend. Mode 2 doesn't make this a binary gate — the Internal Exit Record has a "Prior improvement plan" field that documents the history.

**Mode 2 Type 2 placeholder.** The Firm Exit Notice uses [Firm] as a deliberate review gate — it stays as [Firm] in the external document even when the firm name is provided in session. The internal exit record uses the firm's actual name. Same pattern as the Formal Non-Compliance Notice in invoice-review-compliance (Skill 6).

**Step-out as a leading indicator.** Step-out frequency connects to three diagnoses: coverage gap, underperforming panel firm, or panel discipline failure. This is the methodology connecting Mode 3 (gap identification) back to Mode 1 (panel health) and forward to Mode 4 (refresh).

**Mode 4 as hand-off document.** The Panel Refresh Brief is framed as a scoped input to rfp-pitch-management (Skill 3), not a standalone decision. Template includes a hand-off instruction block naming the appropriate Skill 3 mode as the next step.

**Consequence framework.** Mode 1 Panel Health Report maps each firm to one of four recommendations: Retain, Watch, Improvement Plan, or Exit Review. Each recommendation has defined trigger criteria and consequences.

---

## Known limitations — Modes 3 and 4

Modes 3 and 4 have documented failure modes identified during Phase 2 testing. Four instruction-based fix attempts on Mode 3 and three on Mode 4 produced no change in the failure pattern.

**Mode 3 failure pattern:** Produces consulting prose with numbered strategic options instead of the structured Coverage Gap Report template. Closes with offer or question menu.

**Mode 4 failure pattern:** Produces Skill 3 execution documents (RFP, longlist, capabilities questionnaire with named firms) instead of the Panel Refresh Brief template. Web search runs pre-document. Account-level context may appear.

**Root cause:** Rich domain knowledge overrides template instructions when input is conversational (Mode 3) or execution-oriented (Mode 4). The model ignores first-token anchors and IS/IS NOT definitions when it has sufficient domain knowledge to generate plausible alternative content.

**Impact:** Modes 3 and 4 will produce useful content on the right topic but may not follow the template structure. Modes 1 and 2 are clean.

**Future revision path:** Two-step intake exchange before document production, or fundamentally different design accepting conversational register and routing to structured output differently.

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
| Performance management | performance-scorecard (Skill 7) |
| **Panel review** | **panel-review-rationalisation (Skill 8) ← this skill** |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| performance-scorecard (Skill 7) | Scorecard tier per firm feeds Mode 1 Panel Health Assessment. Primary data input. |
| invoice-review-compliance (Skill 6) | Billing compliance rate and violation records feed Mode 1. |
| matter-allocation-instruction (Skill 5) | Step-out log and matter allocation records feed Mode 1 and Mode 3 gap identification. |
| panel-design-selection (Skill 2) | Defines original panel structure and selection criteria against which review assesses each firm. |
| rfp-pitch-management (Skill 3) | Receives Mode 4 Panel Refresh Brief as input. Executes the competitive process to fill an identified slot. |
| engagement-terms-billing-guidelines (Skill 1) | OCG adherence is a panel retention criterion in Mode 1. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `panel-review-rationalisation/SKILL.md` — skill instructions
- `panel-review-rationalisation-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
