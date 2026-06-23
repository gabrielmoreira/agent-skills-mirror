---
name: fee-arrangement-structuring
description: "AFA design, scope-to-fee matching, negotiation preparation, health check, and scope dispute assessment for in-house legal ops teams managing outside counsel arrangements. Design fee structures (fixed, capped, collar, blended, phased, success). Assess whether scope supports a proposed AFA. Prepare commercial positions for fee negotiations. Review existing AFAs against delivery data. Assess OOS claims and build dispute response. Trigger on: 'structure the fee', 'move off hourly', 'design an AFA', 'does scope support a fixed fee?', 'negotiate the fee', 'renegotiate the arrangement', 'is our AFA holding?', 'fee health check', 'cap is being approached', 'firm is claiming OOS', 'is this in scope?', 'is this OOS?', 'AI should reduce the cost', 'blended rate vs fixed', 'collar arrangement', 'phased fees'."
---

# fee-arrangement-structuring

## Description

AFA design, scope-to-fee matching, negotiation preparation, and health check for in-house legal ops teams managing outside counsel arrangements. Design fee structures (fixed, capped, collar, blended, phased, success) matched to matter characteristics. Assess whether scope supports a proposed AFA structure. Prepare commercial positions for fee renegotiation conversations. Review existing AFAs against delivery data. Trigger on: 'structure the fee for this matter', 'move off hourly', 'design an AFA', 'fixed fee for this type of work', 'does scope support a fixed fee?', 'negotiate the fee', 'renegotiate the arrangement', 'is our AFA holding?', 'fee health check', 'cap is being approached', 'firm is claiming OOS', 'AI should reduce the cost', 'blended rate vs fixed', 'collar arrangement', 'phased fees', 'success fee structure'.

---

## What This Skill Does

Structures commercial fee arrangements between in-house legal teams and outside counsel. Encodes the methodology for selecting, documenting, stress-testing, and renegotiating AFA structures across the full arrangement lifecycle.

**This skill does NOT:**
- Build the phase-based matter budget or track WIP variance — use **budget-and-fee-manager** (LPM Core)
- Draft billing guidelines or rate card policy — use **engagement-terms-billing-guidelines** (OCM Skill 1)
- Run the RFP process or evaluate firm proposals — use **rfp-pitch-management** (OCM Skill 3)
- Manage scope change control from the law firm side — that is a firm-side LPM function; this skill handles scope disputes from the in-house client perspective

**Cross-skill connection:** fee-arrangement-structuring determines the commercial structure. budget-and-fee-manager models whether the number is viable and monitors actual vs agreed during execution.

---

## Pre-flight — Confirm and Fill

Gather what you have. Fill in what's known. Use placeholders for the rest. Proceed immediately.

| Field | Value |
|-------|-------|
| Company / Legal department | [Company] |
| Matter name / description | [Matter name] |
| Practice area | [Practice area] |
| Instruction type | New matter / Existing matter / Matter type (portfolio) |
| Approximate matter value / complexity | [High / Medium / Low or £/$ estimate] |
| Current fee arrangement (if any) | [Hourly / AFA type / None] |
| Fee preference or constraint (if any) | [e.g., "GC wants fixed", "firm proposing capped", "no preference"] |
| Scope status | [Defined / Partially defined / Undefined] |
| Maturity level | Early / Intermediate / Advanced |

**Jurisdiction note:** Rate benchmarks default to UK/GBP. US benchmarks (AmLaw data) and Australian benchmarks are available — state your jurisdiction in pre-flight or within mode input and the skill adapts.

**Routing:**
- Structuring a new arrangement → **Mode 1: AFA Design**
- Checking if scope supports a proposed AFA → **Mode 2: Scope-to-Fee Matching**
- Preparing for a fee negotiation or renegotiation → **Mode 3: AFA Negotiation Brief**
- Reviewing an existing AFA mid-matter or at close → **Mode 4: AFA Health Check**
- A firm is claiming work is out of scope (OOS) → **Mode 5: Scope Dispute Assessment**
- "Is this in scope?" / "Is this OOS?" / "Is the firm's OOS claim valid?" / "Does this scope clause cover this work?" → **Mode 5: Scope Dispute Assessment**

All outputs are produced as .docx files unless the user explicitly requests otherwise. Include Client Name, Matter Name, and date in every document header.

---

## Mode 1: AFA Design

**Produce an AFA Recommendation Memo and GC Sign-off Brief immediately. Do not ask clarifying questions, offer a menu of deliverables, or provide analysis before producing the documents. Do not answer the user's question conversationally — the AFA Recommendation Memo and GC Sign-off Brief are the answer. A user asking how to assess a fee proposal, whether a number is reasonable, or how to respond to a firm is requesting these two documents — produce them immediately. Build from what the user has provided, state assumptions inline. The documents are the response.**

