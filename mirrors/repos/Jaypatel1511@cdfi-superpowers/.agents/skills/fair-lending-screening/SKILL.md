---
name: fair-lending-screening
description: >-
  Run adjusted denial-disparity screening on public HMDA data — logistic
  regression with FFIEC-standard controls — to flag lending disparities that
  warrant further review. Use when the user asks about "fair lending analysis,"
  "denial rate disparities," "adjusted odds ratio," "HMDA disparity analysis,"
  "mortgage lending discrimination screening," or wants to compare denial rates
  between racial groups with statistical controls. Backed by the audited PyPI
  package fair-lending-screener (import `fair_lending_screener`) — this is the
  inferential analysis the hmda-analysis skill explicitly excludes. Never assert
  discrimination from screening results.
compatibility: >-
  Requires Python >=3.9, pip, and network access to pypi.org and ffiec.cfpb.gov
  (CFPB HMDA Data Browser API, via hmda-analyzer). Heavy dependencies: pandas,
  numpy, statsmodels, scipy, hmda-analyzer. Data years 2018 to the current year
  only — earlier LAR files lack the LTV, DTI and property-value controls.
---

# Fair Lending Screening

Runs binary logistic regression on public HMDA data to produce an **adjusted
denial disparity** — an odds ratio with a 95% confidence interval and p-value —
for a protected race group against a comparison group, holding FFIEC-standard
underwriting controls constant. This is **the inferential analysis** that the
`hmda-analysis` skill (descriptive only) firewalls. The two skills sit on
opposite sides of the descriptive/inferential line and must not be conflated.

**This package is alpha-status software.** Its methodology has not been
reviewed by an external fair-lending expert (the package plans that before
v1.0.0). Results are screening signals warranting further review, not findings
of discrimination.

**What it is, in the package's own words (0.2.2):** a *lending-disparity
screening* tool, *informed by* the FFIEC Interagency Fair Lending Examination
Procedures (2009). It is **not** "the methodology examiners use" and it is
**not** "disparate-impact analysis" — 0.2.2 retracted both labels. Examiners
work from full loan files with credit scores and AUS records; an adjusted
regression that holds legitimate factors constant is the disparate-*treatment*
statistical approach. The tool asserts neither legal theory — it reports an
unexplained adjusted disparity as a screening signal. Use that vocabulary.

## When to use

- "Are Black applicants denied mortgages at higher rates in Illinois after
  controlling for income and LTV?"
- "Run a fair-lending screen on 2023 conventional home-purchase loans in Cook
  County."
- "What's the adjusted denial disparity for Asian applicants in California?"
- "Screen this lender's HMDA data for a denial disparity."
- "Generate a fair-lending disparity report for our state."

## When NOT to use

- **Descriptive HMDA analysis** (lending volumes, market shares, top lenders,
  CRA-proxy distributions) — that is `hmda-analysis`, which is descriptive only
  and carries its own firewall against the analysis this skill performs.
- **Ethnicity (Hispanic/Latino) analysis** — 0.2.2 matches `protected_class`
  and `comparison_class` against `derived_race` only. Passing
  `derived_ethnicity` values raises `InvalidProtectedClassError`. Say so; do
  not hand-roll an ethnicity model.
- **Proving discrimination** — this tool produces screening signals, not legal
  findings. It cannot establish that discrimination occurred.
- **Small-business lending (Section 1071)** — different statute, different
  data.
- **Pricing / rate-spread disparity** — evaluated and deferred by the package;
  public HMDA lacks the credit-risk controls for a defensible adjusted estimate.
- **Any analysis where the user wants a definitive finding** — decline and
  explain that definitive findings require full loan-file data, credit scores,
  and examiner access.

## Install

```
pip install "fair-lending-screener>=0.2.2"
```

The `>=0.2.2` floor is load-bearing on two counts: **0.1.1 is yanked** (a
breaking API change shipped in a patch release; 0.2.0 restructured the API into
its current form), and **0.2.2 is the release that corrected the package's own
provenance claims** — below it the generated report calls itself examiner
methodology, which is false.

Import names (dist name ≠ import name):

