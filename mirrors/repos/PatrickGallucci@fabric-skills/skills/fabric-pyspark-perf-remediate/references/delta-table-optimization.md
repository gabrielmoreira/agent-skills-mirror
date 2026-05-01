# Delta Table Optimization in Microsoft Fabric

## Table of Contents

- [Small File Problem](#small-file-problem)
- [OPTIMIZE Command](#optimize-command)
- [VACUUM Command](#vacuum-command)
- [Z-ORDER Clustering](#z-order-clustering)
- [VOrder Configuration](#vorder-configuration)
- [Optimized Write](#optimized-write)
- [Table Partitioning Best Practices](#table-partitioning-best-practices)
- [Streaming Write Optimization](#streaming-write-optimization)
- [Table Maintenance Automation](#table-maintenance-automation)

## Small File Problem

Delta Lake tables accumulate small files over time from append operations, streaming ingestion, and high-frequency updates. Each small file adds overhead to file listing, metadata management, and read operations.

### Diagnosing Small Files

```python
# Check file count and sizes for a Delta table
from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, "Tables/my_table")

# File statistics
files_df = spark.read.format("delta").load("Tables/my_table").inputFiles()
print(f"Total files: {len(files_df)}")

# More detailed analysis using the log
detail = spark.sql("DESCRIBE DETAIL my_table")
detail.select("numFiles", "sizeInBytes").show()

# Check file size distribution
import pyspark.sql.functions as F
file_sizes = spark.sql("""
    SELECT 
        input_file_name() as file_name,
        count(*) as row_count
    FROM my_table
    GROUP BY input_file_name()
""")
file_sizes.select(
    F.count("*").alias("total_files"),
    F.avg("row_count").alias("avg_rows_per_file"),
    F.min("row_count").alias("min_rows"),
    F.max("row_count").alias("max_rows")
).show()
```

### Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Files per table | < 1,000 | 1,000 - 10,000 | > 10,000 |
| Avg file size | 64 - 1024 MB | 1 - 64 MB | < 1 MB |
| Read time trend | Stable | Increasing 20%+ | Doubled+ |

## OPTIMIZE Command

`OPTIMIZE` compacts small files into larger ones, improving read performance.

### Basic Usage

```sql
-- Optimize entire table
OPTIMIZE my_table

-- Optimize specific partition
OPTIMIZE my_table WHERE date = '2025-01-15'

-- Optimize with Z-ORDER
OPTIMIZE my_table ZORDER BY (customer_id, event_type)
```

### PySpark API

```python
from delta.tables import DeltaTable

dt = DeltaTable.forPath(spark, "Tables/my_table")

# Basic optimize
dt.optimize().executeCompaction()

# Optimize with Z-ORDER
dt.optimize().executeZOrderBy("customer_id", "event_type")

# Optimize specific partition
dt.optimize() \
    .where("date = '2025-01-15'") \
    .executeCompaction()
```

### When to Run OPTIMIZE

- After batch load operations that append many small files
- On a schedule (daily or weekly) for tables with frequent small writes
- Before intensive read workloads (reports, dashboards, ML training)
- When `DESCRIBE DETAIL` shows file count growing significantly

### OPTIMIZE Target File Size

Fabric's Delta defaults target file sizes around 256 MB - 1 GB. You can override:

```python
spark.conf.set("spark.databricks.delta.optimize.maxFileSize", "536870912")  # 512 MB
```

## VACUUM Command

`VACUUM` removes old file versions that are no longer needed by the Delta transaction log.

```sql
-- Remove files older than 7 days (default retention)
VACUUM my_table

-- Remove files older than 24 hours (use with caution)
VACUUM my_table RETAIN 24 HOURS
```

### Safety Rules

```python
# VACUUM will not delete files newer than retention period
# Default retention: 7 days
# Minimum safe retention: 7 days (unless explicitly overridden)

# Override minimum (DANGEROUS - can break time travel and concurrent readers)
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql("VACUUM my_table RETAIN 0 HOURS")  # Removes ALL old versions
```

**Warning**: Setting retention below 7 days can break concurrent readers and time travel. Only do this for tables with no concurrent access and no time travel requirements.

### VACUUM Order of Operations

Always run `OPTIMIZE` before `VACUUM`:

```python
# 1. Compact small files into larger ones
spark.sql("OPTIMIZE my_table")

# 2. Remove old small files that are no longer referenced
spark.sql("VACUUM my_table RETAIN 168 HOURS")  # 7 days
```

## Z-ORDER Clustering

Z-ORDER co-locates related data within files, enabling data skipping during reads. Dramatically improves performance for filtered queries.

### When to Use Z-ORDER

- Queries frequently filter on specific non-partition columns
- The column has moderate-to-high cardinality
- Table is large enough that data skipping provides meaningful benefit (>1 GB)

```sql
-- Z-ORDER on frequently filtered columns
OPTIMIZE events ZORDER BY (customer_id, event_type)

-- Multi-column Z-ORDER (first column gets priority)
OPTIMIZE orders ZORDER BY (product_id, region, order_date)
```

### Z-ORDER vs Partitioning

| Feature | Partitioning | Z-ORDER |
|---------|-------------|---------|
| Cardinality | Low (10-1000 values) | Medium to High |
| Data layout | Separate directories | Co-located within files |
| Combinable | Yes (use both) | Applied during OPTIMIZE |
| Filter type | Equality, range | Equality, range, IN |
| Overhead | Directory management | OPTIMIZE execution time |

Use partitioning for low-cardinality, consistently-used filters (e.g., date). Use Z-ORDER for medium-high cardinality filters within partitions.

## VOrder Configuration

VOrder applies special encoding to Parquet files that significantly improves read performance for Power BI and SQL endpoint queries.

### Resource Profile Interaction

| Profile | VOrder Default | Use Case |
|---------|---------------|----------|
| `writeHeavy` | **Disabled** | ETL pipelines, data ingestion |
| `readHeavyForSpark` | Enabled | Interactive Spark queries |
| `readHeavyForPBI` | Enabled | Power BI, SQL analytics endpoint |

### Manual VOrder Control

```python
# Enable VOrder for specific write operations
spark.conf.set("spark.sql.parquet.vorder.default", "true")

# Disable VOrder for write-heavy operations
spark.conf.set("spark.sql.parquet.vorder.default", "false")

# Per-write VOrder (table property)
spark.sql("""
    ALTER TABLE my_table 
    SET TBLPROPERTIES ('delta.parquet.vorder.enabled' = 'true')
""")
```

### Trade-offs

VOrder adds write-time overhead (10-15% slower writes) but significantly improves read performance (2-5x for Power BI DirectQuery). Enable it for tables consumed by Power BI or the SQL analytics endpoint; disable for staging/intermediate ETL tables.

## Optimized Write

Optimized Write merges or splits partitions before writing to produce optimally-sized files, eliminating the need for manual `repartition()` or `coalesce()`.

### Enable Optimized Write

```python
# Session-level
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# Table property (permanent)
spark.sql("""
    ALTER TABLE my_table 
    SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true')
""")
```

### When Optimized Write Helps

- Replacing `repartition()` + `write` patterns
- Append-heavy workloads with inconsistent input sizes
- Streaming writes producing many small files

### When to Avoid

- Workloads already using manual partition management with `coalesce()` tuned to specific output requirements
- Very small writes where the optimization overhead exceeds benefit

## Table Partitioning Best Practices

### Choosing Partition Columns

```python
# Good: Low cardinality, commonly filtered
df.write.format("delta") \
    .partitionBy("year", "month") \
    .save("Tables/events")

# Bad: High cardinality creates too many small directories
# df.write.format("delta") \
#     .partitionBy("user_id") \  # Millions of unique values = millions of dirs
#     .save("Tables/events")
```

### Partition Guidelines

| Table Size | Recommended Partitioning |
|-----------|-------------------------|
| < 1 GB | No partitioning |
| 1 - 100 GB | 1 column (e.g., month or category) |
| 100 GB - 1 TB | 1-2 columns (e.g., year/month) |
| > 1 TB | 2 columns max, with Z-ORDER on additional columns |

**Target**: Each partition should contain at least 1 GB of data.

## Streaming Write Optimization

For structured streaming workloads writing to Delta tables:

### Trigger Interval Batching

```python
# Batch events to reduce file creation frequency
stream = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .trigger(processingTime="5 minutes") \
    .outputMode("append") \
    .toTable("streaming_events")
```

Longer trigger intervals produce fewer, larger files. Balance latency requirements against file size.

### Enable Optimized Write for Streaming

```python
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

stream = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .trigger(processingTime="2 minutes") \
    .outputMode("append") \
    .toTable("streaming_events")
```

## Table Maintenance Automation

### Fabric Lakehouse Table Maintenance

Fabric provides built-in table maintenance through the lakehouse UI. You can also schedule it programmatically:

```python
# Maintenance notebook - schedule via pipeline or Fabric scheduler
from datetime import datetime

tables = ["events", "orders", "customers", "products"]

for table in tables:
    print(f"[{datetime.now()}] Optimizing {table}...")
    spark.sql(f"OPTIMIZE {table}")
    print(f"[{datetime.now()}] Vacuuming {table}...")
    spark.sql(f"VACUUM {table} RETAIN 168 HOURS")
    print(f"[{datetime.now()}] {table} maintenance complete.")

# Verify results
for table in tables:
    detail = spark.sql(f"DESCRIBE DETAIL {table}")
    detail.select("name", "numFiles", "sizeInBytes").show(truncate=False)
```

### REST API Table Maintenance

Use the Fabric REST API to trigger table maintenance jobs programmatically. See the Fabric REST API documentation for the Jobs endpoint format.