### Input

Matter description, practice area, scope status, any fee preference. Minimum viable input is a matter type and practice area.

### How to run this mode

1. Produce the AFA Recommendation Memo — embed the AFA selection classification, recommended structure, rationale, alternatives, and AI pricing terms inside the document template.
2. Produce the GC Sign-off Brief.
3. Observations and follow-up questions come after the documents — not before them.

### AFA selection matrix

Use this logic to determine the appropriate structure. State the classification inline in the memo.

| Factor | Fixed Fee | Capped Fee | Phased Fixed | Blended Rate | Collar | Success Fee |
|--------|-----------|------------|--------------|--------------|--------|-------------|
| Scope defined | Required | Helpful | Phase 1 only | Not required | Required | Defined outcome |
| Scope stable | Required | Helpful | Per phase | Not required | Required | Outcome-stable |
| Repeat/portfolio work | Strong fit | Acceptable | Acceptable | Strong fit | Strong fit | Situational |
| High matter value | Viable | Viable | Preferred | Not fit | Preferred | Litigation only |
| Price certainty priority | Primary fit | Good fit | Good fit | Poor fit | Good fit | Poor fit |
| Risk sharing appetite | Moderate | Low | Moderate | None | High | High |

**Fixed fee:** Total price for defined scope. Requires upfront scope clarity. Firm assumes delivery risk. Client assumes scope stability risk. The standard AFA for transactional and advisory matters with defined outputs.

**Capped fee:** Hourly billing up to a maximum. Client gets downside protection; firm retains hourly until cap. Common where scope is broadly predictable but firm is unwilling to accept full fixed-fee risk. Risk: firm may slow-walk work to cap, then quality drops.

**Phased fixed fees:** Fixed fee per project phase. Scope is renegotiated between phases. Best structure for multi-phase matters (transactions, regulatory processes, restructurings) where later phases are genuinely uncertain at outset. Preferred over a single fixed fee on any matter with meaningful phase-gate decisions.

**Blended rate:** Single agreed rate across all timekeepers. Simplifies billing. Hides leverage mix — firm can use any combination of partner/associate/paralegal and bill at blended rate. Check whether the blended rate was modelled on expected staffing or optimistic staffing. Volume commitment or long-term panel relationship is the typical commercial basis.

**Volume discount:** Reduced rates in exchange for committed spend or matter volume. Not a standalone AFA type — a commercial term layered on top of hourly or blended. Appropriate for high-volume portfolio relationships. Requires spend tracking to validate.

**Collar arrangement:** Both parties share upside and downside around an agreed estimated fee. If actual cost is within the collar (e.g., ±15%), each party absorbs their share. Outside the collar, variance is split according to agreed percentages. Most sophisticated and fair structure. Requires mutual trust, good scope definition, and data to model the collar width. Appropriate for mature relationships with historical cost data.

**Success fee / contingency element:** Payment tied to defined outcome. Pure contingency (no win, no fee) is rare in non-litigation transactional work. Hybrid structures — base fee plus success element tied to completion, value threshold, or regulatory approval — are common in M&A, real estate, and some finance work. Requires unambiguous definition of the triggering outcome.

**Hourly remains appropriate when:** scope is genuinely unpredictable (contested litigation with no ceiling visibility; regulatory investigation with uncertain scope); first-time instruction on a novel matter type with no historical data; matter where the risk of mis-scoping materially exceeds the benefit of price certainty.

### AI pricing — non-negotiable content

Encode AI efficiency expectations in every AFA structure. This is a standard commercial term, not an optional addition.

**The core tension:** Hourly billing creates a perverse incentive — AI makes tasks faster, reducing hours and firm revenue. Fixed fees solve this: AI efficiency is captured as margin by the firm unless benchmarks and expectations are set at the time of agreement.

**Required commercial term in every Mode 1 output:**

> *AI efficiency expectation:* The fee has been set on the basis that [Company] expects [Firm] to utilise AI tools where they reduce delivery time and cost. [Company] requires [Firm] to disclose, upon request, which tasks have been AI-assisted and the time savings realised. If AI adoption materially reduces delivery cost below the fixed fee during the engagement term, [Company] expects the benefit to be reflected in the next renewal cycle.

**AI-adjusted fixed fee question:** In any fixed-fee negotiation, ask the firm: "What portion of this estimate reflects hours that AI tools could accelerate?" If the answer is materially non-zero, the starting price should be lower than the unadjusted historical estimate.

**Market context for negotiations (use in GC brief):**
- Top 100 firm rates increased 10% in 2024; top 50 firms increased 12.1%. Senior partner M&A rates average £1,400–£1,680/hour in London.
- 83% of proposals on PERSUIT use value-based pricing — fixed-fee structures are market standard for well-scoped work.
- 71% of in-house teams expect outside counsel to use generative AI; only 6% of AI efficiency savings are currently passed to clients (Axiom 2025). Rate negotiations in 2026 routinely include AI pricing questions.

