---
name: feature-prioritization-frameworks
description: "Scores and ranks a product backlog with RICE, Kano, Value vs Effort, and WSJF so assumptions beat HiPPO. Use when ordering a candidate feature list, resolving stakeholder conflict, or choosing a scoring method. Not for problem discovery, OKR/vision definition, sprint poker, A/B test design, or single-bet financial ROI models."
version: 1.0.1
---

## Overview

This skill governs how the agent converts a messy, contested backlog into a defensible, ordered development queue using structured scoring frameworks — **RICE**, the **Kano Model**, **Value vs. Effort**, and **WSJF** — without letting false precision, effort-blindness, or the loudest stakeholder dictate the roadmap. Treat a prioritization framework as a *forcing function for honest conversation*, not as an oracle.

> **Prime Directive:** *Score to expose assumptions, not to manufacture certainty. A framework converts a fight about opinions into a comparison of estimates — but a confident number built on a guessed reach and an underestimated effort is a lie with a decimal point. Make every input traceable to evidence, divide by effort so big-but-expensive loses to small-but-cheap, and never let a score override a strategic veto you can write down a reason for.*

### Core Principles
1. **Defeat the HiPPO:** The framework's primary job is to defeat the Highest Paid Person's Opinion, not to compute a number. Make everyone expose assumptions on the same axes.
2. **Source Inputs from Data:** Populate estimate fields from instrumented reality (analytics, past experiments) rather than guessing.
3. **Continuous Prioritization:** Re-score the backlog as the world changes. A score computed in January on January's data is a January decision.
4. **Align to Stated Objectives:** Every score must align to a stated objective (OKR, North Star), or "value" means nothing.
5. **Divide by Effort:** Always divide benefit by cost/effort so cheap wins beat expensive grandeur.
6. **Match Tool to Decision:** RICE for mixed backlogs, Kano for value-type, Value vs. Effort for fast triage, WSJF for time-criticality.
7. **Resist Decimal-Point Delusion:** Treat scores as producing tiers and rough rank order, not precise cardinal rankings.
8. **Confidence Punishes Hype:** Use the Confidence multiplier to discount speculative features.
9. **Output is Recommendation + Rationale:** The deliverable is a sorted list plus inputs, ties, and strategic overrides.

## When to Use

**Prioritization triggers (ordering work):**
- "Prioritize this backlog / these features / our roadmap."
- "Which of these should we build first?" / "rank these features."
- "Score this feature list with RICE / Kano / value-vs-effort / WSJF."
- "Help me decide what goes in the next sprint / quarter / release."
- "Build me a prioritization scorecard / scoring rubric / RICE sheet."
- "We have 40 things in the backlog and capacity for 6 — what makes the cut?"

**Conflict-resolution triggers (adjudicating):**
- "Engineering and sales disagree on what to build — how do we decide objectively?"
- "The CEO wants X but the data says Y — how do we reconcile this?"
- "Stop us from just building whatever the loudest person wants" / "kill the HiPPO problem."
- "Justify why feature A beats feature B to a stakeholder."

**Scoping & framework-selection triggers (choosing a method):**
- "Which prioritization framework should we use?"
- "Set up a Kano survey for these features."
- "Is RICE or WSJF better for our team?"
- "Classify these features as must-haves vs. delighters."
- "How do I estimate reach / impact / confidence for RICE?"

**Anti-triggers — do NOT use this skill when:**
- The request is about **discovering or validating *whether* a problem is worth solving** (customer interviews, problem validation). Prioritization assumes you already have a *candidate list* of solutions to rank.
- The request is about **defining the strategy, vision, or objectives** the priorities should serve (OKRs, North Star metric). Prioritization is downstream of strategy.
- The request is about **detailed engineering estimation / sprint mechanics** (story-point poker, capacity planning). This skill consumes an effort estimate to rank features.
- The request is about **running the A/B test that decides whether a shipped feature worked**. Route experiment design to the **ab-testing-design-and-analysis** skill.
- The request is about **diagnosing where users drop off** to *generate* improvement ideas. Route to the **conversion-funnel-optimization** skill.
- The request is **pure financial ROI / business-case modeling** for a single large bet.