| dist | import |
|---|---|
| fair-lending-screener | `fair_lending_screener` (canonical) or `fairlendingscreener` (alias) |

Dependencies pulled in automatically: `hmda-analyzer>=0.3.1` (the CFPB fetch
and its identifying User-Agent), `pandas`, `numpy`, `statsmodels`, `scipy`,
`requests`.

## The screening-not-finding rule (non-negotiable)

**Every result from this tool is a screening signal warranting further review.
NEVER assert, imply, or let the user conclude that discrimination has been
proven, established, or demonstrated.** The package embeds this language in
`DisparityResult.interpretation`, in `result.limitations`, and in every
generated report:

> "This analysis identifies a statistically significant adjusted disparity in
> denial rates. It does not constitute a finding of discrimination under ECOA
> or the Fair Housing Act, and it does not establish that any protected class
> characteristic caused any lending outcome. Further review of application
> files, underwriting guidelines, and internal lender data would be required
> to assess whether discrimination occurred."

Repeat it in every conversational presentation of results. It is not a
disclaimer to trim — it is the honest scope of what public-data logistic
regression can show. A user who wants it dropped is asking for something the
methodology does not support.

## The omitted-variable-bias rule (non-negotiable)

**Public HMDA omits the most predictive underwriting variables.** Credit score,
AUS recommendation, assets/reserves, co-applicant credit profile, credit
history/tradelines, underwriter overrides, appraisal method, and employment
history are all absent — `result.limitations` lists each one with its citation.

**Consequence:** the adjusted odds ratio is an **upper-bound estimate** of the
disparity that would remain after controlling for all legitimate factors
(omitting AUS and credit score, which correlate with both race and denial,
biases the coefficient upward — Wooldridge 2019 §3.3, as the package cites).
The true disparity under a fully specified model would likely be lower; how
much lower is unknowable from public data.

Always say this beside the number. Present the odds ratio as "the disparity
unexplained by the controls available in public HMDA data," never as "the"
disparity.

## The directionality rule

When `is_statistically_significant` is **False** (p ≥ 0.05 or the 95% CI
includes 1.0 — both conditions must hold for `True`), report that **no
statistically significant disparity was found in this sample with these
controls.** Not "no discrimination," not "fair lending confirmed" —
non-significance means the test did not detect a signal, not that none exists.

When the adjusted OR **is** significant but **below 1.0** (the comparison group
faces higher denial odds), report it accurately and note that it is atypical —
possibly a data issue, an unusual market, or structural factors.

## Core API

### Data loading

```python
import fair_lending_screener as fls

# CFPB HMDA Data Browser API — one year; state, lei, county are optional filters
df_raw = fls.load_from_api(year=2023, state="IL", limit=50_000)
df_raw = fls.load_from_api(year=2023, lei="549300...", limit=50_000)
df_raw = fls.load_from_api(year=2023, county="17031", limit=50_000)

# Local CSV in CFPB modified-LAR format
df_raw = fls.load_from_file("path/to/hmda_data.csv")

# Synthetic sample — demos only; label output as illustrative
df_raw = fls.load_sample(n=5000, seed=42)     # default n=2000

# Apply FFIEC dataset filters and build the regression features
df = fls.prepare_for_analysis(df_raw)         # loan_purpose=1 (home purchase) by default

# Optional standalone diagnostic — NOT a data-loading step
fls.check_data_source(timeout=15)             # -> {"reachable", "status_code", "url"}
```

- **`limit=` truncates, not samples** — the first N rows the API returns.
  50,000 (the default) is a reasonable working size for a state.
- **`year=` defaults to 2023** in `load_from_api`. Always pass it explicitly and
  pass the same value as `data_year` below.
- **`check_data_source()` takes no DataFrame.** It probes the API endpoint and
  is deliberately *not* called by `load_from_api` (a bare HEAD probe draws HTTP
  403 from the CFPB/Akamai edge on cloud IPs and would short-circuit real
  fetches). Use it only when the user wants a reachability check.
- **`prepare_for_analysis(df, loan_purpose=1, validate_controls=True)`**
  applies the filters listed under "Regression model specification," restricts
  to originated-or-denied, builds `is_denied`, log-transforms income / loan
  amount / property value, and bins DTI. It warns (does not raise) when a
  control column is missing, and raises `ValueError` if nothing survives the
  filters. `loan_purpose=None` skips that filter — not recommended.