### Common AFA failure modes

Encode these as named risks in every AFA Recommendation Memo:

1. **Scope not defined before fixing the fee.** The fixed fee becomes an informal cap; overruns are argued rather than documented. Mitigation: scope definition is a prerequisite to signing the AFA. Attach the scope document to the engagement letter.

2. **Fee fixed without understanding the firm's cost base.** An unprofitable arrangement produces a deprioritised matter. Mitigation: require the firm to provide a high-level cost breakdown (hours by grade, assumptions) alongside any fixed-fee proposal. The breakdown reveals whether the fee is viable.

3. **Capped fee creating a perverse incentive.** Firm races to the cap, then quality drops. Mitigation: build in a milestone-based trigger — if 80% of cap is reached before 60% of scope is complete, a review is mandatory before further work proceeds.

4. **Success fee with undefined "success."** Dispute on completion. Mitigation: define the triggering outcome in writing before work begins. Attach to engagement letter. Common failures: "successful completion" of a transaction without defining what completion means if a condition is not satisfied.

5. **Blended rate hiding unhelpful leverage mix.** Firm uses partner-heavy team; client pays blended rate for overqualified resourcing. Mitigation: specify expected staffing grade mix as a condition of the blended rate. Include a rate adjustment mechanism if actual mix diverges materially.

6. **AFA agreed but billing system doesn't support it.** WIP is tracked hourly; AFA reconciliation is manual; finance loses confidence in accruals. Mitigation: confirm e-billing system supports AFA billing before agreeing the structure. If not, build monthly fixed-amount invoice schedule into the engagement letter.

7. **No scope change mechanism.** First OOS request collapses the AFA — either the firm absorbs it (unprofitable) or the client pays full hourly for it (defeating the purpose). Mitigation: define a named scope change protocol in the engagement letter. Small OOS items (below threshold) are absorbed. Material OOS triggers a mini-scoping conversation and a fee amendment.

### Maturity calibration

**Early:** Recommend capped fee or phased fixed fee as first step off hourly. Don't design an arrangement the team can't administer. Skip collar structures. Focus on scope definition as prerequisite.

**Intermediate:** Fixed fee with AI transparency term. Blended rate for high-volume portfolio work. Scope change mechanism as a standard term.

**Advanced:** Collar structures for high-value strategic relationships. Multi-year AFA programmes with annual rate review tied to AI efficiency benchmarks. Portfolio-level volume commitments with blended panel rates.

### Output template: AFA Recommendation Memo

---
**AFA RECOMMENDATION MEMO**
**Company:** [Company]
**Matter:** [Matter name]
**Date:** [Date]
**Prepared by:** Legal Operations

**Recommended structure:** [AFA type]
**Recommended fee range:** [£X–£Y] / [Confirm]
**Alternatives considered:** [Type 1 — rationale for rejecting] / [Type 2 — when to reconsider]

**Scope prerequisites:** [What must be defined before this AFA is viable]
**Key commercial terms:**
- AI efficiency expectation: [standard term above, adapted to matter]
- Scope change protocol: [threshold and mechanism]
- Cap / collar parameters: [if applicable]
- Success trigger definition: [if applicable]
- Billing / invoicing: [frequency, format, e-billing system]

**Named risks:**
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| [Failure mode 1] | [H/M/L] | [Mitigation] |
| [Failure mode 2] | [H/M/L] | [Mitigation] |

**Next step:** [Confirm scope document / Instruct firm to submit cost breakdown / Raise in panel review]

---

### Output template: GC Sign-off Brief

---
**GC SIGN-OFF — FEE ARRANGEMENT**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]

**Recommended fee structure:** [AFA type] — [one sentence rationale]

**Proposed fee:** [£X] / [Confirm — subject to scope finalisation]

**Why this structure:**
[2–3 sentences: matter characteristics that support this AFA type]

**Market context:**
[1–2 sentences: rate environment, AFA adoption trends, AI pricing relevance]

**Key protection terms:** [AI transparency term / scope change mechanism / milestone trigger]

**Approval required:** ☐ Approve recommended structure and proceed to firm negotiation
**GC:** _________________________ **Date:** _________________________

---

---

## Mode 2: Scope-to-Fee Matching

**Produce a Scope-Fee Assessment and Risk Register immediately. Do not ask clarifying questions, offer a menu of deliverables, or provide analysis before producing the documents. Do not answer the user's question conversationally — the Scope-Fee Assessment and Risk Register are the answer. A user asking "is this OOS?", "is this in scope?", "does this scope clause cover this work?", or "is the firm's OOS claim valid?" is requesting these two documents — fill in the templates below immediately. Do not answer the question with a yes/no analysis. Example: if a user provides a scope clause and asks whether specific work falls within it, the Scope-Fee Assessment is the answer, not a legal opinion. The documents are the response.**

