# Delta Table Health Assessment Reference

## Table of Contents

- [Overview](#overview)
- [Health Indicators](#health-indicators)
- [Diagnostic Queries](#diagnostic-queries)
- [File Size Guidelines](#file-size-guidelines)
- [Partitioning Best Practices](#partitioning-best-practices)
- [V-Order Assessment](#v-order-assessment)
- [Maintenance Scheduling](#maintenance-scheduling)

## Overview

Delta table health directly impacts query performance across all Fabric engines. Unhealthy tables exhibit symptoms like excessive small files, missing V-Order optimization, over-partitioning, and stale unreferenced files. This reference covers how to assess and monitor table health.

## Health Indicators

| Indicator | Healthy | Unhealthy | Impact |
|-----------|---------|-----------|--------|
| Average file size | 128 MB - 1 GB | < 10 MB or > 2 GB | Read/write performance |
| File count per table | Proportional to data size | Thousands of tiny files | Metadata overhead |
| V-Order applied | Yes (for read workloads) | No (when reads are primary) | 10-50% slower reads |
| Partition count | < 100-200 distinct values | Thousands of partitions | Excessive file fragmentation |
| Unreferenced files | Cleaned within 7 days | Months of orphaned files | Storage cost, confusion |
| Last OPTIMIZE run | Within past week | Never or months ago | Cumulative degradation |

## Diagnostic Queries

### Check Table Detail (File Count, Size)

```python
# PySpark — Get Delta table detail
from delta.tables import DeltaTable

dt = DeltaTable.forName(spark, "lakehouse_name.schema_name.table_name")
detail = dt.detail()
detail.show(truncate=False)
```

Key columns in detail output: `numFiles`, `sizeInBytes`, `partitionColumns`, `createdAt`, `lastModified`.

### Check Table History (Recent Operations)

```sql
-- Spark SQL
DESCRIBE HISTORY lakehouse_name.schema_name.table_name LIMIT 20;
```

Look for: frequency of OPTIMIZE operations, WRITE operations (indicates ingestion pattern), and any VACUUM entries.

### Count Files Per Partition

```python
# PySpark — Analyze file distribution across partitions
from pyspark.sql.functions import input_file_name, count, avg, lit
import os

table_path = "abfss://workspace@onelake.dfs.fabric.microsoft.com/lakehouse.Lakehouse/Tables/table_name"

df = spark.read.format("delta").load(table_path)
file_stats = (
    df.select(input_file_name().alias("file_path"))
    .distinct()
    .groupBy(lit("all").alias("group"))
    .agg(count("file_path").alias("total_files"))
)
file_stats.show()
```

### Check Current Spark Configuration

```python
# Check all performance-relevant settings
configs = [
    "spark.fabric.resourceProfile",
    "spark.sql.parquet.vorder.default",
    "spark.databricks.delta.optimizeWrite.enabled",
    "spark.databricks.delta.optimizeWrite.binSize",
    "spark.sql.shuffle.partitions",
    "spark.sql.autoBroadcastJoinThreshold",
    "spark.sql.files.maxPartitionBytes",
    "spark.ms.autotune.enabled",
    "spark.microsoft.delta.merge.lowShuffle.enabled",
]

for c in configs:
    try:
        val = spark.conf.get(c)
        print(f"{c} = {val}")
    except Exception:
        print(f"{c} = [not set]")
```

## File Size Guidelines

### General Lakehouse

Target 128 MB - 1 GB per Parquet file. Use OPTIMIZE to consolidate small files.

### SQL Analytics Endpoint

For best SQL analytics endpoint performance:
- Target ~2 million rows per Parquet file
- Target ~400 MB per file
- Set `maxRecordsPerFile = 2000000` before data changes
- Set `maxFileSize = 4 GB` before running OPTIMIZE

### Direct Lake / Power BI

- Keep total Parquet file count within guardrail limits
- Run OPTIMIZE regularly (daily for high-frequency ingestion)
- V-Order is critical for Verti-Scan acceleration
- Partition on low-cardinality columns only (< 100-200 distinct values)

## Partitioning Best Practices

### When to Partition

- Large tables (> 1 billion rows) with predictable filter patterns
- Low-cardinality columns: date keys, region codes, status flags
- Tables receiving incremental loads where you OPTIMIZE specific partitions

### When NOT to Partition

- Small to medium tables (partition overhead exceeds benefit)
- High-cardinality columns (customer_id, transaction_id) — use Z-Order instead
- When unsure — start without partitions and add later if needed

### Partition + Z-Order Strategy

```sql
-- Table partitioned by date, Z-Ordered by high-selectivity column
OPTIMIZE my_table WHERE date_key >= '2025-01-01'
  ZORDER BY (customer_id) VORDER;
```

## V-Order Assessment

### Check if Files Are V-Ordered

V-Order is metadata embedded in Parquet files. The easiest way to verify is to check the table properties and session configuration:

```sql
-- Check table property
SHOW TBLPROPERTIES lakehouse_name.schema_name.table_name;
```

Look for `delta.parquet.vorder.enabled`. If not set, files written before OPTIMIZE VORDER may not have V-Order.

### When V-Order Matters

| Scenario | V-Order Impact |
|----------|---------------|
| Power BI Direct Lake | Critical — enables Verti-Scan, major performance gain |
| SQL analytics endpoint | Important — faster analytical queries |
| Spark reads | Moderate — 10-50% read improvement |
| Spark writes | Negative — ~15% write overhead |

### Applying V-Order to Existing Tables

```sql
-- Rewrite all files with V-Order
OPTIMIZE my_table VORDER;

-- Or set table property for future writes
ALTER TABLE my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true");
```

## Maintenance Scheduling

### Recommended Cadence

| Workload Pattern | OPTIMIZE Frequency | VACUUM Frequency |
|-----------------|-------------------|-----------------|
| Daily batch ETL | Daily (after load) | Weekly |
| Hourly micro-batch | Daily | Weekly |
| Real-time streaming | Every 4-6 hours | Daily |
| Infrequent updates | Weekly or after large loads | Monthly |

### Automation Options

1. **Fabric Pipelines** — Schedule notebooks containing OPTIMIZE/VACUUM commands
2. **REST API** — Use PowerShell or Python to call the Table Maintenance API on a schedule
3. **Lakehouse UI** — Ad-hoc maintenance via right-click > Maintenance (manual only)
