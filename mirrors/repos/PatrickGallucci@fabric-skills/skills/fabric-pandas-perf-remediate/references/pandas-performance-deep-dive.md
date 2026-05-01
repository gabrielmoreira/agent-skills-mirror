# Pandas Performance Deep Dive Reference

Comprehensive reference for advanced pandas optimization patterns in Microsoft Fabric Spark notebooks.

## Table of Contents

- [pandas UDF Optimization](#pandas-udf-optimization)
- [Native Execution Engine Integration](#native-execution-engine-integration)
- [Capacity Planning for Pandas Workloads](#capacity-planning-for-pandas-workloads)
- [pandas-on-Spark Advanced Patterns](#pandas-on-spark-advanced-patterns)
- [Koalas to pyspark.pandas Migration](#koalas-to-pysparkpandas-migration)
- [Delta Lake Read Optimization for pandas](#delta-lake-read-optimization-for-pandas)
- [Serialization and Data Transfer](#serialization-and-data-transfer)
- [Spark Configuration Reference](#spark-configuration-reference)
- [Anti-Patterns and Fixes](#anti-patterns-and-fixes)
- [Monitoring and Observability](#monitoring-and-observability)

---

## pandas UDF Optimization

pandas UDFs (Vectorized UDFs) are the recommended way to run custom Python/pandas logic at Spark scale without collecting data to the driver.

### Types of pandas UDFs

| UDF Type | Input | Output | Use Case |
|----------|-------|--------|----------|
| Series to Series | `pd.Series` | `pd.Series` | Column transforms |
| Iterator of Series | `Iterator[pd.Series]` | `Iterator[pd.Series]` | Stateful transforms, expensive init |
| Iterator of Multiple Series | `Iterator[Tuple[pd.Series, ...]]` | `Iterator[pd.Series]` | Multi-column input |
| Series to Scalar | `pd.Series` | Scalar | Aggregations |
| Grouped Map | `pd.DataFrame` | `pd.DataFrame` | Group-level transforms |

### Series to Series (Most Common)

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("double")
def normalize_revenue(revenue: pd.Series) -> pd.Series:
    """Vectorized normalization — runs on each partition."""
    return (revenue - revenue.mean()) / revenue.std()

# Apply — executes distributed, no driver memory pressure
result_df = spark_df.withColumn("norm_revenue", normalize_revenue("revenue"))
```

### Iterator of Series (Expensive Initialization)

```python
from typing import Iterator

@pandas_udf("string")
def classify_with_model(batches: Iterator[pd.Series]) -> Iterator[pd.Series]:
    """Load model once, apply to all batches in partition."""
    import joblib
    model = joblib.load("/mnt/models/classifier.pkl")  # Load once per partition
    for batch in batches:
        yield pd.Series(model.predict(batch.values.reshape(-1, 1)))

result_df = spark_df.withColumn("category", classify_with_model("feature_col"))
```

### Grouped Map (applyInPandas)

```python
def fit_per_group(pdf: pd.DataFrame) -> pd.DataFrame:
    """Fit a model per group — full pandas API available."""
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    X = pdf[["feature1", "feature2"]].values
    y = pdf["target"].values
    model.fit(X, y)
    pdf["prediction"] = model.predict(X)
    pdf["r_squared"] = model.score(X, y)
    return pdf

# Schema must match output DataFrame
result_schema = spark_df.schema.add("prediction", "double").add("r_squared", "double")

result_df = spark_df.groupBy("segment").applyInPandas(fit_per_group, schema=result_schema)
```

### Performance Tips for pandas UDFs

1. **Batch size tuning**: Control rows per batch with `spark.sql.execution.arrow.maxRecordsPerBatch` (default 10,000)
2. **Arrow optimization**: Ensure Arrow is enabled (`spark.sql.execution.arrow.pyspark.enabled = true`)
3. **Avoid Python objects**: Return primitive types, not custom objects
4. **Minimize serialization**: Do heavy computation inside the UDF, not outside
5. **Partition alignment**: If using groupBy + applyInPandas, ensure groups fit in executor memory

```python
# Tune batch size for your workload
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "50000")  # Larger batches = fewer calls
```

---

## Native Execution Engine Integration

Fabric's Native Execution Engine (vectorized engine based on Velox) accelerates Spark SQL and DataFrame operations. Understanding its interaction with pandas operations is critical.

### What It Accelerates

- Spark SQL queries (SELECT, JOIN, GROUP BY, aggregations)
- PySpark DataFrame operations that compile to Spark SQL
- Parquet/Delta file reads

### What It Does NOT Accelerate

- `toPandas()` collection to driver
- pandas UDF execution (Python code runs outside the engine)
- `collect()` / `take()` operations
- Native pandas operations after conversion

### Optimal Pattern with Native Execution Engine

```python
# Enable Native Execution Engine
spark.conf.set("spark.native.enabled", "true")
spark.conf.set("spark.shuffle.manager", "org.apache.spark.shuffle.sort.ColumnarShuffleManager")

# FAST: Spark operations benefit from native engine
transformed = (spark_df
    .filter(F.col("amount") > 100)              # Native accelerated
    .groupBy("region", "product")                 # Native accelerated
    .agg(F.sum("amount"), F.avg("quantity"))      # Native accelerated
)

# SLOW: This part runs on driver — minimize data before this point
pdf = transformed.toPandas()  # Arrow transfer only
```

### Compatibility Notes

- Native Execution Engine works with Runtime 1.2+
- Some operations fall back to JVM Spark if unsupported
- Check fallback count in Spark UI > SQL tab > "Native Engine Fallback"
- VOrder and Native Execution Engine are complementary (VOrder for reads, NEE for compute)

---

## Capacity Planning for Pandas Workloads

### Memory Budget Formula

```
Available for toPandas() = (Driver Memory) × 0.6 - (Spark overhead) - (Other notebooks in session)

Example — Medium node (64 GB):
  Driver memory:     ~28 GB (configurable)
  Spark overhead:    ~4 GB
  Safety margin:     ~4 GB
  Available:         ~20 GB for pandas DataFrames
  
  With pandas copy-on-write:
  Practical limit:   ~10 GB raw data (pandas duplicates during ops)
```

### Capacity SKU Recommendations

| Pandas Workload | Min Fabric SKU | Node Size | Rationale |
|----------------|----------------|-----------|-----------|
| EDA on < 1 GB | F2 | Small (32 GB) | Minimal memory needed |
| EDA on 1-5 GB | F8 | Medium (64 GB) | Room for copies |
| ML feature engineering | F16 | Large (128 GB) | Multiple DataFrames in memory |
| Large-scale pandas UDFs | F32+ | Large/X-Large | Executor memory for UDF batches |
| Production notebooks (pandas finish) | F16+ | Medium+ | Aggregate in Spark, small pandas |

### High Concurrency Mode Considerations

When using High Concurrency mode, multiple notebooks share the same Spark session. This means:

- Driver memory is shared across all active notebooks
- Each notebook's `toPandas()` competes for the same driver heap
- Only the initiating notebook is billed, but all consume memory
- Recommendation: Avoid large `toPandas()` calls in shared sessions

---

## pandas-on-Spark Advanced Patterns

### Efficient GroupBy Operations

```python
import pyspark.pandas as ps

psdf = spark_df.pandas_api()

# GOOD: Built-in aggregations (pushed to Spark)
result = psdf.groupby("category").agg({
    "revenue": ["sum", "mean", "std"],
    "quantity": "count"
})

# GOOD: Transform (keeps original shape, distributed)
psdf["pct_of_group"] = psdf.groupby("category")["revenue"].transform(
    lambda x: x / x.sum()
)

# AVOID: Custom apply with complex Python (forces row-by-row)
# If needed, use Spark applyInPandas instead
```

### Window Functions

```python
# pandas-on-Spark window functions execute as Spark window operations
psdf["rolling_avg"] = psdf.groupby("product")["revenue"].transform(
    lambda x: x.rolling(7).mean()
)

# For complex windows, drop to Spark API
from pyspark.sql.window import Window
w = Window.partitionBy("product").orderBy("date").rowsBetween(-6, 0)
spark_df = spark_df.withColumn("rolling_avg", F.avg("revenue").over(w))
```

### MultiIndex Handling

```python
# pandas-on-Spark supports MultiIndex but it can cause performance issues
# Flatten MultiIndex after groupby for better performance
result = psdf.groupby(["region", "product"]).sum()
result = result.reset_index()  # Flatten — improves downstream ops

# If you need MultiIndex, set the index explicitly
psdf = psdf.set_index(["region", "product"])
```

### Conversion Between APIs

```python
# Spark → pandas-on-Spark (no data movement)
psdf = spark_df.pandas_api()

# pandas-on-Spark → Spark (no data movement)
spark_df = psdf.to_spark()

# pandas-on-Spark → pandas (COLLECTS to driver!)
pdf = psdf.to_pandas()  # Same risk as toPandas()

# pandas → pandas-on-Spark
psdf = ps.from_pandas(pdf)  # Distributes from driver to executors

# pandas → Spark
spark_df = spark.createDataFrame(pdf)  # Uses Arrow if enabled
```

---

## Koalas to pyspark.pandas Migration

Koalas was merged into PySpark as `pyspark.pandas` in Spark 3.2. Fabric uses Spark 3.4+.

### Import Changes

```python
# OLD (Koalas — deprecated)
import databricks.koalas as ks
kdf = ks.read_delta("Tables/my_table")

# NEW (pyspark.pandas)
import pyspark.pandas as ps
psdf = ps.read_delta("Tables/my_table")
```

### Key Behavioral Changes

| Feature | Koalas | pyspark.pandas |
|---------|--------|----------------|
| Default index | Sequence index | Distributed sequence |
| `compute.default_index_type` | `sequence` | `distributed-sequence` |
| `.to_pandas()` behavior | Full collect | Full collect (same) |
| SQL integration | `ks.sql()` | `ps.sql()` |
| Type hints | Limited | Full PEP 484 support |

### Performance-Relevant Changes

```python
# pyspark.pandas default index is distributed — faster for large data
# but adds overhead for small data
ps.set_option("compute.default_index_type", "sequence")  # For small datasets
ps.set_option("compute.default_index_type", "distributed-sequence")  # For large datasets (default)

# Operations per partition (reduces shuffles)
ps.set_option("compute.ops_on_diff_frames", True)  # Allow cross-DataFrame ops
```

---

## Delta Lake Read Optimization for pandas

### Predicate Pushdown

```python
# Delta predicate pushdown reduces data scanned before any conversion
# This works with toPandas(), pandas API on Spark, and pandas UDFs

# GOOD: Predicates pushed to Delta scan
spark_df = spark.read.format("delta").load("Tables/sales") \
    .filter("year = 2024 AND region = 'US'")  # Pushed to file pruning

# Column pruning — only reads selected columns from Parquet
spark_df = spark_df.select("customer_id", "amount", "date")

# THEN convert (much less data)
pdf = spark_df.toPandas()
```

### VOrder for Read Performance

```python
# VOrder-optimized files read faster for pandas conversion
# Enable for read-heavy workloads
spark.conf.set("spark.sql.parquet.vorder.default", "true")

# Or use the readHeavyForSpark resource profile
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
```

### Partition Elimination

```python
# If Delta table is partitioned, filter on partition columns first
# This eliminates entire file groups before any processing

# Check partitioning
spark.sql("DESCRIBE DETAIL delta.`Tables/sales`").select("partitionColumns").show()

# Filter on partition column for massive speedup
spark_df = spark.read.format("delta").load("Tables/sales") \
    .filter("partition_date = '2024-01-15'")  # File-level pruning
```

---

## Serialization and Data Transfer

### Arrow Transfer Optimization

```python
# Full Arrow configuration for fastest pandas ↔ Spark transfer
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "10000")

# For createDataFrame (pandas → Spark)
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
# Arrow makes createDataFrame 10-100x faster for large DataFrames
```

### Benchmarking Transfer Speed

```python
import time

# Benchmark toPandas with and without Arrow
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "false")
start = time.time()
pdf1 = spark_df.toPandas()
no_arrow = time.time() - start

spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
start = time.time()
pdf2 = spark_df.toPandas()
with_arrow = time.time() - start

print(f"Without Arrow: {no_arrow:.2f}s")
print(f"With Arrow:    {with_arrow:.2f}s")
print(f"Speedup:       {no_arrow/with_arrow:.1f}x")
```

---

## Spark Configuration Reference

### Key Settings for Pandas Workloads

| Configuration | Default | Recommended | Purpose |
|--------------|---------|-------------|---------|
| `spark.sql.execution.arrow.pyspark.enabled` | `false` | `true` | Arrow columnar transfer |
| `spark.sql.execution.arrow.pyspark.fallback.enabled` | `false` | `true` | Graceful fallback for unsupported types |
| `spark.sql.execution.arrow.maxRecordsPerBatch` | `10000` | `10000-50000` | Batch size for Arrow transfer |
| `spark.sql.shuffle.partitions` | `200` | `auto` or data-size based | Shuffle partition count |
| `spark.sql.autoBroadcastJoinThreshold` | `10m` | `100m` for pandas-on-Spark | Broadcast join threshold |
| `spark.driver.memory` | SKU default | Max for node size | Driver heap for toPandas() |
| `spark.driver.maxResultSize` | `1g` | `4g-8g` | Max size of serialized results |
| `spark.sql.adaptive.enabled` | `true` | `true` | Adaptive Query Execution |
| `spark.ms.autotune.enabled` | `false` | `true` | Fabric autotune for queries |
| `spark.fabric.resourceProfile` | `writeHeavy` | `readHeavyForSpark` | Fabric resource profile |
| `spark.native.enabled` | varies | `true` | Native Execution Engine |

### Apply All Recommended Settings

```python
# Paste as first cell in notebook for pandas-optimized configuration
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "104857600")  # 100 MB
spark.conf.set("spark.driver.maxResultSize", "4g")
```

---

## Anti-Patterns and Fixes

### 1. Collecting Before Filtering

```python
# ANTI-PATTERN
pdf = spark_df.toPandas()
filtered = pdf[pdf["region"] == "US"]

# FIX
pdf = spark_df.filter(F.col("region") == "US").toPandas()
```

### 2. Python Loops Over Spark Data

```python
# ANTI-PATTERN
for row in spark_df.collect():
    process(row)

# FIX: Use pandas UDF or Spark operations
@pandas_udf("string")
def process_batch(series: pd.Series) -> pd.Series:
    return series.apply(process)
```

### 3. Repeated toPandas() Calls

```python
# ANTI-PATTERN
pdf1 = spark_df.filter("type = 'A'").toPandas()
pdf2 = spark_df.filter("type = 'B'").toPandas()
pdf3 = spark_df.filter("type = 'C'").toPandas()

# FIX: Single conversion with pandas filtering
pdf = spark_df.filter(F.col("type").isin("A", "B", "C")).toPandas()
pdf1 = pdf[pdf["type"] == "A"]
pdf2 = pdf[pdf["type"] == "B"]
pdf3 = pdf[pdf["type"] == "C"]
```

### 4. Using pandas for Large Joins

```python
# ANTI-PATTERN
pdf_large = spark_df_large.toPandas()
pdf_lookup = spark_df_lookup.toPandas()
result = pdf_large.merge(pdf_lookup, on="key")

# FIX: Join in Spark
result = spark_df_large.join(broadcast(spark_df_lookup), "key").toPandas()
```

### 5. Ignoring createDataFrame Overhead

```python
# ANTI-PATTERN (slow without Arrow)
spark_df = spark.createDataFrame(large_pandas_df)

# FIX: Ensure Arrow is enabled for fast pandas → Spark
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark_df = spark.createDataFrame(large_pandas_df)
```

---

## Monitoring and Observability

### Spark UI Indicators

| What to Check | Where | Warning Sign |
|--------------|-------|-------------|
| Driver memory usage | Executors tab > Driver | > 80% used |
| Shuffle data size | Stages tab > Shuffle Read/Write | > 10 GB for simple ops |
| Task duration skew | Stages tab > Task Duration | Max >> Median (data skew) |
| GC time | Executors tab > GC Time | > 10% of task time |
| Arrow fallback | Driver logs | "Arrow optimization disabled" |

### Programmatic Monitoring

```python
# Check Spark configuration at runtime
configs = [
    "spark.sql.execution.arrow.pyspark.enabled",
    "spark.sql.shuffle.partitions",
    "spark.sql.autoBroadcastJoinThreshold",
    "spark.driver.memory",
    "spark.driver.maxResultSize",
    "spark.ms.autotune.enabled",
    "spark.fabric.resourceProfile",
    "spark.native.enabled"
]
for c in configs:
    print(f"{c} = {spark.conf.get(c, 'NOT SET')}")
```

### Memory Tracking Decorator

```python
import functools
import psutil
import os

def track_memory(func):
    """Decorator to track memory usage of pandas operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024**3
        result = func(*args, **kwargs)
        mem_after = process.memory_info().rss / 1024**3
        print(f"[{func.__name__}] Memory: {mem_before:.2f} GB → {mem_after:.2f} GB (Δ {mem_after - mem_before:+.2f} GB)")
        return result
    return wrapper

@track_memory
def load_and_process():
    pdf = spark_df.toPandas()
    return pdf.groupby("region")["revenue"].sum()
```
