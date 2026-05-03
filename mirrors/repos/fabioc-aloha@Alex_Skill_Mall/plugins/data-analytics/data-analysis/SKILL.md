---
type: skill
lifecycle: stable
inheritance: inheritable
name: data-analysis
description: Exploratory data analysis patterns -- profiling, distributions, correlations, segmentation, anomaly detection, and translating statistics into narrative insights
tier: standard
applyTo: '**/*data*,**/*analysis*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Data Analysis


| Property     | Value                                                          |
| ------------ | -------------------------------------------------------------- |
| **Domain**   | Data Analytics                                                 |
| **Category** | Analysis & Insight Extraction                                  |
| **Components** | SKILL.md + data-analysis.instructions.md + analyze.prompt.md   |
| **Depends**  | data-visualization (chart output), data-ingest.cjs (ingestion) |

## Overview

Turn raw data into actionable insight statements. This skill covers the full EDA pipeline: profiling the dataset, exploring distributions, finding correlations, detecting anomalies, and -- critically -- translating statistical findings into business-language narratives tagged with story intents for downstream visualization.

The cardinal rule: **statistics are not insights**. "Mean revenue is $4.2M" is a statistic. "Revenue grew 34% YoY but growth is decelerating -- Q3 peak was 8% vs. 22% last year" is an insight.

## Module 1: Data Profiling

First pass on any dataset. Compute before exploring.

| Metric             | What It Tells You                        | Red Flag                              |
| ------------------ | ---------------------------------------- | ------------------------------------- |
| Row count          | Dataset scale                            | <100 rows limits statistical power    |
| Column count       | Dimensionality                           | >50 columns suggests feature bloat    |
| Null percentage    | Data completeness                        | >20% nulls in key column = unreliable |
| Unique count       | Cardinality                              | Unique count = row count → likely ID  |
| Type inference     | String/number/date/boolean               | Mixed types in same column = dirty    |
| Memory estimate    | Processing feasibility                   | >500MB warns for browser context      |
| Duplicate rows     | Data quality                             | >1% duplicates needs dedup decision   |

### Profiling Output Template

```
Dataset: {name} ({rowCount} rows x {colCount} columns)
Source:  {source} | Format: {format} | Encoding: {encoding}

Column Summary:
  {name}: {type} | {nullPct}% null | {uniqueCount} unique | min={min} max={max} mean={mean}
  ...

Quality Score: {score}/100
  - Completeness: {completeness}% (columns with <5% nulls)
  - Consistency: {consistency}% (columns with single type)
  - Uniqueness: {uniqueness}% (no unexpected duplicates)

Warnings:
  - Column "X" has 23% nulls -- consider imputation or exclusion
  - Column "Y" has mixed types (78% number, 22% string) -- needs cleaning
```

## Module 2: Descriptive Statistics

What to compute first for every numeric column.

| Statistic        | When It Matters                                    |
| ---------------- | -------------------------------------------------- |
| Mean vs. Median  | If mean >> median, right-skewed (outliers pull up) |
| Standard Dev     | Spread -- is the data tight or dispersed?          |
| Min / Max        | Range -- any impossible values?                    |
| Percentiles      | P25, P50, P75 -- where does the bulk sit?          |
| Skewness         | >1 or <-1 suggests non-normal distribution         |
| Kurtosis         | >3 = heavy tails (more outliers than expected)     |

### Rule of Thumb: Mean vs. Median

- If `|mean - median| / median > 0.1` (10%), report median as the "typical" value
- Always report both -- the gap itself is an insight

## Module 3: Distribution Analysis

| Shape        | What It Suggests                          | Story Intent     |
| ------------ | ----------------------------------------- | ---------------- |
| Normal       | Stable process, predictable               | Distribution     |
| Right-skewed | Many small values, few large (income)     | Deviation        |
| Left-skewed  | Most values high, some low (test scores)  | Deviation        |
| Bimodal      | Two populations mixed together            | Compare (groups) |
| Uniform      | No pattern -- random or categorical codes | None (check)     |
| Power law    | Few items dominate (Pareto, web traffic)  | Part-to-Whole    |

### Normality Quick Check

1. Compare mean to median (>10% gap = non-normal)
2. Check skewness (|skew| > 1 = non-normal)
3. If important: Shapiro-Wilk test (n < 5000) or Anderson-Darling

## Module 4: Correlation & Relationship

| Strength | `|r|` Range | Interpretation              |
| -------- | ----------- | --------------------------- |
| Strong   | 0.7 -- 1.0  | Likely meaningful           |
| Moderate | 0.4 -- 0.7  | Worth investigating         |
| Weak     | 0.1 -- 0.4  | Unlikely actionable alone   |
| None     | < 0.1       | No linear relationship      |

### Simpson's Paradox Awareness

Always check: does the correlation reverse when you split by a categorical variable?

```
Overall: Ad spend positively correlates with sales (+0.6)
By region: In 3 of 4 regions, correlation is NEGATIVE
Cause: High-spend region has higher baseline sales (confound)
```

