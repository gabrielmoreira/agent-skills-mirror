"""
Fabric Notebook Performance Health Check
=========================================
Run this script in a Fabric notebook cell to audit your current Spark session
configuration and identify common performance issues.

Usage:
    Copy this entire script into a notebook cell and execute it.
    Review the output for warnings and recommendations.
"""

from pyspark.sql import SparkSession

def get_config_safely(spark, key, default="NOT SET"):
    """Retrieve a Spark configuration value safely."""
    try:
        return spark.conf.get(key)
    except Exception:
        return default

def run_health_check():
    """Run a comprehensive health check on the current Spark session."""

    spark = SparkSession.builder.getOrCreate()

    print("=" * 70)
    print("  FABRIC NOTEBOOK PERFORMANCE HEALTH CHECK")
    print("=" * 70)

    warnings = []
    info = []

    # ── 1. Native Execution Engine ──────────────────────────────────────
    nee = get_config_safely(spark, "spark.native.enabled", "false")
    print(f"\n[1] Native Execution Engine (NEE): {nee}")
    if nee.lower() != "true":
        warnings.append(
            "NEE is DISABLED. Enable for 2x-5x performance gain:\n"
            "    spark.conf.set('spark.native.enabled', 'true')"
        )
    else:
        info.append("NEE is enabled.")

    # ── 2. Adaptive Query Execution ─────────────────────────────────────
    aqe = get_config_safely(spark, "spark.sql.adaptive.enabled", "false")
    aqe_coalesce = get_config_safely(
        spark, "spark.sql.adaptive.coalescePartitions.enabled", "false"
    )
    aqe_skew = get_config_safely(
        spark, "spark.sql.adaptive.skewJoin.enabled", "false"
    )
    print(f"\n[2] Adaptive Query Execution (AQE): {aqe}")
    print(f"    Coalesce partitions: {aqe_coalesce}")
    print(f"    Skew join optimization: {aqe_skew}")
    if aqe.lower() != "true":
        warnings.append(
            "AQE is DISABLED. Enable for automatic shuffle and skew optimization:\n"
            "    spark.conf.set('spark.sql.adaptive.enabled', 'true')\n"
            "    spark.conf.set('spark.sql.adaptive.coalescePartitions.enabled', 'true')\n"
            "    spark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')"
        )

    # ── 3. Shuffle Partitions ───────────────────────────────────────────
    shuffle_parts = get_config_safely(
        spark, "spark.sql.shuffle.partitions", "200"
    )
    print(f"\n[3] Shuffle partitions: {shuffle_parts}")
    if shuffle_parts == "200":
        info.append(
            "Shuffle partitions at default (200). Consider tuning based on data volume:\n"
            "    < 1 GB: 10-20  |  1-10 GB: 50-100  |  > 100 GB: 400-2000"
        )

    # ── 4. Max Partition Bytes ──────────────────────────────────────────
    max_part_bytes = get_config_safely(
        spark, "spark.sql.files.maxPartitionBytes", "134217728"
    )
    print(f"\n[4] Max partition bytes (read): {max_part_bytes}")

    # ── 5. Task CPUs ────────────────────────────────────────────────────
    task_cpus = get_config_safely(spark, "spark.task.cpus", "1")
    print(f"\n[5] Task CPUs: {task_cpus}")

    # ── 6. Autotune ────────────────────────────────────────────────────
    autotune = get_config_safely(
        spark, "spark.ms.autotune.enabled", "false"
    )
    print(f"\n[6] Autotune: {autotune}")
    if autotune.lower() != "true":
        info.append(
            "Autotune is disabled. Consider enabling for adaptive optimization:\n"
            "    spark.conf.set('spark.ms.autotune.enabled', 'true')"
        )

    # ── 7. V-Order ──────────────────────────────────────────────────────
    vorder = get_config_safely(
        spark, "spark.sql.parquet.vorder.default", "false"
    )
    print(f"\n[7] V-Order (session default): {vorder}")
    if vorder.lower() == "true":
        info.append(
            "V-Order is ENABLED at session level. All writes use V-Order.\n"
            "    Disable for write-heavy ingestion pipelines if write speed is priority."
        )
    else:
        info.append(
            "V-Order is disabled. Enable for read-heavy / dashboard workloads:\n"
            "    spark.conf.set('spark.sql.parquet.vorder.default', 'true')"
        )

    # ── 8. Auto Compaction ──────────────────────────────────────────────
    auto_compact = get_config_safely(
        spark, "spark.databricks.delta.autoCompact.enabled", "false"
    )
    print(f"\n[8] Auto Compaction: {auto_compact}")
    if auto_compact.lower() != "true":
        info.append(
            "Auto Compaction is disabled. Enable for frequent small writes:\n"
            "    spark.conf.set('spark.databricks.delta.autoCompact.enabled', 'true')"
        )

    # ── 9. Optimize Write ───────────────────────────────────────────────
    opt_write = get_config_safely(
        spark, "spark.microsoft.delta.optimizeWrite.enabled", "false"
    )
    print(f"\n[9] Optimize Write: {opt_write}")

    # ── 10. Broadcast Join Threshold ────────────────────────────────────
    broadcast_threshold = get_config_safely(
        spark, "spark.sql.autoBroadcastJoinThreshold", "10485760"
    )
    print(f"\n[10] Broadcast join threshold: {broadcast_threshold} bytes")

    # ── Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for i, w in enumerate(warnings, 1):
            print(f"\n  [{i}] {w}")

    if info:
        print(f"\n  RECOMMENDATIONS ({len(info)}):")
        for i, item in enumerate(info, 1):
            print(f"\n  [{i}] {item}")

    if not warnings:
        print("\n  No critical warnings found.")

    print("\n" + "=" * 70)
    print("  Health check complete. Apply recommendations and re-run to verify.")
    print("=" * 70)


# Execute
run_health_check()
