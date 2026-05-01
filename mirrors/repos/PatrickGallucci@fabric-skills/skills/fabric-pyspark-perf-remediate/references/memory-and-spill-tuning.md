# Memory and Spill Tuning in Microsoft Fabric

## Table of Contents

- [Fabric Memory Architecture](#fabric-memory-architecture)
- [Diagnosing Memory Issues](#diagnosing-memory-issues)
- [OOM Error Types and Fixes](#oom-error-types-and-fixes)
- [Disk Spill Optimization](#disk-spill-optimization)
- [Caching Strategy](#caching-strategy)
- [Driver Memory Management](#driver-memory-management)
- [Executor Memory Configuration](#executor-memory-configuration)

## Fabric Memory Architecture

In Microsoft Fabric, memory is allocated per node based on the pool configuration:

| Node Size | Memory | Cores | Typical Use Case |
|-----------|--------|-------|-----------------|
| Small | 28 GB | 4 | Light workloads, prototyping |
| Medium | 56 GB | 8 | Standard ETL, EDA (starter pool default) |
| Large | 112 GB | 16 | Large joins, complex transformations |
| X-Large | 224 GB | 32 | Memory-intensive analytics |
| XX-Large | 400 GB | 64 | Extreme scale processing |

**Spark Memory Split** (per executor):
- **Execution Memory** (~60%): Used for shuffles, joins, sorts, aggregations
- **Storage Memory** (~40%): Used for cached DataFrames and broadcast variables
- **User Memory** (~remaining): Used for internal metadata, UDF overhead

The boundary between execution and storage is dynamic (unified memory management). Execution can borrow from storage and evict cached data if needed.

## Diagnosing Memory Issues

### Check Current Configuration

```python
# Print memory configuration
print(f"Driver memory: {spark.conf.get('spark.driver.memory')}")
print(f"Executor memory: {spark.conf.get('spark.executor.memory')}")
print(f"Executor cores: {spark.conf.get('spark.executor.cores')}")
print(f"Memory overhead: {spark.conf.get('spark.executor.memoryOverhead', 'default')}")
print(f"Memory fraction: {spark.conf.get('spark.memory.fraction')}")
print(f"Storage fraction: {spark.conf.get('spark.memory.storageFraction')}")
```

### Identifying Memory Pressure in Spark UI

Navigate to Spark UI > Stages > Click on the slow stage > Task Metrics:

- **GC Time**: If GC time > 10% of task time, memory is under pressure
- **Spill (Memory)**: Data that overflowed execution memory and was serialized
- **Spill (Disk)**: Data written to local disk because memory was exhausted
- **Peak Execution Memory**: Maximum memory used by a single task

Navigate to Spark UI > Executors tab:
- Check **Memory Used** vs **Memory Available** across executors
- Look for executors that are consistently at capacity

## OOM Error Types and Fixes

### Driver OOM: `java.lang.OutOfMemoryError: Java heap space`

**Cause**: Too much data collected to the driver node.

**Common triggers**:
- `df.collect()` on a large DataFrame
- `df.toPandas()` on millions of rows
- `spark.sql("SELECT *").show()` on large tables (show() collects to driver)
- Large broadcast variables

**Fixes**:

```python
# Instead of collect(), write to Delta table
df.write.format("delta").mode("overwrite").save("Tables/results")

# Instead of toPandas() on full dataset, sample or limit
pdf = df.limit(100000).toPandas()

# Or use Arrow-based conversion with chunking
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
pdf = df.limit(100000).toPandas()

# Increase driver memory in environment compute settings
# Driver memory options: 28g, 56g, 112g, 224g, 400g
```

### Executor OOM: `Container killed by YARN for exceeding memory limits`

**Cause**: Task processing more data than executor memory can handle.

**Common triggers**:
- Skewed partitions (one partition has disproportionate data)
- Too few partitions (each partition too large)
- Large shuffle operations
- Explode or cartesian joins creating data multiplication

**Fixes**:

```python
# Increase partitions to reduce per-task memory
spark.conf.set("spark.sql.shuffle.partitions", "800")

# Reduce max partition bytes for read operations
spark.conf.set("spark.sql.files.maxPartitionBytes", "64m")

# Increase memory overhead for off-heap usage
spark.conf.set("spark.executor.memoryOverhead", "2g")

# Check for and fix data skew (see data-skew-resolution.md)
```

### Python Worker OOM

**Cause**: Python UDFs or pandas operations consuming too much memory in the Python process.

**Fixes**:

```python
# Use Pandas UDFs (Arrow-based, vectorized) instead of row-level UDFs
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("double")
def vectorized_transform(series: pd.Series) -> pd.Series:
    return series * 2.0

# Instead of:
# from pyspark.sql.functions import udf
# @udf("double")
# def slow_transform(value):
#     return value * 2.0

# Increase Python worker memory
spark.conf.set("spark.executor.pyspark.memory", "2g")
```

## Disk Spill Optimization

Spill occurs when Spark cannot fit intermediate data in memory and writes it to disk. Some spill is normal; excessive spill significantly degrades performance.

### Acceptable vs Problematic Spill

| Metric | Acceptable | Investigate | Critical |
|--------|-----------|-------------|----------|
| Spill (Memory) | < 1 GB per task | 1-10 GB per task | > 10 GB per task |
| Spill (Disk) | < 500 MB per task | 500 MB - 5 GB | > 5 GB per task |
| Ratio to Input | < 2x input size | 2-5x input | > 5x input |

### Reducing Spill

```python
# 1. Increase partitions to reduce per-task data volume
spark.conf.set("spark.sql.shuffle.partitions", "1000")

# 2. Increase execution memory fraction
spark.conf.set("spark.memory.fraction", "0.8")  # Default 0.6

# 3. Use a larger node size in custom pool configuration
# Workspace Settings > Data Engineering > Spark Pools > Node Size

# 4. For sort operations, increase sort buffer
spark.conf.set("spark.sql.sort.spillThreshold", "268435456")  # 256 MB
```

## Caching Strategy

### When to Cache

Cache when a DataFrame is:
- Read once but **used in 2+ actions** (joins, writes, counts)
- Expensive to compute (complex transformations, external reads)
- Stable during the session (not being modified between uses)

### When NOT to Cache

Do not cache when:
- The DataFrame is used only once
- The DataFrame is very large (larger than available storage memory)
- The data source supports predicate pushdown (Delta tables with filters)
- You're in a memory-constrained environment

### Caching Levels

```python
from pyspark import StorageLevel

# Memory only (fastest, evicts under pressure)
df.cache()  # Same as df.persist(StorageLevel.MEMORY_AND_DISK)

# Memory and disk (spills to disk when memory full)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Serialized memory (uses less memory, more CPU for ser/deser)
df.persist(StorageLevel.MEMORY_ONLY_SER)

# Disk only (when memory is critical)
df.persist(StorageLevel.DISK_ONLY)

# ALWAYS unpersist when done
df.unpersist()
```

### Cache Validation

```python
# Verify a DataFrame is cached
print(df.is_cached)

# Check storage level
print(df.storageLevel)

# In Spark UI > Storage tab, verify cache is being used
# If "Fraction Cached" < 100%, not all partitions fit in memory
```

## Driver Memory Management

The driver is a single point of failure. Keep its memory usage minimal.

### Rules

1. Never `collect()` more than ~100K rows to the driver
2. Use `df.write` instead of `df.toPandas()` for large results
3. Avoid accumulating large Python objects (lists, dicts) in the driver
4. Monitor driver memory in Spark UI > Executors > Driver row

### Driver Memory Configuration in Fabric

Configure through Environment settings:
- Navigate to Environment > Spark Compute > Compute
- Set **Spark driver core** and **Spark driver memory**
- Allowed memory values: 28g, 56g, 112g, 224g, 400g

## Executor Memory Configuration

### Environment-Level Settings

```
Environment > Spark Compute > Compute:
  Spark executor cores: 4 | 8 | 16 | 32 | 64
  Spark executor memory: 28g | 56g | 112g | 224g | 400g
```

### Dynamic Allocation

Fabric uses dynamic executor allocation by default. The system automatically scales executors based on workload. Configure min/max in pool settings:

```
Workspace Settings > Data Engineering > Spark Pools:
  Min executors: 1 (default)
  Max executors: depends on pool/capacity
```

### Memory Per Core Ratio

Each executor's memory should align with its core count. The default Fabric configurations maintain appropriate ratios. Avoid setting executor memory very high with low core counts (wastes cores) or very low memory with high core counts (causes spill).
