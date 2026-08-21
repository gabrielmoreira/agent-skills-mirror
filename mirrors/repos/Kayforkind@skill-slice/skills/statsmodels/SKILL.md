---
name: statsmodels
description: "Fits statsmodels OLS/WLS/GLS, GLM families, logit/probit/MNLogit, and ARIMA/SARIMAX/VAR with inference, sandwich SEs, and residual tests. Use for publication tables, forecast intervals, or assumption checks (Breusch-Pagan, ADF, Cook's distance). Not for scikit-learn pipelines or NumPy-only numerics; never a symbolic-algebra chair (sympy)."
version: 1.0.1
license: BSD-3-Clause license
metadata:
  skill-author: K-Dense Inc.
risk: unknown
source: community
---

## Overview

Statsmodels is Python's premier library for statistical modeling, providing tools for estimation, inference, and diagnostics across a wide range of statistical methods. Use this skill for rigorous statistical analysis — from simple linear regression to complex time series models and econometric analyses.

## When to Use

Apply this skill when the task involves any of the following:

- Fitting regression models (OLS, WLS, GLS, quantile regression)
- Performing generalized linear modeling (logistic, Poisson, Gamma, etc.)
- Analyzing discrete outcomes (binary, multinomial, count, ordinal)
- Conducting time series analysis (ARIMA, SARIMAX, VAR, forecasting)
- Running statistical tests and diagnostics
- Testing model assumptions (heteroskedasticity, autocorrelation, normality)
- Detecting outliers and influential observations
- Comparing models (AIC/BIC, likelihood ratio tests)
- Estimating causal effects
- Producing publication-ready statistical tables and inference

**Trigger keywords:** OLS, regression, logistic, logit, probit, Poisson, GLM, ARIMA, SARIMAX, time series, forecast, AIC, BIC, heteroskedasticity, autocorrelation, Durbin-Watson, Breusch-Pagan, Cook's distance, marginal effects, odds ratios, VAR, cointegration, stationarity, ADF test.

## Prerequisites

1. **Python 3.8+** installed and available on PATH.
2. **statsmodels** installed: `pip install statsmodels` (or `conda install -c conda-forge statsmodels`).
3. Supporting libraries: `numpy`, `pandas`, `scipy`, `matplotlib` (for diagnostics plots).
4. Optional: `scikit-learn` for cross-validation and classification metrics.
5. On Windows (PowerShell), ensure your virtual environment is activated before running scripts:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install statsmodels pandas numpy scipy matplotlib scikit-learn
   ```

## Procedure

### 1. Linear Regression (OLS)

```python
import statsmodels.api as sm
import numpy as np
import pandas as pd

# Prepare data - ALWAYS add constant for intercept
X = sm.add_constant(X_data)

# Fit OLS model
model = sm.OLS(y, X)
results = model.fit()

# View comprehensive results
print(results.summary())

# Key results
print(f"R-squared: {results.rsquared:.4f}")
print(f"Coefficients:\n{results.params}")
print(f"P-values:\n{results.pvalues}")

# Predictions with confidence intervals
predictions = results.get_prediction(X_new)
pred_summary = predictions.summary_frame()
print(pred_summary)  # includes mean, CI, prediction intervals

# Diagnostics
from statsmodels.stats.diagnostic import het_breuschpagan
bp_test = het_breuschpagan(results.resid, X)
print(f"Breusch-Pagan p-value: {bp_test[1]:.4f}")

# Visualize residuals
import matplotlib.pyplot as plt
plt.scatter(results.fittedvalues, results.resid)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted values')
plt.ylabel('Residuals')
plt.show()
```

**When to load reference:** If you need detailed guidance on model selection among OLS/WLS/GLS/GLSAR, robust standard error types (HC0–HC3, HAC, cluster), or influence statistics, load `references/linear_models.md`.

### 2. Logistic Regression (Binary Outcomes)

```python
from statsmodels.discrete.discrete_model import Logit

# Add constant
X = sm.add_constant(X_data)

