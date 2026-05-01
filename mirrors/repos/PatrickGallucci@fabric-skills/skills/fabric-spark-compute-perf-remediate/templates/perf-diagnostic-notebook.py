# ============================================================================
# Fabric Delta Lake & Spark Performance Diagnostic Notebook
# ============================================================================
# Purpose: Comprehensive diagnostics for Spark compute and Delta table health.
# Usage:   Paste into a Fabric notebook. Update TABLE_NAME and run all cells.
# ============================================================================

# %% [markdown]
# # Performance Diagnostic Notebook
# Run each section to identify performance bottlenecks in your Fabric Lakehouse.

# %% Configuration - UPDATE THESE VALUES
TABLE_NAME = "your_table_name"           # Delta table to diagnose
SCHEMA_NAME = "dbo"                       # Schema (default: dbo)
FULL_TABLE = f"{SCHEMA_NAME}.{TABLE_NAME}" if SCHEMA_NAME else TABLE_NAME

# %% [markdown]
# ## 1. Session & Environment Info

# %%
import time
start_time = time.time()
spark.sql("SELECT 1").collect()
startup_seconds = time.time() - start_time
print(f"Session startup/warm-up: {startup_seconds:.1f} seconds")

print(f"\nSpark Version  : {spark.version}")
print(f"App Name       : {spark.sparkContext.appName}")
print(f"App ID         : {spark.sparkContext.applicationId}")
print(f"Master         : {spark.sparkContext.master}")
print(f"Default Parallelism: {spark.sparkContext.defaultParallelism}")

# %% [markdown]
# ## 2. Active Spark Configuration

# %%
key_properties = [
    "spark.sql.parquet.vorder.default",
    "spark.microsoft.delta.optimizeWrite.enabled",
    "spark.ms.autotune.enabled",
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.fabric.nativeExecution.enabled",
    "spark.sql.shuffle.partitions",
    "spark.sql.autoBroadcastJoinThreshold",
    "spark.dynamicAllocation.enabled",
    "spark.dynamicAllocation.minExecutors",
    "spark.dynamicAllocation.maxExecutors",
    "spark.executor.memory",
    "spark.executor.cores",
    "spark.driver.memory",
    "spark.driver.cores",
    "spark.databricks.delta.retentionDurationCheck.enabled",
]

print("=== Key Spark Configuration ===\n")
for prop in key_properties:
    try:
        val = spark.conf.get(prop)
    except Exception:
        val = "(not set)"
    status = ""
    # Flag potential issues
    if prop == "spark.sql.parquet.vorder.default" and val.lower() != "true":
        status = " ⚠️  VOrder disabled (read performance may suffer)"
    elif prop == "spark.sql.adaptive.enabled" and val.lower() != "true":
        status = " ⚠️  AQE disabled"
    elif prop == "spark.microsoft.delta.optimizeWrite.enabled" and val.lower() != "true":
        status = " ℹ️  Optimized Write disabled"
    print(f"  {prop} = {val}{status}")

# %% [markdown]
# ## 3. Delta Table Health Check

# %%
from delta.tables import DeltaTable
import pyspark.sql.functions as F

print(f"=== Delta Table Health: {FULL_TABLE} ===\n")

try:
    # Table details
    detail = spark.sql(f"DESCRIBE DETAIL {FULL_TABLE}")
    detail_row = detail.collect()[0]

    num_files = detail_row["numFiles"]
    size_bytes = detail_row["sizeInBytes"]
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_bytes / (1024 * 1024 * 1024)
    avg_file_mb = (size_bytes / num_files / (1024 * 1024)) if num_files > 0 else 0
    partitions = detail_row["partitionColumns"]
    table_format = detail_row["format"]

    print(f"  Format           : {table_format}")
    print(f"  Total Size       : {size_gb:.2f} GB ({size_mb:.0f} MB)")
    print(f"  Total Files      : {num_files:,}")
    print(f"  Avg File Size    : {avg_file_mb:.1f} MB")
    print(f"  Partition Columns: {partitions if partitions else 'None'}")

    # Health assessment
    print(f"\n  --- Health Assessment ---")

    if avg_file_mb < 32 and num_files > 10:
        print(f"  ❌ SMALL FILE PROBLEM: Avg file size {avg_file_mb:.1f} MB (target: 128–1024 MB)")
        print(f"     → Run: OPTIMIZE {FULL_TABLE} VORDER")
    elif avg_file_mb < 128:
        print(f"  ⚠️  Files below optimal size ({avg_file_mb:.1f} MB). Consider OPTIMIZE.")
    else:
        print(f"  ✅ File sizes healthy ({avg_file_mb:.1f} MB avg)")

    if num_files > 10000:
        print(f"  ⚠️  High file count ({num_files:,}). May slow file listing operations.")
        print(f"     → Run OPTIMIZE to compact, then VACUUM to remove old files.")
    else:
        print(f"  ✅ File count acceptable ({num_files:,})")

    if partitions and len(partitions) > 3:
        print(f"  ⚠️  Over-partitioned ({len(partitions)} columns). Consider reducing.")
    elif partitions:
        print(f"  ✅ Partition column count OK ({len(partitions)})")

