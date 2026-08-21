---
name: trend-analysis
version: 1.1.1
description: "Tests long-term time-series trends with linear regression and Mann-Kendall / Sen's slope. Use when asking whether a series is statistically increasing or decreasing over years. Not for forecasting, seasonality without detrend, change-point detection, or series shorter than 15 points."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

## When to Use

Use this skill when you need to determine if a time series shows a statistically significant long-term increase or decrease. Trigger keywords: **trend detection**, **long-term trend**, **Mann-Kendall**, **Sen's slope**, **is it increasing**, **is it decreasing**, **statistically significant trend**, **time series trend**.

Typical scenarios:

- Identifying long-term changes in environmental data (temperature, precipitation, air quality).
- Analyzing financial or economic market trends over multi-year horizons.
- Monitoring drift in scientific measurements or sensor readings.
- Detecting gradual shifts in operational metrics (latency, error rate, throughput).

This skill supports both **parametric** (linear regression) and **non-parametric** (Sen's slope with Mann-Kendall test) methods, giving flexibility based on data characteristics and distributional assumptions.

### Do NOT use this skill for

- Data with no temporal component.
- Short-term fluctuations or seasonality without first detrending (use STL decomposition first).
- Forecasting future values (use a dedicated forecasting skill/model).
- Non-stationary processes with abrupt structural breaks not captured by a simple linear trend (use change-point detection first).
- Datasets with fewer than **15** observations (results unreliable below this threshold).
- Time series with significant autocorrelation (apply pre-whitening first).
- Data with missing values (impute or use specialized methods such as Seasonal-Trend decomposition).

## Prerequisites

### Python environment

- Python **3.11+**
- `scipy` (for parametric linear regression)
- `numpy`
- `pandas` **2.0+** (for data loading and preprocessing)
- `pymannkendall` **2.0.0+** (for non-parametric Mann-Kendall / Sen's slope)

Install dependencies:

```powershell
pip install "scipy>=1.11" "numpy>=1.24" "pandas>=2.0" "pymannkendall>=2.0.0"
```

### Data requirements

- A time series with at least **15** observations.
- Evenly spaced time intervals (or documented irregularity).
- No missing values — impute or drop before analysis.
- For autocorrelated series, pre-whiten before applying Mann-Kendall.

### Method notes in this file

This folder ships `SKILL.md` only. Use Step 2 (method table), the p-value table in Step 3a, and the autocorrelation pitfall below. For autocorrelated series: fit an AR(1) (or ARMA as needed), run Mann-Kendall on the residuals, and report that pre-whitening was applied.

## Procedure

### Step 1 — Load and validate data

```python
import pandas as pd
import numpy as np

# Windows path example: r"~\data\precipitation.csv"
filepath = r"~\data\precipitation.csv"

df = pd.read_csv(filepath, parse_dates=["Year"], dtype={"Precipitation": np.float64})

# Hard checks
assert df["Precipitation"].isna().sum() == 0, "Missing values detected — impute before analysis"
assert len(df) >= 15, "Need at least 15 data points for reliable trend results"

values = df["Precipitation"].values
years  = df["Year"].dt.year.values  # numeric time axis
```

### Step 2 — Choose method

| Condition | Recommended method |
|---|---|
| Linear relationship, normal residuals, homoscedastic | Linear regression (`scipy.stats.linregress`) |
| Non-normal, outliers present, environmental data | Mann-Kendall + Sen's slope (`pymannkendall`) |
| Seasonal data (monthly, quarterly) | Seasonal Mann-Kendall (`mk.seasonal_test`) |
| Autocorrelated data | Pre-whiten (AR(1)/ARMA residuals), then Mann-Kendall |

If unsure, use the table above: normal linear residuals → `linregress`; outliers / environmental → Mann-Kendall + Sen's slope; monthly/quarterly → seasonal MK.

### Step 3a — Parametric: Linear Regression

```python
from scipy import stats

slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)

print(f"Slope:      {slope:.4f} units/year")
print(f"95% CI:     [{slope - 1.96*std_err:.4f}, {slope + 1.96*std_err:.4f}]")
print(f"p-value:    {p_value:.4f}")
print(f"R-squared:  {r_value**2:.4f}")
```

**Interpretation:**

| p-value | Interpretation |
|---------|----------------|
| p < 0.001 | Very highly significant trend |
| p < 0.01  | Highly significant trend |
| p < 0.05  | Significant trend |
| p < 0.10  | Marginally significant |
| p >= 0.10 | No significant trend |

Use the p-value table above when reporting significance to stakeholders.

### Step 3b — Non-Parametric: Mann-Kendall + Sen's Slope

```python
import pymannkendall as mk  # version 2.0.0+

result = mk.original_test(values, alpha=0.05)

print(f"Trend:        {result.trend}")        # 'increasing', 'decreasing', or 'no trend'
print(f"Sen's slope:  {result.slope:.4f} units/time_unit")
print(f"p-value:      {result.p:.4f}")
print(f"Intercept:    {result.intercept:.4f}")
print(f"CI (lower):   {result.intercept_ci[0]:.4f}")
print(f"CI (upper):   {result.intercept_ci[1]:.4f}")
```

### Step 3c — Seasonal Mann-Kendall (for monthly/quarterly data)

```python
result = mk.seasonal_test(values, period=12, alpha=0.05)

print(f"Trend:        {result.trend}")
print(f"Sen's slope:  {result.slope:.4f}")
print(f"p-value:      {result.p:.4f}")
```

### Step 4 — Full analysis with error handling

```python
import pandas as pd
import numpy as np
import pymannkendall as mk
from datetime import datetime
import json

def analyze_trend(filepath: str, column: str = "Precipitation", period: int = 12):
    """Analyze trend with comprehensive error handling."""
    try:
        df = pd.read_csv(filepath, parse_dates=["Year"], dtype={column: np.float64})

        if df[column].isna().sum() > 0:
            raise ValueError(f"Missing values detected in '{column}' column — impute before analysis")

        if len(df) < 15:
            print("Warning: Sample size < 15 may reduce result reliability")

        result = mk.original_test(df[column].values, alpha=0.05)

        report = {
            "analysis_date": datetime.now().isoformat(),
            "method": "Mann-Kendall with Sen's Slope",
            "n": len(df),
            "trend": result.trend,
            "slope": round(result.slope, 4),
            "p_value": round(result.p, 6),
            "intercept": round(result.intercept, 4),
            "ci_lower": round(result.intercept_ci[0], 4),
            "ci_upper": round(result.intercept_ci[1], 4),
        }
        return report

    except FileNotFoundError:
        raise FileNotFoundError(f"Data file {filepath} not found")
    except Exception as e:
        raise RuntimeError(f"Analysis failed: {str(e)}")

# Usage on Windows:
# report = analyze_trend(r"~\data\precipitation.csv")
# print(json.dumps(report, indent=2))
```

### Step 5 — Report results

Always include:

1. **Method used** (linear regression vs. Mann-Kendall + Sen's slope).
2. **Slope estimate** with units (e.g., `0.32 mm/year`).
3. **95% confidence interval** for the slope.
4. **p-value** rounded to 4 decimal places.
5. **Sample size** (n).
6. **Trend direction** (increasing / decreasing / no trend).
7. **Caveats** (autocorrelation, seasonality, sample size limitations).

## Pitfalls

- **Fewer than 15 data points** — Results unreliable. The 2026 standard raises the minimum from 10 to 15 observations.
- **Autocorrelation inflates significance** — Mann-Kendall assumes independence. If autocorrelation is present, pre-whiten the series first (AR(1) or ARMA residuals, then MK).
- **Missing values silently dropped** — Always check `df[column].isna().sum()` before analysis. Do not let pandas silently drop rows.
- **Confusing Sen's slope with regression slope** — Sen's slope is the median of pairwise slopes; it is robust to outliers but not directly comparable to OLS slope.
- **Using `mk.original_test` on seasonal data** — Use `mk.seasonal_test()` with the correct `period` parameter instead.
- **pymannkendall version < 2.0.0** — The `alpha` parameter and enhanced tests require version 2.0.0+. Verify with `pip show pymannkendall`.
- **Not reporting confidence intervals** — Always report CIs alongside point estimates; a slope without a CI is incomplete.
- **Rounding p-values too aggressively** — Round to at least 4 decimal places. Report `p < 0.001` rather than `p = 0.000`.
- **Passing lists instead of numpy arrays** — Use `np.array()` or `.values` for performance and correctness.
- **Ignoring structural breaks** — A single abrupt change can create an apparent trend. Run change-point detection first if breaks are suspected.

## Verification

Run these checks after implementing the analysis:

```powershell
# Confirm package versions
python -c "import scipy; print('scipy', scipy.__version__)"
python -c "import pymannkendall as mk; print('pymannkendall', mk.__version__)"
python -c "import pandas; print('pandas', pandas.__version__)"
```

```python
# Verify linear regression against a known dataset
import numpy as np
from scipy import stats

years  = np.arange(2000, 2020)
values = np.arange(2000, 2020) * 0.5 + np.random.normal(0, 0.1, 20)
slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)

assert p_value < 0.001, f"Expected highly significant trend, got p={p_value}"
assert abs(slope - 0.5) < 0.05, f"Slope should be ~0.5, got {slope}"
print("Linear regression verification: PASS")
```

```python
# Verify Mann-Kendall on increasing, decreasing, and flat series
import numpy as np
import pymannkendall as mk

inc = np.arange(50, dtype=float) + np.random.normal(0, 0.5, 50)
dec = -np.arange(50, dtype=float) + np.random.normal(0, 0.5, 50)
flat = np.random.normal(10, 1, 50)

assert mk.original_test(inc).trend == "increasing"
assert mk.original_test(dec).trend == "decreasing"
assert mk.original_test(flat).trend == "no trend"
print("Mann-Kendall verification: PASS")
```

Checklist:

- [ ] `scipy.stats.linregress` produces correct results against known datasets.
- [ ] `pymannkendall 2.0.0+` correctly classifies increasing, decreasing, and no-trend scenarios.
- [ ] Confidence intervals are calculated and reported for both methods.
- [ ] Edge cases tested: small datasets (< 15), missing values, outliers.
- [ ] Datetime objects handled correctly in trend analysis.
- [ ] Seasonal decomposition works when preprocessing data.
- [ ] Both numpy arrays and pandas Series inputs accepted.
- [ ] Error handling covers `FileNotFoundError`, missing values, and insufficient sample size.

## Related Skills

- **Time Series Forecasting** — Predicting future values from historical patterns (Prophet, NeuralProphet).
- **Anomaly Detection** — Identifying unusual points deviating from expected trend (Isolation Forest, LSTM detectors).
- **Data Visualization** — Plotting time series and trend lines (Plotly, Altair for interactive charts).
- **Change Point Detection** — Identifying structural breaks (ruptures, Bayesian methods).
- **Spatial-Temporal Analysis** — Analyzing trends across both space and time dimensions.
