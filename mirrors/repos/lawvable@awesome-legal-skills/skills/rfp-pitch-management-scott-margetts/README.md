# rfp-pitch-management

**OCM Skills Plugin** — Skill 3 of 8
**Status:** Complete — Phase 1 and Phase 2 tested

---

## What this skill does

Runs structured RFP processes for selecting outside counsel — from drafting the initial document through evaluating firm responses and producing a defensible selection recommendation for GC sign-off.

An average law firm spends 47 hours on an RFP response. That cost gets built into the price of legal services. Poorly structured RFPs produce responses that are incomparable and select by default for the most polished proposal, not the best firm. This skill encodes the methodology for running processes that produce genuine comparability and defensible decisions.

---

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1 — Draft RFP | "Draft an RFP" / "Write a legal RFP" / "We need to go to market" | RFP Document + Evaluation Criteria Framework |
| 2 — Evaluate Responses | "Evaluate firm responses" / "Score the RFP submissions" / "Compare the proposals" | Scored Evaluation Matrix + Evaluation Summary Note |
| 3 — Shortlist and Selection Brief | "Which firms should we shortlist" / "Selection recommendation" / "We want to appoint [firm]" | Selection Brief + Feedback Letters (successful and unsuccessful) |
| 4 — RFP Process Design | "How do we run a panel RFP" / "Design the RFP process" / "How do we weight the criteria" | RFP Process Plan + Evaluation Criteria Framework |

---

## Key design decisions

**Named firms in internal documents.** Evaluation documents (Mode 2 scored matrix, Mode 3 selection brief) use actual firm names — these are internal governance records. Feedback letters (Mode 3) use [Firm] placeholder in the template, populated at send time.

**Pricing structure requirements.** RFP templates include structured pricing sections requiring AFA options, AI discount disclosure, and rate transparency. 83% of proposals on PERSUIT now use value-based pricing. An RFP that doesn't address pricing structure leaves money on the table.

**OCG as appointment condition.** Mode 1 includes OCG acknowledgment as a condition of appointment. If OCGs don't exist, the skill flags that engagement-terms-billing-guidelines (Skill 1) should run in parallel so the document is ready when appointment letters go out.

**Defensible process documentation.** Every mode produces documentation sufficient to withstand a GC challenge on process fairness. Evaluation criteria are defined before responses are received. Scoring is anchored to descriptive rubrics, not subjective impressions.

---

## Placement in the OCM lifecycle

| Stage | Skill |
|-------|-------|
| Billing rules | engagement-terms-billing-guidelines (Skill 1) |
| Panel design | panel-design-selection (Skill 2) |
| **Firm selection** | **rfp-pitch-management (Skill 3) ← this skill** |
| Fee arrangements | fee-arrangement-structuring (Skill 4) |
| Matter instruction | matter-allocation-instruction (Skill 5) |
| Invoice review | invoice-review-compliance (Skill 6) |
| Performance management | performance-scorecard (Skill 7) |
| Panel review | panel-review-rationalisation (Skill 8) |

---

## Cross-skill connections

| Skill | Connection |
|-------|-----------|
| panel-design-selection (Skill 2) | Selection criteria matrix from panel design feeds RFP evaluation criteria and weightings. |
| engagement-terms-billing-guidelines (Skill 1) | Firms appointed through RFP must receive and sign OCGs before work begins. |
| fee-arrangement-structuring (Skill 4) | Commercial terms agreed in RFP negotiations become the baseline for matter-level fee arrangement. |
| matter-allocation-instruction (Skill 5) | Firms appointed via RFP get instructed via Skill 5 on their first matter. |
| performance-scorecard (Skill 7) | RFP selection criteria should become ongoing evaluation criteria. |
| panel-review-rationalisation (Skill 8) | Panel review can trigger a refresh RFP. Mode 4 of Skill 8 produces the Panel Refresh Brief that feeds into this skill. |

---

## Testing

Phase 1 and Phase 2 test prompts and assertion sets are in the build log.

---

## Files

- `rfp-pitch-management/SKILL.md` — skill instructions
- `rfp-pitch-management-README.md` — this document

---

## Licence

Apache 2.0 — LegalOps Consulting Limited
