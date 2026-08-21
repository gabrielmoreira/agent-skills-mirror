# Discrete choice and count models

Load this file for MNLogit, ordered outcomes, conditional logit, zero-inflated, and hurdle specs, plus marginal effects. Binary Logit/Probit live in `SKILL.md`; this file goes past them. APIs match statsmodels 0.14.x (`https://www.statsmodels.org/stable/discretemod.html`).

```python
import numpy as np
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Logit, Probit, MNLogit, Poisson, NegativeBinomial
X = sm.add_constant(X_data)
```

## Binary extras

Odds ratios and average marginal effects:

```python
logit = Logit(y_bin, X).fit()
print(np.exp(logit.params))
print(np.exp(logit.conf_int()))
print(logit.get_margeff(at="overall").summary())  # dy/dx, not log-odds
print(logit.prsquared)
```

Probit uses Φ(Xβ). Coefficients are not on the same scale as Logit; compare `get_margeff()`, not raw β. Formula helpers: `smf.logit`, `smf.probit`.

Complete separation (a dummy perfectly predicts y) prevents MLE from existing. Drop the dummy or regularize; do not “just raise maxiter”.

## Unordered multinomial

`MNLogit` needs integer codes `0..J-1`. Category 0 is the reference. `predict` returns an `(n, J)` probability matrix.

```python
mn = MNLogit(y_cat, X).fit()
probs = mn.predict(X)
hat = probs.argmax(axis=1)
print(np.exp(mn.params))  # relative-risk ratios vs reference
```

Formula: `smf.mnlogit("choice ~ x1 + C(region)", data=df)`.

## Alternative-specific (conditional) logit

Long data: one row per person–alternative, with a choice dummy and `groups=` person id.

```python
from statsmodels.discrete.conditional_models import ConditionalLogit
cl = ConditionalLogit(y_choice, X_alts, groups=person_id).fit()
```

Use this when regressors vary by alternative (price of mode A vs B), not when they vary only by person.

## Ordered outcomes

Ratings, Likert, low/medium/high: keep the order.

```python
from statsmodels.miscmodels.ordinal_model import OrderedModel
ordm = OrderedModel(y_ord, X, distr="logit").fit(method="bfgs")  # or distr="probit"
probs = ordm.predict(X)
```

Do not feed ordered labels to `MNLogit` unless the order truly does not matter.

## Counts: Poisson, NB, ZIP, hurdle

Poisson `log(λ) = Xβ`. Incident-rate ratios are `exp(β)`. Offset for exposure: `Poisson(y, X, offset=np.log(exposure))`.

If `var(y) / mean(y)` is well above 1, or GLM `pearson_chi2 / df_resid > 1.5`, fit `NegativeBinomial` and compare AIC plus an LR test on the extra `alpha`.

Excess zeros: a separate inflation process.

```python
from statsmodels.discrete.count_model import (
    ZeroInflatedPoisson,
    ZeroInflatedNegativeBinomialP,
)
zipm = ZeroInflatedPoisson(y, X, exog_infl=X_infl).fit()
zinb = ZeroInflatedNegativeBinomialP(y, X, exog_infl=X_infl).fit()
```

`exog_infl` is the design for P(structural zero). If omitted, statsmodels uses an intercept-only inflation equation.

Hurdle (zero vs positive as two sequential stages), added in 0.14:

```python
from statsmodels.discrete.truncated_model import HurdleCountModel
hurdle = HurdleCountModel(y, X, dist="poisson", zerodist="poisson").fit()
```

`dist` / `zerodist` are `"poisson"` or `"negbin"`. NB zeros are weakly identified if the hurdle mean barely varies.

Formula helpers: `smf.poisson`, `smf.negativebinomial`.

## Selection

- Nested: LR on `2*(llf_full - llf_reduced)`.
- Non-nested (Logit vs Probit, ZIP vs hurdle): AIC/BIC, not LR.
- Predictive binary work: hold-out AUC, not in-sample pseudo-R² alone.
- Always `add_constant` unless the design already has it.

## Pitfalls

- Treating MNLogit β as if they were binary Logit odds ratios for every class.
- Poisson on overdispersed or zero-inflated counts.
- Reporting coefficients and skipping `get_margeff()`.
- Feeding string labels into MNLogit/OrderedModel without encoding.
- Comparing LR tests across models that dropped different rows.
