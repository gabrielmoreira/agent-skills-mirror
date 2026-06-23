# panel-design-selection

**OCM Skills Plugin** — Skill 2 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Designs panel structures, defines firm selection criteria, runs right-sourcing analysis, and assesses coverage gaps for in-house legal teams building or formalising their outside counsel panel.

Panel design is not panel review. Design asks: what should the panel look like? Review asks: is the panel performing? This skill builds the framework. Panel-review-rationalisation (Skill 8) measures against it.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Panel Design | "Design our panel" / "How many firms do we need" / "Panel structure" | Panel Design Document + GC Briefing Note |
| 2 — Selection Criteria Framework | "Firm selection criteria" / "How do we choose firms" / "Weight the criteria" | Selection Criteria Matrix + GC Briefing Note |
| 3 — Right-Sourcing Analysis | "Right-sourcing" / "Are we sending work to the right firms" / "Do we need BigLaw for this" | Right-Sourcing Analysis + GC Briefing Note |
| 4 — Coverage Gap Analysis | "Panel gaps" / "We need a firm for [area]" / "Too many firms" / "Consolidate" | Coverage Assessment + GC Briefing Note |

---

## Key design decisions

**Dual-use criteria framework.** The selection criteria matrix (Mode 2) is designed for both RFP evaluation (rfp-pitch-management) and ongoing performance measurement (performance-scorecard). The criteria you select firms on should be the criteria you evaluate them against. If the framework is used once for selection and then filed, it has failed.

**ABC tiering for right-sourcing.** Mode 3 classifies work into three tiers — Complex/Strategic (A), Specialist/Substantial (B), Routine/Volume (C) — and maps current provider allocation against them. The most common mismatch is Tier C work at Tier A providers. That's where the financial impact sits.

**Relationship dimension flagged.** Right-sourcing recommendations that affect a firm the GC has a strong relationship with are explicitly flagged. The analysis is about the work, not the firm. The GC decides how to act on it.

**Pilot-first reallocation.** Right-sourcing recommendations include a recommended pilot scope rather than wholesale reallocation. A pilot produces evidence that makes the case for broader change.

**Benchmarks by spend.** Panel size recommendations are anchored to annual spend benchmarks rather than abstract best practice. Under £2m: 3–5 firms. £2m–£10m: 5–10. Over £10m: 8–15+.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| **Panel design** | **panel-design-selection (Skill 2) ← this skill** |
| Firm selection | rfp-pitch-management (Skill 3) |
| Fee arrangements | fee-arrangement-structuring (Skill 4) |
| Matter instruction | matter-allocation-instruction (Skill 5) |
| Invoice review | invoice-review-compliance (Skill 6) |
| Performance management | performance-scorecard (Skill 7) |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| rfp-pitch-management (Skill 3) | Panel structure and selection criteria feed directly into RFP design and evaluation. |
| engagement-terms-billing-guidelines (Skill 1) | Panel tier determines OCG intensity. Strategic partners may have negotiated terms. |
| performance-scorecard (Skill 7) | Selection criteria framework is the baseline for ongoing performance measurement. |
| panel-review-rationalisation (Skill 8) | This skill builds the framework; Skill 8 assesses the panel against it. |
| matter-allocation-instruction (Skill 5) | Panel structure determines which firm gets which type of matter. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `panel-design-selection/SKILL.md` — skill instructions
- `panel-design-selection-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
