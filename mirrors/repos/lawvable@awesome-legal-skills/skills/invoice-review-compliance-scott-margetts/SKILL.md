---
name: invoice-review-compliance
description: "Invoice review, non-compliance flagging, rejection communication, billing trend analysis, and conversation preparation for in-house legal ops teams managing outside counsel. Review invoices against billing guidelines; flag block billing, prohibited fees, rate violations, staffing violations, late submission. Produce line-item review report and approval note. Draft rejection letter to outside counsel. Build invoice review checklist. Analyse billing trends across multiple invoices and produce a structured conversation guide for the relationship review. Identify systemic patterns and produce formal non-compliance notice. Trigger on: 'review this invoice', 'flag billing issues', 'check invoice against guidelines', 'write the rejection letter', 'build an invoice checklist', 'block billing', 'UTBMS', 'billing non-compliance', 'analyse our invoices', 'billing trends', 'prep for the billing conversation', 'relationship review', 'the firm keeps doing this', 'escalate'."
---

# invoice-review-compliance

## Description

Invoice review, non-compliance flagging, rejection communication, and billing compliance tracking for in-house legal ops teams managing outside counsel. Review an invoice against billing guidelines, flag violations by category, and produce a line-item review report with an approval note for the payment team. Draft a formal rejection letter to the firm for flagged entries. Build an invoice review checklist calibrated to your billing guidelines. Identify recurring compliance patterns across invoices and produce a formal non-compliance notice for the firm. Trigger on: 'review this invoice', 'check this against our guidelines', 'flag the billing issues', 'write the rejection letter', 'communicate the reductions', 'build an invoice checklist', 'our review process', 'block billing', 'UTBMS', 'LEDES', 'billing non-compliance', 'recurring violations', 'the firm keeps doing this', 'escalate the billing issue'.

---

## What This Skill Does

Executes invoice compliance review from line-item flagging through to formal firm communication. Encodes the methodology for reviewing invoices against billing guidelines, categorising violations, producing defensible approval decisions, and escalating systemic non-compliance.

**This skill does NOT:**
- Draft the billing guidelines or OCGs that define what is and is not compliant — use **engagement-terms-billing-guidelines** (OCM Skill 1)
- Design or negotiate the fee arrangement that governs the invoice — use **fee-arrangement-structuring** (OCM Skill 4)
- Produce the original matter instruction that sets reporting and invoicing expectations — use **matter-allocation-instruction** (OCM Skill 5)
- Run firm performance scorecards or QBRs — use **performance-scorecard** (OCM Skill 7)

**Cross-skill connection:** Instruction gaps identified by matter-allocation-instruction (missing UTBMS requirement, no staffing disclosure, no late submission penalty) are the upstream cause of invoice compliance failures caught by this skill. The review checklist in Mode 3 should reflect what the engagement terms in OCM Skill 1 require.

---

## Pre-flight — Confirm and Fill

Gather what you have. Fill in what's known. Use placeholders for the rest. Proceed immediately.

**Billing guidelines:** Search project knowledge and Google Drive for outside counsel guidelines, billing guidelines, or OCGs before running any mode. An organisation has one set of billing guidelines — use those as the compliance reference throughout. If no guidelines are found in project knowledge or Google Drive, apply best-practice defaults and label them as defaults explicitly.

**E-billing system:** Some organisations use an e-billing platform (Brightflag, SimpleLegal, Legal Tracker, CounselLink); others manage invoice review manually by email and spreadsheet. The skill works for both. Where an e-billing system is in place, LEDES format and UTBMS coding are hard gates. Where there is no e-billing system, invoice submission by email is the channel and UTBMS coding is a best-efforts flag rather than a hard rejection trigger.

