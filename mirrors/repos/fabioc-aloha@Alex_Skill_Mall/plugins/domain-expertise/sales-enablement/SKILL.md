---
type: skill
lifecycle: stable
inheritance: inheritable
name: sales-enablement
description: Sales methodology, pipeline management, negotiation frameworks, and customer engagement patterns.
tier: extended
applyTo: '**/*sales*,**/*enablement*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Sales Enablement Skill


> Sales methodology, pipeline management, negotiation frameworks, and customer engagement patterns.

## Core Principle

Selling is structured problem-solving. You diagnose a customer's pain, match it to a solution, and guide the decision. Process beats personality.

## Sales Methodologies

### MEDDPICC (Enterprise/Complex Sales)

| Letter | Stands For | Question |
|--------|-----------|----------|
| **M** | Metrics | What measurable outcome does the buyer need? |
| **E** | Economic Buyer | Who has budget authority? |
| **D** | Decision Criteria | What factors drive the decision? |
| **D** | Decision Process | What are the steps to close? |
| **P** | Paper Process | What legal/procurement steps are required? |
| **I** | Implicate Pain | What happens if they do nothing? |
| **C** | Champion | Who inside the account is actively selling for you? |
| **C** | Competition | Who else is being evaluated? |

### SPIN Selling (Consultative)

| Phase | Question Type | Example |
|-------|-------------|---------|
| **S** — Situation | Understand current state | "How do you currently handle X?" |
| **P** — Problem | Surface pain points | "What challenges does that create?" |
| **I** — Implication | Expand the pain | "What impact does that have on Y?" |
| **N** — Need-Payoff | Let buyer articulate value | "How would solving that help?" |

### Challenger Sale

1. **Teach**: Provide insights the buyer didn't know
2. **Tailor**: Customize the message to stakeholder type
3. **Take control**: Guide the buying process, push back constructively

### Solution Selling (Simpler Deals)

| Step | Action |
|------|--------|
| 1 | Identify the pain |
| 2 | Qualify the opportunity |
| 3 | Map solution to pain |
| 4 | Demonstrate value |
| 5 | Negotiate and close |

## Pipeline Management

### Deal Tracker (MEDDPICC)

```json
{
  "deal": "Acme Corp - Platform Expansion",
  "value": 250000,
  "stage": "negotiation",
  "close_date": "2026-06-30",
  "meddpicc": {
    "metrics": { "score": 3, "note": "10% efficiency gain target confirmed" },
    "economic_buyer": { "score": 3, "contact": "CFO Jane Smith" },
    "decision_criteria": { "score": 2, "note": "Waiting on technical eval results" },
    "decision_process": { "score": 3, "note": "Procurement involved, legal review next" },
    "paper_process": { "score": 2, "note": "MSA required, 2-week legal cycle" },
    "implicate_pain": { "score": 3, "note": "$500K annual loss without solution" },
    "champion": { "score": 3, "contact": "VP Ops Mike Chen" },
    "competition": { "score": 2, "note": "Competitor X shortlisted" }
  },
  "total_score": 21,
  "next_step": "Send ROI calculator to CFO before 4/20"
}
```

### Pipeline Stages

| Stage | Definition | Exit Criteria |
|-------|-----------|---------------|
| **Prospecting** | Initial outreach, cold/warm | Meeting confirmed |
| **Discovery** | Needs assessment, pain qualification | Pain confirmed, budget discussed |
| **Proposal** | Solution presented, pricing shared | Decision criteria agreed |
| **Negotiation** | Terms, pricing, legal | Verbal commitment |
| **Closed Won** | Signed contract | Revenue booked |
| **Closed Lost** | Deal lost | Loss reason documented |

### Pipeline Metrics

| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| Win Rate | Closed Won / Total Opportunities | 20–35% (enterprise) |
| Average Deal Size | Total Revenue / Deals Closed | Varies by segment |
| Sales Cycle Length | Avg days from creation to close | Track trend, not absolutes |
| Pipeline Coverage | Pipeline Value / Quota | 3–4× for enterprise |
| Stage Conversion | Opportunities advancing / Total in stage | Monitor each stage |

### Forecasting Categories

| Category | Definition | Commit Level |
|----------|-----------|-------------|
| **Commit** | High confidence, expected this period | 90%+ probability |
| **Best Case** | Could close if things go well | 60–89% |
| **Pipeline** | Active but early stage | 10–59% |
| **Upside** | Stretch opportunities | <10% |

## Prospecting & Outreach

### Cold Outreach Framework

**Email structure (3-sentence max):**

1. Relevant observation about their business (shows research)
2. One sentence connecting their challenge to your solution
3. Low-friction ask (15-minute call, not a demo)

### Qualification Framework (BANT)

| Criterion | Question | Disqualifier |
|-----------|----------|-------------|
| **B** — Budget | Is there budget allocated? | No budget and no path to budget |
| **A** — Authority | Can this person make or influence the decision? | No access to decision maker |
| **N** — Need | Is the pain real and urgent? | Nice-to-have, no urgency |
| **T** — Timeline | When do they need to decide? | No timeline = no deal |

## Negotiation Frameworks

### Principled Negotiation (Fisher & Ury)

1. **Separate people from the problem** — Address emotions, maintain relationships
2. **Focus on interests, not positions** — Ask why, not just what
3. **Invent options for mutual gain** — Expand the pie before dividing
4. **Use objective criteria** — Industry benchmarks, precedents, standards

### Common Negotiation Tactics (and Counters)

| Tactic | Description | Counter |
|--------|-----------|---------|
| **Anchoring** | Extreme first offer | Re-anchor with data |
| **Flinch** | Physical reaction to price | Hold steady, stay silent |
| **Nibbling** | Adding small asks after agreement | "That would require re-opening terms" |
| **Good cop/bad cop** | Paired pressure | Address the issue, ignore the dynamic |
| **Deadline pressure** | "Offer expires Friday" | Verify deadline is real |

### Discount Discipline

- **Never discount without getting something**: Shorter term, larger volume, case study, referral
- **Discount from value, not from list**: Show the full value before any reduction
- **Document the justification**: Every discount needs a recorded business reason

## Customer Success Handoff

### Post-Sale Transition

| Step | Owner | Deliverable |
|------|-------|-----------|
| 1 | Sales | Handoff document (pain, solution, stakeholders, commitments) |
| 2 | CS/AM | Welcome call within 48 hours |
| 3 | Both | Joint account plan (90-day) |
| 4 | CS/AM | Onboarding kickoff |

## Real Estate Sales Patterns

### Property Presentation

- **CMA (Comparative Market Analysis)**: 3–5 comparable recent sales, adjusted for features
- **Days on Market (DOM)**: Track vs market average — high DOM signals pricing issue
- **Absorption Rate**: Monthly sales / Available inventory — measures market speed

### Client Communication

- **Buyer's journey**: Discovery → Pre-approval → Viewings → Offer → Inspection → Close
- **Seller's journey**: Valuation → Staging → Listing → Showings → Offers → Negotiation → Close
- **Follow-up cadence**: 24h post-showing, 72h if no response, 2-week check-in for nurture

## Anti-Patterns

- Pitching features before understanding the problem
- Discounting to win without addressing the real objection
- Forecasting based on hope instead of evidence
- Skipping discovery to rush to demo
- Single-threading (only one contact in the account)
- Not documenting loss reasons (repeats same mistakes)
