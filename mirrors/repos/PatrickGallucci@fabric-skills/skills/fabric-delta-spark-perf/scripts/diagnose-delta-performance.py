"""
Fabric Delta Lake Spark Performance Diagnostic Script
======================================================
Automated diagnostic scan for Delta tables in Microsoft Fabric.
Checks file health, detects data skew, and audits Spark configuration.

Usage (in a Fabric notebook):
    %run /path/to/diagnose-delta-performance

    # Scan a specific table
    diagnose_table("schema_name.table_name")

    # Scan a table with skew detection on a specific column
    diagnose_table("schema_name.table_name", skew_column="customer_id")

    # Audit current Spark configuration
    audit_spark_config()

    # Scan all tables in a schema
    diagnose_schema("schema_name")
"""

from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from delta.tables import DeltaTable


def get_spark():
    """Get or create SparkSession."""
    return SparkSession.builder.getOrCreate()


def diagnose_table(table_name, skew_column=None, file_size_threshold_mb=32):
    """
    Run a comprehensive diagnostic on a Delta table.

    Parameters
    ----------
    table_name : str
        Fully qualified table name (schema_name.table_name).
    skew_column : str, optional
        Column name to check for data skew distribution.
    file_size_threshold_mb : int, optional
        Minimum average file size in MB before flagging (default 32MB).

    Returns
    -------
    dict
        Diagnostic results with findings and recommendations.
    """
    spark = get_spark()
    results = {
        "table": table_name,
        "findings": [],
        "recommendations": [],
        "status": "HEALTHY"
    }

    print(f"\n{'='*60}")
    print(f"  DIAGNOSING: {table_name}")
    print(f"{'='*60}")

    # --- File Health Check ---
    print("\n[1/4] Checking file health...")
    try:
        detail = spark.sql(f"DESCRIBE DETAIL {table_name}").first()
        num_files = detail["numFiles"]
        size_bytes = detail["sizeInBytes"]
        size_gb = size_bytes / (1024**3)
        avg_file_mb = (size_bytes / max(num_files, 1)) / (1024**2)

        print(f"  Total files: {num_files:,}")
        print(f"  Total size:  {size_gb:.2f} GB")
        print(f"  Avg file:    {avg_file_mb:.1f} MB")

        if avg_file_mb < file_size_threshold_mb and num_files > 10:
            results["findings"].append(
                f"SMALL FILES: Average file size is {avg_file_mb:.1f} MB "
                f"(threshold: {file_size_threshold_mb} MB)"
            )
            results["recommendations"].append(
                f"Run: OPTIMIZE {table_name} VORDER;"
            )
            results["status"] = "NEEDS_ATTENTION"

        if num_files > 1000 and size_gb < 10:
            results["findings"].append(
                f"HIGH FILE COUNT: {num_files:,} files for only {size_gb:.2f} GB"
            )
            results["recommendations"].append(
                f"Run: OPTIMIZE {table_name} VORDER; -- consolidate files"
            )
            results["status"] = "NEEDS_ATTENTION"

        if avg_file_mb > 2048:
            results["findings"].append(
                f"OVERSIZED FILES: Average file size is {avg_file_mb:.1f} MB. "
                "Consider increasing parallelism on writes."
            )
            results["recommendations"].append(
                "Increase spark.sql.shuffle.partitions or use partitionBy()"
            )

    except Exception as e:
        results["findings"].append(f"FILE CHECK FAILED: {str(e)}")
        results["status"] = "ERROR"

    # --- Partition Check ---
    print("\n[2/4] Checking partition layout...")
    try:
        partitions = spark.sql(f"SHOW PARTITIONS {table_name}")
        part_count = partitions.count()
        print(f"  Partitions: {part_count}")

        if part_count > 500:
            results["findings"].append(
                f"OVER-PARTITIONED: {part_count} partitions. "
                "This can cause small file proliferation."
            )
            results["recommendations"].append(
                "Consider reducing partition cardinality or removing partitioning"
            )
            results["status"] = "NEEDS_ATTENTION"
    except Exception:
        print("  Not a partitioned table (or unable to read partitions)")

    # --- Data Skew Check ---
    print("\n[3/4] Checking data skew...")
    if skew_column:
        try:
            df = spark.table(table_name)
            stats = df.groupBy(skew_column) \
                .agg(F.count("*").alias("row_count")) \
                .orderBy(F.desc("row_count"))

            total_keys = stats.count()
            top_rows = stats.limit(5).collect()
            all_counts = stats.select("row_count").rdd.flatMap(lambda x: x).collect()

            if all_counts:
                median_idx = len(all_counts) // 2
                median_count = sorted(all_counts)[median_idx]
                max_count = all_counts[0]  # already sorted desc
                skew_ratio = max_count / max(median_count, 1)

                print(f"  Column: {skew_column}")
                print(f"  Distinct keys: {total_keys:,}")
                print(f"  Max key count: {max_count:,}")
                print(f"  Median count:  {median_count:,}")
                print(f"  Skew ratio:    {skew_ratio:.1f}x")

                if skew_ratio > 10:
                    results["findings"].append(
                        f"SEVERE SKEW on '{skew_column}': "
                        f"top key has {skew_ratio:.0f}x more rows than median"
                    )
                    results["recommendations"].append(
                        "Enable AQE skew join handling or apply key salting. "
                        "Check for NULL keys."
                    )
                    results["status"] = "NEEDS_ATTENTION"
                elif skew_ratio > 5:
                    results["findings"].append(
                        f"MODERATE SKEW on '{skew_column}': "
                        f"top key has {skew_ratio:.0f}x more rows than median"
                    )
                    results["recommendations"].append(
                        "Monitor performance. AQE should handle this automatically."
                    )

                # Check for null keys
                null_count = df.filter(F.col(skew_column).isNull()).count()
                if null_count > 0:
                    null_pct = (null_count / df.count()) * 100
                    print(f"  NULL keys:     {null_count:,} ({null_pct:.1f}%)")
                    if null_pct > 5:
                        results["findings"].append(
                            f"HIGH NULL RATE on '{skew_column}': "
                            f"{null_pct:.1f}% of rows have NULL keys"
                        )
                        results["recommendations"].append(
                            "Filter NULL keys before joins or handle separately"
                        )

                print(f"\n  Top 5 keys by row count:")
                for row in top_rows:
                    print(f"    {row[skew_column]}: {row['row_count']:,}")

        except Exception as e:
            results["findings"].append(f"SKEW CHECK FAILED: {str(e)}")
    else:
        print("  Skipped (no skew_column specified)")

    # --- Table Properties Check ---
    print("\n[4/4] Checking table properties...")
    try:
        props = spark.sql(f"SHOW TBLPROPERTIES {table_name}").collect()
        prop_dict = {row["key"]: row["value"] for row in props}

        vorder = prop_dict.get("delta.parquet.vorder.enabled", "not set")
        print(f"  V-Order enabled: {vorder}")

        if vorder == "not set" or vorder == "false":
            results["findings"].append(
                "V-ORDER DISABLED: Table does not have V-Order enabled"
            )
            results["recommendations"].append(
                "For read-heavy tables, enable V-Order: "
                f"ALTER TABLE {table_name} "
                "SET TBLPROPERTIES('delta.parquet.vorder.enabled' = 'true')"
            )

    except Exception as e:
        print(f"  Could not read table properties: {e}")

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"  DIAGNOSIS: {results['status']}")
    print(f"{'='*60}")

    if results["findings"]:
        print("\n  FINDINGS:")
        for i, f_item in enumerate(results["findings"], 1):
            print(f"    {i}. {f_item}")

    if results["recommendations"]:
        print("\n  RECOMMENDATIONS:")
        for i, r in enumerate(results["recommendations"], 1):
            print(f"    {i}. {r}")

    if not results["findings"]:
        print("\n  No issues detected. Table appears healthy.")

    print()
    return results


