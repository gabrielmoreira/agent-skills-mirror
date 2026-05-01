# OneLake Shortcuts Performance Optimization

Comprehensive guide for diagnosing and resolving performance issues with OneLake shortcuts,
including cross-cloud access, caching configuration, and query acceleration.

## Table of Contents

- [How Shortcuts Work](#how-shortcuts-work)
- [Cross-Region and Cross-Cloud Latency](#cross-region-and-cross-cloud-latency)
- [Shortcut Caching](#shortcut-caching)
- [Small File Problem with Shortcuts](#small-file-problem-with-shortcuts)
- [Query Acceleration for External Shortcuts](#query-acceleration-for-external-shortcuts)
- [Shortcut Security Performance Impact](#shortcut-security-performance-impact)
- [Troubleshooting Matrix](#troubleshooting-matrix)

---

## How Shortcuts Work

Shortcuts are symbolic links in OneLake that point to other storage locations (internal
OneLake items or external sources like ADLS Gen2, S3, GCS). They appear as folders and
are transparent to any workload or service with OneLake access.

Key performance characteristics:

- **Internal shortcuts** (OneLake-to-OneLake): Use caller's identity, minimal overhead
- **External shortcuts** (ADLS Gen2, S3, GCS): Use connection credentials, subject to
  network latency and egress costs
- Shortcuts do NOT copy data — every read goes to the target source unless caching is enabled
- Deleting a shortcut does not affect the target; renaming/moving target breaks the shortcut

### CU Billing for Shortcuts

Transaction usage for shortcut access is billed to the capacity where the shortcut is
created (the consumer), not the capacity where data is stored. External shortcut requests
to ADLS Gen2 or S3 are NOT counted as OneLake CU usage — the external service bills
directly.

---

## Cross-Region and Cross-Cloud Latency

The single largest performance factor for shortcuts is data locality. Querying data in a
different region from your Fabric capacity introduces network round-trip latency.

### Diagnosis

1. Check your Fabric capacity region in the Admin portal
2. Check the location of the shortcut target data
3. If they differ, cross-region latency is the likely cause

### Resolution Strategies

| Strategy | When to Use |
|----------|-------------|
| Move data to same region | Feasible for owned data, maximum performance gain |
| Use regional OneLake endpoint | Data residency compliance, prevents cross-region routing |
| Keep only small tables remote | Dimension tables < 100 MB tolerate latency well |
| Enable shortcut caching | Reduces repeated cross-cloud reads |
| Use query acceleration | KQL-based acceleration for external Delta tables |

### Regional Endpoint Configuration

```powershell
# Instead of global endpoint:
# https://onelake.dfs.fabric.microsoft.com/...

# Use region-specific endpoint:
$region = "westus"  # Match your capacity region
$endpoint = "https://$region-onelake.dfs.fabric.microsoft.com"
```

---

## Shortcut Caching

Caching stores copies of externally-read files locally in the Fabric workspace, reducing
egress costs and latency for repeated reads.

### Supported Sources

Caching is available for: GCS, S3, S3-compatible, and on-premises data gateway shortcuts.
ADLS Gen2 shortcuts do NOT currently support caching.

### Configuration

1. Open **Workspace settings**
2. Select the **OneLake** tab
3. Toggle cache to **On**
4. Set **Retention Period** (1-28 days)

### Cache Behavior

- Files are cached on first read and served from cache on subsequent reads
- Retention resets each time the file is accessed
- If the remote file is newer than the cached version, OneLake serves from remote
  and updates the cache
- **Files larger than 1 GB are NOT cached**
- Cache can be cleared manually via **Reset cache** button in workspace settings

### Best Practices

- Set retention period to match your data refresh cadence
- For daily refreshed data, 2-3 day retention provides good hit rates
- Monitor cache hit rates through OneLake diagnostics events
- Consider that cache occupies capacity storage

---

## Small File Problem with Shortcuts

Shortcuts that point to locations with many small files suffer compounded performance
degradation because each file requires a separate network request.

### Diagnosis

```sql
-- Check file count and sizes for a shortcut-backed table via SQL analytics endpoint
SELECT COUNT(*) AS file_count,
       AVG(file_size_bytes) / 1048576.0 AS avg_file_mb,
       MIN(file_size_bytes) / 1048576.0 AS min_file_mb,
       MAX(file_size_bytes) / 1048576.0 AS max_file_mb
FROM system.files('my_table');
```

### Resolution

If the shortcut points to an internal OneLake location, run OPTIMIZE on the source:

```sql
OPTIMIZE source_lakehouse.source_table;
```

If the shortcut points to an external location:

- Compact files at the source before creating the shortcut
- Consider using a pipeline to copy and compact data into a local lakehouse table
- For Eventhouse OneLake availability, adjust `TargetLatencyInMinutes` to batch
  larger files (default up to 3 hours, minimum 5 minutes):

```kusto
.alter-merge table <TableName> policy mirroring
    dataformat=parquet
    with (IsEnabled=true, TargetLatencyInMinutes=60);
```

> **Warning**: Shorter latency settings create more small files. Balance freshness
> against query performance.

---

## Query Acceleration for External Shortcuts

Query acceleration (Real-Time Intelligence feature) creates indexed, cached copies of
external Delta table data for fast KQL and SQL queries.

### When to Use

- Frequent analytical queries against external Delta tables via shortcuts
- Need sub-second query performance on shortcut data
- Acceptable to consume additional CUs for acceleration

### Limitations

- Maximum 900 columns per external table
- Tables with >2.5 million data files may not perform optimally
- Schema changes require re-enabling the acceleration policy
- Parquet files >6 GB compressed are not cached
- Index-based pruning not supported for partitions

### Billing

Accelerated data is charged under the OneLake Premium cache meter, similar to native
Eventhouse tables. Control cost by configuring the number of days to cache.

---

## Shortcut Security Performance Impact

OneLake security (data access roles) adds authorization checks that consume capacity and
introduce latency.

### Performance Considerations

- OneLake security RLS consumes 0.1 CU seconds per million rows in secured tables
- Cross-region shortcuts return 404 errors when OneLake security is enabled
- Distribution lists in security roles cannot be resolved by SQL analytics endpoint
- Role definition changes take ~5 minutes to propagate
- User group membership changes take ~1 hour to propagate
- Some Fabric engines have additional caching layers adding up to 1 more hour

### Optimization

- Minimize the number of rows covered by RLS when possible
- Pre-filter data into separate tables/folders rather than relying on row-level security
  for performance-critical queries
- Test security role propagation timing in your deployment workflow

---

## Troubleshooting Matrix

| Symptom | Check | Resolution |
|---------|-------|------------|
| Slow shortcut reads, first access | Cross-region latency | Enable caching, move data closer |
| Slow shortcut reads, repeated access | Caching not enabled or file >1 GB | Enable caching, compact files |
| Shortcut returns 404 | Target moved/deleted, or cross-region + OneLake security | Verify target exists, check security config |
| High egress costs on shortcuts | No caching, frequent cross-cloud reads | Enable shortcut caching |
| Shortcut works but queries are slow | Small files at target | OPTIMIZE at source or copy/compact locally |
| Connection errors on external shortcut | Expired cloud connection credentials | Update connection in Fabric portal |
| Cannot create shortcut | Missing connection permissions | Request bind permission on cloud connection |
| Shortcut data stale in cache | Cache retention too long, remote file updated | Reduce retention or manually reset cache |