# Fit logit model
model = Logit(y_binary, X)
results = model.fit()

print(results.summary())

# Odds ratios
odds_ratios = np.exp(results.params)
print("Odds ratios:\n", odds_ratios)

# Predicted probabilities
probs = results.predict(X)

# Binary predictions (0.5 threshold)
predictions = (probs > 0.5).astype(int)

# Model evaluation
from sklearn.metrics import classification_report, roc_auc_score

print(classification_report(y_binary, predictions))
print(f"AUC: {roc_auc_score(y_binary, probs):.4f}")

# Marginal effects
marginal = results.get_margeff()
print(marginal.summary())
```

**When to load reference:** For multinomial (MNLogit), ordered, conditional logit, zero-inflated, or hurdle models, load `references/discrete_choice.md`.

### 3. Time Series (ARIMA)

```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Check stationarity
from statsmodels.tsa.stattools import adfuller

adf_result = adfuller(y_series)
print(f"ADF p-value: {adf_result[1]:.4f}")

if adf_result[1] > 0.05:
    # Series is non-stationary, difference it
    y_diff = y_series.diff().dropna()

# Plot ACF/PACF to identify p, q
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
plot_acf(y_diff, lags=40, ax=ax1)
plot_pacf(y_diff, lags=40, ax=ax2)
plt.show()

# Fit ARIMA(p,d,q)
model = ARIMA(y_series, order=(1, 1, 1))
results = model.fit()

print(results.summary())

# Forecast
forecast = results.forecast(steps=10)
forecast_obj = results.get_forecast(steps=10)
forecast_df = forecast_obj.summary_frame()

print(forecast_df)  # includes mean and confidence intervals

# Residual diagnostics
results.plot_diagnostics(figsize=(12, 8))
plt.show()
```

**When to load reference:** For SARIMAX, VAR/VARMAX, VECM, state space, exponential smoothing, Granger causality, IRF, or FEVD, load `references/time_series.md`.

### 4. Generalized Linear Models (GLM)

```python
import statsmodels.api as sm

# Poisson regression for count data
X = sm.add_constant(X_data)
model = sm.GLM(y_counts, X, family=sm.families.Poisson())
results = model.fit()

print(results.summary())

# Rate ratios (for Poisson with log link)
rate_ratios = np.exp(results.params)
print("Rate ratios:\n", rate_ratios)

# Check overdispersion
overdispersion = results.pearson_chi2 / results.df_resid
print(f"Overdispersion: {overdispersion:.2f}")

if overdispersion > 1.5:
    # Use Negative Binomial instead
    from statsmodels.discrete.count_model import NegativeBinomial
    nb_model = NegativeBinomial(y_counts, X)
    nb_results = nb_model.fit()
    print(nb_results.summary())
```

**When to load reference:** For family selection (Binomial, Gamma, Inverse Gaussian, Tweedie), link function guidance, or pseudo R-squared interpretation, load `references/glm.md`.

### 5. Formula API (R-style)

Statsmodels supports R-style formulas for intuitive model specification:

```python
import statsmodels.formula.api as smf

# OLS with formula
results = smf.ols('y ~ x1 + x2 + x1:x2', data=df).fit()

# Categorical variables (automatic dummy coding)
results = smf.ols('y ~ x1 + C(category)', data=df).fit()

# Interactions
results = smf.ols('y ~ x1 * x2', data=df).fit()  # x1 + x2 + x1:x2

# Polynomial terms
results = smf.ols('y ~ x + I(x**2)', data=df).fit()

# Logit
results = smf.logit('y ~ x1 + x2 + C(group)', data=df).fit()

# Poisson
results = smf.poisson('count ~ x1 + x2', data=df).fit()

# ARIMA (not available via formula, use regular API)
```

### 6. Model Selection and Comparison

**Information criteria (non-nested models):**

```python
# Compare models using AIC/BIC
models = {
    'Model 1': model1_results,
    'Model 2': model2_results,
    'Model 3': model3_results
}

