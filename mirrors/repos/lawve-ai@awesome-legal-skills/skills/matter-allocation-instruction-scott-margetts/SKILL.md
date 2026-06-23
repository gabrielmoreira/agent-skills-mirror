---
name: matter-allocation-instruction
description: "Firm-matter matching, matter instruction drafting, firm onboarding checklist, and instruction audit for in-house legal ops teams. Match a new matter to the right panel firm by practice area, jurisdiction, complexity, and cost tier. Produce a structured matter instruction with scope, timeline, budget, staffing, and reporting requirements. Generate an onboarding checklist covering conflict clearance, engagement letter, OCG acknowledgment, e-billing setup, and platform access. Audit an existing instruction for completeness and produce a remediation note. Trigger on: 'which firm should handle this', 'instruct the firm', 'write the instruction', 'matter instruction template', 'onboard the firm', 'set up the matter', 'conflict check', 'e-billing setup', 'is our instruction complete', 'review our instruction', 'instruction gap', 'allocate this matter'."
---

# matter-allocation-instruction

## Description

Firm-matter matching, matter instruction drafting, firm onboarding, and instruction quality review for in-house legal ops teams managing outside counsel. Match a new matter to the right panel firm. Produce a structured matter instruction that tells the firm what you need. Generate a matter onboarding checklist that closes the hard gates before work starts. Audit an existing instruction for gaps and produce a remediation note. Trigger on: 'which firm should we use for this', 'instruct [firm]', 'write the instruction letter', 'matter instruction template', 'onboard the firm on this matter', 'set the matter up', 'has conflict been cleared', 'e-billing matter setup', 'review our instruction', 'is our instruction complete', 'instruction gap', 'allocate this matter'.

---

## What This Skill Does

Executes matter allocation and firm engagement from firm selection through to a live, properly-instructed matter. Encodes the methodology for matching work to the right provider, producing a clear instruction, closing onboarding gates, and auditing instruction quality.

**This skill does NOT:**
- Design the panel structure or define firm tiers — use **panel-design-selection** (OCM Skill 2)
- Run the RFP or pitch process to select panel firms — use **rfp-pitch-management** (OCM Skill 3)
- Draft billing guidelines or OCGs — use **engagement-terms-billing-guidelines** (OCM Skill 1)
- Design or negotiate the fee arrangement — use **fee-arrangement-structuring** (OCM Skill 4)
- Review invoices after work has been billed — use **invoice-review-compliance** (OCM Skill 6)

**Cross-skill connection:** panel-design-selection defines which firms are on the panel and at what tier. This skill executes within that structure — it allocates a specific matter to a specific firm, then closes the onboarding gates required before that firm starts work.

---

## Pre-flight — Confirm and Fill

Gather what you have. Fill in what's known. Use placeholders for the rest. Proceed immediately.

| Field | Value |
|-------|-------|
| Company / Legal department | [Company] |
| Matter name / description | [Matter name] |
| Practice area | [Practice area] |
| Jurisdiction(s) | [Jurisdiction(s)] |
| Matter type | New instruction / Existing matter audit / Onboarding setup |
| Panel available | Yes — [describe] / No — proceed with right-sourcing guidance |
| Fee arrangement | Agreed: [type] / To be agreed / Unknown |
| E-billing system | [Platform name] / None / Unknown |
| Maturity level | Early / Intermediate / Advanced |

**Routing:**
- Selecting the right firm for a new matter → **Mode 1: Matter Allocation**
- Writing the instruction to a selected firm → **Mode 2: Instruction Template**
- Setting up a newly instructed firm on a matter → **Mode 3: Firm Onboarding**
- Reviewing an existing instruction for gaps → **Mode 4: Instruction Audit**
- "Which firm should we use?" / "Who should handle this?" / "Allocate this matter" → **Mode 1: Matter Allocation**
- "Write the instruction" / "Draft the instruction letter" / "Instruct [firm]" → **Mode 2: Instruction Template**
- "Onboard the firm" / "Set the matter up" / "What do we need to do before they start?" → **Mode 3: Firm Onboarding**
- "Is our instruction complete?" / "Review the instruction" / "What's missing from our instruction?" → **Mode 4: Instruction Audit**

All documents produced as .docx files unless the user explicitly requests otherwise. Include Company Name, Matter Name, and date in every document header.

---

## Mode 1: Matter Allocation

