# OneLake Performance Checklist

Use this checklist for pre-deployment reviews, periodic performance audits, and
incident troubleshooting. Copy and customize for your environment.

---

## Pre-Deployment Checklist

### Data Layout
- [ ] Target file size ~1 GB for analytical workloads
- [ ] Delta tables partitioned on low-cardinality filter columns (date, region)
- [ ] Z-ORDER applied for high-selectivity secondary filter columns
- [ ] V-Order enabled if read-heavy (Power BI, interactive Spark queries)
- [ ] Optimized Write enabled for ETL pipelines writing to Delta tables

### Shortcut Configuration
- [ ] Shortcut targets are in the same region as the Fabric capacity
- [ ] Shortcut caching enabled for external sources (S3, GCS, on-prem gateway)
- [ ] Cache retention period matches data refresh cadence
- [ ] Cloud connection credentials are current and non-expiring (or have rotation plan)
- [ ] Files at shortcut targets are compacted (no small file proliferation)

### Capacity Planning
- [ ] CU consumption estimated for expected read/write volumes
- [ ] Write-heavy ETL scheduled during off-peak hours
- [ ] BCDR cost impact understood if disaster recovery is enabled
- [ ] Iterative operations minimized (directory scans, metadata writes)

### Connectivity
- [ ] Regional OneLake endpoint configured for data residency requirements
- [ ] ABFS URI format validated for Spark/Databricks integrations
- [ ] External tool URL validation tested (some tools reject fabric.microsoft.com)
- [ ] Authentication flow tested (Entra ID token with Storage audience)

### Security
- [ ] OneLake security roles have minimal scope (fewer rows in RLS = less CU)
- [ ] Role propagation timing accounted for in deployment (5 min - 1 hr)
- [ ] Cross-region shortcuts avoided when OneLake security is enabled
- [ ] Distribution lists NOT used in roles accessed via SQL analytics endpoint

---

## Ongoing Performance Audit

### Monthly Review
- [ ] Run OPTIMIZE on all actively written Delta tables
- [ ] Run VACUUM to clean up stale files (check retention period)
- [ ] Review Fabric Capacity Metrics app for OneLake CU trends
- [ ] Check for write:read CU ratio — high ratio = optimization opportunity
- [ ] Verify shortcut targets are still valid (no broken shortcuts)
- [ ] Review shortcut cache hit rates (via OneLake diagnostics if enabled)

### Quarterly Review
- [ ] Assess Delta table partitioning strategy against actual query patterns
- [ ] Review and update V-Order settings based on workload profile changes
- [ ] Audit OneLake security roles for least-privilege compliance
- [ ] Evaluate whether shortcut caching retention periods need adjustment
- [ ] Review diagnostics data for unusual access patterns or errors
- [ ] Check for capacity SKU right-sizing based on CU consumption trends

---

## Incident Troubleshooting Checklist

### Slow Read Performance
- [ ] Check file sizes — are there many files under 100 MB?
- [ ] Was OPTIMIZE run recently on affected tables?
- [ ] Is V-Order enabled for tables queried by Power BI / Direct Lake?
- [ ] Is the data in the same region as the Fabric capacity?
- [ ] If accessed via shortcut, is caching enabled and warm?
- [ ] Check for concurrent heavy write operations competing for capacity

### API Throttling (HTTP 429)
- [ ] Check Retry-After header value for required wait time
- [ ] Review API call patterns — can operations be batched?
- [ ] Verify exponential backoff is implemented in client code
- [ ] Check if iterative operations (directory listing) are excessive
- [ ] Distribute API calls across multiple time windows or principals

### Unexpected CU Consumption
- [ ] Check Fabric Capacity Metrics app for OneLake operation breakdown
- [ ] Identify write vs read vs iterative operation mix
- [ ] Look for small file read patterns (under 4 MB = full transaction each)
- [ ] Review diagnostics for unexpected access patterns or integrations
- [ ] Check if BCDR is enabled (write costs ~2x higher)
- [ ] Verify diagnostics overhead if enabled on high-traffic workspaces

### Security Role Propagation Issues
- [ ] Wait 5 minutes for role definition changes to propagate
- [ ] Wait 1 hour for user group membership changes
- [ ] Wait additional hour for engine-specific cache refresh
- [ ] Verify user is not in a distribution list (SQL endpoint limitation)
- [ ] Confirm Spark environment is 3.5+ / Runtime 1.3+
- [ ] Check that private link protection is not conflicting with OneLake security

---

## Environment Details (Fill In)

| Setting | Value |
|---------|-------|
| Workspace Name | |
| Workspace ID | |
| Capacity SKU | |
| Capacity Region | |
| BCDR Enabled | Yes / No |
| OneLake Diagnostics Enabled | Yes / No |
| Diagnostics Lakehouse | |
| Shortcut Caching Enabled | Yes / No |
| Cache Retention Period | days |
| V-Order Enabled | Yes / No |
| Compute Profile | writeHeavy / readHeavyForSpark / readHeavyForPBI |
