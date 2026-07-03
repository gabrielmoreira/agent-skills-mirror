# Product Health: Separating Signal from Dashboard Noise

A health analysis answers one question — "is this product okay, and where is it not?" — from twenty metrics that each answer something narrower. The craft is composition: which signals dominate, which corroborate, which mislead.

## The health stack (read top-down)

1. **Retention curves by cohort** — the ground truth; everything else is commentary. Flattening plateau = alive. If retention is healthy and everything else looks bad, investigate the everything-else instrumentation first.
2. **The North Star trend, decomposed** — level and slope, split into new-user contribution vs existing-user depth. Growth that's all-new-users with flat depth is acquisition wearing a product costume.
3. **Activation funnel** — of this month's signups, what % reached the value moment, and where do the rest pool? The pools are the roadmap.
4. **Engagement distribution, not average** — DAU/MAU means little; the histogram means a lot. A "healthy 25% ratio" can be a small addicted core plus a vast dead ring — different diagnosis, different treatment than uniform-moderate use.
5. **Corroborating vitals** — support contact rate per active user, NPS *verbatims* (the score is weak; the words aren't), performance/error rates. These confirm or complicate; they never lead.

## Composite scores: use with suspicion

A single "health score" (weighted blend) is fine for scanning many products/accounts, dangerous for diagnosing one: the weights encode opinions, and a green blend can hide a red retention curve. Rule: composites for triage, raw signals for diagnosis, and never let a composite into an exec deck without its worst component named beside it.

## Reading changes honestly

- Any sudden metric move: check instrumentation/release calendar BEFORE strategy ("we broke the event" outnumbers "the market shifted" 10:1)
- Seasonality: compare year-over-year cohort-matched, not month-over-month, for anything consumer-adjacent
- Mix shift: a "declining" average is often two stable segments with changing proportions — decompose before diagnosing

## The output discipline

A health analysis ends in a verdict per area (🟢/🟡/🔴 with the evidence), the ONE thing to fix first, and what to instrument that you couldn't see this time. "Everything is sort of yellow" means the analysis didn't finish.