### Core analysis

```python
result = fls.adjusted_denial_disparity(
    df,
    protected_class="Black or African American",   # value in derived_race
    comparison_class="White",                       # reference group
    data_year=2023,                                 # keyword-only, REQUIRED
    # controls=None,         # list[str] to override; [] = unadjusted only (not recommended)
    # msa=None,              # restrict to one msa_md code
    # min_sample_size=500,   # Peduzzi et al. (1996) floor
)
```

- **`data_year` is keyword-only and required.** It must be an `int` in
  `[2018, current_year]`; a string or an out-of-range year raises
  `InvalidDataYearError`.
- **`protected_class` / `comparison_class` are `derived_race` values only:**
  `"Black or African American"`, `"White"`, `"Asian"`, `"American Indian or
  Alaska Native"`, `"Native Hawaiian or Other Pacific Islander"`, and the
  other values HMDA reports. Spelling and capitalization must match exactly;
  the `InvalidProtectedClassError` message lists the values present in the
  data.
- The defaults are `"Black or African American"` vs. `"White"`; state both
  explicitly in every call so the report is unambiguous.

### DisparityResult

| attribute | type | meaning |
|---|---|---|
| `protected_class`, `comparison_class` | str | the two groups compared |
| `adjusted_odds_ratio` | float | exp(β₁) — the primary output |
| `unadjusted_odds_ratio` | float | raw odds ratio, no controls |
| `confidence_interval_95` | tuple[float, float] | 95% CI on the adjusted OR |
| `p_value` | float | two-tailed test of H₀: β₁ = 0 |
| `is_statistically_significant` | bool | p < 0.05 **and** CI excludes 1.0 |
| `sample_size` | int | observations in the model |
| `sample_size_protected`, `sample_size_comparison` | int | per-group observations |
| `controls_used` | list[str] | every regressor, including each MSA dummy |
| `dropped_controls` | list[str] | controls removed (e.g. `dti_missing` when constant) |
| `model_diagnostics` | dict | `pseudo_r2_mcfadden`, `pseudo_r2_flag`, `log_likelihood`, `converged`, `n_iterations`, `n_msa_dummies`, `n_obs_in_model` |
| `interpretation` | str | one-paragraph plain-language summary with the required caveat |
| `limitations` | list[str] | the omitted-variable list, each with a citation |
| `methodology_citation` | str | FFIEC (2009) and The Markup (2021) |
| `provenance` | dict | package/dependency versions, data source URL, timestamp, input parameters, calibration reference |

There is no `pseudo_r_squared`, `is_significant`, `n_total`, or
`denial_rate_*` attribute. Pseudo-R² is `model_diagnostics["pseudo_r2_mcfadden"]`;
raw per-group denial rates are not exposed on the result.

### Report generation

```python
report_md = fls.generate_disparity_report(
    result,
    lender_name=None,          # optional; see the guardrail below
    geography="Illinois",      # optional label for the title
    year=2023,                 # optional label for the title
    include_methodology=True,
)
```

Returns a Markdown report: alpha-release notice, quality flags, headline
finding with the required caveat, key-numbers table, "What 'Adjusted' Means,"
controls used, limitations, methodology and reproduction notes. **Always use it
for user-facing output** — it carries the caveats the raw numbers do not.

**Lender-name guardrail:** `lender_name` is suppressed from the headline and
interpretation when p > 0.05, the model did not converge, or pseudo-R² < 0.05.
The numbers still print; the report flags why the name is withheld. Do not
re-attach the name by hand.

### Methodology documentation

```python
fls.get_methodology_path()    # pathlib.Path to the bundled methodology doc
fls.get_limitations_path()    # pathlib.Path to the bundled limitations doc
```

Both return `Path` objects to Markdown files inside the installed package
(`_methodology_doc.md`, `_limitations_doc.md`). Cite them when users ask about
the method; `MethodologyDocNotFoundError` if the install is broken.

## Worked example — synthetic sample (run against 0.2.2)

