---
name: spark-optimization
description: "Tunes Apache Spark 3 jobs: Adaptive Query Execution, 128-256MB partitions, Kryo, shuffle coalescing, skew joins, cache vs persist, and Spark UI stage diagnosis. Use when jobs are slow, skewed, or OOMing executors. Not for Polars/pandas in-memory frames, teaching Spark from zero, or GPU LLM serving (vllm)."
version: 1.0.1
risk: unknown
source: community
date_added: "2026-02-27"
---

# Apache Spark Optimization

Production patterns for optimizing Apache Spark jobs including partitioning strategies, memory management, shuffle optimization, and performance tuning.

## When to Use

Use this skill when:
- Optimizing slow Spark jobs
- Tuning memory and executor configuration
- Implementing efficient partitioning strategies
- Debugging Spark performance issues
- Scaling Spark pipelines for large datasets
- Reducing shuffle and data skew

Do **not** use this skill when:
- The task is unrelated to Apache Spark optimization
- You need a different domain or tool outside this scope

## Prerequisites

- Apache Spark 3.0+ (AQE features require Spark 3.0+; skew join requires 3.1+)
- PySpark or Scala Spark API access
- Spark UI accessible (default port 4040 for running apps, 18080 for history server)
- Windows host is primary (PowerShell). When running Spark locally on Windows, ensure `winutils.exe` is present in a Hadoop home directory (e.g., `C:\hadoop\bin\winutils.exe`) and set `$env:HADOOP_HOME="C:\hadoop"` in PowerShell before launching Spark.
- If detailed examples are required, open `resources/implementation-playbook.md` for extended walkthroughs and code samples.

## Procedure

### 1. Establish an Optimized Spark Session

Always start with Adaptive Query Execution (AQE), Kryo serialization, and appropriate shuffle partitions enabled.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (SparkSession.builder
    .appName("OptimizedJob")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate())
```

### 2. Right-Size Partitions

Target 128MB–256MB per partition. Too few partitions cause under-utilization and memory pressure; too many cause task scheduling overhead.

```python
def calculate_partitions(data_size_gb: float, partition_size_mb: int = 128) -> int:
    return max(int(data_size_gb * 1024 / partition_size_mb), 1)

# Repartition for even distribution (triggers shuffle)
df_repartitioned = df.repartition(200, "partition_key")

# Coalesce to reduce partitions (no shuffle)
df_coalesced = df.coalesce(100)
```

Use partition pruning with predicate pushdown when reading partitioned data:

```python
df = (spark.read.parquet("s3://bucket/data/")
    .filter(F.col("date") == "2024-01-01"))  # Spark pushes this down
```

Write with partitioning for future query efficiency:

```python
(df.write
    .partitionBy("year", "month", "day")
    .mode("overwrite")
    .parquet("s3://bucket/partitioned_output/"))
```

### 3. Optimize Joins

**Broadcast Join** — use when one side is small (< 10MB by default, configurable via `spark.sql.autoBroadcastJoinThreshold`):

```python
result = large_df.join(
    F.broadcast(small_df),
    on="key",
    how="left"
)
```

**Sort-Merge Join** — default for large-to-large joins. Requires shuffle but handles any size.

**Bucket Join** — pre-sorted, no shuffle at join time:

```python
(df.write
    .bucketBy(200, "customer_id")
    .sortBy("customer_id")
    .mode("overwrite")
    .saveAsTable("bucketed_orders"))

# Join bucketed tables (no shuffle!)
orders = spark.table("bucketed_orders")
customers = spark.table("bucketed_customers")  # Same bucket count
result = orders.join(customers, on="customer_id")
```

**Skew Join Handling** — enable AQE skew join optimization:

```python
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

For severe skew, apply manual salting:

```python
def salt_join(df_skewed, df_other, key_col, num_salts=10):
    df_salted = df_skewed.withColumn(
        "salt",
        (F.rand() * num_salts).cast("int")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    df_exploded = df_other.crossJoin(
        spark.range(num_salts).withColumnRenamed("id", "salt")
    ).withColumn(
        "salted_key",
        F.concat(F.col(key_col), F.lit("_"), F.col("salt"))
    )

    return df_salted.join(df_exploded, on="salted_key", how="inner")
```

