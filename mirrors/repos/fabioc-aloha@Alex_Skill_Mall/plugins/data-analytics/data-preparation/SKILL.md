---
type: skill
lifecycle: evolving
inheritance: inheritable
name: data-preparation
description: "Data cleaning, profiling, transformation, and quality gates -- prepares raw data for visualization and analysis"
tier: standard
applyTo: "**/*data*,**/*clean*,**/*transform*,**/*prep*,**/*pivot*,**/*aggregate*"
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Data Preparation

Prepare raw data for visualization. This module fires after ingestion and before
chart selection. It does not analyze or visualize; it makes data ready for those
steps.

## When to Use

- Raw data has nulls, duplicates, or inconsistent types
- Data needs aggregation, pivoting, or reshaping for the target visual
- The brief specifies quality concerns
- You are unsure whether the data is visualization-ready

## When to Skip

- Data is already clean, typed, and shaped for the target visuals
- The dataset is small and you can verify quality by inspection
- The brief says "data is analysis-ready"

State why you are skipping. Silent skips hide data problems.

## Step 1: Profile

Before cleaning, understand what you have. Run these checks on every column:

| Check | What to look for |
| --- | --- |
| **Row count** | Is it what you expected? Zero rows = ingestion failed |
| **Column types** | Dates stored as strings? Numbers as text? |
| **Null count** | Which columns have nulls? What percentage? |
| **Unique count** | Cardinality: is this a dimension (low) or measure (high)? |
| **Min / Max / Mean** | For numeric columns: are ranges plausible? |
| **Sample values** | Eyeball 5 rows. Do they look right? |

Report the profile as a table before proceeding. The user (or orchestrator)
needs to see it to decide what cleaning is needed.

## Step 2: Clean

Apply fixes in this order. Each fix is a decision; state what you chose and why.

### 2a. Duplicates

| Signal | Action |
| --- | --- |
| Exact duplicate rows | Remove. Log count removed. |
| Near-duplicates (same key, different values) | Flag for user decision. Do not silently drop. |

### 2b. Null handling

| Strategy | When to use |
| --- | --- |
| **Drop row** | Null is in a must-have column and row is < 5% of data |
| **Fill with default** | Column has an obvious default (e.g., 0 for optional count) |
| **Fill with median/mode** | Numeric column, nulls are < 10%, distribution is stable |
| **Leave as-is** | The visual can handle nulls (e.g., gap in a line chart) |

Never fill nulls silently. State the strategy and count affected.

### 2c. Type coercion

| Problem | Fix |
| --- | --- |
| Date as string | Parse to date. State the format detected. |
| Number as string | Convert. Check for non-numeric values first. |
| Boolean as string | Map "yes/no", "true/false", "1/0" to boolean. |
| Mixed types in one column | Flag for user. This usually means the schema is wrong. |

### 2d. Outliers

| Context | Action |
| --- | --- |
| Outlier is a data error (negative revenue, future date) | Remove or fix. Log. |
| Outlier is real but extreme | Keep. Note it for the visual (it may need axis adjustment). |
| Unsure | Flag for user. Do not remove real data silently. |

## Step 3: Transform

Reshape the data to match what the target visual needs.

### Aggregation

Aggregate when the raw data is too granular for the visual.

| Visual need | Aggregation |
| --- | --- |
| Monthly trend | Group by month, sum or average the measure |
| Category comparison | Group by category, sum the measure |
| Proportion | Group by category, compute share of total |
| Distribution | Bin the values, count per bin |

Always state the grain change: "Aggregated from daily to monthly by summing revenue."

### Pivot / Unpivot

| Need | Direction |
| --- | --- |
| One column per category (wide format) | Pivot |
| One row per observation (long format) | Unpivot |

Most visualizations prefer long format. Pivot only when the delivery module
explicitly needs wide format (e.g., side-by-side bar chart in ASCII).

### Computed columns

Add columns only when the brief requires a metric that is not in the raw data:

- **Margin**: revenue - cost
- **Margin %**: (revenue - cost) / revenue
- **Growth**: (current - previous) / previous
- **Share**: value / total

Name computed columns clearly. Do not overwrite source columns.

## Step 4: Quality Gates

Before passing data downstream, assert:

| Gate | Assertion | Fail action |
| --- | --- | --- |
| **No nulls in key columns** | Dimensions and must-have measures are null-free | Push back: data is not ready |
| **Row count is plausible** | Within expected range (not 0, not 10x expected) | Push back: ingestion may have failed |
| **Types are correct** | Every column has the expected type after coercion | Push back: type fix needed |
| **Grain is correct** | One row per expected unit (e.g., one per month per region) | Push back: dedup or aggregate needed |

If any gate fails, push back to the orchestrator with a specific message:
"Quality gate failed: 12 nulls in revenue column. Recommend: drop rows (< 1% of data)."

## Output

Pass to the next module:

- The cleaned, transformed dataset (or a reference to it)
- A one-paragraph data profile summary
- A list of any decisions made (nulls filled, outliers flagged, columns added)

## Relationship to Mall Plugins

| Mall plugin | This module's role |
| --- | --- |
| `data-analysis` | Runs after this module; assumes clean data |
| `data-quality-monitoring` | Monitors ongoing quality; this module does initial prep |
| `data-visualization` | Designs the visual; needs correctly shaped data from this module |

## Anti-Patterns

| Do not | Do instead |
| --- | --- |
| Clean silently | Log every change with count and reason |
| Remove outliers without context | Keep real data; flag for user if unsure |
| Aggregate without stating the grain change | "Aggregated from X to Y by Z" |
| Add computed columns the brief did not ask for | Only add what the questions require |
| Skip profiling because "the data looks fine" | Profile always; it costs one table and catches surprises |
