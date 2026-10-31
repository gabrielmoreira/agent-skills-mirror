# Exploratory Data Analysis

EDA is directed exploration: you enter with the framing question, you leave
with verified data understanding and a ranked list of hypotheses. It is not a
ritual dump of `df.describe()` — every look at the data should either answer
"can I trust this?" or "what might explain the outcome?".

Start from the `profile_data.py` output; it covers the mechanical layer. This
file covers the judgment layer on top.

## Order of operations

Work top-down; each layer's problems invalidate the layers below it.

### 1. Integrity — can I trust this data at all?

- Reconcile row counts against reality: does the number of customers/orders
  match what the user believes exists? A 3x mismatch means duplicated grain or
  filtered extract — settle it before anything else.
- Check the primary key is actually unique. If not, understand why before
  deduplicating; duplicates are sometimes real (retries, amendments).
- Date ranges: does history start/end where expected? Silent truncation and
  timezone shifts live here. Check whether "2024-01-01 00:00" spikes are real
  events or default-value artifacts.
- Cross-field consistency: totals that should sum, dates that should order
  (signup ≤ first_purchase ≤ churn_date), categories that should nest.

### 2. Univariate — what does each variable look like?

For variables that matter to the question (not all 400 columns):

- **Distributions, not just means.** Skew, multimodality, zero-inflation, and
  impossible values (negative ages, 999 placeholders) all hide behind a mean.
  Multimodality usually means mixed populations — a segmentation clue.
- **Missingness is information.** For each key variable ask: missing because
  it doesn't exist (no phone), wasn't recorded (old system), or wasn't
  recorded *because of the outcome* (churned users stop generating data — the
  dangerous kind)? The mechanism decides the treatment: dropping rows is only
  safe when missingness is unrelated to the outcome; otherwise impute and/or
  add a missing-indicator, and say which you chose and why.
- **Outliers get investigated, not deleted.** An outlier is an error, a
  different population, or your most interesting finding. Look at the actual
  rows before deciding. If you exclude, report results with and without.

### 3. Bivariate — what relates to the outcome?

- Look at the target against each candidate driver: group means/rates for
  categoricals, binned rates or scatter for numerics. Prefer *rates within
  groups* over raw counts.
- Anything correlated with the target at a suspicious level (the profile
  script flags these) is a leakage suspect first, a great feature second.
- Check driver–driver correlations: highly collinear drivers will confuse both
  regression coefficients and importance rankings later.
- **Always try one split-by.** A relationship that holds overall can reverse
  within segments (Simpson's paradox). Split the headline relationship by the
  most obvious grouping variable (region, plan, cohort) before believing it.

### 4. Time structure — if any date column exists

- Plot the outcome over time. Trend, seasonality, level shifts, and the
  COVID-shaped hole all change what modeling is valid.
- Look for *regime changes in the data itself*: a field that starts being
  populated in 2023, a category renamed mid-history. These masquerade as real
  effects.
- If the question is predictive, time structure decides the validation split
  (see `references/modeling.md`) — note it now.

## Output: the EDA report

Fill `templates/eda-report.md`. The report's centerpiece is not the plots —
it's the closing sections:

- **What I now believe about this data** (grain, coverage, quality verdict,
  quirks the next person must know).
- **Ranked hypotheses**: each one falsifiable, stated with the evidence that
  suggested it and what analysis would confirm it. This is the Explore flow's
  entire deliverable value.
- **Leakage watchlist** (if modeling is next): every column you already
  suspect encodes the outcome.

## Habits

- Compute, don't estimate: every claim in the report traces to executed code
  (non-negotiable #2).
- Note dead ends briefly ("no weekday effect: rates flat Mon–Sun") — they
  spare the next iteration from re-exploring.
- Charts are for the report, not for you: explore with tables and summaries;
  make a figure only when it will carry a claim to a reader. If a `dataviz`
  skill is available, read it before plotting.
