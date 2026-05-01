# Diagnostic Checklist for Fabric Spark Delta Lake Performance

Detailed remediate steps organized by symptom category. Use the [SKILL.md](../SKILL.md) Quick Diagnostic Workflow to identify which section to start with.

## Table of Contents

- [OOM Errors](#oom-errors)
- [Data Skew](#data-skew)
- [Shuffle Bottlenecks](#shuffle-bottlenecks)
- [Small File Problem](#small-file-problem)
- [Streaming Performance](#streaming-performance)
- [Query Performance on Read](#query-performance-on-read)

---

## OOM Errors

### Driver OOM

Driver OOM occurs when the Spark driver exceeds its allocated memory. The driver is a single JVM that coordinates the Spark application.

**Common causes:**

- Calling `collect()`, `toPandas()`, or `countByKey()` on large DataFrames
- Large broadcast variables exceeding driver memory
- Too many accumulated accumulator values
- Complex query plans with deep lineage

**Diagnostic steps:**

1. Search notebook code for `collect()`, `toPandas()`, `take(n)` with large n, or `countByKey()`
2. Check if broadcast joins are exceeding driver memory:
   ```python
   print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
   # Default is 10MB. If set very high, large tables may be broadcast
   ```
3. Review Spark UI > Executors tab for driver memory usage

**Remediation:**

```python
# WRONG: Pulling entire DataFrame to driver
results = df.collect()

# RIGHT: Use show() for inspection, write for persistence
df.show(20)
df.write.format("delta").saveAsTable("results_table")

# RIGHT: If you need pandas, limit the data first
pdf = df.limit(100000).toPandas()

# RIGHT: Increase driver memory if unavoidable
# Set in Environment > Compute > Spark driver memory
# Allowed values: 28g, 56g, 112g, 224g, 400g
```

### Executor OOM

Executor OOM occurs when a Spark executor (worker) exceeds its allocated memory during task execution.

**Common causes:**

- Wide joins or aggregations on large datasets causing excessive shuffle
- Cached/persisted datasets exceeding executor storage region
- Skewed partitions where one partition is much larger than others
- Insufficient executor memory for the data volume

**Diagnostic steps:**

1. Check Spark UI > Stages tab for failed tasks with OOM
2. Look for skew: large gap between median and max task times
3. Review memory configuration:
   ```python
   print(spark.conf.get("spark.executor.memory"))
   print(spark.conf.get("spark.memory.fraction", "0.6"))
   print(spark.conf.get("spark.memory.storageFraction", "0.5"))
   ```

**Remediation:**

```python
# Increase executor memory via Environment > Compute settings
# Allowed values: 28g, 56g, 112g, 224g, 400g

# Tune memory fractions if caching is heavy
spark.conf.set("spark.memory.fraction", "0.8")
spark.conf.set("spark.memory.storageFraction", "0.3")

# Reduce partition sizes to prevent per-task OOM
spark.conf.set("spark.sql.shuffle.partitions", "400")

# Unpersist cached DataFrames when no longer needed
df.unpersist()
```

---

## Data Skew

Data skew occurs when one or more partitions contain significantly more data than others, causing straggler tasks that hold up the entire stage.

**Symptoms in Spark UI:**

- A few tasks take 10x+ longer than the median task in a stage
- Large gap between median and max task duration in stage metrics
- Stages with disproportionate shuffle read/write for specific partitions

**Diagnostic steps:**

1. Open Spark UI > Jobs > click the slow stage
2. Review Task Metrics: compare median, 75th percentile, and max values
3. Check partition distribution for the join/group key:
   ```python
   from pyspark.sql import functions as F

   # Check distribution of the key column
   df.groupBy("join_key_column") \
     .agg(F.count("*").alias("row_count")) \
     .orderBy(F.desc("row_count")) \
     .show(20)

   # Check for null/empty keys (common skew source)
   null_count = df.filter(F.col("join_key_column").isNull()).count()
   print(f"Null key rows: {null_count}")
   ```

**Remediation:**

```python
# 1. Enable AQE skew join optimization (usually on by default)
spark.conf.set("spark.databricks.optimizer.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")

# 2. Key salting for severe skew on joins
from pyspark.sql import functions as F
import random

num_salt_buckets = 10

# Salt the skewed (large) table
df_large_salted = df_large.withColumn(
    "salt", (F.rand() * num_salt_buckets).cast("int")
)

# Explode the small table to match all salt values
df_small_exploded = df_small.crossJoin(
    spark.range(num_salt_buckets).withColumnRenamed("id", "salt")
)

# Join on original key + salt
result = df_large_salted.join(
    df_small_exploded,
    ["join_key", "salt"],
    "inner"
).drop("salt")

# 3. Filter out null keys before joining (process separately if needed)
df_nulls = df.filter(F.col("join_key").isNull())
df_valid = df.filter(F.col("join_key").isNotNull())

# 4. Repartition to increase parallelism
df_balanced = df.repartition(200, "join_key")

# 5. Use broadcast join for small lookup tables (< 100MB)
from pyspark.sql.functions import broadcast
result = df_large.join(broadcast(df_small), "join_key")
```

---

## Shuffle Bottlenecks

Shuffles move data across executors for joins, aggregations, and repartitioning. Excessive shuffling is the most common performance bottleneck.

**Symptoms:**

- Spark UI shows large Shuffle Read/Write sizes
- Stages with "Exchange" or "ShuffleExchange" operators dominate runtime
- Disk spill visible in Spark UI (Shuffle Spill Memory/Disk columns)

**Diagnostic steps:**

1. Open Spark UI > Stages tab
2. Sort by Duration to find the slowest stages
3. Check Shuffle Read/Write and Spill columns
4. Review the DAG visualization for Exchange operators

**Remediation:**

```python
# 1. Use broadcast joins for small tables (avoid shuffle entirely)
from pyspark.sql.functions import broadcast

# Increase broadcast threshold if small tables aren't being broadcast
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")

result = large_df.join(broadcast(small_df), "key")

# 2. Tune shuffle partitions
# Default is 200, which may be too few for large data or too many for small
spark.conf.set("spark.sql.shuffle.partitions", "auto")  # Let AQE decide
# Or set manually based on data volume:
# Rule of thumb: target ~128MB per partition after shuffle
# For 100GB shuffle: 100GB / 128MB ≈ 800 partitions
spark.conf.set("spark.sql.shuffle.partitions", "800")

# 3. Enable AQE partition coalescing (on by default)
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64m")

# 4. Apply column pruning and row filtering BEFORE joins
# WRONG: Join first, then filter
result = df_a.join(df_b, "key").filter("status = 'active'")

# RIGHT: Filter first, then join
df_a_filtered = df_a.filter("status = 'active'").select("key", "value")
result = df_a_filtered.join(df_b.select("key", "info"), "key")

# 5. Use Optimized Write to reduce post-write file shuffling
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
```

---

## Small File Problem

The small file problem occurs when a Delta table accumulates many files much smaller than the optimal 128MB–1GB target. This causes metadata overhead, slow reads, and excessive task scheduling.

**Causes:**

- Frequent small appends (especially from streaming)
- Over-partitioning with `partitionBy()` on high-cardinality columns
- UPDATE/DELETE operations creating new small Parquet files
- Optimized Write disabled

**Diagnostic steps:**

```python
# Check file count and average size
detail = spark.sql("DESCRIBE DETAIL schema_name.table_name")
detail.select("numFiles", "sizeInBytes").show()

# Calculate average file size
row = detail.first()
avg_mb = (row["sizeInBytes"] / row["numFiles"]) / (1024 * 1024)
print(f"Average file size: {avg_mb:.1f} MB")
print(f"Total files: {row['numFiles']}")

# Target: 128MB-1GB average, <1000 files for tables under 10GB
if avg_mb < 32:
    print("WARNING: Small file problem detected. Run OPTIMIZE.")
if row["numFiles"] > 1000 and row["sizeInBytes"] < 10 * 1024**3:
    print("WARNING: Too many files for table size. Run OPTIMIZE.")
```

**Remediation:**

See [table-maintenance-guide.md](./table-maintenance-guide.md#optimize-command) for detailed OPTIMIZE instructions.

Quick fix:

```sql
%%sql
-- Basic OPTIMIZE (bin-compaction)
OPTIMIZE schema_name.table_name;

-- OPTIMIZE with V-Order for read performance
OPTIMIZE schema_name.table_name VORDER;

-- OPTIMIZE specific partition only
OPTIMIZE schema_name.table_name WHERE date_key = '2025-01-15' VORDER;
```

**Prevention:**

```python
# Enable Optimized Write to prevent small files during writes
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# For streaming: use trigger intervals to batch events
stream.writeStream \
    .format("delta") \
    .trigger(processingTime="1 minute") \
    .toTable("target_table")
```

---

## Streaming Performance

Streaming performance issues manifest as increasing processing latency, growing batch durations, or checkpoint failures.

**Diagnostic steps:**

1. Check Structured Streaming UI metrics:
   - Input Rate vs Process Rate (process should keep up with input)
   - Batch Duration trend (should be stable, not increasing)
   - Operation Duration breakdown (where time is spent)

2. Check partition alignment:
   ```python
   # Event Hubs partitions should align with Spark parallelism
   # If Event Hub has 32 partitions, Spark should have >= 32 cores
   print(f"Executor cores: {spark.conf.get('spark.executor.cores')}")
   print(f"Num executors: {spark.conf.get('spark.executor.instances', 'dynamic')}")
   ```

3. Check for small file accumulation in the Delta sink table

**Remediation:**

```python
# 1. Use appropriate trigger interval to batch events
# Too frequent = many small files; too infrequent = high latency
stream = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .toTable("target_table")

# 2. Match memory partitions to Event Hub partitions
# If Event Hub has 48 partitions:
df_repartitioned = df.repartition(48)

# 3. Use Optimized Write instead of manual repartition + partitionBy
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
stream = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .outputMode("append") \
    .partitionBy("date_column") \
    .toTable("target_table")

# 4. Enable retry policy for resilience
# Configure in Spark Job Definition settings:
# - Max retries: set based on tolerance
# - Retry interval: time between restarts
```

---

## Query Performance on Read

Slow read queries on Delta tables are commonly caused by suboptimal file layout, missing V-Order, or poor partitioning.

**Diagnostic steps:**

1. Check if V-Order is applied:
   ```python
   print(spark.conf.get("spark.sql.parquet.vorder.default", "false"))
   # Check table property
   spark.sql("SHOW TBLPROPERTIES schema_name.table_name").show()
   ```

2. Check file statistics and sizes (see Small File Problem section)

3. Verify the query is leveraging partition pruning:
   ```python
   # Check the physical plan for PartitionFilters
   df.filter("date_key = '2025-01-15'").explain(True)
   ```

4. Check if the table would benefit from Z-Order on filter columns

**Remediation:**

```python
# 1. Switch to a read-optimized resource profile
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")

# 2. Enable V-Order on the table
spark.sql("""
    ALTER TABLE schema_name.table_name
    SET TBLPROPERTIES('delta.parquet.vorder.enabled' = 'true')
""")

# 3. Run OPTIMIZE with V-Order and Z-Order on frequently filtered columns
spark.sql("""
    OPTIMIZE schema_name.table_name
    ZORDER BY (customer_id, transaction_date)
    VORDER
""")

# 4. Use predicate pushdown — filter early in the query
# WRONG
df = spark.table("big_table").join(other, "key").filter("status = 'A'")

# RIGHT
df = spark.table("big_table").filter("status = 'A'").join(other, "key")

# 5. Enable Native Execution Engine for compatible workloads
# Set in Environment > Spark settings > enable_native_execution_engine = true
```