**Produce a Matter Allocation Recommendation and GC/Budget Holder Note immediately. Do not provide analysis, commentary, bullet points, or narrative before producing the documents. Do not ask clarifying questions. Do not end with a question. A user asking "which firm should handle this", "who should we use", "allocate this matter", or "should we use [firm] or [firm]" is requesting a Matter Allocation Recommendation and a GC/Budget Holder Note — produce both documents immediately using the templates below. The analysis goes inside the Allocation Rationale field of the Recommendation — not before the document. Build from what the user has provided, state assumptions inline. The documents are the response.**

### Input

Matter description, practice area, jurisdiction(s), complexity indication, and panel composition (if known). Minimum viable input is a matter type, practice area, and jurisdiction.

### How to run this mode

1. Produce the Matter Allocation Recommendation — embed the right-sourcing classification, recommended firm (or firm type if no named panel), rationale, alternatives, and conflict clearance instruction inside the document template.
2. Produce the GC/Budget Holder Note.
3. Observations and follow-up questions come after the documents — not before them.

### Matter Allocation Recommendation template

---
**[Company] — Matter Allocation Recommendation**
**Matter:** [Matter name]
**Practice area:** [Practice area]
**Jurisdiction(s):** [Jurisdiction(s)]
**Date:** [Date]
**Prepared by:** [Legal Ops / Relationship Manager name]

**Right-sourcing classification:** [Tier A / Tier B / Tier C — see rationale below]

**Recommended firm:** [Firm name or "Tier A panel firm" if no named panel]
**Alternative(s):** [Firm name(s) or "none identified"]

**Allocation rationale:**
[4–6 sentences. State the right-sourcing tier and why this matter qualifies. Name the specific factors: practice area match, jurisdiction coverage, complexity level, matter value, relationship considerations, cost tier alignment. State any panel standing relevant to the decision — e.g., preferred provider for this practice area; D&I mandate for this work type.]

**Right-sourcing factors applied:**
| Factor | Assessment | Weight |
|--------|------------|--------|
| Practice area match | [Strong / Acceptable / Gap] | High |
| Jurisdiction coverage | [Strong / Acceptable / Gap] | High |
| Matter complexity | [Complex/novel → Tier A; Specialist → Tier B; Routine → Tier C] | High |
| Matter value / materiality | [High / Medium / Low] | Medium |
| Relationship / confidentiality | [Named requirement / None] | Situational |
| Cost tier alignment | [On-tier / Over-tiered / Under-tiered] | Medium |
| D&I panel target | [Applicable / Not applicable] | Low–Medium |

**Conflict clearance:** Required before instruction proceeds. [Firm name] must confirm clearance in writing across [Company]'s full corporate family before any work commences. Do not send confidential materials until clearance is confirmed.

**Fee arrangement:** [Reference agreed AFA if known; or flag: fee arrangement to be agreed before instruction — see fee-arrangement-structuring (OCM Skill 4).]

**Next step:** Proceed to matter instruction (Mode 2) once conflict clearance is confirmed.

---

### GC/Budget Holder Note template

---
**[Company] — Matter Allocation Note**
**Matter:** [Matter name] | **Recommended firm:** [Firm] | **Date:** [Date]

[2 sentences: matter type and recommended firm.] [1 sentence: why this firm — tier match, practice area, jurisdiction coverage.] [1 sentence: cost context — on-tier for this work type, or flag if over-tiered with rationale.] [1 sentence: conflict clearance status and instruction timeline.]

---

### Right-sourcing reference — apply inside templates above

**Tier A — Full-service / BigLaw:** Complex, novel, or multi-jurisdictional matters. Material transaction value. Regulatory, crisis, or contested matters. Matters where institutional scale, bench depth, or relationship continuity is a genuine requirement — not just a default. Risk: over-tiering routine work. Test before allocating to Tier A: does this matter require skills or scale that a Tier B firm demonstrably cannot provide?

**Tier B — Specialist / boutique / mid-market:** Matters within a defined practice specialty where depth outweighs breadth. Cost-sensitive matters with a defined expertise requirement. Geographic specialists for single-jurisdiction work. Emerging areas where specialist firms lead institutional firms. Most matters sent to Tier A by default could appropriately be allocated to Tier B without quality reduction.

**Tier C — ALSP / LPO / process provider:** Routine, templated, or high-volume work. Document review, due diligence, contract abstraction. Process-driven tasks where judgment intensity is low and throughput is the primary metric. Sending Tier C work to Tier A is the most common and most expensive right-sourcing failure.