### Output template: Scope-Fee Assessment

---
**SCOPE-FEE ASSESSMENT**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]
**Proposed AFA:** [AFA type] | **Proposed fee:** [£X] / [Confirm]

**Assessment: [VIABLE / VIABLE WITH CONDITIONS / NOT VIABLE]**

**Scope inventory:**
| Scope element | Defined? | Stable? | Precedented? | AI-sensitive? |
|---------------|----------|---------|--------------|---------------|
| [Element 1] | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |
| [Element 2] | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |
| [Undefined/open element] | ✗ | — | — | — |

**Compatibility verdict:**
[1–2 sentences: why the proposed AFA type does or doesn't suit the scope as defined]

**Conditions for viability (if any):**
1. [Scope element to define before AFA is viable]
2. [Confirm]

**Alternative structure (if proposed type is not viable):**
[Alternative AFA type and rationale]

---

### Output template: Risk Register

---
**SCOPE-FEE RISK REGISTER**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]

| Risk | Description | Likelihood | Impact | Mitigation |
|------|-------------|-----------|--------|------------|
| Scope expansion | [Which element is undefined and could grow] | [H/M/L] | [H/M/L] | [Scope change protocol] |
| AI efficiency gap | [Which AI-sensitive tasks are priced at full hourly rate] | [H/M/L] | [H/M/L] | [Require AI disclosure at proposal stage] |
| Delivery mis-model | [What firm assumptions may be wrong] | [H/M/L] | [H/M/L] | [Require cost breakdown] |
| Billing system gap | [E-billing support for AFA type] | [Confirm] | [H/M/L] | [Confirm before signing] |

---

### Scope assessment framework (reference — apply inside templates above)

**Defined:** The work is specified with enough clarity that a firm could price it with confidence. Examples: "draft and negotiate the SPA and ancillary documents for a £50M UK share sale, expected to close by end of Q3" is defined. "Advise on the transaction" is not.

**Stable:** The scope is unlikely to change materially during delivery. Indicators of instability: regulatory approval pending; counterparty not yet engaged; client not fully committed to structure; prior instructions suggesting frequent scope changes.

**Precedented:** The firm has done similar work before. Indicators: repeat matter type, same industry, similar value.

**AI-sensitive:** Portions of the scope that AI tools are likely to accelerate (contract drafting, due diligence, research, boilerplate). Flag these because they affect the correct fixed-fee benchmark.

### AFA viability thresholds

| AFA Type | Minimum scope requirements |
|----------|---------------------------|
| Fixed fee | Defined, Stable, Precedented — all three |
| Capped fee | Defined — one of Stable or Precedented |
| Phased fixed | Phase 1 Defined + Stable; later phases can be undefined |
| Blended rate | None — suitable for undefined/unpredictable work |
| Collar | Defined, Stable, Precedented + historical cost data |
| Success fee | Outcome precisely defined; base scope Defined |

If the proposed AFA type does not meet the minimum requirements, produce the assessment anyway — state what's missing and what needs to be resolved before the AFA is viable.

Observations and follow-up questions come after the documents — not before them.

## Mode 3: AFA Negotiation Brief

**Produce a Negotiation Brief and Firm-Facing Agenda immediately. Do not ask clarifying questions, offer a menu of deliverables, or provide analysis before producing the documents. Do not answer the user's question conversationally — the Negotiation Brief and Firm-Facing Agenda are the answer. A user asking how to handle a negotiation, how to respond to a rate request, or how to frame a fee conversation is requesting these two documents — produce them immediately. Build from what the user has provided, state assumptions inline. The documents are the response.**

### Output template: Negotiation Brief

---
**AFA NEGOTIATION BRIEF — INTERNAL**
**Company:** [Company] | **Matter / Arrangement:** [Matter name] | **Date:** [Date]
**Firm:** [Firm name]

**Objective:** [One sentence: what we want to achieve in this conversation]

**Current position:** [Existing arrangement and why it needs to change]

**Our opening:** [Specific commercial position — number or structure]

**Rationale:** [Why this position is reasonable — scope, precedent, market data, AI efficiency]

