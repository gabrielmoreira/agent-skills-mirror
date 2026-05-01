# Memory & Compute Tuning

## Table of Contents

- [Common Memory Errors](#common-memory-errors)
- [Understanding Fabric Spark Node Sizes](#understanding-fabric-spark-node-sizes)
- [Diagnosing OOM Errors](#diagnosing-oom-errors)
- [Fixing Memory Issues](#fixing-memory-issues)
- [Executor and Driver Sizing](#executor-and-driver-sizing)

## Common Memory Errors

| Error Pattern | Meaning |
|--------------|---------|
| `java.lang.OutOfMemoryError: Java heap space` | Executor JVM heap exhausted |
| `java.lang.OutOfMemoryError: GC overhead limit` | Too much time in garbage collection |
| `Container killed by YARN for exceeding memory limits` | Total executor memory (heap + overhead) exceeded |
| `ExecutorLostFailure` | Executor crashed, often from OOM |
| `Task failed, broadcast timeout` | Driver OOM during broadcast join |
| `SparkException: Job aborted due to stage failure` | Multiple task OOMs caused stage failure |

## Understanding Fabric Spark Node Sizes

Environment compute settings determine available memory per executor.

### Allowed Configurations

| Setting | Allowed Values |
|---------|---------------|
| Driver cores | 4, 8, 16, 32, 64 |
| Driver memory | 28g, 56g, 112g, 224g, 400g |
| Executor cores | 4, 8, 16, 32, 64 |
| Executor memory | 28g, 56g, 112g, 224g, 400g |

These must fit within the node size of the selected pool. For a Large node (16 VCores),
driver/executor cores can be 4, 8, or 16, and memory up to 112g.

### SKU to Node Size Mapping

| SKU | Capacity Units | VCores | Node Size | Default Max Nodes |
|-----|---------------|--------|-----------|------------------|
| F2 | 2 | 4 | Medium | 1 |
| F4 | 4 | 8 | Medium | 1 |
| F8 | 8 | 16 | Medium | 2 |
| F16 | 16 | 32 | Medium | 4 |
| F32 | 32 | 64 | Medium | 8 |
| F64 | 64 | 128 | Medium | 16 |

## Diagnosing OOM Errors

### Step 1: Check the Spark UI

Navigate to the failed stage in Spark UI. Look at:
- **Task metrics**: Peak memory per task
- **Shuffle Read/Write**: Excessive shuffle indicates partition skew
- **Task duration variance**: 1 task taking 100x longer = data skew

### Step 2: Identify Data Skew

```python
# Check partition sizes for skew
df = spark.read.format("delta").load("Tables/your_table")

from pyspark.sql import functions as F

# Add partition ID and count rows per partition
df.withColumn("part_id", F.spark_partition_id()) \
  .groupBy("part_id") \
  .count() \
  .agg(
      F.min("count").alias("min_rows"),
      F.max("count").alias("max_rows"),
      F.avg("count").alias("avg_rows"),
      F.stddev("count").alias("stddev_rows")
  ).show()
```

If `max_rows` is 10x+ larger than `avg_rows`, you have data skew.

### Step 3: Check Broadcast Join Threshold

```python
# Current broadcast threshold (default 10MB)
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
```

If a table larger than this threshold is being broadcast, the driver may OOM.

## Fixing Memory Issues

### Increase Executor Memory

Configure in the environment Spark compute settings:

1. Navigate to the attached Environment
2. Open Compute section
3. Increase Spark executor memory to the next tier (28g → 56g → 112g)
4. Publish the environment

### Fix Data Skew

```python
# Option 1: Salting technique for skewed joins
from pyspark.sql import functions as F

salt_range = 10
large_df = large_df.withColumn("salt", (F.rand() * salt_range).cast("int"))
small_df = small_df.crossJoin(
    spark.range(salt_range).withColumnRenamed("id", "salt")
)
result = large_df.join(small_df, ["join_key", "salt"])
result = result.drop("salt")

# Option 2: Enable AQE skew join optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

### Reduce Broadcast Join Size

```python
# Disable broadcast for large tables
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

# Or increase threshold if driver has enough memory
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50m")
```

### Enable Dynamic Executor Allocation

Configure in environment to automatically scale executors based on workload:

```python
spark.conf.set("spark.dynamicAllocation.enabled", "true")
spark.conf.set("spark.dynamicAllocation.minExecutors", "1")
spark.conf.set("spark.dynamicAllocation.maxExecutors", "15")
```

## Executor and Driver Sizing

### Guidelines

| Workload Type | Recommended Executor Memory | Executor Cores |
|--------------|---------------------------|----------------|
| Light ETL (< 10 GB) | 28g | 4 |
| Medium ETL (10–100 GB) | 56g | 8 |
| Heavy ETL (100+ GB) | 112g | 16 |
| ML training (large datasets) | 112g–224g | 16–32 |
| Interactive queries | 28g–56g | 4–8 |

### Driver Sizing

The driver needs enough memory to:
- Collect results (`df.collect()`, `df.toPandas()`)
- Hold broadcast tables
- Manage job metadata

Rule of thumb: Driver memory >= largest broadcast table + 2x overhead for results.
Avoid `collect()` on large datasets — use `limit()` or write to table instead.
