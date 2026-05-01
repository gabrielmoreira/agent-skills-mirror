"""
Fabric Delta Lake Table Maintenance Script
===========================================
Automates OPTIMIZE and VACUUM operations across all Delta tables
in a Lakehouse schema.

Usage (in a Fabric notebook):
    %run /path/to/table-maintenance

    # Maintain all tables in a schema with defaults
    maintain_schema("schema_name")

    # Maintain with V-Order and custom VACUUM retention
    maintain_schema("schema_name", vorder=True, vacuum_hours=168)

    # Maintain a single table with Z-Order
    maintain_table("schema_name.table_name", vorder=True,
                   zorder_columns=["customer_id"])

    # Dry run (show what would be done without executing)
    maintain_schema("schema_name", dry_run=True)
"""

from pyspark.sql import SparkSession
from datetime import datetime
import time


def get_spark():
    """Get or create SparkSession."""
    return SparkSession.builder.getOrCreate()


def maintain_table(
    table_name,
    optimize=True,
    vacuum=True,
    vorder=False,
    zorder_columns=None,
    vacuum_hours=168,
    partition_predicate=None,
    dry_run=False
):
    """
    Run maintenance operations on a single Delta table.

    Parameters
    ----------
    table_name : str
        Fully qualified table name (schema_name.table_name).
    optimize : bool
        Run OPTIMIZE bin-compaction (default True).
    vacuum : bool
        Run VACUUM to clean up old files (default True).
    vorder : bool
        Apply V-Order during OPTIMIZE (default False).
    zorder_columns : list of str, optional
        Columns to Z-Order by during OPTIMIZE.
    vacuum_hours : int
        VACUUM retention period in hours (default 168 = 7 days).
    partition_predicate : str, optional
        WHERE clause to limit OPTIMIZE to specific partitions.
        Example: "date_key >= '2025-01-01'"
    dry_run : bool
        If True, print SQL commands without executing (default False).

    Returns
    -------
    dict
        Results of the maintenance operations.
    """
    spark = get_spark()
    result = {
        "table": table_name,
        "operations": [],
        "errors": [],
        "start_time": datetime.now().isoformat()
    }

    print(f"\n--- Maintaining: {table_name} ---")

    # --- Pre-maintenance stats ---
    try:
        detail_before = spark.sql(f"DESCRIBE DETAIL {table_name}").first()
        files_before = detail_before["numFiles"]
        size_before = detail_before["sizeInBytes"]
        print(f"  Before: {files_before:,} files, "
              f"{size_before / (1024**3):.2f} GB")
    except Exception as e:
        print(f"  Could not get table details: {e}")
        files_before = None

    # --- OPTIMIZE ---
    if optimize:
        optimize_sql = f"OPTIMIZE {table_name}"

        if partition_predicate:
            optimize_sql += f" WHERE {partition_predicate}"

        if zorder_columns:
            cols = ", ".join(zorder_columns)
            optimize_sql += f" ZORDER BY ({cols})"

        if vorder:
            optimize_sql += " VORDER"

        optimize_sql += ";"

        if dry_run:
            print(f"  [DRY RUN] Would execute: {optimize_sql}")
            result["operations"].append({"type": "OPTIMIZE", "sql": optimize_sql,
                                          "status": "DRY_RUN"})
        else:
            print(f"  Running: {optimize_sql}")
            start = time.time()
            try:
                spark.sql(optimize_sql)
                elapsed = time.time() - start
                print(f"  OPTIMIZE completed in {elapsed:.1f}s")
                result["operations"].append({
                    "type": "OPTIMIZE",
                    "sql": optimize_sql,
                    "status": "SUCCESS",
                    "duration_seconds": round(elapsed, 1)
                })
            except Exception as e:
                print(f"  OPTIMIZE FAILED: {e}")
                result["operations"].append({
                    "type": "OPTIMIZE",
                    "sql": optimize_sql,
                    "status": "FAILED",
                    "error": str(e)
                })
                result["errors"].append(str(e))

    # --- VACUUM ---
    if vacuum:
        vacuum_sql = f"VACUUM {table_name} RETAIN {vacuum_hours} HOURS;"

        if dry_run:
            print(f"  [DRY RUN] Would execute: {vacuum_sql}")
            result["operations"].append({"type": "VACUUM", "sql": vacuum_sql,
                                          "status": "DRY_RUN"})
        else:
            print(f"  Running: {vacuum_sql}")
            start = time.time()
            try:
                spark.sql(vacuum_sql)
                elapsed = time.time() - start
                print(f"  VACUUM completed in {elapsed:.1f}s")
                result["operations"].append({
                    "type": "VACUUM",
                    "sql": vacuum_sql,
                    "status": "SUCCESS",
                    "duration_seconds": round(elapsed, 1)
                })
            except Exception as e:
                print(f"  VACUUM FAILED: {e}")
                result["operations"].append({
                    "type": "VACUUM",
                    "sql": vacuum_sql,
                    "status": "FAILED",
                    "error": str(e)
                })
                result["errors"].append(str(e))

    # --- Post-maintenance stats ---
    if not dry_run:
        try:
            detail_after = spark.sql(f"DESCRIBE DETAIL {table_name}").first()
            files_after = detail_after["numFiles"]
            size_after = detail_after["sizeInBytes"]
            print(f"  After:  {files_after:,} files, "
                  f"{size_after / (1024**3):.2f} GB")

            if files_before is not None:
                file_reduction = files_before - files_after
                size_change_mb = (size_before - size_after) / (1024**2)
                if file_reduction > 0:
                    print(f"  Reduced by {file_reduction:,} files, "
                          f"saved {size_change_mb:.1f} MB")

            result["files_after"] = files_after
            result["size_after"] = size_after
        except Exception:
            pass

    result["end_time"] = datetime.now().isoformat()
    return result


