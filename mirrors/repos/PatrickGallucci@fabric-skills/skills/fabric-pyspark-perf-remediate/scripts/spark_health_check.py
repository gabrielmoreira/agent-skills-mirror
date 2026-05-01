"""
Spark Health Check - Microsoft Fabric PySpark Diagnostic Script

Run this in a Fabric notebook to gather comprehensive session diagnostics
including Spark configuration, pool information, and environment details.

Usage:
    Copy this script into a notebook cell and execute.
    Review the output for configuration issues and optimization opportunities.
"""

from datetime import datetime

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def check_spark_config(spark):
    """Display critical Spark configuration settings."""
    print_section("SPARK CONFIGURATION")

    configs = [
        ("spark.sql.shuffle.partitions", "200", "Shuffle partition count"),
        ("spark.sql.autoBroadcastJoinThreshold", "10485760", "Broadcast join threshold (bytes)"),
        ("spark.sql.files.maxPartitionBytes", "134217728", "Max partition bytes for reads"),
        ("spark.sql.adaptive.enabled", "true", "Adaptive Query Execution"),
        ("spark.sql.adaptive.coalescePartitions.enabled", "true", "AQE partition coalescing"),
        ("spark.sql.adaptive.skewJoin.enabled", "true", "AQE skew join optimization"),
        ("spark.microsoft.delta.optimizeWrite.enabled", "false", "Delta Optimized Write"),
        ("spark.ms.autotune.enabled", "false", "Autotune (ML-based tuning)"),
        ("spark.native.enabled", "false", "Native Execution Engine"),
        ("spark.sql.parquet.vorder.default", "false", "VOrder encoding"),
        ("spark.memory.fraction", "0.6", "Memory fraction for execution+storage"),
        ("spark.memory.storageFraction", "0.5", "Storage fraction within memory"),
        ("spark.driver.memory", "N/A", "Driver memory"),
        ("spark.executor.memory", "N/A", "Executor memory"),
        ("spark.executor.cores", "N/A", "Executor cores"),
        ("spark.executor.instances", "N/A", "Executor instances"),
        ("spark.dynamicAllocation.enabled", "N/A", "Dynamic allocation"),
        ("spark.dynamicAllocation.minExecutors", "N/A", "Min executors"),
        ("spark.dynamicAllocation.maxExecutors", "N/A", "Max executors"),
    ]

    print(f"\n{'Setting':<55} {'Current Value':<20} {'Default':<15}")
    print(f"{'-'*55} {'-'*20} {'-'*15}")

    recommendations = []

    for key, default, description in configs:
        try:
            value = spark.conf.get(key)
        except Exception:
            value = "(not set)"

        flag = ""
        if value != default and default != "N/A":
            flag = " *"

        print(f"{key:<55} {str(value):<20} {default:<15}{flag}")

        # Generate recommendations
        if key == "spark.sql.adaptive.enabled" and value != "true":
            recommendations.append("ENABLE AQE: spark.conf.set('spark.sql.adaptive.enabled', 'true')")
        if key == "spark.microsoft.delta.optimizeWrite.enabled" and value != "true":
            recommendations.append("CONSIDER enabling Optimized Write for Delta tables")
        if key == "spark.sql.shuffle.partitions" and value == "200":
            recommendations.append("CONSIDER tuning shuffle partitions or using 'auto' with AQE")

    if recommendations:
        print(f"\nRecommendations:")
        for r in recommendations:
            print(f"  -> {r}")


def check_runtime_info(spark):
    """Display runtime and environment information."""
    print_section("RUNTIME INFORMATION")

    print(f"  Spark Version:     {spark.version}")
    print(f"  Timestamp:         {datetime.now().isoformat()}")

    try:
        runtime = spark.conf.get("spark.fabric.runtime.version", "(unknown)")
        print(f"  Fabric Runtime:    {runtime}")
    except Exception:
        print(f"  Fabric Runtime:    (unable to determine)")

    try:
        app_name = spark.conf.get("spark.app.name", "(unknown)")
        app_id = spark.sparkContext.applicationId
        print(f"  Application Name:  {app_name}")
        print(f"  Application ID:    {app_id}")
    except Exception:
        pass


def check_executor_status(spark):
    """Display executor count and status."""
    print_section("EXECUTOR STATUS")

    try:
        sc = spark.sparkContext
        # Get executor info from status tracker
        executors = sc._jsc.sc().getExecutorMemoryStatus()
        executor_count = executors.size() - 1  # Subtract driver

        print(f"  Active Executors:  {executor_count}")
        print(f"  Default Parallelism: {sc.defaultParallelism}")
    except Exception as e:
        print(f"  Unable to retrieve executor status: {e}")


def check_delta_tables(spark, table_names=None):
    """Check Delta table health for specified tables."""
    print_section("DELTA TABLE HEALTH")

    if table_names is None:
        # Auto-discover tables in the default lakehouse
        try:
            tables_df = spark.sql("SHOW TABLES")
            table_names = [
                row.tableName for row in tables_df.collect()
                if not row.tableName.startswith("_")
            ]
        except Exception:
            print("  No default lakehouse attached or no tables found.")
            print("  Attach a lakehouse or pass table_names=['table1', 'table2']")
            return

    if not table_names:
        print("  No tables found to analyze.")
        return

    print(f"\n  {'Table':<30} {'Files':<10} {'Size (MB)':<15} {'Partitions'}")
    print(f"  {'-'*30} {'-'*10} {'-'*15} {'-'*20}")

    for table in table_names[:10]:  # Limit to 10 tables
        try:
            detail = spark.sql(f"DESCRIBE DETAIL {table}").collect()[0]
            num_files = detail.numFiles
            size_mb = detail.sizeInBytes / (1024 * 1024)
            partitions = detail.partitionColumns if detail.partitionColumns else "None"

            flag = ""
            if num_files > 1000:
                flag = " [!] Run OPTIMIZE"
            elif num_files > 5000:
                flag = " [!!] OPTIMIZE urgently needed"

            print(f"  {table:<30} {num_files:<10} {size_mb:<15.1f} {str(partitions)}{flag}")
        except Exception as e:
            print(f"  {table:<30} Error: {str(e)[:50]}")


def run_health_check(spark, table_names=None):
    """Run the complete health check."""
    print(f"\n{'#'*70}")
    print(f"  MICROSOFT FABRIC SPARK HEALTH CHECK")
    print(f"  Generated: {datetime.now().isoformat()}")
    print(f"{'#'*70}")

    check_runtime_info(spark)
    check_spark_config(spark)
    check_executor_status(spark)
    check_delta_tables(spark, table_names)

    print(f"\n{'='*70}")
    print(f"  HEALTH CHECK COMPLETE")
    print(f"{'='*70}\n")


# Execute health check
# Uncomment and customize the table_names parameter as needed:
# run_health_check(spark, table_names=["events", "orders", "customers"])
run_health_check(spark)