**Rule**: If a strong correlation exists, segment by the top 2-3 categorical variables and re-check.

## Module 5: Segmentation

Group-by patterns for discovering sub-populations.

| Technique          | When to Use                          | Output            |
| ------------------ | ------------------------------------ | ----------------- |
| Group-by aggregate | Categorical × numeric                | Segment averages  |
| Percentile buckets | Continuous variable, create tiers    | Low/Mid/High      |
| RFM analysis       | Customer behavior (recency, freq, $) | Customer segments |
| Cohort analysis    | Time-based grouping (signup month)   | Retention curves  |
| Cross-tabulation   | Two categorical variables            | Contingency table |

### "So What?" for Segments

For each segment found, answer: "If I could only act on ONE segment, which one and why?"

## Module 6: Time-Series Decomposition

| Component    | What It Is                            | Detection                       |
| ------------ | ------------------------------------- | ------------------------------- |
| Trend        | Long-term direction                   | Rolling average (window = period) |
| Seasonality  | Repeating pattern at fixed intervals  | Autocorrelation at lag = period |
| Residual     | What's left (noise + anomalies)       | Original - trend - seasonality  |

### Rolling Average Windows

| Data Frequency | Window  |
| -------------- | ------- |
| Daily          | 7 or 30 |
| Weekly         | 4 or 13 |
| Monthly        | 3 or 12 |
| Quarterly      | 4       |

## Module 7: Anomaly Detection

| Method     | Best For                   | Threshold              |
| ---------- | -------------------------- | ---------------------- |
| Z-score    | Normal-ish distributions   | |z| > 3               |
| IQR fence  | Skewed distributions       | < Q1-1.5×IQR or > Q3+1.5×IQR |
| Isolation   | Multivariate outliers      | Score > 0.7 (heuristic) |
| Visual      | Any -- always plot first   | Inspect scatter/box    |

### Anomaly Protocol

1. Detect and **flag** -- never auto-remove
2. Investigate: is it a data error, a real outlier, or a different population?
3. Document the decision: kept (real), removed (error), or separated (sub-population)

## Module 8: "So What?" Translation (DIKW)

The most important module. Convert statistics into business language.

| Level           | Example (Bad)                    | Example (Good)                                                           |
| --------------- | -------------------------------- | ------------------------------------------------------------------------ |
| **Data**        | "Column revenue has 5000 values" | (Don't report raw data)                                                  |
| **Information** | "Mean revenue is $4.2M"          | "Average quarterly revenue is $4.2M across 8 quarters"                   |
| **Knowledge**   | "Revenue has a positive trend"   | "Revenue grew 34% YoY but growth rate decelerated from 22% to 8%"       |
| **Wisdom**      | (Requires domain context)        | "Growth is decelerating -- if Q3 seasonal effect weakens, plan for flat" |

### Insight Statement Template

```
[WHAT]: {metric} is {value/behavior}
[SO WHAT]: This means {business implication}
[NOW WHAT]: Consider {action or follow-up question}
[STORY INTENT]: {compare|trend|deviation|distribution|relationship|part-to-whole|flow|hierarchy|spatial}
[CHART]: {recommended chart type} because {rationale}
```

### Example Insight Statements

```
[WHAT]: California's population (39M) is 5x the median state (7.5M)
[SO WHAT]: Resource allocation models using state averages will dramatically under-serve CA
[NOW WHAT]: Segment by population tier, not just state count
[STORY INTENT]: Compare
[CHART]: Horizontal bar (sorted descending) because ranking 50 items with long labels

[WHAT]: Support ticket resolution time has a bimodal distribution (peaks at 2h and 48h)
[SO WHAT]: Two distinct processes exist -- quick fixes and escalated investigations
[NOW WHAT]: Separate the two populations before setting SLA targets
[STORY INTENT]: Distribution
[CHART]: Histogram with two highlighted peaks, or violin plot for visual impact
```

## Module 9: Hypothesis Framework

Structured approach to moving from observation to testable claim.

| Step         | Action                                             |
| ------------ | -------------------------------------------------- |
| Observe      | Note a pattern in the data                         |
| Hypothesize  | State a testable claim ("X causes Y because Z")   |
| Test         | Check against data (filter, segment, correlate)    |
| Conclude     | Supported, refuted, or inconclusive                |
| Narrate      | Write the finding as an insight statement          |

### Anti-Patterns

| Anti-Pattern             | Problem                                     | Fix                                         |
| ------------------------ | ------------------------------------------- | ------------------------------------------- |
| Reporting stats only     | No business meaning                         | Always add "so what?"                       |
| Correlation = causation  | Misleading conclusions                      | Check for confounders, state "correlates"   |
| Ignoring base rates      | Percentages without context                 | Always report denominator                   |
| Survivorship bias        | Only analyzing what's visible               | Ask "what's missing from this data?"        |
| Over-aggregation         | Hiding variation with averages              | Show distribution, not just mean            |
| Premature optimization   | Jumping to solutions before understanding   | Complete the EDA before recommending action |
