# Data Analysis Orchestration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Data yields insights faster when explored in parallel.    │
│   Multiple dimensions, simultaneous analysis, clear story.  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Load when**: Exploratory data analysis, data quality, report generation, ETL pipelines, statistical analysis
> **Common patterns**: Multi-Dimensional Exploration, Comprehensive Quality Audit, Hypothesis Testing

## Table of Contents

1. [Exploratory Data Analysis](#exploratory-data-analysis)
2. [Data Quality](#data-quality)
3. [Report Generation](#report-generation)
4. [ETL Pipelines](#etl-pipelines)
5. [Statistical Analysis](#statistical-analysis)

---

## Exploratory Data Analysis

### Pattern: Multi-Dimensional Exploration

```
User Request: "Analyze this dataset"

Phase 1: FAN-OUT (Parallel initial exploration)
├─ Agent A: Schema analysis (columns, types, constraints)
├─ Agent B: Statistical summary (distributions, outliers)
├─ Agent C: Missing data analysis
├─ Agent D: Cardinality and uniqueness analysis
└─ Agent E: Sample data examination

Phase 2: REDUCE
└─ General-purpose agent: Synthesize initial findings

Phase 3: FAN-OUT (Deep dive based on findings)
├─ Agent A: Correlation analysis
├─ Agent B: Time series patterns (if applicable)
└─ Agent C: Categorical relationship analysis

Phase 4: REDUCE
└─ General-purpose agent: Complete EDA report
```

### Pattern: Question-Driven Analysis

```
User Request: "Why are sales declining?"

Phase 1: EXPLORE
└─ Explore agent: Understand available data sources

Phase 2: FAN-OUT (Parallel hypothesis investigation)
├─ Agent A: Analyze sales by region
├─ Agent B: Analyze sales by product
├─ Agent C: Analyze sales by customer segment
├─ Agent D: Analyze external factors (seasonality, competition)
└─ Agent E: Analyze marketing/promotion effectiveness

Phase 3: REDUCE
└─ General-purpose agent: Identify key drivers, recommendations
```

---

## Data Quality

### Pattern: Comprehensive Quality Audit

```
User Request: "Check data quality for the customer table"

Phase 1: FAN-OUT (Parallel quality dimensions)
├─ Agent A: Completeness (null rates, missing values)
├─ Agent B: Accuracy (format validation, range checks)
├─ Agent C: Consistency (cross-field validation)
├─ Agent D: Timeliness (freshness, update patterns)
├─ Agent E: Uniqueness (duplicates, key integrity)
└─ Agent F: Validity (business rule compliance)

Phase 2: REDUCE
└─ General-purpose agent: Quality scorecard with issues

Phase 3: FAN-OUT (Remediation)
├─ Agent A: Fix completeness issues
├─ Agent B: Fix accuracy issues
└─ Agent C: Fix consistency issues
```

### Pattern: Anomaly Detection

```
Phase 1: FAN-OUT
├─ Agent A: Statistical outlier detection
├─ Agent B: Business rule violations
├─ Agent C: Pattern anomalies (sudden changes)
└─ Agent D: Referential integrity issues

Phase 2: REDUCE
└─ General-purpose agent: Anomaly report with severity
```

---

## Report Generation

### Pattern: Multi-Section Report

```
User Request: "Generate monthly business report"

Phase 1: FAN-OUT (Parallel section generation)
├─ Agent A: Executive summary section
├─ Agent B: Sales performance section
├─ Agent C: Customer metrics section
├─ Agent D: Product analytics section
├─ Agent E: Financial summary section
└─ Agent F: Operational metrics section

Phase 2: REDUCE
└─ General-purpose agent: Compile sections, add insights

Phase 3: PIPELINE
└─ General-purpose agent: Format, add visualizations
```

---

## ETL Pipelines

### Pattern: ETL Development

```
User Request: "Create ETL pipeline for user events"

Phase 1: EXPLORE
└─ Explore agent: Understand source schema, target requirements

Phase 2: PLAN
└─ Plan agent: Design ETL architecture

Phase 3: FAN-OUT (Parallel component development)
├─ Agent A: Extract logic (source connectors)
├─ Agent B: Transform logic (cleaning, mapping)
├─ Agent C: Load logic (target insertion)
└─ Agent D: Error handling and logging

Phase 4: PIPELINE
├─ General-purpose agent: Wire components
└─ Background agent: Test with sample data
```

### Pattern: ETL Debugging

```
User Request: "ETL job is failing"

Phase 1: FAN-OUT (Parallel diagnosis)
├─ Explore agent: Check job logs
├─ Explore agent: Check source data quality
├─ Explore agent: Check target schema compatibility
└─ Explore agent: Check resource utilization

Phase 2: REDUCE
└─ General-purpose agent: Root cause identification

Phase 3: PIPELINE
├─ General-purpose agent: Implement fix
└─ Background agent: Verify fix with test run
```

---

## Statistical Analysis

### Pattern: Hypothesis Testing

```
User Request: "Did the new feature improve conversion?"

Phase 1: EXPLORE
└─ Explore agent: Gather pre and post data

Phase 2: FAN-OUT
├─ Agent A: Descriptive statistics (both groups)
├─ Agent B: Distribution analysis
└─ Agent C: Confounding variable check

Phase 3: PIPELINE
├─ General-purpose agent: Select appropriate test
├─ General-purpose agent: Run statistical test
└─ General-purpose agent: Interpret results

Phase 4: REDUCE
└─ General-purpose agent: Conclusion with confidence
```

### Pattern: Predictive Modeling

```
Phase 1: FAN-OUT (Data preparation)
├─ Agent A: Feature engineering
├─ Agent B: Data cleaning
└─ Agent C: Train/test split

Phase 2: SPECULATIVE (Model selection)
├─ Agent A: Train model type 1
├─ Agent B: Train model type 2
└─ Agent C: Train model type 3

Phase 3: REDUCE
└─ General-purpose agent: Compare models, select best
```

---

## Task Management for Data Analysis

Structure data analysis with parallel exploration:

```bash
# Create analysis tasks
npx cc-mirror tasks create --subject "Understand data sources" --description "Schema, types, relationships..."
npx cc-mirror tasks create --subject "Explore distributions" --description "Statistical summaries, outliers..."
npx cc-mirror tasks create --subject "Analyze missing data" --description "Null patterns, imputation needs..."
npx cc-mirror tasks create --subject "Check data quality" --description "Validation, consistency..."
npx cc-mirror tasks create --subject "Synthesize findings" --description "Aggregate insights, recommendations..."
npx cc-mirror tasks create --subject "Generate report" --description "Visualizations, documentation..."

# Parallel exploration after understanding
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 1
npx cc-mirror tasks update 4 --add-blocked-by 1
npx cc-mirror tasks update 5 --add-blocked-by 2,3,4
npx cc-mirror tasks update 6 --add-blocked-by 5
```

```python
# Spawn parallel analysis agents (haiku for data exploration)
Task(subagent_type="Explore", prompt="Task 2: Explore distributions...",
     model="haiku", run_in_background=True)
Task(subagent_type="Explore", prompt="Task 3: Analyze missing data...",
     model="haiku", run_in_background=True)
Task(subagent_type="Explore", prompt="Task 4: Check data quality...",
     model="haiku", run_in_background=True)
```

## Best Practices

1. **Parallelize exploration** across dimensions
2. **Validate data quality** before analysis
3. **Background long queries** to maintain responsiveness
4. **Document assumptions** in reports
5. **Include confidence levels** in statistical conclusions

---

```
─── ◈ Data Analysis ─────────────────────
```
