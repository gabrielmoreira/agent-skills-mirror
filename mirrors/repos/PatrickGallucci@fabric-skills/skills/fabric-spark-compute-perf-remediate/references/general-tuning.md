# General Spark Tuning Guide

## Table of Contents

- [Adaptive Query Execution](#adaptive-query-execution)
- [Native Execution Engine](#native-execution-engine)
- [Autotune ML-Based Tuning](#autotune-ml-based-tuning)
- [Partition Tuning](#partition-tuning)
- [Join Optimization](#join-optimization)
- [Caching Strategy](#caching-strategy)
- [Essential Spark Properties](#essential-spark-properties)

## Adaptive Query Execution

AQE dynamically adjusts query plans at runtime based on actual data statistics.

```python
# Enable AQE (enabled by default on most Fabric runtimes)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

### What AQE Optimizes

- **Coalesces partitions** — merges small shuffle partitions after a stage
- **Switches join strategies** — changes sort-merge to broadcast if one side is small
- **Handles skew** — splits skewed partitions for balanced processing

AQE requires shuffle stages to take effect. It does not help with initial table scans.

## Native Execution Engine

The Fabric Native Execution Engine runs Spark SQL and DataFrame operations using a
vectorized C++ engine instead of the JVM. Significant performance gains for SQL-heavy
workloads.

```python
# Enable Native Execution Engine
spark.conf.set("spark.fabric.nativeExecution.enabled", "true")
```

### Compatibility

- Requires Fabric Runtime 1.3 or higher
- Supports common SQL operations (filter, project, join, aggregate, sort)
- Falls back to JVM for unsupported operations transparently
- No code changes required

### When to Enable

- SQL-heavy ETL workloads (SELECT, JOIN, GROUP BY, WINDOW)
- Interactive query notebooks
- Any workload dominated by DataFrame/SQL operations

### When to Be Cautious

- RDD API-heavy workloads (no benefit)
- UDF-heavy workloads (UDFs run in JVM regardless)
- Very small datasets (overhead may exceed benefit)

## Autotune ML-Based Tuning

Autotune uses machine learning to optimize Spark configuration per query pattern.

### How It Works

1. Starts with default configuration (centroid)
2. Generates candidate configurations using ML model
3. Applies the best predicted candidate
4. After execution, feeds performance data back to refine the model
5. Converges to optimal configuration after 20–25 iterations

### Enable Autotune

```python
spark.conf.set("spark.ms.autotune.enabled", "true")
```

### Requirements and Limitations

| Requirement | Detail |
|-------------|--------|
| Runtime | Fabric Runtime 1.1 or 1.2 only (not higher) |
| Query type | Spark SQL API (not RDD API) |
| Query duration | Minimum 15 seconds execution time |
| High concurrency | Not compatible |
| Private endpoints | Not compatible |
| Autoscaling | Compatible |

### Autotune Status Codes

| Status | Meaning |
|--------|---------|
| QUERY_TUNING_SUCCEED | Optimal settings applied |
| QUERY_TUNING_DISABLED | Autotune is disabled; enable it |
| QUERY_PATTERN_NOT_MATCH | Query is not read-only; autotune targets reads |
| QUERY_DURATION_TOO_SHORT | Query runs < 15 seconds; too fast to optimize |

## Partition Tuning

### Shuffle Partitions

```python
# Default is 200; adjust based on data size
spark.conf.set("spark.sql.shuffle.partitions", "auto")  # AQE auto-tuning

# Or set explicitly
spark.conf.set("spark.sql.shuffle.partitions", "100")
```

**Rule of thumb**: Target 128 MB–256 MB per partition after shuffle.

### Delta Table Partitioning

Partition only on low-cardinality columns used in virtually every query filter.

Good partition columns: date, region, category (< 1,000 distinct values)
Bad partition columns: user_id, timestamp, UUID (high cardinality = millions of tiny directories)

### Repartition Before Write

```python
# Repartition to control output file count
df.repartition(48).write.format("delta").mode("overwrite").saveAsTable("table")

# Coalesce to reduce files without full shuffle
df.coalesce(16).write.format("delta").mode("overwrite").saveAsTable("table")
```

## Join Optimization

### Broadcast Joins

Best for joining a large table with a small table (< 10 MB default threshold).

```python
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "join_key")
```

### Sort-Merge Joins

Default for large-large table joins. Ensure join keys have compatible types and
statistics are fresh.

### Skew Join Handling

```python
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256m")
```

## Caching Strategy

### When to Cache

- DataFrames reused multiple times in the same notebook/job
- Small-to-medium lookup tables used in joins
- Iterative ML algorithms on the same dataset

### When Not to Cache

- Data used only once
- Data larger than available executor memory
- Streaming DataFrames (use continuous processing instead)

```python
# Cache and materialize
df.cache()
df.count()  # Force materialization

# Unpersist when done
df.unpersist()
```

## Essential Spark Properties

| Property | Recommended Value | Purpose |
|----------|------------------|---------|
| `spark.sql.adaptive.enabled` | true | Adaptive Query Execution |
| `spark.sql.adaptive.coalescePartitions.enabled` | true | Auto-coalesce shuffle partitions |
| `spark.sql.adaptive.skewJoin.enabled` | true | Handle skewed joins |
| `spark.sql.parquet.vorder.default` | true (read workloads) | VOrder for read performance |
| `spark.microsoft.delta.optimizeWrite.enabled` | true | Reduce small files on write |
| `spark.fabric.nativeExecution.enabled` | true | Native C++ execution engine |
| `spark.ms.autotune.enabled` | true | ML-based query tuning |
| `spark.sql.shuffle.partitions` | auto or calculated | Control parallelism |
| `spark.dynamicAllocation.enabled` | true | Auto-scale executors |
