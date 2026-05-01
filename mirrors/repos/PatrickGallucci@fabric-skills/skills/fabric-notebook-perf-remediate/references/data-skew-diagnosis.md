# Data Skew Diagnosis and Resolution

Guide for identifying, analyzing, and resolving data skew in Microsoft Fabric Spark notebooks.

## Table of Contents

- [What is Data Skew](#what-is-data-skew)
- [Diagnosing Skew](#diagnosing-skew)
- [Resolution Strategies](#resolution-strategies)
- [AQE Skew Join Optimization](#aqe-skew-join-optimization)
- [Manual Salting Technique](#manual-salting-technique)
- [Repartitioning Strategies](#repartitioning-strategies)

## What is Data Skew

Data skew occurs when one or more partitions contain significantly more data than others, leading to imbalanced workloads. Time skew arises when certain tasks take substantially longer due to data skew or computational complexity differences.

Partitions are the fundamental units of parallelism in Spark. When you partition 1 GB of data into 100 partitions, Spark processes these concurrently as separate tasks up to the number of available CPU cores.

**Key principle:** For optimal performance, data must be evenly distributed across partitions. However, too many partitions introduce overhead from task scheduling and shuffle operations.

## Diagnosing Skew

### Method 1: Spark Job UI Progress Bar

The in-notebook Spark job progress indicator shows task-level metrics. Look for:

- One or two tasks running significantly longer than others
- Large gap between mean and max task duration
- A stage that appears "stuck" at 99%

### Method 2: Spark UI Task Aggregation Metrics

Navigate to the Spark UI from the Monitoring Hub. Check the task aggregation metrics for each stage:

| Metric | Healthy | Skewed |
|--------|---------|--------|
| Median vs Max duration | Within 2x | Max is 5x+ of median |
| 75th percentile vs Max | Similar | Large gap |
| Input size distribution | Even | One task has 10x+ data |
| Shuffle read/write | Balanced | One partition dominates |

If a significant gap exists between the median, 75th percentile, and max metrics, skew is likely present. If that stage takes significant time and skew is significant, remediation is warranted.

### Method 3: Code-Level Inspection

```python
# Check partition sizes
from pyspark.sql.functions import spark_partition_id, count

df.groupBy(spark_partition_id().alias("partition_id")) \
  .agg(count("*").alias("row_count")) \
  .orderBy("row_count", ascending=False) \
  .show(20)
```

```python
# Check value distribution for join/group-by columns
df.groupBy("join_key_column") \
  .count() \
  .orderBy("count", ascending=False) \
  .show(20)
```

## Resolution Strategies

### Strategy 1: Enable AQE (Recommended First Step)

Adaptive Query Execution handles skew automatically at runtime.

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")
```

AQE detects skewed partitions during shuffle and splits them automatically.

### Strategy 2: Broadcast Join for Small Tables

If one side of a join is small enough to fit in memory, use a broadcast join to eliminate shuffle entirely.

```python
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "key_column")
```

```python
# Increase broadcast threshold (default 10 MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")
```

### Strategy 3: Salting

For joins where both sides are large and one key is heavily skewed:

```python
from pyspark.sql.functions import col, lit, rand, explode, array, concat

SALT_BUCKETS = 10

# Salt the skewed (large) side
skewed_df = skewed_df.withColumn(
    "salt", (rand() * SALT_BUCKETS).cast("int")
).withColumn(
    "salted_key", concat(col("join_key"), lit("_"), col("salt"))
)

# Explode the non-skewed (smaller) side
salt_array = array([lit(i) for i in range(SALT_BUCKETS)])
other_df = other_df.withColumn(
    "salt", explode(salt_array)
).withColumn(
    "salted_key", concat(col("join_key"), lit("_"), col("salt"))
)

# Join on salted key
result = skewed_df.join(other_df, "salted_key")

# Drop salt columns
result = result.drop("salt", "salted_key")
```

### Strategy 4: Repartitioning

Force even distribution before expensive operations:

```python
# Repartition by a high-cardinality column
df = df.repartition(200, "high_cardinality_column")

# Repartition to a specific number of even partitions
df = df.repartition(200)
```

### Strategy 5: Filter Before Join

Reduce data volume before shuffle-heavy operations:

```python
# Apply filters and column pruning BEFORE joins
filtered_df = raw_df \
    .select("key", "value1", "value2") \
    .filter(col("date") >= "2024-01-01")

result = filtered_df.join(lookup_df, "key")
```

## AQE Skew Join Optimization

When AQE detects a skewed partition during a sort-merge join, it:

1. Identifies partitions exceeding the skew threshold
2. Splits the skewed partition into smaller sub-partitions
3. Replicates the corresponding partition from the other side
4. Processes sub-joins in parallel

**Configuration:**

- `skewedPartitionFactor` (default 5): A partition is skewed if its size is more than this factor times the median partition size
- `skewedPartitionThresholdInBytes` (default 256 MB): Minimum size for a partition to be considered skewed

## Repartitioning Strategies

| Method | Shuffle | Use Case |
|--------|---------|----------|
| `repartition(n)` | Full shuffle | Increase parallelism, even distribution |
| `repartition(n, col)` | Full shuffle | Distribute by specific column |
| `coalesce(n)` | No shuffle (narrow) | Reduce partitions only |
| AQE coalesce | Automatic | Post-shuffle partition merging |

> Adding more compute nodes does not fix data skew. Address the skew itself using the techniques above before scaling out resources.
