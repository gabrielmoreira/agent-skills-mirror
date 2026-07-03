# Reading Retention Curves Without Fooling Yourself

A retention curve is the most information-dense chart in product analytics — and the easiest to misread. These are the reading rules.

## The three curve shapes and what they mean

1. **Flattening (the good one)** — drops, then stabilises at a plateau. The plateau height IS your product-market fit for that segment; the flatten point is when habit formed. Strategy: raise the plateau (activation work) and move the flatten point earlier.
2. **Declining forever** — never flattens; every cohort eventually leaves. No amount of acquisition fixes this; the product isn't retaining anyone long-term. Strategy: stop pouring, find who (if anyone) does flatten, rebuild around them.
3. **Smile** — decline then recovery: resurrection is real (seasonal jobs, billing-cycle usage). Verify it's genuine reactivation, not a tracking artifact (auth changes and bot traffic both draw smiles).

## The mistakes that generate wrong roadmaps

- **Averaging across cohorts** — a blended curve mixes your 2023 users with last week's; improvement in new cohorts is invisible. ALWAYS plot cohorts separately; the question is whether *newer curves sit higher*.
- **Wrong activity definition** — "opened the app" retention flatters; define retention on the value action (created/report-viewed/message-sent). If the curve changes shape when you switch definitions, the vanity definition was hiding the truth.
- **Wrong period granularity** — a monthly-use product (expense tools) measured weekly shows fake churn. Match the period to the natural job frequency; if you don't know it, that's the first finding.
- **Survivorship in feature analysis** — "users of feature X retain 2× better" is selection, not causation, until you compare *similar users* who did/didn't adopt (or run the experiment).

## Benchmarks worth holding

The number to obsess over is the plateau, by segment. A product where enterprise flattens at 85% and self-serve at 15% isn't "average 40% retained" — it's two businesses, one working.

## The one-sentence output

Every retention analysis should end in a sentence of this form: "Cohorts flatten at [x]% around week [n]; the biggest lever is [moving the plateau/flatten point] for [segment], via [the behaviour that separates flatteners from leavers]."
