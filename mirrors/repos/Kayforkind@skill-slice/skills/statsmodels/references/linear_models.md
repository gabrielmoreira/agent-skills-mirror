# Linear models (OLS / WLS / GLS / GLSAR)

Load this file when choosing among OLS, WLS, GLS, and GLSAR, picking a sandwich covariance, or reading influence statistics. APIs match statsmodels 0.14.x (`https://www.statsmodels.org/stable/regression.html`).

Always add an intercept unless the specification truly has none:

```python
import statsmodels.api as sm
X = sm.add_constant(X_data)
```

## Estimator pick

| Class | Error covariance | Reach for it when |
| --- | --- | --- |
| `sm.OLS` | Σ = I | Homoskedastic, independent residuals |
| `sm.WLS` | diagonal Σ | Known (or feasible) per-row weights |
| `sm.GLS` | arbitrary Σ | A full residual covariance is available |
| `sm.GLSAR` | AR(p) Σ | Serial correlation in a time-ordered regression |

OLS is the default start. Switch after diagnostics, not before.

```python
ols = sm.OLS(y, X).fit()
print(ols.summary())
print(ols.params, ols.bse, ols.rsquared_adj)
```

WLS takes inverse-variance weights. Feasible WLS estimates those weights from an OLS residual model:

```python
import numpy as np
ols = sm.OLS(y, X).fit()
log_var = sm.OLS(np.log(ols.resid**2), X).fit()
w = 1.0 / np.exp(log_var.fittedvalues)
wls = sm.WLS(y, X, weights=w).fit()
```

GLS needs an `(n, n)` `sigma`. GLSAR iterates the AR coefficients:

```python
glsar = sm.GLSAR(y, X, rho=1)
glsar_res = glsar.iterative_fit()
print(glsar_res.model.rho)
```

Formula API dummy-codes categories and interactions:

```python
import statsmodels.formula.api as smf
fit = smf.ols("y ~ x1 + C(group) + x1:x2", data=df).fit()
```

## Quantile, rolling, mixed

Median and other conditional quantiles (robust to tail leverage):

```python
from statsmodels.regression.quantile_regression import QuantReg
qr = QuantReg(y, X)
for q in (0.1, 0.5, 0.9):
    print(q, qr.fit(q=q).params)
```

Rolling windows and recursive CUSUM:

```python
from statsmodels.regression.rolling import RollingOLS
from statsmodels.regression.recursive_ls import RecursiveLS
roll = RollingOLS(y, X, window=60).fit()
rls = RecursiveLS(y, X).fit()
print(rls.cusum)
```

Clustered / nested data: random intercepts via `MixedLM`, or keep OLS and use cluster-robust SEs (below).

```python
from statsmodels.regression.mixed_linear_model import MixedLM
mixed = MixedLM(y, X, groups=group_ids).fit()
```

## Sandwich covariance

Keep the mean model; change how SEs are computed.

```python
hc3 = ols.get_robustcov_results(cov_type="HC3")
hac = ols.get_robustcov_results(cov_type="HAC", maxlags=4)
cl = ols.get_robustcov_results(cov_type="cluster", groups=cluster_ids)
print(hc3.summary())
```

`HC0`–`HC3` are heteroskedasticity-robust (HC3 is the conservative default). `HAC` is Newey–West. Cluster when residuals share a group (firm, school, country).

## Influence and collinearity

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics.regressionplots import influence_plot

infl = ols.get_influence()
leverage = infl.hat_matrix_diag          # high if > 2p/n
cooks = infl.cooks_distance[0]           # high if > 4/n
dffits = infl.dffits[0]                  # high if |DFFITS| > 2*sqrt(p/n)
dfbetas = infl.dfbetas

vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(ols.condition_number)  # worry above ~30
```

`mean_ci_*` in `get_prediction(...).summary_frame()` is the mean confidence band. `obs_ci_*` is the wider prediction interval for a new draw.

## Nested vs non-nested comparison

```python
from statsmodels.stats.anova import anova_lm
print(anova_lm(restricted, full))
print(full.aic, full.bic)  # lower wins among non-nested specs
print(full.f_test("x1 = x2 = 0"))
```

## Pitfalls

- Dropping `add_constant` silently fits through the origin and wrecks R².
- OLS t-tests are invalid under heteroskedasticity; use HC3 or WLS, not wishful thinking.
- Autocorrelated residuals need GLSAR or HAC, not more lags of *y* stuffed into OLS.
- VIF on the constant column is expected to be large; interpret VIF on the regressors.
- Do not compare AIC across fits that dropped different rows.
