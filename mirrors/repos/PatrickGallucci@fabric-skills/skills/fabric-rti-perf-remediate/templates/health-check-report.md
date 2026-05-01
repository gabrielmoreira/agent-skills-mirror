# Fabric Real-Time Intelligence Health Check Report

**Date:** [YYYY-MM-DD]
**Workspace:** [Workspace Name]
**Capacity SKU:** [F2/F4/F8/.../F2048]
**Analyst:** [Name]

---

## 1. Eventhouse Inventory

| Eventhouse Name | KQL Databases | Always-On | Min Consumption CUs |
|----------------|---------------|-----------|---------------------|
| | | ☐ Yes ☐ No | |
| | | ☐ Yes ☐ No | |

## 2. Resource Utilization (Last 24 Hours)

| Metric | Average | P95 | Max | Status |
|--------|---------|-----|-----|--------|
| CPU Usage % | | | | ☐ Healthy ☐ Warning ☐ Critical |
| Memory Usage % | | | | ☐ Healthy ☐ Warning ☐ Critical |
| Cache Utilization % | | | | ☐ Healthy ☐ Warning ☐ Critical |
| Ingestion Utilization % | | | | ☐ Healthy ☐ Warning ☐ Critical |

## 3. Query Performance

| Metric | Value |
|--------|-------|
| Total queries (24h) | |
| Failed queries (24h) | |
| Throttled queries (24h) | |
| Failure rate % | |
| Avg query duration (sec) | |
| P95 query duration (sec) | |
| Cold storage query count | |

### Top 5 Expensive Queries

| # | Query Pattern (first 100 chars) | Avg Duration | CPU Time | Frequency |
|---|-------------------------------|-------------|----------|-----------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## 4. Ingestion Health

| Metric | Value |
|--------|-------|
| Total ingestion batches (24h) | |
| Success rate % | |
| Total rows ingested | |
| Total data ingested (GB) | |
| Avg ingestion latency (sec) | |
| P95 ingestion latency (sec) | |

### Tables with Ingestion Issues

| Database | Table | Success Rate | Error Type | Action Needed |
|----------|-------|-------------|------------|---------------|
| | | | | |

## 5. Materialized View Health

| View Name | Is Healthy | Age Behind (min) | Action Needed |
|-----------|-----------|-------------------|---------------|
| | ☐ Yes ☐ No | | |

## 6. Cache Policy Review

| Table | Current Cache | Query Time Range | Aligned? | Recommended |
|-------|-------------|-----------------|----------|-------------|
| | | | ☐ Yes ☐ No | |

## 7. Findings and Recommendations

### Critical (Action Required)

1. [Finding]
   - **Impact:** [Description]
   - **Recommendation:** [Action]

### Warning (Monitor)

1. [Finding]
   - **Impact:** [Description]
   - **Recommendation:** [Action]

### Informational

1. [Finding]

## 8. Next Steps

- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]
- [ ] Schedule follow-up review: [Date]
