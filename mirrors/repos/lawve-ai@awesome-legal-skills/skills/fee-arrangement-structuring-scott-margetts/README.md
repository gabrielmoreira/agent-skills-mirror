# fee-arrangement-structuring

**OCM Skills Plugin** — Skill 4 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Structures commercial fee arrangements between in-house legal teams and outside counsel. Designs AFAs (fixed, capped, collar, blended, phased, success), assesses whether scope supports a proposed structure, prepares commercial positions for fee negotiations, reviews existing arrangements against delivery data, and assesses out-of-scope claims.

Five modes covering the full AFA lifecycle — from initial design through to scope dispute response.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — AFA Design | "Structure the fee" / "Design an AFA" / "Move off hourly" / "Fixed fee for this work" | AFA Recommendation Memo + GC Sign-off Brief |
| 2 — Scope-to-Fee Matching | "Does scope support a fixed fee?" / "Can we do a cap on this?" | Scope-Fee Assessment + Recommendation Note |
| 3 — AFA Negotiation Brief | "Negotiate the fee" / "Renegotiate the arrangement" / "AI should reduce the cost" | Negotiation Brief + Talking Points |
| 4 — AFA Health Check | "Is our AFA holding?" / "Fee health check" / "Cap is being approached" | AFA Health Assessment + Action Recommendation |
| 5 — Scope Dispute Assessment | "Firm is claiming OOS" / "Is this in scope?" / "Is this OOS?" | Scope Assessment + Dispute Response Note |

---

## Key design decisions

**Boundary with LPM Core.** fee-arrangement-structuring designs and negotiates the commercial structure across matters and firm relationships. budget-and-fee-manager (LPM Core) builds the phase-based budget and monitors WIP variance on a single matter within that structure. The arrangement the AFA skill agrees is what the budget skill monitors.

**Scope status as a design input.** Mode 1 uses scope status (Defined / Partially defined / Undefined) as a primary variable in AFA selection. Undefined scope + fixed fee = risk transferred to the firm and priced accordingly. The skill names this explicitly rather than designing an AFA that will fail.

**Mode 5 for scope disputes.** Added after the initial 4-mode design when testing showed that "the firm says this is out of scope" is a distinct workflow from health check or renegotiation. The mode produces an assessment that either validates or challenges the claim with reference to the engagement terms.

**Jurisdiction adaptation.** Rate benchmarks default to UK/GBP. US (AmLaw data) and Australian benchmarks available — stated in pre-flight or within input.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| Panel design | panel-design-selection (Skill 2) |
| Firm selection | rfp-pitch-management (Skill 3) |
| **Fee arrangements** | **fee-arrangement-structuring (Skill 4) ← this skill** |
| Matter instruction | matter-allocation-instruction (Skill 5) |
| Invoice review | invoice-review-compliance (Skill 6) |
| Performance management | performance-scorecard (Skill 7) |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| engagement-terms-billing-guidelines (Skill 1) | OCG sets AFA policy preference; this skill designs the specific arrangement for a matter. |
| rfp-pitch-management (Skill 3) | Competitive fee proposals from the RFP process anchor the negotiation position. |
| matter-allocation-instruction (Skill 5) | Agreed fee arrangement is referenced in the matter instruction template. |
| invoice-review-compliance (Skill 6) | AFA type determines invoice structure and compliance rules. Fixed fee invoices reviewed differently from hourly. |
| budget-and-fee-manager (LPM Core) | AFA structure agreed here → phase-based budget built and WIP monitored in budget-and-fee-manager. |
| scope-change-controller (LPM Core) | Scope drift identified in Mode 4 should be logged and controlled in scope-change-controller. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `fee-arrangement-structuring/SKILL.md` — skill instructions
- `fee-arrangement-structuring-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
