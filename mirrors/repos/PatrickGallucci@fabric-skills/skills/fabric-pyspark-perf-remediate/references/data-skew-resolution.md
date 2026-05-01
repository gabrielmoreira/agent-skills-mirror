# Data Skew Resolution in Microsoft Fabric

## Table of Contents

- [Detecting Data Skew](#detecting-data-skew)
- [Skew in Joins](#skew-in-joins)
- [Skew in Aggregations](#skew-in-aggregations)
- [Salting Technique](#salting-technique)
- [Adaptive Query Execution for Skew](#adaptive-query-execution-for-skew)
- [Repartitioning Strategies](#repartitioning-strategies)
- [Handling NULL Key Skew](#handling-null-key-skew)

## Detecting Data Skew

Data skew occurs when data is unevenly distributed across partitions, causing some tasks to process significantly more data than others. The slowest task determines stage completion time.

### Symptoms in Spark UI

Navigate to Spark UI > Stages > Click on the slow stage > Task Metrics:

- **Duration**: Look at min, median, max, and 75th percentile. If max is >5x the median, you have skew.
- **Input Size**: If one task reads 2 GB while the median is 50 MB, data is skewed on the partition key.
- **Shuffle Read Size**: Same uneven distribution pattern in post-shuffle stages.

### Programmatic Detection

Use the [identify_skew.py](../scripts/identify_skew.py) script, or run this quick check:

```python
from pyspark.sql import functions as F

# Check distribution of a key column
df.groupBy("join_key") \
    .count() \
    .orderBy(F.desc("count")) \
    .show(20)

# Check for NULL concentration
null_count = df.filter(F.col("join_key").isNull()).count()
total_count = df.count()
print(f"NULL keys: {null_count} ({null_count/total_count*100:.1f}%)")
```

## Skew in Joins

Join skew happens when a few key values appear in millions of rows. During a shuffle join, all rows with the same key go to the same partition/task.

### Example: Customer Join with Hot Keys

```python
# Problem: customer_id "GUEST" has 50M rows, others have <1000
orders = spark.table("orders")           # 100M rows
customers = spark.table("customers")     # 500K rows

# This join will skew on "GUEST" customer_id
result = orders.join(customers, "customer_id")  # One task gets 50M rows
```

### Fix 1: Filter and Union (Separate Hot Keys)

```python
hot_keys = ["GUEST", "UNKNOWN", "SYSTEM"]

# Process hot keys separately with broadcast
hot_orders = orders.filter(F.col("customer_id").isin(hot_keys))
hot_result = hot_orders.join(broadcast(customers), "customer_id")

# Process normal keys with standard join
normal_orders = orders.filter(~F.col("customer_id").isin(hot_keys))
normal_result = normal_orders.join(customers, "customer_id")

# Combine results
result = hot_result.unionAll(normal_result)
```

### Fix 2: Salting (See Section Below)

## Skew in Aggregations

Aggregation skew occurs during `groupBy` operations when some groups are much larger than others.

```python
# Problem: groupBy with skewed key
daily_totals = orders.groupBy("date", "category").agg(
    F.sum("amount").alias("total"),
    F.count("*").alias("order_count")
)
# If "Electronics" category has 100x more orders than others, that task is 100x slower
```

### Fix: Two-Stage Aggregation

```python
import pyspark.sql.functions as F

# Stage 1: Add salt and partial aggregate
num_salts = 10
salted = orders.withColumn("salt", (F.rand() * num_salts).cast("int"))

partial_agg = salted.groupBy("date", "category", "salt").agg(
    F.sum("amount").alias("partial_total"),
    F.count("*").alias("partial_count")
)

# Stage 2: Remove salt and final aggregate
final_agg = partial_agg.groupBy("date", "category").agg(
    F.sum("partial_total").alias("total"),
    F.sum("partial_count").alias("order_count")
)
```

## Salting Technique

Salting adds a random suffix to skewed join keys to distribute hot keys across multiple partitions. This is the most general-purpose skew fix.

### Implementation Pattern

```python
import pyspark.sql.functions as F

num_salts = 20  # Spread hot keys across 20 partitions

# Salt the large (skewed) side
large_salted = large_df.withColumn(
    "salt", (F.rand() * num_salts).cast("int")
).withColumn(
    "salted_key", F.concat(F.col("join_key"), F.lit("_"), F.col("salt"))
)

# Explode the small side to match all salt values
from pyspark.sql.types import ArrayType, IntegerType
salt_array = F.array([F.lit(i) for i in range(num_salts)])

small_exploded = small_df.withColumn(
    "salt", F.explode(salt_array)
).withColumn(
    "salted_key", F.concat(F.col("join_key"), F.lit("_"), F.col("salt"))
)

# Join on salted key (now evenly distributed)
result = large_salted.join(small_exploded, "salted_key") \
    .drop("salt", "salted_key")
```

### Trade-offs

- **Pro**: Effectively eliminates skew for any key distribution
- **Con**: Exploding the small side increases its row count by `num_salts` factor
- **Con**: Adds complexity to the query plan
- **When to use**: When AQE skew handling is insufficient and hot keys are known or detectable

## Adaptive Query Execution for Skew

AQE can handle skew automatically in Fabric. It detects skewed partitions at runtime and splits them.

### Enable and Configure

```python
# AQE is on by default in Fabric, verify:
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Enable skew join optimization
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# A partition is considered skewed if it is this many times larger than median
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")

# Minimum absolute size to be considered skewed
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")
```

### When AQE Skew Handling Falls Short

AQE works well for moderate skew but may not fully resolve extreme cases where a single key represents >30% of the data. In those cases, use salting or the filter-and-union approach above.

## Repartitioning Strategies

### Round-Robin Repartition

```python
# Spread data evenly across N partitions (full shuffle)
df_balanced = df.repartition(100)
```

### Hash Repartition on Non-Skewed Column

```python
# Repartition on a column with better distribution
df_balanced = df.repartition(100, "secondary_key")
```

### Coalesce (Reduce Partitions Without Full Shuffle)

```python
# Reduce partitions without a full shuffle (only merges)
df_compacted = df.coalesce(50)
```

**Important**: `coalesce()` can worsen skew because it only merges adjacent partitions. Use `repartition()` when you need even distribution.

## Handling NULL Key Skew

NULL values in join keys are a common source of skew because all NULLs hash to the same partition.

### Fix: Replace NULLs with Unique Identifiers

```python
# Replace NULLs with unique values to spread them across partitions
df_fixed = df.withColumn(
    "join_key",
    F.when(F.col("join_key").isNull(),
           F.concat(F.lit("NULL_"), F.monotonically_increasing_id()))
     .otherwise(F.col("join_key"))
)
```

### Fix: Filter NULLs Before Join

```python
# If NULL keys don't need to join, filter them out
df_with_keys = df.filter(F.col("join_key").isNotNull())
df_null_keys = df.filter(F.col("join_key").isNull())

# Join only the rows with valid keys
joined = df_with_keys.join(other_df, "join_key")

# Union back NULL rows with NULL join columns
result = joined.unionByName(
    df_null_keys.select(joined.columns),
    allowMissingColumns=True
)
```
