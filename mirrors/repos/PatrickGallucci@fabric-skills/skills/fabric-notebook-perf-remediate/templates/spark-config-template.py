"""
Fabric Notebook Spark Configuration Template
==============================================
Place this as the FIRST cell in your Fabric notebook to apply optimized
Spark session settings before any data operations.

Customize the settings below based on your workload type.
See the comments for guidance on when to adjust each setting.
"""

# ── Core Performance ────────────────────────────────────────────────────
# Native Execution Engine: 2x-5x performance boost. Always enable.
spark.conf.set("spark.native.enabled", "true")

# Adaptive Query Execution: auto-optimizes shuffles, joins, and skew.
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# ── Shuffle Tuning ──────────────────────────────────────────────────────
# Default is 200. Adjust based on data volume:
#   < 1 GB  → 10-20
#   1-10 GB → 50-100
#   > 10 GB → 200 (default) or higher
spark.conf.set("spark.sql.shuffle.partitions", "100")

# ── Read Optimization ───────────────────────────────────────────────────
# Max partition size for input files (default 128 MB).
# Increase for fewer, larger partitions; decrease for more parallelism.
spark.conf.set("spark.sql.files.maxPartitionBytes", "128m")

# Broadcast join threshold (default 10 MB).
# Increase if small dimension tables are not being broadcast automatically.
# spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")

# ── Write Optimization ──────────────────────────────────────────────────
# Auto Compaction: merges small files after writes. Enable for ingestion.
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")

# Optimize Write: reduces output file count, targets ~128 MB file size.
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# ── V-Order ─────────────────────────────────────────────────────────────
# V-Order: optimizes Parquet for fast reads across Fabric engines.
# Enable for read-heavy / dashboard workloads.
# Disable (default) for write-heavy ingestion pipelines.
# spark.conf.set("spark.sql.parquet.vorder.default", "true")

# ── Autotune (Optional) ────────────────────────────────────────────────
# Learns optimal config over ~20-25 iterations. Compatible with RT 1.1-1.2.
# Does not work with high concurrency mode or private endpoints.
# spark.conf.set("spark.ms.autotune.enabled", "true")

# ── Task Parallelism ───────────────────────────────────────────────────
# Default is 1 core per task. Adjust for specific workloads:
#   CPU-bound (no memory pressure) → 0.5 (more parallelism)
#   Memory-intensive (OOM errors)  → 2   (more memory per task)
# spark.conf.set("spark.task.cpus", "1")

print("Spark session configured successfully.")
