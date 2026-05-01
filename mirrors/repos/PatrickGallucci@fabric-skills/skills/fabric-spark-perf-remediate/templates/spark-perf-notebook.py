# =============================================================================
# Fabric Spark Performance Analysis Notebook Template
# =============================================================================
# Paste this into a Microsoft Fabric notebook to diagnose performance issues
# in the current Spark session. Customize the table names and thresholds
# for your specific workload.
#
# Usage:
#   1. Attach to your Fabric lakehouse/environment.
#   2. Run each section sequentially to build a performance profile.
#   3. Review output and follow recommended actions.
# =============================================================================

# %% [markdown]
# ## 1. Session Configuration Audit

# %%
# Capture current Spark configuration for review
import json

config_keys = [
    "spark.sql.shuffle.partitions",
    "spark.sql.autoBroadcastJoinThreshold",
    "spark.sql.files.maxPartitionBytes",
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.ms.autotune.enabled",
    "spark.sql.parquet.vorder.default",
    "spark.microsoft.delta.optimizeWrite.enabled",
    "spark.fabric.resource.profile",
    "spark.executor.memory",
    "spark.executor.cores",
    "spark.driver.memory",
    "spark.dynamicAllocation.enabled",
    "spark.dynamicAllocation.minExecutors",
    "spark.dynamicAllocation.maxExecutors",
]

print("=" * 60)
print("  CURRENT SPARK CONFIGURATION")
print("=" * 60)

for key in config_keys:
    try:
        value = spark.conf.get(key)
    except Exception:
        value = "(not set)"
    print(f"  {key}: {value}")

print("=" * 60)

# %%
# Runtime and cluster information
sc = spark.sparkContext
print(f"Spark Version     : {sc.version}")
print(f"Application ID    : {sc.applicationId}")
print(f"Default Parallelism: {sc.defaultParallelism}")
print(f"Active Executors   : {sc._jsc.sc().getExecutorMemoryStatus().size()}")

# %% [markdown]
# ## 2. Delta Table Health Check
#
# Update `TARGET_TABLES` with the tables you want to analyze.

# %%
from delta.tables import DeltaTable
import pyspark.sql.functions as F

# --- CONFIGURE: Add your table names here ---
TARGET_TABLES = [
    "my_lakehouse.dbo.fact_sales",
    "my_lakehouse.dbo.dim_customer",
    # Add more tables as needed
]

# Thresholds for warnings
SMALL_FILE_THRESHOLD_MB = 32  # Files smaller than this trigger a warning
MAX_FILES_WARNING = 10000     # More files than this triggers a warning

print("=" * 60)
print("  DELTA TABLE HEALTH CHECK")
print("=" * 60)

for table_name in TARGET_TABLES:
    try:
        dt = DeltaTable.forName(spark, table_name)
        detail = dt.detail().collect()[0]

        num_files = detail["numFiles"]
        size_bytes = detail["sizeInBytes"]
        avg_file_mb = (size_bytes / max(num_files, 1)) / (1024 * 1024)
        size_gb = size_bytes / (1024 ** 3)

        warnings = []
        if avg_file_mb < SMALL_FILE_THRESHOLD_MB:
            warnings.append(f"SMALL FILES: Avg {avg_file_mb:.1f} MB (target: 128-1024 MB)")
        if num_files > MAX_FILES_WARNING:
            warnings.append(f"HIGH FILE COUNT: {num_files:,} files")

        status = "WARNING" if warnings else "HEALTHY"
        color_marker = "!!" if warnings else "OK"

        print(f"\n[{color_marker}] {table_name}")
        print(f"     Files: {num_files:,}  |  Size: {size_gb:.2f} GB  |  Avg File: {avg_file_mb:.1f} MB")
        if detail.get("partitionColumns"):
            print(f"     Partitioned by: {detail['partitionColumns']}")
        for w in warnings:
            print(f"     >>> {w}")
            if "SMALL FILES" in w:
                print(f"     >>> ACTION: Run OPTIMIZE {table_name} VORDER")
            if "HIGH FILE COUNT" in w:
                print(f"     >>> ACTION: Run table maintenance (bin-compaction)")

    except Exception as e:
        print(f"\n[--] {table_name}: Could not analyze - {str(e)[:80]}")

print("\n" + "=" * 60)

# %% [markdown]
# ## 3. Query Performance Profiler
#
# Wraps a target query to measure execution time, shuffle metrics,
# and partition characteristics.

# %%
import time