except Exception as e:
    print(f"  ❌ Error analyzing table: {e}")

# %% [markdown]
# ## 4. Delta Table History (Recent Operations)

# %%
print(f"=== Recent Delta Operations: {FULL_TABLE} ===\n")

try:
    history = spark.sql(f"DESCRIBE HISTORY {FULL_TABLE} LIMIT 20")
    history.select("version", "timestamp", "operation", "operationMetrics").show(20, truncate=False)

    # Check for maintenance operations
    ops = history.select("operation").distinct().collect()
    op_list = [row["operation"] for row in ops]

    has_optimize = "OPTIMIZE" in op_list
    has_vacuum = "VACUUM START" in op_list or "VACUUM END" in op_list

    if not has_optimize:
        print("  ⚠️  No OPTIMIZE operations in recent history.")
        print(f"     → Run: OPTIMIZE {FULL_TABLE} VORDER")
    else:
        print("  ✅ OPTIMIZE has been run recently.")

    if not has_vacuum:
        print("  ⚠️  No VACUUM operations in recent history.")
        print(f"     → Run: VACUUM {FULL_TABLE} RETAIN 168 HOURS")
    else:
        print("  ✅ VACUUM has been run recently.")

except Exception as e:
    print(f"  ❌ Error reading history: {e}")

# %% [markdown]
# ## 5. Partition Skew Analysis

# %%
print(f"=== Partition Skew Analysis: {FULL_TABLE} ===\n")

try:
    df = spark.read.format("delta").table(FULL_TABLE)

    partition_stats = df.withColumn("_part_id", F.spark_partition_id()) \
        .groupBy("_part_id") \
        .count() \
        .agg(
            F.count("count").alias("num_partitions"),
            F.min("count").alias("min_rows"),
            F.max("count").alias("max_rows"),
            F.round(F.avg("count"), 0).alias("avg_rows"),
            F.round(F.stddev("count"), 0).alias("stddev_rows")
        ).collect()[0]

    num_parts = partition_stats["num_partitions"]
    min_rows = partition_stats["min_rows"]
    max_rows = partition_stats["max_rows"]
    avg_rows = partition_stats["avg_rows"]
    stddev_rows = partition_stats["stddev_rows"] or 0

    print(f"  Spark Partitions : {num_parts}")
    print(f"  Min Rows/Part    : {min_rows:,.0f}")
    print(f"  Max Rows/Part    : {max_rows:,.0f}")
    print(f"  Avg Rows/Part    : {avg_rows:,.0f}")
    print(f"  StdDev           : {stddev_rows:,.0f}")

    skew_ratio = max_rows / avg_rows if avg_rows > 0 else 0
    print(f"  Skew Ratio       : {skew_ratio:.1f}x")

    if skew_ratio > 10:
        print(f"\n  ❌ SEVERE SKEW detected (max is {skew_ratio:.0f}x average)")
        print(f"     → Enable AQE skew join: spark.sql.adaptive.skewJoin.enabled = true")
        print(f"     → Consider salting technique for skewed join keys")
    elif skew_ratio > 3:
        print(f"\n  ⚠️  Moderate skew detected ({skew_ratio:.1f}x)")
        print(f"     → AQE should handle this if enabled")
    else:
        print(f"\n  ✅ Partition distribution is balanced")

except Exception as e:
    print(f"  ❌ Error analyzing partitions: {e}")

# %% [markdown]
# ## 6. Summary & Recommendations

# %%
print("=" * 60)
print("  PERFORMANCE DIAGNOSTIC SUMMARY")
print("=" * 60)
print(f"\n  Table: {FULL_TABLE}")
print(f"  Run at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
print()
print("  Review the output above for ❌ and ⚠️ indicators.")
print("  Prioritize fixes in this order:")
print("    1. Fix small file problems (OPTIMIZE)")
print("    2. Enable VOrder for read workloads")
print("    3. Address data skew (AQE or salting)")
print("    4. Right-size executor memory if OOM errors occur")
print("    5. Schedule regular VACUUM to reclaim storage")
print("    6. Enable Native Execution Engine for SQL-heavy workloads")
print()
print("  For detailed guidance on each issue, see the skill references/")
print("  directory or the linked Microsoft documentation.")
print("=" * 60)
