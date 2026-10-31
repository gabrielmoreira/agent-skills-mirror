# Statistical Inference

Standards for the Inquire flow: choosing tests, checking assumptions, sizing
effects, quantifying uncertainty, and — the part that separates a data
scientist from a test-runner — knowing when a causal claim is earned.

Contents: [Test selection](#test-selection) ·
[Assumption checks](#assumption-checks) ·
[Effect sizes & CIs](#effect-sizes-and-confidence-intervals) ·
[Multiple comparisons](#multiple-comparisons) ·
[Power & sample size](#power-and-sample-size) ·
[Causality](#causality) · [Reporting](#reporting)

## Test selection

Identify three things: the question type, the outcome type, and the design
(independent vs paired groups). Then read off the tree.

### Comparing groups

| Design | Outcome | Test | Effect size |
|---|---|---|---|
| 2 independent groups | continuous, ~normal | Welch's t-test (default over Student's) | Cohen's d + CI |
| 2 independent groups | continuous, skewed/ordinal | Mann-Whitney U | rank-biserial r |
| 2 independent groups | binary (conversion, churn) | two-proportion z-test / chi-square; Fisher's exact if any expected cell < 5 | difference in proportions + CI, relative risk |
| 2 paired groups (before/after, matched) | continuous | paired t-test; Wilcoxon signed-rank if skewed | d for paired |
| 2 paired groups | binary | McNemar's test | odds ratio |
| 3+ independent groups | continuous | Welch's ANOVA (or one-way ANOVA if variances equal); Kruskal-Wallis if skewed | eta-squared |
| 3+ paired | continuous | repeated-measures ANOVA; Friedman if skewed | — |

After any significant 3+-group omnibus test, run pairwise post-hocs with
multiple-comparison correction (Tukey HSD, or pairwise tests + Holm).

### Relationships

| Variables | Method |
|---|---|
| two continuous, linear | Pearson correlation + CI |
| two continuous, monotonic or outlier-prone | Spearman correlation |
| continuous outcome, several predictors | linear regression (see diagnostics below) |
| binary outcome, predictors | logistic regression; report odds ratios with CIs |
| count outcome | Poisson regression; negative binomial if variance ≫ mean |
| time-to-event (churn timing, survival) | Kaplan-Meier curves, log-rank test, Cox regression |

Business data leans heavily on three cells of this table: two-proportion tests
(A/B tests on conversion), Welch's t (A/B on spend — beware skew; consider
Mann-Whitney or bootstrap the mean difference), and logistic regression
(driver analysis with confounders included).

## Assumption checks

Check assumptions with cheap code, not hope. Snippets below are paste-ready —
run them rather than skipping the step.

```python
import numpy as np
from scipy import stats

def check_groups(*groups, names=None):
    """Pre-test triage for comparing groups: sizes, skew, normality, variance."""
    names = names or [f"g{i}" for i in range(len(groups))]
    for name, g in zip(names, groups):
        g = np.asarray(g); g = g[~np.isnan(g)]
        line = f"{name}: n={len(g)}, mean={g.mean():.4g}, median={np.median(g):.4g}, skew={stats.skew(g):.2f}"
        if 3 <= len(g) <= 5000:
            _, p = stats.shapiro(g)
            line += f", shapiro_p={p:.3g}"
        print(line)
    if len(groups) >= 2:
        _, p_lev = stats.levene(*[np.asarray(g)[~np.isnan(np.asarray(g))] for g in groups])
        print(f"levene equal-variance p={p_lev:.3g}")
```

Interpretation, not ceremony:

- With n per group in the hundreds+, the CLT protects t-tests against
  non-normality; worry about *heavy skew and outliers* (which distort means
  themselves), not Shapiro p-values — at large n Shapiro rejects trivially.
- Unequal variances: already handled if you defaulted to Welch.
- **Independence is the assumption that actually kills analyses**, and no test
  detects it. Ask: are there repeated measures per user? Users clustered in
  the same stores/sessions? If observations cluster, naive p-values are
  overconfident — aggregate to one observation per cluster, or use
  mixed-effects / cluster-robust models.
- Regression diagnostics: plot residuals vs fitted (curvature → wrong
  functional form; funnel → heteroscedasticity, use robust SEs), check
  influential points (Cook's distance), check multicollinearity (VIF > 10 →
  coefficients uninterpretable, though predictions are fine).

When assumptions fail and no clean alternative exists, bootstrap:

```python
def bootstrap_ci(x, stat=np.mean, n_boot=10_000, ci=95, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x); x = x[~np.isnan(x)]
    boots = np.array([stat(rng.choice(x, size=len(x), replace=True)) for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [(100-ci)/2, 100-(100-ci)/2])
    return stat(x), (lo, hi)
```

The same idea gives a CI for a difference in means, a median, a ratio of
conversion rates — anything you can compute per resample.

## Effect sizes and confidence intervals

A p-value answers "could this be noise?" — never "does this matter?". With big
data everything is significant; the effect size is the finding.

- Always report the effect in *business units first* ("conversion +1.8
  percentage points, 95% CI [0.9, 2.7]"), standardized units second (d = 0.21).
- Rough anchors for Cohen's d: 0.2 small, 0.5 medium, 0.8 large — but the real
  benchmark is the framing brief's "good enough to act" bar. A d of 0.05 on
  revenue-per-user can be worth millions; a d of 0.6 on a vanity metric is
  worth nothing.
- A CI that includes zero but is narrow says "no effect big enough to care
  about" — a *useful, publishable* conclusion. A wide CI says "underpowered,
  we learned little." Distinguish these; never say "no effect" for the latter.

## Multiple comparisons

Every extra look inflates false positives: 20 independent tests at α=0.05
expect one bogus "discovery". This includes informal looks — testing many
segments, many metrics, peeking at an A/B test daily.

- Confirmatory analysis: correct within each family of tests — Holm-Bonferroni
  (safe default) or Benjamini-Hochberg FDR when the family is large and
  exploratory.
- Exploratory analysis: corrections optional, but then *label every finding as
  hypothesis-generating* and never report its uncorrected p-value as
  confirmation.
- A/B tests: decide the stopping rule before starting. Peek-and-stop-when
  -significant roughly triples the false positive rate; if continuous
  monitoring is needed, use sequential methods, otherwise fix n in advance
  (see power below).

## Power and sample size

"How many samples do we need?" — answer it before the experiment, and use it
diagnostically after.

Closed-form for the two common cases:

```python
# pip: statsmodels
from statsmodels.stats.power import TTestIndPower, NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# Two-sample t: n per group to detect d=0.2 at 80% power
n = TTestIndPower().solve_power(effect_size=0.2, power=0.8, alpha=0.05)

# Two proportions: baseline 5% conversion, want to detect lift to 5.5%
es = proportion_effectsize(0.055, 0.05)
n = NormalIndPower().solve_power(effect_size=es, power=0.8, alpha=0.05)
```

The *minimum detectable effect* (MDE) framing is usually more useful to a
stakeholder: "with the traffic you have in two weeks, we can detect a lift of
X or larger; smaller real lifts will look like noise." Compute it by solving
the same equations for effect size given n.

For anything non-textbook (skewed metrics, clustered units, sequential
designs), simulate: generate data under an assumed effect, run the planned
analysis, repeat ~1000 times, count how often p < α. Simulation-based power is
honest about the analysis you'll actually run.

## Causality

The question "why?" is a causal question, and correlation-based evidence
answers it only under conditions that must be argued, not assumed.

**The hierarchy of evidence:**

1. **Randomized experiment (A/B test).** Randomization severs confounding;
   "causes" is earned. Still verify: randomization balance (compare groups on
   pre-treatment covariates), no interference between units, no differential
   dropout (if one arm loses more users, the survivors aren't comparable).
2. **Quasi-experiments.** No randomization, but a defensible identification
   strategy: difference-in-differences (parallel-trends check is mandatory —
   plot pre-period trends), regression discontinuity, instrumental variables.
   Causal language allowed *with the design named and its assumption shown*.
3. **Observational with confounder adjustment.** Regression/matching
   controlling for known confounders. At best: "associated with, after
   adjusting for X, Y, Z" — plus an honest sentence about what unmeasured
   confounding could remain.
4. **Raw correlation.** "Is associated with." Nothing more, ever.

**Confounding is the default explanation**, not the exception. Before
reporting any driver, ask: what third variable could drive both? (Heavy users
both adopt the feature *and* retain — the feature may cause nothing.)
Conditioning has traps of its own: controlling for a *mediator* (a variable on
the causal path) erases the effect you're measuring, and conditioning on a
*collider* (a common consequence — e.g., analyzing only converted users)
manufactures fake associations. Selection effects are colliders in disguise.

**Wording audit** (also enforced in `checklists/analysis-review.md`): scan the
final report for "causes", "drives", "leads to", "because of", "impact of".
Each instance must be backed by level 1–2 evidence or rewritten to
"associated with". Watch for the bait-and-switch where the analysis says
"correlated" and the executive summary says "drives" — summaries must carry
the *weakest* causal language in the chain, not the strongest.

## Reporting

Report every test in one self-contained sentence pattern:

> [Groups and n] differed on [metric]: [group values], a difference of
> [effect in business units] (95% CI [..], [test], p = [..], [effect size]).
> [Practical interpretation against the framing bar.]

Report exact p-values (p = 0.03, not p < 0.05); never "marginally
significant"; never a bare "significant" without the effect size next to it.
State which comparisons were pre-planned and which were exploratory.
