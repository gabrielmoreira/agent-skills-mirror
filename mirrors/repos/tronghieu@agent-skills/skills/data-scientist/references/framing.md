# Framing: Business Question → Data Problem

Framing is where data science engagements are won or lost. A perfect model of
the wrong target is worth less than a crude answer to the right question. Fill
`templates/project-brief.md` as you work through this file.

## Locate the question on the ladder

| Level | Question | What answers it |
|---|---|---|
| Descriptive | What happened? | Aggregation, EDA, segmentation |
| Diagnostic | Why did it happen? | Statistical comparison, causal analysis |
| Predictive | What is likely to happen? | Supervised model |
| Prescriptive | What should we do? | Recommendation + quantified trade-offs |

Users routinely ask at the wrong level. The classic mismatch: "build me a churn
model" when nobody will act on per-customer scores, but everyone would act on
knowing *why* churn spiked — a diagnostic question. Ask what would be done
differently with the answer; the action reveals the true level.

Prescriptive questions decompose: they need a predictive or diagnostic core
plus a decision layer. Deliver the core rigorously, then express the decision
layer as levers and trade-offs ("threshold at 0.4 catches X at the cost of Y").
The choice of lever position belongs to the decision owner.

## The five framing questions

Elicit these from the user; don't guess silently. When the user is
unavailable, state your assumptions explicitly in the brief and flag them as
assumptions.

1. **What decision hangs on this?** Who makes it, and what actions are
   actually available to them? If the answer is "none, just curious," scope
   down to Explore and say so.
2. **What is the unit of analysis?** Customer, order, session, day,
   store-week? Most silent disasters are grain mismatches — churn defined per
   customer, data logged per subscription.
3. **What exactly is the target / quantity of interest?** "Churn" is not a
   column; it's a definition with choices in it (canceled within 90 days of
   what date? voluntary only?). Write the operational definition down and get
   it confirmed. Bad target definitions are irreversible downstream.
4. **What information is legitimately available at decision time?** Anything
   not knowable at the moment the prediction/decision would be made is
   leakage-in-waiting. Establishing this line *now* makes the leakage
   checklist mechanical later.
5. **What does "good enough to act" look like?** Get it in business terms
   (catch half the fraud at under 2% false alarms) and translate to metric
   terms yourself. Also elicit the *cost asymmetry*: which error is more
   expensive, missing a positive or raising a false alarm? This single answer
   drives metric choice, threshold setting, and the final recommendation.

## Translate, then confirm

End framing by writing, in one short paragraph: "I will treat this as a
[level] problem: [target/quantity] at the [unit] grain, using data available
as of [decision time], judged by [metric] where [success bar]." Present this
mirror to the user before proceeding. Thirty seconds of confirmation here
saves the engagement.

## Anti-patterns

- **Solution-first framing.** The user names a technique ("we need deep
  learning for this"). Acknowledge, then frame the question level anyway —
  the technique falls out of the framing, not the other way around.
- **Proxy drift.** The measurable proxy quietly replaces the real goal
  (clicks stand in for satisfaction). Name the gap between proxy and goal in
  the brief; it belongs in the final report's limitations.
- **Boiling the ocean.** "Analyze everything and tell me something
  interesting" — negotiate down to the one or two decisions the user actually
  faces this quarter, or run Explore honestly labeled as hypothesis
  generation, not answers.
- **Unfalsifiable asks.** If no possible data result would change the user's
  mind, say so and reframe. Analysis theater helps nobody.
