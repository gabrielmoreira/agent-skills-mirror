# data-analysis

Use this skill when asked to explore, analyse, or visualise any dataset, CSV, table, or collection of numbers.

---

## Analysis Workflow

Always follow this sequence:

1. **Inventory** - How many rows? How many columns? What are the column names and types?
2. **Quality check** - Missing values, duplicates, outliers, type mismatches.
3. **Descriptive stats** - Mean, median, std, min, max, percentiles for numeric columns.
4. **Distribution** - Are numeric columns skewed? Are categorical columns imbalanced?
5. **Relationships** - Correlations, group comparisons, time trends if a date column exists.
6. **Key findings** - The 3-5 most actionable insights from the above.

Never skip steps. Never jump to "Key findings" without the groundwork.

---

## Output Format

```
## Dataset Overview
Rows, columns, source, date range if applicable.

## Data Quality
Missing values per column, duplicates found, anomalies flagged.

## Descriptive Statistics
Table of numeric column stats. Categorical column value counts (top 5).

## Key Patterns
Bullet points - one insight per bullet, quantified.
Bad:  "Sales seem higher in Q4"
Good: "Q4 sales average 34% higher than Q1-Q3 combined (mean: $2.1M vs $1.57M)"

## Recommendations
What to investigate further, or what action the data supports.
```

---

## Rules

- Every insight must include a number. "Higher" without a figure is not an insight.
- Flag data quality issues before drawing conclusions - dirty data produces wrong insights.
- Distinguish correlation from causation explicitly when it matters.
- If asked to plot or chart, use the scripts in `scripts/` - do not write raw matplotlib from scratch.
- If a column looks like a date but is typed as a string, note it and parse it before time-series analysis.

---

## Scripts

Pre-built analysis scripts live in `scripts/`. Read them before writing any analysis code.

| Script | Purpose |
|---|---|
| `scripts/profile.py` | Full dataset profile: types, nulls, stats, top values |
| `scripts/correlations.py` | Pearson + Spearman correlation matrix with heatmap |
| `scripts/time_series.py` | Date-aware trend analysis, resampling, rolling averages |

Usage: copy the relevant script, adapt the `INPUT_FILE` and column name variables at the top, then run.
