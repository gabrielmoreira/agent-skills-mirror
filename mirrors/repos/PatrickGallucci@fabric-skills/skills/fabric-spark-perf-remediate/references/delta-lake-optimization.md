# Delta Lake Optimization Reference

## Table of Contents

- [File Scan Optimization](#file-scan-optimization)
- [Delta Write Optimization](#delta-write-optimization)
- [Table Maintenance Operations](#table-maintenance-operations)
- [VOrder Configuration](#vorder-configuration)
- [Partitioning Best Practices](#partitioning-best-practices)
- [Streaming Optimization](#streaming-optimization)
- [Small Files Problem](#small-files-problem)
- [Vacuum and Retention](#vacuum-and-retention)

---

## File Scan Optimization

### Diagnosing Slow Scans

Open Spark UI → SQL tab → look for `FileScan` nodes. Check:

- **Number of files scanned**: Thousands of small files = fragmentation problem
- **PushedFilters**: Absent = predicate pushdown not working
- **PartitionFilters**: Absent on partitioned tables = partition pruning not effective
- **Data read vs data processed**: Large gap = column pruning opportunity

### Improving Scan Performance

**Enable VOrder for read-heavy tables**:

```python
# At write time
df.write.format("delta") \
    .option("parquet.vorder.enabled", "true") \
    .mode("overwrite") \
    .saveAsTable("optimized_table")

# Or via spark config
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

**Tune maxPartitionBytes for large sequential scans**:

```python
# Increase for large table scans to reduce task count
spark.conf.set("spark.sql.files.maxPartitionBytes", "268435456")  # 256 MB
```

**Use Z-Order on frequently filtered columns**:

```sql
-- Apply Z-Order via SQL (or table maintenance API)
OPTIMIZE my_table ZORDER BY (customer_id, order_date)
```

---

## Delta Write Optimization

### Optimized Write

Optimized Write merges or splits partitions before writing to produce optimally-sized files:

```python
# Enable globally for the session
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# Or per-write operation
df.write.format("delta") \
    .option("optimizeWrite", "true") \
    .mode("append") \
    .saveAsTable("my_table")
```

**Trade-offs**:

- Pro: Produces fewer, larger files (reduces small files problem)
- Pro: Eliminates need for manual repartition/coalesce before write
- Con: Incurs a full shuffle before write (adds latency)
- Con: May degrade performance for jobs already using repartition/coalesce

**When to use**: ETL pipelines with many small append operations. Disable for jobs that already produce well-sized output partitions.

### Repartition vs Coalesce vs Optimized Write

| Approach | Shuffle? | Balanced Partitions? | Best For |
|----------|---------|---------------------|----------|
| `repartition(N)` | Yes (full) | Yes | When you need specific partition count |
| `coalesce(N)` | No (narrow) | No (uneven) | Reducing partitions efficiently |
| Optimized Write | Yes (full) | Yes (auto-sized) | General-purpose write optimization |

**Recommendation**: For most Fabric workloads, Optimized Write is the simplest option. Use repartition when you need precise control over partition count.

### Merge Operation Optimization

For Delta MERGE (upsert) operations:

```python
# Enable merge optimization settings
spark.conf.set("spark.microsoft.delta.merge.lowShuffle.enabled", "true")

# Ensure target table is Z-Ordered on merge key for faster lookups
# OPTIMIZE target_table ZORDER BY (merge_key)
```

---

## Table Maintenance Operations

### What Table Maintenance Does

Table maintenance performs three operations on Delta tables:

1. **Bin-compaction**: Merges small files into larger, optimally-sized files
2. **V-Order**: Applies columnar optimization for read performance
3. **Vacuum**: Removes unreferenced old files to reclaim storage

### Running Table Maintenance via UI

1. Open the Lakehouse in Fabric portal.
2. Right-click the target table → Maintenance.
3. Select operations: Optimize (compaction + VOrder) and/or Vacuum.
4. Configure vacuum retention (minimum 7 days recommended).
5. Run and monitor progress.

### Running Table Maintenance via REST API

```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance

{
    "executionData": {
        "tableName": "my_table",
        "schemaName": "dbo",
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

### Monitor Table Maintenance Progress

```http
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances/{operationId}
```

Status values: NotStarted, InProgress, Completed, Failed, Canceled, Deduped.

### Running Table Maintenance via Spark SQL

```sql
-- Bin compaction with V-Order
OPTIMIZE my_schema.my_table VORDER

-- Bin compaction with Z-Order
OPTIMIZE my_schema.my_table ZORDER BY (customer_id, order_date)

-- Vacuum with 7-day retention
VACUUM my_schema.my_table RETAIN 168 HOURS
```

### Maintenance Schedule Recommendations

| Table Characteristics | Compaction Frequency | Vacuum Frequency |
|----------------------|---------------------|-----------------|
| High-frequency append (streaming) | Every 1-4 hours | Daily |
| Daily batch ETL | After each ETL run | Weekly |
| Low-change reference tables | Weekly | Monthly |
| Tables consumed by Power BI | After each ETL + VOrder | Weekly |

---

## VOrder Configuration

### When to Enable VOrder

| Scenario | Enable VOrder? | Reason |
|----------|---------------|--------|
| Write-heavy ETL pipeline | No | Adds 10-20% write overhead |
| Tables read by Power BI DirectLake | Yes | Dramatically improves DirectLake performance |
| Interactive Spark analytics | Yes | Faster columnar reads |
| Temporary/staging tables | No | Short-lived, write overhead not justified |
| Archive/cold storage | No | Rarely read, write cost not justified |

### Enabling VOrder

**Per-session**:

```python
spark.conf.set("spark.sql.parquet.vorder.default", "true")
```

**Per-environment** (in Spark Properties):

```
spark.sql.parquet.vorder.default = true
```

**Retroactively via table maintenance**:

```sql
OPTIMIZE my_table VORDER
```

---

## Partitioning Best Practices

### Choosing Partition Columns

**Good partition columns have**:

- Low to medium cardinality (10-1000 distinct values)
- Commonly used in WHERE clauses
- Even data distribution across values

**Common choices**: year, month, region, category

**Avoid partitioning on**:

- High cardinality columns (customer_id, order_id) → thousands of tiny files
- Columns rarely used in filters → no partition pruning benefit
- Boolean columns → only 2 partitions, likely uneven

### Partition Count Guidelines

Target file sizes of 128 MB - 1 GB per partition:

```python
# Calculate optimal partition count
data_size_gb = 100  # Total data size in GB
target_file_size_gb = 0.5  # Target 500 MB files
partition_count = int(data_size_gb / target_file_size_gb)
```

### Avoiding Over-Partitioning

If your table has partitions producing files < 10 MB each:

1. Remove low-cardinality partition columns.
2. Use Z-Order instead of partitioning for filter columns.
3. Run table maintenance to compact existing small files.

---

## Streaming Optimization

### Structured Streaming Throughput Tuning

For Spark Structured Streaming jobs writing to Delta Lake:

**1. Match Spark partitions to Event Hub partitions**:

```python
# If Event Hub has 32 partitions, use 32 or a multiple
df = spark.readStream.format("eventhubs").options(**ehConf).load()
processed = df.repartition(32)  # Match source partitions
```

**2. Use trigger intervals to batch events**:

```python
# Available Once for batch-like processing
query = df.writeStream \
    .trigger(availableNow=True) \
    .format("delta") \
    .start()

# Or set a processing time interval
query = df.writeStream \
    .trigger(processingTime="30 seconds") \
    .format("delta") \
    .start()
```

**3. Enable Optimized Write for streaming sinks**:

```python
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```

**4. Combine in-memory and disk partitioning**:

```python
rawData = df \
    .repartition(48) \
    .writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint") \
    .outputMode("append") \
    .partitionBy("region", "event_date") \
    .toTable("streaming_events")
```

### Streaming vs Spark Job Definitions

| Feature | Notebook Streaming | Spark Job Definition |
|---------|-------------------|---------------------|
| Interactive debugging | Yes | No |
| Retry policy | Manual restart | Built-in retry with configurable interval |
| Production suitability | Development only | Recommended for production |
| Session resilience | Stops if session ends | Auto-restarts on failure |

For production streaming, use Spark Job Definitions with retry policies enabled.

---

## Small Files Problem

### Detecting Small Files

```python
# Check file count and sizes for a Delta table
from delta.tables import DeltaTable

dt = DeltaTable.forName(spark, "my_table")
detail = dt.detail().collect()[0]

print(f"Number of files: {detail['numFiles']}")
print(f"Size in bytes: {detail['sizeInBytes']}")
print(f"Average file size: {detail['sizeInBytes'] / max(detail['numFiles'], 1) / 1024 / 1024:.1f} MB")
```

**Healthy**: Average file size 128 MB - 1 GB.
**Problem**: Average file size < 32 MB or file count > 10,000 for tables under 100 GB.

### Resolving Small Files

1. **Immediate**: Run table maintenance with bin-compaction.
2. **Preventive**: Enable Optimized Write for the pipeline.
3. **Structural**: Review partition strategy and reduce over-partitioning.

---

## Vacuum and Retention

### Vacuum Best Practices

```sql
-- Standard vacuum with 7-day retention (recommended minimum)
VACUUM my_table RETAIN 168 HOURS
```

**Retention period considerations**:

- Minimum recommended: 7 days (protects concurrent readers and time travel)
- Default retention check prevents periods < 7 days
- Shorter periods can be forced but risk reader failures:

```python
# CAUTION: Only use shorter retention with full understanding of risks
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
```

### Impact of Vacuum on Time Travel

After vacuum, time travel queries to versions older than the retention period will fail. Plan retention periods based on your time travel requirements.

### Automated Vacuum via Table Maintenance API

Schedule regular vacuum operations using the Table Maintenance REST API in a pipeline or Spark Job Definition for consistent storage management.
