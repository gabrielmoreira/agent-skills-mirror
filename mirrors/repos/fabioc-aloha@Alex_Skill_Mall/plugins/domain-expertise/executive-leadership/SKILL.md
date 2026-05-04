---
type: skill
lifecycle: stable
inheritance: inheritable
name: agent-protocol
description: Inter-agent communication protocol for C-suite agent teams. Defines invocation syntax, loop prevention, isolation rules, and response formats. Use when C-suite agents need to query each other, coor...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Inter-Agent Protocol

How C-suite agents talk to each other. Rules that prevent chaos, loops, and circular reasoning.

## Keywords
agent protocol, inter-agent communication, agent invocation, agent orchestration, multi-agent, c-suite coordination, agent chain, loop prevention, agent isolation, board meeting protocol

## Invocation Syntax

Any agent can query another using:

```
[INVOKE:role|question]
```

**Examples:**
```
[INVOKE:cfo|What's the burn rate impact of hiring 5 engineers in Q3?]
[INVOKE:cto|Can we realistically ship this feature by end of quarter?]
[INVOKE:chro|What's our typical time-to-hire for senior engineers?]
[INVOKE:cro|What does our pipeline look like for the next 90 days?]
```

**Valid roles:** `ceo`, `cfo`, `cro`, `cmo`, `cpo`, `cto`, `chro`, `coo`, `ciso`

## Response Format

Invoked agents respond using this structure:

```
[RESPONSE:role]
Key finding: [one line — the actual answer]
Supporting data:
  - [data point 1]
  - [data point 2]
  - [data point 3 — optional]
Confidence: [high | medium | low]
Caveat: [one line — what could make this wrong]
[/RESPONSE]
```

**Example:**
```
[RESPONSE:cfo]
Key finding: Hiring 5 engineers in Q3 extends runway from 14 to 9 months at current burn.
Supporting data:
  - Current monthly burn: $280K → increases to ~$380K (+$100K fully loaded)
  - ARR needed to offset: ~$1.2M additional within 12 months
  - Current pipeline covers 60% of that target
Confidence: medium
Caveat: Assumes 3-month ramp and no change in revenue trajectory.
[/RESPONSE]
```

## Loop Prevention (Hard Rules)

These rules are enforced unconditionally. No exceptions.

### Rule 1: No Self-Invocation
An agent cannot invoke itself.
```
❌ CFO → [INVOKE:cfo|...] — BLOCKED
```

### Rule 2: Maximum Depth = 2
Chains can go A→B→C. The third hop is blocked.
```
✅ CRO → CFO → COO (depth 2)
❌ CRO → CFO → COO → CHRO (depth 3 — BLOCKED)
```

### Rule 3: No Circular Calls
If agent A called agent B, agent B cannot call agent A in the same chain.
```
✅ CRO → CFO → CMO
❌ CRO → CFO → CRO (circular — BLOCKED)
```

### Rule 4: Chain Tracking
Each invocation carries its call chain. Format:
```
[CHAIN: cro → cfo → coo]
```
Agents check this chain before responding with another invocation.

**When blocked:** Return this instead of invoking:
```
[BLOCKED: cannot invoke cfo — circular call detected in chain cro→cfo]
State assumption used instead: [explicit assumption the agent is making]
```

## Isolation Rules

### Board Meeting Phase 2 (Independent Analysis)
**NO invocations allowed.** Each role forms independent views before cross-pollination.
- Reason: prevent anchoring and groupthink
- Duration: entire Phase 2 analysis period
- If an agent needs data from another role: state explicit assumption, flag it with `[ASSUMPTION: ...]`

### Board Meeting Phase 3 (Critic Role)
Executive Mentor can **reference** other roles' outputs but **cannot invoke** them.
- Reason: critique must be independent of new data requests
- Allowed: "The CFO's projection assumes X, which contradicts the CRO's pipeline data"
- Not allowed: `[INVOKE:cfo|...]` during critique phase

### Outside Board Meetings
Invocations are allowed freely, subject to loop prevention rules above.

## When to Invoke vs When to Assume

**Invoke when:**
- The question requires domain-specific data you don't have
- An error here would materially change the recommendation
- The question is cross-functional by nature (e.g., hiring impact on both budget and capacity)

**Assume when:**
- The data is directionally clear and precision isn't critical
- You're in Phase 2 isolation (always assume, never invoke)
- The chain is already at depth 2
- The question is minor compared to your main analysis

**When assuming, always state it:**
```
[ASSUMPTION: runway ~12 months based on typical Series A burn profile — not verified with CFO]
```

## Conflict Resolution

When two invoked agents give conflicting answers:

1. **Flag the conflict explicitly:**
   ```
   [CONFLICT: CFO projects 14-month runway; CRO expects pipeline to close 80% → implies 18+ months]
   ```
2. **State the resolution approach:**
   - Conservative: use the worse case
   - Probabilistic: weight by confidence scores
   - Escalate: flag for human decision
3. **Never silently pick one** — surface the conflict to the user.

## Broadcast Pattern (Crisis / CEO)

CEO can broadcast to all roles simultaneously:
```
[BROADCAST:all|What's the impact if we miss the fundraise?]
```

