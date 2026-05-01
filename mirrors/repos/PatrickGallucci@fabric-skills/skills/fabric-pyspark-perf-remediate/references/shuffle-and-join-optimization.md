# Shuffle and Join Optimization in Microsoft Fabric

## Table of Contents

- [Understanding Shuffles](#understanding-shuffles)
- [Join Strategy Selection](#join-strategy-selection)
- [Broadcast Join Optimization](#broadcast-join-optimization)
- [Shuffle Partition Tuning](#shuffle-partition-tuning)
- [Sort-Merge Join Optimization](#sort-merge-join-optimization)
- [Shuffle Hash Join](#shuffle-hash-join)
- [Pre-Partitioning Strategy](#pre-partitioning-strategy)
- [Adaptive Query Execution](#adaptive-query-execution)

## Understanding Shuffles

A shuffle occurs when Spark must redistribute data across partitions — typically during joins, aggregations (`groupBy`), window functions, `repartition()`, or `DISTINCT`. Shuffles are the most expensive operation in Spark because they involve disk I/O, serialization, and network transfer.

### Identifying Shuffle Problems in Spark UI

Open the Spark UI from Monitoring Hub or the notebook session. Navigate to the SQL/DataFrame tab and look for Exchange nodes in the physical plan. Key metrics to check:

- **Shuffle Read Size**: Total bytes read across all tasks in a stage
- **Shuffle Write Size**: Total bytes written by the prior stage
- **Shuffle Spill (Memory)**: Data spilled from memory during shuffle
- **Shuffle Spill (Disk)**: Data spilled to disk — indicates memory pressure

**Rule of thumb**: If shuffle read/write exceeds 10 GB and the job is taking longer than expected, shuffle optimization is warranted.

## Join Strategy Selection

Spark supports multiple join strategies. The optimizer selects one based on table sizes and configuration. Use hints or configuration to override when the optimizer chooses poorly.

### Decision Tree

```
Is one side < autoBroadcastJoinThreshold (default 10MB)?
├── YES → Broadcast Hash Join (fastest, no shuffle)
└── NO → Are both sides sortable and equi-join?
    ├── YES → Sort-Merge Join (default for large-large joins)
    └── NO → Shuffle Hash Join or Cartesian (expensive)
```

### Join Hint Syntax

```python
# Broadcast hint (PySpark)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key_column")

# SQL hint
spark.sql("""
    SELECT /*+ BROADCAST(dim) */ f.*, dim.name
    FROM fact_table f
    JOIN dim_table dim ON f.dim_id = dim.id
""")
```

## Broadcast Join Optimization

Broadcast joins eliminate shuffles entirely by sending the smaller table to all executors. This is the single most impactful join optimization.

### When to Use

- One side of the join fits in executor memory (after filtering)
- Table size < 500 MB (practical upper limit depending on executor memory)
- The smaller table is referenced in multiple joins (broadcast once, reuse)

### Configuration

```python
# Increase threshold to 50MB (default is 10MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50m")

# Increase to 100MB for dimension tables
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "104857600")

# Disable broadcast entirely (for debugging)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
```

### Common Pitfall

Spark estimates table sizes from catalog statistics or file sizes. If statistics are stale or missing, Spark may not broadcast a table that would benefit from it. Force broadcast with the `broadcast()` hint when you know the table is small.

```python
# Force broadcast even if stats say table is too large
result = orders_df.join(broadcast(product_dim_df), "product_id")
```

## Shuffle Partition Tuning

The `spark.sql.shuffle.partitions` setting controls how many partitions are created after a shuffle. The default of 200 is often wrong.

### Sizing Guidelines

| Data Volume After Shuffle | Recommended Partitions | Target Partition Size |
|--------------------------|----------------------|----------------------|
| < 100 MB | 8 - 20 | ~5-10 MB each |
| 100 MB - 1 GB | 20 - 100 | ~10-50 MB each |
| 1 GB - 10 GB | 100 - 500 | ~20-100 MB each |
| 10 GB - 100 GB | 500 - 2000 | ~50-128 MB each |
| > 100 GB | 2000 - 8000 | ~50-128 MB each |

**Target**: Each post-shuffle partition should be 50-200 MB for optimal task execution.

### Setting in Fabric

```python
# Static setting
spark.conf.set("spark.sql.shuffle.partitions", "400")

# Use "auto" with AQE enabled (Fabric default)
spark.conf.set("spark.sql.shuffle.partitions", "auto")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

### When "auto" Is Not Enough

AQE's `auto` shuffle partitions work well for most cases but can underperform when data volume varies wildly between runs. If you have predictable data volumes, a static value tuned to your workload may outperform `auto`.

## Sort-Merge Join Optimization

For large-large table joins, Sort-Merge Join is the default. Optimize it by pre-sorting and co-partitioning the data.

### Pre-Bucketing for Repeated Joins

If you join the same tables repeatedly (e.g., daily ETL), write them as bucketed Delta tables:

```python
# Write bucketed table (one-time cost)
df.write.format("delta") \
    .bucketBy(256, "join_key") \
    .sortBy("join_key") \
    .saveAsTable("bucketed_fact_table")

# Subsequent joins skip shuffle
fact = spark.table("bucketed_fact_table")
dim = spark.table("bucketed_dim_table")  # also bucketed on same key & count
result = fact.join(dim, "join_key")
```

**Note**: Both tables must be bucketed on the same column with the same bucket count to eliminate the shuffle.

## Shuffle Hash Join

Shuffle Hash Join can outperform Sort-Merge Join when one side is significantly smaller (but too large to broadcast) and the data does not need sorting.

```python
# Enable shuffle hash join consideration
spark.conf.set("spark.sql.join.preferSortMergeJoin", "false")
```

Use sparingly — Sort-Merge Join is more robust for most workloads.

## Pre-Partitioning Strategy

Structure your Delta tables to minimize shuffles during common query patterns:

```python
# Partition by date for time-series queries
df.write.format("delta") \
    .partitionBy("year", "month") \
    .save("Tables/partitioned_events")

# Z-ORDER for multi-column filter patterns
spark.sql("OPTIMIZE events ZORDER BY (customer_id, event_type)")
```

### Partition Column Selection

Choose columns with low cardinality (10-1000 distinct values). High-cardinality partitioning (e.g., user_id) creates too many directories and small files.

## Adaptive Query Execution

AQE is enabled by default in Fabric and provides runtime optimizations:

- **Coalescing post-shuffle partitions**: Merges small partitions automatically
- **Converting sort-merge join to broadcast**: When runtime stats show one side is small
- **Optimizing skew joins**: Splits skewed partitions automatically

### Verify AQE is Active

```python
print(spark.conf.get("spark.sql.adaptive.enabled"))  # Should be "true"
print(spark.conf.get("spark.sql.adaptive.coalescePartitions.enabled"))
print(spark.conf.get("spark.sql.adaptive.skewJoin.enabled"))
```

### AQE Skew Join Settings

```python
# Minimum partition size to consider skewed (default 256MB)
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")

# Factor: partition is skewed if N times larger than median
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
```