**Acceptable outcome:** [What we'll sign]

**Walkaway:** [What we won't accept]

**Key levers:**
1. [Scope document — attach if available]
2. [Competing proposal — reference if available]
3. [AI efficiency question — script below]
4. [Market data — rate benchmarks relevant to this practice area]

**AI efficiency script:**
> "We understand your firm has invested significantly in AI tooling. For this type of work, what proportion of hours in your estimate reflects tasks that AI could accelerate? We'd like to understand your AI-adjusted cost base before we agree a structure."

**Non-negotiables:**
- AI efficiency expectation term (standard — non-negotiable)
- Scope change protocol (threshold: [£X or %])
- Cost breakdown before fixed-fee agreement

---

### Output template: Firm-Facing Agenda

---
**FEE STRUCTURE CONVERSATION — AGENDA**
**[Company] | [Matter / Arrangement] | [Date]**

1. **Context** — [Company] is [brief: new matter / renewal / panel review context] (5 min)
2. **Scope alignment** — confirm scope and any open items (10 min)
3. **Fee structure discussion** — [Company] position on preferred AFA type (15 min)
4. **Commercial terms** — AI transparency, scope change mechanism, billing format (10 min)
5. **Next steps** — timeline for firm to submit [cost breakdown / revised proposal] (5 min)

**To prepare:** [Firm] to bring [cost breakdown / prior matter data / AI capability overview / Confirm]

---

---


### Negotiation dynamics (reference — apply inside templates above)

**Firms price uncertainty into fixed fees.** The first fixed-fee proposal from any firm includes a risk premium. The correct response is not to accept or reject — it is to require a cost breakdown. A breakdown reveals whether the premium is justified or inflated.

**Scope document is leverage.** A well-scoped matter reduces the firm's uncertainty, which reduces their risk premium, which reduces the fee. Investing one hour in scope definition before the negotiation is worth more than one hour of negotiating.

**AI efficiency is a negotiating lever in 2026.** 71% of in-house teams expect AI use; only 6% of savings pass through. In any renewal or renegotiation: "Your AI adoption should reduce the delivery cost below last cycle's number — what's your AI-adjusted estimate?" If the firm cannot answer, that is itself informative.

**Multi-firm competition drives pricing down.** If the matter has been through a competitive process (rfp-pitch-management Mode 1 or 2), use competing proposals to anchor the negotiation.

**Partner resistance to AFAs is about control.** Hourly billing means unlimited scope; partners rarely track their own cost base. Reframe: "We're not asking you to take a loss — we're asking you to price what you know how to deliver." The partner who can't scope their own work is the more significant problem.

**Rate escalation context (UK):**
- Top 100 firm rates +10% in 2024; top 50 firms +12.1%.
- Senior partner M&A rates averaging £1,400–£1,680/hour in London.
- Partners in top 25 global firms approaching £2,500/hour.
- AI-adjusted rates have not yet standardised — this is where in-house teams have the most leverage now.

**Common opens and walkaway points:**

| Scenario | Opening position | Acceptable outcome | Walkaway |
|----------|-----------------|-------------------|----------|
| New fixed fee | AI-adjusted estimate, require breakdown | Fixed fee with AI transparency term | Hourly without cap |
| Cap renegotiation | Reset cap based on current scope | Milestone trigger at 80% of cap | Cap increase without scope review |
| Rate increase request | Require AI efficiency disclosure first | Inflation-linked increase with AI discount | >8% increase without AI offset |
| AFA collapse (overrun) | Understand root cause first | Absorb partial overrun, scope change protocol going forward | Full acceptance of overrun without learning |


## Mode 4: AFA Health Check

**Produce an AFA Health Check Report and Recommended Actions document immediately. Do not ask clarifying questions, offer a menu of deliverables, or provide analysis before producing the documents. Do not answer the user's question conversationally — the AFA Health Check Report and Recommended Actions are the answer. A user asking about AFA status, whether a cap is being approached, what their options are, or describing a change in delivery circumstances (cap reached, hearing relisted, scope expanded, WIP overrun) is requesting these two documents — fill in the templates below immediately. Do not rank options or provide analysis before producing the documents. The documents are the response.**

### Output template: AFA Health Check Report

---
**AFA HEALTH CHECK REPORT**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]
**Original AFA:** [Type] | **Agreed fee:** [£X] / [Confirm]
**Review period:** [Date range or matter stage]

**Status: [ON TRACK / AT RISK / BROKEN]**

**WIP position:**
| Metric | Agreed | Actual to date | Projected at completion |
|--------|--------|----------------|------------------------|
| Fee | [£X] | [£Y] / [Confirm] | [£Z] / [Confirm] |
| Scope completion | — | [%] / [Confirm] | [%] / [Confirm] |
| Milestones | [N] planned | [N] completed | [Confirm] |

**Drift signals:**
| Signal | Status | Evidence |
|--------|--------|----------|
| Scope expansion | [Yes / No / Unconfirmed] | [Description] / [Confirm] |
| WIP ahead of scope | [Yes / No] | [WIP % vs scope %] / [Confirm] |
| AI assumption drift | [Assessed / Not assessed] | [Confirm] |
| Milestone slippage | [Yes / No] | [Which milestones] / [Confirm] |

**Assessment:**
[2–3 sentences: why the AFA is on track, at risk, or broken — specific to this matter]

---

### Output template: Recommended Actions

---
**RECOMMENDED ACTIONS**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]

| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | [Specific action] | [Company / Firm / Joint] | [Date] / [Confirm] |
| 2 | [Specific action] | [Company / Firm / Joint] | [Date] / [Confirm] |

**Escalation threshold:** If [trigger condition], escalate to [GC / CPO / Confirm] before proceeding.

**Next health check:** [Date or milestone trigger]

---

---


### Health check reference (apply inside templates above)

Run Mode 4 when any of the following occur — do not wait for matter close:

- WIP has reached 60–70% of a fixed fee or cap before 50% of scope is complete
- A scope change has been accepted without formal OOS documentation
- The firm has mentioned "additional work" or "out of scope" in any communication
- A milestone has been missed and no timeline adjustment has been agreed
- AI efficiency assumptions built into the fee have not been validated mid-matter
- It has been >90 days since the AFA was agreed and no check-in has occurred

### Health check assessment framework

**On track:** WIP trajectory consistent with scope completion. No material scope changes. Milestones met. AI assumptions either validated or neutral.

**At risk:** WIP running ahead of scope completion (>15% variance). One or more scope changes absorbed without fee adjustment. Milestone slippage creating delivery uncertainty. AI assumptions not reviewed.

**Broken:** WIP at or beyond agreed cap or fixed fee with material scope outstanding. Multiple unacknowledged OOS items. Firm communicating overrun expectation. AFA no longer reflects the matter being delivered.

### Recommended action logic

| Status | Recommended action |
|--------|-------------------|
| On track | Continue. Schedule next health check at 80% of scope. |
| At risk (WIP) | Trigger milestone review. Apply 80%-of-cap clause if present. Require WIP projection from firm. |
| At risk (scope) | Invoke scope change protocol. Document OOS items. Agree fee amendment or scope reduction before further work proceeds. |
| At risk (AI) | Request AI efficiency disclosure. If AI savings are material, reopen fee discussion for current or next phase. |
| Broken | Escalate. Three options: (a) negotiate revised AFA for remaining scope; (b) convert to capped hourly for completion; (c) apply dispute resolution clause. |


## Mode 5: Scope Dispute Assessment

**Produce a Scope Dispute Assessment and Recommended Response immediately. Do not ask clarifying questions, offer a menu of deliverables, or provide analysis before producing the documents. Do not answer the user's question with a yes/no legal opinion — the Scope Dispute Assessment and Recommended Response are the answer. A user asking "is this OOS?", "is the firm's OOS claim valid?", "does our scope clause cover this work?", or "the firm is saying this is out of scope — are they right?" is requesting these two documents — fill in the templates below immediately. The documents are the response.**

### Output template: Scope Dispute Assessment

---
**SCOPE DISPUTE ASSESSMENT**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]
**Scope clause:** [Paste or summarise the operative scope language]
**Work claimed OOS:** [What the firm says is out of scope]
**Agreed fee:** [£X] / [Confirm]

**Preliminary view: [CLIENT HAS STRONGER ARGUMENT / FIRM HAS STRONGER ARGUMENT / GENUINELY AMBIGUOUS]**

**Scope clause analysis:**
| Factor | Assessment |
|--------|-----------|
| Natural and ordinary meaning of scope language | [What a reasonable party would understand the clause to cover] |
| Whether claimed OOS work was reasonably necessary to deliver the agreed scope | [Yes / No / Arguable] |
| Whether scope language was drafted by the firm or negotiated | [Firm-drafted / Negotiated / Unknown] |
| Contra proferentem applicability (English law) | [Applies if ambiguous and firm-drafted / Not applicable / Confirm jurisdiction] |

**Traction points for client position:**
| Point | Strength | Notes |
|-------|----------|-------|
| Course of dealing — OOS work delivered without contemporaneous objection | [H/M/L / Confirm] | [Any evidence firm delivered this work without raising OOS] |
| SPA / contract obligations — work triggered by completion mechanics | [H/M/L / N/A] | [Whether the work was legally required to complete the transaction] |
| Pre-engagement representations — pitch, scope call, engagement letter discussions | [H/M/L / Confirm] | [Any references to this work in pre-engagement materials] |
| Ambiguous drafting — no exclusion list, no phase definition, no scope schedule | [H/M/L] | [Whether the absence of exclusions supports a wider reading] |

**Items to contest (individually):**
| Work item claimed OOS | Client position | Firm position | Recommended stance |
|-----------------------|----------------|---------------|-------------------|
| [Item 1] | [In scope / arguable] | [OOS] | [Contest / Concede / Negotiate] |
| [Item 2] | [In scope / arguable] | [OOS] | [Contest / Concede / Negotiate] |
| [Item 3 — if any clearly separable] | [OOS] | [OOS] | [Concede early — preserves credibility on contested items] |

