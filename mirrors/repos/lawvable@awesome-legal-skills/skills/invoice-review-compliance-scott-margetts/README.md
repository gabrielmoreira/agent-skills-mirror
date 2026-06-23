# invoice-review-compliance

**OCM Skills Plugin** — Skill 6 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Reviews outside counsel invoices against billing guidelines, flags non-compliant entries by category, and produces the documents needed to approve, reduce, reject, and communicate those decisions. Covers the full invoice compliance workflow: line-item review through to formal firm escalation.

Works with or without an e-billing platform. Where an e-billing system is in place, LEDES format and UTBMS coding are hard gates. Where there is no e-billing system, invoice submission by email is the channel and UTBMS coding is a best-efforts flag.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Invoice Line-Item Review | "Review this invoice" / "Flag the billing issues" / "Check against our guidelines" | Line-Item Review Report + Invoice Approval Note |
| 2 — Invoice Rejection Communication | "Write the rejection letter" / "Communicate the reductions to the firm" | Invoice Rejection Letter + Internal Rejection Record |
| 3 — Review Process Setup | "Build an invoice checklist" / "How should we review invoices?" / "Set up our review process" | Invoice Review Checklist + Reviewer Guidance Note |
| 4 — Compliance Pattern Analysis | "The firm keeps doing this" / "Recurring violations" / "Escalate the billing issue" | Compliance Pattern Summary + Formal Non-Compliance Notice |

Mode 5 — Conversation Guide: a structured guide for less mature teams preparing for a billing conversation with outside counsel, produced when the team needs to raise compliance issues but lacks the process maturity for a formal non-compliance notice.

---

## Key design decisions

**Rule vs. guideline distinction.** Four action values — REJECT, REDUCE, APPROVE WITH NOTE, APPROVE — map to the rule/guideline distinction. REJECT for hard OCG breaches (prohibited fees, rate violations, block billing). REDUCE for discretionary judgments (excessive time, description quality). The distinction makes review decisions defensible.

**Seven-phase review checklist.** Mode 3 sequences review in the order a reviewer would actually work: mechanical checks → line-item review → prohibited fees → expenses → UTBMS coding → internal comms threshold → budget. REJECT-heavy phases front-loaded.

**Upstream cause documented.** Domain knowledge explicitly connects billing compliance failures to instruction quality. Mode 4 pattern analysis prompts: is this a firm failing or an instruction gap? Cross-reference to matter-allocation-instruction Mode 4 (Instruction Audit).

**PDF invoice ingestion.** Mode 1 accepts uploaded PDF invoices. The skill extracts line items and maps them against billing guidelines without requiring the user to reformat.

---

## Violation categories

| Category | Action | Examples |
|----------|--------|---------|
| Block billing | REJECT | Multiple tasks with different UTBMS codes in a single entry |
| Prohibited fees | REJECT | Invoice prep, conflict checks, training, ramp-up, clerical work |
| Rate violation | REJECT | Unapproved rate, unapproved timekeeper, volume discount not applied |
| Staffing violation | REJECT or REDUCE | Multiple timekeepers at event without approval, daily hours cap exceeded |
| Description violation | REDUCE or APPROVE WITH NOTE | "Services rendered", "Document review" — no specific task described |
| Internal comms excess | REDUCE | Internal firm communications >10% of invoice total |
| Expense violation | REJECT or REDUCE | Overhead expenses, first-class travel, expense markups |
| Late submission | REDUCE | 60+ days late: 20% reduction; 90+ days: possible rejection |

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| Panel design | panel-design-selection (Skill 2) |
| Firm selection | rfp-pitch-management (Skill 3) |
| Fee arrangements | fee-arrangement-structuring (Skill 4) |
| Matter instruction | matter-allocation-instruction (Skill 5) |
| **Invoice review** | **invoice-review-compliance (Skill 6) ← this skill** |
| Performance management | performance-scorecard (Skill 7) |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| engagement-terms-billing-guidelines (Skill 1) | The OCG defines the rules this skill enforces. Mode 3 checklist reflects Skill 1 output. |
| fee-arrangement-structuring (Skill 4) | Fee arrangement type determines invoice structure. Fixed fee invoices reviewed differently from hourly. |
| matter-allocation-instruction (Skill 5) | Instruction gaps are the upstream cause of most compliance failures. Mode 4 pattern analysis prompts the instruction gap check. |
| performance-scorecard (Skill 7) | Invoice compliance data feeds the billing adherence component of the performance scorecard. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `invoice-review-compliance/SKILL.md` — skill instructions
- `invoice-review-compliance-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
