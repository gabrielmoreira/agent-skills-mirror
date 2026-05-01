# Capacity and Sizing Guide

## Table of Contents

1. [Eventhouse Compute Model](#eventhouse-compute-model)
2. [Always-On and Minimum Consumption](#always-on-and-minimum-consumption)
3. [Cache Policy Tuning](#cache-policy-tuning)
4. [Retention Policy](#retention-policy)
5. [Storage Tiers and Billing](#storage-tiers-and-billing)
6. [Capacity Metrics App Analysis](#capacity-metrics-app-analysis)
7. [Sizing Decision Matrix](#sizing-decision-matrix)

---

## Eventhouse Compute Model

Eventhouse uses an **autoscale mechanism** that dynamically adjusts compute based on workload demand. Key concepts:

- **Eventhouse UpTime**: Measured as `active_seconds × virtual_cores_used`. This is the primary CU consumption metric.
- **Autoscale**: The system automatically scales up during high query/ingestion load and scales down during idle periods.
- **Suspension**: When idle, Eventhouse suspends to reduce cost. Reactivation incurs a latency of a few seconds.

Example: An Eventhouse using 4 virtual cores that is active for 30 seconds consumes 120 CU-seconds.

If a KQL database is a subitem of an Eventhouse, UpTime is reflected at the Eventhouse level — the database subitem does not appear separately in capacity metrics.

---

## Always-On and Minimum Consumption

### When to enable Always-On

Enable Always-On if your workload cannot tolerate the cold-start latency when Eventhouse reactivates from suspension. With Always-On:

- Eventhouse is always active (100% UpTime)
- No cold-start latency on first query
- OneLake Cache Storage charges are included in capacity (no separate cache storage billing)

### Minimum Consumption sizing

Minimum consumption prevents autoscale from scaling below a configured floor, ensuring adequate performance during sudden load spikes.

| Minimum CUs | Included SSD Cache (GB) |
|-------------|------------------------|
| 4.25 | 50 |
| 8.5 | 200 |
| 13 | 800 |
| 18 | 3,500–4,000 |
| 26 | 5,250–6,000 |
| 34 | 7,000–8,000 |
| 50 | 10,500–12,000 |
| Custom | ~200 GB per CU |

### Decision criteria

- **Predictable, steady load**: Always-On with minimum consumption matching typical usage
- **Bursty, unpredictable load**: Always-On with minimum consumption matching baseline, autoscale handles peaks
- **Cost-sensitive, tolerance for cold start**: Disable Always-On, let autoscale handle everything
- **Development/test workloads**: Disable Always-On to minimize cost

---

## Cache Policy Tuning

The cache policy controls how much data stays in **OneLake Cache Storage** (fast SSD) versus **OneLake Standard Storage** (cost-optimized).

### Setting cache policy

```kql
-- Set cache to 7 days for a specific table
.alter table MyTable policy caching hot = 7d

-- Set cache at database level (applies to all tables without explicit policy)
.alter database MyDB policy caching hot = 30d

-- Check current cache policy
.show table MyTable policy caching
```

### Tuning guidance

| Query Pattern | Recommended Cache | Rationale |
|--------------|-------------------|-----------|
| Last 24 hours only | `hot = 1d` | Minimum cache, lowest cost |
| Last 7 days (dashboards) | `hot = 7d` | Covers typical dashboard time ranges |
| Last 30 days (analytics) | `hot = 30d` | Good balance for ad-hoc analysis |
| Rare historical queries | `hot = 7d` with longer retention | Keep old data in standard storage |
| Compliance / audit | Match retention period | Avoid cold storage scans on audits |

### Detecting cold storage access

If queries frequently access data outside the cache window, you will see elevated cold storage access in query statistics. This significantly impacts query performance.

```kql
-- Find queries hitting cold storage (via workspace monitoring)
QueryLogs
| where TimeGenerated > ago(1d)
| where CacheStatistics has "Disk"
| project User, QueryText, Duration, CacheStatistics
| order by Duration desc
| take 20
```

If many queries hit cold storage, either expand the cache window or restructure queries to stay within the hot cache period.

---

## Retention Policy

Retention controls how long data is queryable in OneLake Standard Storage.

```kql
-- Set retention to 365 days
.alter table MyTable policy retention softdelete = 365d

-- Check retention policy
.show table MyTable policy retention
```

Data beyond the retention period is permanently deleted. Retention has no impact on query performance — it only affects storage cost and data availability.

---

## Storage Tiers and Billing

| Tier | Description | Comparable To | Billing |
|------|-------------|---------------|---------|
| OneLake Cache Storage | Fast SSD, used for hot data within cache policy | Azure ADLS Premium | Separate from CU; free with Always-On |
| OneLake Standard Storage | Cost-optimized, stores all queryable data within retention | Azure ADLS Hot | Separate from CU, billed per GB |

Monitor storage via the Fabric Capacity Metrics app → Storage page. Filter to KQL Database items to see per-database storage breakdown.

---

## Capacity Metrics App Analysis

### Accessing the app

1. Navigate to the Fabric Capacity Metrics app (requires capacity administrator role)
2. Select your capacity
3. Filter to the workspace containing your Eventhouse

### Key views for RTI remediate

**Compute page**:
- Filter Items to `Eventhouse` and `KQL Database`
- Check CU utilization percentage — sustained > 90% indicates need for SKU upgrade
- Identify which Eventhouse consumes the most CUs
- Look for throttling events

**Storage page**:
- Monitor OneLake Cache Storage growth
- Monitor OneLake Standard Storage growth
- Correlate storage spikes with ingestion volume changes

### Throttling indicators

When capacity is fully consumed, Fabric throttles operations. Symptoms visible in the Capacity Metrics app:

- CU utilization at or near 100%
- Throttled queries appearing in workspace monitoring dashboards
- HTTP 430 errors in query or ingestion logs

---

## Sizing Decision Matrix

| Scenario | Recommended Action |
|----------|-------------------|
| Sustained CU > 90% | Increase SKU or enable autoscale billing |
| Sporadic CU spikes > 100% | Configure minimum consumption to smooth baseline |
| Cold-start latency unacceptable | Enable Always-On |
| Query cache miss rate high | Expand cache policy to cover common query ranges |
| Storage growing faster than expected | Review retention policy; archive old data |
| Single Eventhouse dominates CU | Split into multiple Eventhouses; distribute workload |
| Ingestion throttled at capacity level | Increase SKU; reduce competing workloads during peak ingestion |
| Development environment | Disable Always-On; use smallest viable SKU |
