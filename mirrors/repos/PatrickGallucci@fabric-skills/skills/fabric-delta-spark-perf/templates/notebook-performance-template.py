"""
Fabric Spark Performance-Optimized Notebook Template
=====================================================
Starter notebook with performance best practices baked in.
Copy this template and modify for your specific workload.

Sections marked with TODO require customization for your use case.
"""

# =============================================================================
# Cell 1: Session Configuration
# =============================================================================
# TODO: Choose the resource profile that matches your workload.
#   writeHeavy       -> High-frequency ingestion, ETL, streaming
#   readHeavyForSpark -> Interactive Spark SQL queries, analytics
#   readHeavyForPBI   -> Power BI Direct Lake backing tables

RESOURCE_PROFILE = "writeHeavy"  # TODO: Change to match workload

spark.conf.set("spark.fabric.resourceProfile", RESOURCE_PROFILE)

# Enable Adaptive Query Execution (keep enabled for all workloads)
spark.conf.set("spark.databricks.optimizer.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Enable Optimized Write to prevent small file accumulation
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

# TODO: Tune shuffle partitions based on data volume.
#   Rule of thumb: total_shuffle_data_gb / 0.128 = target partitions
#   Or use "auto" to let AQE decide dynamically.
spark.conf.set("spark.sql.shuffle.partitions", "auto")

# TODO: Set broadcast threshold based on your small table sizes.
#   Default 10MB. Increase if you have lookup tables up to ~100MB.
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "30m")

print(f"Resource profile: {RESOURCE_PROFILE}")
print("Session configured with performance best practices.")


# =============================================================================
# Cell 2: Read Source Data
# =============================================================================
# Best practices:
#   - Apply column pruning: select only needed columns
#   - Apply row filtering early: push predicates before joins
#   - Use Delta format for ACID and performance benefits

# TODO: Replace with your source table and columns
SOURCE_TABLE = "bronze.raw_transactions"  # TODO
FILTER_PREDICATE = "load_date >= '2025-01-01'"  # TODO

df_source = (
    spark.table(SOURCE_TABLE)
    .filter(FILTER_PREDICATE)
    .select(
        "transaction_id",
        "customer_id",
        "amount",
        "transaction_date",
        "status"
        # TODO: Add only the columns you need
    )
)

print(f"Source: {SOURCE_TABLE}")
print(f"Filter: {FILTER_PREDICATE}")


# =============================================================================
# Cell 3: Transformations
# =============================================================================
from pyspark.sql import functions as F
from pyspark.sql.functions import broadcast

# Best practices:
#   - Filter before joins (reduces shuffle volume)
#   - Use broadcast() for small lookup tables
#   - Avoid collect(), toPandas() on large DataFrames
#   - Use DataFrame API over RDD API (Catalyst optimizer)

# TODO: Replace with your lookup table
LOOKUP_TABLE = "silver.dim_customers"  # TODO

df_lookup = spark.table(LOOKUP_TABLE)

# Broadcast small lookup tables to avoid shuffle
df_enriched = df_source.join(
    broadcast(df_lookup),
    "customer_id",
    "left"
)

# TODO: Add your business transformations here
df_transformed = (
    df_enriched
    .withColumn("amount_usd", F.col("amount") * F.lit(1.0))
    .withColumn("processed_at", F.current_timestamp())
    .filter(F.col("status").isin("completed", "pending"))
)


# =============================================================================
# Cell 4: Write to Target
# =============================================================================
# Best practices:
#   - Use Delta format for all persisted tables
#   - Partition only if table will exceed 1TB and you have a
#     low-cardinality column (< 200 distinct values)
#   - Optimized Write handles file sizing automatically
#   - Use saveAsTable for managed tables, save for external

TARGET_TABLE = "silver.fact_transactions"  # TODO
WRITE_MODE = "overwrite"  # TODO: "overwrite", "append", or "merge"

if WRITE_MODE in ("overwrite", "append"):
    (
        df_transformed
        .write
        .format("delta")
        .mode(WRITE_MODE)
        # TODO: Uncomment partitionBy for tables > 1TB with low-cardinality column
        # .partitionBy("transaction_date")
        .saveAsTable(TARGET_TABLE)
    )
    print(f"Written to {TARGET_TABLE} (mode: {WRITE_MODE})")


# =============================================================================
# Cell 5: Post-Write Validation
# =============================================================================
# Quick health check on the output table

detail = spark.sql(f"DESCRIBE DETAIL {TARGET_TABLE}").first()
num_files = detail["numFiles"]
size_bytes = detail["sizeInBytes"]
avg_mb = (size_bytes / max(num_files, 1)) / (1024**2)

print(f"\nTarget table health:")
print(f"  Files: {num_files:,}")
print(f"  Size:  {size_bytes / (1024**3):.2f} GB")
print(f"  Avg file size: {avg_mb:.1f} MB")

if avg_mb < 32 and num_files > 10:
    print("  WARNING: Small files detected. Consider running OPTIMIZE.")
elif avg_mb > 2048:
    print("  WARNING: Oversized files. Consider increasing parallelism.")
else:
    print("  File sizes look healthy.")


# =============================================================================
# Cell 6: Optional Post-Write Maintenance
# =============================================================================
# Uncomment to run OPTIMIZE after writes (recommended for read-heavy tables)

# spark.sql(f"OPTIMIZE {TARGET_TABLE} VORDER")
# print(f"OPTIMIZE with V-Order completed for {TARGET_TABLE}")

# Uncomment to run VACUUM (recommended weekly, not after every write)
# spark.sql(f"VACUUM {TARGET_TABLE} RETAIN 168 HOURS")
# print(f"VACUUM completed for {TARGET_TABLE}")
