# Cold Cache Diagnostics

## Table of Contents

- [Understanding Cold Cache](#understanding-cold-cache)
- [Diagnostic T-SQL Queries](#diagnostic-t-sql-queries)
- [Interpreting Results](#interpreting-results)
- [Mitigation Strategies](#mitigation-strategies)

## Understanding Cold Cache

The first execution of a query in Fabric Data Warehouse or Lakehouse SQL analytics endpoint can be significantly slower than subsequent runs. This is a cold start caused by:

1. **Data loading** — Data fetched from OneLake into memory for the first time (not yet cached)
2. **Statistics generation** — Automatic statistics created on first access, delaying execution
3. **Node resume** — Fabric auto-pauses nodes after inactivity; resuming typically takes less than one second

Cold starts can be partial — some nodes, data, or statistics may already be available while the query waits for others.

## Diagnostic T-SQL Queries

### Check cold start impact on recent queries

```sql
-- Identify queries impacted by cold cache
-- Non-zero data_scanned_remote_storage_mb indicates cold start
SELECT
    distributed_statement_id,
    start_time,
    end_time,
    DATEDIFF(MILLISECOND, start_time, end_time) AS duration_ms,
    command,
    data_scanned_remote_storage_mb,
    data_scanned_memory_mb,
    data_scanned_disk_mb,
    result_cache_hit
FROM queryinsights.exec_requests_history
WHERE start_time > DATEADD(HOUR, -4, GETUTCDATE())
ORDER BY start_time DESC;
```

### Compare cold vs warm execution times

```sql
-- Group by query pattern to compare first vs subsequent runs
SELECT
    LEFT(command, 100) AS query_pattern,
    COUNT(*) AS execution_count,
    MIN(DATEDIFF(MILLISECOND, start_time, end_time)) AS min_duration_ms,
    MAX(DATEDIFF(MILLISECOND, start_time, end_time)) AS max_duration_ms,
    AVG(DATEDIFF(MILLISECOND, start_time, end_time)) AS avg_duration_ms,
    MAX(data_scanned_remote_storage_mb) AS max_remote_scan_mb,
    MIN(data_scanned_remote_storage_mb) AS min_remote_scan_mb
FROM queryinsights.exec_requests_history
WHERE start_time > DATEADD(HOUR, -24, GETUTCDATE())
GROUP BY LEFT(command, 100)
HAVING COUNT(*) > 1
ORDER BY MAX(data_scanned_remote_storage_mb) DESC;
```

### Check result set caching status

```sql
-- Identify queries that hit the result set cache
SELECT
    distributed_statement_id,
    command,
    result_cache_hit,
    DATEDIFF(MILLISECOND, start_time, end_time) AS duration_ms
FROM queryinsights.exec_requests_history
WHERE start_time > DATEADD(HOUR, -1, GETUTCDATE())
    AND result_cache_hit IS NOT NULL
ORDER BY start_time DESC;
```

## Interpreting Results

| data_scanned_remote_storage_mb | Meaning | Action |
|-------------------------------|---------|--------|
| 0 | Fully cached — optimal state | No action needed |
| Low (< 100 MB) | Partial cold start | Minor; subsequent queries will be faster |
| High (> 1 GB) | Full cold start | Expected on first run; verify subsequent runs are cached |
| Consistently high | Caching not effective | Check if data volume exceeds available cache; consider capacity sizing |

**Critical rule:** Never judge query performance based on the first execution. Always measure the second and third runs to establish baseline performance.

## Mitigation Strategies

**Enable result set caching** (preview) — Stores final SELECT results so subsequent identical queries skip compilation and data processing entirely. Enable per session:

```sql
-- Enable result set caching for the session
SET RESULT_SET_CACHING ON;
```

**Schedule warm-up queries** — Run representative queries on a schedule (e.g., before business hours) to pre-populate the cache. Use a Fabric pipeline with a SQL activity.

**Right-size string columns** — Use `varchar(n)` with the smallest `n` that accommodates values instead of `varchar(8000)` or `varchar(max)`. Lakehouse tables without defined string lengths appear as `varchar(8000)` in Fabric Warehouse.

```sql
-- In Spark SQL, define precise string column widths
CREATE TABLE sales.customers (
    customer_id BIGINT,
    customer_name VARCHAR(100),  -- Not varchar(8000)
    email VARCHAR(255),
    region VARCHAR(50)
);
```

**Partition and cluster tables** — Use partitioning for low-cardinality filter columns (like year/month) and Z-ORDER for high-selectivity columns.

**Keep data co-located** — Ensure OneLake data and Fabric capacity are in the same Azure region to avoid network latency on cache misses.
