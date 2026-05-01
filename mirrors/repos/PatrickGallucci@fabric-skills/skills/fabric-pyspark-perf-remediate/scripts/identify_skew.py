"""
Identify Data Skew - Microsoft Fabric PySpark Diagnostic Script

Analyzes a DataFrame to detect data skew on specified columns by
examining partition sizes and key value distribution.

Usage:
    Copy this script into a notebook cell. Modify the parameters
    at the bottom and execute.
"""

from pyspark.sql import functions as F
from pyspark.sql import DataFrame


def analyze_column_skew(df: DataFrame, column_name: str, top_n: int = 20):
    """
    Analyze skew on a specific column by examining value distribution.

    Args:
        df: The DataFrame to analyze
        column_name: Column to check for skew
        top_n: Number of top values to display
    """
    print(f"\n{'='*60}")
    print(f"  SKEW ANALYSIS: {column_name}")
    print(f"{'='*60}")

    total_rows = df.count()
    distinct_count = df.select(column_name).distinct().count()
    null_count = df.filter(F.col(column_name).isNull()).count()

    print(f"\n  Total Rows:     {total_rows:,}")
    print(f"  Distinct Values: {distinct_count:,}")
    print(f"  NULL Count:      {null_count:,} ({null_count/total_rows*100:.1f}%)")

    # Distribution analysis
    dist = df.groupBy(column_name) \
        .count() \
        .withColumn("percentage", F.round(F.col("count") / total_rows * 100, 2))

    stats = dist.select(
        F.min("count").alias("min_count"),
        F.max("count").alias("max_count"),
        F.avg("count").alias("avg_count"),
        F.percentile_approx("count", 0.5).alias("median_count"),
        F.percentile_approx("count", 0.75).alias("p75_count"),
        F.percentile_approx("count", 0.95).alias("p95_count"),
        F.percentile_approx("count", 0.99).alias("p99_count"),
        F.stddev("count").alias("stddev_count"),
    ).collect()[0]

    print(f"\n  Distribution Statistics:")
    print(f"    Min:        {int(stats.min_count):,}")
    print(f"    Median:     {int(stats.median_count):,}")
    print(f"    Average:    {int(stats.avg_count):,}")
    print(f"    P75:        {int(stats.p75_count):,}")
    print(f"    P95:        {int(stats.p95_count):,}")
    print(f"    P99:        {int(stats.p99_count):,}")
    print(f"    Max:        {int(stats.max_count):,}")
    print(f"    Std Dev:    {int(stats.stddev_count):,}")

    # Skew ratio
    skew_ratio = stats.max_count / stats.median_count if stats.median_count > 0 else float('inf')
    print(f"\n  Skew Ratio (max/median): {skew_ratio:.1f}x")

    if skew_ratio > 10:
        print(f"  ** SEVERE SKEW DETECTED ** - Max value has {skew_ratio:.0f}x more rows than median")
        print(f"  Recommendation: Use salting, filter-and-union, or AQE skew join handling")
    elif skew_ratio > 5:
        print(f"  * MODERATE SKEW * - Consider enabling AQE skew join optimization")
    elif skew_ratio > 2:
        print(f"  ~ MILD SKEW ~ - Likely acceptable, monitor with AQE enabled")
    else:
        print(f"  Distribution is relatively even - no skew concern")

    # Top N values
    print(f"\n  Top {top_n} Values by Count:")
    print(f"  {'Value':<40} {'Count':<15} {'%':<8}")
    print(f"  {'-'*40} {'-'*15} {'-'*8}")

    top_values = dist.orderBy(F.desc("count")).limit(top_n).collect()
    for row in top_values:
        val = str(row[column_name]) if row[column_name] is not None else "NULL"
        if len(val) > 38:
            val = val[:35] + "..."
        print(f"  {val:<40} {row['count']:<15,} {row['percentage']:<8}")

    # NULL skew warning
    if null_count > 0 and null_count / total_rows > 0.01:
        print(f"\n  WARNING: {null_count:,} NULL values ({null_count/total_rows*100:.1f}%)")
        print(f"  NULLs hash to the same partition during joins, causing skew.")
        print(f"  Consider filtering NULLs or replacing with unique identifiers.")


def analyze_partition_sizes(df: DataFrame):
    """
    Analyze the physical partition size distribution of a DataFrame.

    Args:
        df: The DataFrame to analyze (must have been read, not transformed)
    """
    print(f"\n{'='*60}")
    print(f"  PARTITION SIZE ANALYSIS")
    print(f"{'='*60}")

    num_partitions = df.rdd.getNumPartitions()
    print(f"\n  Number of Partitions: {num_partitions}")

    # Get row count per partition
    partition_counts = df.rdd.mapPartitions(
        lambda it: [sum(1 for _ in it)]
    ).collect()

    if not partition_counts:
        print("  No data in DataFrame")
        return

    import statistics

    total = sum(partition_counts)
    avg = statistics.mean(partition_counts)
    median = statistics.median(partition_counts)
    max_val = max(partition_counts)
    min_val = min(partition_counts)
    empty = sum(1 for c in partition_counts if c == 0)

    print(f"  Total Rows:          {total:,}")
    print(f"  Avg Rows/Partition:  {avg:,.0f}")
    print(f"  Median:              {median:,.0f}")
    print(f"  Min:                 {min_val:,}")
    print(f"  Max:                 {max_val:,}")
    print(f"  Empty Partitions:    {empty} ({empty/num_partitions*100:.1f}%)")

    if max_val > 0 and median > 0:
        ratio = max_val / median
        print(f"  Skew Ratio:          {ratio:.1f}x")

        if ratio > 10:
            print(f"\n  ** PARTITION SKEW ** - Largest partition has {ratio:.0f}x more rows")
            print(f"  Recommendation: Repartition on a better column or increase partitions")
    elif empty > num_partitions * 0.5:
        print(f"\n  ** MANY EMPTY PARTITIONS ** - {empty}/{num_partitions} partitions empty")
        print(f"  Recommendation: Use coalesce() to reduce partition count")


# ============================================================
#  USAGE - Modify these parameters for your analysis
# ============================================================

# Example: Analyze a Delta table for skew on a join key
# df = spark.table("my_table")
# analyze_column_skew(df, "customer_id", top_n=20)
# analyze_column_skew(df, "product_id", top_n=20)
# analyze_partition_sizes(df)

# Uncomment and modify the lines above to run the analysis
print("Skew analysis functions loaded. Uncomment the usage section to run.")
print("Example:")
print('  df = spark.table("my_table")')
print('  analyze_column_skew(df, "join_key_column")')
print('  analyze_partition_sizes(df)')
