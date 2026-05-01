# Delta Table Health & Maintenance

## Table of Contents

- [Symptoms of Unhealthy Delta Tables](#symptoms-of-unhealthy-delta-tables)
- [Small File Problem](#small-file-problem)
- [Running OPTIMIZE](#running-optimize)
- [V-Order Configuration](#v-order-configuration)
- [Z-Order (Column Clustering)](#z-order-column-clustering)
- [VACUUM Operations](#vacuum-operations)
- [Table Maintenance via REST API](#table-maintenance-via-rest-api)
- [Maintenance Scheduling Best Practices](#maintenance-scheduling-best-practices)

## Symptoms of Unhealthy Delta Tables

Delta tables degrade over time without maintenance. Watch for these signs:

1. **Query duration increasing** without data volume growth
2. **File listing operations** taking longer (visible in Spark UI stage details)
3. **Many small Parquet files** in the Delta table directory (< 32 MB each)
4. **High version counts** in `DESCRIBE HISTORY` without corresponding OPTIMIZE runs
5. **Storage bloat** from unreferenced files left after updates/deletes

## Small File Problem

The most common Delta performance issue. Causes include:

- Frequent append operations from streaming workloads
- Low-volume batch writes (e.g., hourly micro-batches)
- UPDATE/DELETE/MERGE operations that rewrite small portions of data
- Over-partitioning (too many partition columns or high-cardinality partitions)

### Diagnosing Small Files

```python
# Count files and assess sizes
import pyspark.sql.functions as F

table_path = "Tables/your_table_name"
files_df = spark.read.format("delta").load(table_path)

# Check file count and sizes via Delta log
dt = DeltaTable.forPath(spark, table_path)
detail = spark.sql(f"DESCRIBE DETAIL delta.`{table_path}`")
detail.select("numFiles", "sizeInBytes").show()

# Calculate average file size
detail_row = detail.collect()[0]
avg_size_mb = (detail_row["sizeInBytes"] / detail_row["numFiles"]) / (1024 * 1024)
print(f"Average file size: {avg_size_mb:.1f} MB")
print(f"Total files: {detail_row['numFiles']}")

# Target: 128 MB–1 GB per file for optimal read performance
if avg_size_mb < 32:
    print("WARNING: Small file problem detected. Run OPTIMIZE.")
elif avg_size_mb < 128:
    print("INFO: Files are below optimal size. Consider OPTIMIZE.")
else:
    print("OK: File sizes are in healthy range.")
```

## Running OPTIMIZE

OPTIMIZE compacts small files into larger ones (bin-compaction).

### Via Spark SQL

```python
# Basic OPTIMIZE
spark.sql("OPTIMIZE your_table_name")

# OPTIMIZE with V-Order (recommended for read-heavy workloads)
spark.sql("OPTIMIZE your_table_name VORDER")

# OPTIMIZE with Z-Order on specific columns
spark.sql("OPTIMIZE your_table_name ZORDER BY (column1, column2)")

# OPTIMIZE a specific partition
spark.sql("""
    OPTIMIZE your_table_name
    WHERE date_partition = '2025-01-15'
    VORDER
""")
```

### Via Delta API

```python
from delta.tables import DeltaTable

dt = DeltaTable.forName(spark, "your_table_name")

# Basic optimize
dt.optimize().executeCompaction()

# Optimize with Z-Order
dt.optimize().executeZOrderBy("column1", "column2")
```

## V-Order Configuration

V-Order applies a special sort order during writes that accelerates reads for Power BI
Direct Lake, SQL analytics endpoint, and Spark SQL queries.

### Enable V-Order Globally

```python
# In environment Spark properties or notebook
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

### Enable V-Order per Write

```python
df.write.format("delta") \
    .option("parquet.vorder.enabled", "true") \
    .mode("overwrite") \
    .saveAsTable("your_table_name")
```

### Key Consideration

New Fabric workspaces default to the `writeHeavy` resource profile, which **disables
VOrder by default** (`spark.sql.parquet.vorder.default=false`). If your workload is
read-heavy (dashboards, interactive queries), switch to `readHeavyForSpark` or
`readHeavyForPBI`, or manually enable VOrder.

## Z-Order (Column Clustering)

Z-Order co-locates related data in the same files based on column values. Most
beneficial for columns frequently used in WHERE clauses, JOIN keys, or GROUP BY.

### When to Use Z-Order

- Queries consistently filter on the same 1–3 columns
- Table is large (millions+ rows) and full scans are expensive
- Column has moderate-to-high cardinality

### Z-Order Best Practices

- Limit to 1–3 columns (diminishing returns beyond that)
- Choose columns that appear together in query predicates
- Re-run Z-Order after significant data changes (not needed on every write)
- Combine with V-Order: `OPTIMIZE table ZORDER BY (col1) VORDER`

## VACUUM Operations

VACUUM removes unreferenced data files older than the retention threshold.

```python
# VACUUM with default retention (7 days)
spark.sql("VACUUM your_table_name")

# VACUUM with custom retention
spark.sql("VACUUM your_table_name RETAIN 168 HOURS")  -- 7 days
```

### Retention Period Warning

Setting retention below 7 days can break concurrent readers and time travel.
To force shorter retention (not recommended for production):

```python
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql("VACUUM your_table_name RETAIN 24 HOURS")
```

### Dry Run First

```python
# Preview files that would be deleted
spark.sql("VACUUM your_table_name RETAIN 168 HOURS DRY RUN")
```

## Table Maintenance via REST API

Use the Fabric REST API for automated maintenance in pipelines.

### Submit Maintenance Job

```
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance
```

```json
{
  "executionData": {
    "tableName": "your_table",
    "schemaName": "dbo",
    "optimizeSettings": {
      "vOrder": "true",
      "zOrderBy": ["frequently_filtered_column"]
    },
    "vacuumSettings": {
      "retentionPeriod": "7.01:00:00"
    }
  }
}
```

### Monitor Job Status

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances/{operationId}
```

Status values: `NotStarted`, `InProgress`, `Completed`, `Failed`, `Canceled`, `Deduped`.

See the [Invoke-TableMaintenance.ps1](../scripts/Invoke-TableMaintenance.ps1) script
for a complete PowerShell implementation.

## Maintenance Scheduling Best Practices

| Table Pattern | OPTIMIZE Frequency | VACUUM Frequency | V-Order | Z-Order |
|--------------|-------------------|------------------|---------|---------|
| Streaming append (high volume) | Daily | Weekly | Yes | On filter columns |
| Batch ETL (daily loads) | After each load | Weekly | Yes | On join/filter columns |
| Slowly changing dimensions | Weekly | Monthly | Yes | On lookup key |
| Log/audit tables (append only) | Weekly | Monthly | Optional | On timestamp |
| Aggregation tables (overwrite) | Not needed | Monthly | Yes | Not needed |
