# Spark Configuration Tuning Reference

## Table of Contents

- [Capacity and Concurrency](#capacity-and-concurrency)
- [Shuffle Optimization](#shuffle-optimization)
- [Data Skew Resolution](#data-skew-resolution)
- [Spark SQL Tuning](#spark-sql-tuning)
- [Pool and Executor Sizing](#pool-and-executor-sizing)
- [Partitioning Strategy](#partitioning-strategy)
- [Resource Profiles Deep Dive](#resource-profiles-deep-dive)
- [Autotune Configuration](#autotune-configuration)

---

## Capacity and Concurrency

### Understanding Fabric Spark VCores

Every Fabric Capacity Unit (CU) provides 2 Apache Spark VCores:

| Fabric SKU | Spark VCores | Max Queue Depth |
|------------|-------------|-----------------|
| F2         | 4           | 4               |
| F4         | 8           | 4               |
| F8         | 16          | 8               |
| F16        | 32          | 16              |
| F32        | 64          | 32              |
| F64 (P1)   | 128         | 64              |
| F128 (P2)  | 256         | 128             |
| F256 (P3)  | 512         | 256             |
| F512 (P4)  | 1024        | 512             |
| Trial      | 128         | N/A (no queue)  |

### Diagnosing HTTP 430 Throttling

When all VCores are consumed, new jobs receive HTTP 430. Steps to resolve:

1. Open Monitoring Hub in the Fabric portal.
2. Filter by status "In Progress" to see active Spark applications.
3. Identify long-running or idle sessions consuming VCores.
4. Cancel unnecessary sessions or wait for queue processing.
5. If persistent, consider upgrading to a larger Fabric SKU.

### Optimistic Job Admission

With autoscale enabled, Fabric admits jobs at minimum node configuration (1 node = 8 VCores for Medium size). This allows significantly more concurrent jobs. For an F32 capacity (192 VCores with 3x burst), up to 24 concurrent jobs can be admitted versus only 3 without optimistic admission.

Enable autoscale on custom pools to maximize concurrency:

1. Workspace Settings → Data Engineering/Science → Spark Settings
2. Select your custom pool → Enable autoscaling
3. Set minimum nodes to 1 for maximum admission flexibility

---

## Shuffle Optimization

### Identifying Shuffle Bottlenecks

Open Spark UI → Stages tab. Look for stages with:

- High "Shuffle Read" or "Shuffle Write" values (multiple GB)
- Task count of exactly 200 (indicates default `shuffle.partitions`)
- Significant time gap between median and max task duration

### Tuning spark.sql.shuffle.partitions

The default of 200 is rarely optimal. Calculate a better value:

```python
# Rule of thumb: 2-3x total executor cores
total_cores = spark.sparkContext.defaultParallelism
optimal_partitions = total_cores * 2

spark.conf.set("spark.sql.shuffle.partitions", str(optimal_partitions))
```

**Guidelines by data volume:**

| Data Volume per Stage | Recommended Partitions |
|-----------------------|----------------------|
| < 1 GB               | 20-50                |
| 1-10 GB              | 100-200              |
| 10-100 GB            | 200-500              |
| 100 GB - 1 TB        | 500-2000             |
| > 1 TB               | 2000-4000            |

Target approximately 128-256 MB per partition after shuffle.

### Broadcast Join Optimization

When one side of a join is small, broadcast it to avoid shuffle entirely:

```python
# Increase broadcast threshold (default 10 MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "268435456")  # 256 MB

# Or use explicit broadcast hint in SQL
# SELECT /*+ BROADCAST(small_table) */ * FROM large_table JOIN small_table ...

# Or in PySpark
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

**Warning**: Broadcasting tables larger than available executor memory causes OOM errors. Monitor executor memory in the Resources tab.

---

## Data Skew Resolution

### Detecting Skew

The Fabric Spark Advisor automatically detects skew in notebook cells (Runtime 3.4+). You can also detect it manually:

```python
# Check value distribution of join/group key
df.groupBy("join_key").count().orderBy(F.desc("count")).show(20)

# Look for values with >10x the average count
```

In Spark UI, skew appears as one task taking much longer than others in the same stage.

### Resolution Strategies

**Strategy 1: Salting (for joins)**

```python
import pyspark.sql.functions as F

# Add salt to skewed key
salt_buckets = 10
skewed_df = skewed_df.withColumn(
    "salted_key",
    F.concat(F.col("join_key"), F.lit("_"), (F.rand() * salt_buckets).cast("int"))
)

# Explode the other side to match
other_df_exploded = other_df.crossJoin(
    spark.range(salt_buckets).withColumnRenamed("id", "salt")
).withColumn(
    "salted_key",
    F.concat(F.col("join_key"), F.lit("_"), F.col("salt"))
)

# Join on salted key
result = skewed_df.join(other_df_exploded, "salted_key")
```

**Strategy 2: Broadcast the smaller side**

If the non-skewed table fits in memory, broadcast it to eliminate the shuffle entirely. See the broadcast join section above.

**Strategy 3: Isolate and union**

```python
# Process skewed keys separately
skewed_keys = ["key_with_millions_of_rows"]
skewed_part = df.filter(F.col("join_key").isin(skewed_keys))
normal_part = df.filter(~F.col("join_key").isin(skewed_keys))

# Process each partition with appropriate strategy
result = normal_part.join(other_df, "join_key").unionByName(
    skewed_part.join(broadcast(other_df), "join_key")
)
```

---

## Spark SQL Tuning

### Adaptive Query Execution (AQE)

AQE is enabled by default in Fabric and handles many optimizations automatically:

- Coalesces small post-shuffle partitions
- Converts sort-merge joins to broadcast joins at runtime
- Optimizes skew joins

Verify AQE is active:

```python
print(spark.conf.get("spark.sql.adaptive.enabled"))  # Should be "true"
```

### Predicate Pushdown

Ensure filters are pushed down to the scan level:

```python
# Good: Filter before join (predicate pushdown)
filtered = large_table.filter(F.col("date") >= "2025-01-01")
result = filtered.join(dim_table, "key")

# Check physical plan for PushedFilters
result.explain(True)
```

### Column Pruning

Select only needed columns early in the pipeline to reduce I/O:

```python
# Good: Select needed columns early
df = spark.read.table("sales").select("order_id", "amount", "date")

# Bad: Read all columns then filter late
df = spark.read.table("sales")  # Reads all 50 columns
# ... many transformations later ...
result = df.select("order_id", "amount")
```

### Caching Strategy

Cache intermediate results that are reused multiple times:

```python
# Cache a filtered dataset used in multiple downstream operations
base_df = spark.read.table("large_table").filter(F.col("active") == True)
base_df.cache()
base_df.count()  # Materialize the cache

# Now use base_df in multiple operations
agg1 = base_df.groupBy("region").sum("amount")
agg2 = base_df.groupBy("product").avg("amount")

# Unpersist when done
base_df.unpersist()
```

---

## Pool and Executor Sizing

### Starter Pools vs Custom Pools

| Feature | Starter Pool | Custom Pool |
|---------|-------------|-------------|
| Session start | 5-10 seconds | Depends on node allocation |
| Node size | Fixed (Medium) | Configurable (Small to XXLarge) |
| Autoscale | Default behavior | Configurable min/max nodes |
| Use case | Development, ad-hoc | Production workloads |

### Right-Sizing Custom Pools

1. Start with Medium nodes (8 VCores, 56 GB per node).
2. Set min nodes to 1, max nodes based on capacity headroom.
3. Monitor executor utilization in the Resources tab.
4. If executors are consistently >80% idle, reduce max nodes.
5. If jobs queue frequently, increase max nodes or upgrade SKU.

### Driver vs Executor Memory

For jobs that collect large results to the driver:

```python
# Increase driver memory for collect() or toPandas() operations
# Set in Environment Spark Compute configuration:
# spark.driver.memory = 8g (or higher)

# Better approach: avoid collect() on large datasets
# Use .write instead of .collect() for large outputs
```

---

## Partitioning Strategy

### In-Memory Partitioning

```python
# repartition() - creates specified number of partitions (full shuffle)
df = df.repartition(48)  # Match to total CPU cores

# coalesce() - reduces partitions without full shuffle (more efficient)
df = df.coalesce(10)  # Use when reducing partition count

# repartition by column for subsequent operations on that column
df = df.repartition("customer_id")
```

### Disk Partitioning with partitionBy

```python
# Partition on disk by column(s) with good cardinality
df.write.format("delta") \
    .partitionBy("year", "month") \
    .mode("overwrite") \
    .saveAsTable("partitioned_table")
```

**Avoid over-partitioning**: If a partition column has >10,000 distinct values, the resulting small files degrade read performance.

### Combined Strategy for High Throughput

```python
# Combine in-memory and disk partitioning
df.repartition(48) \
    .write.format("delta") \
    .option("checkpointLocation", "Files/checkpoint") \
    .partitionBy("region", "date") \
    .mode("append") \
    .saveAsTable("events")
```

---

## Resource Profiles Deep Dive

### Applying Resource Profiles

**At the workspace level** (affects all new environments):

1. Go to Workspace Settings → Data Engineering/Science → Spark Settings
2. Select the desired resource profile

**At the environment level**:

```python
# Set in Environment Spark Properties before publishing
# spark.fabric.resource.profile = readHeavyForSpark
```

**Per-session override**:

```python
spark.conf.set("spark.fabric.resource.profile", "writeHeavy")
```

### When to Change Profiles

| Current Profile | Switch To | When |
|----------------|-----------|------|
| writeHeavy (default) | readHeavyForSpark | Interactive analytics notebooks with frequent reads |
| writeHeavy | readHeavyForPBI | Tables primarily consumed by Power BI DirectLake |
| readHeavyForSpark | writeHeavy | Batch ETL pipelines with heavy ingestion |

### VOrder Considerations

VOrder is Fabric's columnar optimization for read performance. Key facts:

- **Disabled by default** on new workspaces (writeHeavy profile)
- Enable manually for read-optimized tables: `spark.sql.parquet.vorder.default = true`
- Apply retroactively via table maintenance (bin-compaction with VOrder)
- Adds write overhead (~10-20% slower writes) but significantly improves read performance

---

## Autotune Configuration

### Enabling Autotune

**Via Environment (recommended for production)**:

1. Open Environment → Spark Compute → Spark Properties
2. Add: `spark.ms.autotune.enabled = true`
3. Publish the environment

**Via Notebook (for testing)**:

```python
spark.conf.set("spark.ms.autotune.enabled", "true")
```

### Autotune Limitations

- Compatible only with Runtime 1.1 and 1.2
- Cannot be used with high concurrency mode
- Cannot be used with private endpoints
- Only tunes read-only queries (not write operations)
- Queries must run for at least 15 seconds
- Requires 20-25 iterations to converge

### Interpreting Autotune Status

After running a query, check the Spark UI SQL tab for autotune status:

| Status | Meaning | Action |
|--------|---------|--------|
| QUERY_TUNING_SUCCEED | Optimal settings applied | None needed |
| QUERY_TUNING_DISABLED | Autotune is off | Enable in environment |
| QUERY_PATTERN_NOT_MATCH | Not a read-only query | Autotune only works for reads |
| QUERY_DURATION_TOO_SHORT | Query < 15 seconds | No tuning needed for fast queries |

### Manual Fallback Settings

If autotune is not available, use these as starting points:

```python
# For read-heavy analytical queries
spark.conf.set("spark.sql.shuffle.partitions", "auto")  # AQE handles it
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "268435456")  # 256 MB
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128 MB

# For write-heavy ETL jobs
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")  # 10 MB
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```
