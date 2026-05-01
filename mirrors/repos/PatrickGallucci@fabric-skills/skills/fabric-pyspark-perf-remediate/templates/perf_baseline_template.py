"""
Performance Baseline Template - Microsoft Fabric PySpark

Use this template to establish performance baselines for your PySpark workloads.
Includes timing instrumentation, configuration capture, and comparison utilities.

Instructions:
    1. Copy this template into a new Fabric notebook
    2. Replace the placeholder sections with your actual transformations
    3. Run the notebook to capture baseline metrics
    4. After making optimizations, re-run to compare
"""

import time
import json
from datetime import datetime
from contextlib import contextmanager
from pyspark.sql import functions as F

# ============================================================
#  CONFIGURATION - Tune these for your workload
# ============================================================

# Performance-optimized session settings (uncomment as needed)
# spark.conf.set("spark.sql.shuffle.partitions", "auto")
# spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50m")
# spark.conf.set("spark.sql.files.maxPartitionBytes", "256m")
# spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
# spark.conf.set("spark.sql.adaptive.enabled", "true")
# spark.conf.set("spark.native.enabled", "true")

# ============================================================
#  TIMING UTILITIES
# ============================================================

class PerfTracker:
    """Track and report execution times for notebook operations."""

    def __init__(self, run_name: str = "baseline"):
        self.run_name = run_name
        self.timings = []
        self.start_time = datetime.now()

    @contextmanager
    def track(self, operation_name: str):
        """Context manager to time an operation."""
        start = time.time()
        print(f"  [START] {operation_name}...")
        yield
        elapsed = time.time() - start
        self.timings.append({
            "operation": operation_name,
            "duration_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat()
        })
        print(f"  [DONE]  {operation_name} - {elapsed:.2f}s")

    def report(self):
        """Print a summary report of all tracked operations."""
        total = sum(t["duration_seconds"] for t in self.timings)

        print(f"\n{'='*60}")
        print(f"  PERFORMANCE REPORT: {self.run_name}")
        print(f"  Run started: {self.start_time.isoformat()}")
        print(f"{'='*60}")
        print(f"\n  {'Operation':<40} {'Duration (s)':<15} {'% of Total'}")
        print(f"  {'-'*40} {'-'*15} {'-'*10}")

        for t in self.timings:
            pct = (t["duration_seconds"] / total * 100) if total > 0 else 0
            print(f"  {t['operation']:<40} {t['duration_seconds']:<15.2f} {pct:.1f}%")

        print(f"\n  {'TOTAL':<40} {total:<15.2f} 100.0%")
        print(f"{'='*60}\n")

    def to_dict(self):
        """Export timings as a dictionary for comparison."""
        return {
            "run_name": self.run_name,
            "start_time": self.start_time.isoformat(),
            "total_seconds": sum(t["duration_seconds"] for t in self.timings),
            "operations": self.timings
        }

    def capture_config(self, spark):
        """Capture current Spark configuration for reproducibility."""
        key_configs = [
            "spark.sql.shuffle.partitions",
            "spark.sql.autoBroadcastJoinThreshold",
            "spark.sql.files.maxPartitionBytes",
            "spark.sql.adaptive.enabled",
            "spark.microsoft.delta.optimizeWrite.enabled",
            "spark.ms.autotune.enabled",
            "spark.native.enabled",
            "spark.sql.parquet.vorder.default",
            "spark.executor.memory",
            "spark.executor.cores",
            "spark.driver.memory",
        ]
        config = {}
        for key in key_configs:
            try:
                config[key] = spark.conf.get(key)
            except Exception:
                config[key] = "(not set)"

        print(f"\n  Captured Spark Configuration:")
        for k, v in config.items():
            print(f"    {k}: {v}")

        return config


# ============================================================
#  INITIALIZE TRACKER
# ============================================================

# Change run_name to identify this run (e.g., "baseline", "after-broadcast-fix")
perf = PerfTracker(run_name="baseline")

# Capture configuration
config = perf.capture_config(spark)

# ============================================================
#  YOUR WORKLOAD - Replace with your actual transformations
# ============================================================

# --- Step 1: Read Source Data ---
with perf.track("Read source table"):
    # REPLACE with your actual table read
    # df_source = spark.table("your_source_table")
    # row_count = df_source.count()
    # print(f"    Source rows: {row_count:,}")
    pass  # Remove this line when adding your code

# --- Step 2: Transform / Join ---
with perf.track("Apply transformations"):
    # REPLACE with your actual transformations
    # df_transformed = df_source \
    #     .filter(F.col("date") >= "2025-01-01") \
    #     .groupBy("category") \
    #     .agg(F.sum("amount").alias("total_amount"))
    pass  # Remove this line when adding your code

# --- Step 3: Join with dimension ---
with perf.track("Join with dimension table"):
    # REPLACE with your actual join
    # df_dim = spark.table("dimension_table")
    # df_joined = df_transformed.join(broadcast(df_dim), "dim_key")
    pass  # Remove this line when adding your code

# --- Step 4: Write results ---
with perf.track("Write to Delta table"):
    # REPLACE with your actual write
    # df_joined.write.format("delta") \
    #     .mode("overwrite") \
    #     .save("Tables/output_table")
    pass  # Remove this line when adding your code

# ============================================================
#  REPORT
# ============================================================

perf.report()

# To save results for later comparison:
# results = perf.to_dict()
# spark.createDataFrame([results]).write.format("delta") \
#     .mode("append").save("Tables/_perf_baselines")