**Commercial exposure:**
- Estimated value of OOS claim: [£X] / [Confirm — request itemised breakdown from firm]
- Relationship risk: [High / Medium / Low]
- Recommended resolution path: [Contest specific items / Negotiate prospective fee for remaining work / Escalate]

---

### Output template: Recommended Response

---
**RECOMMENDED RESPONSE — SCOPE DISPUTE**
**Company:** [Company] | **Matter:** [Matter name] | **Date:** [Date]

**Immediate actions (before responding to the firm):**
| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | Pull the full engagement letter and any scope schedule or annexure | [Company] | Immediately |
| 2 | Identify all work delivered by the firm since [completion / relevant date] without OOS flag | [Company] | Within 48 hours |
| 3 | Map claimed OOS items against SPA completion obligations and conditions | [Company] | Within 48 hours |
| 4 | Request itemised breakdown from firm: what specific work, what hours, on what basis OOS | [Company] | Within 5 days |

**Posture until assessment complete:** Do not concede anything in writing. Do not dispute anything in writing. Holding position: *"We are reviewing the scope and will revert shortly."*

**Negotiating position once assessed:**
- **Contest:** [List items where client has traction — course of dealing, SPA obligations, contra proferentem]
- **Concede early:** [List items clearly outside any reasonable reading — conceding these early preserves credibility]
- **Negotiate prospectively:** [Agree a separate fee structure for remaining integration / post-completion work rather than litigating the past]

**What not to do:**
- Do not pay the OOS invoice without challenge — payment is an implied acceptance of the firm's scope reading
- Do not send a detailed written rebuttal before the assessment is complete — it reveals your position before you know theirs
- Do not let the relationship dynamic override the commercial analysis — a firm that raises OOS without contemporaneous flagging has chosen commercial confrontation

**GC briefing — one paragraph:**
[Company] is in a scope dispute with [Firm] over [brief description of claimed OOS work], estimated value [£X] / [Confirm]. The operative scope clause ([quote]) is [ambiguous / weighted toward firm / weighted toward client]. [Company]'s strongest arguments are [top 1–2 traction points]. Recommended position: [contest specific items / negotiate prospective fee / concede and close]. No written concession should be made until the itemised breakdown is received and reviewed.

---

### Scope dispute reference (apply inside templates above)

**The standard construction approach (English law):**
Courts and arbitrators interpreting professional services scope disputes apply: (1) ordinary and natural meaning of the language; (2) purpose of the engagement — was the work reasonably necessary to deliver what was agreed?; (3) course of dealing — did the firm deliver this work without objection?; (4) contra proferentem — ambiguity in a firm-drafted clause is construed against the firm.

**Firm-drafted ambiguity is the client's friend.** If the scope clause has no exclusion list, no phase definitions, and no scope schedule, the firm created that ambiguity. "All legal work required for the acquisition" with no carve-outs is not a tight scope clause — and the party that wrote it bears the cost of that vagueness.

**Course of dealing is often decisive.** If the firm delivered work without raising OOS contemporaneously, they have weakened or waived their position. The question is always: when did they first flag this? If it was weeks or months after the work was done, that timing is itself an argument.

**Contra proferentem in English law:** Where a contract term is ambiguous, it is construed against the party who drafted it. This applies to professional services engagement letters. If the firm drafted the scope clause and it is genuinely ambiguous, English law construes it against the firm.

**The commercial reality:** Professional services firms almost never litigate fee disputes with sophisticated in-house clients. The reputational and relationship cost is too high. The leverage points are: (a) the engagement letter language; (b) contemporaneous conduct; (c) the ongoing panel relationship. Press on specifics, not headlines. Ask the firm to defend each OOS item individually — the contestable items are usually a subset of what's initially claimed.

**What "integration" covers — the spectrum:**
- Mandatory regulatory notifications triggered by closing → hard to call OOS on any reasonable reading
- Contractual novation obligations under the SPA → arguable as completion work
- Employee consultation required by TUPE or equivalent → arguable depending on SPA terms
- Day-2 IT integration, commercial contract renegotiation, group restructuring → clearly post-acquisition on most readings
- Deferred consideration, earn-out mechanics, escrow management → arguable as acquisition obligations if documented in the SPA

## Domain Knowledge

### The case for AFAs — encode in every GC brief

Hourly billing misaligns firm and client incentives at a structural level. The firm earns more when the matter takes longer. The client pays more when the matter takes longer. AFAs do not eliminate this tension but they shift the risk allocation — the firm is paid for outcomes and scope, not time.

