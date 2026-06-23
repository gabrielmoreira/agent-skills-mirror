# engagement-terms-billing-guidelines

**OCM Skills Plugin** — Skill 1 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Drafts, reviews, and maintains outside counsel guidelines (OCGs) — the operational document that sets expectations for how external law firms bill, staff, communicate, and deliver legal services.

OCGs are the single lowest-cost, highest-impact intervention available to an in-house legal ops function. 60% of in-house teams don't have them. Of the 40% that do, 87% barely enforce them. This skill encodes the methodology for building OCGs calibrated to the team's maturity level and producing the internal business case to get them adopted.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Draft OCG | "Draft billing guidelines" / "We don't have billing guidelines" / "Write an OCG" | OCG document + GC Briefing Note + cover email |
| 2 — Review and Gap Analysis | "Review our guidelines" / "What's missing from our OCG" | Gap Analysis + GC Briefing Note |
| 3 — Targeted Update | "Update the AI clause" / "Add D&I requirements" / "Strengthen the rate review terms" | Replacement section text + GC Note |
| 4 — Internal Business Case | "GC briefing on billing guidelines" / "How do I get buy-in for OCGs" | GC Decision Memo |

---

## Key design decisions

**Maturity calibration.** Output length, component coverage, and enforcement intensity are driven by maturity level (Early / Intermediate / Advanced). An Early-stage team gets a concise, collaborative OCG. An Advanced team gets comprehensive provisions with formal enforcement. Start low — escalating maturity is easier than retreating from terms firms have already pushed back on.

**15-component framework.** Gap analysis (Mode 2) assesses against a structured best-practice framework covering rate governance, billing format, prohibited fees, staffing, AI transparency, D&I, and more. Item-level assessment, not an overall score — the user needs to know which specific provisions to fix.

**GC-facing output in every mode.** Every mode produces both the operational document and the GC/leadership-facing document. The user needs the tool and the internal case for using it.

**AI billing clause.** All maturity levels include AI policy provisions. 59% of in-house counsel don't know whether firms are using AI on their matters. The OCG is where disclosure requirements and AI billing rules get established.

**Existing OCG routing.** If the user provides existing OCGs, the skill defaults to Mode 2 (gap analysis) even if they say "help me draft guidelines." Improving what exists is faster and less disruptive than starting from scratch.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| **Billing rules** | **engagement-terms-billing-guidelines (Skill 1) ← this skill** |
| Panel design | panel-design-selection (Skill 2) |
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
| fee-arrangement-structuring (Skill 4) | OCG sets AFA policy preferences. Skill 4 designs the specific arrangement for a matter. |
| matter-allocation-instruction (Skill 5) | OCG is the standing document; the matter instruction references it per engagement. |
| invoice-review-compliance (Skill 6) | OCG defines the rules that invoice review enforces. Weak OCG = nothing to measure against. |
| performance-scorecard (Skill 7) | OCG compliance rate is a scorecard metric. Scorecard identifies non-compliance → OCG update strengthens the provision. |
| panel-review-rationalisation (Skill 8) | OCG adherence is a panel retention criterion. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `engagement-terms-billing-guidelines/SKILL.md` — skill instructions
- `engagement-terms-billing-guidelines-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
