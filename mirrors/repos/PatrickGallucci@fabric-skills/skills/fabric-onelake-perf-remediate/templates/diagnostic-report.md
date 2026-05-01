# OneLake Performance Diagnostic Report

## Investigation Summary

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Investigator | [Name] |
| Workspace | [Workspace Name / ID] |
| Capacity SKU | [F-SKU] |
| Region | [Azure Region] |
| Affected Items | [Lakehouse / Warehouse / Notebook names] |

## Reported Symptoms

Describe what the user or system reported:

- [ ] Slow query execution
- [ ] HTTP 430 throttling errors
- [ ] Direct Lake fallback to DirectQuery
- [ ] Cold cache latency
- [ ] Streaming ingestion delays
- [ ] Table maintenance failures
- [ ] Other: _____________________

## Diagnostic Steps Performed

### 1. Capacity Assessment

- Current SKU: [F-SKU]
- VCore limit: [N]
- Active Spark sessions at time of issue: [N]
- Queue depth at time of issue: [N]
- Queue limit: [N]
- Throttling observed: [Yes/No]

### 2. Cold Cache Analysis

- `data_scanned_remote_storage_mb` for affected query: [N MB]
- First execution time: [N ms]
- Second execution time: [N ms]
- Cache hit on subsequent runs: [Yes/No]

### 3. Table Health

| Table | File Count | Total Size (MB) | Avg File Size (MB) | V-Order | Last OPTIMIZE |
|-------|-----------|-----------------|--------------------|---------|--------------:|
| | | | | | |
| | | | | | |

### 4. Cross-Region Check

- Fabric capacity region: [Region]
- OneLake data region: [Region]
- Shortcut destinations region(s): [Region(s)]
- Measured latency (avg): [N ms]

### 5. Resource Profile

- Current profile: [writeHeavy / readHeavyForSpark / readHeavyForPBI]
- V-Order default: [Enabled / Disabled]
- Dominant workload type: [Ingestion / Analytics / Mixed]

## Root Cause

[Describe the identified root cause]

## Remediation Actions

| # | Action | Status | Owner | Due Date |
|---|--------|--------|-------|----------|
| 1 | | [ ] Pending | | |
| 2 | | [ ] Pending | | |
| 3 | | [ ] Pending | | |

## Performance Before / After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Query duration (avg) | | | |
| Cold cache scan (MB) | | | |
| File count | | | |
| Avg file size (MB) | | | |

## Notes

[Additional observations, caveats, or follow-up items]
