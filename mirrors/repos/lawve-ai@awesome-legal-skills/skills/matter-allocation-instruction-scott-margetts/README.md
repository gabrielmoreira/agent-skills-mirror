# matter-allocation-instruction

**OCM Skills Plugin** — Skill 5 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Executes matter allocation and firm engagement from firm selection through to a live, properly-instructed matter. Match the right firm to a new matter using the right-sourcing framework. Produce a complete matter instruction ready to send. Generate the onboarding checklist that closes conflict clearance, engagement letter, OCG, and e-billing gates. Audit an existing instruction for gaps with a remediation note ready to send.

This is the execution layer for a matter that has been sourced. Panel-design-selection (Skill 2) defines which firms are on the panel. RFP-pitch-management (Skill 3) selects firms through a competitive process. This skill instructs the selected firm and closes the onboarding gates.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Matter Allocation | "Which firm should handle this" / "Allocate this matter" / "Who should we use" | Matter Allocation Recommendation + GC/Budget Holder Note |
| 2 — Instruction Template | "Instruct the firm" / "Write the instruction" / "Draft the instruction letter" | Matter Instruction (email-ready) + Internal Allocation Record |
| 3 — Firm Onboarding | "Onboard the firm" / "Set up the matter" / "What do we need before they start" | Matter Onboarding Checklist + Firm Onboarding Confirmation Request |
| 4 — Instruction Audit | "Is our instruction complete" / "Review the instruction" / "What's missing" | Instruction Gap Assessment + Instruction Remediation Note |

---

## Key design decisions

**Conflict clearance as a hard gate.** Mode 3 Phase 1 gates are sequenced to block work commencement. Mode 2 includes conflict clearance as a standalone clause. Mode 4 flags its absence as critical. Not a reminder — a structural control.

**E-billing setup at instruction.** Treated as a named onboarding item with a 2-business-day deadline and explicit ownership. The pattern of invoices arriving in PDF without UTBMS codes because no one told the firm's billing contact the format requirement is a process failure at instruction, not at invoice review.

**Right-sourcing logic in Mode 1.** The allocation recommendation scores against seven right-sourcing factors. The default BigLaw bias — allocating to Tier A because that's where the relationship sits — is named as a common failure mode. The test: does this matter require skills or scale that a Tier B firm demonstrably cannot provide?

**Email-ready instruction.** Mode 2 output is structured to paste directly into an email to the supervising partner. Instructions go out by email. A skill output that requires conversion before use creates friction that reduces adoption.

**Reporting cadence at instruction.** Mode 2 includes reporting cadence, format, and first report date as named fields. This is when the client has leverage.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| Panel design | panel-design-selection (Skill 2) |
| Firm selection | rfp-pitch-management (Skill 3) |
| Fee arrangements | fee-arrangement-structuring (Skill 4) |
| **Matter instruction** | **matter-allocation-instruction (Skill 5) ← this skill** |
| Invoice review | invoice-review-compliance (Skill 6) |
| Performance management | performance-scorecard (Skill 7) |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| panel-design-selection (Skill 2) | Defines which firms are on the panel and at what tier. Mode 1 allocates within that structure. |
| rfp-pitch-management (Skill 3) | Firms appointed via RFP are first instructed via this skill. |
| fee-arrangement-structuring (Skill 4) | Agreed AFA is referenced in the instruction template. |
| engagement-terms-billing-guidelines (Skill 1) | OCGs are a prerequisite confirmed at onboarding. Mode 3 closes the acknowledgment gate. |
| invoice-review-compliance (Skill 6) | Instruction gaps (no UTBMS requirement, no staffing disclosure) are the upstream cause of invoice compliance failures. |
| matter-intake-scoping (LPM Core) | The matter instruction is the client-side equivalent of the LPM intake — same information, different audience. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `matter-allocation-instruction/SKILL.md` — skill instructions
- `matter-allocation-instruction-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
