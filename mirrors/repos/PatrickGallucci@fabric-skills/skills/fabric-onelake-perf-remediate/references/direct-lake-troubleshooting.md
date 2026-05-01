# Direct Lake remediate

## Table of Contents

- [How Direct Lake Works](#how-direct-lake-works)
- [Common Fallback Causes](#common-fallback-causes)
- [Diagnostic Steps](#diagnostic-steps)
- [Optimization Checklist](#optimization-checklist)

## How Direct Lake Works

Direct Lake is a storage mode for Power BI semantic models that reads data directly from Delta tables in OneLake. It avoids data import while maintaining near-import performance through two key operations:

- **Framing** — A refresh operation that scans the Delta log to build a mapping of which Parquet files and row groups contain the data. This must be run after data changes.
- **Transcoding** — On-demand loading of column data from V-Ordered Parquet files into the VertiPaq in-memory store. Columns are loaded as queries request them.

When Direct Lake cannot serve a query (due to guardrails, unframed data, or unsupported operations), it falls back to **DirectQuery**, which is significantly slower.

## Common Fallback Causes

| Cause | Symptom | Resolution |
|-------|---------|------------|
| Model not framed after data load | Stale data, DirectQuery fallback | Run semantic model refresh |
| Table exceeds row count guardrail | Fallback on large tables | Check SKU guardrails; upgrade SKU |
| Too many Parquet files per table | Slow framing, potential fallback | Run OPTIMIZE to compact files |
| Non-V-Ordered files | Slow transcoding, higher memory | Apply V-Order via OPTIMIZE VORDER |
| Large string columns | Excessive memory for transcoding | Use varchar(n) with smallest needed n |
| DAX query uses unsupported pattern | Query-level fallback | Review DAX for Direct Lake compatibility |
| Column count exceeds guardrails | Fallback | Reduce column count or upgrade SKU |

## Diagnostic Steps

### Step 1: Check framing status

After loading data into lakehouse tables, verify the semantic model has been refreshed:

1. Open the semantic model in the Fabric portal
2. Check the last refresh time — it should be after your latest data load
3. If stale, trigger a refresh manually or via API

### Step 2: Verify V-Order on source tables

```sql
%%sql
-- Check V-Order property
SHOW TBLPROPERTIES my_schema.my_table;
```

If `delta.parquet.vorder.enabled` is absent or false, apply V-Order:

```sql
%%sql
OPTIMIZE my_schema.my_table VORDER;
```

### Step 3: Check file count and size

Excessive small files slow framing and transcoding. Run the table health check script or use:

```python
# Check Delta table detail
from delta.tables import DeltaTable
dt = DeltaTable.forName(spark, "my_schema.my_table")
detail = dt.detail().collect()[0]
print(f"Files: {detail['numFiles']}")
print(f"Size (bytes): {detail['sizeInBytes']}")
print(f"Avg file size (MB): {detail['sizeInBytes'] / detail['numFiles'] / 1024 / 1024:.1f}")
```

Target: fewer than 1,000 files per table, average file size 128 MB to 1 GB.

### Step 4: Review string column widths

Large string data types (varchar(8000), varchar(max)) cause excessive memory consumption during transcoding. Use the smallest varchar(n) that accommodates actual data:

```sql
-- In Spark SQL, create tables with precise column widths
CREATE TABLE analytics.customers (
    customer_id BIGINT,
    customer_name VARCHAR(100),
    email VARCHAR(255)
);
```

### Step 5: Check SKU guardrails

Each Fabric SKU has limits on the number of rows and columns per table in Direct Lake mode. If your tables exceed these limits, Direct Lake falls back to DirectQuery. Upgrade the SKU or reduce table size.

## Optimization Checklist

Before deploying a Direct Lake semantic model:

- [ ] All source tables are in Delta format in OneLake
- [ ] V-Order is enabled on all source tables
- [ ] Tables have been compacted with OPTIMIZE (target < 1,000 files)
- [ ] String columns use precise varchar(n) widths
- [ ] Table row counts are within SKU guardrails
- [ ] Semantic model has been framed (refreshed) after latest data load
- [ ] VACUUM has been run to remove stale files
- [ ] Partitioning strategy aligns with common filter patterns