## Prerequisites

Before any scoring, resolve these ground truth items. If unknown, ask the user *once*, in a batch:
1. **The objective(s):** What current goal does this prioritization serve? "Value" and "Impact" are scored *against this*.
2. **The candidate list:** The features/items to rank, each as a discrete, comparably-sized unit of work.
3. **The capacity constraint:** How much can actually ship this cycle (team-weeks, sprint count, headcount)?
4. **Available evidence:** What analytics, past experiment results, customer-research themes, and engineering estimates exist to source inputs from?
5. **The time pressure, if any:** Are there hard deadlines, market windows, or regulatory dates that make *cost of delay* a first-class factor (→ favors WSJF)?
6. **The stakeholders and known conflicts:** Who is requesting what, and where are the disagreements? Naming the HiPPO risk up front lets the framework do its job.

## Procedure

### Phase 1 — Prepare the candidate list and select the framework
1. **Normalize the items to comparable units.** Break epics into shippable sub-features; merge trivially-coupled tiny items.
2. **Select the framework(s):**
   - **RICE**: A mixed backlog ranked on one objective, with varying evidence quality.
   - **Kano**: Needing to know the *type* of value (basic / performance / delight).
   - **Value vs. Effort**: Fast group triage, small list, low stakes.
   - **WSJF**: Time-criticality and cost of delay (deadlines, market windows, unblocking).
   - *Default to RICE for a general mixed backlog; layer Kano when you suspect the queue is imbalanced; use Value vs. Effort for a 20-minute triage; switch to WSJF when waiting has a measurable cost.*
3. **Define the scoring scales explicitly *before* scoring.** Lock the Impact scale, the Effort unit, the Confidence rubric, and the time window for Reach now.

### Phase 2 — RICE scoring (the workhorse)
**Formula:** `RICE = (Reach × Impact × Confidence) / Effort`

- **Reach**: How many units (users, events, transactions) does this affect per a fixed time period? Source from product analytics, not a guess.
- **Impact**: How much does it move the objective per affected unit? Use a fixed ordinal scale:
  - Massive (3), High (2), Medium (1), Low (0.5), Minimal (0.25)
- **Confidence**: How much evidence backs the Reach and Impact estimates?
  - High (100% - run experiment/hard analytics), Medium (80% - some data/qualitative theme), Low (50% - informed guess), Moonshot (≤20% - speculation)
- **Effort**: Total person-time to design, build, test, and ship, in a fixed unit (person-months or person-weeks), from engineering's bottoms-up estimate. Always round *up* under uncertainty.

*Read the result as tiers, not exact ranks. Features within ~10–20% of each other are a tie to be broken by judgment, dependency, or strategic fit.*

### Phase 3 — Kano Model (classify the *type* of value)
RICE ranks magnitude; Kano reveals *kind*. Kano classifies each feature by how its **presence** and **absence** affect satisfaction.
1. **Build the survey.** For each feature, ask users two paired questions:
   - Functional (present): *"How would you feel if [feature] were available?"*
   - Dysfunctional (absent): *"How would you feel if [feature] were NOT available?"*
   - Scale: 1. I like it, 2. I expect it (must-be), 3. I am neutral, 4. I can tolerate it, 5. I dislike it.
2. **Classify each respondent's answer pair** using the Kano evaluation table (Functional answer × Dysfunctional answer) to determine if it's a Must-be, Performance, Attractive, Indifferent, or Reverse feature.
3. **Report the full category distribution** so polarizing features are flagged, not flattened to a single label.

### Phase 4 — Value vs. Effort (2×2)
Best for a fast, visual, low-stakes triage with a small group.
1. Plot features on a 2×2 matrix (Value: High/Low, Effort: High/Low).
2. Prioritize the "Quick Wins" (High Value, Low Effort) quadrant.
3. Schedule "Big Bets" (High Value, High Effort) carefully.
4. Fill in with "Maybes" (Low Value, Low Effort) if capacity allows.
5. Avoid "Time Sinks" (Low Value, High Effort).