**Common right-sourcing failure modes:**
- Default BigLaw: allocating to Tier A because that is where the relationship sits, not because the work requires it
- Panel avoidance: sending work outside the panel to a known firm without right-sourcing assessment
- Complexity inflation: characterising routine work as complex to justify a preferred firm
- D&I bypass: consistently allocating to majority firms without assessing diverse provider alternatives

---

## Mode 2: Instruction Template

**Produce a Matter Instruction and Internal Allocation Record immediately. Do not ask clarifying questions, offer a menu of formats, or provide analysis before producing the documents. A user asking to write the instruction, draft the instruction letter, or instruct a named firm is requesting these two documents — produce them immediately. The instruction must be email-ready: complete enough to paste into an email to the supervising partner with no further editing required. Build from what the user has provided, state assumptions inline.**

### Input

Firm name, matter description, scope, timeline, budget (if known), key contacts. Minimum viable input is firm name, matter type, and practice area.

### How to run this mode

1. Produce the Matter Instruction — embed all eleven instruction components inside the template below.
2. Produce the Internal Allocation Record.
3. Observations and follow-up questions come after the documents — not before them.

### Matter Instruction template

---
**[Company]**
**Matter Instruction**
**To:** [Firm name] — [Supervising partner / relationship contact name]
**From:** [In-house counsel / Legal Ops contact name]
**Date:** [Date]
**Matter name:** [Matter name]
**Internal matter number:** [Number or TBC]

**1. Instruction**
[Company] instructs [Firm] to act on the following matter: [1–2 sentences describing the matter and the nature of the instruction — what we need the firm to do.]

**2. Scope**
[3–5 sentences or bullet list. What is included. What is explicitly excluded. If scope is partially defined, state what is known and flag what will be confirmed separately. A vague scope at instruction is the primary cause of AFA failure and OOS disputes — be specific.]

**3. Key contacts**
| Role | Name | Contact |
|------|------|---------|
| In-house matter lead | [Name] | [Email / phone] |
| Legal ops / relationship manager | [Name] | [Email] |
| Firm supervising partner | [Name — to be confirmed by firm] | — |
| Firm billing contact | [Name — to be confirmed by firm] | — |

**4. Timeline and key dates**
| Milestone | Date |
|-----------|------|
| [Key milestone 1] | [Date] |
| [Key milestone 2] | [Date] |
| [Target completion / first deliverable] | [Date] |
| [Any external deadline — regulatory, transaction, court] | [Date] |

**5. Budget and fee arrangement**
Fee arrangement: [Fixed fee: £[X] / Capped fee: £[X] / Hourly — [rate card reference] / TBC — to be agreed within [X] days of this instruction.]
[If AFA: Reference AFA agreed [date]. Firm is reminded of the AI efficiency expectation term in the agreed arrangement.]
Budget approval: [Name / level] has approved legal spend to [£X] for this matter.

**6. Staffing**
[Company] expects the following staffing: [Partner-led / partner name to lead; associate support at [seniority]; no staffing changes without prior notification to [contact name].] Staffing must be disclosed on the first invoice and on any invoice where the staffing mix changes.

**7. Reporting**
Reporting cadence: [Weekly status note / Monthly status report / Milestone-based / Ad hoc on request].
Format: [Email narrative / Template — see attached / Verbal call].
First report due: [Date or trigger event].
Budget alerts: Firm must notify [contact] when WIP reaches [50% / 75% / 80%] of agreed fee and immediately if any circumstance arises that may affect scope or cost.

**8. Outside Counsel Guidelines**
[Company]'s Outside Counsel Guidelines (OCGs) apply to this instruction in full. [Firm] must confirm acknowledgment of current OCGs within [5] business days of this instruction. [If OCGs are attached: See attached.] [If not: OCGs are available at [link or: will be provided by legal ops].]

**9. Conflict clearance**
[Firm] has confirmed conflict clearance in writing on [date] / [Conflict clearance is outstanding — work must not commence until written clearance is received.] Clearance must cover [Company] and its full corporate family as defined in the OCGs.

**10. E-billing and invoicing**
E-billing platform: [Platform name / not yet established — firm to submit invoices by [method]].
Matter number for e-billing: [Number or TBC — legal ops will confirm within [X] business days].
Invoice format: LEDES [1998B / 2.0] with UTBMS task codes. [Or: PDF invoice with UTBMS task-level breakdown.]
Invoice frequency: [Monthly / upon milestone completion / upon completion].
Billing contact: [Name and email].

