# Table Maintenance Workflow

## Table of Contents

- [Maintenance Operations Overview](#maintenance-operations-overview)
- [OPTIMIZE: File Compaction](#optimize-file-compaction)
- [V-Order: Read Optimization](#v-order-read-optimization)
- [VACUUM: Storage Cleanup](#vacuum-storage-cleanup)
- [Scheduling Maintenance](#scheduling-maintenance)
- [REST API for Table Maintenance](#rest-api-for-table-maintenance)

## Maintenance Operations Overview

Delta tables degrade over time due to data skew from new data, accumulation of small files from batch/streaming ingestion, overhead from update/delete operations adding immutable Parquet files, and stale files and logs consuming storage. Regular maintenance is essential.

Three operations are available:

1. **OPTIMIZE** — Consolidates small Parquet files into larger ones (target 128 MB to 1 GB)
2. **V-Order** — Applies optimized sorting, encoding, and compression for fast reads
3. **VACUUM** — Removes old files no longer referenced by the Delta log

## OPTIMIZE: File Compaction

### Basic OPTIMIZE

```sql
%%sql
OPTIMIZE my_schema.my_table;
```

### OPTIMIZE with predicate (partial compaction)

```sql
%%sql
OPTIMIZE my_schema.my_table WHERE date_column >= '2025-01-01';
```

### OPTIMIZE with Z-ORDER

```sql
%%sql
OPTIMIZE my_schema.my_table ZORDER BY (region, product_category);
```

### Fast OPTIMIZE (skip unnecessary compaction)

Fast Optimize evaluates whether each candidate bin of files meets compaction goals before rewriting. Enable it to reduce unnecessary I/O:

```python
# PySpark
spark.conf.set('spark.microsoft.delta.optimize.fast.enabled', True)
```

```sql
-- Spark SQL
SET spark.microsoft.delta.optimize.fast.enabled = TRUE;
```

### When to run OPTIMIZE

- After loading large datasets (batch ETL completion)
- When file count exceeds 10x the optimal count
- When average file size drops below 64 MB
- After heavy update/delete operations

## V-Order: Read Optimization

V-Order applies optimized sorting, encoding, and compression to Parquet files. It adds approximately 15% to write time but delivers up to 50% better compression and significantly faster reads across all Fabric engines.

### Enable V-Order at table level

```sql
%%sql
ALTER TABLE my_schema.my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true");
```

### Apply V-Order during OPTIMIZE

```sql
%%sql
OPTIMIZE my_schema.my_table VORDER;
```

### Combined Z-ORDER and V-Order

```sql
%%sql
OPTIMIZE my_schema.my_table ZORDER BY (customer_id, order_date) VORDER;
```

### Session-level V-Order control

```python
# Enable V-Order for all writes in the session
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

**Important:** New Fabric workspaces default to `writeHeavy` profile where V-Order is disabled (`spark.sql.parquet.vorder.default=false`). Explicitly enable V-Order for read-optimized tables.

## VACUUM: Storage Cleanup

VACUUM removes old Parquet files no longer referenced by the Delta transaction log.

```sql
%%sql
VACUUM my_schema.my_table RETAIN 168 HOURS;  -- 7 days
```

**Critical warnings:**

- Default retention is 7 days — do NOT reduce below 7 days without understanding the impact
- Shorter retention breaks Delta time travel capabilities
- Concurrent readers may fail if active files are vacuumed
- VACUUM will fail by default with retention less than 7 days

To force shorter retention (use with extreme caution):

```python
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
```

## Scheduling Maintenance

### Using Fabric Pipelines

Create a pipeline with a Notebook activity that runs maintenance on a schedule:

```python
# maintenance_notebook.py
tables_to_maintain = [
    "sales.fact_orders",
    "sales.fact_line_items",
    "inventory.fact_movements"
]

for table_name in tables_to_maintain:
    print(f"Optimizing {table_name}...")
    spark.sql(f"OPTIMIZE {table_name} VORDER")
    print(f"Vacuuming {table_name}...")
    spark.sql(f"VACUUM {table_name} RETAIN 168 HOURS")
    print(f"Completed {table_name}")
```

Schedule the pipeline to run nightly or after major ETL loads.

### Using Fabric REST API

The REST API enables automation from PowerShell or CI/CD pipelines. See the [run-table-maintenance.ps1](../scripts/run-table-maintenance.ps1) script for a complete implementation.

## REST API for Table Maintenance

### Submit maintenance request

```
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance
```

Request body:

```json
{
  "executionData": {
    "tableName": "my_table",
    "schemaName": "my_schema",
    "optimizeSettings": {
      "vOrder": "true",
      "zOrderBy": ["customer_id"]
    },
    "vacuumSettings": {
      "retentionPeriod": "7.01:00:00"
    }
  }
}
```

### Monitor operation status

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances/{operationId}
```

Possible statuses: `NotStarted`, `InProgress`, `Completed`, `Failed`, `Canceled`, `Deduped`