| Field | Value |
|-------|-------|
| Company / Legal department | [Company] |
| Firm name | [Firm] |
| Matter name / number | [Matter] |
| Invoice number | [Invoice #] |
| Invoice period | [Date range] |
| Invoice amount (total) | [Amount + currency] |
| E-billing system | [Platform name] / None — manual review |
| Review type | Single invoice / Systemic pattern / Process setup |

**Routing:**
- Reviewing a specific invoice for compliance issues → **Mode 1: Invoice Line-Item Review**
- Writing a rejection or reduction letter to the firm → **Mode 2: Invoice Rejection Communication**
- Building an invoice review checklist or process → **Mode 3: Review Process Setup**
- Addressing recurring non-compliance across multiple invoices → **Mode 4: Compliance Pattern Analysis**
- "Review this invoice" / "Check this against our guidelines" / "Flag the billing issues" / "What's wrong with this invoice?" → **Mode 1**
- "Write the rejection letter" / "Communicate the reductions" / "Tell the firm we're rejecting [entry]" → **Mode 2**
- "Build us an invoice checklist" / "How should we review invoices?" / "Set up our review process" → **Mode 3**
- "The firm keeps doing this" / "Recurring block billing" / "Escalate the billing issue" / "Non-compliance pattern" → **Mode 4**
- "Analyse our invoices" / "What trends are we seeing?" / "Prep me for the billing conversation" / "I want to talk to the firm about their billing" / "Relationship review" / "What should I raise with the partner?" → **Mode 5**

All documents produced as .docx files unless the user requests otherwise. Include Company Name, Firm Name, Matter Name, and date in every document header.

---

## Mode 1: Invoice Line-Item Review

**Produce a Line-Item Review Report and an Invoice Approval Note immediately — start with the Line-Item Review Report table. Do not produce narrative analysis, a list of observations, or conversational commentary before producing the documents. Do not ask clarifying questions before producing the documents. Do not end the response with a question. A user asking "review this invoice", "check this against our guidelines", "what's wrong with this invoice", "flag the billing issues", or "should we approve this?" is requesting a Line-Item Review Report and an Invoice Approval Note — produce both documents immediately using the templates below. Analysis belongs inside the Issue Detail column of the table and the Recommendation field of the Approval Note — not before the documents. Build from what the user has provided. If invoice data is incomplete, use placeholders and flag what is missing after the documents. Do not withhold the Invoice Approval Note pending additional information — produce it with placeholders where data is missing. Use [Company] in all document headers unless the company name has been explicitly stated in the user's input in this session — do not substitute names from session context. The documents are the response.**

### Input

Invoice details — entries, timekeepers, rates, hours, amounts, descriptions, and dates. Invoice may be provided as an attached PDF — if so, extract the line items from it directly and apply the review without asking the user to re-describe the entries. Billing guidelines are sourced from project knowledge or Google Drive — reference them directly when assessing each entry. Where no guidelines are available, apply best-practice defaults. Minimum viable input is a description of the invoice or specific entries.

### How to run this mode

1. Produce the Line-Item Review Report — populate the table with each flagged entry, the violation category, the specific issue, the amount at risk, and the action recommendation.
2. Produce the Invoice Approval Note — summarise the findings for the payment team with a clear approve / partial approve / reject recommendation.
3. Observations and follow-up questions come after both documents. Do not end the response with a question.

### Line-Item Review Report template

---
**[Company] — Invoice Line-Item Review Report**
**Firm:** [Firm]
**Matter:** [Matter name / number]
**Invoice number:** [Invoice #]
**Invoice period:** [Date range]
**Invoice amount (submitted):** [Amount]
**Review date:** [Date]
**Reviewed by:** [Legal Ops / Reviewer name]

**Review summary:**
[2–3 sentences. Total entries reviewed. Number flagged. Total amount at issue. Overall compliance assessment.]

**Flagged entries:**

| # | Entry ref | Timekeeper | Hours | Amount | Violation category | Issue detail | Action |
|---|-----------|------------|-------|--------|--------------------|--------------|--------|
| 1 | [Date / line ref] | [Name / level] | [Hours] | [Amount] | [Block billing / Prohibited fee / Rate violation / Staffing / Description / Late submission / Expense] | [Specific issue — what the entry says and why it violates the guideline] | [REJECT / REDUCE to [amount] / APPROVE WITH NOTE] |
| 2 | | | | | | | |

**Entries approved without issue:** [Count] entries totalling [amount] — no violations identified.

**Violation category key:**
- REJECT: Clear OCG breach — prohibited activity, unapproved rate, duplicate entry. No payment.
- REDUCE: Excessive time, questionable description, over-staffing, partially prohibited. Apply reduction stated.
- APPROVE WITH NOTE: Minor issue worth flagging but within acceptable range. Note recorded.

**Total amount rejected / reduced:** [Amount]
**Recommended approval amount:** [Submitted amount] minus [rejected / reduced amount] = [Recommended payment amount]

---

### Invoice Approval Note template

---
**[Company] — Invoice Approval Note**
**To:** [Accounts Payable / Finance contact]
**From:** [Legal Ops]
**Firm:** [Firm]
**Invoice number:** [Invoice #]
**Matter:** [Matter]
**Submitted amount:** [Amount]
**Date:** [Date]

**Recommendation:** [APPROVE IN FULL / PARTIAL APPROVAL — see below / REJECT — see below]

**Payment instruction:**
[Approve: "Approve for payment in full: [amount]." Partial: "Approve for payment at [amount], being the submitted amount of [amount] less [amount] in rejected / reduced entries. Do not pay line items [reference numbers] pending firm resubmission." Reject: "Do not approve for payment. Full invoice returned to firm for resubmission. See rejection communication [reference]."]

**Reason for reduction / rejection (if applicable):**
[2–4 sentences summarising the primary violations. Reference the Line-Item Review Report for detail.]

**Action required from firm (if applicable):**
[What the firm must do — resubmit specific entries, provide supporting documentation, acknowledge OCG breach.]

**Appeal deadline:** [Date — typically 30 days from rejection notice]

---

### Violation reference framework — apply inside templates above

**Block billing (most common violation):** Multiple tasks aggregated into a single time entry where the tasks fit different UTBMS codes. Standard response: reject and require resubmission with entries separated. Zscaler benchmark: resubmitted block-billed entries subject to 15% penalty, or 10% non-appealable reduction at client's election.

**Prohibited fees (always REJECT):** Invoice/budget/accrual preparation; conflict checks; engagement letter preparation; training junior attorneys; ramp-up/read-in time; clerical/secretarial work; internal firm administrative activities; basic legal research (within firm's expertise area without pre-approval); CLE/professional development.

**Rate violations (always REJECT):** Any rate not pre-approved in writing. Unapproved timekeepers. Rates applied to work performed before rate approval. Volume discounts not applied as agreed.

**Staffing violations (REJECT or REDUCE depending on OCG):** More attorneys at a matter event than approved; summer associates/clerks billed without approval; contract attorneys billed without approval; excessive daily hours per timekeeper (benchmark: 8–10 hours maximum).

**Description violations (REDUCE or APPROVE WITH NOTE):** Entries that say "For services rendered", "Document review", "Research" with no further detail. For communications: must identify parties and general subject. Target standard: each entry should identify the specific task performed.

**Internal communications threshold:** Entries for internal firm communications (conferences, memos, emails between firm staff) exceeding 10% of total invoice amount should be flagged. Entries for internal comms on routine matters are typically REDUCE.

**Late submission penalties (graduated):** Invoices submitted 60+ days after work performed: 20% reduction. 90+ days: may reject entirely. Apply the client's OCG late submission terms if stated; use this benchmark if not.

**Expense violations:** No markups on third-party costs (actual cost only); first/business class travel without approval; local travel within 50 miles of office; communication charges (phone, fax, internet); photocopying/scanning; online research subscriptions; staff overtime meals. Pre-approval required for third-party vendors above threshold.

---

## Mode 2: Invoice Rejection Communication

**Produce an Invoice Rejection Letter and an Internal Rejection Record immediately — start with the Invoice Rejection Letter. Do not produce analysis, commentary, or a list of issues before producing the documents. Do not ask for more information before producing the documents. Do not end with a question. A user asking "write the rejection letter", "communicate the reductions to the firm", "tell the firm we're rejecting [entry]", or "draft the firm communication for the flagged items" is requesting an Invoice Rejection Letter and an Internal Rejection Record — produce both documents immediately using the templates below. If rejected line items are not fully detailed in the user's input, use placeholders for specific entries and flag what is missing after the documents. Do not withhold the Internal Rejection Record pending further information. Use [Company] in all document headers and letterheads unless the company name has been explicitly stated in the user's input in this session — do not substitute names from session context or account memory. Use [Firm] throughout the letter if the firm's name has not been provided in this session's input. The documents are the response.**

### Input

Flagged invoice entries with violation categories and actions — typically the output of Mode 1, or a description of the specific entries being rejected. Minimum viable input is a description of the issue and the invoice reference.

### How to run this mode

1. Produce the Invoice Rejection Letter — addressed to the firm, setting out the rejected / reduced entries, the reason for each, the adjusted payment amount, and the instructions for resubmission or appeal.
2. Produce the Internal Rejection Record — the internal log entry for this rejection, for tracking and future pattern analysis.
3. Observations come after both documents.

### Invoice Rejection Letter template

---
**[Company Legal Department]**
**[Date]**

**[Relationship Partner name / Billing Coordinator name]**
**[Firm]**

**Re: Invoice [Invoice #] — Matter: [Matter name / number] — Billing Adjustment Notice**

Dear [Name / "Billing Team"],

We have completed our review of Invoice [Invoice #] dated [date] for matter [matter name / number]. The invoice has been partially approved / rejected for the reasons set out below.

**Payment approved:**
We will process payment of [approved amount] against this invoice. This represents the submitted amount of [submitted amount] less the adjustments detailed below.

**Entries rejected / reduced:**

| Entry ref | Timekeeper | Hours billed | Amount billed | Reason for rejection / reduction | Approved amount |
|-----------|------------|-------------|---------------|----------------------------------|-----------------|
| [Entry ref] | [Name] | [Hours] | [Amount] | [Reason — reference specific OCG provision where possible] | [Nil / Reduced amount] |

**Total adjusted amount:** [Amount rejected/reduced]
**Approved payment:** [Amount]

**Financial summary:**

| | Amount |
|---|---|
| Invoice amount submitted | [Submitted amount] |
| [Entry ref] — [violation type] — hard rejected | ([Amount]) |
| [Entry ref] — withheld pending resubmission | ([Amount]) |
| [Entry ref] — rate correction pending | (TBC) |
| **Approved for immediate payment** | **[Approved amount]** |

**Required action:**
[Resubmit: "Please resubmit the above entries with corrections within [X] business days. Corrected entries must carry the original invoice number with a revised date. Resubmitted entries remain subject to review." OR Acknowledge: "No resubmission is required. Please acknowledge receipt and confirm compliance with [specific rule] on all future invoices for this matter."]

**Appeals:**
If you wish to appeal any of the above adjustments, please submit your appeal in writing within [30] days of this notice, referencing the entry number and the basis for your appeal. Adjustments made on the basis of [prohibited fees / rate violations — as applicable] are non-appealable.

We remain committed to a productive working relationship. These adjustments are made in accordance with our billing guidelines, a copy of which [was provided at matter opening / is attached for reference].

Regards,

[Name]
[Legal Operations / General Counsel's Office]
[Company]

---

### Internal Rejection Record template

---
**[Company] — Invoice Rejection Record**
**Date:** [Date]
**Firm:** [Firm name]
**Matter:** [Matter name / number]
**Invoice #:** [Invoice #]
**Invoice period:** [Date range]
**Submitted amount:** [Amount]
**Approved amount:** [Amount]
**Total rejected / reduced:** [Amount]

**Violations recorded:**
| # | Violation category | Entry ref | Amount at issue | Action taken | Resubmission required |
|---|--------------------|-----------|----------------|--------------|-----------------------|
| 1 | [Category] | [Ref] | [Amount] | [REJECT / REDUCE] | [Yes / No] |

**Notes for pattern tracking:**
[1–2 sentences. First occurrence / repeat violation? Cross-reference to any previous rejection records for this firm.]

**Follow-up required:** [Yes — by [date] / No]
**Escalation trigger reached:** [Yes — proceed to Mode 4 / No]

---

## Mode 3: Review Process Setup

**Produce an Invoice Review Checklist and a Reviewer Guidance Note immediately — start with the Invoice Review Checklist. Do not produce analysis, discussion of review approaches, or a general overview of invoice review before producing the documents. Do not ask clarifying questions before producing the documents. Do not end with a question. A user asking "build us an invoice checklist", "how should we review invoices", "set up our invoice review process", "what should we check on invoices", or "we need a systematic approach to bill review" is requesting an Invoice Review Checklist and a Reviewer Guidance Note — produce both documents immediately using the templates below. Search project knowledge and Google Drive for billing guidelines or OCGs before building the checklist — calibrate the checklist to those guidelines. If no guidelines are found, build from best-practice defaults and label those defaults explicitly. Use [Company] in all document headers unless the company name has been explicitly stated in the user's input in this session — do not substitute names from session context or account memory. Do not withhold the Reviewer Guidance Note pending further information. The documents are the response.**

### Input

Billing guidelines sourced from project knowledge or Google Drive. E-billing system status (platform name, or none — manual review). Team maturity — how formal and detailed the checklist needs to be. Minimum viable input is the intent to build a review process. If no e-billing system is in place, Phase 1 and Phase 5 of the checklist adapt accordingly — see checklist template notes.

### How to run this mode

1. Produce the Invoice Review Checklist — ordered by review sequence, calibrated to the user's stated guidelines (or best-practice defaults where guidelines are not specified).
2. Produce the Reviewer Guidance Note — how to use the checklist, escalation thresholds, and what to do when a determination is unclear.
3. Observations come after both documents. Do not end the response with a question.

### Invoice Review Checklist template

---
**[Company] — Invoice Review Checklist**
**Version:** [1.0]
**Applies to:** All outside counsel invoices
**Date issued:** [Date]
**Issued by:** [Legal Operations]

**How to use:** Work through each check in order. Record the outcome for each flagged entry in your review record. Escalation thresholds and guidance are in the attached Reviewer Guidance Note.

---

**Phase 1 — Mechanical checks (do these first; failures here are always REJECT)**

*If e-billing system in place:*
- [ ] Invoice submitted via [platform name] in LEDES format
- [ ] LEDES file parses without errors — reject and return if file is malformed

*If no e-billing system (manual review):*
- [ ] Invoice received via agreed channel (email to [address] / post)
- [ ] Invoice in agreed format (PDF / Word — as specified in billing guidelines or engagement letter)

*Apply in all cases:*
- [ ] Invoice is for the correct legal entity ([Company legal entity name])
- [ ] Correct matter number on invoice
- [ ] One invoice per matter per billing period — confirm no duplicate invoices for this matter / period
- [ ] Invoice submitted within [30 / 60] days of work performed — flag any entries older than [X] days
- [ ] All rates on invoice match pre-approved rate schedule — flag any unapproved rates or timekeepers
- [ ] Currency correct — [GBP / USD / AUD / other] as agreed

**Phase 2 — Line-item review (apply to every entry)**

- [ ] Each entry describes a specific task — reject entries that say only "document review", "research", "meeting", "services rendered", or equivalent
- [ ] Each communication entry identifies parties and subject matter
- [ ] No block billing — each entry covers a single task fitting one UTBMS task code; reject combined entries
- [ ] Time recorded to nearest 0.1 hour (6-minute increments)
- [ ] No single timekeeper has billed more than [8 / 10] hours on any given day — flag any that do
- [ ] No more than [agreed number] timekeepers on any single matter event (deposition, hearing, meeting) without prior approval

**Phase 3 — Prohibited fees check (flag and REJECT)**

- [ ] No billing for: invoice/accrual/budget preparation
- [ ] No billing for: conflict check or engagement letter preparation
- [ ] No billing for: training junior attorneys, CLE, or professional development
- [ ] No billing for: ramp-up or read-in time caused by firm staffing changes
- [ ] No billing for: clerical, secretarial, or administrative tasks
- [ ] No billing for: basic legal research (within firm's area of expertise) without prior approval
- [ ] No unapproved summer associates, law clerks, or contract attorneys

**Phase 4 — Expenses check**

- [ ] All expenses at actual cost — no markups
- [ ] No overhead expenses (phone, fax, internet, postage, photocopying, office supplies)
- [ ] No online research subscription charges
- [ ] Travel at coach / economy class — flag any first/business class without approval
- [ ] No local travel within [50] miles of office without approval
- [ ] Receipts attached for all expenses above [£25 / $25] threshold
- [ ] Third-party vendor invoices attached with original; pre-approval confirmed

**Phase 5 — UTBMS coding check**

*If e-billing system in place (hard gate):*
- [ ] All entries carry a UTBMS task code — reject entries without a code
- [ ] Task codes match the work described — flag mismatches (e.g., litigation codes on transactional matter)
- [ ] Activity codes present where required by billing guidelines
- [ ] Expense codes applied to expense entries

*If no e-billing system (best-efforts flag):*
- [ ] Note any entries where UTBMS codes are absent or clearly misapplied — flag to firm as a recommendation, not a hard rejection, unless billing guidelines specifically require coding
- [ ] If the organisation plans to move to an e-billing system, consistent coding from now builds the data set needed for future benchmarking

**Phase 6 — Internal communications threshold**

- [ ] Calculate internal firm communication entries as a percentage of total invoice — flag if above 10%

**Phase 7 — Budget check**

- [ ] Confirm cumulative spend on this matter against approved budget
- [ ] If cumulative spend is at or above [80%] of approved budget, flag for GC notification
- [ ] If invoice would take spend over approved budget, do not approve without GC authorisation

---

### Reviewer Guidance Note template

---
**[Company] — Invoice Reviewer Guidance Note**
**Date:** [Date]

**How to use the checklist**

Work through all seven phases in order for each invoice. Record each finding in the Invoice Review Record (see below). Produce a Line-Item Review Report (using invoice-review-compliance Mode 1) for any invoice with flagged items before approving or rejecting.

**Action levels**

- **REJECT:** Clear OCG breach — prohibited activity, unapproved rate, duplicate entry. Do not pay. Return to firm for correction. Always document the specific OCG provision breached.
- **REDUCE:** Excessive time, questionable description, over-staffing, partially prohibited activity. Approve a reduced amount. Document the basis for the reduction.
- **APPROVE WITH NOTE:** Minor issue within acceptable range. Approve but log for pattern tracking.
- **APPROVE:** No issues. Approve.

**Escalation thresholds**

- Any single REJECT or REDUCE exceeding [£5,000 / $5,000] requires GC review before the rejection letter is sent.
- Three or more violations of the same type across a single invoice: escalate to Mode 4 (Compliance Pattern Analysis) before processing payment.
- Any rate violation: escalate immediately — do not process invoice until rate issue is resolved.
- Invoice submitted more than 90 days after work performed: escalate for GC decision on whether to accept.

**When in doubt**

If an entry is unclear — the description is ambiguous, or you are not sure whether the activity is prohibited — contact the supervising attorney or request clarification from the firm before making a determination. Do not approve uncertain entries by default.

**Tracking**

Maintain a review record for each invoice reviewed. Record: invoice number, firm, matter, submitted amount, approved amount, violations found, action taken. Review records feed the compliance pattern analysis in Mode 4.

---

## Mode 4: Compliance Pattern Analysis

**Produce a Compliance Pattern Summary and a Formal Non-Compliance Notice immediately — start with the Compliance Pattern Summary. Do not produce conversational analysis, a list of observations, or discussion of how to address the problem before producing the documents. Do not ask clarifying questions before producing the documents. Do not end with a question. A user asking "the firm keeps doing this", "recurring block billing", "we've flagged this multiple times", "escalate the billing issue", "non-compliance pattern", or "how do we address this systemically" is requesting a Compliance Pattern Summary and a Formal Non-Compliance Notice — produce both documents immediately using the templates below. The Compliance Pattern Summary may use the firm's actual name (internal document). The Formal Non-Compliance Notice uses [Firm] as a deliberate placeholder throughout — including in the salutation, body, and required action section — even if the firm's name has been provided in the user's input. The [Firm] placeholder signals that the user should confirm the addressee, partner name, and OCG clause reference before sending. Do not populate the firm's actual name into the external Notice under any circumstances. Use [Company] in all document headers unless the company name has been explicitly stated in the user's input in this session — do not substitute names from session context or account memory. Do not withhold the Formal Non-Compliance Notice pending additional data — produce it with placeholders where data is missing. The documents are the response.**

### Input

Description of the recurring pattern — violation type, frequency, number of invoices affected, total amount at issue, and any previous communications. Minimum viable input is a description of the pattern and the firm. Full invoice history produces a stronger analysis but is not required.

### How to run this mode

1. Produce the Compliance Pattern Summary — the internal record of the pattern, for the legal ops file and GC visibility.
2. Produce the Formal Non-Compliance Notice — the external communication to the firm, escalating beyond per-invoice rejection to a formal notice requiring acknowledgment and a remediation commitment.
3. Observations come after both documents. Do not end the response with a question.

### Compliance Pattern Summary template

---
**[Company] — Outside Counsel Compliance Pattern Summary**
**Firm:** [Firm name]
**Matter(s) affected:** [List]
**Period:** [Date range]
**Date of this review:** [Date]
**Prepared by:** [Legal Ops]

**Pattern identified:**
[2–3 sentences. Name the violation type(s). State how many invoices and what time period. State the total amount at issue.]

**Compliance record:**

| Invoice # | Invoice period | Violation category | Amount at issue | Previous action taken | Firm response |
|-----------|---------------|-------------------|----------------|----------------------|---------------|
| [Invoice #] | [Period] | [Category] | [Amount] | [Rejected / Reduced / Flagged] | [Resubmitted / No response / Repeated] |

**Cumulative impact:**
- Total invoices reviewed in period: [Count]
- Total invoices with violations: [Count]
- Total amount rejected / reduced to date: [Amount]
- Violation recurrence rate for [violation type]: [%]

**Pattern assessment:**
[3–4 sentences. Is this a single type of violation or multiple? Is it isolated to one timekeeper, one matter, or firm-wide? Has the firm acknowledged previous rejections? Does the pattern suggest a systemic billing practice rather than isolated error?]

**Recommended escalation level:**
[Standard notice / Senior relationship escalation / Contract review trigger]

**Next review date:** [Date — recommend 60 days after notice sent]

---

### Formal Non-Compliance Notice template

---
**[Company Legal Department]**
**[Date]**

**[Senior Partner / Managing Partner / Billing Coordinator — as appropriate]**
**[Firm]**

**Re: Formal Notice — Billing Guideline Non-Compliance — Matter(s): [Matter name(s)]**

Dear [Name],

We are writing to formally notify you of a pattern of non-compliance with [Company]'s billing guidelines on the above matter(s).

**Pattern identified**

Our invoice review has identified repeated instances of [violation type — e.g., block billing / prohibited fee entries / rate violations] across [number] invoices submitted between [date] and [date]. The total amount rejected or reduced on this basis is [amount].

The specific pattern is as follows:
[2–3 sentences describing the pattern — what the entries say, which guideline provision they breach, and why this is a systemic issue rather than an isolated error.]

**Previous communications**

We have raised this issue on [number] previous occasions:
- [Date]: [Brief description of previous rejection or communication]
- [Date]: [Brief description]

[Omit this section if this is the first formal notice.]

**Required action**

We require the following by [date — typically 30 days]:

1. Written acknowledgment of receipt of this notice.
2. Written explanation of the steps [Firm] will take to ensure compliance on future invoices, including any changes to billing practices or internal review processes.
3. Resubmission of the invoices identified in this notice with corrections applied, if not already completed.

**Consequence of continued non-compliance**

If the pattern identified in this notice continues on future invoices, [Company] reserves the right to [apply an automatic reduction to all invoices from [Firm] / initiate a formal billing audit / refer the matter to [firm relationship review] / other — as appropriate to the user's OCG terms].

Our billing guidelines remain in effect for all current and future matters. A copy is attached for your reference.

We value our working relationship with [Firm] and expect this notice will resolve the issue. Please contact [name / Legal Operations] if you would like to discuss.

Regards,

[Name]
[Legal Operations / General Counsel's Office]
[Company]

---

## Mode 5: Invoice Trend Review and Conversation Prep

**Produce an Invoice Trend Summary and a Conversation Guide immediately — start with the Invoice Trend Summary. Do not produce a general discussion of billing patterns, options for how to approach the conversation, or commentary on the relationship before producing the documents. Do not ask clarifying questions before producing the documents. Do not end with a question. A user asking "analyse our invoices", "what trends are we seeing in the billing", "prep me for the billing conversation with the firm", "I want to raise billing concerns at the next relationship review", or "what should I say to the partner about their invoices" is requesting an Invoice Trend Summary and a Conversation Guide — produce both documents immediately using the templates below. Build from whatever invoice data the user provides. If data covers multiple invoices, identify patterns across the set. If data covers a single invoice, identify patterns within it and note that trend analysis strengthens with more data. Do not withhold the Conversation Guide pending additional data — produce it with the available information and note where more data would sharpen specific points. Use [Company] in all document headers unless the company name has been explicitly stated in the user's input in this session — do not substitute names from session context or account memory. The documents are the response.**

### Input

Invoice data across a series of invoices — the more invoices the stronger the trend analysis, but the mode operates from a single invoice upward. The user may also provide context about the relationship, the matter type, the fee arrangement, or what they want to achieve in the conversation.

### How to run this mode

1. Produce the Invoice Trend Summary — structured analysis of billing patterns across the invoices provided, with the data presented in a way the user can refer to during the meeting.
2. Produce the Conversation Guide — a structured script for the relationship review conversation, including an opening, the key points to raise, anticipated firm responses with suggested replies, and a close.
3. Observations come after both documents. Do not end the response with a question.

### Invoice Trend Summary template

---
**[Company] — Invoice Trend Summary**
**Firm:** [Firm name]
**Matter(s):** [Matter name(s) / numbers]
**Period covered:** [Date range]
**Invoices reviewed:** [Count]
**Total spend in period:** [Amount]
**Date prepared:** [Date]
**Prepared by:** [Legal Ops]

**Spend overview:**

| Invoice # | Period | Submitted amount | Approved amount | Rejected / reduced | Notes |
|-----------|--------|-----------------|----------------|-------------------|-------|
| [Invoice #] | [Period] | [Amount] | [Amount] | [Amount] | [Key issue flag] |
| Total | | [Total submitted] | [Total approved] | [Total at issue] | |

**Billing patterns identified:**

| Pattern | Frequency | Amount at issue | Trend |
|---------|-----------|----------------|-------|
| [e.g., Block billing] | [Count — x of y invoices] | [Amount] | [Increasing / Stable / Decreasing] |
| [e.g., Description quality] | [Count] | [Amount] | |
| [e.g., Internal comms volume] | [Count] | [Amount] | |

**Spend profile:**
[3–4 sentences. How is time distributed across timekeepers? Is the right seniority doing the right work? Is one timekeeper driving a disproportionate share of the spend? Are there months or phases where billing spiked?]

**Budget position:**
[2 sentences. Where does cumulative spend sit against budget? Is the trajectory for the remaining matter period within budget?]

**Compliance summary:**
[2–3 sentences. Overall compliance level — is this a firm with occasional issues or persistent problems? Are issues concentrated in one timekeeper, one matter, or across the relationship? Is the trend improving or worsening over the period?]

**Key points to raise:**
[Numbered list of 3–5 specific, evidence-based points. Each point states the observation and the supporting data. These feed directly into the Conversation Guide below.]

---

### Conversation Guide template

---
**[Company] — Billing Relationship Conversation Guide**
**For:** [User name / Legal Ops]
**Conversation with:** [Firm relationship partner / billing contact]
**Meeting date:** [Date]
**Context:** [Relationship review / Ad hoc billing discussion / Matter close / Other]

---

**Before the meeting**

Confirm you have: the Invoice Trend Summary, the specific invoice numbers and line references for any issues you are raising, and your billing guidelines to hand. The goal of this conversation is to resolve the issues and improve future billing — not to win an argument. Come in with the data, not the frustration.

---

**Opening**

> "Thanks for making time. I want to use part of this conversation to talk through some patterns I've been seeing in the billing over the last [period]. Nothing that needs to be a formal issue — I'd rather flag it now and make sure we're aligned going forward."

*Why this works:* Non-accusatory. Signals data, not complaint. Positions this as collaborative. Gives the partner space to respond without being defensive.

---

**Key points to raise**

*For each point, state the observation, show the data, and make the ask. Do not apologise for raising it.*

**Point 1 — [Issue from Trend Summary, e.g., Block billing]**

> "[Opening observation based on data from Trend Summary — e.g., 'Across the last four invoices I've been seeing entries where multiple tasks are combined into a single line item. For example, on [date], there's an entry that covers document review, a team meeting, and research in a single 5.5-hour block.']"

> "[Specific ask — e.g., 'Going forward we need entries separated by task. Our billing guidelines require one task per entry. It makes the review easier on our side and it means we're not having to reject and resubmit.']"

*Anticipated response:* "That's just how our billing system works / our fee earners have always done it that way."
*Your reply:* "I understand it may be a system default — the fix is usually a note to billing coordinators at the matter level. It would save us both time if we can sort it from the next invoice."

---

**Point 2 — [Issue from Trend Summary, e.g., Prohibited fee entries]**

> "[Opening observation — e.g., 'We've also been seeing entries for invoice and budget preparation, which our guidelines treat as non-billable overhead.']"

> "[Specific ask — e.g., 'Those need to come off future invoices. We've been rejecting them on review but I'd rather not have the back-and-forth — it's easier if the billing coordinator removes them before submission.']"

*Anticipated response:* "We weren't aware that was in your guidelines / we don't normally get pushback on those."
*Your reply:* "It's been in our guidelines since [date]. I'll send you the specific section after this call. Happy to set up a short briefing with your billing team if that would help."

---

**Point 3 — [Issue from Trend Summary, e.g., Budget trajectory]**

> "[Opening observation — e.g., 'On budget — we're at [X]% of the approved amount with [Y] months of the matter still to run. At the current run rate we'll be over budget by [month].']"

> "[Specific ask — e.g., 'I need a revised estimate from you by [date] so I can get GC sign-off on a budget adjustment or we need to talk about scope. Which would you prefer to address first?']"

*Anticipated response:* "The scope has expanded / we've had more work than anticipated."
*Your reply:* "I understand — but our guidelines require you to flag that at 80% of budget and we're past that now. Let's make sure we have a process for that on this matter and going forward."

---

**Point 4 — [Additional point if applicable — add or remove as needed]**

---

**Closing the conversation**

> "That covers the main things I wanted to raise. To summarise what we've agreed: [restate the 2–3 specific commitments made during the conversation]. I'll follow up with a short email confirming those so we both have a record. Is there anything you want to raise from your side?"

*Why this works:* States the outcomes clearly. Creates a record. Opens space for the firm to raise issues — which is useful intelligence. Ends collaboratively.

---

**After the meeting**

Send a follow-up email within 24 hours summarising: what was discussed, what was agreed, and any actions with owners and deadlines. Keep it brief — two paragraphs. This email becomes the record if the issues persist and escalation to Mode 4 becomes necessary.

---

### Interpretation framework — apply inside templates above

**What to look for across invoices:**

- *Timekeeper concentration:* One senior timekeeper driving 70%+ of billing on a matter that should be junior-led is a cost management problem, not a compliance problem. Raise it as a staffing conversation, not a billing dispute.
- *Description quality over time:* If descriptions start adequate and degrade over a long matter, that is a supervision failure at the firm. Flag the trend, not just the individual entries.
- *Spend acceleration:* A matter that bills relatively flat for months then spikes is either approaching a fee cap or something changed in scope that was not flagged. Ask which it is before raising as a billing issue.
- *Violation type consistency:* The same violation appearing on every invoice is a process failure at the firm. A different violation each time is more likely to be individual timekeeper behaviour. The distinction affects how you frame the conversation.
- *Improvement after previous flags:* If you have raised issues before and the invoice record shows improvement, acknowledge it. If the firm has made no change, that is the evidence base for Mode 4.

**Tone calibration for the conversation:**

- First time raising an issue: collaborative, information-sharing, forward-looking. The conversation guide opening tone.
- Issue raised before with no improvement: direct. State the history, state what needs to change, set a deadline. Still not adversarial, but not soft.
- Repeated pattern with no acknowledgment: Mode 4 (Compliance Pattern Analysis) is the right tool, not a conversation. The conversation has been had.

---

## Domain Knowledge

### The rule vs. guideline distinction

Billing guidelines contain two types of requirements. **Rules** are enforced universally — prohibited fees, unapproved rates, block billing, duplicate entries. These are always REJECT. **Guidelines** are enforced at the lead attorney's discretion based on context — staffing levels, description quality, internal communications volume. These are REDUCE or APPROVE WITH NOTE depending on the circumstances. The checklist and review report should distinguish between the two. Mixing them creates disputes where firms argue that a discretionary matter was treated as a hard rule.

### Block billing — the most common violation

Defined as combining multiple tasks that would fit different UTBMS codes into a single time entry. The practical test: could this entry legitimately carry two different task codes? If yes, it is block-billed. Standard response is reject and resubmit. Some organisations apply a 10–15% penalty to resubmitted block-billed entries as a compliance incentive. Short tasks totalling 0.1 hours combined in a single entry are a common concession — worth building into the guidelines rather than disputing.

### Prohibited fees — the "don't pay for overhead" principle

The single most consistent thread across billing guidelines: law firms should not bill clients for activities that are the cost of running a law firm. The prohibited fees list is a checklist version of this principle. Invoice preparation, conflict checks, engagement letter preparation, training junior attorneys, and clerical work appear in every published billing guideline. They are non-negotiable rejections. Firms that bill these activities are either not reading the OCGs or testing the client's review rigour.

### The 10% internal communications threshold

Multiple sources converge on 10% of total invoice value as the threshold for internal firm communication entries. Above 10%, it becomes a systemic issue — flag the entire category, not just individual entries. Some organisations make this a per-invoice rule in their OCGs; others apply it as a review heuristic.

### Late submission penalties — graduated approach

Best practice follows a graduated model: invoices 30–60 days late receive a warning; 60–90 days incur a 20% reduction; 90+ days may be rejected entirely. This creates urgency without penalising minor delays. Enforce these consistently — inconsistent enforcement is the primary reason firms ignore submission deadlines.

### UTBMS coding and why it matters beyond compliance

UTBMS codes enable spend analytics. A matter coded entirely as L120 (Analysis/Strategy) rather than L110 (Fact Investigation/Development) and L130 (Expert Witnesses) tells the finance team nothing useful. Enforce coding accuracy not because the codes themselves matter but because they are the foundation for portfolio-level spend analysis, budget benchmarking, and AFA structure. Teams that accept sloppy coding cannot build the data set that justifies moving off hourly.

### The upstream cause: instruction gaps

The majority of billing compliance problems are traceable to instruction quality. A firm that was never told the matter number format, UTBMS requirement, or daily timekeeper cap will bill however their default systems produce. Mode 4 (compliance pattern analysis) should always prompt the question: is this a firm failing or an instruction gap? If the instruction did not specify the requirement, a formal notice is appropriate; if the instruction specified it clearly, the notice is more formal. Cross-reference matter-allocation-instruction (OCM Skill 5) Mode 4 (Instruction Audit) if the root cause is unclear.

### E-billing platforms and what they automate

Brightflag, SimpleLegal, CounselLink, Legal Tracker, and similar platforms automate the mechanical checks (Phase 1 and Phase 5 of the review checklist) and apply billing rules automatically. Teams with these platforms should focus this skill on the judgment-heavy phases: description quality, proportionality of time, staffing appropriateness, and pattern analysis. Teams without a platform need the full checklist to compensate for the absence of automated rule enforcement.

### Appeal windows and defensibility

Standard practice is a 30-day appeal window from the date of rejection notice. The rejection letter should state this explicitly. Adjustments made for prohibited fees and rate violations are typically non-appealable — state this in the rejection letter. Adjustments made for excessive time or description quality are discretionary and should be described as such. Defensibility requires: (a) a written rejection with specific OCG references, (b) a consistent record of enforcement across firms, and (c) documentation of any previous communications on the same issue.

---

## Cross-Skill References

| Upstream skill | Connection to invoice-review-compliance |
|---------------|----------------------------------------|
| engagement-terms-billing-guidelines (Skill 1) | The OCG terms that define what is and is not compliant. Mode 3 checklist reflects what Skill 1 generates. |
| fee-arrangement-structuring (Skill 4) | Fixed fees and capped fees change what the invoice should look like — progress invoices vs. milestone invoices vs. final invoices. Mode 1 review must account for the fee arrangement type. |
| matter-allocation-instruction (Skill 5) | Instruction gaps (missing UTBMS requirement, no staffing disclosure, no late submission penalty) are the root cause of most compliance failures. Mode 4 pattern analysis should surface whether the issue is an instruction gap before escalating to the firm. |
| performance-scorecard (Skill 7) | Invoice compliance feeds the billing adherence component of the performance scorecard. Mode 4 rejection records are input data for the periodic scorecard. |
