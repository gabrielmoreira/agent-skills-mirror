# Delta Table Optimization and V-Order

Guide for optimizing Delta Lake tables in Microsoft Fabric for read and write performance.

## Table of Contents

- [Why Tables Degrade](#why-tables-degrade)
- [OPTIMIZE Command](#optimize-command)
- [VACUUM Command](#vacuum-command)
- [V-Order Configuration](#v-order-configuration)
- [ZORDER Indexing](#zorder-indexing)
- [Auto Compaction](#auto-compaction)
- [Optimize Write](#optimize-write)
- [Choosing the Right Strategy](#choosing-the-right-strategy)

## Why Tables Degrade

Delta table performance degrades over time for these reasons:

1. **Data skew** — New data added may create uneven partition distribution.
2. **Small files** — Batch and streaming ingestion produces many small Parquet files.
3. **Update/delete overhead** — Parquet files are immutable; changes create new files with changesets.
4. **Orphaned files** — Deleted data files and old log files remain in storage.

> Designing table physical structure based on ingestion frequency and read patterns is often more important than optimization commands.

## OPTIMIZE Command

Bin-compaction merges small files into larger, consolidated Parquet files.

```sql
%%sql
-- Basic optimize
OPTIMIZE my_lakehouse.my_table

-- Optimize with predicate (only affects matching partitions)
OPTIMIZE my_lakehouse.my_table WHERE date >= '2024-01-01'

-- Optimize with V-Order rewrite
OPTIMIZE my_lakehouse.my_table VORDER

-- Optimize with ZORDER and V-Order
OPTIMIZE my_lakehouse.my_table
  WHERE date >= '2024-01-01'
  ZORDER BY (customer_id, product_id) VORDER
```

When ZORDER and VORDER are used together, Spark performs bin-compaction, ZORDER, then VORDER sequentially.

**Schedule OPTIMIZE** for tables with frequent writes. Run during off-peak hours to minimize capacity impact.

## VACUUM Command

Removes dereferenced data files no longer needed by the current table version.

```sql
%%sql
-- Remove files older than 7 days (default retention)
VACUUM my_lakehouse.my_table

-- Remove files older than 24 hours (use with caution)
VACUUM my_lakehouse.my_table RETAIN 24 HOURS
```

> Do not set retention below your longest-running query duration to avoid breaking time travel or active reads.

## V-Order Configuration

V-Order is a write-time Parquet optimization that enables faster reads across all Fabric engines (Power BI, SQL, Spark). It applies special sorting, row group distribution, dictionary encoding, and compression.

**Performance characteristics:**

- Read improvement: 10% average, up to 50% in some scenarios
- Write overhead: approximately 15% increase in write time
- Compression improvement: up to 50% better compression

**Default behavior (new workspaces):**

V-Order is disabled by default (`spark.sql.parquet.vorder.default = false`) to optimize for write-heavy data engineering workloads.

### Check Current V-Order Setting

```python
spark.conf.get("spark.sql.parquet.vorder.default")
```

```sql
%%sql
SET spark.sql.parquet.vorder.default
```

### Enable V-Order (Read-Heavy Workloads)

```python
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

### Disable V-Order (Write-Heavy Workloads)

```python
spark.conf.set("spark.sql.parquet.vorder.default", "false")
```

### Table-Level V-Order

```sql
%%sql
-- Enable during table creation
CREATE TABLE my_table (id INT, name STRING)
USING parquet
TBLPROPERTIES("delta.parquet.vorder.enabled" = "true")

-- Enable on existing table
ALTER TABLE my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true")

-- Disable on existing table
ALTER TABLE my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "false")
```

> Session-level V-Order overrides table-level settings. When session is set to `true`, ALL writes use V-Order regardless of table properties.

### Runtime 1.3+ Behavior

In Fabric Runtime 1.3 and higher, `spark.sql.parquet.vorder.enable` is removed. V-Order is applied automatically during OPTIMIZE statements. Remove manual enable settings when migrating from earlier runtimes.

## ZORDER Indexing

ZORDER co-locates related data in the same files based on column values. Effective for columns frequently used in WHERE clauses.

```sql
%%sql
OPTIMIZE my_table ZORDER BY (date, region)
```

**Best practices:**

- ZORDER on 1–4 columns that appear most in query filters
- Choose high-cardinality columns for best results
- ZORDER is compatible with V-Order (apply both together)
- Re-run ZORDER after significant data changes

## Auto Compaction

Automatically compacts small files after write operations without manual OPTIMIZE scheduling.

```python
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
```

**Recommended for:**

- Ingestion pipelines with frequent small writes
- Streaming workloads producing many small files
- Replacing manually scheduled OPTIMIZE jobs on new tables

## Optimize Write

Reduces the number of output files and increases individual file sizes during write operations.

```python
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```

Fabric dynamically optimizes partitions with a default 128 MB target file size, configurable per workload.

## Choosing the Right Strategy

| Workload Pattern | V-Order | Auto Compact | Optimize Write | Scheduled OPTIMIZE |
|-----------------|---------|-------------|----------------|-------------------|
| Write-heavy ingestion | Off | On | On | Weekly |
| Read-heavy analytics | On | Optional | Optional | After major loads |
| Mixed read/write | Table-level | On | On | Daily off-peak |
| Streaming ingestion | Off | On | On | Hourly or daily |
| Dashboard / Power BI | On | Optional | Optional | Before refresh |

**Resource Profile shortcut:** Switch to `readHeavyforSpark` or `ReadHeavy` profiles to automatically enable V-Order and read-optimized configurations.
