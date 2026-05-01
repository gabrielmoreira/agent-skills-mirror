# Read Optimization (VOrder, Resource Profiles)

## Table of Contents

- [Resource Profiles Overview](#resource-profiles-overview)
- [VOrder Deep Dive](#vorder-deep-dive)
- [SQL Analytics Endpoint Performance](#sql-analytics-endpoint-performance)
- [Power BI Direct Lake Optimization](#power-bi-direct-lake-optimization)

## Resource Profiles Overview

Fabric supports predefined Spark resource profiles that apply workload-optimized
configurations as a property bag.

### Available Profiles

| Profile | Use Case | VOrder | Write Perf | Read Perf |
|---------|----------|--------|-----------|-----------|
| writeHeavy | ETL, ingestion, batch writes | Disabled | Best | Baseline |
| readHeavyForSpark | Interactive Spark queries, EDA | Enabled | Reduced | Optimized |
| readHeavyForPBI | Power BI Direct Lake, dashboards | Enabled | Reduced | Best for PBI |

### Workspace Default

All new Fabric workspaces default to `writeHeavy`. This is optimal for data engineering
workloads but suboptimal if the primary consumers are Power BI reports or interactive queries.

### Changing the Resource Profile

Configure at the environment level in Workspace Settings > Data Engineering/Science:

1. Open the Fabric environment attached to your workspace
2. Navigate to Spark properties
3. Set the resource profile property
4. Publish the environment

Or set programmatically:

```python
# Check current profile
print(spark.conf.get("spark.fabric.resourceProfile", "not set"))
```

### When to Change Profiles

Switch to `readHeavyForSpark` or `readHeavyForPBI` when:
- Power BI reports query the Lakehouse via Direct Lake
- Users run interactive queries in notebooks for data exploration
- SQL analytics endpoint queries are the primary workload
- Dashboard refresh times are too slow

Keep `writeHeavy` when:
- The workspace is primarily used for ETL/data engineering
- Streaming ingestion is the dominant workload
- Write throughput is the bottleneck

## VOrder Deep Dive

VOrder applies a special columnar sort order to Parquet files at write time. This sort order
is optimized for the Fabric query engines (Spark SQL, SQL analytics endpoint, Power BI).

### How VOrder Works

1. During write, data within each Parquet row group is sorted by a computed order
2. The sort order maximizes compression and enables efficient predicate pushdown
3. Read operations can skip more data and decompress faster
4. Most beneficial for selective queries (WHERE, JOIN, aggregation)

### VOrder Impact

| Operation | Without VOrder | With VOrder |
|-----------|---------------|-------------|
| Point lookups | Full row group scan | Efficient skip |
| Range scans | Moderate skip | Excellent skip |
| Aggregations | Read all rows | Reduced I/O |
| Full table scan | No difference | Slightly faster (compression) |
| Write speed | Baseline | 5–15% slower |

### Applying VOrder to Existing Tables

Run OPTIMIZE with VORDER on existing tables to retrofit:

```python
spark.sql("OPTIMIZE your_table VORDER")
```

This rewrites all files with VOrder applied. Schedule during maintenance windows
for large tables.

## SQL Analytics Endpoint Performance

The SQL analytics endpoint provides read-only T-SQL access to Delta tables. Performance
depends on Delta table health and VOrder status.

### Key Limitations

- Read-only — cannot INSERT, UPDATE, or DELETE
- Only Delta format tables are visible (not Parquet, CSV, etc.)
- External Delta tables created with Spark code are not visible — use shortcuts
- Does not support full T-SQL (subset of Fabric Data Warehouse engine)

### Optimization for SQL Analytics Endpoint

1. **Enable VOrder** — most impactful single optimization
2. **Run OPTIMIZE regularly** — compacted files read faster
3. **Use Z-Order on filter columns** — improves predicate pushdown for SQL queries
4. **Avoid over-partitioning** — too many partitions create overhead for SQL engine
5. **Create views** — encapsulate complex joins for reuse

## Power BI Direct Lake Optimization

Direct Lake mode reads Delta tables directly from OneLake without importing data.
Performance is heavily influenced by file layout and VOrder.

### Checklist for Fast Direct Lake

1. Enable VOrder on all tables used by Direct Lake
2. Use the `readHeavyForPBI` resource profile
3. Run OPTIMIZE after ETL loads complete
4. Keep table file count reasonable (< 10,000 files per table)
5. Use partitioning sparingly — Direct Lake handles non-partitioned tables well
6. Ensure the semantic model is refreshed after table maintenance
