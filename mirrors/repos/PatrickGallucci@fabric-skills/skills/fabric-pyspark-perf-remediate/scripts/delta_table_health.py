"""
Delta Table Health Check - Microsoft Fabric PySpark Diagnostic Script

Analyzes Delta table file sizes, transaction history, and maintenance
status to identify optimization opportunities.

Usage:
    Copy this script into a notebook cell. Modify the table_name
    parameter at the bottom and execute.
"""

from pyspark.sql import functions as F
from datetime import datetime, timedelta


def analyze_delta_table(spark, table_name: str):
    """
    Comprehensive Delta table health analysis.

    Args:
        spark: Active SparkSession
        table_name: Name of the Delta table to analyze
    """
    print(f"\n{'#'*60}")
    print(f"  DELTA TABLE HEALTH: {table_name}")
    print(f"  Generated: {datetime.now().isoformat()}")
    print(f"{'#'*60}")

    # ---- Table Detail ----
    print(f"\n{'='*60}")
    print(f"  TABLE DETAILS")
    print(f"{'='*60}")

    try:
        detail = spark.sql(f"DESCRIBE DETAIL {table_name}").collect()[0]
        size_gb = detail.sizeInBytes / (1024**3)
        size_mb = detail.sizeInBytes / (1024**2)

        print(f"  Name:            {detail.name}")
        print(f"  Format:          {detail.format}")
        print(f"  Location:        {detail.location}")
        print(f"  Num Files:       {detail.numFiles:,}")
        print(f"  Size:            {size_gb:.2f} GB ({size_mb:.0f} MB)")
        print(f"  Partitions:      {detail.partitionColumns or 'None'}")
        print(f"  Created:         {detail.createdAt}")
        print(f"  Last Modified:   {detail.lastModified}")

        # File size analysis
        if detail.numFiles > 0:
            avg_file_mb = size_mb / detail.numFiles
            print(f"\n  Avg File Size:   {avg_file_mb:.1f} MB")

            if avg_file_mb < 1:
                print(f"  ** CRITICAL: Very small files ({avg_file_mb:.2f} MB avg) **")
                print(f"  Run: OPTIMIZE {table_name}")
            elif avg_file_mb < 32:
                print(f"  * WARNING: Small files ({avg_file_mb:.1f} MB avg) *")
                print(f"  Consider running: OPTIMIZE {table_name}")
            elif avg_file_mb < 64:
                print(f"  ~ Acceptable but could be better ({avg_file_mb:.1f} MB avg)")
            else:
                print(f"  File sizes look healthy ({avg_file_mb:.1f} MB avg)")

        if detail.numFiles > 10000:
            print(f"\n  ** FILE COUNT WARNING: {detail.numFiles:,} files **")
            print(f"  Excessive file count degrades read performance.")
            print(f"  Run: OPTIMIZE {table_name}")
            print(f"  Then: VACUUM {table_name} RETAIN 168 HOURS")

    except Exception as e:
        print(f"  Error getting table details: {e}")
        return

    # ---- Table History ----
    print(f"\n{'='*60}")
    print(f"  RECENT HISTORY (Last 20 Operations)")
    print(f"{'='*60}")

    try:
        history = spark.sql(f"DESCRIBE HISTORY {table_name} LIMIT 20").collect()

        print(f"\n  {'Version':<8} {'Timestamp':<22} {'Operation':<20} {'Parameters'}")
        print(f"  {'-'*8} {'-'*22} {'-'*20} {'-'*30}")

        optimize_count = 0
        vacuum_count = 0
        last_optimize = None

        for row in history:
            ts = str(row.timestamp)[:19] if row.timestamp else "N/A"
            op = row.operation or "N/A"
            params = str(row.operationParameters)[:40] if row.operationParameters else ""

            print(f"  {row.version:<8} {ts:<22} {op:<20} {params}")

            if op == "OPTIMIZE":
                optimize_count += 1
                if last_optimize is None:
                    last_optimize = row.timestamp
            if op == "VACUUM START" or op == "VACUUM END":
                vacuum_count += 1

        print(f"\n  Maintenance Summary (in last 20 operations):")
        print(f"    OPTIMIZE runs:  {optimize_count}")
        print(f"    VACUUM runs:    {vacuum_count}")

        if optimize_count == 0:
            print(f"\n  * WARNING: No OPTIMIZE found in recent history *")
            print(f"  Schedule regular OPTIMIZE for tables with frequent writes.")

        if last_optimize:
            days_since = (datetime.now() - last_optimize.replace(tzinfo=None)).days
            if days_since > 7:
                print(f"  * Last OPTIMIZE was {days_since} days ago - consider running again *")

    except Exception as e:
        print(f"  Error getting history: {e}")

    # ---- Schema Info ----
    print(f"\n{'='*60}")
    print(f"  SCHEMA")
    print(f"{'='*60}")

    try:
        schema = spark.table(table_name).schema
        print(f"\n  {'Column':<35} {'Type':<20} {'Nullable'}")
        print(f"  {'-'*35} {'-'*20} {'-'*10}")
        for field in schema.fields:
            print(f"  {field.name:<35} {str(field.dataType):<20} {field.nullable}")
    except Exception as e:
        print(f"  Error getting schema: {e}")

    # ---- Table Properties ----
    print(f"\n{'='*60}")
    print(f"  TABLE PROPERTIES")
    print(f"{'='*60}")

    try:
        props = spark.sql(f"SHOW TBLPROPERTIES {table_name}").collect()
        for prop in props:
            if not prop.key.startswith("delta."):
                continue
            print(f"  {prop.key:<45} {prop.value}")
    except Exception as e:
        print(f"  Error getting properties: {e}")

    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*60}\n")


def compare_tables(spark, table_names: list):
    """
    Compare multiple Delta tables side by side.

    Args:
        spark: Active SparkSession
        table_names: List of table names to compare
    """
    print(f"\n{'='*70}")
    print(f"  DELTA TABLE COMPARISON")
    print(f"{'='*70}")

    print(f"\n  {'Table':<25} {'Files':<10} {'Size (MB)':<12} {'Avg File MB':<12} {'Status'}")
    print(f"  {'-'*25} {'-'*10} {'-'*12} {'-'*12} {'-'*15}")

    for table in table_names:
        try:
            detail = spark.sql(f"DESCRIBE DETAIL {table}").collect()[0]
            size_mb = detail.sizeInBytes / (1024**2)
            avg_mb = size_mb / detail.numFiles if detail.numFiles > 0 else 0

            if avg_mb < 1:
                status = "CRITICAL"
            elif avg_mb < 32:
                status = "WARN"
            elif detail.numFiles > 5000:
                status = "TOO MANY FILES"
            else:
                status = "OK"

            print(f"  {table:<25} {detail.numFiles:<10,} {size_mb:<12,.0f} {avg_mb:<12,.1f} {status}")
        except Exception as e:
            print(f"  {table:<25} Error: {str(e)[:40]}")


# ============================================================
#  USAGE - Modify these parameters for your analysis
# ============================================================

# Analyze a single table:
# analyze_delta_table(spark, "my_table_name")

# Compare multiple tables:
# compare_tables(spark, ["events", "orders", "customers", "products"])

print("Delta table health functions loaded.")
print("Example:")
print('  analyze_delta_table(spark, "my_table")')
print('  compare_tables(spark, ["table1", "table2", "table3"])')
