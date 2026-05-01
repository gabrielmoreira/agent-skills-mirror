# Table Maintenance Guide for Fabric Delta Lake

Comprehensive guide to Delta Lake table maintenance operations in Microsoft Fabric, including OPTIMIZE, VACUUM, V-Order, Z-Order, and Optimized Write.

## Table of Contents

- [Why Table Maintenance Matters](#why-table-maintenance-matters)
- [OPTIMIZE Command](#optimize-command)
- [VACUUM Command](#vacuum-command)
- [V-Order](#v-order)
- [Z-Order](#z-order)
- [Optimized Write](#optimized-write)
- [Partition Strategy](#partition-strategy)
- [Table Maintenance API](#table-maintenance-api)
- [Maintenance Scheduling](#maintenance-scheduling)

---

## Why Table Maintenance Matters

Delta tables degrade over time due to four factors:

1. **Data skew** — New data may be unevenly distributed across partitions
2. **Small file accumulation** — Frequent batch/streaming ingestion creates many small Parquet files
3. **Immutable file overhead** — UPDATE and DELETE operations create new files (Parquet files are immutable), amplifying the small file problem
4. **Stale file buildup** — Old, dereferenced Parquet and log files consume storage

Designing the table's physical structure based on ingestion frequency and read patterns is often more important than running maintenance commands after the fact.

---

## OPTIMIZE Command

OPTIMIZE performs bin-compaction: it merges many small Parquet files into fewer, larger files for better read performance.

### Basic Usage

```sql
%%sql
-- Compact all files in a table
OPTIMIZE schema_name.table_name;

-- Compact only files in a specific partition
OPTIMIZE schema_name.table_name WHERE date_key = '2025-01-15';

-- Compact with V-Order applied
OPTIMIZE schema_name.table_name VORDER;

-- Compact with Z-Order on specific columns, plus V-Order
OPTIMIZE schema_name.table_name
    ZORDER BY (customer_id, transaction_date)
    VORDER;

-- Compact with partition predicate + Z-Order + V-Order
OPTIMIZE schema_name.table_name
    WHERE date_key >= '2025-01-01'
    ZORDER BY (customer_id)
    VORDER;
```

### PySpark API

```python
from delta.tables import DeltaTable

dt = DeltaTable.forName(spark, "schema_name.table_name")

# Basic optimize
dt.optimize().executeCompaction()

# Optimize with Z-Order
dt.optimize().executeZOrderBy("customer_id", "transaction_date")
```

### Target File Sizes

- Default target: ~128MB (controlled by `spark.databricks.delta.optimizeWrite.binSize`)
- For Direct Lake / Power BI: target 1GB files for optimal segment sizes (1M-16M rows per row group)
- Adaptive target file size can improve compaction performance by 30-60%

### When to Run OPTIMIZE

| Scenario | Frequency | Scope |
|----------|-----------|-------|
| Daily batch ETL | After each load | Full table or recent partitions |
| Streaming tables | Daily or more often | Recent partitions |
| Ad-hoc heavy updates | After bulk operations | Affected partitions |
| Direct Lake backing tables | Weekly or when small files accumulate | Full table |
| Tables under 1GB | Rarely needed | Full table |

### OPTIMIZE via Lakehouse UI

1. Open Lakehouse in Fabric portal
2. In the Explorer, right-click on the table
3. Select **Maintenance**
4. Choose optimization options on the **Run maintenance commands** page
5. Click **Run now**

---

## VACUUM Command

VACUUM removes old Parquet files that are no longer referenced by the current Delta table version. This reclaims storage but eliminates the ability to time-travel to versions that used those files.

### Basic Usage

```sql
%%sql
-- VACUUM with default 7-day retention
VACUUM schema_name.table_name;

-- VACUUM with explicit retention (minimum 7 days recommended)
VACUUM schema_name.table_name RETAIN 168 HOURS;  -- 7 days
```

### Safety Considerations

> **Critical:** Setting retention shorter than 7 days can break concurrent readers and cause table corruption if uncommitted files are removed.

- Default retention: 7 days
- Minimum safe retention: 7 days (enforced by `spark.databricks.delta.retentionDurationCheck.enabled`)
- After VACUUM, time travel to versions older than the retention period will fail

To force shorter retention (use with extreme caution):

```python
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql("VACUUM schema_name.table_name RETAIN 24 HOURS")
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "true")
```

### VACUUM and Direct Lake

Direct Lake semantic models reference specific Delta commit versions. Ensure the Delta table retains the commit version that a framed Direct Lake model depends on. If those Parquet files are vacuumed before the model is reframed, users will encounter query errors.

Best practice: Run VACUUM daily with 7-day retention, and ensure Direct Lake model refresh (framing) happens more frequently than the retention period.

---

## V-Order

V-Order is a write-time optimization that applies special sorting and encoding to Parquet files, enabling faster reads in Power BI (VertiScan) and Spark SQL queries.

### How V-Order Works

- Applies columnar compression optimizations during file writes
- Faster data loading: streaming compressed data boosts transcoding efficiency
- VertiScan can compute results directly on V-Ordered compressed data, skipping decompression
- Compatible with standard Parquet readers (graceful fallback)

### Enable V-Order

**Session level:**

```python
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

**Table level (persisted):**

```sql
%%sql
ALTER TABLE schema_name.table_name
SET TBLPROPERTIES('delta.parquet.vorder.enabled' = 'true');
```

**During OPTIMIZE only:**

```sql
%%sql
-- Apply V-Order without enabling it for future writes
OPTIMIZE schema_name.table_name VORDER;
```

### Disable V-Order

```sql
%%sql
ALTER TABLE schema_name.table_name
SET TBLPROPERTIES('delta.parquet.vorder.enabled' = 'false');

-- Or remove the property entirely
ALTER TABLE schema_name.table_name
UNSET TBLPROPERTIES('delta.parquet.vorder.enabled');
```

### V-Order Decision Matrix

| Workload | Enable V-Order? | Reasoning |
|----------|----------------|-----------|
| Write-heavy ETL / streaming | No | V-Order adds write overhead |
| Power BI Direct Lake | Yes | Significantly faster VertiScan |
| Interactive Spark SQL | Optional | Moderate read improvement |
| Mixed read/write | Apply via OPTIMIZE only | Best of both: fast writes, periodic read optimization |

> **Important:** On new Fabric workspaces, V-Order is disabled by default (`writeHeavy` profile). Enable it explicitly for read-optimized scenarios.

---

## Z-Order

Z-Order co-locates related data in the same set of files using a space-filling curve. This dramatically improves data skipping for queries that filter on Z-Ordered columns.

### Usage

```sql
%%sql
-- Z-Order on one column
OPTIMIZE schema_name.table_name ZORDER BY (customer_id);

-- Z-Order on multiple columns (ordered by selectivity/frequency)
OPTIMIZE schema_name.table_name ZORDER BY (customer_id, transaction_date);

-- Combined with V-Order
OPTIMIZE schema_name.table_name ZORDER BY (customer_id) VORDER;
```

### When to Use Z-Order

- Tables frequently filtered by specific columns that are NOT partition columns
- High-cardinality filter columns where partitioning would create too many small files
- Tables over 1TB where partition pruning alone is insufficient
- Columns commonly used in JOIN or WHERE clauses

### Z-Order vs Partitioning

| Feature | Partitioning | Z-Order |
|---------|-------------|---------|
| Mechanism | Separate folders per value | Co-locate within files |
| Best for | Low cardinality (< 200 values) | High cardinality |
| Tables | > 1TB | Any size |
| Applied during | Write time | OPTIMIZE time |
| Can combine? | Yes — partition on date, Z-Order on ID within partitions |

---

## Optimized Write

Optimized Write is a Delta Lake feature that dynamically merges or splits partitions before writing to produce well-sized output files, reducing the small file problem.

### How It Works

- Merges small partitions into larger writes
- Splits oversized partitions into multiple files
- Eliminates the need for manual `repartition()` or `coalesce()` before writes
- Incurs a full shuffle, so may degrade performance for some workloads

### Configuration

```python
# Enable Optimized Write
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# Set target file size (default 128MB)
spark.conf.set("spark.databricks.delta.optimizeWrite.binSize", "128")

# Enable for partitioned tables
spark.conf.set("spark.databricks.delta.optimizeWrite.partitioned.enabled", "true")
```

### When to Use

| Scenario | Recommended? | Notes |
|----------|-------------|-------|
| Streaming ingestion | Yes | Prevents small file accumulation |
| Batch ETL with `partitionBy` | Yes | Replaces manual repartition |
| Jobs already using `coalesce()`/`repartition()` | Yes | Refactor to use Optimized Write instead |
| Write-heavy jobs prioritizing throughput | Maybe | Full shuffle adds overhead |

---

## Partition Strategy

### Decision Framework

1. **Table under 1TB?** Do not partition. Use Z-Order on filter columns instead.
2. **Low-cardinality column available?** (< 200 distinct values) Partition on it (e.g., date, region).
3. **Each partition will have >= 1GB of data?** Proceed with partitioning.
4. **Direct Lake backing table?** Partition on a low-cardinality column to enable efficient incremental framing.

### Partitioning Best Practices

- Target at least 1GB per partition after compaction
- Common partition columns: date keys, region codes, load batch identifiers
- Never partition on high-cardinality columns (user IDs, transaction IDs)
- Combine partition pruning with Z-Order for multi-dimensional filtering

```python
# Good: Partition by date (365 values/year)
df.write.format("delta") \
    .partitionBy("date_key") \
    .saveAsTable("schema_name.fact_transactions")

# Bad: Partition by customer_id (millions of values)
# This creates millions of tiny folders
```

---

## Table Maintenance API

Fabric provides a REST API for automated table maintenance (OPTIMIZE + V-Order + Z-Order + VACUUM).

### Submit Maintenance Job

```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance

{
    "executionData": {
        "tableName": "{table_name}",
        "schemaName": "{schema_name}",
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

### Monitor Maintenance Job

```http
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances/{operationId}
```

**Status values:** NotStarted, InProgress, Completed, Failed, Canceled, Deduped

---

## Maintenance Scheduling

### Recommended Cadence

| Table Type | OPTIMIZE | VACUUM | V-Order |
|-----------|----------|--------|---------|
| Streaming sink | Daily | Weekly | Apply during OPTIMIZE |
| Daily batch load | After each load | Weekly | Apply during OPTIMIZE |
| Infrequently updated | Monthly | Monthly | Apply during OPTIMIZE |
| Direct Lake backing | Weekly or when file count spikes | Weekly (ensure retention > frame interval) | Always |

### Automation Approaches

1. **Notebook-based:** Schedule a maintenance notebook via Fabric pipelines
2. **REST API-based:** Use the Table Maintenance API from PowerShell, Python, or Data Factory
3. **Lakehouse UI:** Manual ad-hoc maintenance for individual tables
