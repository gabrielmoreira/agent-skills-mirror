# Diagnostics, robust covariance, and multiple testing

Load this file for residual tests, influence cutoffs, sandwich types, ANOVA/post-hoc, and power. APIs match statsmodels 0.14.x (`https://www.statsmodels.org/stable/diagnostic.html`, `https://www.statsmodels.org/stable/stats.html`).

```python
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import (
    acorr_ljungbox,
    acorr_breusch_godfrey,
    het_breuschpagan,
    het_white,
    het_arch,
    het_goldfeldquandt,
    linear_reset,
    linear_harvey_collier,
    normal_ad,
    lilliefors,
)
from statsmodels.stats.stattools import durbin_watson, jarque_bera, omni_normtest
```

## Residual battery (after OLS/GLM/ARIMA)

| Question | Call | Reject H0 when |
| --- | --- | --- |
| Serial correlation (general) | `acorr_ljungbox(resid, lags=10, return_df=True)` | p < 0.05 |
| AR(1) shortcut | `durbin_watson(resid)` | far from 2 |
| Serial correlation with lagged y | `acorr_breusch_godfrey(results, nlags=k)` | p < 0.05 |
| Heteroskedasticity | `het_breuschpagan(resid, exog)` | p < 0.05 |
| Heteroskedasticity (general) | `het_white(resid, exog)` | p < 0.05 |
| ARCH | `het_arch(resid, nlags=k)` | p < 0.05 |
| Normality | `jarque_bera(resid)` / `omni_normtest` / `normal_ad` / `lilliefors` | p < 0.05 |
| Neglected nonlinearity | `linear_reset(results, power=2)` | `reset.pvalue` small |
| Linearity (Harvey–Collier) | `linear_harvey_collier(results)` | p < 0.05 |

`linear_reset` in 0.14 returns a `ContrastResults` object (use `.pvalue`), not a 2-tuple.

Goldfeld–Quandt splits the sample to test whether variance changes with a column (`het_goldfeldquandt(y, X, idx=column)`).

Normality of residuals is a large-sample convenience for OLS t/F; sandwich SEs still want a correct mean, not Gaussian errors.

## Influence

```python
infl = ols.get_influence()
n, p = len(y), len(ols.params)
high_hat = infl.hat_matrix_diag > (2 * p / n)
high_cook = infl.cooks_distance[0] > (4 / n)
high_dffits = np.abs(infl.dffits[0]) > (2 * np.sqrt(p / n))
high_dfbeta = np.abs(infl.dfbetas) > (2 / np.sqrt(n))
out_stud = np.abs(infl.resid_studentized_external) > 3
```

GLM/MLE fits expose `get_influence()` with the same Cook/leverage idea; some measures are OLS-only. Plot with `statsmodels.graphics.regressionplots.influence_plot`.

VIF: `variance_inflation_factor(exog, i)`. Treat VIF > 10 on a *regressor* (not the constant) as a collinearity flag. `results.condition_number` above ~30 is the same story in one number.

## Sandwich catalog

```python
# Prefer passing cov_type at fit time, or wrap an existing results object.
import statsmodels.api as sm
hc3 = sm.OLS(y, X).fit(cov_type="HC3")
hac = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
cl = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": cluster_ids})
wrapped = sm.OLS(y, X).fit().get_robustcov_results(cov_type="HC3")
```

| `cov_type` | Robust to |
| --- | --- |
| `HC0`–`HC3` | Heteroskedasticity (prefer HC3 in small n) |
| `HAC` | Heteroskedasticity + autocorrelation (set `maxlags`) |
| `cluster` | Within-group residual correlation |
| `hac-panel` / Driscoll–Kraay helpers | Panels with cross-section dependence |

Do not use default OLS SEs after a significant Breusch–Pagan or Ljung–Box.

## Hypothesis tests beyond the regression table

Proportions: `statsmodels.stats.proportion.proportions_ztest`.

ANOVA: `statsmodels.stats.anova.anova_lm` on formula OLS; repeated measures via `AnovaRM`.

Non-parametric companions (SciPy, often paired with statsmodels tables): Mann–Whitney, Wilcoxon, Kruskal–Wallis. Sign test: `statsmodels.stats.descriptivestats.sign_test`.

## Multiple comparisons

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests

print(pairwise_tukeyhsd(endog, groups, alpha=0.05).summary())
rej, p_adj, _, _ = multipletests(pvalues, alpha=0.05, method="fdr_bh")
# method="bonferroni" is stricter; "fdr_bh" is Benjamini–Hochberg
```

Tukey HSD after a significant one-way ANOVA. FDR when many tests share a family; Bonferroni when you need FWER control.

## Power

```python
from statsmodels.stats.power import TTestIndPower, FTestAnovaPower
print(TTestIndPower().solve_power(effect_size=0.5, power=0.8, alpha=0.05, ratio=1.0))
```

Solve for `nobs`, `effect_size`, `power`, or `alpha` — one unknown at a time. Cohen d (t) and Cohen f (ANOVA) are the usual effect-size inputs. Do not reverse-engineer power from the p-value of the sample you already collected and call it a design.

## Pitfalls

- Running twenty diagnostics and “correcting” the model until every p > 0.05 (researcher degrees of freedom).
- Treating Durbin–Watson as a substitute for Ljung–Box with lagged dependent variables.
- Applying OLS influence rules blindly to logit/Poisson.
- Skipping multiple-testing correction on a wall of p-values.
- Using LR tests on non-nested or unequal-sample fits.