def audit_spark_config():
    """
    Audit the current Spark session configuration for performance.
    Prints current values and flags suboptimal settings.
    """
    spark = get_spark()

    print(f"\n{'='*60}")
    print(f"  SPARK CONFIGURATION AUDIT")
    print(f"{'='*60}")

    checks = [
        ("spark.fabric.resourceProfile", "not set", "Workload profile"),
        ("spark.sql.parquet.vorder.default", "false", "V-Order on writes"),
        ("spark.microsoft.delta.optimizeWrite.enabled", "varies", "Optimized Write"),
        ("spark.databricks.delta.optimizeWrite.binSize", "128", "Target file size (MB)"),
        ("spark.databricks.delta.stats.collect", "true", "Delta stats collection"),
        ("spark.sql.shuffle.partitions", "200", "Shuffle partitions"),
        ("spark.sql.autoBroadcastJoinThreshold", "10485760", "Broadcast threshold"),
        ("spark.sql.files.maxPartitionBytes", "134217728", "Max partition bytes"),
        ("spark.databricks.optimizer.adaptive.enabled", "true", "AQE enabled"),
        ("spark.sql.adaptive.coalescePartitions.enabled", "true", "AQE coalesce"),
        ("spark.sql.adaptive.skewJoin.enabled", "true", "AQE skew join"),
        ("spark.ms.autotune.enabled", "false", "Autotune"),
        ("spark.executor.memory", "varies", "Executor memory"),
        ("spark.executor.cores", "varies", "Executor cores"),
        ("spark.driver.memory", "varies", "Driver memory"),
    ]

    warnings = []

    for prop, default, description in checks:
        try:
            value = spark.conf.get(prop)
        except Exception:
            value = f"(default: {default})"

        print(f"  {description:30s} | {prop}")
        print(f"  {'':30s} | Value: {value}")

        # Flag potential issues
        if prop == "spark.databricks.optimizer.adaptive.enabled" and value == "false":
            warnings.append("AQE is DISABLED. Enable it for automatic query optimization.")
        if prop == "spark.sql.adaptive.skewJoin.enabled" and value == "false":
            warnings.append("AQE skew join is DISABLED. Enable for automatic skew handling.")

    if warnings:
        print(f"\n  WARNINGS:")
        for w in warnings:
            print(f"    - {w}")
    else:
        print(f"\n  No configuration warnings detected.")

    print()