The practical case for moving off hourly:
- Price certainty allows accurate budget forecasting. Hourly billing makes accruals a guess.
- AFAs create a natural conversation about scope before work begins. Hourly billing defers that conversation until the invoice arrives.
- Fixed fees and phased fixed fees align firm behaviour with client outcomes — faster and more efficient delivery improves the firm's margin, not their invoice.
- "Our starting point is always an AFA" — Haleon General Counsel (quoted in PERSUIT research). This framing is appropriate at any maturity level.

### AI pricing in 2026 — what in-house teams need to know

This is the most significant near-term lever in outside counsel pricing and is underused.

- **The billing model problem:** Under hourly billing, AI tools reduce time, which reduces the invoice. Firms have no financial incentive to adopt AI at full speed — efficiency destroys revenue. Fixed fees solve this: efficiency improves margin, so firms have incentive to use AI.
- **The data gap:** Rate benchmarking data (PERSUIT's $20B in proposals, AmLaw 100 rate surveys) reflects historical hourly cost structures. AI-adjusted benchmarks are not yet standardised. In-house teams that ask the right questions now will have the best negotiating position as benchmarks evolve.
- **The disclosure question:** 71% of in-house teams expect AI use by outside counsel. Only 6% of AI-driven efficiency savings are currently passed to clients (Axiom 2025). The commercial question is not whether the firm uses AI — it is whether the fee reflects it.
- **Practical leverage:** Ask any firm proposing a fixed fee to disclose: (1) which tasks in the estimate are AI-assisted; (2) what the AI-adjusted time estimate is for those tasks; (3) how this compares to the equivalent non-AI estimate from a prior cycle.

### Rate benchmarking context (UK default)

- Top 100 firm average rate increase: +10% in 2024 (more than double 2023 increase)
- Top 50 firms: +12.1% in 2024
- Partners in top 25 global firms: £1,400–£1,680/hour for M&A work in London
- Senior partner rates approaching £2,500/hour in top-tier global firms
- 83% of proposals on PERSUIT (representing $20B in proposal value) use value-based pricing
- Goodwin Procter first major firm to adopt PERSUIT fixed-fee benchmarking globally (December 2025)

**US benchmarks:** $1,680/hour (M&A partners, top 25 firms); rate increases averaging 8–10% across AmLaw 100.

**Australian benchmarks:** Adapt from PERSUIT APAC data and local market intelligence — rate levels materially lower than UK/US; AFA adoption slower but growing.

### Named firms rule

Named firms are permitted in internal documents and chat responses where they help the user. Named firms are not included in external-facing documents distributed to firms. Use [Firm] placeholder in all external templates (Firm-Facing Agenda, engagement letter templates). This is a liability and dating risk management rule — firm names in documents create a paper trail that may not reflect the current relationship.

---

## Cross-Skill Connections

| This skill | Connected skill | Connection |
|------------|----------------|------------|
| Mode 1 (AFA Design) | **budget-and-fee-manager** (LPM Core) | AFA structure agreed here → phase-based budget built and WIP monitored in budget-and-fee-manager |
| Mode 1 (AFA Design) | **engagement-terms-billing-guidelines** (OCM Skill 1) | OCG sets AFA policy preference; this skill designs the specific arrangement for a matter |
| Mode 3 (Negotiation Brief) | **rfp-pitch-management** (OCM Skill 3) | Competitive fee proposals from RFP process anchor the negotiation |
| Mode 4 (Health Check) | **scope-change-controller** (LPM Core) | Scope drift identified in Mode 4 should be logged and controlled in scope-change-controller |
| All modes | **billing-cycle-manager** (LPM Core) | AFA structure determines the billing cadence; billing-cycle-manager executes it |

---

## M365 Connected Mode (Optional)

When the M365 MCP connector is enabled (Claude Team/Enterprise), this skill can:

- **Outlook:** Search for firm communications mentioning scope changes, "additional work," or overrun signals; pull original engagement letter and fee agreement for Mode 4 input
- **SharePoint/Teams:** Retrieve matter budget tracking data and WIP reports to populate Mode 4 health check; pull panel AFA programme data for Mode 3 negotiation context
- **E-billing integration (if available):** Import WIP-to-date figures directly into Mode 4 assessment rather than requiring manual input

Without the connector, provide the same information by pasting email text, billing data, or describing the current delivery status directly.

---

## Time-Sensitive Assumptions

The following content encodes market data that will become stale:
- Rate benchmarks (UK, US, Australian) — update with current year AmLaw, PERSUIT, and Brightflag reports
- AI adoption statistics (71% of in-house teams expect AI use; 6% pass-through rate) — sourced from Axiom 2025; verify against current year data
- PERSUIT platform data ($20B proposal value; 83% value-based pricing) — verify against current PERSUIT publications

Flag these sections for review at the next skills maintenance cycle.