def maintain_schema(
    schema_name,
    optimize=True,
    vacuum=True,
    vorder=False,
    vacuum_hours=168,
    exclude_tables=None,
    include_tables=None,
    dry_run=False,
    max_tables=100
):
    """
    Run maintenance operations on all Delta tables in a schema.

    Parameters
    ----------
    schema_name : str
        Schema name to maintain.
    optimize : bool
        Run OPTIMIZE on each table (default True).
    vacuum : bool
        Run VACUUM on each table (default True).
    vorder : bool
        Apply V-Order during OPTIMIZE (default False).
    vacuum_hours : int
        VACUUM retention hours (default 168 = 7 days).
    exclude_tables : list of str, optional
        Table names to skip (without schema prefix).
    include_tables : list of str, optional
        If specified, only maintain these tables (without schema prefix).
    dry_run : bool
        Print commands without executing (default False).
    max_tables : int
        Maximum tables to process (default 100).

    Returns
    -------
    list of dict
        Results for each table processed.
    """
    spark = get_spark()
    exclude_tables = set(exclude_tables or [])

    tables = spark.sql(f"SHOW TABLES IN {schema_name}").collect()

    if include_tables:
        include_set = set(include_tables)
        tables = [t for t in tables if t["tableName"] in include_set]

    tables = [t for t in tables if t["tableName"] not in exclude_tables]
    tables = tables[:max_tables]

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"  TABLE MAINTENANCE [{mode}]")
    print(f"  Schema: {schema_name}")
    print(f"  Tables: {len(tables)}")
    print(f"  OPTIMIZE: {optimize} | VACUUM: {vacuum} | V-Order: {vorder}")
    print(f"  VACUUM retention: {vacuum_hours} hours")
    print(f"{'='*60}")

    all_results = []
    total_start = time.time()

    for i, table_row in enumerate(tables, 1):
        table_name = f"{schema_name}.{table_row['tableName']}"
        print(f"\n[{i}/{len(tables)}]", end="")

        try:
            result = maintain_table(
                table_name,
                optimize=optimize,
                vacuum=vacuum,
                vorder=vorder,
                vacuum_hours=vacuum_hours,
                dry_run=dry_run
            )
            all_results.append(result)
        except Exception as e:
            print(f"  FAILED: {e}")
            all_results.append({
                "table": table_name,
                "errors": [str(e)],
                "operations": []
            })

    total_elapsed = time.time() - total_start

    # --- Summary ---
    succeeded = sum(1 for r in all_results if not r.get("errors"))
    failed = sum(1 for r in all_results if r.get("errors"))

    print(f"\n{'='*60}")
    print(f"  MAINTENANCE COMPLETE")
    print(f"{'='*60}")
    print(f"  Total time:  {total_elapsed:.1f}s")
    print(f"  Succeeded:   {succeeded}")
    print(f"  Failed:      {failed}")

    if failed > 0:
        print(f"\n  Failed tables:")
        for r in all_results:
            if r.get("errors"):
                print(f"    - {r['table']}: {r['errors'][0]}")

    print()
    return all_results
