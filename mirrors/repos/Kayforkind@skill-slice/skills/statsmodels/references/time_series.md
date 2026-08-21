# Time series (SARIMAX, VAR, VECM, ETS)

Load this file for seasonal ARIMA, VAR/VARMAX, VECM, state-space / ETS, Granger, IRF, and FEVD. Univariate ARIMA(p,d,q) is in `SKILL.md`. APIs match statsmodels 0.14.x (`https://www.statsmodels.org/stable/tsa.html`).

Do not shuffle time-series rows. Split by date.

## Stationarity and seasonality

```python
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose, STL, MSTL

print(adfuller(y, autolag="AIC")[1])   # H0: unit root
print(kpss(y, regression="c", nlags="auto")[1])  # H0: stationary
```

Difference until ADF rejects and KPSS does not. Seasonal difference monthly series with `D=1`, `s=12` rather than stuffing lag-12 into a non-seasonal ARIMA.

`seasonal_decompose` (additive vs multiplicative), `STL` (robust, odd `seasonal=`), and `MSTL` (several periods, e.g. 24 and 168) separate trend from season before modeling.

## SARIMAX

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
sar = SARIMAX(
    y,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),  # (P, D, Q, s); s=12 monthly, s=4 quarterly
    exog=X,                         # optional; must supply future X to forecast
).fit()
print(sar.summary())
fc = sar.get_forecast(steps=12, exog=X_future).summary_frame()
```

`enforce_stationarity=False` / `enforce_invertibility=False` are last-resort convergence knobs, not defaults.

AutoReg / ARX when the series is already stationary and you only need lagged y (and maybe X):

```python
from statsmodels.tsa.ar_model import AutoReg
ar = AutoReg(y, lags=5, exog=X, seasonal=False).fit()
```

## Exponential smoothing / ETS

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

hw = ExponentialSmoothing(y, trend="add", seasonal="add", seasonal_periods=12).fit()
ets = ETSModel(y, error="add", trend="add", seasonal="add", seasonal_periods=12).fit()
```

Additive season when the seasonal swing is level-stable; multiplicative when it grows with the level.

## VAR, Granger, IRF, FEVD

```python
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests

var = VAR(df_multi)  # columns = series, DatetimeIndex preferred
print(var.select_order(maxlags=15).summary())
vres = var.fit(maxlags=5, ic="aic")
print(grangercausalitytests(df_multi[["y", "x"]], maxlag=5, verbose=False))
irf = vres.irf(10)
fevd = vres.fevd(10)
```

Columns passed to `grangercausalitytests` are `[caused, causing]`. Orthogonal IRFs (`orth=True`) depend on column order (Cholesky).

VARMAX adds MA terms and exogenous inputs:

```python
from statsmodels.tsa.statespace.varmax import VARMAX
vmx = VARMAX(df_multi, order=(1, 1), exog=X).fit()
```

## Cointegration / VECM

If several I(1) series share a stochastic trend, VAR-in-differences drops the long-run relation. Johansen + VECM keep it.

```python
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
j = coint_johansen(df_multi, det_order=0, k_ar_diff=1)
vecm = VECM(df_multi, k_ar_diff=1, coint_rank=1).fit()
```

ARDL / UECM cover single-equation distributed lags (`statsmodels.tsa.ardl`).

## State space extras

Unobserved components, dynamic factors, and Markov switching live under `statsmodels.tsa.statespace` and `statsmodels.tsa.regime_switching`. Prefer SARIMAX/ETS unless the state is the object of interest.

```python
from statsmodels.tsa.statespace.dynamic_factor import DynamicFactor
dfm = DynamicFactor(df_multi, k_factors=1, factor_order=1).fit()
```

## Residual checks after a fit

```python
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
print(acorr_ljungbox(sar.resid, lags=10, return_df=True))
print(het_arch(sar.resid.dropna(), nlags=10)[1])
sar.plot_diagnostics()
```

Ljung–Box p-values should stay large if the mean model absorbed serial correlation. Significant ARCH in residuals is a variance model (GARCH), not more ARIMA lags.

## Evaluation

- AIC/BIC for in-sample specification search.
- Hold out the **last** block; report RMSE/MAE there.
- Rolling one-step updates beat a single static multi-step path for honesty.
- `TimeSeriesSplit` expanding windows; never `KFold(shuffle=True)`.
- MAPE dies on zeros and sign changes; prefer MAE/RMSE then.

## Pitfalls

- Fitting ARIMA on a unit-root series with `d=0`.
- Seasonal period `s=12` on quarterly data (use 4).
- Forecasting SARIMAX without future `exog`.
- Treating dynamic multi-step forecasts as if they were one-step static.
- Leaking test-set scaling or differencing parameters computed on the full sample.