### 4. Cache and Persist Strategically

Cache only when a DataFrame is reused multiple times. Always materialize with an action after caching.

```python
from pyspark import StorageLevel

df_filtered = df.filter(F.col("status") == "active")
df_filtered.cache()
df_filtered.count()  # Force materialization

# Use in multiple actions
agg1 = df_filtered.groupBy("category").count()
agg2 = df_filtered.groupBy("region").sum("amount")

df_filtered.unpersist()  # Release when done
```

Storage levels:
- `MEMORY_ONLY` — Fast, but may not fit
- `MEMORY_AND_DISK` — Spills to disk if needed (recommended default)
- `MEMORY_ONLY_SER` — Serialized, less memory, more CPU
- `DISK_ONLY` — When memory is tight
- `OFF_HEAP` — Tungsten off-heap memory

For complex lineages, use checkpointing to break the DAG:

```python
spark.sparkContext.setCheckpointDir("s3://bucket/checkpoints/")
df_complex = (df.join(other_df, "key").groupBy("category").agg(F.sum("amount")))
df_complex.checkpoint()  # Breaks lineage, materializes
```

### 5. Tune Memory

Executor memory breakdown (8GB executor example):
- `spark.memory.fraction = 0.6` → 60% (4.8GB) for execution + storage
  - `spark.memory.storageFraction = 0.5` → 50% of 4.8GB (2.4GB) for cache
  - Remaining 2.4GB for execution (shuffles, joins, sorts)
- 40% (3.2GB) for user data structures and internal metadata

```python
spark = (SparkSession.builder
    .config("spark.executor.memory", "8g")
    .config("spark.executor.memoryOverhead", "2g")  # For non-JVM memory
    .config("spark.memory.fraction", "0.6")
    .config("spark.memory.storageFraction", "0.5")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.autoBroadcastJoinThreshold", "50MB")
    .config("spark.sql.files.maxPartitionBytes", "128MB")
    .getOrCreate())
```

### 6. Optimize Shuffles

```python
spark.conf.set("spark.sql.shuffle.partitions", "auto")  # With AQE
spark.conf.set("spark.shuffle.compress", "true")
spark.conf.set("spark.shuffle.spill.compress", "true")
spark.conf.set("spark.io.compression.codec", "lz4")  # Fast compression
```

Pre-aggregate before shuffle (combiner pattern):

```python
df_optimized = (df
    .groupBy("key", "partition_col")
    .agg(F.sum("value").alias("partial_sum"))
    .groupBy("key")
    .agg(F.sum("partial_sum").alias("total")))
```

Use approximate distinct to avoid shuffle:

```python
# BAD: Shuffle for each distinct
distinct_count = df.select("category").distinct().count()

# GOOD: Approximate distinct (no shuffle)
approx_count = df.select(F.approx_count_distinct("category")).collect()[0][0]
```

### 7. Optimize Data Formats

```python
# Parquet with Snappy compression and 128MB row groups
(df.write
    .option("compression", "snappy")
    .option("parquet.block.size", 128 * 1024 * 1024)
    .parquet("s3://bucket/output/"))

# Column pruning - only read needed columns
df = (spark.read.parquet("s3://bucket/data/")
    .select("id", "amount", "date"))

# Delta Lake optimizations
(df.write
    .format("delta")
    .option("optimizeWrite", "true")
    .option("autoCompact", "true")
    .mode("overwrite")
    .save("s3://bucket/delta_table/"))

# Z-ordering for multi-dimensional queries
spark.sql("""
    OPTIMIZE delta.`s3://bucket/delta_table/`
    ZORDER BY (customer_id, date)