comparison = pd.DataFrame({
    'AIC': {name: res.aic for name, res in models.items()},
    'BIC': {name: res.bic for name, res in models.items()},
    'Log-Likelihood': {name: res.llf for name, res in models.items()}
})

print(comparison.sort_values('AIC'))
# Lower AIC/BIC indicates better model
```

**Likelihood ratio test (nested models only):**

```python
from scipy import stats

lr_stat = 2 * (full_model.llf - reduced_model.llf)
df = full_model.df_model - reduced_model.df_model
p_value = 1 - stats.chi2.cdf(lr_stat, df)

print(f"LR statistic: {lr_stat:.4f}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Full model significantly better")
else:
    print("Reduced model preferred (parsimony)")
```

**Cross-validation:**

```python
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []

for train_idx, val_idx in kf.split(X):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    model = sm.OLS(y_train, X_train).fit()
    y_pred = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    cv_scores.append(rmse)

print(f"CV RMSE: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
```

### 7. Statistical Tests and Diagnostics

**When to load reference:** For comprehensive testing procedures — residual diagnostics, influence/outlier detection, hypothesis tests (parametric and non-parametric), ANOVA, multiple comparisons correction, robust covariance matrices, power analysis — load `references/stats_diagnostics.md`.

Key capabilities:

- **Autocorrelation tests:** Ljung-Box, Durbin-Watson, Breusch-Godfrey
- **Heteroskedasticity tests:** Breusch-Pagan, White, ARCH
- **Normality tests:** Jarque-Bera, Omnibus, Anderson-Darling, Lilliefors
- **Specification tests:** RESET, Harvey-Collier
- **Influence:** Leverage (hat values), Cook's distance, DFFITS, DFBETAs, studentized residuals
- **Robust SEs:** HC0–HC3, HAC (Newey-West), cluster-robust
- **Multiple comparisons:** Tukey's HSD, Bonferroni, FDR

### Common Workflows

**Workflow 1 — Linear Regression Analysis:**
1. Explore data (plots, descriptives)
2. Fit initial OLS model
3. Check residual diagnostics
4. Test for heteroskedasticity, autocorrelation
5. Check for multicollinearity (VIF)
6. Identify influential observations
7. Refit with robust SEs if needed
8. Interpret coefficients and inference
9. Validate on holdout or via CV

**Workflow 2 — Binary Classification:**
1. Fit logistic regression (Logit)
2. Check for convergence issues
3. Interpret odds ratios
4. Calculate marginal effects
5. Evaluate classification performance (AUC, confusion matrix)
6. Check for influential observations
7. Compare with alternative models (Probit)
8. Validate predictions on test set

**Workflow 3 — Count Data Analysis:**
1. Fit Poisson regression
2. Check for overdispersion
3. If overdispersed, fit Negative Binomial
4. Check for excess zeros (consider ZIP/ZINB)
5. Interpret rate ratios
6. Assess goodness of fit
7. Compare models via AIC
8. Validate predictions

**Workflow 4 — Time Series Forecasting:**
1. Plot series, check for trend/seasonality
2. Test for stationarity (ADF, KPSS)
3. Difference if non-stationary
4. Identify p, q from ACF/PACF
5. Fit ARIMA or SARIMAX
6. Check residual diagnostics (Ljung-Box)
7. Generate forecasts with confidence intervals
8. Evaluate forecast accuracy on test set

## Reference Files

This skill bundles detailed reference files. Load them on demand:

| File | Load when... |
|------|-------------|
| `references/linear_models.md` | Choosing among OLS/WLS/GLS/GLSAR, need robust SE details, influence statistics, or multicollinearity diagnostics |
| `references/glm.md` | Selecting distribution families or link functions, interpreting pseudo R-squared, or troubleshooting GLM convergence |
| `references/discrete_choice.md` | Working with multinomial, ordered, conditional logit, zero-inflated, or hurdle models; interpreting marginal effects |
| `references/time_series.md` | Using SARIMAX, VAR/VARMAX, VECM, state space, exponential smoothing, Granger causality, IRF, or FEVD |
| `references/stats_diagnostics.md` | Running specific diagnostic tests, multiple comparisons correction, power analysis, or robust covariance selection |

**Search patterns (PowerShell):**

```powershell
# Find information about specific models
Select-String -Path references\*.md -Pattern "Quantile Regression"

# Find diagnostic tests
Select-String -Path references\stats_diagnostics.md -Pattern "Breusch-Pagan"

# Find time series guidance
Select-String -Path references\time_series.md -Pattern "SARIMAX"
```

## Pitfalls

1. **Forgetting constant term:** Always use `sm.add_constant()` unless no intercept is desired. Without it, coefficients and R-squared are meaningless.
2. **Ignoring assumptions:** Check residuals, heteroskedasticity, autocorrelation before trusting inference.
3. **Wrong model for outcome type:** Binary → Logit/Probit, Count → Poisson/NB, not OLS.
4. **Not checking convergence:** Look for optimization warnings in `.fit()` output; non-convergence invalidates results.
5. **Misinterpreting coefficients:** Remember link functions — `exp(β)` for log link (rate ratios), `exp(β)` for logit link (odds ratios).
6. **Using Poisson with overdispersion:** Check `pearson_chi2 / df_resid`; if > 1.5, switch to Negative Binomial.
7. **Not using robust SEs:** When heteroskedasticity or clustering is present, default SEs are wrong. Use `cov_type='HC3'` or `cov_type='cluster'`.
8. **Overfitting:** Too many parameters relative to sample size inflates R-squared and destabilizes estimates.
9. **Data leakage:** Never fit on test data or use future information in time series.
10. **Not validating predictions:** Always check out-of-sample performance; in-sample fit is necessary but not sufficient.
11. **Comparing non-nested models with LR test:** Use AIC/BIC for non-nested; LR test only valid for nested models.
12. **Ignoring influential observations:** Check Cook's distance and leverage; single points can drive results.
13. **Multiple testing without correction:** Correct p-values (Bonferroni, FDR) when testing many hypotheses.
14. **Not differencing non-stationary time series:** Fitting ARIMA on non-stationary data without differencing produces spurious results.
15. **Confusing prediction vs confidence intervals:** Prediction intervals are wider — they account for both parameter uncertainty and individual observation variance.

## Verification

After fitting any model, verify correctness with these checks:

**1. Confirm model fitted without errors:**
```python
print(results.summary())
# Should show coefficient table, R-squared, F-statistic, and no convergence warnings
```

**2. Verify constant term present (for models requiring intercept):**
```python
print(X.columns)  # 'const' should appear if sm.add_constant() was used
print(results.params.index)  # should include 'const'
```

**3. Check residual diagnostics:**
```python
from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
bp = het_breuschpagan(results.resid, X)
print(f"Breusch-Pagan p-value: {bp[1]:.4f}")  # > 0.05 → no heteroskedasticity
```

**4. Verify predictions shape and range:**
```python
preds = results.predict(X_new)
print(f"Shape: {preds.shape}")  # should match X_new rows
print(f"Range: [{preds.min():.4f}, {preds.max():.4f}]")
```

**5. Confirm statsmodels installation and version:**
```powershell
python -c "import statsmodels; print(statsmodels.__version__)"
# Expected: 0.14.x or later
```

**6. Validate time series stationarity after differencing:**
```python
from statsmodels.tsa.stattools import adfuller
adf_result = adfuller(y_diff)
print(f"ADF p-value after differencing: {adf_result[1]:.4f}")
# Should be < 0.05 for stationarity
```

## Related Skills

- **pandas** — data manipulation and preparation before modeling
- **scikit-learn** — machine learning models, cross-validation infrastructure, classification metrics
- **matplotlib** — visualization of residuals, diagnostics, and forecasts
- **scipy** — statistical distributions, hypothesis tests, optimization routines

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