**11. Engagement letter**
[Firm] must issue an engagement letter consistent with these instructions and [Company]'s OCGs within [5] business days. [Or: Engagement letter received and agreed on [date] — this instruction supplements that agreement.]

*Any questions regarding this instruction should be directed to [contact name] before work commences.*

---

### Internal Allocation Record template

---
**[Company] — Internal Allocation Record**
**Matter:** [Matter name] | **Firm:** [Firm] | **Date:** [Date]

| Field | Value |
|-------|-------|
| Panel tier | [Tier A / B / C] |
| Practice area | [Practice area] |
| Jurisdiction | [Jurisdiction(s)] |
| Fee arrangement | [Type and amount] |
| Budget authority | [Approver name and level] |
| Conflict clearance | Confirmed [date] / Outstanding |
| Engagement letter | Received [date] / Pending |
| OCG acknowledgment | Received [date] / Pending |
| E-billing matter number | [Number] / TBC |
| Relationship manager (in-house) | [Name] |
| Reporting cadence | [Cadence] |

---

## Mode 3: Firm Onboarding

**Produce a Matter Onboarding Checklist and a Firm Onboarding Confirmation Request immediately — both documents, in full. Do not ask clarifying questions, provide commentary, or produce one document without the other. A user asking to onboard a firm, set a matter up, or asking what needs to happen before the firm starts work is requesting both documents — produce them immediately using the templates below. The checklist must include all four phases (Phase 1: hard gates; Phase 2: matter setup; Phase 3: reporting setup; Phase 4: ongoing monitoring). If company name is not provided in the input, use [Company] throughout — including inside checklist item text and the email body. If relationship manager name is not provided, use [Relationship Manager]. Do not substitute names from session context. Do not ask a question at the end of the response.**

### Input

Firm name, matter name, instruction status. Minimum viable input is firm name and matter description.

### How to run this mode

1. Produce the Matter Onboarding Checklist — include all four phases with completion fields.
2. Produce the Firm Onboarding Confirmation Request.
3. Observations and follow-up questions come after the documents — not before them.

### Matter Onboarding Checklist template

---
**[Company] — Matter Onboarding Checklist**
**Matter:** [Matter name] | **Firm:** [Firm] | **Date:** [Date]
**Relationship manager:** [Name]

**PHASE 1: Hard gates — work must not commence until all items complete**

| # | Item | Owner | Due | Status |
|---|------|-------|-----|--------|
| 1 | Conflict clearance confirmed in writing (corporate family scope) | Firm | Before instruction | ☐ |
| 2 | Engagement letter issued and agreed | Firm | Within 5 business days of instruction | ☐ |
| 3 | OCG acknowledgment received from firm | Firm | Within 5 business days of instruction | ☐ |
| 4 | Fee arrangement confirmed and documented | Both | Before instruction / within [X] days | ☐ |

*Do not release confidential materials or permit work to commence until Phase 1 is complete.*

**PHASE 2: Matter setup — complete within 2 business days of instruction**

| # | Item | Owner | Due | Status |
|---|------|-------|-----|--------|
| 5 | Matter opened in e-billing system | Legal Ops | Day 1–2 | ☐ |
| 6 | E-billing matter number issued to firm | Legal Ops | Day 1–2 | ☐ |
| 7 | E-billing platform access granted to firm's billing contact | Legal Ops / IT | Day 1–2 | ☐ |
| 8 | Invoice format confirmed with firm billing team (LEDES / PDF + UTBMS) | Legal Ops | Day 1–2 | ☐ |
| 9 | Budget entered in e-billing system or tracking tool | Legal Ops | Day 1–2 | ☐ |
| 10 | NDA / confidentiality terms agreed if required | Legal / Firm | Before document transfer | ☐ |
| 11 | Background documents and key materials transferred to firm | Matter lead | Day 1–5 | ☐ |

**PHASE 3: Reporting setup — complete within first week**

| # | Item | Owner | Due | Status |
|---|------|-------|-----|--------|
| 12 | Supervising partner confirmed at firm | Firm | Day 1 | ☐ |
| 13 | Billing contact confirmed at firm | Firm | Day 1–2 | ☐ |
| 14 | Reporting cadence agreed and first report date confirmed | Both | Week 1 | ☐ |
| 15 | Status report format agreed (email / template / call) | Both | Week 1 | ☐ |
| 16 | Budget alert thresholds communicated to firm (50% / 75% / 80% WIP) | Legal Ops | Week 1 | ☐ |