""")
```

### 8. Monitor and Debug

```python
# Explain query plan
df.explain(mode="extended")  # Modes: simple, extended, codegen, cost, formatted
df.explain(mode="cost")      # Physical plan statistics

# Check for partition skew
def check_partition_skew(df):
    partition_counts = (df
        .withColumn("partition_id", F.spark_partition_id())
        .groupBy("partition_id")
        .count()
        .orderBy(F.desc("count")))

    partition_counts.show(20)

    stats = partition_counts.select(
        F.min("count").alias("min"),
        F.max("count").alias("max"),
        F.avg("count").alias("avg"),
        F.stddev("count").alias("stddev")
    ).collect()[0]

    skew_ratio = stats["max"] / stats["avg"]
    print(f"Skew ratio: {skew_ratio:.2f}x (>2x indicates skew)")
```

### 9. Production Configuration Template

```python
spark_configs = {
    # Adaptive Query Execution (AQE)
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",

    # Memory
    "spark.executor.memory": "8g",
    "spark.executor.memoryOverhead": "2g",
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.5",

    # Parallelism
    "spark.sql.shuffle.partitions": "200",
    "spark.default.parallelism": "200",

    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    "spark.sql.execution.arrow.pyspark.enabled": "true",

    # Compression
    "spark.io.compression.codec": "lz4",
    "spark.shuffle.compress": "true",

    # Broadcast
    "spark.sql.autoBroadcastJoinThreshold": "50MB",

    # File handling
    "spark.sql.files.maxPartitionBytes": "128MB",
    "spark.sql.files.openCostInBytes": "4MB",
}
```

## Pitfalls

- **Don't collect large data** — `collect()` pulls all data to the driver. Use `take(n)`, `limit(n)`, or write to distributed storage instead.
- **Don't use UDFs unnecessarily** — UDFs bypass Catalyst optimization and codegen. Use built-in Spark SQL functions wherever possible.
- **Don't over-cache** — Caching consumes memory. Only cache DataFrames reused multiple times, and always `unpersist()` when done.
- **Don't ignore data skew** — A single skewed partition can dominate job time. Check skew ratio with `check_partition_skew()`; ratios > 2x indicate skew.
- **Don't use `.count()` for existence checks** — Use `.take(1)` or `.isEmpty()` instead; `count()` forces a full scan.
- **Don't use `repartition()` when `coalesce()` suffices** — `repartition()` always triggers a shuffle; `coalesce()` reduces partitions without one.
- **Don't use `mergeSchema` by default** — Set `mergeSchema` to `false` unless you explicitly need schema merging; it adds overhead.
- **Windows `winutils.exe` missing** — On Windows hosts, Spark will fail to start without `winutils.exe` in `$env:HADOOP_HOME\bin`. Verify before launching.
- **Forgetting to materialize after cache** — `.cache()` is lazy. Without an action like `.count()`, nothing is actually cached.
- **Checkpoint directory not set** — Calling `.checkpoint()` without `setCheckpointDir()` will fail. Set a distributed filesystem path.

## Verification

1. **Verify AQE is enabled:**
   ```python
   print(spark.conf.get("spark.sql.adaptive.enabled"))  # Should print: true
   ```

2. **Verify partition skew is within bounds:**
   ```python
   check_partition_skew(df)  # Skew ratio should be < 2x
   ```

3. **Verify query plan uses expected join strategy:**
   ```python
   df.explain(mode="extended")
   # Look for BroadcastHashJoin, SortMergeJoin, or BucketedHashJoin in the plan
   ```

4. **Verify no excessive spills or GC via Spark UI:**
   - Open Spark UI at `http://<driver-host>:4040`
   - Check Stage > Task metrics for spill (memory) and spill (disk) columns
   - Check Executors tab for GC time; sustained high GC indicates memory pressure

5. **Verify caching is active:**
   ```python
   df_filtered.count()  # Materialize
   # In Spark UI > Storage tab, confirm the DataFrame is cached with expected size
   ```

6. **Verify Kryo serializer is active:**
   ```python
   print(spark.conf.get("spark.serializer"))
   # Should print: org.apache.spark.serializer.KryoSerializer
   ```

## Related Skills

- For extended walkthroughs and detailed code examples, open `resources/implementation-playbook.md`.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