```python
import fair_lending_screener as fls

df_raw = fls.load_sample(n=5000, seed=42)     # synthetic — illustrative only
df = fls.prepare_for_analysis(df_raw)

result = fls.adjusted_denial_disparity(
    df,
    protected_class="Black or African American",
    comparison_class="White",
    data_year=2023,
)

lo, hi = result.confidence_interval_95
print(f"Adjusted odds ratio: {result.adjusted_odds_ratio:.2f}×")
print(f"95% CI: ({lo:.2f}, {hi:.2f})")
print(f"p-value: {result.p_value:.4g}")
print(f"Significant: {result.is_statistically_significant}")
print(f"Pseudo-R²: {result.model_diagnostics['pseudo_r2_mcfadden']:.4f}")
print(f"N protected / comparison: {result.sample_size_protected:,} / "
      f"{result.sample_size_comparison:,}")

report = fls.generate_disparity_report(result, geography="synthetic sample", year=2023)
```

Output on 0.2.2 (synthetic data — these numbers describe the generator, not
any lender):

```
Adjusted odds ratio: 1.81×
95% CI: (1.43, 2.28)
p-value: 8.873e-07
Significant: True
Pseudo-R²: 0.0177
N protected / comparison: 664 / 3,274
```

`sample_size` was 3,938 (of 5,000 raw rows) after filters; `dropped_controls`
was `['dti_missing']`; `model_diagnostics["pseudo_r2_flag"]` was
`'BELOW_0.05_THRESHOLD'`, and the report opened with a **⚠ Analysis Quality
Flags** section saying so. On synthetic data that is expected — MSA assignments
are random, so the MSA dummies carry no real signal — and the report says the
numbers "should not be used to draw conclusions about any specific lender."

For real data, replace `load_sample` with `load_from_api(year=2023,
state="IL", limit=50_000)` and keep `data_year=2023`.

**Calibration reference (from `result.provenance`):** The Markup (2021) found a
1.8× adjusted OR for Black vs. White applicants nationally with a fuller
control set (AUS, credit model, lender, tract demographics). The package's
expected range for this model on real national data is **1.6×–2.2×** — above
The Markup's figure because AUS and credit score are omitted (see the
omitted-variable-bias rule). A real-data result far outside that band is a
reason to inspect the data before reporting.

## Relationship to hmda-analysis

`hmda-analysis` wraps `hmda-analyzer` for **descriptive** analysis: volumes,
top lenders, CRA-proxy distributions, lending-desert scores. It carries a
**non-negotiable firewall** against any inferential or disparity analysis, and
does not wrap `hmda-analyzer`'s own disparity functions.

This skill is the other side of that firewall. The two are complementary:

- `hmda-analysis` describes lending patterns (what happened).
- `fair-lending-screening` screens for an adjusted denial disparity (whether,
  after controls, denial odds differed by race).

**Never cross the line in either direction.** `hmda-analysis` must not produce
disparity ratios or protected-class stratified denial analysis; if a user asks
it to, it routes here. This skill must not be described as "descriptive" — it
is inferential by design — and it must not be used to dress a descriptive
table up as a finding.

## Regression model specification (for transparency)

Binary logistic regression via `statsmodels.api.Logit`:

```
logit(P(denied)) = β₀ + β₁·protected_class + β₂·log(income) + β₃·log(loan_amount)
    + β₄·LTV + β₅₋₇·DTI_bins + β₈·log(property_value) + Σγⱼ·MSA_dummyⱼ
```

- **exp(β₁)** is the adjusted odds ratio.
- **MSA fixed effects:** one dummy per `msa_md` with ≥ 30 observations; sparser
  MSAs are pooled into the `MSA_other` reference category. On real state data
  expect dozens of dummies; nationally, hundreds. Every dummy appears in
  `controls_used`, which is why the report says "26 legitimate underwriting
  factors" on the sample above (7 borrower/loan controls + 19 MSA dummies).
- **DTI** is categorical — bins ≤35% (reference), 36–42%, 43–49%, ≥50%, plus a
  missing indicator that is dropped when constant.
- **Continuous controls** (income, loan amount, property value) are
  log-transformed.