def diagnose_schema(schema_name, skew_column=None, max_tables=50):
    """
    Run diagnostics on all Delta tables in a schema.

    Parameters
    ----------
    schema_name : str
        Schema name to scan.
    skew_column : str, optional
        Column to check for skew (must exist in all tables, or will be skipped).
    max_tables : int, optional
        Maximum number of tables to scan (default 50).
    """
    spark = get_spark()

    tables = spark.sql(f"SHOW TABLES IN {schema_name}").collect()
    print(f"\nFound {len(tables)} tables in schema '{schema_name}'")
    print(f"Scanning up to {max_tables} tables...\n")

    all_results = []
    for i, table_row in enumerate(tables[:max_tables]):
        table_name = f"{schema_name}.{table_row['tableName']}"
        try:
            result = diagnose_table(table_name, skew_column=skew_column)
            all_results.append(result)
        except Exception as e:
            print(f"  ERROR scanning {table_name}: {e}\n")

    # Summary
    needs_attention = [r for r in all_results if r["status"] == "NEEDS_ATTENTION"]
    errors = [r for r in all_results if r["status"] == "ERROR"]
    healthy = [r for r in all_results if r["status"] == "HEALTHY"]

    print(f"\n{'='*60}")
    print(f"  SCHEMA SUMMARY: {schema_name}")
    print(f"{'='*60}")
    print(f"  Healthy:         {len(healthy)}")
    print(f"  Needs attention: {len(needs_attention)}")
    print(f"  Errors:          {len(errors)}")

    if needs_attention:
        print(f"\n  Tables needing attention:")
        for r in needs_attention:
            print(f"    - {r['table']}")
            for rec in r["recommendations"]:
                print(f"      -> {rec}")

    print()
    return all_results
