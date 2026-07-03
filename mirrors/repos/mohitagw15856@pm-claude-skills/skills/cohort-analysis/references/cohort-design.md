# Cohort Design: the Decisions Before the Query

Cohort analysis fails at design time, not query time. Four decisions determine whether the table means anything; make them explicitly.

## 1. Cohorting dimension — what groups the users

- **Time-of-signup** (default) answers "is the product getting better?"
- **Acquisition channel** answers "which pipes bring keepers?"
- **First-action/feature** answers "which early behaviour predicts staying?" — the most actionable and least used
- **Plan/segment** answers "who is this product actually for?"
Pick the dimension that matches the decision on the table; running signup-cohorts to answer a channel question wastes the exercise.

## 2. The metric per cell — one honest number

Retained% is standard; revenue-retained% tells a different (often opposite) story — a cohort can shrink in logos while expanding in dollars. If the decision is financial, cohort dollars, not bodies.

## 3. Cohort width vs maturity

Weekly cohorts need weeks to mature; judging last week's cohort at week 1 against an old cohort's week 12 is the classic self-deception. Grey out immature cells. Rule: a cohort is comparable only at equal age ("diagonal reading").

## 4. Minimum size

Cells under ~50 users are noise theatre — percentages swing 10 points on two users' behaviour. Widen the cohort period or aggregate segments until cells are stable; report n per row.

## Reading the table (the three passes)

1. **Down a column** (same age, different cohorts): is the product improving? The most important read.
2. **Across a row** (one cohort aging): where's the cliff? That's the intervention moment.
3. **The diagonal** (calendar time): did something happen to EVERYONE in March (pricing change, outage, seasonality)? Diagonal effects masquerade as cohort effects; check before crediting the roadmap.

## The trap gallery

Mixed populations in one cohort (a marketing burst brings tourists; segment before concluding) · definition drift (activity definition changed mid-history — annotate the table) · celebrating month-1 improvements that vanish by month-3 (early retention is easiest to inflate and least valuable).
