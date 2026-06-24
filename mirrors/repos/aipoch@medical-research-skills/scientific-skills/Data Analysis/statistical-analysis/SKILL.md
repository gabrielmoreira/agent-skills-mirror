---
name: statistical-analysis
description: Guided statistical analysis for test selection, assumption checks, power analysis, and APA-style reporting. Use when you need to choose an appropriate statistical test for your data and produce publication-ready results (including effect sizes and diagnostics).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## When to Use

Use this skill when you need to:

1. Choose an appropriate statistical test (e.g., t-test vs. ANOVA vs. non-parametric vs. Bayesian) based on study design and variable types.
2. Validate assumptions before inference (normality, homoscedasticity, linearity, outliers) and decide on remedies when assumptions fail.
3. Run common inferential analyses (hypothesis tests, correlation, regression) and interpret results with effect sizes and uncertainty.
4. Plan studies with a priori power analysis (sample size planning) or run sensitivity analysis after data collection.
5. Write results in APA style with complete reporting elements (test statistic, df, p, effect size, CI, assumption checks).

> For programming model-specific workflows (especially regression variants and custom diagnostics), prefer **statsmodels** directly; this skill focuses on *guided selection, checks, interpretation, and reporting*.

## Key Features

- **Test selection guidance** by research question, design (independent/paired; 2+ groups), outcome type, and distributional properties (see `references/test_selection_guide.md`).
- **Assumption checking and diagnostics** with automated checks and plots (Q–Q, residual plots, boxplots) via `scripts/assumption_checks.py` (see `references/assumptions_and_diagnostics.md`).
- **Frequentist analyses**: t-tests, ANOVA (+ post-hoc), chi-square/Fisher, correlation (Pearson/Spearman), linear/logistic regression with diagnostics.
- **Bayesian alternatives** with posterior summaries and Bayes Factors (see `references/bayesian_statistics.md`).
- **Effect sizes + confidence intervals** for interpretation beyond p-values (see `references/effect_sizes_and_power.md`).
- **APA-style reporting templates** and required reporting elements (see `references/reporting_standards.md`).

## Dependencies

Python (recommended **3.10+**) with:

- `numpy>=1.24`
- `pandas>=2.0`
- `scipy>=1.10`
- `statsmodels>=0.14`
- `pingouin>=0.5`
- `matplotlib>=3.7`
- `pymc>=5.0` (Bayesian workflows)
- `arviz>=0.16` (Bayesian diagnostics/plots)

## Example Usage

The example below is designed to be runnable end-to-end: it generates synthetic data, checks assumptions, runs an independent-samples t-test with effect size, performs power analysis, and prints an APA-style result string.

```python
import numpy as np
import pandas as pd
import pingouin as pg

from statsmodels.stats.power import tt_ind_solve_power

# If your repo provides this module, use it; otherwise comment it out.
from scripts.assumption_checks import comprehensive_assumption_check

# ----------------------------
# 1) Create example dataset
# ----------------------------
rng = np.random.default_rng(7)
n_a, n_b = 50, 52

group_a = rng.normal(loc=75, scale=9, size=n_a)
group_b = rng.normal(loc=69, scale=9, size=n_b)

df = pd.DataFrame({
    "score": np.r_[group_a, group_b],
    "group": ["A"] * n_a + ["B"] * n_b
})

# ----------------------------
# 2) Assumption checks
# ----------------------------
assump = comprehensive_assumption_check(
    data=df,
    value_col="score",
    group_col="group",
    alpha=0.05
)
print("Assumption check summary:")
print(assump["summary"] if "summary" in assump else assump)

# ----------------------------
# 3) Run test + effect size
# ----------------------------
res = pg.ttest(group_a, group_b, correction="auto")  # Welch if needed
t_stat = float(res["T"].iloc[0])
dfree = float(res["dof"].iloc[0])
pval = float(res["p-val"].iloc[0])
d = float(res["cohen-d"].iloc[0])
ci_low, ci_high = res["CI95%"].iloc[0]

# ----------------------------
# 4) Power analysis (planning)
# ----------------------------
n_required = tt_ind_solve_power(
    effect_size=0.5, alpha=0.05, power=0.80, ratio=1.0, alternative="two-sided"
)

# ----------------------------
# 5) APA-style reporting string
# ----------------------------
m_a, sd_a = group_a.mean(), group_a.std(ddof=1)
m_b, sd_b = group_b.mean(), group_b.std(ddof=1)

apa = (
    f"Group A (n = {n_a}, M = {m_a:.2f}, SD = {sd_a:.2f}) and "
    f"Group B (n = {n_b}, M = {m_b:.2f}, SD = {sd_b:.2f}) differed, "
    f"t({dfree:.0f}) = {t_stat:.2f}, p = {pval:.3f}, d = {d:.2f}, "
    f"95% CI [{ci_low:.2f}, {ci_high:.2f}]."
)

print("\nAPA-style result:")
print(apa)

print(f"\nPlanning note: to detect d = 0.50 with 80% power, "
      f"required n per group ≈ {n_required:.0f}.")
```

