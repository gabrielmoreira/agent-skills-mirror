# DAX Optimization Patterns

## Table of Contents

- [Understanding DAX Engine Architecture](#understanding-dax-engine-architecture)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
- [Measure Optimization Techniques](#measure-optimization-techniques)
- [Filter Context Optimization](#filter-context-optimization)
- [Time Intelligence Optimization](#time-intelligence-optimization)
- [Relationship and Schema Patterns](#relationship-and-schema-patterns)
- [Profiling Workflow with DAX Studio](#profiling-workflow-with-dax-studio)

---

## Understanding DAX Engine Architecture

The DAX engine has two components that process queries:

**Formula Engine (FE)**: Single-threaded, handles complex DAX logic (iterations, row context, CALCULATE modifiers). High FE time means your DAX logic is complex.

**Storage Engine (SE)**: Multi-threaded, scans the VertiPaq columnar store or issues DirectQuery SQL. High SE time means data retrieval is expensive.

**Optimization goal**: Maximize work done by SE (parallel, fast scans) and minimize FE work (single-threaded, slow iterations).

**Key metrics from DAX Studio Server Timings:**

| Metric | Healthy | Needs Attention |
|--------|---------|-----------------|
| Total query time | < 500ms | > 1000ms |
| SE queries count | < 20 | > 50 |
| SE cache hit ratio | > 80% | < 50% |
| FE as % of total | < 30% | > 50% |

---

## Anti-Pattern Catalog

### AP-01: Iterators Over Large Tables

**Problem**: Using SUMX, AVERAGEX, MAXX, COUNTX over millions of rows with row-by-row calculation.

**Slow:**
```dax
Total Revenue =
SUMX(
    Sales,
    Sales[Quantity] * RELATED(Products[UnitPrice])
)
```

**Fast:**
```dax
// Pre-compute in source or use a calculated column if truly needed
Total Revenue =
SUMX(
    Sales,
    Sales[LineTotal]  // Pre-calculated column in the source
)

// Or if the relationship allows:
Total Revenue = [Total Quantity] * [Avg Unit Price]  // Simplified aggregation
```

**Why**: Each RELATED() call inside SUMX forces the FE to resolve the relationship row-by-row. Pre-computing the value avoids this overhead.

---

### AP-02: Nested CALCULATE with Complex Filters

**Problem**: Multiple nested CALCULATE calls with overlapping or conflicting filters.

**Slow:**
```dax
Complex Measure =
CALCULATE(
    CALCULATE(
        SUM(Sales[Amount]),
        FILTER(ALL(Sales), Sales[Status] = "Completed")
    ),
    FILTER(ALL(Date), Date[Year] = 2024)
)
```

**Fast:**
```dax
Complex Measure =
CALCULATE(
    SUM(Sales[Amount]),
    Sales[Status] = "Completed",
    Date[Year] = 2024
)
```

**Why**: Simple column predicates in CALCULATE are optimized by the engine into efficient SE queries. FILTER(ALL(...)) forces FE iteration.

---

### AP-03: FILTER with Table Expressions

**Problem**: Using FILTER() on entire tables instead of column predicates.

**Slow:**
```dax
High Value Sales =
CALCULATE(
    SUM(Sales[Amount]),
    FILTER(Sales, Sales[Amount] > 1000)
)
```

**Fast:**
```dax
High Value Sales =
CALCULATE(
    SUM(Sales[Amount]),
    KEEPFILTERS(Sales[Amount] > 1000)
)
```

**Why**: FILTER(Sales, ...) materializes the entire Sales table in FE memory. Column predicates push the filter directly to SE.

---

### AP-04: Calculated Columns Instead of Measures

**Problem**: Using calculated columns for values that should be measures.

**Issue:** Calculated columns are computed at refresh time and stored in memory, increasing model size. They cannot benefit from query-time filter context.

**Replace calculated columns with measures when:**
- The calculation depends on filter context (slicers, cross-filters)
- The column is used only in visuals, not in relationships or row-level security
- The column duplicates aggregatable data

---

### AP-05: DISTINCTCOUNT on High-Cardinality Columns

**Problem**: DISTINCTCOUNT on columns with millions of unique values.

**Mitigation:**
- Add a pre-computed distinct count column in the source
- Use approximate distinct count if precision is not critical
- Reduce cardinality by binning or grouping

---

### AP-06: IF with Expensive Branches

**Problem**: IF() evaluates both branches before choosing one.

**Slow:**
```dax
KPI =
IF(
    [Total Sales] > 1000000,
    [Complex Calculation A],
    [Complex Calculation B]
)
```

**Fast:**
```dax
KPI =
VAR _Sales = [Total Sales]
VAR _Result =
    IF(
        _Sales > 1000000,
        [Complex Calculation A],
        [Complex Calculation B]
    )
RETURN _Result
```

**Even better**: Use SWITCH(TRUE(), ...) for multi-branch logic, and ensure expensive branches are calculated only when needed by using variables to cache intermediate results.

---

## Measure Optimization Techniques

### Use Variables (VAR/RETURN)

Variables are evaluated once and cached. Use them to avoid redundant calculations.

```dax
Profit Margin =
VAR _Revenue = SUM(Sales[Revenue])
VAR _Cost = SUM(Sales[Cost])
RETURN
    DIVIDE(_Revenue - _Cost, _Revenue)
```

### Prefer DIVIDE over Division Operator

```dax
// Safe (handles divide by zero)
Ratio = DIVIDE([Numerator], [Denominator], 0)

// Unsafe (can error)
Ratio = [Numerator] / [Denominator]
```

### Avoid COUNTROWS(FILTER(...)) When Possible

```dax
// Slow
Active Customers = COUNTROWS(FILTER(Customers, Customers[Status] = "Active"))

// Fast
Active Customers = CALCULATE(COUNTROWS(Customers), Customers[Status] = "Active")
```

---

## Filter Context Optimization

### Minimize Use of ALL() and REMOVEFILTERS()

Every ALL() call resets filter context, forcing the engine to recalculate without cache benefits. Use ALLEXCEPT() or ALLSELECTED() when you only need to remove specific filters.

### Avoid Bi-Directional Cross-Filtering

Bi-directional relationships (double arrow) cause exponential filter propagation. Use single-direction relationships and CROSSFILTER() in specific measures when needed.

### Use TREATAS for Virtual Relationships

When you need to apply filters across unrelated tables without physical relationships:

```dax
Sales in Selected Region =
CALCULATE(
    SUM(Sales[Amount]),
    TREATAS(VALUES(Geography[Region]), Sales[Region])
)
```

---

## Time Intelligence Optimization

### Use a Proper Date Table

- Mark it as a Date Table in the model
- Ensure it has contiguous dates (no gaps)
- Include pre-computed fiscal periods if needed

### Avoid Nested Time Intelligence

```dax
// Slow: nested time intelligence
YoY Growth =
DIVIDE(
    [Total Sales] - CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Date[Date])),
    CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Date[Date]))
)

// Fast: use variables
YoY Growth =
VAR _CurrentSales = [Total Sales]
VAR _PriorYearSales = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Date[Date]))
RETURN
    DIVIDE(_CurrentSales - _PriorYearSales, _PriorYearSales)
```

### Consider Calendar-Based Time Intelligence (Preview)

For DirectQuery models, calendar-based time intelligence can execute far more efficiently than traditional DAX time intelligence functions by pushing calculations to the source.

---

## Relationship and Schema Patterns

### Star Schema Design

- Fact tables contain numeric measures and foreign keys only
- Dimension tables contain descriptive attributes
- Relationships flow from dimension to fact (one-to-many)
- Avoid snowflake schemas where possible (flatten dimensions)

### Reduce Column Cardinality

| Technique | When to Use |
|-----------|-------------|
| Remove unnecessary columns | Always (first step) |
| Round decimals | When precision beyond 2 decimal places is not needed |
| Bin continuous values | When exact values are not needed for analysis |
| Group rare categories into "Other" | When long tail adds no analytical value |
| Hash or remove long text columns | When text is not used in visuals or filters |

### Optimize Data Types

| From | To | Savings |
|------|----|---------|
| Text dates ("2024-01-15") | Date/DateTime | Major (enables VertiPaq compression) |
| Decimal (15,10) | Decimal (15,2) | Moderate |
| Whole Number (Int64) | Whole Number (Int32) | Minor |
| Large text columns | Remove or shorten | Major (text compresses poorly) |

---

## Profiling Workflow with DAX Studio

### Step 1: Connect to the Model

- Open DAX Studio
- Connect to Power BI Desktop (local) or the XMLA endpoint (service)

### Step 2: Enable Diagnostics

- Advanced > Server Timings (check)
- Advanced > Query Plan (check for advanced analysis)

### Step 3: Run the Query

Paste the DAX query from Performance Analyzer and execute.

### Step 4: Analyze Results

**Server Timings tab:**
- Total: End-to-end duration
- SE (Storage Engine): Time scanning data
- FE (Formula Engine): Time computing DAX logic
- SE Queries: Number of VertiPaq scans

**Action matrix:**

| Pattern | Meaning | Fix |
|---------|---------|-----|
| High SE, Low FE | Large data scans | Reduce model size, add aggregations |
| Low SE, High FE | Complex DAX logic | Simplify measures, use variables |
| Many SE queries | Excessive row-by-row | Remove iterators, use bulk aggregation |
| High SE cache misses | Unique filter combinations | Reduce slicer cardinality |