Responses come back independently (no agent sees another's response before forming its own). Aggregate after all respond.

## Quick Reference

| Rule | Behavior |
|------|----------|
| Self-invoke | ❌ Always blocked |
| Depth > 2 | ❌ Blocked, state assumption |
| Circular | ❌ Blocked, state assumption |
| Phase 2 isolation | ❌ No invocations |
| Phase 3 critique | ❌ Reference only, no invoke |
| Conflict | ✅ Surface it, don't hide it |
| Assumption | ✅ Always explicit with `[ASSUMPTION: ...]` |

## Internal Quality Loop (before anything reaches the founder)

No role presents to the founder without passing through this verification loop. The founder sees polished, verified output — not first drafts.

### Step 1: Self-Verification (every role, every time)

Before presenting, every role runs this internal checklist:

```
SELF-VERIFY CHECKLIST:
□ Source Attribution — Where did each data point come from?
  ✅ "ARR is $2.1M (from CRO pipeline report, Q4 actuals)"
  ❌ "ARR is around $2M" (no source, vague)

□ Assumption Audit — What am I assuming vs what I verified?
  Tag every assumption: [VERIFIED: checked against data] or [ASSUMED: not verified]
  If >50% of findings are ASSUMED → flag low confidence

□ Confidence Score — How sure am I on each finding?
  🟢 High: verified data, established pattern, multiple sources
  🟡 Medium: single source, reasonable inference, some uncertainty
  🔴 Low: assumption-based, limited data, first-time analysis

□ Contradiction Check — Does this conflict with known context?
  Check against company-context.md and recent decisions in decision-log
  If it contradicts a past decision → flag explicitly

□ "So What?" Test — Does every finding have a business consequence?
  If you can't answer "so what?" in one sentence → cut it
```

### Step 2: Peer Verification (cross-functional validation)

When a recommendation impacts another role's domain, that role validates BEFORE presenting.

| If your recommendation involves... | Validate with... | They check... |
|-------------------------------------|-------------------|---------------|
| Financial numbers or budget | CFO | Math, runway impact, budget reality |
| Revenue projections | CRO | Pipeline backing, historical accuracy |
| Headcount or hiring | CHRO | Market reality, comp feasibility, timeline |
| Technical feasibility or timeline | CTO | Engineering capacity, technical debt load |
| Operational process changes | COO | Capacity, dependencies, scaling impact |
| Customer-facing changes | CRO + CPO | Churn risk, product roadmap conflict |
| Security or compliance claims | CISO | Actual posture, regulation requirements |
| Market or positioning claims | CMO | Data backing, competitive reality |

**Peer validation format:**
```
[PEER-VERIFY:cfo]
Validated: ✅ Burn rate calculation correct
Adjusted: ⚠️ Hiring timeline should be Q3 not Q2 (budget constraint)
Flagged: 🔴 Missing equity cost in total comp projection
[/PEER-VERIFY]
```

**Skip peer verification when:**
- Single-domain question with no cross-functional impact
- Time-sensitive proactive alert (send alert, verify after)
- Founder explicitly asked for a quick take

### Step 3: Critic Pre-Screen (high-stakes decisions only)

For decisions that are **irreversible, high-cost, or bet-the-company**, the Executive Mentor pre-screens before the founder sees it.

**Triggers for pre-screen:**
- Involves spending > 20% of remaining runway
- Affects >30% of the team (layoffs, reorg)
- Changes company strategy or direction
- Involves external commitments (fundraising terms, partnerships, M&A)
- Any recommendation where all roles agree (suspicious consensus)

**Pre-screen output:**
```
[CRITIC-SCREEN]
Weakest point: [The single biggest vulnerability in this recommendation]
Missing perspective: [What nobody considered]
If wrong, the cost is: [Quantified downside]
Proceed: ✅ With noted risks | ⚠️ After addressing [specific gap] | 🔴 Rethink
[/CRITIC-SCREEN]
```

### Step 4: Course Correction (after founder feedback)

The loop doesn't end at delivery. After the founder responds:

```
FOUNDER FEEDBACK LOOP:
1. Founder approves → log decision (Layer 2), assign actions
2. Founder modifies → update analysis with corrections, re-verify changed parts
3. Founder rejects → log rejection with DO_NOT_RESURFACE, understand WHY
4. Founder asks follow-up → deepen analysis on specific point, re-verify

POST-DECISION REVIEW (30/60/90 days):
- Was the recommendation correct?
- What did we miss?
- Update company-context.md with what we learned
- If wrong → document the lesson, adjust future analysis
```

### Verification Level by Stakes

| Stakes | Self-Verify | Peer-Verify | Critic Pre-Screen |
|--------|-------------|-------------|-------------------|
| Low (informational) | ✅ Required | ❌ Skip | ❌ Skip |
| Medium (operational) | ✅ Required | ✅ Required | ❌ Skip |
| High (strategic) | ✅ Required | ✅ Required | ✅ Required |
| Critical (irreversible) | ✅ Required | ✅ Required | ✅ Required + board meeting |

### What Changes in the Output Format

The verified output adds confidence and source information:

```
BOTTOM LINE
[Answer] — Confidence: 🟢 High

WHAT
• [Finding 1] [VERIFIED: Q4 actuals] 🟢
• [Finding 2] [VERIFIED: CRO pipeline data] 🟢  
• [Finding 3] [ASSUMED: based on industry benchmarks] 🟡

PEER-VERIFIED BY: CFO (math ✅), CTO (timeline ⚠️ adjusted to Q3)
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-1
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: board-deck-builder
description: Assembles comprehensive board and investor update decks by pulling perspectives from all C-suite roles. Use when preparing board meetings, investor updates, quarterly business reviews, or fundraisi...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Board Deck Builder

Build board decks that tell a story — not just show data. Every section has an owner, a narrative, and a "so what."

## Keywords
board deck, investor update, board meeting, board pack, investor relations, quarterly review, board presentation, fundraising deck, investor deck, board narrative, QBR, quarterly business review

## Quick Start

```
/board-deck [quarterly|monthly|fundraising] [stage: seed|seriesA|seriesB]
```

Provide available metrics. The builder fills gaps with explicit placeholders — never invents numbers.

## Deck Structure (Standard Order)

Every section follows: **Headline → Data → Narrative → Ask/Next**

### 1. Executive Summary (CEO)
**3 sentences. No more.**
- Sentence 1: State of the business (where we are)
- Sentence 2: Biggest thing that happened this period
- Sentence 3: Where we're going next quarter

*Bad:* "We had a good quarter with lots of progress across all areas."
*Good:* "We closed Q3 at $2.4M ARR (+22% QoQ), signed our largest enterprise contract, and enter Q4 with 14-month runway. The strategic shift to mid-market is working — ACV up 40% and sales cycle down 3 weeks. Q4 priority: close the $3M Series A and hit $2.8M ARR."

### 2. Key Metrics Dashboard (COO)
**6-8 metrics max. Use a table.**

| Metric | This Period | Last Period | Target | Status |
|--------|-------------|-------------|--------|--------|
| ARR | $2.4M | $1.97M | $2.3M | ✅ |
| MoM growth | 8.1% | 7.2% | 7.5% | ✅ |
| Burn multiple | 1.8x | 2.1x | <2x | ✅ |
| NRR | 112% | 108% | >110% | ✅ |
| CAC payback | 11 months | 14 months | <12 months | ✅ |
| Headcount | 24 | 21 | 25 | 🟡 |

Pick metrics the board actually tracks. Swap out anything they've said they don't care about.

### 3. Financial Update (CFO)
- P&L summary: Revenue, COGS, Gross margin, OpEx, Net burn
- Cash position and runway (months)
- Burn multiple trend (3-quarter view)
- Variance to plan (what was different and why)
- Forecast update for next quarter

**One sentence on each variance.** Boards hate "revenue was below target" with no explanation. Say why.

### 4. Revenue & Pipeline (CRO)
- ARR waterfall: starting → new → expansion → churn → ending
- NRR and logo churn rates
- Pipeline by stage (in $, not just count)
- Forecast: next quarter with confidence level
- Top 3 deals: name/amount/close date/risk

**The forecast must have a confidence level.** "We expect $2.8M" is weak. "High confidence $2.6M, upside to $2.9M if two late-stage deals close" is useful.

### 5. Product Update (CPO)
- Shipped this quarter: 3-5 bullets, user impact for each
- Shipping next quarter: 3-5 bullets with target dates
- PMF signal: NPS trend, DAU/MAU ratio, feature adoption
- One key learning from customer research

**No feature lists.** Only features with evidence of user impact.

### 6. Growth & Marketing (CMO)
- CAC by channel (table)
- Pipeline contribution by channel ($)
- Brand/awareness metrics relevant to stage (traffic, share of voice)
- What's working, what's being cut, what's being tested

### 7. Engineering & Technical (CTO)
- Delivery velocity trend (last 4 quarters)
- Tech debt ratio and plan
- Infrastructure: uptime, incidents, cost trend
- Security posture (one line, flag anything pending)

**Keep this short unless there's a material issue.** Boards don't need sprint details.

### 8. Team & People (CHRO)
- Headcount: actual vs plan
- Hiring: offers out, pipeline, time-to-fill trend
- Attrition: regrettable vs non-regrettable
- Engagement: last survey score, trend
- Key hires this quarter, key open roles

### 9. Risk & Security (CISO)
- Security posture: status of critical controls
- Compliance: certifications in progress, deadlines
- Incidents this quarter (if any): impact, resolution, prevention
- Top 3 risks and mitigation status

### 10. Strategic Outlook (CEO)
- Next quarter priorities: 3-5 items, ranked
- Key decisions needed from the board
- Asks: budget, introductions, advice, votes

**The "asks" slide is the most important.** Be specific. "We'd like 3 warm introductions to CFOs at Series B companies" beats "any help would be appreciated."

### 11. Appendix
- Detailed financial model
- Full pipeline data
- Cohort retention charts
- Customer case studies
- Detailed headcount breakdown

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-3
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Delivering Bad News

Never bury it. Boards find out eventually. Finding out late makes it worse.

**Framework:**
1. **State it plainly** — "We missed Q3 ARR target by $300K (12% gap)"
2. **Own the cause** — "Primary driver was longer-than-expected sales cycle in enterprise segment"
3. **Show you understand it** — "We analyzed 8 lost/stalled deals; the pattern is X"
4. **Present the fix** — "We've made 3 changes: [specific, dated changes]"
5. **Update the forecast** — "Revised Q4 target is $2.6M; here's the bottom-up build"

**What NOT to do:**
- Don't lead with good news to soften bad news — boards notice and distrust the framing
- Don't explain without owning — "market conditions" is not a cause, it's a context
- Don't present a fix without data behind it
- Don't show a revised forecast without showing your assumptions

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-4
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Cadence Notes

**Quarterly (standard):** Full deck, all sections, 20-30 slides. Sent 48 hours in advance.
**Monthly (for early-stage):** Condensed — metrics dashboard, financials, pipeline, top risks. 8-12 slides.
**Fundraising:** Opens with market/vision, closes with ask. See `references/deck-frameworks.md` for Sequoia format.

## References
- `references/deck-frameworks.md` — SaaS board pack format, Sequoia structure, investor tailoring
- `templates/board-deck-template.md` — fill-in template for complete board decks


---
type: skill
lifecycle: stable
inheritance: inheritable
name: board-meeting
description: Multi-agent board meeting protocol for strategic decisions. Runs a structured 6-phase deliberation: context loading, independent C-suite contributions (isolated, no cross-pollination), critic analy...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Board Meeting Protocol

Structured multi-agent deliberation that prevents groupthink, captures minority views, and produces clean, actionable decisions.

## Keywords
board meeting, executive deliberation, strategic decision, C-suite, multi-agent, /cs:board, founder review, decision extraction, independent perspectives

## Invoke
`/cs:board [topic]` — e.g. `/cs:board Should we expand to Spain in Q3?`

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-6
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### PHASE 2: Independent Contributions (ISOLATED)

**No cross-pollination. Each agent runs before seeing others' outputs.**

Order: Research (if needed) → CMO → CFO → CEO → CTO → COO → CHRO → CRO → CISO → CPO

**Reasoning techniques:** CEO: Tree of Thought (3 futures) | CFO: Chain of Thought (show the math) | CMO: Recursion of Thought (draft→critique→refine) | CPO: First Principles | CRO: Chain of Thought (pipeline math) | COO: Step by Step (process map) | CTO: ReAct (research→analyze→act) | CISO: Risk-Based (P×I) | CHRO: Empathy + Data

**Contribution format (max 5 key points, self-verified):**
```
## [ROLE] — [DATE]

Key points (max 5):
• [Finding] — [VERIFIED/ASSUMED] — 🟢/🟡/🔴
• [Finding] — [VERIFIED/ASSUMED] — 🟢/🟡/🔴

Recommendation: [clear position]
Confidence: High / Medium / Low
Source: [where the data came from]
What would change my mind: [specific condition]
```

Each agent self-verifies before contributing: source attribution, assumption audit, confidence scoring. No untagged claims.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-7
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### PHASE 4: Synthesis
Chief of Staff delivers using the **Board Meeting Output** format (defined in `agent-protocol/SKILL.md`):
- Decision Required (one sentence)
- Perspectives (one line per contributing role)
- Where They Agree / Where They Disagree
- Critic's View (the uncomfortable truth)
- Recommended Decision + Action Items (owners, deadlines)
- Your Call (options if founder disagrees)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-8
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### PHASE 6: Decision Extraction
After founder approval:
- **Layer 1:** Write full transcript → `memory/board-meetings/YYYY-MM-DD-raw.md`
- **Layer 2:** Append approved decisions → `memory/board-meetings/decisions.md`
- Mark rejected proposals `[DO_NOT_RESURFACE]`
- Confirm to founder with count of decisions logged, actions tracked, flags added

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-9
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Failure Mode Quick Reference
| Failure | Fix |
|---------|-----|
| Groupthink (all agree) | Re-run Phase 2 isolated; force "strongest argument against" |
| Analysis paralysis | Cap at 5 points; force recommendation even with Low confidence |
| Bikeshedding | Log as async action item; return to main agenda |
| Role bleed (CFO making product calls) | Critic flags; exclude from synthesis |
| Layer contamination | Phase 1 loads decisions.md only — hard rule |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-10
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: c-level-advisor
description: 10 C-level advisory agent skills and plugins for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. CEO, CTO, COO, CPO, CMO, CFO, CRO, CISO, CHRO, Executive Mentor. Multi-role board meetings, strate...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# C-Level Advisory Ecosystem

A complete virtual board of directors for founders and executives.

## Quick Start

```
1. Run /cs:setup → creates company-context.md (all agents read this)
   ✓ Verify company-context.md was created and contains your company name,
     stage, and core metrics before proceeding.
2. Ask any strategic question → Chief of Staff routes to the right role
3. For big decisions → /cs:board triggers a multi-role board meeting
   ✓ Confirm at least 3 roles have weighed in before accepting a conclusion.
```

### Commands

#### `/cs:setup` — Onboarding Questionnaire

Walks through the following prompts and writes `company-context.md` to the project root. Run once per company or when context changes significantly.

```
Q1. What is your company name and one-line description?
Q2. What stage are you at? (Idea / Pre-seed / Seed / Series A / Series B+)
Q3. What is your current ARR (or MRR) and runway in months?
Q4. What is your team size and structure?
Q5. What industry and customer segment do you serve?
Q6. What are your top 3 priorities for the next 90 days?
Q7. What is your biggest current risk or blocker?
```

After collecting answers, the agent writes structured output:

```markdown
# Company Context
- Name: <answer>
- Stage: <answer>
- Industry: <answer>
- Team size: <answer>
- Key metrics: <ARR/MRR, growth rate, runway>
- Top priorities: <answer>
- Key risks: <answer>
```

#### `/cs:board` — Full Board Meeting

Convenes all relevant executive roles in three phases:

```
Phase 1 — Framing:   Chief of Staff states the decision and success criteria.
Phase 2 — Isolation: Each role produces independent analysis (no cross-talk).
Phase 3 — Debate:    Roles surface conflicts, stress-test assumptions, align on
                     a recommendation. Dissenting views are preserved in the log.
```

Use for high-stakes or cross-functional decisions. Confirm at least 3 roles have weighed in before accepting a conclusion.

### Chief of Staff Routing Matrix

When a question arrives without a role prefix, the Chief of Staff maps it to the appropriate executive using these primary signals:

| Topic Signal | Primary Role | Supporting Roles |
|---|---|---|
| Fundraising, valuation, burn | CFO | CEO, CRO |
| Architecture, build vs. buy, tech debt | CTO | CPO, CISO |
| Hiring, culture, performance | CHRO | CEO, Executive Mentor |
| GTM, demand gen, positioning | CMO | CRO, CPO |
| Revenue, pipeline, sales motion | CRO | CMO, CFO |
| Security, compliance, risk | CISO | CTO, CFO |
| Product roadmap, prioritisation | CPO | CTO, CMO |
| Ops, process, scaling | COO | CFO, CHRO |
| Vision, strategy, investor relations | CEO | Executive Mentor |
| Career, founder psychology, leadership | Executive Mentor | CEO, CHRO |
| Multi-domain / unclear | Chief of Staff convenes board | All relevant roles |

### Invoking a Specific Role Directly

To bypass Chief of Staff routing and address one executive directly, prefix your question with the role name:

```
CFO: What is our optimal burn rate heading into a Series A?
CTO: Should we rebuild our auth layer in-house or buy a solution?
CHRO: How do we design a performance review process for a 15-person team?
```

The Chief of Staff still logs the exchange; only routing is skipped.

### Example: Strategic Question

**Input:** "Should we raise a Series A now or extend runway and grow ARR first?"

**Output format:**
- **Bottom Line:** Extend runway 6 months; raise at $2M ARR for better terms.
- **What:** Current $800K ARR is below the threshold most Series A investors benchmark.
- **Why:** Raising now increases dilution risk; 6-month extension is achievable with current burn.
- **How to Act:** Cut 2 low-ROI channels, hit $2M ARR, then run a 6-week fundraise sprint.
- **Your Decision:** Proceed with extension / Raise now anyway (choose one).

### Example: company-context.md (after /cs:setup)

```markdown
# Company Context
- Name: Acme Inc.
- Stage: Seed ($800K ARR)
- Industry: B2B SaaS
- Team size: 12
- Key metrics: 15% MoM growth, 18-month runway
- Top priorities: Series A readiness, enterprise GTM
```

## What's Included

### 10 C-Suite Roles
CEO, CTO, COO, CPO, CMO, CFO, CRO, CISO, CHRO, Executive Mentor

### 6 Orchestration Skills
Founder Onboard, Chief of Staff (router), Board Meeting, Decision Logger, Agent Protocol, Context Engine

### 6 Cross-Cutting Capabilities
Board Deck Builder, Scenario War Room, Competitive Intel, Org Health Diagnostic, M&A Playbook, International Expansion

### 6 Culture & Collaboration
Culture Architect, Company OS, Founder Coach, Strategic Alignment, Change Management, Internal Narrative

## Key Features

- **Internal Quality Loop:** Self-verify → peer-verify → critic pre-screen → present
- **Two-Layer Memory:** Raw transcripts + approved decisions only (prevents hallucinated consensus)
- **Board Meeting Isolation:** Phase 2 independent analysis before cross-examination
- **Proactive Triggers:** Context-driven early warnings without being asked
- **Structured Output:** Bottom Line → What → Why → How to Act → Your Decision
- **25 Python Tools:** All stdlib-only, CLI-first, JSON output, zero dependencies

## See Also

- `CLAUDE.md` — full architecture diagram and integration guide
- `agent-protocol/SKILL.md` — communication standard and quality loop details
- `chief-of-staff/SKILL.md` — routing matrix for all 28 skills


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ceo-advisor
description: Executive leadership guidance for strategic decision-making, organizational development, and stakeholder management. Use when planning strategy, preparing board presentations, managing investors, d...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CEO Advisor

Strategic leadership frameworks for vision, fundraising, board management, culture, and stakeholder alignment.

## Keywords
CEO, chief executive officer, strategy, strategic planning, fundraising, board management, investor relations, culture, organizational leadership, vision, mission, stakeholder management, capital allocation, crisis management, succession planning

## Quick Start

```bash
python scripts/strategy_analyzer.py          # Analyze strategic options with weighted scoring
python scripts/financial_scenario_analyzer.py # Model financial scenarios (base/bull/bear)
```

## Core Responsibilities

### 1. Vision & Strategy
Set the direction. Not a 50-page document — a clear, compelling answer to "Where are we going and why?"

**Strategic planning cycle:**
- Annual: 3-year vision refresh + 1-year strategic plan
- Quarterly: OKR setting with C-suite (COO drives execution)
- Monthly: strategy health check — are we still on track?

**Stage-adaptive time horizons:**
- Seed/Pre-PMF: 3-month / 6-month / 12-month
- Series A: 6-month / 1-year / 2-year
- Series B+: 1-year / 3-year / 5-year

See `references/executive_decision_framework.md` for the full Go/No-Go framework, crisis playbook, and capital allocation model.

### 2. Capital & Resource Management
You're the chief allocator. Every dollar, every person, every hour of engineering time is a bet.

**Capital allocation priorities:**
1. Keep the lights on (operations, must-haves)
2. Protect the core (retention, quality, security)
3. Grow the core (expansion of what works)
4. Fund new bets (innovation, new products/markets)

**Fundraising:** Know your numbers cold. Timing matters more than valuation. See `references/board_governance_investor_relations.md`.

### 3. Stakeholder Leadership
You serve multiple masters. Priority order:
1. Customers (they pay the bills)
2. Team (they build the product)
3. Board/Investors (they fund the mission)
4. Partners (they extend your reach)

### 4. Organizational Culture
Culture is what people do when you're not in the room. It's your job to define it, model it, and enforce it.

See `references/leadership_organizational_culture.md` for culture development frameworks and the CEO learning agenda. Also see `culture-architect/` for the operational culture toolkit.

### 5. Board & Investor Management
Your board can be your greatest asset or your biggest liability. The difference is how you manage them.

See `references/board_governance_investor_relations.md` for board meeting prep, investor communication cadence, and managing difficult directors. Also see `board-deck-builder/` for assembling the actual board deck.

## Key Questions a CEO Asks

- "Can every person in this company explain our strategy in one sentence?"
- "What's the one thing that, if it goes wrong, kills us?"
- "Am I spending my time on the highest-leverage activity right now?"
- "What decision am I avoiding? Why?"
- "If we could only do one thing this quarter, what would it be?"
- "Do our investors and our team hear the same story from me?"
- "Who would replace me if I got hit by a bus tomorrow?"

## CEO Metrics Dashboard

| Category | Metric | Target | Frequency |
|----------|--------|--------|-----------|
| **Strategy** | Annual goals hit rate | > 70% | Quarterly |
| **Revenue** | ARR growth rate | Stage-dependent | Monthly |
| **Capital** | Months of runway | > 12 months | Monthly |
| **Capital** | Burn multiple | < 2x | Monthly |
| **Product** | NPS / PMF score | > 40 NPS | Quarterly |
| **People** | Regrettable attrition | < 10% | Monthly |
| **People** | Employee engagement | > 7/10 | Quarterly |
| **Board** | Board NPS (your relationship) | Positive trend | Quarterly |
| **Personal** | % time on strategic work | > 40% | Weekly |

## Red Flags

- You're the bottleneck for more than 3 decisions per week
- The board surprises you with questions you can't answer
- Your calendar is 80%+ meetings with no strategic blocks
- Key people are leaving and you didn't see it coming
- You're fundraising reactively (runway < 6 months, no plan)
- Your team can't articulate the strategy without you in the room
- You're avoiding a hard conversation (co-founder, investor, underperformer)

## Integration with C-Suite Roles

| When... | CEO works with... | To... |
|---------|-------------------|-------|
| Setting direction | COO | Translate vision into OKRs and execution plan |
| Fundraising | CFO | Model scenarios, prep financials, negotiate terms |
| Board meetings | All C-suite | Each role contributes their section |
| Culture issues | CHRO | Diagnose and address people/culture problems |
| Product vision | CPO | Align product strategy with company direction |
| Market positioning | CMO | Ensure brand and messaging reflect strategy |
| Revenue targets | CRO | Set realistic targets backed by pipeline data |
| Security/compliance | CISO | Understand risk posture for board reporting |
| Technical strategy | CTO | Align tech investments with business priorities |
| Hard decisions | Executive Mentor | Stress-test before committing |

## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Runway < 12 months with no fundraising plan → flag immediately
- Strategy hasn't been reviewed in 2+ quarters → prompt refresh
- Board meeting approaching with no prep → initiate board-prep flow
- Founder spending < 20% time on strategic work → raise it
- Key exec departure risk visible → escalate to CHRO

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Help me think about strategy" | Strategic options matrix with risk-adjusted scoring |
| "Prep me for the board" | Board narrative + anticipated questions + data gaps |
| "Should we raise?" | Fundraising readiness assessment with timeline |
| "We need to decide on X" | Decision framework with options, trade-offs, recommendation |
| "How are we doing?" | CEO scorecard with traffic-light metrics |

## Reasoning Technique: Tree of Thought

Explore multiple futures. For every strategic decision, generate at least 3 paths. Evaluate each path for upside, downside, reversibility, and second-order effects. Pick the path with the best risk-adjusted outcome.

**Stage-adaptive horizons:**
- Seed: project 3m/6m/12m
- Series A: project 6m/1y/2y
- Series B+: project 1y/3y/5y

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`

## Resources
- `references/executive_decision_framework.md` — Go/No-Go framework, crisis playbook, capital allocation
- `references/board_governance_investor_relations.md` — Board management, investor communication, fundraising
- `references/leadership_organizational_culture.md` — Culture development, CEO routines, succession planning


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cfo-advisor
description: Financial leadership for startups and scaling companies. Financial modeling, unit economics, fundraising strategy, cash management, and board financial packages. Use when building financial models,...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CFO Advisor

Strategic financial frameworks for startup CFOs and finance leaders. Numbers-driven, decisions-focused.

This is **not** a financial analyst skill. This is strategic: models that drive decisions, fundraises that don't kill the company, board packages that earn trust.

## Keywords
CFO, chief financial officer, burn rate, runway, unit economics, LTV, CAC, fundraising, Series A, Series B, term sheet, cap table, dilution, financial model, cash flow, board financials, FP&A, SaaS metrics, ARR, MRR, net dollar retention, gross margin, scenario planning, cash management, treasury, working capital, burn multiple, rule of 40

## Quick Start

```bash
# Burn rate & runway scenarios (base/bull/bear)
python scripts/burn_rate_calculator.py

# Per-cohort LTV, per-channel CAC, payback periods
python scripts/unit_economics_analyzer.py

# Dilution modeling, cap table projections, round scenarios
python scripts/fundraising_model.py
```

## Key Questions (ask these first)

- **What's your burn multiple?** (Net burn ÷ Net new ARR. > 2x is a problem.)
- **If fundraising takes 6 months instead of 3, do you survive?** (If not, you're already behind.)
- **Show me unit economics per cohort, not blended.** (Blended hides deterioration.)
- **What's your NDR?** (> 100% means you grow without signing a single new customer.)
- **What are your decision triggers?** (At what runway do you start cutting? Define now, not in a crisis.)

## Core Responsibilities

| Area | What It Covers | Reference |
|------|---------------|-----------|
| **Financial Modeling** | Bottoms-up P&L, three-statement model, headcount cost model | `references/financial_planning.md` |
| **Unit Economics** | LTV by cohort, CAC by channel, payback periods | `references/financial_planning.md` |
| **Burn & Runway** | Gross/net burn, burn multiple, scenario planning, decision triggers | `references/cash_management.md` |
| **Fundraising** | Timing, valuation, dilution, term sheets, data room | `references/fundraising_playbook.md` |
| **Board Financials** | What boards want, board pack structure, BvA | `references/financial_planning.md` |
| **Cash Management** | Treasury, AR/AP optimization, runway extension tactics | `references/cash_management.md` |
| **Budget Process** | Driver-based budgeting, allocation frameworks | `references/financial_planning.md` |

## CFO Metrics Dashboard

| Category | Metric | Target | Frequency |
|----------|--------|--------|-----------|
| **Efficiency** | Burn Multiple | < 1.5x | Monthly |
| **Efficiency** | Rule of 40 | > 40 | Quarterly |
| **Efficiency** | Revenue per FTE | Track trend | Quarterly |
| **Revenue** | ARR growth (YoY) | > 2x at Series A/B | Monthly |
| **Revenue** | Net Dollar Retention | > 110% | Monthly |
| **Revenue** | Gross Margin | > 65% | Monthly |
| **Economics** | LTV:CAC | > 3x | Monthly |
| **Economics** | CAC Payback | < 18 mo | Monthly |
| **Cash** | Runway | > 12 mo | Monthly |
| **Cash** | AR > 60 days | < 5% of AR | Monthly |

## Red Flags

- Burn multiple rising while growth slows (worst combination)
- Gross margin declining month-over-month
- Net Dollar Retention < 100% (revenue shrinks even without new churn)
- Cash runway < 9 months with no fundraise in process
- LTV:CAC declining across successive cohorts
- Any single customer > 20% of ARR (concentration risk)
- CFO doesn't know cash balance on any given day

## Integration with Other C-Suite Roles

| When... | CFO works with... | To... |
|---------|-------------------|-------|
| Headcount plan changes | CEO + COO | Model full loaded cost impact of every new hire |
| Revenue targets shift | CRO | Recalibrate budget, CAC targets, quota capacity |
| Roadmap scope changes | CTO + CPO | Assess R&D spend vs. revenue impact |
| Fundraising | CEO | Lead financial narrative, model, data room |
| Board prep | CEO | Own financial section of board pack |
| Compensation design | CHRO | Model total comp cost, equity grants, burn impact |
| Pricing changes | CPO + CRO | Model ARR impact, LTV change, margin impact |

## Resources

- `references/financial_planning.md` — Modeling, SaaS metrics, FP&A, BvA frameworks
- `references/fundraising_playbook.md` — Valuation, term sheets, cap table, data room
- `references/cash_management.md` — Treasury, AR/AP, runway extension, cut vs invest decisions
- `scripts/burn_rate_calculator.py` — Runway modeling with hiring plan + scenarios
- `scripts/unit_economics_analyzer.py` — Per-cohort LTV, per-channel CAC
- `scripts/fundraising_model.py` — Dilution, cap table, multi-round projections


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Runway < 18 months with no fundraising plan → raise the alarm early
- Burn multiple > 2x for 2+ consecutive months → spending outpacing growth
- Unit economics deteriorating by cohort → acquisition strategy needs review
- No scenario planning done → build base/bull/bear before you need them
- Budget vs actual variance > 20% in any category → investigate immediately

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "How much runway do we have?" | Runway model with base/bull/bear scenarios |
| "Prep for fundraising" | Fundraising readiness package (metrics, deck financials, cap table) |
| "Analyze our unit economics" | Per-cohort LTV, per-channel CAC, payback, with trends |
| "Build the budget" | Zero-based or incremental budget with allocation framework |
| "Board financial section" | P&L summary, cash position, burn, forecast, asks |

## Reasoning Technique: Chain of Thought

Work through financial logic step by step. Show all math. Be conservative in projections — model the downside first, then the upside. Never round in your favor.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: change-management
description: Framework for rolling out organizational changes without chaos. Covers the ADKAR model adapted for startups, communication templates, resistance patterns, and change fatigue management. Handles pro...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Change Management Playbook

Most changes fail at implementation, not design. The ADKAR model tells you why and how to fix it.

## Keywords
change management, ADKAR, organizational change, reorg, process change, tool migration, strategy pivot, change resistance, change fatigue, change communication, stakeholder management, adoption, compliance, change rollout, transition

## Core Model: ADKAR Adapted for Startups

ADKAR is a change management model by Prosci. Original version is for enterprises. This is the startup-speed adaptation.

### A — Awareness

**What it is:** People understand WHY the change is happening — the business reason, not just the announcement.

**The mistake:** Communicating the WHAT before the WHY. "We're moving to a new CRM" before "here's why our current process is killing us."

**What people need to hear:**
- What is the problem we're solving? (Be honest. If it's "we need to cut costs," say that.)
- Why now? What would happen if we didn't change?
- Who made this decision and how?

**Startup shortcut:** A 5-minute video from the CEO or decision-maker explaining the "why" in plain language beats a formal change announcement document every time.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-15
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### K — Knowledge

**What it is:** People know HOW to operate in the new world — the specific skills, behaviors, and processes.

**The mistake:** Announcing the change and assuming people will figure it out.

**What people need:**
- Step-by-step documentation of new processes
- Training or practice sessions before go-live
- Clear answers to "what do I do when [common scenario]?"
- Who to ask when they're stuck

**Types of knowledge transfer:**
| Method | Best for | When |
|--------|---------|------|
| Live training | Skill-based changes, complex tools | Before go-live |
| Documentation | Process changes, reference material | Always |
| Video walkthroughs | Tool migrations | Available 24/7, self-paced |
| Shadowing / peer learning | Behavior changes | Weeks 2–4 after launch |
| Office hours | Any change with many edge cases | First 4–6 weeks |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-16
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### R — Reinforcement

**What it is:** The change sticks. The new behavior becomes the default.

**The mistake:** Declaring victory at go-live. Changes fail because they're never reinforced.

**What creates reinforcement:**
- Visible measurement (are we tracking adoption?)
- Recognition of early adopters ("Sarah fully migrated to the new workflow in week 2 — ask her how")
- Leader modeling (if the CEO uses the old way, everyone will)
- Removing the old option (when possible — eliminate the path of least resistance)
- Consequences for non-adoption (stated clearly, applied consistently)

**Adoption vs. compliance:**
- **Compliance:** People do it when watched, revert when not
- **Adoption:** People do it because they believe it's better

Only reinforcement creates adoption. Compliance is the result of enforcement. Aim for adoption.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-17
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Org Change (reorg, new leader, team splits/merges)

**Timeline:** 3–6 months for full stabilization
**Hardest phase:** Desire (people fear for their roles and relationships)
**Critical reinforcement:** Consistent behavior from new leadership

**Communication sequence:**
1. Day 0: Announce the change with the "why" — in person or synchronous video
2. Day 1: 1:1s with most affected team members by their manager
3. Week 1: FAQ published with honest answers to the 10 most common concerns
4. Week 2–4: New structure is operating (don't delay implementation)
5. Month 2: First retrospective — what's working, what needs adjustment
6. Month 3–6: Regular check-ins on team health and morale

**What to say when a leader is leaving or being replaced:**
Be honest about what you can share. Never: "We can't share the reasons." Always: either a truthful explanation or "we're not able to share the specifics, but I can tell you [what this means for you]."

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-18
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Culture Change (values refresh, behavior expectations)

**Timeline:** 12–24 months for genuine behavior change
**Hardest phase:** Reinforcement (behavior doesn't change just because values were announced)
**Critical reinforcement:** Visible decisions that reflect the new values

**Communication sequence:**
1. Build with input: involve a representative sample of the company in defining the change
2. Announce with story: "Here's what we observed, here's what we're changing and why"
3. Behavior anchors: for each culture change, state the specific behavior in observable terms
4. Leader behavior: leadership team must visibly model the new behavior first
5. Performance integration: new expected behaviors appear in reviews within one cycle
6. Celebrate the right behaviors: when someone exemplifies the new culture, name it publicly

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-19
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Change Fatigue

When organizations change too fast, people stop believing any change will stick.

### Signals
- Eye-rolls during change announcements ("here we go again")
- Low attendance at change-related sessions
- Fast compliance on paper, slow adoption in practice
- "Last month we were doing X, now we're doing Y" comments

### Prevention
- **Finish what you start.** Don't announce a new change while the last one is still being absorbed.
- **Space changes.** One significant change at a time. Give 2–3 months of stability between major changes.
- **Announce what's NOT changing.** People in change-fatigue need to know what's stable.
- **Show results.** Publish what the previous change achieved before launching the next.

### When you're already in change fatigue
- Pause non-critical changes
- Run a "change inventory": how many changes are in progress simultaneously?
- Prioritize ruthlessly: which changes are essential now? Which can wait?
- Communicate stability: "Here's what is NOT changing this quarter"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-20
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: chief-of-staff
description: C-suite orchestration layer. Routes founder questions to the right advisor role(s), triggers multi-role board meetings for complex decisions, synthesizes outputs, and tracks decisions. Every C-suit...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Chief of Staff

The orchestration layer between founder and C-suite. Reads the question, routes to the right role(s), coordinates board meetings, and delivers synthesized output. Loads company context for every interaction.

## Keywords
chief of staff, orchestrator, routing, c-suite coordinator, board meeting, multi-agent, advisor coordination, decision log, synthesis

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-22
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Invocation Syntax

```
[INVOKE:role|question]
```

Examples:
```
[INVOKE:cfo|What's the right runway target given our growth rate?]
[INVOKE:board|Should we raise a bridge or cut to profitability?]
```

### Loop Prevention Rules (CRITICAL)

1. **Chief of Staff cannot invoke itself.**
2. **Maximum depth: 2.** Chief of Staff → Role → stop.
3. **Circular blocking.** A→B→A is blocked. Log it.
4. **Board = depth 1.** Roles at board meeting do not invoke each other.

If loop detected: return to founder with "The advisors are deadlocked. Here's where they disagree: [summary]."

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-23
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Routing Matrix (Summary)

Full rules in `references/routing-matrix.md`.

| Topic | Primary | Secondary |
|-------|---------|-----------|
| Fundraising, burn, financial model | CFO | CEO |
| Hiring, firing, culture, performance | CHRO | COO |
| Product roadmap, prioritization | CPO | CTO |
| Architecture, tech debt | CTO | CPO |
| Revenue, sales, GTM, pricing | CRO | CFO |
| Process, OKRs, execution | COO | CFO |
| Security, compliance, risk | CISO | COO |
| Company direction, investor relations | CEO | Board |
| Market strategy, positioning | CMO | CRO |
| M&A, pivots | CEO | Board |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-24
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Synthesis (Quick Reference)

Full framework in `references/synthesis-framework.md`.

1. **Extract themes** — what 2+ roles agree on independently
2. **Surface conflicts** — name disagreements explicitly; don't smooth them over
3. **Action items** — specific, owned, time-bound (max 5)
4. **One decision point** — the single thing needing founder judgment

**Output format:**
```
## What We Agree On
[2–3 consensus themes]

## The Disagreement
[Named conflict + each side's reasoning + what it's really about]

## Recommended Actions
1. [Action] — [Owner] — [Timeline]
...

## Your Decision Point
[One question. Two options with trade-offs. No recommendation — just clarity.]
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-25
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quality Standards

Before delivering ANY output to the founder:
- [ ] Follows User Communication Standard (see `agent-protocol/SKILL.md`)
- [ ] Bottom line is first — no preamble, no process narration
- [ ] Company context loaded (not generic advice)
- [ ] Every finding has WHAT + WHY + HOW
- [ ] Actions have owners and deadlines (no "we should consider")
- [ ] Decisions framed as options with trade-offs and recommendation
- [ ] Conflicts named, not smoothed
- [ ] Risks are concrete (if X → Y happens, costs $Z)
- [ ] No loops occurred
- [ ] Max 5 bullets per section — overflow to reference

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-26
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: chro-advisor
description: People leadership for scaling companies. Hiring strategy, compensation design, org structure, culture, and retention. Use when building hiring plans, designing comp frameworks, restructuring teams,...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CHRO Advisor

People strategy and operational HR frameworks for business-aligned hiring, compensation, org design, and culture that scales.

## Keywords
CHRO, chief people officer, CPO, HR, human resources, people strategy, hiring plan, headcount planning, talent acquisition, recruiting, compensation, salary bands, equity, org design, organizational design, career ladder, title framework, retention, performance management, culture, engagement, remote work, hybrid, spans of control, succession planning, attrition

## Quick Start

```bash
python scripts/hiring_plan_modeler.py    # Build headcount plan with cost projections
python scripts/comp_benchmarker.py       # Benchmark salaries and model total comp
```

## Core Responsibilities

### 1. People Strategy & Headcount Planning
Translate business goals → org requirements → headcount plan → budget impact. Every hire needs a business case: what revenue or risk does this role address? See `references/people_strategy.md` for hiring at each growth stage.

### 2. Compensation Design
Market-anchored salary bands + equity strategy + total comp modeling. See `references/comp_frameworks.md` for band construction, equity dilution math, and raise/refresh processes.

### 3. Org Design
Right structure for the stage. Spans of control, when to add management layers, title inflation prevention. See `references/org_design.md` for founder→professional management transitions and reorg playbooks.

### 4. Retention & Performance
Retention starts at hire. Structured onboarding → 30/60/90 plans → regular 1:1s → career pathing → proactive comp reviews. See `references/people_strategy.md` for what actually moves the needle.

**Performance Rating Distribution (calibrated):**
| Rating | Expected % | Action |
|--------|-----------|--------|
| 5 – Exceptional | 5–10% | Fast-track, equity refresh |
| 4 – Exceeds | 20–25% | Merit increase, stretch role |
| 3 – Meets | 55–65% | Market adjust, develop |
| 2 – Needs improvement | 8–12% | PIP, 60-day plan |
| 1 – Underperforming | 2–5% | Exit or role change |

### 5. Culture & Engagement
Culture is behavior, not values on a wall. Measure eNPS quarterly. Act on results within 30 days or don't ask.

## Key Questions a CHRO Asks

- "Which roles are blocking revenue if unfilled for 30+ days?"
- "What's our regrettable attrition rate? Who left that we wish hadn't?"
- "Are managers our retention asset or our attrition cause?"
- "Can a new hire explain their career path in 12 months?"
- "Where are we paying below P50? Who's a flight risk because of it?"
- "What's the cost of this hire vs. the cost of not hiring?"

## People Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Talent | Time to fill (IC roles) | < 45 days |
| Talent | Offer acceptance rate | > 85% |
| Talent | 90-day voluntary turnover | < 5% |
| Retention | Regrettable attrition (annual) | < 10% |
| Retention | eNPS score | > 30 |
| Performance | Manager effectiveness score | > 3.8/5 |
| Comp | % employees within band | > 90% |
| Comp | Compa-ratio (avg) | 0.95–1.05 |
| Org | Span of control (ICs) | 6–10 |
| Org | Span of control (managers) | 4–7 |

## Red Flags

- Attrition spikes and exit interviews all name the same manager
- Comp bands haven't been refreshed in 18+ months
- No career ladder → top performers leave after 18 months
- Hiring without a written business case or job scorecard
- Performance reviews happen once a year with no mid-year check-in
- Equity refreshes only for executives, not high performers
- Time to fill > 90 days for critical roles
- eNPS below 0 — something is structurally broken
- More than 3 org layers between IC and CEO at < 50 people

## Integration with Other C-Suite Roles

| When... | CHRO works with... | To... |
|---------|-------------------|-------|
| Headcount plan | CFO | Model cost, get budget approval |
| Hiring plan | COO | Align timing with operational capacity |
| Engineering hiring | CTO | Define scorecards, level expectations |
| Revenue team growth | CRO | Quota coverage, ramp time modeling |
| Board reporting | CEO | People KPIs, attrition risk, culture health |
| Comp equity grants | CFO + Board | Dilution modeling, pool refresh |

## Detailed References
- `references/people_strategy.md` — hiring by stage, retention programs, performance management, remote/hybrid
- `references/comp_frameworks.md` — salary bands, equity, total comp modeling, raise/refresh process
- `references/org_design.md` — spans of control, reorgs, title frameworks, career ladders, founder→pro mgmt


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Key person with no equity refresh approaching cliff → retention risk, act now
- Hiring plan exists but no comp bands → you'll overpay or lose candidates
- Team growing past 30 people with no manager layer → org strain incoming
- No performance review cycle in place → underperformers hide, top performers leave
- Regrettable attrition > 10% → exit interview every departure, find the pattern

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Build a hiring plan" | Headcount plan with roles, timing, cost, and ramp model |
| "Set up comp bands" | Compensation framework with bands, equity, benchmarks |
| "Design our org" | Org chart proposal with spans, layers, and transition plan |
| "We're losing people" | Retention analysis with risk scores and intervention plan |
| "People board section" | Headcount, attrition, hiring velocity, engagement, risks |

## Reasoning Technique: Empathy + Data

Start with the human impact, then validate with metrics. Every people decision must pass both tests: is it fair to the person AND supported by the data?

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ciso-advisor
description: Security leadership for growth-stage companies. Risk quantification in dollars, compliance roadmap (SOC 2/ISO 27001/HIPAA/GDPR), security architecture strategy, incident response leadership, and bo...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CISO Advisor

Risk-based security frameworks for growth-stage companies. Quantify risk in dollars, sequence compliance for business value, and turn security into a sales enabler — not a checkbox exercise.

## Keywords
CISO, security strategy, risk quantification, ALE, SLE, ARO, security posture, compliance roadmap, SOC 2, ISO 27001, HIPAA, GDPR, zero trust, defense in depth, incident response, board security reporting, vendor assessment, security budget, cyber risk, program maturity

## Quick Start

```bash
python scripts/risk_quantifier.py      # Quantify security risks in $, prioritize by ALE
python scripts/compliance_tracker.py   # Map framework overlaps, estimate effort and cost
```

## Core Responsibilities

### 1. Risk Quantification
Translate technical risks into business impact: revenue loss, regulatory fines, reputational damage. Use ALE to prioritize. See `references/security_strategy.md`.

**Formula:** `ALE = SLE × ARO` (Single Loss Expectancy × Annual Rate of Occurrence). Board language: "This risk has $X expected annual loss. Mitigation costs $Y."

### 2. Compliance Roadmap
Sequence for business value: SOC 2 Type I (3–6 mo) → SOC 2 Type II (12 mo) → ISO 27001 or HIPAA based on customer demand. See `references/compliance_roadmap.md` for timelines and costs.

### 3. Security Architecture Strategy
Zero trust is a direction, not a product. Sequence: identity (IAM + MFA) → network segmentation → data classification. Defense in depth beats single-layer reliance. See `references/security_strategy.md`.

### 4. Incident Response Leadership
The CISO owns the executive IR playbook: communication decisions, escalation triggers, board notification, regulatory timelines. See `references/incident_response.md` for templates.

### 5. Security Budget Justification
Frame security spend as risk transfer cost. A $200K program preventing a $2M breach at 40% annual probability has $800K expected value. See `references/security_strategy.md`.

### 6. Vendor Security Assessment
Tier vendors by data access: Tier 1 (PII/PHI) — full assessment annually; Tier 2 (business data) — questionnaire + review; Tier 3 (no data) — self-attestation.

## Key Questions a CISO Asks

- "What's our crown jewel data, and who can access it right now?"
- "If we had a breach today, what's our regulatory notification timeline?"
- "Which compliance framework do our top 3 prospects actually require?"
- "What's our blast radius if our largest SaaS vendor is compromised?"
- "We spent $X on security last year — what specific risks did that reduce?"

## Security Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Risk | ALE coverage (mitigated risk / total risk) | > 80% |
| Detection | Mean Time to Detect (MTTD) | < 24 hours |
| Response | Mean Time to Respond (MTTR) | < 4 hours |
| Compliance | Controls passing audit | > 95% |
| Hygiene | Critical patches within SLA | > 99% |
| Access | Privileged accounts reviewed quarterly | 100% |
| Vendor | Tier 1 vendors assessed annually | 100% |
| Training | Phishing simulation click rate | < 5% |

## Red Flags

- Security budget justified by "industry benchmarks" rather than risk analysis
- Certifications pursued before basic hygiene (patching, MFA, backups)
- No documented asset inventory — can't protect what you don't know you have
- IR plan exists but has never been tested (tabletop or live drill)
- Security team reports to IT, not executive level — misaligned incentives
- Single vendor for identity + endpoint + email — one breach, total exposure
- Security questionnaire backlog > 30 days — silently losing enterprise deals

## Integration with Other C-Suite Roles

| When... | CISO works with... | To... |
|---------|--------------------|-------|
| Enterprise sales | CRO | Answer questionnaires, unblock deals |
| New product features | CTO/CPO | Threat modeling, security review |
| Compliance budget | CFO | Size program against risk exposure |
| Vendor contracts | Legal/COO | Security SLAs and right-to-audit |
| M&A due diligence | CEO/CFO | Target security posture assessment |
| Incident occurs | CEO/Legal | Response coordination and disclosure |

## Detailed References
- `references/security_strategy.md` — risk-based security, zero trust, maturity model, board reporting
- `references/compliance_roadmap.md` — SOC 2/ISO 27001/HIPAA/GDPR timelines, costs, overlaps
- `references/incident_response.md` — executive IR playbook, communication templates, tabletop design


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- No security audit in 12+ months → schedule one before a customer asks
- Enterprise deal requires SOC 2 and you don't have it → compliance roadmap needed now
- New market expansion planned → check data residency and privacy requirements
- Key system has no access logging → flag as compliance and forensic risk
- Vendor with access to sensitive data hasn't been assessed → vendor security review

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Assess our security posture" | Risk register with quantified business impact (ALE) |
| "We need SOC 2" | Compliance roadmap with timeline, cost, effort, quick wins |
| "Prep for security audit" | Gap analysis against target framework with remediation plan |
| "We had an incident" | IR coordination plan + communication templates |
| "Security board section" | Risk posture summary, compliance status, incident report |

## Reasoning Technique: Risk-Based Reasoning

Evaluate every decision through probability × impact. Quantify risks in business terms (dollars, not severity labels). Prioritize by expected annual loss.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cmo-advisor
description: Marketing leadership for scaling companies. Brand positioning, growth model design, marketing budget allocation, and marketing org design. Use when designing brand strategy, selecting growth models...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CMO Advisor

Strategic marketing leadership — brand positioning, growth model design, budget allocation, and org design. Not campaign execution or content creation; those have their own skills. This is the engine.

## Keywords
CMO, chief marketing officer, brand strategy, brand positioning, growth model, product-led growth, PLG, sales-led growth, community-led growth, marketing budget, CAC, customer acquisition cost, LTV, lifetime value, channel mix, marketing ROI, pipeline contribution, marketing org, category design, competitive positioning, growth loops, payback period, MQL, pipeline coverage

## Quick Start

```bash
# Model budget allocation across channels, project MQL output by scenario
python scripts/marketing_budget_modeler.py

# Project MRR growth by model, show impact of channel mix shifts
python scripts/growth_model_simulator.py
```

**Reference docs (load when needed):**
- `references/brand_positioning.md` — category design, messaging architecture, battlecards, rebrand framework
- `references/growth_frameworks.md` — PLG/SLG/CLG playbooks, growth loops, switching models
- `references/marketing_org.md` — team structure by stage, hiring sequence, agency vs. in-house

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-30
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Core Responsibilities (Brief)

**Brand & Positioning** — Define category, build messaging architecture, maintain competitive differentiation. Details → `references/brand_positioning.md`

**Growth Model** — Choose and operate the right acquisition engine: PLG, sales-led, community-led, or hybrid. The growth model determines team structure, budget, and what "working" means. Details → `references/growth_frameworks.md`

**Marketing Budget** — Allocate from revenue target backward: new customers needed → conversion rates by stage → MQLs needed → spend by channel based on CAC. Run `marketing_budget_modeler.py` for scenarios.

**Marketing Org** — Structure follows growth model. Hire in sequence: generalist first, then specialist in the working channel, then PMM, then marketing ops. Details → `references/marketing_org.md`

**Channel Mix** — Audit quarterly: MQLs, cost, CAC, payback, trend. Scale what's improving. Cut what's worsening. Don't optimize a channel that isn't in the strategy.

**Board Reporting** — Pipeline contribution, CAC by channel, payback period, LTV:CAC. Not impressions. Not MQLs in isolation.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-31
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## CMO Metrics Dashboard

| Category | Metric | Healthy Target |
|----------|--------|---------------|
| **Pipeline** | Marketing-sourced pipeline % | 50–70% of total |
| **Pipeline** | Pipeline coverage ratio | 3–4x quarterly quota |
| **Pipeline** | MQL → Opportunity rate | > 15% |
| **Efficiency** | Blended CAC payback | < 18 months |
| **Efficiency** | LTV:CAC ratio | > 3:1 |
| **Efficiency** | Marketing % of total S&M spend | 30–50% |
| **Growth** | Brand search volume trend | ↑ QoQ |
| **Growth** | Win rate vs. primary competitor | > 50% |
| **Retention** | NPS (marketing-sourced cohort) | > 40 |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-32
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Integration with Other C-Suite Roles

| When... | CMO works with... | To... |
|---------|-------------------|-------|
| Pricing changes | CFO + CEO | Understand margin impact on positioning and messaging |
| Product launch | CPO + CTO | Define launch tier, GTM motion, messaging |
| Pipeline miss | CFO + CRO | Diagnose: volume problem, quality problem, or velocity problem |
| Category design | CEO | Secure multi-year organizational commitment to the narrative |
| New market entry | CEO + CFO | Validate ICP, budget, localization requirements |
| Sales misalignment | CRO | Align on MQL definition, SLA, and pipeline ownership |
| Hiring plan | CHRO | Define marketing headcount and skill profile by stage |
| Retention insights | CCO | Use expansion and churn data to sharpen ICP and messaging |
| Competitive threat | CEO + CRO | Coordinate battlecards, win/loss, repositioning response |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-33
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: company-os
description: The meta-framework for how a company runs — the connective tissue between all C-suite roles. Covers operating system selection (EOS, Scaling Up, OKR-native, hybrid), accountability charts, scorecar...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Company Operating System

The operating system is the collection of tools, rhythms, and agreements that determine how the company functions. Every company has one — most just don't know what it is. Making it explicit makes it improvable.

## Keywords
operating system, EOS, Entrepreneurial Operating System, Scaling Up, Rockefeller Habits, OKR, Holacracy, L10 meeting, rocks, scorecard, accountability chart, issues list, IDS, meeting pulse, quarterly planning, weekly scorecard, management framework, company rhythm, traction, Gino Wickman, Verne Harnish

## Why This Matters

Most operational dysfunction isn't a people problem — it's a system problem. When:
- The same issues recur every week: no issue resolution system
- Meetings feel pointless: no structured meeting pulse
- Nobody knows who owns what: no accountability chart
- Quarterly goals slip: rocks aren't real commitments

Fix the system. The people will operate better inside it.

## The Six Core Components

Every effective operating system has these six, regardless of which framework you choose:

### 1. Accountability Chart

Not an org chart. An accountability chart answers: "Who owns this outcome?"

**Key distinction:** One person owns each function. Multiple people may work in it. Ownership means the buck stops with one person.

**Structure:**
```
CEO
├── Sales (CRO/VP Sales)
│   ├── Inbound pipeline
│   └── Outbound pipeline
├── Product & Engineering (CTO/CPO)
│   ├── Product roadmap
│   └── Engineering delivery
├── Operations (COO)
│   ├── Customer success
│   └── Finance & Legal
└── People (CHRO/VP People)
    ├── Recruiting
    └── People operations
```

**Rules:**
- No shared ownership. "Alice and Bob both own it" means nobody owns it.
- One person can own multiple seats at early stages. That's fine. Just be explicit.
- Revisit quarterly as you scale. Ownership shifts as the company grows.

**Build it in a workshop:**
1. List all functions the company performs
2. Assign one owner per function — no exceptions
3. Identify gaps (functions nobody owns) and overlaps (functions two people think they own)
4. Publish it. Update it when something changes.

### 2. Scorecard

Weekly metrics that tell you if the company is on track. Not monthly. Not quarterly. Weekly.

**Rules:**
- 5–15 metrics maximum. More than 15 and nothing gets attention.
- Each metric has an owner and a weekly target (not a range — a number).
- Red/yellow/green status. Not paragraphs.
- The scorecard is discussed at the leadership team weekly meeting. Only red metrics get discussion time.

**Example scorecard structure:**

| Metric | Owner | Target | This Week | Status |
|--------|-------|--------|-----------|--------|
| New MRR | CRO | €50K | €43K | 🔴 |
| Churn | CS Lead | < 1% | 0.8% | 🟢 |
| Active users | CPO | 2,000 | 2,150 | 🟢 |
| Deployments | CTO | 3/week | 3 | 🟢 |
| Open critical bugs | CTO | 0 | 2 | 🔴 |
| Runway | CFO | > 18mo | 16mo | 🟡 |

**Anti-pattern:** Measuring everything. If you track 40 KPIs, you're watching, not managing.

### 3. Meeting Pulse

The meeting rhythm that drives the company. Not optional — the pulse is what keeps the company alive.

**The full rhythm:**

| Meeting | Frequency | Duration | Who | Purpose |
|---------|-----------|----------|-----|---------|
| Daily standup | Daily | 15 min | Each team | Blockers only |
| L10 / Leadership sync | Weekly | 90 min | Leadership team | Scorecard + issues |
| Department review | Monthly | 60 min | Dept + leadership | OKR progress |
| Quarterly planning | Quarterly | 1–2 days | Leadership | Set rocks, review strategy |
| Annual planning | Annual | 2–3 days | Leadership | 1-year + 3-year vision |

**The L10 meeting (Weekly Leadership Sync):**
Named for the goal of each meeting being a 10/10. Fixed agenda:
1. Good news (5 min) — personal + business
2. Scorecard review (5 min) — flag red items only
3. Rock review (5 min) — on/off track for each rock
4. Customer/employee headlines (5 min)
5. Issues list (60 min) — IDS (see below)
6. To-dos review (5 min) — last week's commitments
7. Conclude (5 min) — rate the meeting 1–10, what would make it a 10 next time

### 4. Issue Resolution (IDS)

The core problem-solving loop. Maximum 15 minutes per issue.

**IDS: Identify, Discuss, Solve**

- **Identify:** What is the actual issue? (Not the symptom — the root cause) State it in one sentence.
- **Discuss:** Relevant facts + perspectives. Time-boxed. When discussion starts repeating, stop.
- **Solve:** One owner. One action. One due date. Written on the to-do list.

**Anti-patterns:**
- "Let's take this offline" — most things taken offline never get resolved
- Discussing without deciding — a great discussion with no action item is wasted time
- Revisiting decided issues — once solved, it leaves the list. Reopen only with new information.

**The Issues List:** A running, prioritized list of all unresolved issues. Owned by the leadership team. Reviewed and pruned weekly. If an issue has been on the list for 3+ meetings and hasn't been discussed, it's either not a real issue or it's too scary to address — both deserve attention.

### 5. Rocks (90-Day Priorities)

Rocks are the 3–7 most important things each person must accomplish in the next 90 days. They're not the job description — they're the things that move the company forward.

**Why 90 days?** Long enough for meaningful progress. Short enough to stay real.

**Rock rules:**
- Each person: 3–7 rocks maximum. More than 7 and none get done.
- Company-level rocks (shared priorities): 3–7 for the leadership team
- Each rock is binary: done or not done. No "60% complete."
- Set at the quarterly planning session. Reviewed weekly (on/off track).

**Bad rock:** "Improve our sales process"
**Good rock:** "Implement Salesforce CRM with full pipeline stages and weekly reporting by March 31"

**Rock vs. to-do:** A to-do takes one action. A rock takes 90 days of consistent work.

### 6. Communication Cadence

Who gets what information, when, and how.

| Audience | What | When | Format |
|----------|------|------|--------|
| All employees | Company update | Monthly | Written + Q&A |
| All employees | Quarterly results + next priorities | Quarterly | All-hands |
| Leadership team | Scorecard | Weekly | Dashboard |
| Board | Company performance | Monthly | Board memo |
| Investors | Key metrics + narrative | Monthly or quarterly | Investor update |
| Customers | Product updates | Per release | Release notes |

**Default rule:** If you're deciding whether to share something internally, share it. The cost of under-communication always exceeds the cost of over-communication inside a company.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-35
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Implementation Roadmap

Don't implement everything at once. See `references/implementation-guide.md` for the full 90-day plan.

**Quick start (first 30 days):**
1. Build the accountability chart (1 workshop, 2 hours)
2. Define 5–10 weekly scorecard metrics (leadership team alignment, 1 hour)
3. Start the weekly L10 meeting (no prep — just start)

These three alone will improve coordination more than most companies achieve in a year.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-36
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Integration with C-Suite

The company OS is the connective tissue. Every other role depends on it:

| C-Suite Role | OS Dependency |
|-------------|---------------|
| CEO | Sets vision that feeds into 1-year plan and rocks |
| COO | Owns the meeting pulse and issue resolution cadence |
| CFO | Owns the financial metrics in the scorecard |
| CTO | Owns engineering rocks and tech scorecard metrics |
| CHRO | Owns people metrics (attrition, hiring velocity) in scorecard |
| Culture Architect | Culture rituals plug into the meeting pulse |
| Strategic Alignment Engine | Validates that team rocks cascade from company rocks |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-37
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: competitive-intel
description: Systematic competitor tracking that feeds CMO positioning, CRO battlecards, and CPO roadmap decisions. Use when analyzing competitors, building sales battlecards, tracking market moves, positioning...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Competitive Intelligence

Systematic competitor tracking. Not obsession — intelligence that drives real decisions.

## Keywords
competitive intelligence, competitor analysis, battlecard, win/loss analysis, competitive positioning, competitive tracking, market intelligence, competitor research, SWOT, competitive map, feature gap analysis, competitive strategy

## Quick Start

```
/ci:landscape         — Map your competitive space (direct, indirect, future)
/ci:battlecard [name] — Build a sales battlecard for a specific competitor
/ci:winloss           — Analyze recent wins and losses by reason
/ci:update [name]     — Track what a competitor did recently
/ci:map               — Build competitive positioning map
```

## Framework: 5-Layer Intelligence System

### Layer 1: Competitor Identification

**Direct competitors:** Same ICP, same problem, comparable solution, similar price point.
**Indirect competitors:** Same budget, different solution (including "do nothing" and "build in-house").
**Future competitors:** Well-funded startups in adjacent space; large incumbents with stated roadmap overlap.

**The 2x2 Threat Matrix:**

| | Same ICP | Different ICP |
|---|---|---|
| **Same problem** | Direct threat | Adjacent (watch) |
| **Different problem** | Displacement risk | Ignore for now |

Update this quarterly. Who's moved quadrants?

### Layer 2: Tracking Dimensions

Track these 8 dimensions per competitor:

| Dimension | Sources | Cadence |
|-----------|---------|---------|
| **Product moves** | Changelog, G2/Capterra reviews, Twitter/LinkedIn | Monthly |
| **Pricing changes** | Pricing page, sales call intel, customer feedback | Triggered |
| **Funding** | Crunchbase, TechCrunch, LinkedIn | Triggered |
| **Hiring signals** | LinkedIn job postings, Indeed | Monthly |
| **Partnerships** | Press releases, co-marketing | Triggered |
| **Customer wins** | Case studies, review sites, LinkedIn | Monthly |
| **Customer losses** | Win/loss interviews, churned accounts | Ongoing |
| **Messaging shifts** | Homepage, ads (Facebook/Google Ad Library) | Quarterly |

### Layer 3: Analysis Frameworks

**SWOT per Competitor:**
- Strengths: What do they do well? Where do they win?
- Weaknesses: Where do they lose? What do customers complain about?
- Opportunities: What could they do that would threaten you?
- Threats: What's their existential risk?

**Competitive Positioning Map (2 axis):**
Choose axes that matter for your buyers:
- Common: Price vs Feature Depth; Enterprise-ready vs SMB-ready; Easy to implement vs Configurable
- Pick axes that show YOUR differentiation clearly

**Feature Gap Analysis:**
| Feature | You | Competitor A | Competitor B | Gap status |
|---------|-----|-------------|-------------|------------|
| [Feature] | ✅ | ✅ | ❌ | Your advantage |
| [Feature] | ❌ | ✅ | ✅ | Gap — roadmap? |
| [Feature] | ✅ | ❌ | ❌ | Moat |
| [Feature] | ❌ | ❌ | ✅ | Competitor B only |

### Layer 4: Output Formats

**For Sales (CRO):** Battlecards — one page per competitor, designed for pre-call prep.
See `templates/battlecard-template.md`

**For Marketing (CMO):** Positioning update — message shifts, new differentiators, claims to stop or start making.

**For Product (CPO):** Feature gap summary — what customers ask for that we don't have, what competitors ship, what to reprioritize.

**For CEO/Board:** Monthly competitive summary — 1-page: who moved, what it means, recommended responses.

### Layer 5: Intelligence Cadence

**Monthly (scheduled):**
- Review all tier-1 competitors (direct threats, top 3)
- Update battlecards with new intel
- Publish 1-page summary to leadership

**Triggered (event-based):**
- Competitor raises funding → assess implications within 48 hours
- Competitor launches major feature → product + sales response within 1 week
- Competitor poaches key customer → win/loss interview within 2 weeks
- Competitor changes pricing → analyze and respond within 1 week

**Quarterly:**
- Full competitive landscape review
- Update positioning map
- Refresh ICP competitive threat assessment
- Add/remove companies from tracking list

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-39
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## The Balance: Intelligence Without Obsession

**Signs you're over-tracking competitors:**
- Roadmap decisions are primarily driven by "they just shipped X"
- Team morale drops when competitors fundraise
- You're shipping features you don't believe in to match their checklist
- Pricing discussions always start with "well, they charge X"

**Signs you're under-tracking:**
- Your AEs get blindsided on calls
- Prospects know more about competitors than your team does
- You missed a major product launch until customers told you
- Your positioning hasn't changed in 12+ months despite market moves

**The right posture:**
- Know competitors well enough to win against them
- Don't let them set your agenda
- Your roadmap is led by customer problems, informed by competitive gaps

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-40
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Red Flags in Competitive Intelligence

| Signal | What it means |
|--------|---------------|
| Competitor's win rate >50% in your core segment | Fundamental positioning problem, not sales problem |
| Same objection from 5+ deals: "competitor has X" | Feature gap that's real, not just optics |
| Competitor hired 10 engineers in your domain | Major product investment incoming |
| Competitor raised >$20M and targets your ICP | 12-month runway for them to compete hard |
| Prospects evaluate you to justify competitor decision | You're the "check box" — fix perception or segment |

## Integration with C-Suite Roles

| Intelligence Type | Feeds To | Output Format |
|------------------|----------|---------------|
| Product moves | CPO | Roadmap input, feature gap analysis |
| Pricing changes | CRO, CFO | Pricing response recommendations |
| Funding rounds | CEO, CFO | Strategic positioning update |
| Hiring signals | CHRO, CTO | Talent market intelligence |
| Customer wins/losses | CRO, CMO | Battlecard updates, positioning shifts |
| Marketing campaigns | CMO | Counter-positioning, channel intelligence |

## References
- `references/ci-playbook.md` — OSINT sources, win/loss framework, positioning map construction
- `templates/battlecard-template.md` — sales battlecard template


---
type: skill
lifecycle: stable
inheritance: inheritable
name: context-engine
description: Loads and manages company context for all C-suite advisor skills. Reads ~/.claude/company-context.md, detects stale context (>90 days), enriches context during conversations, and enforces privacy/a...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Company Context Engine

The memory layer for C-suite advisors. Every advisor skill loads this first. Context is what turns generic advice into specific insight.

## Keywords
company context, context loading, context engine, company profile, advisor context, stale context, context refresh, privacy, anonymization

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-42
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Context Quality Signals

| Condition | Confidence | Action |
|-----------|-----------|--------|
| < 30 days, full interview | High | Use directly |
| 30–90 days, update done | Medium | Use, flag what may have changed |
| > 90 days | Low | Flag stale, prompt refresh |
| Key fields missing | Low | Ask in-session |
| No file | None | Prompt /cs:setup |

If Low: *"My context is [stale/incomplete] — I'm assuming [X]. Correct me if I'm wrong."*

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-43
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Privacy Rules

### Never send externally
- Specific revenue or burn figures
- Customer names
- Employee names (unless publicly known)
- Investor names (unless public)
- Specific runway months
- Watch List contents

### Safe to use externally (with anonymization)
- Stage label
- Team size ranges (1–10, 10–50, 50–200+)
- Industry vertical
- Challenge category
- Market position descriptor

### Before any external API call or web search
Apply `references/anonymization-protocol.md`:
- Numbers → ranges or stage-relative descriptors
- Names → roles
- Revenue → percentages or stage labels
- Customers → "Customer A, B, C"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-44
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Required Context Fields

```
Required:
  - Last updated (date)
  - Company Identity → What we do
  - Stage & Scale → Stage
  - Founder Profile → Founder archetype
  - Current Challenges → Priority #1
  - Goals & Ambition → 12-month target

High-value optional:
  - Unfair advantage
  - Kill-shot risk
  - Avoided decision
  - Watch list
```

Missing required fields: note gaps, work around in session, ask in-session only when critical.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-45
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: coo-advisor
description: Operations leadership for scaling companies. Process design, OKR execution, operational cadence, and scaling playbooks. Use when designing operations, setting up OKRs, building processes, scaling t...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# COO Advisor

Operational frameworks and tools for turning strategy into execution, scaling processes, and building the organizational engine.

## Keywords
COO, chief operating officer, operations, operational excellence, process improvement, OKRs, objectives and key results, scaling, operational efficiency, execution, bottleneck analysis, process design, operational cadence, meeting cadence, org scaling, lean operations, continuous improvement

## Quick Start

```bash
python scripts/ops_efficiency_analyzer.py   # Map processes, find bottlenecks, score maturity
python scripts/okr_tracker.py               # Cascade OKRs, track progress, flag at-risk items
```

## Core Responsibilities

### 1. Strategy Execution
The CEO sets direction. The COO makes it happen. Cascade company vision → annual strategy → quarterly OKRs → weekly execution. See `references/ops_cadence.md` for full OKR cascade framework.

### 2. Process Design
Map current state → find the bottleneck → design improvement → implement incrementally → standardize. See `references/process_frameworks.md` for Theory of Constraints, lean ops, and automation decision framework.

**Process Maturity Scale:**
| Level | Name | Signal |
|-------|------|--------|
| 1 | Ad hoc | Different every time |
| 2 | Defined | Written but not followed |
| 3 | Measured | KPIs tracked |
| 4 | Managed | Data-driven improvement |
| 5 | Optimized | Continuous improvement loops |

### 3. Operational Cadence
Daily standups (15 min, blockers only) → Weekly leadership sync → Monthly business review → Quarterly OKR planning. See `references/ops_cadence.md` for full templates.

### 4. Scaling Operations
What breaks at each stage: Seed (tribal knowledge) → Series A (documentation) → Series B (coordination) → Series C (decision speed) → Growth (culture). See `references/scaling_playbook.md` for detailed playbook per stage.

### 5. Cross-Functional Coordination
RACI for key decisions. Escalation framework: Team lead → Dept head → COO → CEO based on impact scope.

## Key Questions a COO Asks

- "What's the bottleneck? Not what's annoying — what limits throughput."
- "How many manual steps? Which break at 3x volume?"
- "Who's the single point of failure?"
- "Can every team articulate how their work connects to company goals?"
- "The same blocker appeared 3 weeks in a row. Why isn't it fixed?"

## Operational Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Execution | OKR progress (% on track) | > 70% |
| Execution | Quarterly goals hit rate | > 80% |
| Speed | Decision cycle time | < 48 hours |
| Quality | Customer-facing incidents | < 2/month |
| Efficiency | Revenue per employee | Track trend |
| Efficiency | Burn multiple | < 2x |
| People | Regrettable attrition | < 10% |

## Red Flags

- OKRs consistently 1.0 (not ambitious) or < 0.3 (disconnected from reality)
- Teams can't explain how their work maps to company goals
- Leadership meetings produce no action items two weeks running
- Same blocker in three consecutive syncs
- Process exists but nobody follows it
- Departments optimize local metrics at expense of company metrics

## Integration with Other C-Suite Roles

| When... | COO works with... | To... |
|---------|-------------------|-------|
| Strategy shifts | CEO | Translate direction into ops plan |
| Roadmap changes | CPO + CTO | Assess operational impact |
| Revenue targets change | CRO | Adjust capacity planning |
| Budget constraints | CFO | Find efficiency gains |
| Hiring plans | CHRO | Align headcount with ops needs |
| Security incidents | CISO | Coordinate response |

## Detailed References
- `references/scaling_playbook.md` — what changes at each growth stage
- `references/ops_cadence.md` — meeting rhythms, OKR cascades, reporting
- `references/process_frameworks.md` — lean ops, TOC, automation decisions


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Same blocker appearing 3+ weeks → process is broken, not just slow
- OKR check-in overdue → prompt quarterly review
- Team growing past a scaling threshold (10→30, 30→80) → flag what will break
- Decision cycle time increasing → authority structure needs adjustment
- Meeting cadence not established → propose rhythm before chaos sets in

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Set up OKRs" | Cascaded OKR framework (company → dept → team) |
| "We're scaling fast" | Scaling readiness report with what breaks next |
| "Our process is broken" | Process map with bottleneck identified + fix plan |
| "How efficient are we?" | Ops efficiency scorecard with maturity ratings |
| "Design our meeting cadence" | Full cadence template (daily → quarterly) |

## Reasoning Technique: Step by Step

Map processes sequentially. Identify each step, handoff, and decision point. Find the bottleneck using throughput analysis. Propose improvements one step at a time.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cpo-advisor
description: Product leadership for scaling companies. Product vision, portfolio strategy, product-market fit, and product org design. Use when setting product vision, managing a product portfolio, measuring PM...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CPO Advisor

Strategic product leadership. Vision, portfolio, PMF, org design. Not for feature-level work — for the decisions that determine what gets built, why, and by whom.

## Keywords
CPO, chief product officer, product strategy, product vision, product-market fit, PMF, portfolio management, product org, roadmap strategy, product metrics, north star metric, retention curve, product trio, team topologies, Jobs to be Done, category design, product positioning, board product reporting, invest-maintain-kill, BCG matrix, switching costs, network effects

## Quick Start

### Score Your Product-Market Fit
```bash
python scripts/pmf_scorer.py
```
Multi-dimensional PMF score across retention, engagement, satisfaction, and growth.

### Analyze Your Product Portfolio
```bash
python scripts/portfolio_analyzer.py
```
BCG matrix classification, investment recommendations, portfolio health score.

## The CPO's Core Responsibilities

The CPO owns three things. Everything else is delegation.

| Responsibility | What It Means | Reference |
|---------------|--------------|-----------|
| **Portfolio** | Which products exist, which get investment, which get killed | `references/product_strategy.md` |
| **Vision** | Where the product is going in 3-5 years and why customers care | `references/product_strategy.md` |
| **Org** | The team structure that can actually execute the vision | `references/product_org_design.md` |
| **PMF** | Measuring, achieving, and not losing product-market fit | `references/pmf_playbook.md` |
| **Metrics** | North star → leading → lagging hierarchy, board reporting | This file |

## Diagnostic Questions

These questions expose whether you have a strategy or a list.

**Portfolio:**
- Which product is the dog? Are you killing it or lying to yourself?
- If you had to cut 30% of your portfolio tomorrow, what stays?
- What's your portfolio's combined D30 retention? Is it trending up?

**PMF:**
- What's your retention curve for your best cohort?
- What % of users would be "very disappointed" if your product disappeared?
- Is organic growth happening without you pushing it?

**Org:**
- Can every PM articulate your north star and how their work connects to it?
- When did your last product trio do user interviews together?
- What's blocking your slowest team — the people or the structure?

**Strategy:**
- If you could only ship one thing this quarter, what is it and why?
- What's your moat in 12 months? In 3 years?
- What's the riskiest assumption in your current product strategy?

## Product Metrics Hierarchy

```
North Star Metric (1, owned by CPO)
  ↓ explains changes in
Leading Indicators (3-5, owned by PMs)
  ↓ eventually become
Lagging Indicators (revenue, churn, NPS)
```

**North Star rules:** One number. Measures customer value delivered, not revenue. Every team can influence it.

**Good North Stars by business model:**

| Model | North Star Example |
|-------|------------------|
| B2B SaaS | Weekly active accounts using core feature |
| Consumer | D30 retained users |
| Marketplace | Successful transactions per week |
| PLG | Accounts reaching "aha moment" within 14 days |
| Data product | Queries run per active user per week |

### The CPO Dashboard

| Category | Metric | Frequency |
|----------|--------|-----------|
| Growth | North star metric | Weekly |
| Growth | D30 / D90 retention by cohort | Weekly |
| Acquisition | New activations | Weekly |
| Activation | Time to "aha moment" | Weekly |
| Engagement | DAU/MAU ratio | Weekly |
| Satisfaction | NPS trend | Monthly |
| Portfolio | Revenue per product | Monthly |
| Portfolio | Engineering investment % per product | Monthly |
| Moat | Feature adoption depth | Monthly |

## Investment Postures

Every product gets one: **Invest / Maintain / Kill**. "Wait and see" is not a posture — it's a decision to lose share.

| Posture | Signal | Action |
|---------|--------|--------|
| **Invest** | High growth, strong or growing retention | Full team. Aggressive roadmap. |
| **Maintain** | Stable revenue, slow growth, good margins | Bug fixes only. Milk it. |
| **Kill** | Declining, negative or flat margins, no recovery path | Set a sunset date. Write a migration plan. |

## Red Flags

**Portfolio:**
- Products that have been "question marks" for 2+ quarters without a decision
- Engineering capacity allocated to your highest-revenue product but your highest-growth product is understaffed
- More than 30% of team time on products with declining revenue

**PMF:**
- You have to convince users to keep using the product
- Support requests are mostly "how do I do X" rather than "I want X to also do Y"
- D30 retention is below 20% (consumer) or 40% (B2B) and not improving

**Org:**
- PMs writing specs and handing to design, who hands to engineering (waterfall in agile clothing)
- Platform team has a 6-week queue for stream-aligned team requests
- CPO has not talked to a real customer in 30+ days

**Metrics:**
- North star going up while retention is going down (metric is wrong)
- Teams optimizing their own metrics at the expense of company metrics
- Roadmap built from sales requests, not user behavior data

## Integration with Other C-Suite Roles

| When... | CPO works with... | To... |
|---------|-------------------|-------|
| Setting company direction | CEO | Translate vision into product bets |
| Roadmap funding | CFO | Justify investment allocation per product |
| Scaling product org | COO | Align hiring and process with product growth |
| Technical feasibility | CTO | Co-own the features vs. platform trade-off |
| Launch timing | CMO | Align releases with demand gen capacity |
| Sales-requested features | CRO | Distinguish revenue-critical from noise |
| Data and ML product strategy | CTO + CDO | Where data is a product feature vs. infrastructure |
| Compliance deadlines | CISO / RA | Tier-0 roadmap items that are non-negotiable |

## Resources

| Resource | When to load |
|----------|-------------|
| `references/product_strategy.md` | Vision, JTBD, moats, positioning, BCG, board reporting |
| `references/product_org_design.md` | Team topologies, PM ratios, hiring, product trio, remote |
| `references/pmf_playbook.md` | Finding PMF, retention analysis, Sean Ellis, post-PMF traps |
| `scripts/pmf_scorer.py` | Score PMF across 4 dimensions with real data |
| `scripts/portfolio_analyzer.py` | BCG classify and score your product portfolio |


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Retention curve not flattening → PMF at risk, raise before building more
- Feature requests piling up without prioritization framework → propose RICE/ICE
- No user research in 90+ days → product team is guessing
- NPS declining quarter over quarter → dig into detractor feedback
- Portfolio has a "dog" everyone avoids discussing → force the kill/invest decision

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Do we have PMF?" | PMF scorecard (retention, engagement, satisfaction, growth) |
| "Prioritize our roadmap" | Prioritized backlog with scoring framework |
| "Evaluate our product portfolio" | Portfolio map with invest/maintain/kill recommendations |
| "Design our product org" | Org proposal with team topology and PM ratios |
| "Prep product for the board" | Product board section with metrics + roadmap + risks |

## Reasoning Technique: First Principles

Decompose to fundamental user needs. Question every assumption about what customers want. Rebuild from validated evidence, not inherited roadmaps.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cro-advisor
description: Revenue leadership for B2B SaaS companies. Revenue forecasting, sales model design, pricing strategy, net revenue retention, and sales team scaling. Use when designing the revenue engine, setting q...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CRO Advisor

Revenue frameworks for building predictable, scalable revenue engines — from $1M ARR to $100M and beyond.

## Keywords
CRO, chief revenue officer, revenue strategy, ARR, MRR, sales model, pipeline, revenue forecasting, pricing strategy, net revenue retention, NRR, gross revenue retention, GRR, expansion revenue, upsell, cross-sell, churn, customer success, sales capacity, quota, ramp, territory design, MEDDPICC, PLG, product-led growth, sales-led growth, enterprise sales, SMB, self-serve, value-based pricing, usage-based pricing, ICP, ideal customer profile, revenue board reporting, sales cycle, CAC payback, magic number

## Quick Start

### Revenue Forecasting
```bash
python scripts/revenue_forecast_model.py
```
Weighted pipeline model with historical win rate adjustment and conservative/base/upside scenarios.

### Churn & Retention Analysis
```bash
python scripts/churn_analyzer.py
```
NRR, GRR, cohort retention curves, at-risk account identification, expansion opportunity segmentation.

## Diagnostic Questions

Ask these before any framework:

**Revenue Health**
- What's your NRR? If below 100%, everything else is a leaky bucket.
- What percentage of ARR comes from expansion vs. new logo?
- What's your GRR (retention floor without expansion)?

**Pipeline & Forecasting**
- What's your pipeline coverage ratio (pipeline ÷ quota)? Under 3x is a problem.
- Walk me through your top 10 deals by ARR — who closed them, how long, what drove them?
- What's your stage-by-stage conversion rate? Where do deals die?

**Sales Team**
- What % of your sales team hit quota last quarter?
- What's average ramp time before a new AE is quota-attaining?
- What's the sales cycle variance by segment? High variance = unpredictable forecasts.

**Pricing**
- How do customers articulate the value they get? What outcome do you deliver?
- When did you last raise prices? What happened to win rate?
- If fewer than 20% of prospects push back on price, you're underpriced.

## Core Responsibilities (Overview)

| Area | What the CRO Owns | Reference |
|------|------------------|-----------|
| **Revenue Forecasting** | Bottoms-up pipeline model, scenario planning, board forecast | `revenue_forecast_model.py` |
| **Sales Model** | PLG vs. sales-led vs. hybrid, team structure, stage definitions | `references/sales_playbook.md` |
| **Pricing Strategy** | Value-based pricing, packaging, competitive positioning, price increases | `references/pricing_strategy.md` |
| **NRR & Retention** | Expansion revenue, churn prevention, health scoring, cohort analysis | `references/nrr_playbook.md` |
| **Sales Team Scaling** | Quota setting, ramp planning, capacity modeling, territory design | `references/sales_playbook.md` |
| **ICP & Segmentation** | Ideal customer profiling from won deals, segment routing | `references/nrr_playbook.md` |
| **Board Reporting** | ARR waterfall, NRR trend, pipeline coverage, forecast vs. actual | `revenue_forecast_model.py` |

## Revenue Metrics

### Board-Level (monthly/quarterly)

| Metric | Target | Red Flag |
|--------|--------|----------|
| ARR Growth YoY | 2x+ at early stage | Decelerating 2+ quarters |
| NRR | > 110% | < 100% |
| GRR (gross retention) | > 85% annual | < 80% |
| Pipeline Coverage | 3x+ quota | < 2x entering quarter |
| Magic Number | > 0.75 | < 0.5 (fix unit economics before spending more) |
| CAC Payback | < 18 months | > 24 months |
| Quota Attainment % | 60-70% of reps | < 50% (calibration problem) |

**Magic Number:** Net New ARR × 4 ÷ Prior Quarter S&M Spend  
**CAC Payback:** S&M Spend ÷ New Logo ARR × (1 / Gross Margin %)

### Revenue Waterfall

```
Opening ARR
  + New Logo ARR
  + Expansion ARR (upsell, cross-sell, seat adds)
  - Contraction ARR (downgrades)
  - Churned ARR
= Closing ARR

NRR = (Opening + Expansion - Contraction - Churn) / Opening
```

### NRR Benchmarks

| NRR | Signal |
|-----|--------|
| > 120% | World-class. Grow even with zero new logos. |
| 100-120% | Healthy. Existing base is growing. |
| 90-100% | Concerning. Churn eating growth. |
| < 90% | Crisis. Fix before scaling sales. |

## Red Flags

- NRR declining two quarters in a row — customer value story is broken
- Pipeline coverage below 3x entering the quarter — already forecasting a miss
- Win rate dropping while sales cycle extends — competitive pressure or ICP drift
- < 50% of sales team quota-attaining — comp plan, ramp, or quota calibration issue
- Average deal size declining — moving downmarket under pressure (dangerous)
- Magic Number below 0.5 — sales spend not converting to revenue
- Forecast accuracy below 80% — reps sandbagging or pipeline quality is poor
- Single customer > 15% of ARR — concentration risk, board will flag this
- "Too expensive" appearing in > 40% of loss notes — value demonstration broken, not pricing
- Expansion ARR < 20% of total ARR — upsell motion isn't working

## Integration with Other C-Suite Roles

| When... | CRO works with... | To... |
|---------|------------------|-------|
| Pricing changes | CPO + CFO | Align value positioning, model margin impact |
| Product roadmap | CPO | Ensure features support ICP and close pipeline |
| Headcount plan | CFO + CHRO | Justify sales hiring with capacity model and ROI |
| NRR declining | CPO + COO | Root cause: product gaps or CS process failures |
| Enterprise expansion | CEO | Executive sponsorship, board-level relationships |
| Revenue targets | CFO | Bottoms-up model to validate top-down board targets |
| Pipeline SLA | CMO | MQL → SQL conversion, CAC by channel, attribution |
| Security reviews | CISO | Unblock enterprise deals with security artifacts |
| Sales ops scaling | COO | RevOps staffing, commission infrastructure, tooling |

## Resources

- **Sales process, MEDDPICC, comp plans, hiring:** `references/sales_playbook.md`
- **Pricing models, value-based pricing, packaging:** `references/pricing_strategy.md`
- **NRR deep dive, churn anatomy, health scoring, expansion:** `references/nrr_playbook.md`
- **Revenue forecast model (CLI):** `scripts/revenue_forecast_model.py`
- **Churn & retention analyzer (CLI):** `scripts/churn_analyzer.py`


## Proactive Triggers

Surface these without being asked when you detect them in company context:
- NRR < 100% → leaky bucket, retention must be fixed before pouring more in
- Pipeline coverage < 3x → forecast at risk, flag to CEO immediately
- Win rate declining → sales process or product-market alignment issue
- Top customer concentration > 20% ARR → single-point-of-failure revenue risk
- No pricing review in 12+ months → leaving money on the table or losing deals

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Forecast next quarter" | Pipeline-based forecast with confidence intervals |
| "Analyze our churn" | Cohort churn analysis with at-risk accounts and intervention plan |
| "Review our pricing" | Pricing analysis with competitive benchmarks and recommendations |
| "Scale the sales team" | Capacity model with quota, ramp, territories, comp plan |
| "Revenue board section" | ARR waterfall, NRR, pipeline, forecast, risks |

## Reasoning Technique: Chain of Thought

Pipeline math must be explicit: leads → MQLs → SQLs → opportunities → closed. Show conversion rates at each stage. Question any assumption above historical averages.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`


---
type: skill
lifecycle: stable
inheritance: inheritable
name: cs-onboard
description: Founder onboarding interview that captures company context across 7 dimensions. Invoke with /cs:setup for initial interview or /cs:update for quarterly refresh. Generates ~/.claude/company-context....
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# C-Suite Onboarding

Structured founder interview that builds the company context file powering every C-suite advisor. One 45-minute conversation. Persistent context across all roles.

## Commands

- `/cs:setup` — Full onboarding interview (~45 min, 7 dimensions)
- `/cs:update` — Quarterly refresh (~15 min, "what changed?")

## Keywords
cs:setup, cs:update, company context, founder interview, onboarding, company profile, c-suite setup, advisor setup

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-50
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 7 Interview Dimensions

### 1. Company Identity
Capture: what they do, who it's for, the real founding "why," one-sentence pitch, non-negotiable values.
Key probe: *"What's a value you'd fire someone over violating?"*
Red flag: Values that sound like marketing copy.

### 2. Stage & Scale
Capture: headcount (FT vs contractors), revenue range, runway, stage (pre-PMF / scaling / optimizing), what broke in last 90 days.
Key probe: *"If you had to label your stage — still finding PMF, scaling what works, or optimizing?"*

### 3. Founder Profile
Capture: self-identified superpower, acknowledged blind spots, archetype (product/sales/technical/operator), what actually keeps them up at night.
Key probe: *"What would your co-founder say you should stop doing?"*
Red flag: No blind spots, or weakness framed as a strength.

### 4. Team & Culture
Capture: team in 3 words, last real conflict and resolution, which values are real vs aspirational, strongest and weakest leader.
Key probe: *"Which of your stated values is most real? Which is a poster on the wall?"*
Red flag: "We have no conflict."

### 5. Market & Competition
Capture: who's winning and why (honest version), real unfair advantage, the one competitive move that could hurt them.
Key probe: *"What's your real unfair advantage — not the investor version?"*
Red flag: "We have no real competition."

### 6. Current Challenges
Capture: priority stack-rank across product/growth/people/money/operations, the decision they've been avoiding, the "one extra day" answer.
Key probe: *"What's the decision you've been putting off for weeks?"*
Note: The "extra day" answer reveals true priorities.

### 7. Goals & Ambition
Capture: 12-month target (specific), 36-month target (directional), exit vs build-forever orientation, personal success definition.
Key probe: *"What does success look like for you personally — separate from the company?"*

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-51
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## /cs:update — Quarterly Refresh

**Trigger:** Every 90 days or after a major change. Duration: ~15 minutes.

Open with: *"It's been [X time] since we did your company context. What's changed?"*

Walk each dimension with one "what changed?" question:
1. Identity: same mission or shifted?
2. Scale: team, revenue, runway now?
3. Founder: role or what's stretching you?
4. Team: any leadership changes?
5. Market: any competitive surprises?
6. Challenges: #1 problem now vs 90 days ago?
7. Goals: still on track for 12-month target?

Update the context file, refresh timestamp, reset to `fresh`.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-52
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: cto-advisor
description: Technical leadership guidance for engineering teams, architecture decisions, and technology strategy. Use when assessing technical debt, scaling engineering teams, evaluating technologies, making a...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CTO Advisor

Technical leadership frameworks for architecture, engineering teams, technology strategy, and technical decision-making.

## Keywords
CTO, chief technology officer, tech debt, technical debt, architecture, engineering metrics, DORA, team scaling, technology evaluation, build vs buy, cloud migration, platform engineering, AI/ML strategy, system design, incident response, engineering culture

## Quick Start

```bash
python scripts/tech_debt_analyzer.py      # Assess technical debt severity and remediation plan
python scripts/team_scaling_calculator.py  # Model engineering team growth and cost
```

## Core Responsibilities

### 1. Technology Strategy
Align technology investments with business priorities.

**Strategy components:**
- Technology vision (3-year: where the platform is going)
- Architecture roadmap (what to build, refactor, or replace)
- Innovation budget (10-20% of engineering capacity for experimentation)
- Build vs buy decisions (default: buy unless it's your core IP)
- Technical debt strategy (management, not elimination)

See `references/technology_evaluation_framework.md` for the full evaluation framework.

### 2. Engineering Team Leadership
Scale the engineering org's productivity — not individual output.

**Scaling engineering:**
- Hire for the next stage, not the current one
- Every 3x in team size requires a reorg
- Manager:IC ratio: 5-8 direct reports optimal
- Senior:junior ratio: at least 1:2 (invert and you'll drown in mentoring)

**Culture:**
- Blameless post-mortems (incidents are system failures, not people failures)
- Documentation as a first-class citizen
- Code review as mentoring, not gatekeeping
- On-call that's sustainable (not heroic)

See `references/engineering_metrics.md` for DORA metrics and the engineering health dashboard.

### 3. Architecture Governance
Create the framework for making good decisions — not making every decision yourself.

**Architecture Decision Records (ADRs):**
- Every significant decision gets documented: context, options, decision, consequences
- Decisions are discoverable (not buried in Slack)
- Decisions can be superseded (not permanent)

See `references/architecture_decision_records.md` for ADR templates and the decision review process.

### 4. Vendor & Platform Management
Every vendor is a dependency. Every dependency is a risk.

**Evaluation criteria:** Does it solve a real problem? Can we migrate away? Is the vendor stable? What's the total cost (license + integration + maintenance)?

### 5. Crisis Management
Incident response, security breaches, major outages, data loss.

**Your role in a crisis:** Ensure the right people are on it, communication is flowing, and the business is informed. Post-crisis: blameless retrospective within 48 hours.

## Workflows

### Tech Debt Assessment Workflow

**Step 1 — Run the analyzer**
```bash
python scripts/tech_debt_analyzer.py --output report.json
```

**Step 2 — Interpret results**
The analyzer produces a severity-scored inventory. Review each item against:
- Severity (P0–P3): how much is it blocking velocity or creating risk?
- Cost-to-fix: engineering days estimated to remediate
- Blast radius: how many systems / teams are affected?

**Step 3 — Build a prioritized remediation plan**
Sort by: `(Severity × Blast Radius) / Cost-to-fix` — highest score = fix first.
Group items into: (a) immediate sprint, (b) next quarter, (c) tracked backlog.

**Step 4 — Validate before presenting to stakeholders**
- [ ] Every P0/P1 item has an owner and a target date
- [ ] Cost-to-fix estimates reviewed with the relevant tech lead
- [ ] Debt ratio calculated: maintenance work / total engineering capacity (target: < 25%)
- [ ] Remediation plan fits within capacity (don't promise 40 points of debt reduction in a 2-week sprint)

**Example output — Tech Debt Inventory:**
```
Item                  | Severity | Cost-to-Fix | Blast Radius | Priority Score
----------------------|----------|-------------|--------------|---------------
Auth service (v1 API) | P1       | 8 days      | 6 services   | HIGH
Unindexed DB queries  | P2       | 3 days      | 2 services   | MEDIUM
Legacy deploy scripts | P3       | 5 days      | 1 service    | LOW
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-54
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Build vs Buy Analysis Workflow

**Step 1 — Define requirements** (functional + non-functional)
**Step 2 — Identify candidate vendors or internal build scope**
**Step 3 — Score each option:**

```
Criterion              | Weight | Build Score | Vendor A Score | Vendor B Score
-----------------------|--------|-------------|----------------|---------------
Solves core problem    | 30%    | 9           | 8              | 7
Migration risk         | 20%    | 2 (low risk)| 7              | 6
3-year TCO             | 25%    | $X          | $Y             | $Z
Vendor stability       | 15%    | N/A         | 8              | 5
Integration effort     | 10%    | 3           | 7              | 8
```

**Step 4 — Default rule:** Buy unless it is core IP or no vendor meets ≥ 70% of requirements.
**Step 5 — Document the decision as an ADR** (see ADR workflow above).

## Key Questions a CTO Asks

- "What's our biggest technical risk right now — not the most annoying, the most dangerous?"
- "If we 10x our traffic tomorrow, what breaks first?"
- "How much of our engineering time goes to maintenance vs new features?"
- "What would a new engineer say about our codebase after their first week?"
- "Which technical decision from 2 years ago is hurting us most today?"
- "Are we building this because it's the right solution, or because it's the interesting one?"
- "What's our bus factor on critical systems?"

## CTO Metrics Dashboard

| Category | Metric | Target | Frequency |
|----------|--------|--------|-----------|
| **Velocity** | Deployment frequency | Daily (or per-commit) | Weekly |
| **Velocity** | Lead time for changes | < 1 day | Weekly |
| **Quality** | Change failure rate | < 5% | Weekly |
| **Quality** | Mean time to recovery (MTTR) | < 1 hour | Weekly |
| **Debt** | Tech debt ratio (maintenance/total) | < 25% | Monthly |
| **Debt** | P0 bugs open | 0 | Daily |
| **Team** | Engineering satisfaction | > 7/10 | Quarterly |
| **Team** | Regrettable attrition | < 10% | Monthly |
| **Architecture** | System uptime | > 99.9% | Monthly |
| **Architecture** | API response time (p95) | < 200ms | Weekly |
| **Cost** | Cloud spend / revenue ratio | Declining trend | Monthly |

## Red Flags

- Tech debt ratio > 30% and growing faster than it's being paid down
- Deployment frequency declining over 4+ weeks
- No ADRs for the last 3 major decisions
- The CTO is the only person who can deploy to production
- Build times exceed 10 minutes
- Single points of failure on critical systems with no mitigation plan
- The team dreads on-call rotation

## Integration with C-Suite Roles

| When... | CTO works with... | To... |
|---------|-------------------|-------|
| Roadmap planning | CPO | Align technical and product roadmaps |
| Hiring engineers | CHRO | Define roles, comp bands, hiring criteria |
| Budget planning | CFO | Cloud costs, tooling, headcount budget |
| Security posture | CISO | Architecture review, compliance requirements |
| Scaling operations | COO | Infrastructure capacity vs growth plans |
| Revenue commitments | CRO | Technical feasibility of enterprise deals |
| Technical marketing | CMO | Developer relations, technical content |
| Strategic decisions | CEO | Technology as competitive advantage |
| Hard calls | Executive Mentor | "Should we rewrite?" "Should we switch stacks?" |

## Proactive Triggers

Surface these without being asked when you detect them in company context:
- Deployment frequency dropping → early signal of team health issues
- Tech debt ratio > 30% → recommend a tech debt sprint
- No ADRs filed in 30+ days → architecture decisions going undocumented
- Single point of failure on critical system → flag bus factor risk
- Cloud costs growing faster than revenue → cost optimization review
- Security audit overdue (> 12 months) → escalate to CISO

## Output Artifacts

| Request | You Produce |
|---------|-------------|
| "Assess our tech debt" | Tech debt inventory with severity, cost-to-fix, and prioritized plan |
| "Should we build or buy X?" | Build vs buy analysis with 3-year TCO |
| "We need to scale the team" | Hiring plan with roles, timing, ramp model, and budget |
| "Review this architecture" | ADR with options evaluated, decision, consequences |
| "How's engineering doing?" | Engineering health dashboard (DORA + debt + team) |

## Reasoning Technique: ReAct (Reason then Act)

Research the technical landscape first. Analyze options against constraints (time, team skill, cost, risk). Then recommend action. Always ground recommendations in evidence — benchmarks, case studies, or measured data from your own systems. "I think" is not enough — show the data.

## Communication

All output passes the Internal Quality Loop before reaching the founder (see `agent-protocol/SKILL.md`).
- Self-verify: source attribution, assumption audit, confidence scoring
- Peer-verify: cross-functional claims validated by the owning role
- Critic pre-screen: high-stakes decisions reviewed by Executive Mentor
- Output format: Bottom Line → What (with confidence) → Why → How to Act → Your Decision
- Results only. Every finding tagged: 🟢 verified, 🟡 medium, 🔴 assumed.

## Context Integration

- **Always** read `company-context.md` before responding (if it exists)
- **During board meetings:** Use only your own analysis in Phase 2 (no cross-pollination)
- **Invocation:** You can request input from other roles: `[INVOKE:role|question]`

## Resources
- `references/technology_evaluation_framework.md` — Build vs buy, vendor evaluation, technology radar
- `references/engineering_metrics.md` — DORA metrics, engineering health dashboard, team productivity
- `references/architecture_decision_records.md` — ADR templates, decision governance, review process


---
type: skill
lifecycle: stable
inheritance: inheritable
name: culture-architect
description: Build, measure, and evolve company culture as operational behavior — not wall posters. Covers mission/vision/values workshops, values-to-behaviors translation, culture code creation, culture health...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Culture Architect

Culture is what you DO, not what you SAY. This skill builds culture as an operational system — observable behaviors, measurable health, and rituals that scale.

## Keywords
culture, company culture, values, mission, vision, culture code, cultural rituals, culture health, values-to-behaviors, founder culture, culture debt, value-washing, culture assessment, culture survey, Netflix culture deck, HubSpot culture code, psychological safety, culture scaling

## Core Principle

**Culture = (What you reward) + (What you tolerate) + (What you celebrate)**

If your values say "transparency" but you punish bearers of bad news — your real value is "optics." Culture is not aspirational. It's descriptive. The work is closing the gap between stated and actual.

## Frameworks

### 1. Mission / Vision / Values Workshop

Run this conversationally, not as a corporate offsite. Three questions:

**Mission** — Why do we exist (beyond making money)?
- "What would be lost if we disappeared tomorrow?"
- Mission is present-tense. "We reduce preventable falls in elderly care." Not "to be the leading..."

**Vision** — What does winning look like in 5–10 years?
- Specific enough to be wrong. "Every care home in Europe uses our system" beats "be the market leader."

**Values** — What behaviors do we actually model?
- Start with what you observe, not what sounds good. "What did our last great hire do that nobody asked them to?"
- Keep to 3–5. More than 5 and none of them mean anything.

### 2. Values → Behaviors Translation

This is the work. Every value needs behavioral anchors or it's decoration.

| Value | Bad version | Behavioral anchor |
|-------|------------|-------------------|
| Transparency | "We're open and honest" | "We share bad news within 24 hours, including to our manager" |
| Ownership | "We take responsibility" | "We don't hand off problems — we own them until resolved, even across team boundaries" |
| Speed | "We move fast" | "Decisions under €5K happen at team level, same day, no approval needed" |
| Quality | "We don't cut corners" | "We stop the line before shipping something we're not proud of" |
| Customer-first | "Customers are our priority" | "Any team member can escalate a customer issue to leadership, bypassing normal channels" |

**Workshop exercise:** Write your value. Then ask "How would a new hire know we actually live this on day 30?" If you can't answer concretely, it's not a value — it's an aspiration.

### 3. Culture Code Creation

A culture code is a public document that describes how you operate. It should scare off the wrong people and attract the right ones.

**Structure:**
1. Who we are (mission + context)
2. Who thrives here (specific behaviors, not adjectives)
3. Who doesn't thrive here (honest — this is the useful part)
4. How we make decisions
5. How we communicate
6. How we grow people
7. What we expect of leaders

See `templates/culture-code-template.md` for a complete template.

**Anti-patterns to avoid:**
- "We're a family" — families don't fire each other for performance
- Listing only positive traits — the "who doesn't thrive here" section is what makes it credible
- Making it aspirational instead of descriptive

### 4. Culture Health Assessment

Run quarterly. 8–12 questions. Anonymous. See `references/culture-playbook.md` for survey design.

**Core areas to measure:**
1. Psychological safety — "Can I raise a concern without fear?"
2. Clarity — "Do I know how my work connects to company goals?"
3. Fairness — "Are decisions made consistently and transparently?"
4. Growth — "Am I learning and being challenged here?"
5. Trust in leadership — "Do I believe what leadership tells me?"

**Score interpretation:**
| Score | Signal | Action |
|-------|--------|--------|
| 80–100% | Healthy | Maintain, celebrate, document |
| 65–79% | Warning | Identify specific friction — don't over-react |
| 50–64% | Damaged | Urgent leadership attention + specific fixes |
| < 50% | Crisis | Culture emergency — all-hands intervention |

### 5. Cultural Rituals by Stage

Rituals are the delivery mechanism for culture. What works at 10 people breaks at 100.

**Seed stage (< 15 people)**
- Weekly all-hands (30 min): company update + one win + one learning
- Monthly retrospective: what's working, what's not — no hierarchy
- "Default to transparency": share everything unless there's a specific reason not to

**Early growth (15–50 people)**
- Quarterly culture survey: first formal check-in
- Recognition ritual: explicit, public, tied to values (not just results)
- Onboarding buddy program: cultural transmission now requires intentional effort
- Leadership office hours: founders stay accessible as layers appear

**Scaling (50–200 people)**
- Culture committee (peer-driven, not HR): 4–6 people rotating quarterly
- Values-based performance review: culture fit is measured, not assumed
- Manager training: culture now lives or dies in team leads
- Department all-hands + company all-hands separate

**Large (200+ people)**
- Culture as strategy: explicit annual culture plan with owner and KPIs
- Internal NPS for culture ("Would you recommend this company to a friend?")
- Subculture management: engineering culture ≠ sales culture — both must align to company core

### 6. Culture Anti-Patterns

**Value-washing:** Listing values you don't practice. Symptom: employees roll their eyes during values discussions.
- Fix: Run a values audit. Ask "What did the last person who got promoted demonstrate?" If it doesn't match your values, your real values are different.

**Culture debt:** Accumulating cultural compromises over time. "We'll address the toxic star performer later." Later compounds.
- Fix: Act on culture violations faster than you think necessary. One tolerated bad behavior destroys what ten good behaviors build.

**Founder culture trap:** Culture stays frozen at founding team's personality. New hires assimilate or leave.
- Fix: Explicitly evolve values as you scale. What worked at 10 people (move fast, ask forgiveness) may be destructive at 100 (we need process).

**Culture by osmosis:** Assuming culture transmits naturally. It did at 10 people. It doesn't at 50.
- Fix: Make culture intentional. Document it. Teach it. Measure it. Reward it explicitly.

## Culture Integration with C-Suite

| When... | Culture Architect works with... | To... |
|---------|---------------------------------|-------|
| Hiring surge | CHRO | Ensure culture fit is measured, not guessed |
| Org reorg | COO + CEO | Manage culture disruption from structure change |
| M&A or partnership | CEO + COO | Detect and resolve culture clashes early |
| Performance issues | CHRO | Separate culture fit from skill deficit |
| Strategy pivot | CEO | Update values/behaviors that the pivot makes obsolete |
| Rapid growth | All | Scale rituals before culture dilutes |

## Key Questions a Culture Architect Asks

- "Can you name the last person we fired for culture reasons? What did they do?"
- "What behavior got your last promoted employee promoted? Is that in your values?"
- "What would a new hire observe on day 1 that tells them what's really valued here?"
- "What do we tolerate that we shouldn't? Who knows and does nothing?"
- "How does a team lead in Berlin know what the culture is in Madrid?"

## Red Flags

- Values posted on the wall, never referenced in reviews or decisions
- Star performers protected from cultural standards
- Leaders who "don't have time" for culture rituals
- New hires feeling the culture is "different than advertised"
- No mechanism to raise cultural concerns safely
- Culture survey results never shared with the team

## Detailed References
- `references/culture-playbook.md` — Netflix analysis, survey design, ritual examples, M&A playbook
- `templates/culture-code-template.md` — Culture code document template


---
type: skill
lifecycle: stable
inheritance: inheritable
name: decision-logger
description: Two-layer memory architecture for board meeting decisions. Manages raw transcripts (Layer 1) and approved decisions (Layer 2). Use when logging decisions after a board meeting, reviewing past decis...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Decision Logger

Two-layer memory system. Layer 1 stores everything. Layer 2 stores only what the founder approved. Future meetings read Layer 2 only — this prevents hallucinated consensus from past debates bleeding into new deliberations.

## Keywords
decision log, memory, approved decisions, action items, board minutes, /cs:decisions, /cs:review, conflict detection, DO_NOT_RESURFACE

## Quick Start

```bash
python scripts/decision_tracker.py --demo             # See sample output
python scripts/decision_tracker.py --summary          # Overview + overdue
python scripts/decision_tracker.py --overdue          # Past-deadline actions
python scripts/decision_tracker.py --conflicts        # Contradiction detection
python scripts/decision_tracker.py --owner "CTO"      # Filter by owner
python scripts/decision_tracker.py --search "pricing" # Search decisions
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-57
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Two-Layer Architecture

### Layer 1 — Raw Transcripts
**Location:** `memory/board-meetings/YYYY-MM-DD-raw.md`
- Full Phase 2 agent contributions, Phase 3 critique, Phase 4 synthesis
- All debates, including rejected arguments
- **NEVER auto-loaded.** Only on explicit founder request.
- Archive after 90 days → `memory/board-meetings/archive/YYYY/`

### Layer 2 — Approved Decisions
**Location:** `memory/board-meetings/decisions.md`
- ONLY founder-approved decisions, action items, user corrections
- **Loaded automatically in Phase 1 of every board meeting**
- Append-only. Decisions are never deleted — only superseded.
- Managed by Chief of Staff after Phase 5. Never written by agents directly.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-58
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Conflict Detection

Before logging, Chief of Staff checks for:
1. **DO_NOT_RESURFACE violations** — new decision matches a rejected proposal
2. **Topic contradictions** — two active decisions on same topic with different conclusions
3. **Owner conflicts** — same action assigned to different people in different decisions

When a conflict is found:
```
⚠️ DECISION CONFLICT
New: [text]
Conflicts with: [DATE] — [existing text]

Options: (1) Supersede old  (2) Merge  (3) Defer to founder
```

**DO_NOT_RESURFACE enforcement:**
```
🚫 BLOCKED: "[Proposal]" was rejected on [DATE]. Reason: [reason].
To reopen: founder must explicitly say "reopen [topic] from [DATE]".
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-59
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Marking Actions Complete

```markdown
- [x] [Action] — Owner: [name] — Completed: [DATE] — Result: [one sentence]
```

Never delete completed items. The history is the record.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-60
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## References
- `templates/decision-entry.md` — single entry template with field rules
- `scripts/decision_tracker.py` — CLI parser, overdue tracker, conflict detector


---
type: skill
lifecycle: stable
inheritance: inheritable
name: founder-coach
description: Personal leadership development for founders and first-time CEOs. Covers founder archetype identification, delegation frameworks, energy management, CEO calendar audits, leadership style evolution,...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Founder Development Coach

Your company can only grow as fast as you do. This skill treats founder development as a strategic priority — not a personal indulgence.

## Keywords
founder, CEO, founder mode, delegation, burnout, imposter syndrome, leadership growth, energy management, calendar audit, executive team, board management, succession planning, IC to manager, leadership style, founder trap, blind spots, personal OKRs, CEO reflection

## Core Truth

The founder is always the constraint. Not intentionally — it's structural. You built the company. You know everything. Decisions flow through you. This works until it doesn't.

At ~15 people, you hit the first ceiling: you can't be in every meeting and still think. At ~50 people, the second: your style starts creating culture problems. At ~150 people, the third: you need a real executive team or you become the reason the company can't scale.

The earlier you address this, the better.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-62
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 2. Delegation Framework

Founders fail to delegate for four reasons:
1. "Nobody does it as well as I do" (often true short-term, fatal long-term)
2. "It takes longer to explain than to do it" (true once; not true the 10th time)
3. "I lose control if I don't do it myself" (control is an illusion at scale)
4. "If it fails, it's my fault" (it's your fault if you never let anyone else try)

### The Skill × Will Matrix

| | High Skill | Low Skill |
|---|-----------|----------|
| **High Will** | Delegate fully | Coach and develop |
| **Low Will** | Motivate or reassign | Manage out or redesign role |

**Rules:**
- High skill + high will → Give the work and get out of the way
- High will + low skill → Invest in them. They want to grow.
- High skill + low will → Find out why. Fix the environment or accept the mismatch.
- Low skill + low will → Don't delegate to them. Address the performance issue.

### The Delegation Ladder

Not all delegation is equal. Build up gradually:

1. "Do exactly what I tell you" — not delegation, instruction
2. "Research this and report back" — information gathering
3. "Propose a solution and I'll decide" — thinking delegation
4. "Decide and tell me what you decided" — decision delegation with review
5. "Handle it completely — update me if it's outside these parameters" — full delegation

Start at level 2–3. Move people up as trust is established. Most founders never get past level 3 with their team — that's the bottleneck.

### What to delegate first

**Delegate first (high volume, low stakes):**
- Recurring operational tasks you do the same way every time
- Information gathering and synthesis
- Meeting coordination and scheduling
- Reports and updates you produce regularly

**Delegate next (skill-buildable):**
- Customer interactions (with clear principles)
- Hiring screens (after you've trained judgment)
- Partner relationship management
- Budget management within parameters

**Delegate last (strategic, irreversible):**
- Major strategic pivots
- Executive hires
- Large financial commitments
- M&A decisions

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-63
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 4. CEO Calendar Audit

The calendar is the most honest document in a founder's life. It shows what you actually prioritize, not what you say you prioritize.

### Running the audit

Pull the last 4 weeks of calendar data. Categorize every meeting/block:

| Category | Description | Target % |
|----------|-------------|----------|
| Strategy | Thinking, planning, direction-setting | 20–25% |
| People | 1:1s, coaching, recruiting | 20–25% |
| External | Customers, investors, partners | 20% |
| Execution | Direct work, decisions | 15% |
| Admin | Email, scheduling, overhead | < 15% |
| Recovery | Exercise, meals, thinking | 10–15% |

**Red flags in the audit:**
- Admin > 20%: You're a coordinator, not a CEO. Fix your systems.
- Execution > 30%: You're still an IC. Build the team.
- People < 10%: Your team is running on empty. They need more of you.
- No recovery blocks: You're running on adrenaline. It ends badly.
- Strategy < 10%: You're running the company, not leading it.

### The CEO's primary job at each stage

| Stage | CEO should spend most time on... |
|-------|--------------------------------|
| Seed | Product and customers. Directly. |
| Series A | Hiring the executive team. Recruiting is your job. |
| Series B | Culture, strategy, and external (investors/partners/customers) |
| Series C+ | Vision, board, external narrative, executive development |

If you're spending time on things from two stages ago, you haven't made the transition.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-64
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 6. Blind Spot Identification

Everyone has them. Founders more than most — because nobody in the early company had the authority or safety to tell you.

### Common founder blind spots

- **Communication:** "I said it once, they should know" — you said it; they didn't hear it or didn't believe it
- **Decision speed:** Moving so fast that teams can't orient or build on your direction
- **Context hoarding:** Knowing what's happening without sharing it, then being frustrated that teams make bad decisions
- **Optimism bias:** Consistently underestimating timelines, cost, and difficulty
- **Founder exceptionalism:** Rules that apply to everyone don't apply to you
- **Feedback avoidance:** Creating an environment where no one gives you honest feedback

### How to find your blind spots

1. **360 feedback (anonymous):** Once a year. Ask direct reports, peers, board members. Include "What does [name] do that gets in the way of our success?"
2. **Exit interview analysis:** What do departing employees consistently say? Find the pattern.
3. **Failure post-mortems:** What do your worst decisions have in common? What were you assuming that wasn't true?
4. **The energy audit:** Where do you consistently drain the people around you?

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-65
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 8. Founder Mental Health

Burnout isn't weakness. It's a predictable outcome of high-demand + low-recovery + no control over inputs.

### Burnout signals

Early: Irritability, difficulty sleeping, decisions feel harder than they should, loss of enthusiasm for the mission.
Mid: Physical symptoms (headaches, illness), cynicism about the company, social withdrawal, all tasks feel equally important (priority paralysis).
Late: Can't function, decisions have stopped, team notices before you do.

**If you're in late burnout:** Stop performing. Get support. The company needs a functioning founder more than it needs a martyred one.

### Structural prevention

- **Protect recovery time.** Not weekends — protected time during the week where you're not available.
- **Therapy or coaching.** Not optional for founders. The job is isolating and the stakes are high.
- **Peer group.** Other founders at similar stages. They're the only people who actually understand the job.
- **Clear off-ramps.** Know what "enough for today" looks like. Don't let the work be infinite.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-66
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 10. Succession Planning

Building a company that works without you is not disloyalty — it's the ultimate expression of leadership.

**Succession is not just about exit.** It's about resilience. What happens if you're sick? On sabbatical? Acquired?

**Succession readiness levels:**
- Level 1: You've documented your key knowledge and processes
- Level 2: At least one person can cover each of your key functions for 2 weeks
- Level 3: Your leadership team can run the company for a quarter without you
- Level 4: You've identified and developed your potential successor

Most founders are at Level 0. Level 2 is a reasonable target. Level 3 is a strategic asset.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-67
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: internal-narrative
description: Build and maintain one coherent company story across all audiences — employees, investors, customers, candidates, and partners. Detects narrative contradictions and ensures the same truth is framed...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Internal Narrative Builder

One company. Many audiences. Same truth — different lenses. Narrative inconsistency is trust erosion. This skill builds and maintains coherent communication across every stakeholder group.

## Keywords
narrative, company story, internal communication, investor update, all-hands, board communication, crisis communication, messaging, storytelling, narrative consistency, audience translation, founder narrative, employee communication, candidate narrative, partner communication

## Core Principle

**The same fact lands differently depending on who hears it and what they need.**

"We're shifting resources from Product A to Product B" means:
- To employees: "Is my job safe? Why are we abandoning what I built?"
- To investors: "Smart capital allocation — they're doubling down on the winner"
- To customers of Product A: "Are they abandoning us?"
- To candidates: "Exciting new focus — are they decisive?"

Same fact. Four different narratives needed. The skill is maintaining truth while serving each audience's actual question.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-69
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Step 2: Audience Translation Matrix

Take the core narrative and translate it for each audience. Same truth, different frame.

| Fact | Employees need to hear | Investors need to hear | Customers need to hear | Candidates need to hear |
|------|----------------------|----------------------|----------------------|------------------------|
| We have 80 customers | "We've proven the model — your work matters" | "Product-market fit signal, capital efficient" | "80 care facilities trust us" | "Traction you'd be joining" |
| We pivoted from hardware | "We were honest enough to change course" | "Capital-efficient pivot to better unit economics" | "We found a faster, simpler way to serve you" | "We make decisions based on evidence, not ego" |
| We missed Q2 revenue | "Here's why, here's the plan, here's what you can do" | "Revenue mix shifted — trailing indicator improving" | [Usually don't tell customers revenue misses] | [Usually not shared externally] |
| We're hiring fast | "The team is growing — your network matters" | "Headcount plan aligned to growth" | [Not relevant unless it affects service] | "This is a rocket ship moment" |

**Rules:**
- Never contradict yourself across audiences. Different framing ≠ different facts.
- "We told investors growth, told employees efficiency" is a contradiction. Audit for this.
- Investors and employees see each other. Board members talk to your team. Candidates google you.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-70
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Step 4: Audience-Specific Communication Cadence

| Audience | Format | Frequency | Owner |
|----------|--------|-----------|-------|
| Employees | All-hands | Monthly | CEO |
| Employees | Team updates | Weekly | Team leads |
| Investors | Written update | Monthly | CEO + CFO |
| Board | Board meeting + memo | Quarterly | CEO |
| Customers | Product updates | Per release | CPO / CS |
| Candidates | Careers page + interview narrative | Ongoing | CHRO + Founders |
| Partners | Quarterly business review | Quarterly | BD Lead |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-71
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Step 6: Crisis Communication

When the narrative breaks — someone leaves publicly, a product fails, a security breach, a press article.

**The 4-hour rule:** If something is public or about to be, communicate internally within 4 hours. Employees should never learn about company news from Twitter.

**Crisis communication sequence:**

**Hour 0–4 (internal first):**
1. CEO or relevant leader sends an internal message
2. Acknowledge what happened factually
3. State what you know and what you don't know yet
4. Tell people what you're doing about it
5. Tell people what they should do if they're asked about it

**Hour 4–24 (external if needed):**
1. External statement (press, social) only if the event is public
2. Consistent with the internal message — same facts, audience-appropriate framing
3. Legal review if any claims or liability involved

**What not to do in a crisis:**
- Silence: letting rumors fill the vacuum
- Spin: people can detect it and it destroys trust
- "No comment": says "we have something to hide"
- Blaming: even if someone else caused the problem, your audience only cares what you're doing about it

**Template for crisis internal communication:**
> "Here's what happened: [factual description]. Here's what we know right now: [known facts]. Here's what we don't know yet: [honest uncertainty]. Here's what we're doing: [specific actions]. Here's what you should do if you're asked about this: [specific guidance]. I'll update you by [specific time] with more information."

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-72
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Key Questions for Narrative

- "Could a new employee explain to a friend why our company exists? What would they say?"
- "What do we tell investors about our strategy? What do we tell employees? Are these the same?"
- "If a journalist asked our team members to describe the company independently, what would they say?"
- "When did we last update our 'why we exist' story? Is it still true?"
- "What's the hardest question we'd get from each audience? Do we have an honest answer?"

## Red Flags

- Different departments describe the company mission differently
- Investor narrative emphasizes growth; employee narrative emphasizes stability (or vice versa)
- All-hands presentations are mostly slides, mostly one-way
- Q&A questions are screened or deflected
- Bad news reaches employees through Slack rumors before leadership communication
- Careers page describes a culture that employees don't recognize

## Integration with Other C-Suite Roles

| When... | Work with... | To... |
|---------|-------------|-------|
| Investor update prep | CFO | Align financial narrative with company narrative |
| Reorg or leadership change | CHRO + CEO | Sequence: employees first, then external |
| Product pivot | CPO | Align customer communication with investor story |
| Culture change | Culture Architect | Ensure internal story is consistent with external employer brand |
| M&A or partnership | CEO + COO | Control information flow, prevent narrative leaks |
| Crisis | All C-suite | Single voice, consistent story, internal first |

## Detailed References
- `references/narrative-frameworks.md` — Storytelling structures, founder narrative, bad news delivery, all-hands templates
- `templates/all-hands-template.md` — All-hands presentation template


---
type: skill
lifecycle: stable
inheritance: inheritable
name: intl-expansion
description: International market expansion strategy. Market selection, entry modes, localization, regulatory compliance, and go-to-market by region. Use when expanding to new countries, evaluating internationa...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# International Expansion

Frameworks for expanding into new markets: selection, entry, localization, and execution.

## Keywords
international expansion, market entry, localization, go-to-market, GTM, regional strategy, international markets, market selection, cross-border, global expansion

## Quick Start

**Decision sequence:** Market selection → Entry mode → Regulatory assessment → Localization plan → GTM strategy → Team structure → Launch.

## Market Selection Framework

### Scoring Matrix
| Factor | Weight | How to Assess |
|--------|--------|---------------|
| Market size (addressable) | 25% | TAM in target segment, willingness to pay |
| Competitive intensity | 20% | Incumbent strength, market gaps |
| Regulatory complexity | 20% | Barriers to entry, compliance cost, timeline |
| Cultural distance | 15% | Language, business practices, buying behavior |
| Existing traction | 10% | Inbound demand, existing customers, partnerships |
| Operational complexity | 10% | Time zones, infrastructure, payment systems |

### Entry Modes
| Mode | Investment | Control | Risk | Best For |
|------|-----------|---------|------|----------|
| **Export** (sell remotely) | Low | Low | Low | Testing demand |
| **Partnership** (reseller/distributor) | Medium | Medium | Medium | Markets with strong local requirements |
| **Local team** (hire in-market) | High | High | High | Strategic markets with proven demand |
| **Entity** (full subsidiary) | Very high | Full | High | Major markets, regulatory requirement |
| **Acquisition** | Highest | Full | Highest | Fast market entry with existing base |

**Default path:** Export → Partnership → Local team → Entity (graduate as revenue justifies).

## Localization Checklist

### Product
- [ ] Language (UI, documentation, support content)
- [ ] Currency and pricing (local pricing, not just conversion)
- [ ] Payment methods (varies wildly by market)
- [ ] Date/time/number formats
- [ ] Legal requirements (data residency, privacy)
- [ ] Cultural adaptation (not just translation)

### Go-to-Market
- [ ] Messaging adaptation (what resonates locally)
- [ ] Channel strategy (channels differ by market)
- [ ] Local case studies and social proof
- [ ] Local partnerships and integrations
- [ ] Event/conference presence
- [ ] Local SEO and content

### Operations
- [ ] Legal entity (if required)
- [ ] Tax compliance
- [ ] Employment law (if hiring locally)
- [ ] Customer support (hours, language)
- [ ] Banking and payments

## Key Questions

- "Is there pull from the market, or are we pushing?"
- "What's the cost of entry vs the 3-year revenue opportunity?"
- "Can we serve this market from HQ, or do we need boots on the ground?"
- "What's the regulatory timeline? Can we launch before the paperwork is done?"
- "Who's winning in this market and what would it take to displace them?"

## Common Mistakes

| Mistake | Why It Happens | Prevention |
|---------|---------------|------------|
| Entering too many markets at once | FOMO, board pressure | Max 1-2 new markets per year |
| Copy-paste GTM from home market | Assuming buyers are the same | Research local buying behavior |
| Underestimating regulatory cost | "We'll figure it out" | Regulatory assessment BEFORE committing |
| Hiring too early | Optimism | Prove demand before hiring local team |
| Wrong pricing (just converting) | Laziness | Research willingness to pay locally |

## Integration with C-Suite Roles

| Role | Contribution |
|------|-------------|
| CEO | Market selection, strategic commitment |
| CFO | Investment sizing, ROI modeling, entity structure |
| CRO | Revenue targets, sales model adaptation |
| CMO | Positioning, channel strategy, local brand |
| CPO | Localization roadmap, feature priorities |
| CTO | Infrastructure, data residency, scaling |
| CHRO | Local hiring, employment law, comp |
| COO | Operations setup, process adaptation |

## Resources
- `references/market-entry-playbook.md` — detailed entry playbook by market type
- `references/regional-guide.md` — specific considerations for key regions (EU, US, APAC, LATAM)


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ma-playbook
description: M&A strategy for acquiring companies or being acquired. Due diligence, valuation, integration, and deal structure. Use when evaluating acquisitions, preparing for acquisition, M&A due diligence, in...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# M&A Playbook

Frameworks for both sides of M&A: acquiring companies and being acquired.

## Keywords
M&A, mergers and acquisitions, due diligence, acquisition, acqui-hire, integration, deal structure, valuation, LOI, term sheet, earnout

## Quick Start

**Acquiring:** Start with strategic rationale → target screening → due diligence → valuation → negotiation → integration.

**Being Acquired:** Start with readiness assessment → data room prep → advisor selection → negotiation → transition.

## When You're Acquiring

### Strategic Rationale (answer before anything else)
- **Buy vs Build:** Can you build this faster/cheaper? If yes, don't acquire.
- **Acqui-hire vs Product vs Market:** What are you really buying? Talent? Technology? Customers?
- **Integration complexity:** How hard is it to merge this into your company?

### Due Diligence Checklist
| Domain | Key Questions | Red Flags |
|--------|--------------|-----------|
| Financial | Revenue quality, customer concentration, burn rate | >30% revenue from 1 customer |
| Technical | Code quality, tech debt, architecture fit | Monolith with no tests |
| Legal | IP ownership, pending litigation, contracts | Key IP owned by individuals |
| People | Key person risk, culture fit, retention risk | Founders have no lockup/earnout |
| Market | Market position, competitive threats | Declining market share |
| Customers | Churn rate, NPS, contract terms | High churn, short contracts |

### Valuation Approaches
- **Revenue multiple:** Industry-dependent (2-15x ARR for SaaS)
- **Comparable transactions:** What similar companies sold for
- **DCF:** For profitable companies only (most startups: use multiples)
- **Acqui-hire:** $1-3M per engineer in hot markets

### Integration Frameworks
See `references/integration-playbook.md` for the 100-day integration plan.

## When You're Being Acquired

### Readiness Signals
- Inbound interest from strategic buyers
- Market consolidation happening around you
- Fundraising becomes harder than operating
- Founder ready for a transition

### Preparation (6-12 months before)
1. Clean up financials (audited if possible)
2. Document all IP and contracts
3. Reduce customer concentration
4. Lock up key employees
5. Build the data room
6. Engage an M&A advisor

### Negotiation Points
| Term | What to Watch | Your Leverage |
|------|--------------|---------------|
| Valuation | Earnout traps (unreachable targets) | Multiple competing offers |
| Earnout | Milestone definitions, measurement period | Cash-heavy vs earnout-heavy split |
| Lockup | Duration, conditions | Your replaceability |
| Rep & warranties | Scope of liability | Escrow vs indemnification cap |
| Employee retention | Who gets offers, at what terms | Key person dependencies |

## Red Flags (Both Sides)

- No clear strategic rationale beyond "it's a good deal"
- Culture clash visible during due diligence and ignored
- Key people not locked in before close
- Integration plan doesn't exist or is "we'll figure it out"
- Valuation based on projections, not actuals

## Integration with C-Suite Roles

| Role | Contribution to M&A |
|------|-------------------|
| CEO | Strategic rationale, negotiation lead |
| CFO | Valuation, deal structure, financing |
| CTO | Technical due diligence, integration architecture |
| CHRO | People due diligence, retention planning |
| COO | Integration execution, process merge |
| CPO | Product roadmap impact, customer overlap |

## Resources
- `references/integration-playbook.md` — 100-day post-acquisition integration plan
- `references/due-diligence-checklist.md` — comprehensive DD checklist by domain


---
type: skill
lifecycle: stable
inheritance: inheritable
name: org-health-diagnostic
description: Cross-functional organizational health check combining signals from all C-suite roles. Scores 8 dimensions on a traffic-light scale with drill-down recommendations. Use when assessing overall compa...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Org Health Diagnostic

Eight dimensions. Traffic lights. Real benchmarks. Surfaces the problems you don't know you have.

## Keywords
org health, organizational health, health diagnostic, health dashboard, health check, company health, functional health, team health, startup health, health scorecard, health assessment, risk dashboard

## Quick Start

```bash
python scripts/health_scorer.py        # Guided CLI — enter metrics, get scored dashboard
python scripts/health_scorer.py --json # Output raw JSON for integration
```

Or describe your metrics:
```
/health [paste your key metrics or answer prompts]
/health:dimension [financial|revenue|product|engineering|people|ops|security|market]
```

## The 8 Dimensions

### 1. 💰 Financial Health (CFO)
**What it measures:** Can we fund operations and invest in growth?

Key metrics:
- **Runway** — months at current burn (Green: >12, Yellow: 6-12, Red: <6)
- **Burn multiple** — net burn / net new ARR (Green: <1.5x, Yellow: 1.5-2.5x, Red: >2.5x)
- **Gross margin** — SaaS target: >65% (Green: >70%, Yellow: 55-70%, Red: <55%)
- **MoM growth rate** — contextual by stage (see benchmarks)
- **Revenue concentration** — top customer % of ARR (Green: <15%, Yellow: 15-25%, Red: >25%)

### 2. 📈 Revenue Health (CRO)
**What it measures:** Are customers staying, growing, and recommending us?

Key metrics:
- **NRR (Net Revenue Retention)** — Green: >110%, Yellow: 100-110%, Red: <100%
- **Logo churn rate (annualized)** — Green: <5%, Yellow: 5-10%, Red: >10%
- **Pipeline coverage (next quarter)** — Green: >3x, Yellow: 2-3x, Red: <2x
- **CAC payback period** — Green: <12 months, Yellow: 12-18, Red: >18 months
- **Average ACV trend** — directional: growing, flat, declining

### 3. 🚀 Product Health (CPO)
**What it measures:** Do customers love and use the product?

Key metrics:
- **NPS** — Green: >40, Yellow: 20-40, Red: <20
- **DAU/MAU ratio** — engagement proxy (Green: >40%, Yellow: 20-40%, Red: <20%)
- **Core feature adoption** — % of users using primary value feature (Green: >60%)
- **Time-to-value** — days from signup to first core action (lower is better)
- **Customer satisfaction (CSAT)** — Green: >4.2/5, Yellow: 3.5-4.2, Red: <3.5

### 4. ⚙️ Engineering Health (CTO)
**What it measures:** Can we ship reliably and sustain velocity?

Key metrics:
- **Deployment frequency** — Green: daily, Yellow: weekly, Red: monthly or less
- **Change failure rate** — % of deployments causing incidents (Green: <5%, Red: >15%)
- **Mean time to recovery (MTTR)** — Green: <1 hour, Yellow: 1-4 hours, Red: >4 hours
- **Tech debt ratio** — % of sprint capacity on debt (Green: <20%, Yellow: 20-35%, Red: >35%)
- **Incident frequency** — P0/P1 per month (Green: <2, Yellow: 2-5, Red: >5)

### 5. 👥 People Health (CHRO)
**What it measures:** Is the team stable, engaged, and growing?

Key metrics:
- **Regrettable attrition (annualized)** — Green: <10%, Yellow: 10-20%, Red: >20%
- **Engagement score** — (eNPS or similar; Green: >30, Yellow: 0-30, Red: <0)
- **Time-to-fill (avg days)** — Green: <45, Yellow: 45-90, Red: >90
- **Manager-to-IC ratio** — Green: 1:5–1:8, Yellow: 1:3–1:5 or 1:8–1:12, Red: outside
- **Internal promotion rate** — at least 25-30% of senior roles filled internally

### 6. 🔄 Operational Health (COO)
**What it measures:** Are we executing our strategy with discipline?

Key metrics:
- **OKR completion rate** — % of key results hitting target (Green: >70%, Yellow: 50-70%, Red: <50%)
- **Decision cycle time** — days from decision needed to decision made (Green: <48h, Yellow: 48h-1w)
- **Meeting effectiveness** — % of meetings with clear outcome (qualitative)
- **Process maturity** — level 1-5 scale (see COO advisor)
- **Cross-functional initiative completion** — % on time, on scope

### 7. 🔒 Security Health (CISO)
**What it measures:** Are we protecting customers and maintaining compliance?

Key metrics:
- **Security incidents (last 90 days)** — Green: 0, Yellow: 1-2 minor, Red: 1+ major
- **Compliance status** — certifications current/in-progress vs. overdue
- **Vulnerability remediation SLA** — % of critical CVEs patched within SLA (Green: 100%)
- **Security training completion** — % of team current (Green: >95%)
- **Pen test recency** — Green: <12 months, Yellow: 12-24, Red: >24 months

### 8. 📣 Market Health (CMO)
**What it measures:** Are we winning in the market and growing efficiently?

Key metrics:
- **CAC trend** — improving, flat, or worsening QoQ
- **Organic vs paid lead mix** — more organic = healthier (less fragile)
- **Win rate** — % of qualified opportunities closed-won (Green: >25%, Yellow: 15-25%, Red: <15%)
- **Competitive win rate** — against primary competitors specifically
- **Brand NPS** — awareness + preference scores in ICP

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-76
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Dimension Interactions (Why One Problem Creates Another)

| If this dimension is red... | Watch these dimensions next |
|-----------------------------|----------------------------|
| Financial Health | People (freeze hiring) → Engineering (freeze infra) → Product (cut scope) |
| Revenue Health | Financial (cash gap) → People (attrition risk) → Market (lose positioning) |
| People Health | Engineering (velocity drops) → Product (quality drops) → Revenue (churn rises) |
| Engineering Health | Product (features slip) → Revenue (deals stall on product) |
| Product Health | Revenue (NRR drops, churn rises) → Market (CAC rises; referrals dry up) |
| Operational Health | All dimensions degrade over time (execution failure cascades everywhere) |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-77
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Graceful Degradation

You don't need all metrics to run a diagnostic. The tool handles partial data:
- Missing metric → excluded from score, flagged as "[data needed]"
- Score still valid for available dimensions
- Report flags which gaps to fill for next cycle

## References
- `references/health-benchmarks.md` — benchmarks by stage (Seed, A, B, C)
- `scripts/health_scorer.py` — CLI scoring tool with traffic light output


---
type: skill
lifecycle: stable
inheritance: inheritable
name: scenario-war-room
description: Cross-functional what-if modeling for cascading multi-variable scenarios. Unlike single-assumption stress testing, this models compound adversity across all business functions simultaneously. Use w...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Scenario War Room

Model cascading what-if scenarios across all business functions. Not single-assumption stress tests — compound adversity that shows how one problem creates the next.

## Keywords
scenario planning, war room, what-if analysis, risk modeling, cascading effects, compound risk, adversity planning, contingency planning, stress test, crisis planning, multi-variable scenario, pre-mortem

## Quick Start

```bash
python scripts/scenario_modeler.py   # Interactive scenario builder with cascade modeling
```

Or describe the scenario:
```
/war-room "What if we lose our top customer AND miss the Q3 fundraise?"
/war-room "What if 3 engineers quit AND we need to ship by Q3?"
/war-room "What if our market shrinks 30% AND a competitor raises $50M?"
```

## What This Is Not

- **Not** a single-assumption stress test (that's `/em:stress-test`)
- **Not** financial modeling only — every function gets modeled
- **Not** worst-case-only — models 3 severity levels
- **Not** paralysis by analysis — outputs concrete hedges and triggers

## Framework: 6-Step Cascade Model

### Step 1: Define Scenario Variables (max 3)
State each variable with:
- **What changes** — specific, quantified if possible
- **Probability** — your best estimate
- **Timeline** — when it hits

```
Variable A: Top customer (28% ARR) gives 60-day termination notice
  Probability: 15% | Timeline: Within 90 days

Variable B: Series A fundraise delayed 6 months beyond target close
  Probability: 25% | Timeline: Q3

Variable C: Lead engineer resigns
  Probability: 20% | Timeline: Unknown
```

### Step 2: Domain Impact Mapping

For each variable, each relevant role models impact:

| Domain | Owner | Models |
|--------|-------|--------|
| Cash & runway | CFO | Burn impact, runway change, bridge options |
| Revenue | CRO | ARR gap, churn cascade risk, pipeline |
| Product | CPO | Roadmap impact, PMF risk |
| Engineering | CTO | Velocity impact, key person risk |
| People | CHRO | Attrition cascade, hiring freeze implications |
| Operations | COO | Capacity, OKR impact, process risk |
| Security | CISO | Compliance timeline risk |
| Market | CMO | CAC impact, competitive exposure |

### Step 3: Cascade Effect Mapping

This is the core. Show how Variable A triggers consequences in domains that trigger Variable B's effects:

```
TRIGGER: Customer churn ($560K ARR)
  ↓
CFO: Runway drops 14 → 8 months
  ↓
CHRO: Hiring freeze; retention risk increases (morale hit)
  ↓
CTO: 3 open engineering reqs frozen; roadmap slips
  ↓
CPO: Q4 feature launch delayed → customer retention risk
  ↓
CRO: NRR drops; existing accounts see reduced velocity → more churn risk
  ↓
CFO: [Secondary cascade — potential death spiral if not interrupted]
```

Name the cascade explicitly. Show where it can be interrupted.

### Step 4: Severity Matrix

Model three scenarios:

| Scenario | Definition | Recovery |
|----------|------------|---------|
| **Base** | One variable hits; others don't | Manageable with plan |
| **Stress** | Two variables hit simultaneously | Requires significant response |
| **Severe** | All variables hit; full cascade | Existential; requires board intervention |

For each severity level:
- Runway impact
- ARR impact
- Headcount impact
- Timeline to unacceptable state (trigger point)

### Step 5: Trigger Points (Early Warning Signals)

Define the measurable signal that tells you a scenario is unfolding **before** it's confirmed:

```
Trigger for Customer Churn Risk:
  - Sponsor goes dark for >3 weeks
  - Usage drops >25% MoM
  - No Q1 QBR confirmed by Dec 1

Trigger for Fundraise Delay:
  - <3 term sheets after 60 days of process
  - Lead investor requests >30-day extension on DD
  - Competitor raises at lower valuation (market signal)

Trigger for Engineering Attrition:
  - Glassdoor activity from engineering team
  - 2+ referral interview requests from engineers
  - Above-market offer counter-required in last 3 months
```

### Step 6: Hedging Strategies

For each scenario: actions to take **now** (before the scenario materializes) that reduce impact if it does.

| Hedge | Cost | Impact | Owner | Deadline |
|-------|------|--------|-------|---------|
| Establish $500K credit line | $5K/year | Buys 3 months if churn hits | CFO | 60 days |
| 12-month retention bonus for 3 key engineers | $90K | Locks team through fundraise | CHRO | 30 days |
| Diversify to <20% revenue concentration per customer | Sales effort | Reduces single-customer risk | CRO | 2 quarters |
| Compress fundraise timeline, start parallel process | CEO time | Closes before runways merge | CEO | Immediate |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-79
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Rules for Good War Room Sessions

**Max 3 variables per scenario.** More than 3 is noise — you can't meaningfully prepare for 5-variable collapse. Model the 3 that actually worry you.

**Quantify or estimate.** "Revenue drops" is not useful. "$420K ARR at risk over 60 days" is. Use ranges if uncertain.

**Don't stop at first-order effects.** The damage is always in the cascade, not the initial hit.

**Model recovery, not just impact.** Every scenario should have a "what we do" path.

**Separate base case from sensitivity.** Don't conflate "what probably happens" with "what could happen."

**Don't over-model.** 3-4 scenarios per planning cycle is the right number. More creates analysis paralysis.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-80
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: strategic-alignment
description: Cascades strategy from boardroom to individual contributor. Detects and fixes misalignment between company goals and team execution. Covers strategy articulation, cascade mapping, orphan goal detec...
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Strategic Alignment Engine

Strategy fails at the cascade, not the boardroom. This skill detects misalignment before it becomes dysfunction and builds systems that keep strategy connected from CEO to individual contributor.

## Keywords
strategic alignment, strategy cascade, OKR alignment, orphan OKRs, conflicting goals, silos, communication gap, department alignment, alignment checker, strategy articulation, cross-functional, goal cascade, misalignment, alignment score

## Quick Start

```bash
python scripts/alignment_checker.py    # Check OKR alignment: orphans, conflicts, coverage gaps
```

## Core Framework

The alignment problem: **The further a goal gets from the strategy that created it, the less likely it reflects the original intent.** This is the organizational telephone game. It happens at every stage. The question is how bad it is and how to fix it.

### Step 1: Strategy Articulation Test

Before checking cascade, check the source. Ask five people from five different teams:
**"What is the company's most important strategic priority right now?"**

**Scoring:**
- All five give the same answer: ✅ Articulation is clear
- 3–4 give similar answers: 🟡 Loose alignment — clarify and communicate
- < 3 agree: 🔴 Strategy isn't clear enough to cascade. Fix this before fixing cascade.

**Format test:** The strategy should be statable in one sentence. If leadership needs a paragraph, teams won't internalize it.
- ❌ "We focus on product-led growth while maintaining enterprise relationships and expanding our international presence and investing in platform capabilities"
- ✅ "Win the mid-market healthcare segment in DACH before Series B"

### Step 2: Cascade Mapping

Map the flow from company strategy → each level of the organization.

```
Company level:  OKR-1, OKR-2, OKR-3
    ↓
Dept level:     Sales OKRs, Eng OKRs, Product OKRs, CS OKRs
    ↓
Team level:     Team A OKRs, Team B OKRs...
    ↓
Individual:     Personal goals / rocks
```

**For each goal at every level, ask:**
- Which company-level goal does this support?
- If this goal is 100% achieved, how much does it move the company goal?
- Is the connection direct or theoretical?

### Step 3: Alignment Detection

Three failure patterns:

**Orphan goals:** Team or individual goals that don't connect to any company goal.
- Symptom: "We've been working on this for a quarter and nobody above us seems to care"
- Root cause: Goals set bottom-up or from last quarter's priorities without reconciling to current company OKRs
- Fix: Connect or cut. Every goal needs a parent.

**Conflicting goals:** Two teams' goals, when both succeed, create a worse outcome.
- Classic example: Sales commits to volume contracts (revenue), CS is measured on satisfaction scores. Sales closes bad-fit customers; CS scores tank.
- Fix: Cross-functional OKR review before quarter begins. Shared metrics where teams interact.

**Coverage gaps:** Company has 3 OKRs. 5 teams support OKR-1, 2 support OKR-2, 0 support OKR-3.
- Symptom: Company OKR-3 consistently misses; nobody owns it
- Fix: Explicit ownership assignment. If no team owns a company OKR, it won't happen.

See `scripts/alignment_checker.py` for automated detection against your JSON-formatted OKRs.

### Step 4: Silo Identification

Silos exist when teams optimize for local metrics at the expense of company metrics.

**Silo signals:**
- A department consistently hits their goals while the company misses
- Teams don't know what other teams are working on
- "That's not our problem" is a common phrase
- Escalations only flow up; coordination never flows sideways
- Data isn't shared between teams that depend on each other

**Silo root causes:**
1. **Incentive misalignment:** Teams rewarded for local metrics don't optimize for company metrics
2. **No shared goals:** When teams share a goal, they coordinate. When they don't, they drift.
3. **No shared language:** Engineering doesn't understand sales metrics; sales doesn't understand technical debt
4. **Geography or time zones:** Silos accelerate when teams don't interact organically

**Silo measurement:**
- How often do teams request something from each other vs. proceed independently?
- How much time does it take to resolve a cross-functional issue?
- Can a team member describe the current priorities of an adjacent team?

### Step 5: Communication Gap Analysis

What the CEO says ≠ what teams hear. The gap grows with company size.

**The message decay model:**
- CEO communicates strategy at all-hands → managers filter through their lens → teams receive modified version → individuals interpret further

**Gap sources:**
- **Ambiguity:** Strategy stated at too high a level ("grow the business") lets each team fill in their own interpretation
- **Frequency:** One all-hands per quarter isn't enough repetition to change behavior
- **Medium mismatch:** Long written strategy doc for teams that respond to visual communication
- **Trust deficit:** Teams don't believe the strategy is real ("we've heard this before")

**Gap detection:**
- Run the Step 1 articulation test across all levels
- Compare what leadership thinks they communicated vs. what teams say they heard
- Survey: "What changed about how you work since the last strategy update?"

### Step 6: Realignment Protocol

How to fix misalignment without calling it a "realignment" (which creates fear).

**Step 6a: Don't start with what's wrong**
Starting with "here's our misalignment" creates defensiveness. Start with "here's where we're heading and I want to make sure we're connected."

**Step 6b: Re-cascade in a workshop, not a memo**
Alignment workshops are more effective than documents. Get company-level OKR owners and department leads in a room. Map connections. Find gaps together.

**Step 6c: Fix incentives before fixing goals**
If department heads are rewarded for local metrics that conflict with company goals, no amount of goal-setting fixes the problem. The incentive structure must change first.

**Step 6d: Install a quarterly alignment check**
After fixing, prevent recurrence. See `references/alignment-playbook.md` for quarterly cadence.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: executive-leadership-skill-82
description: Skill from executive-leadership plugin
tier: extended
applyTo: '**/*executive*,**/*board*,**/*strategy*,**/*c-suite*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Key Questions for Alignment

- "Ask your newest team member: what is the most important thing the company is trying to achieve right now?"
- "Which company OKR does your team's top priority support? Can you trace the connection?"
- "When Team A and Team B both hit their goals, does the company always win? Are there scenarios where they don't?"
- "What changed in how your team works since the last strategy update?"
- "Name a decision made last week that was influenced by the company strategy."

## Red Flags

- Teams consistently hit goals while company misses targets
- Cross-functional projects take 3x longer than expected (coordination failure)
- Strategy updated quarterly but team priorities don't change
- "That's a leadership problem, not our problem" attitude at the team level
- New initiatives announced without connecting them to existing OKRs
- Department heads optimize for headcount or budget rather than company outcomes

## Integration with Other C-Suite Roles

| When... | Work with... | To... |
|---------|-------------|-------|
| New strategy is set | CEO + COO | Cascade into quarterly rocks before announcing |
| OKR cycle starts | COO | Run cross-team conflict check before finalizing |
| Team consistently misses goals | CHRO | Diagnose: capability gap or alignment gap? |
| Silo identified | COO | Design shared metrics or cross-functional OKRs |
| Post-M&A | CEO + Culture Architect | Detect strategy conflicts between merged entities |

## Detailed References
- `scripts/alignment_checker.py` — Automated OKR alignment analysis (orphans, conflicts, coverage)
- `references/alignment-playbook.md` — Cascade techniques, quarterly alignment check, common patterns