### Phase 5 — WSJF (Weighted Shortest Job First)
Best when time-criticality and the cost of waiting dominate.
**Formula:** `WSJF = Cost of Delay / Job Size`
- **Cost of Delay** = Business Value + Time Criticality + Risk Reduction/Opportunity Enablement
- **Job Size** = Engineering estimate (similar to Effort in RICE).
- Use WSJF when dependencies dominate (a lower-scored unblocker that gates three higher-scored features rises by its enablement value).

### Phase 6 — Synthesis and output
1. Combine the scores into a final ordered queue.
2. Apply the capacity cut line.
3. Break ties with recorded rationale (strategic fit, dependency order, learning value).
4. Sequence dependencies correctly even against raw-score order.
5. Record any strategic override of the score with a written justification next to what it overrode.
6. Set a re-score trigger / cadence (what event or date expires this ranking).

## Pitfalls

- **Effort underestimation (Planning Fallacy):** Source Effort from the engineers who will build it, not the requester. Round up under uncertainty. Keep a running estimate-vs-actual log and derive a team-specific correction multiplier.
- **Stakeholder bias and HiPPO dominance:** Require an evidence source for every Reach and Impact input. A number with no source is downgraded to Low Confidence automatically. Have a neutral facilitator own the scale.
- **Kano classification drift:** Kano categories are perishable (delighters → must-bes as the market normalizes them). Date every classification and re-survey periodically. Require a minimum sample.
- **Score gaming and metric fixation (Goodhart's law):** Audit the definition behind each input. Cross-check Reach against actual analytics segments. Periodically re-rank a sample by pure judgment and see if it diverges wildly from the framework.
- **Comparing incommensurable items:** Normalize to comparable units first. Rank like with like (run separate rankings for "small improvements" vs "big bets" against separate capacity pools).
- **Ties, near-ties, and dependency ordering:** Build a dependency graph before finalizing order. A lower-scored unblocker that gates higher-scored features rises by its enablement value.
- **Low-data / new-product cold start:** Lean on Kano and Value vs. Effort early. Mark all RICE inputs as Low Confidence and treat the ranking as provisional.
- **Multiple competing objectives:** Score features against each objective separately, then make the portfolio allocation between objectives an explicit leadership decision.

## Verification

The skill's output is successful only when **every applicable** box is satisfied.

**Setup & framing**
- [ ] A current, explicit **objective** (OKR / North Star / target) is named, and "Value"/"Impact" are scored *against it*.
- [ ] The **candidate list** is normalized to roughly comparable units.
- [ ] The **capacity constraint** (the cut line) is known.
- [ ] The **framework(s)** were chosen to fit the decision, with the choice justified.
- [ ] Scoring **scales are defined and locked before scoring**.

**Scoring rigor**
- [ ] Every **Reach** is sourced from analytics over a consistent time window.
- [ ] **Impact** uses the fixed ordinal scale; **Effort** comes from engineering bottoms-up and is rounded up under uncertainty.
- [ ] **Confidence** genuinely discriminates by evidence quality — speculative features are pushed down.
- [ ] RICE/WSJF **calculations are shown** and each input traces to a named source.
- [ ] Scores are read as **tiers/bands**, with near-ties explicitly treated as ties.

**Kano & value-type (where applicable)**
- [ ] The Kano survey uses paired functional/dysfunctional questions, classified via the evaluation table, with the **distribution reported**.
- [ ] **Must-be** features gate the queue before delighters consume capacity.
- [ ] **Indifferent/Reverse** features are flagged for cutting; classifications are **dated**.

**Synthesis & integrity**
- [ ] The final queue shows **every input**, the **evidence source**, the **Kano class**, and the **cut line**.
- [ ] **Ties are broken with recorded rationale**, and **dependencies** are sequenced correctly.
- [ ] Any **strategic override** is recorded **with a written justification**.
- [ ] Divergence between frameworks is **surfaced and reconciled** explicitly.
- [ ] A **re-score trigger / cadence** is set.

When all gates pass, report: the objective the queue serves, the framework(s) used and why, the ranked backlog with visible inputs and evidence sources, the Kano balance, the tie-breaks and any strategic overrides, the cut line against capacity, and the re-score trigger. Never present a confident cardinal ranking built on guessed inputs as an objective decision.