**PHASE 4: Ongoing monitoring — confirm at 30 days**

| # | Item | Owner | Due | Status |
|---|------|-------|-----|--------|
| 17 | First invoice received and reviewed | Legal Ops | [First billing cycle] | ☐ |
| 18 | Staffing disclosure confirmed on first invoice | Legal Ops | [First billing cycle] | ☐ |
| 19 | First status report received and filed | Matter lead | [Per agreed cadence] | ☐ |
| 20 | 30-day relationship check (any issues surfaced?) | Relationship mgr | Day 30 | ☐ |

---

### Firm Onboarding Confirmation Request template

---
**To:** [Firm supervising partner / billing contact]
**From:** [Legal Ops / Relationship Manager]
**Subject:** [Company] / [Matter name] — Onboarding requirements

[Partner name],

Thank you for confirming your instruction on [matter name]. To ensure the matter is properly set up before work commences, please action the following within 5 business days:

1. **Conflict clearance:** Confirm in writing that [Firm] has cleared conflicts across [Company] and its full corporate family.
2. **Engagement letter:** Issue an engagement letter consistent with our instruction letter dated [date] and [Company]'s Outside Counsel Guidelines.
3. **OCG acknowledgment:** Confirm in writing that [Firm] has received and will comply with [Company]'s current Outside Counsel Guidelines. [Attached / Available at: [link].]
4. **Billing contact:** Confirm the name and email of [Firm]'s billing contact for this matter. Legal ops will issue e-billing access and the matter number once confirmed.
5. **Staffing:** Confirm the supervising partner and proposed staffing team.

Work should not commence and confidential materials will not be transferred until conflict clearance is confirmed.

[Contact name] from our legal ops team will follow up on e-billing setup once the above is received. Please direct any questions about this instruction to [contact name / email].

Regards,
[Name]

---

## Mode 4: Instruction Audit

**Produce an Instruction Gap Assessment and an Instruction Remediation Note immediately — both documents, in full, using the templates below. Do not produce analysis, bullet points, or narrative before the documents. Do not ask a question at the end. Do not withhold the Remediation Note pending further information — produce it with placeholders where details are unknown. A user pasting an instruction and asking "what's missing", "is this complete", or "review our instruction" is requesting Document 1 (Gap Assessment) and Document 2 (Remediation Note) — produce both immediately. The scoring goes inside the Gap Assessment table. The scope clause, budget cap, reporting cadence, and conflict requirement go inside the Remediation Note. Build from what the user has provided. Use matter context to populate placeholders.**

### Step 1 — Produce the Instruction Gap Assessment using this template:

---
**[Company] — Instruction Gap Assessment**
**Matter:** [Matter name] | **Firm:** [Firm] | **Audit date:** [Date]
**Instruction date:** [Date sent / Unknown]

**Summary:** [X] of 11 components present. [X] absent. [X] partial. Critical gaps: [list or "none"].

| # | Component | Status | Finding |
|---|-----------|--------|---------|
| 1 | Instruction statement (what the firm is asked to do) | ✓ / ✗ / ~ | [Brief finding] |
| 2 | Scope definition (included and excluded) | ✓ / ✗ / ~ | [Brief finding] |
| 3 | Key contacts (in-house lead, firm contact, billing contact) | ✓ / ✗ / ~ | [Brief finding] |
| 4 | Timeline and key dates | ✓ / ✗ / ~ | [Brief finding] |
| 5 | Budget and fee arrangement | ✓ / ✗ / ~ | [Brief finding] |
| 6 | Staffing expectations | ✓ / ✗ / ~ | [Brief finding] |
| 7 | Reporting cadence and format | ✓ / ✗ / ~ | [Brief finding] |
| 8 | OCG reference and acknowledgment requirement | ✓ / ✗ / ~ | [Brief finding] |
| 9 | Conflict clearance confirmation | ✓ / ✗ / ~ | [Brief finding] |
| 10 | E-billing and invoicing instructions | ✓ / ✗ / ~ | [Brief finding] |
| 11 | Engagement letter requirement | ✓ / ✗ / ~ | [Brief finding] |

**Critical gaps (address immediately):**
[Scope, conflict clearance, and fee arrangement gaps are always critical. List any other components scored ✗ that create legal, financial, or relationship risk if not remedied.]

**Supplementary gaps (address before first invoice):**
[Reporting cadence, staffing disclosure, e-billing setup — gaps that create problems downstream but do not block the instruction itself.]

