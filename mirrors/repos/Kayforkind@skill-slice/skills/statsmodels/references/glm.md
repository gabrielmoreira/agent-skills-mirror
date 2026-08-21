# GLM families and links

Load this file for family/link choice, pseudo-R², IRLS convergence, offsets, and GLM influence. APIs match statsmodels 0.14.x (`https://www.statsmodels.org/stable/glm.html`).

A GLM is `g(μ) = Xβ` with a one-parameter exponential family and a variance function of the mean.

```python
import numpy as np
import statsmodels.api as sm
X = sm.add_constant(X_data)
```

## Family vs outcome

| Family | Outcome | Canonical link | Default use |
| --- | --- | --- | --- |
| `Binomial()` | 0/1 or k/n | logit | Odds ratios |
| `Poisson()` | counts | log | Event rates |
| `NegativeBinomial(alpha=...)` | overdispersed counts | log | Variance > mean |
| `Gaussian()` | unbounded continuous | identity | GLM-shaped OLS |
| `Gamma()` | positive continuous | inverse | Costs, durations |
| `InverseGaussian()` | positive, variance ∝ μ³ | inverse squared | Alternative to Gamma |
| `Tweedie(var_power=1.5)` | zeros + continuous | log | Insurance-style claims |

```python
pois = sm.GLM(y_counts, X, family=sm.families.Poisson()).fit()
print(pois.summary())
print(pois.pearson_chi2 / pois.df_resid)  # >> 1.5 → leave Poisson
```

Rate models need an offset on the log-exposure scale (log link only):

```python
rate = sm.GLM(y_counts, X, family=sm.families.Poisson(), offset=np.log(exposure)).fit()
```

Binomial with a log link targets **risk ratios**, not odds ratios, and can fail to stay in (0, 1):

```python
risk = sm.GLM(y_bin, X, family=sm.families.Binomial(link=sm.families.links.Log())).fit()
print(np.exp(risk.params))
```

Gamma with a log link is usually easier to interpret than the canonical inverse:

```python
gam = sm.GLM(
    y_cost, X, family=sm.families.Gamma(link=sm.families.links.Log())
).fit()
print(np.exp(gam.params))
```

Tweedie `var_power` between 1 and 2 is the compound Poisson–Gamma case.

When the GLM NegativeBinomial `alpha` is unknown, estimate it with the discrete count model instead of guessing:

```python
from statsmodels.discrete.discrete_model import NegativeBinomial
nb = NegativeBinomial(y_counts, X).fit()
```

## Links that exist

`Identity`, `Log`, `Logit`, `Probit`, `CLogLog`, `InversePower`, `InverseSquared`, `Sqrt`, `Power`. Not every pair is valid; statsmodels rejects illegal family/link combinations at construct time.

Canonical defaults: Binomial→logit, Poisson→log, Gamma→inverse, Gaussian→identity, InverseGaussian→inverse squared.

## Fit objects

```python
print(glm.params, glm.bse, glm.pvalues)
print(glm.aic, glm.bic, glm.deviance, glm.null_deviance, glm.llf)
print(glm.resid_deviance, glm.resid_pearson, glm.resid_response)
mu = glm.predict(X_new)
```

McFadden-style pseudo-R² from deviance:

```python
pseudo = 1.0 - (glm.deviance / glm.null_deviance)
```

`loglike` / AIC / LR tests are **not** valid for Poisson, Binomial, or NegativeBinomial when variance weights are in play (quasi-likelihood). See the GLM notes on `freq_weights` vs `var_weights`.

IRLS may not converge. Read `.fit()` warnings; try `method="lbfgs"`, better starting values, or drop complete-separation dummies in Binomial.

## Diagnostics

```python
from scipy import stats
disp = glm.pearson_chi2 / glm.df_resid
gof = 1 - stats.chi2.cdf(glm.deviance, glm.df_resid)

infl = glm.get_influence()
cooks = infl.cooks_distance[0]
```

Nested families: LR = `2 * (full.llf - reduced.llf)` on χ² with the extra-parameter df. Non-nested: AIC/BIC only.

Sandwich SEs: `glm.get_robustcov_results(cov_type="HC0")` or `cov_type="cluster"`.

## Pitfalls

- Interpreting β on the link scale as a unit change in *y*.
- Poisson with overdispersion (use NB or a sandwich).
- Identity link on a bounded mean (predictions leave [0, 1] or go negative).
- Complete separation in Binomial (infinite coefficients, failed IRLS).
- Forgetting `log(exposure)` when the outcome is a count over unequal windows.
- Comparing AIC across fits that used different observation sets.
