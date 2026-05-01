# DirectQuery Performance Tuning

## Table of Contents

- [When DirectQuery Makes Sense](#when-directquery-makes-sense)
- [Performance Diagnostics](#performance-diagnostics)
- [Source-Side Optimization](#source-side-optimization)
- [Model-Side Optimization](#model-side-optimization)
- [Composite Model Strategy](#composite-model-strategy)
- [Fabric Lakehouse and Warehouse Specifics](#fabric-lakehouse-and-warehouse-specifics)

---

## When DirectQuery Makes Sense

Use DirectQuery when:
- Data must be real-time or near-real-time
- Dataset exceeds Import model size limits
- Source has strict data residency requirements
- Frequent changes make scheduled refresh impractical

Avoid DirectQuery when:
- Complex DAX calculations are required (FE-heavy measures)
- Source database cannot handle concurrent query load
- Network latency to the source is high (> 50ms round trip)
- Users expect sub-second interactivity

---

## Performance Diagnostics

### Step 1: Performance Analyzer in Desktop

1. View > Performance Analyzer > Start recording
2. Interact with slow visuals
3. Expand results to see DAX query and Direct Query timings
4. Copy the DAX query for deeper analysis

### Step 2: Trace File Analysis

Power BI Desktop writes session traces to the local filesystem:

1. File > Options and settings > Options > Diagnostics
2. Click "Open crash dump/traces folder"
3. Navigate up one level to `AnalysisServicesWorkspaces`
4. Open the active workspace folder > Data > `FlightRecorderCurrent.trc`
5. Open in SQL Server Profiler

**Key events to watch:**

| Event | What It Shows |
|-------|--------------|
| Query Begin / Query End | DAX query sent by the visual |
| DirectQuery Begin / DirectQuery End | Native SQL sent to the source |
| Duration column | Time in milliseconds per event |
| ActivityID | Groups related DAX and SQL events |

### Step 3: Analyze Generated SQL

Power BI generates SQL from your model definition. Common patterns:

- Subselects for each Power Query step (derived tables)
- WHERE clauses from slicer/filter context
- GROUP BY from visual aggregations
- Multiple queries per visual (one per measure + one for filter context)

### Capture Best Practices

- Keep Profiler sessions short (< 10 seconds of targeted actions)
- Reopen trace file to see newly flushed events
- Avoid multiple concurrent Desktop instances

---

## Source-Side Optimization

### Indexing Strategy

| Visual Pattern | Required Index |
|---------------|---------------|
| Filter/slicer on column X | Non-clustered index on X |
| Aggregation (SUM, COUNT) | Columnstore index on fact table |
| Join between tables | Indexes on join key columns |
| Date range filter | Clustered index on date column |
| Top N queries | Index on sort column |

### SQL Server / Synapse Specific

```sql
-- Create columnstore index for aggregation-heavy queries
CREATE NONCLUSTERED COLUMNSTORE INDEX IX_Sales_ColStore
ON dbo.Sales (SalesAmount, Quantity, OrderDate, ProductKey, CustomerKey);

-- Create covering index for common filter patterns
CREATE NONCLUSTERED INDEX IX_Sales_Date_Product
ON dbo.Sales (OrderDate, ProductKey)
INCLUDE (SalesAmount, Quantity);
```

### Materialized Views

For frequently queried aggregations, create materialized views at the source:

```sql
CREATE VIEW dbo.vw_DailySalesSummary
WITH SCHEMABINDING
AS
SELECT
    OrderDate,
    ProductKey,
    SUM(SalesAmount) AS TotalSales,
    COUNT_BIG(*) AS RowCount
FROM dbo.Sales
GROUP BY OrderDate, ProductKey;

-- Add clustered index to materialize
CREATE UNIQUE CLUSTERED INDEX IX_DailySales
ON dbo.vw_DailySalesSummary (OrderDate, ProductKey);
```

### Query Timeout Configuration

Default DirectQuery timeout is 225 seconds. Adjust if needed:
- Dataset settings > DirectQuery > Maximum query timeout

If queries regularly approach this limit, the source needs optimization or the model needs an Import/Composite approach.

---

## Model-Side Optimization

### Reduce Query Complexity

| Technique | How |
|-----------|-----|
| Limit relationships | Use only necessary relationships; avoid bi-directional |
| Simplify DAX | Avoid iterators (SUMX, etc.) in DirectQuery; use pre-aggregated source views |
| Reduce visual fields | Fewer fields per visual = simpler generated SQL |
| Avoid calculated columns | Push calculations to the source as computed columns or views |
| Use pre-aggregated tables | Create summary tables at the source for common aggregations |

### Aggregation Tables (User-Defined)

Create Import-mode aggregation tables that Power BI queries first, falling back to DirectQuery for detail:

1. Create an aggregation table at the source (daily summary, monthly summary)
2. Import this table into the model
3. Configure aggregation mappings in Power BI Desktop
4. Power BI automatically routes queries to the aggregation when possible

### Dual Storage Mode

Set dimension tables to Dual mode:
- Behaves as Import when joined with Import tables
- Behaves as DirectQuery when joined with DirectQuery tables
- Reduces cross-source joins

---

## Composite Model Strategy

### Architecture Pattern

```
[Import: Aggregation tables]     → Fast, pre-aggregated queries
         ↕ (aggregation mapping)
[DirectQuery: Detail tables]     → Real-time, row-level access
         ↕ (relationship)
[Dual: Dimension tables]         → Flexible join behavior
```

### Implementation Steps

1. Identify the most queried aggregation patterns (e.g., daily sales by product)
2. Create summary tables in the source or as Import tables in the model
3. Set the fact table(s) to DirectQuery
4. Set dimension tables to Dual
5. Configure aggregation mappings:
   - Manage Aggregations dialog in Power BI Desktop
   - Map each aggregation column to its detail-level counterpart
6. Test with Performance Analyzer to verify aggregation hits

### Monitoring Aggregation Effectiveness

In DAX Studio with Server Timings enabled:
- Look for "Aggregation" in the query plan
- If queries bypass aggregations, check mapping completeness
- Ensure the visual's granularity matches an available aggregation level

---

## Fabric Lakehouse and Warehouse Specifics

### Lakehouse SQL Analytics Endpoint

When connecting Power BI to a Lakehouse:
- Only Delta tables are queryable via the SQL endpoint
- Enable VOrder for optimal read performance (`readHeavyForPBI` profile)
- Tables in Parquet, CSV, or other formats must be converted to Delta first
- The SQL endpoint is read-only; no DML operations

### Data Warehouse in Fabric

When connecting Power BI to a Fabric Warehouse:
- Full T-SQL support (unlike the Lakehouse SQL endpoint)
- Create indexed views and statistics for query optimization
- Use result set caching for frequently accessed queries
- Native support for stored procedures and functions

### Performance Comparison

| Feature | Lakehouse SQL Endpoint | Fabric Warehouse |
|---------|----------------------|------------------|
| T-SQL Support | Limited (read-only) | Full |
| Indexes | Not supported | Supported |
| Statistics | Auto-generated | Auto + manual |
| VOrder benefit | Yes (significant) | N/A (different engine) |
| Best for PBI DQ | Simple star schema queries | Complex queries with joins |

### Optimization Checklist for Fabric Sources

- [ ] Tables are Delta format (Lakehouse)
- [ ] VOrder is enabled for PBI-serving workloads
- [ ] Unnecessary columns removed from source tables
- [ ] Partitioning strategy aligned with common filter patterns
- [ ] Statistics are up to date (Warehouse)
- [ ] Result set caching enabled for hot queries (Warehouse)