def profile_query(query_name, query_func):
    """
    Profile a Spark query function. Pass a lambda or function that
    returns a DataFrame. The function will be executed and metrics collected.

    Usage:
        profile_query("Sales Aggregation", lambda: spark.sql("SELECT ..."))
    """
    print(f"\n--- Profiling: {query_name} ---")

    start_time = time.time()
    df = query_func()

    # Force execution by counting
    row_count = df.count()
    elapsed = time.time() - start_time

    # Partition info
    num_partitions = df.rdd.getNumPartitions()

    print(f"  Rows returned : {row_count:,}")
    print(f"  Partitions    : {num_partitions}")
    print(f"  Elapsed time  : {elapsed:.2f}s")

    if elapsed > 60:
        print(f"  >>> WARNING: Query took > 60s. Review Spark UI stages for bottlenecks.")
    if num_partitions == 200:
        print(f"  >>> WARNING: Default 200 partitions detected. Consider tuning spark.sql.shuffle.partitions.")

    # Check physical plan for optimization opportunities
    plan = df._jdf.queryExecution().executedPlan().toString()
    if "SortMergeJoin" in plan and row_count < 1000000:
        print(f"  >>> HINT: SortMergeJoin detected on small result. Consider broadcast hint.")
    if "Exchange" in plan:
        exchange_count = plan.count("Exchange")
        print(f"  >>> INFO: {exchange_count} shuffle exchange(s) in execution plan.")

    return df, elapsed

# --- CONFIGURE: Add your queries here ---
# Example usage:
# df, elapsed = profile_query(
#     "Monthly Sales Summary",
#     lambda: spark.sql("""
#         SELECT month, region, SUM(amount) as total
#         FROM my_lakehouse.dbo.fact_sales
#         WHERE year = 2025
#         GROUP BY month, region
#     """)
# )

# %% [markdown]
# ## 4. Data Skew Detection

# %%
def detect_skew(df, key_column, threshold_multiplier=10):
    """
    Detect data skew on a specific column. Reports keys that have
    more than threshold_multiplier times the average count.

    Args:
        df: Input DataFrame
        key_column: Column name to check for skew
        threshold_multiplier: How many times the average triggers a warning (default: 10)
    """
    print(f"\n--- Skew Detection on '{key_column}' ---")

    key_counts = df.groupBy(key_column).count()
    stats = key_counts.agg(
        F.avg("count").alias("avg_count"),
        F.max("count").alias("max_count"),
        F.min("count").alias("min_count"),
        F.stddev("count").alias("stddev_count"),
        F.count("*").alias("num_keys")
    ).collect()[0]

    avg_count = stats["avg_count"]
    max_count = stats["max_count"]
    skew_ratio = max_count / max(avg_count, 1)
    threshold = avg_count * threshold_multiplier

    print(f"  Distinct keys : {stats['num_keys']:,}")
    print(f"  Avg count/key : {avg_count:,.0f}")
    print(f"  Max count/key : {max_count:,.0f}")
    print(f"  Min count/key : {stats['min_count']:,.0f}")
    print(f"  Skew ratio    : {skew_ratio:.1f}x")

    if skew_ratio > threshold_multiplier:
        print(f"\n  >>> SKEW DETECTED (ratio > {threshold_multiplier}x)")
        print(f"  >>> Top skewed keys:")
        skewed_keys = key_counts.filter(F.col("count") > threshold) \
            .orderBy(F.desc("count")) \
            .limit(10)
        skewed_keys.show(truncate=False)
        print(f"  >>> ACTION: Apply salting, broadcast join, or isolate-and-union strategy.")
    else:
        print(f"  >>> Distribution looks healthy (skew ratio < {threshold_multiplier}x)")

# --- CONFIGURE: Run skew detection on your DataFrames ---
# Example:
# detect_skew(spark.table("my_lakehouse.dbo.fact_sales"), "customer_id")

# %% [markdown]
# ## 5. Recommendations Summary

# %%
print("=" * 60)
print("  PERFORMANCE RECOMMENDATIONS SUMMARY")
print("=" * 60)
print("""
Review the output above and take the following actions as needed:

1. CONFIGURATION
   - If shuffle.partitions = 200, tune to 2-3x your executor cores.
   - If autotune is disabled and on Runtime 1.1/1.2, enable it.
   - If VOrder is disabled and tables are read by Power BI, enable it.

2. TABLE HEALTH
   - Run OPTIMIZE on tables with small files or high file counts.
   - Schedule regular table maintenance for active tables.
   - Review partition strategy for over-partitioned tables.

3. QUERY PERFORMANCE
   - Use broadcast hints for small dimension table joins.
   - Add predicate pushdown (filter early in the pipeline).
   - Select only needed columns to reduce I/O.

4. SKEW
   - Apply salting or broadcast strategies for skewed join keys.
   - Consider isolate-and-union for a small number of hot keys.

5. CAPACITY
   - Monitor Spark VCore utilization in the Capacity Metrics app.
   - Cancel idle notebook sessions to free VCores.
   - Consider autoscale billing for bursty workloads.
""")
print("=" * 60)
