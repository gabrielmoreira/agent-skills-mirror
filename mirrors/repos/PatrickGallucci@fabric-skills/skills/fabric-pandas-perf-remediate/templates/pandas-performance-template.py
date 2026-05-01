# Fabric Pandas Performance Template
# ===================================
# Memory-safe pandas workflow template for Microsoft Fabric Spark notebooks.
# Copy this into your notebook as a starting point for pandas-heavy workloads.
#
# Usage:
#   1. Paste Cell 1 as your first notebook cell (configuration)
#   2. Use the helper functions throughout your notebook
#   3. Follow the pattern: Spark processing → size check → pandas conversion

# =============================================================================
# CELL 1: Spark Configuration for Pandas Optimization
# =============================================================================
# Run this as the FIRST cell in your notebook

# Arrow-based columnar transfer (3-100x faster toPandas/createDataFrame)
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
spark.conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")

# Adaptive Query Execution for automatic partition optimization
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Increase broadcast threshold for medium lookup tables
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "104857600")  # 100 MB

# Increase max result size for larger toPandas() conversions
spark.conf.set("spark.driver.maxResultSize", "4g")

# Resource profile optimized for read-heavy notebook workloads
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")

print("✅ Pandas-optimized Spark configuration applied")

# =============================================================================
# CELL 2: Memory Monitoring Utilities
# =============================================================================
import os
import psutil
import functools
import time
import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql.functions import broadcast


def check_memory(label=""):
    """Report current driver memory usage."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    sys_mem = psutil.virtual_memory()
    rss_gb = mem_info.rss / 1024**3
    total_gb = sys_mem.total / 1024**3
    pct = sys_mem.percent
    
    status = "🟢" if pct < 70 else "🟡" if pct < 85 else "🔴"
    prefix = f"[{label}] " if label else ""
    print(f"{status} {prefix}RSS: {rss_gb:.2f} GB | System: {sys_mem.used / 1024**3:.2f}/{total_gb:.2f} GB ({pct}%)")
    
    if pct > 85:
        print("⚠️  WARNING: Memory usage above 85% — risk of OOM on next toPandas() call")
    return rss_gb


def track_memory(func):
    """Decorator to track memory delta of any function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mem_before = check_memory(f"{func.__name__} START")
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        mem_after = check_memory(f"{func.__name__} END")
        delta = mem_after - mem_before
        print(f"   ⏱️  Duration: {elapsed:.2f}s | Memory Δ: {delta:+.2f} GB")
        return result
    return wrapper


print("✅ Memory monitoring utilities loaded")

# =============================================================================
# CELL 3: Safe DataFrame Conversion Helpers
# =============================================================================

def safe_to_pandas(spark_df, max_rows=1_000_000, max_gb=4.0, label="DataFrame"):
    """
    Safely convert Spark DataFrame to pandas with size checks.
    
    Args:
        spark_df: PySpark DataFrame
        max_rows: Maximum row count allowed (default 1M)
        max_gb: Maximum estimated size in GB (default 4.0)
        label: Label for logging
    
    Returns:
        pandas DataFrame or raises ValueError if too large
    """
    # Count rows
    row_count = spark_df.count()
    print(f"📊 [{label}] Row count: {row_count:,}")
    
    if row_count > max_rows:
        raise ValueError(
            f"❌ [{label}] {row_count:,} rows exceeds limit of {max_rows:,}. "
            f"Filter/aggregate in Spark first, or increase max_rows parameter."
        )
    
    # Estimate size (rough: row_count × num_columns × avg_bytes_per_cell)
    num_cols = len(spark_df.columns)
    estimated_gb = (row_count * num_cols * 50) / (1024**3)  # ~50 bytes avg per cell
    print(f"📊 [{label}] Estimated size: ~{estimated_gb:.2f} GB ({num_cols} columns)")
    
    if estimated_gb > max_gb:
        raise ValueError(
            f"❌ [{label}] Estimated {estimated_gb:.1f} GB exceeds limit of {max_gb} GB. "
            f"Select fewer columns or filter more aggressively."
        )
    
    # Check available memory
    available_gb = psutil.virtual_memory().available / (1024**3)
    if estimated_gb > available_gb * 0.5:
        print(f"⚠️  [{label}] Estimated size ({estimated_gb:.1f} GB) is >50% of available memory ({available_gb:.1f} GB)")
    
    # Convert
    start = time.time()
    pdf = spark_df.toPandas()
    elapsed = time.time() - start
    actual_mb = pdf.memory_usage(deep=True).sum() / (1024**2)
    print(f"✅ [{label}] Converted in {elapsed:.2f}s | Actual size: {actual_mb:.1f} MB")
    
    return pdf