## Implementation Details

### 1) Test Selection Logic (Conceptual)
Use `references/test_selection_guide.md` as the primary decision aid. The selection is typically driven by:

- **Design**: independent vs. paired/repeated measures; number of groups (2 vs. 3+).
- **Outcome type**: continuous, ordinal, binary/categorical counts.
- **Distribution/assumptions**:
  - approximate normality (overall or within groups),
  - homogeneity of variance (between-group comparisons),
  - linearity and residual behavior (regression),
  - outliers and leverage points.

Common mappings:
- Two independent groups, continuous outcome:
  - normal + equal variances → Student’s t-test
  - normal + unequal variances → Welch’s t-test
  - non-normal/ordinal → Mann–Whitney U
- 3+ independent groups:
  - normal + equal variances → one-way ANOVA
  - unequal variances → Welch/Brown–Forsythe ANOVA
  - non-normal/ordinal → Kruskal–Wallis
- Relationships:
  - continuous–continuous → Pearson (normal) or Spearman (rank/non-normal)
  - continuous outcome + predictors → linear regression
  - binary outcome + predictors → logistic regression

### 2) Assumption Checks and Diagnostics
The automated workflow in `scripts/assumption_checks.py` (referenced in the original documentation) is expected to cover:

- **Outlier detection**: IQR rule and/or z-score thresholds.
- **Normality**: Shapiro–Wilk test plus Q–Q plot.
- **Homogeneity of variance**: Levene’s test plus group boxplots.
- **Linearity (regression)**: residuals vs fitted; optional component-plus-residual checks.

Key parameter:
- `alpha` (default commonly `0.05`): decision threshold for assumption tests.

Recommended remedies (see `references/assumptions_and_diagnostics.md`):
- Normality violations: consider robust/non-parametric tests, transformations, or bootstrap CIs.
- Variance heterogeneity: Welch variants; robust standard errors in regression.
- Linearity violations: transformations, polynomial terms, splines/GAMs.

### 3) Effect Sizes and Uncertainty
Effect sizes should be reported alongside inferential results (see `references/effect_sizes_and_power.md`):

- t-tests: **Cohen’s d** (or Hedges’ g for small samples)
- ANOVA: **partial η²** (or ω² depending on convention)
- correlation: **r** (already an effect size)
- chi-square: **Cramér’s V**
- regression: **R² / adjusted R²**, plus standardized coefficients where appropriate

Always prefer **confidence intervals** (frequentist) or **credible intervals** (Bayesian) to communicate precision.

### 4) Power Analysis
Implemented via `statsmodels.stats.power`:

- **A priori power**: solve for required `n` given target effect size, `alpha`, and desired power.
- **Sensitivity analysis**: solve for detectable effect size given achieved `n`, `alpha`, and desired power.

Avoid “post-hoc power” computed from observed p-values; use sensitivity analysis instead.

### 5) APA-Style Reporting Requirements
Use `references/reporting_standards.md` to ensure inclusion of:

- descriptive statistics (M, SD, n) per group/condition,
- test statistic + df + exact p (or thresholded p where required),
- effect size + CI,
- assumption checks performed and any corrective actions,
- post-hoc procedures and multiple-comparison corrections when applicable.

For Bayesian reporting (see `references/bayesian_statistics.md`), include:
- priors (type and scale),
- posterior summaries and credible intervals,
- Bayes Factor (if used),
- convergence diagnostics (e.g., R̂, ESS) and posterior predictive checks when relevant.

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.


## Input Validation

This skill accepts requests that match the documented purpose of `statistical-analysis` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `statistical-analysis` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