**Overall assessment:** [Complete — no action required / Gaps identified — see remediation note / Critical gaps — supplement required before work proceeds.]

---

### Step 2 — Produce the Instruction Remediation Note using this template:

---
**[Company]**
**Instruction Supplement — [Matter name]**
**To:** [Firm] — [Supervising partner]
**From:** [In-house contact]
**Date:** [Date]
**Re:** Supplement to instruction dated [original instruction date]

This note supplements our instruction of [date] on [matter name]. The following items were not addressed in the original instruction and are now confirmed.

**1. Scope**
For the avoidance of doubt, the scope of [Firm]'s instruction is: [scope statement drawn from matter context — name what is in, what is out, and what requires prior approval]. Work outside this scope requires prior written approval from [contact] before it is undertaken.

**2. Budget and fee arrangement**
[State the fee basis, approved budget or cap, and budget alert thresholds. If fee is unknown, state: "A budget cap of [£TBC — to be agreed within 5 business days] applies. Firm must provide a current WIP statement and cost forecast within 5 business days of this supplement."]

**3. Reporting**
[Set cadence, format, first report date. State: "First report due within 5 business days of this supplement covering the period from instruction to date."]

**4. Conflict clearance**
[Require written confirmation that conflicts were checked at outset across corporate family. If not checked, require it now.]

**5. Staffing**
[Require disclosure of all fee earners who have recorded time, with grade and rate. Set notification requirement for future changes.]

**6. OCG and billing compliance**
[Reference OCGs and require acknowledgment. State LEDES/UTBMS requirement for future invoices.]

**7. Engagement letter**
[Require issuance within 5 business days or confirmation that one was issued at outset.]

All other terms of the original instruction remain in force. Please confirm receipt and respond to outstanding items within [5] business days.

---

### Instruction quality reference — apply inside templates above

**Scoring guidance:**
- ✓ (Present): Component is addressed with enough specificity that the firm can act on it
- ~ (Partial): Component mentioned but insufficiently specific — scope stated but exclusions not named; budget referenced but no alert threshold
- ✗ (Absent): Component not addressed at all

**Critical gaps are always:** scope (#2), budget/fee (#5), conflict clearance (#9). Reporting (#7) is critical when a matter is already in progress with no reporting in place.

**What poor instructions produce:** scope disputes (firm's interpretation prevails when scope is undefined); unexpected invoices (no ceiling, no obligation to warn); no reporting (you didn't ask for any); staffing surprises (whoever is available runs the matter); conflict risk (undocumented check is not a check).

### Step 3 — Observations after documents

Flags, priorities, and follow-up questions come here — after both documents are complete.

---

## Domain knowledge — right-sourcing and instruction quality

### Why instruction quality matters

The typical matter instruction is a two-line email. That email is the contract. Scope disputes, OOS claims, staffing changes, and invoice compliance failures all trace back to what was — and was not — said at instruction.

A clear, complete instruction does four things a two-line email does not:
1. Defines scope in a way that can be tested against later claims
2. Sets cost and reporting expectations before the first bill arrives
3. Documents conflict clearance and OCG acknowledgment as facts on record
4. Creates the e-billing setup conditions that make invoice review possible

### Conflict clearance is a hard gate

Conflict clearance is not a formality. It is a condition precedent to the instruction. Work commenced before conflict clearance is confirmed exposes both the firm and the client to professional responsibility risk. In corporate matters, clearance must cover the full corporate family — subsidiaries, JV partners, counterparties — not just the entity named on the instruction.

Document the date and form of clearance confirmation in the Internal Allocation Record. An undocumented conflict check is not a conflict check.

### E-billing setup as instruction component

E-billing setup is an instruction task, not an administrative afterthought. If the matter number is not in the system before the first invoice arrives, the invoice cannot be processed. If the firm has not been told the LEDES format requirement, the first invoice will arrive in PDF without UTBMS codes. Retrospective reformatting is operationally expensive and delays payment — which strains the relationship before it has started.

Issue the matter number and e-billing access within two business days of instruction. Confirm invoice format with the firm's billing contact, not the supervising partner. Partners do not control invoice format.

### Reporting cadence at instruction, not mid-matter

Reporting expectations set mid-matter are requests. Reporting expectations set at instruction are requirements. The instruction is the moment when the client has maximum leverage. Use it.

State the cadence, the format, and the first report date. State the budget alert thresholds. If the matter runs six months with no status report, the absence of a reporting requirement in the instruction is why.