def optimize_pandas_dtypes(df):
    """Downcast pandas DataFrame dtypes to reduce memory footprint."""
    mem_before = df.memory_usage(deep=True).sum() / (1024**2)
    
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in df.select_dtypes(include=['object']).columns:
        nunique_ratio = df[col].nunique() / max(len(df), 1)
        if nunique_ratio < 0.5:
            df[col] = df[col].astype('category')
    
    mem_after = df.memory_usage(deep=True).sum() / (1024**2)
    reduction = (1 - mem_after / max(mem_before, 0.001)) * 100
    print(f"🔧 Dtype optimization: {mem_before:.1f} MB → {mem_after:.1f} MB ({reduction:.0f}% reduction)")
    return df


print("✅ Safe conversion helpers loaded")

# =============================================================================
# CELL 4: Example Usage Pattern
# =============================================================================
# Uncomment and adapt for your workload:

# # 1. Read data (stays distributed)
# spark_df = spark.read.format("delta").load("Tables/my_table")
#
# # 2. Heavy processing in Spark (distributed)
# processed = (spark_df
#     .filter(F.col("date") >= "2024-01-01")
#     .select("customer_id", "region", "revenue", "quantity")
#     .groupBy("region")
#     .agg(
#         F.sum("revenue").alias("total_revenue"),
#         F.count("customer_id").alias("customer_count"),
#         F.avg("quantity").alias("avg_quantity")
#     ))
#
# # 3. Safe conversion to pandas (with checks)
# check_memory("Before conversion")
# pdf = safe_to_pandas(processed, label="Regional Summary")
# pdf = optimize_pandas_dtypes(pdf)
# check_memory("After conversion")
#
# # 4. Pandas-specific operations
# pivot = pdf.pivot_table(index='region', values=['total_revenue', 'customer_count'])
# print(pivot)

# =============================================================================
# CELL 5: Spark Config Audit
# =============================================================================

def audit_spark_config():
    """Print current Spark configuration relevant to pandas performance."""
    configs = {
        "Arrow Transfer": "spark.sql.execution.arrow.pyspark.enabled",
        "Arrow Fallback": "spark.sql.execution.arrow.pyspark.fallback.enabled",
        "Arrow Batch Size": "spark.sql.execution.arrow.maxRecordsPerBatch",
        "Shuffle Partitions": "spark.sql.shuffle.partitions",
        "Broadcast Threshold": "spark.sql.autoBroadcastJoinThreshold",
        "AQE Enabled": "spark.sql.adaptive.enabled",
        "Driver Memory": "spark.driver.memory",
        "Max Result Size": "spark.driver.maxResultSize",
        "Autotune": "spark.ms.autotune.enabled",
        "Resource Profile": "spark.fabric.resourceProfile",
        "Native Engine": "spark.native.enabled",
        "VOrder Default": "spark.sql.parquet.vorder.default",
        "Optimized Write": "spark.databricks.delta.optimizeWrite.enabled",
    }
    print("=" * 60)
    print("  Spark Configuration Audit (Pandas Performance)")
    print("=" * 60)
    for label, key in configs.items():
        val = spark.conf.get(key, "NOT SET")
        print(f"  {label:.<35} {val}")
    print("=" * 60)

# audit_spark_config()  # Uncomment to run