Dataset filters `prepare_for_analysis` applies: originated or denied
(`action_taken ∈ {1, 3}`), conventional (`loan_type=1`), home purchase
(`loan_purpose=1`, configurable), first lien (`lien_status=1`), principal
residence (`occupancy_type=1`), 1–4 unit (`property_type=1`), site-built
(`construction_method=1`), LTV present and ≤ 100%, and not business/commercial
purpose (`business_or_commercial_purpose == 2`; when that column is absent the
package warns that the filter could not be applied).

## Output-presentation rules

- **Always use `generate_disparity_report()`** for user-facing output.
- **Never present the odds ratio without its CI and p-value.**
- **Name the controls.** "After controlling for income, loan amount, LTV, DTI,
  property value, and MSA" — not just "after adjusting."
- **Name what is NOT controlled for.** Credit score and AUS recommendation
  first; the full list is `result.limitations`.
- **Never compare directly to The Markup's 1.8×** without noting the
  control-set differences (this package omits AUS, credit model, lender
  type/size, and tract demographics that The Markup included).
- **Pseudo-R² below 0.05** — relay the report's quality flag. On synthetic data
  it is expected; on real data (where 0.15–0.25 is typical) investigate the
  data before reporting.
- **Report both group sizes.** Small protected-class samples give unstable
  estimates.
- **Label synthetic-sample output as illustrative** every time.

## Typed errors (surface, don't smooth)

| Error | Trigger |
|---|---|
| `InvalidDataYearError` | `data_year` not an `int`, or outside `[2018, current_year]` |
| `InvalidProtectedClassError` | class value not present in `derived_race` (including any `derived_ethnicity` value) |
| `InsufficientDataError` | combined observations < `min_sample_size` (default 500) |
| `InsufficientGroupSizeError` | either group < 10 observations |
| `MissingControlsError` | `action_taken`/`derived_race` absent, or an explicitly requested control column absent |
| `ModelConvergenceError` | Logit did not converge (separation or iteration cap) |
| `DataSourceError` | CFPB API failure (raised by `check_data_source`; `load_from_api` re-raises hmda-analyzer's errors with context) |
| `MethodologyDocNotFoundError` | bundled methodology/limitations file missing |
| `FairLendingScreenerError` | base class |

**Report the error type and message verbatim.** Do not catch and proceed with
partial results — each error means the analysis cannot be trusted.
`ModelConvergenceError` usually means perfect or near-perfect separation:
look for an MSA×group cell with only denials or only originations, and suggest
broader geography or restricting with `msa=`.

## Failure modes

- **CFPB API unreachable / 403** — report the error. `ffiec.cfpb.gov` is the
  only supported live source; a local modified-LAR CSV via `load_from_file` is
  the offline path.
- **Too few observations** — broaden geography, raise `limit`, or drop a
  filter deliberately (and disclose it). Do not lower `min_sample_size` to
  make a result appear.
- **Protected class not found** — match HMDA's `derived_race` spelling; the
  error lists what is present.
- **Convergence failure** — see above.
- **Low pseudo-R²** — a diagnostic, not an error; relay the flag.

## Caveats

- **Alpha-status software.** Methodology not yet externally reviewed.
- **Screening signal, not finding.** Not evidence of discrimination under ECOA
  or the FHA; not a basis for enforcement or accusation.
- **Upper-bound estimate.** Omitted credit score and AUS bias the adjusted OR
  upward relative to a fully specified model.
- **Public HMDA only.** No credit scores, AUS results, assets, employment,
  tradelines, or override data.
- **Race only.** No ethnicity, sex, or age comparisons in 0.2.2.
- **Mortgage lending only.** No auto, small-business (1071), or student
  lending; no pricing/rate-spread analysis.
- **Informed by FFIEC, not FFIEC methodology.** Not a supervisory
  examination and not a replication of The Markup (different geographic and
  overall control sets).
- **Target audience:** community advocates, journalists, fair-housing
  organizations, and internal compliance teams running preliminary screens.

---

**Last verified:** 2026-09-21 against `fair-lending-screener 0.2.2` from PyPI
(worked example executed; output and error messages quoted above are what the
package produced).
