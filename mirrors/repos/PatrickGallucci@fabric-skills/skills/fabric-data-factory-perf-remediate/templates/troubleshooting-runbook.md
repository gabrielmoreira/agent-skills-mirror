# Pipeline Performance remediate Runbook

> **Template**: Copy this file and fill in the details for each pipeline that requires performance tracking.

## Pipeline Information

| Field | Value |
|-------|-------|
| **Pipeline Name** | `[PIPELINE_NAME]` |
| **Workspace** | `[WORKSPACE_NAME]` |
| **Capacity SKU** | `[F64 / F128 / etc.]` |
| **Owner** | `[TEAM_OR_PERSON]` |
| **Schedule** | `[CRON_OR_TRIGGER_DESCRIPTION]` |
| **Expected Duration** | `[BASELINE_DURATION]` |
| **SLA** | `[MAX_ACCEPTABLE_DURATION]` |
| **Last Updated** | `[DATE]` |

## Pipeline Architecture

Describe the pipeline structure:

```
[SOURCE] → Copy Activity → [STAGING] → Notebook → [DESTINATION]
```

### Activities

| Activity | Type | Source | Destination | Expected Duration |
|----------|------|--------|-------------|-------------------|
| `[ACTIVITY_1]` | Copy | `[SOURCE]` | `[DEST]` | `[DURATION]` |
| `[ACTIVITY_2]` | Notebook | N/A | N/A | `[DURATION]` |
| `[ACTIVITY_3]` | Dataflow | `[SOURCE]` | `[DEST]` | `[DURATION]` |

## Optimal Configuration

Document the tuned settings for each copy activity:

### Copy Activity: `[ACTIVITY_NAME]`

| Setting | Value | Notes |
|---------|-------|-------|
| ITO | `[Auto/Standard/Balanced/Maximum/Custom]` | |
| Degree of Parallelism | `[Auto/Number]` | |
| Partition Option | `[None/Physical/Dynamic Range]` | |
| Partition Column | `[COLUMN_NAME]` | |
| Partition Upper Bound | `[VALUE]` | |
| Partition Lower Bound | `[VALUE]` | |
| Enable Staging | `[true/false]` | Required for Warehouse sink |
| Source Retry Count | `[NUMBER]` | |
| Isolation Level | `[None/ReadUncommitted/ReadCommitted]` | |

## Known Issues

Document recurring issues and their resolutions:

### Issue 1: `[ISSUE_TITLE]`

- **Symptoms**: [What the user sees]
- **Root Cause**: [Why it happens]
- **Resolution**: [How to fix it]
- **Prevention**: [How to prevent recurrence]

### Issue 2: `[ISSUE_TITLE]`

- **Symptoms**: [What the user sees]
- **Root Cause**: [Why it happens]
- **Resolution**: [How to fix it]
- **Prevention**: [How to prevent recurrence]

## remediate Checklist

When the pipeline runs slower than expected:

- [ ] Check the Monitoring Hub for the run's Duration Breakdown
- [ ] Compare duration against baseline (`[BASELINE_DURATION]`)
- [ ] Verify source system health and connectivity
- [ ] Check destination system health and available capacity
- [ ] Review Fabric capacity utilization (are other jobs consuming resources?)
- [ ] Check for throttling errors (HTTP 430) in the run details
- [ ] Verify credentials and connections are still valid
- [ ] Review if source data volume has increased significantly
- [ ] Check if any configuration was changed recently
- [ ] Run the diagnostic script: `Get-FabricPipelineDiagnostics.ps1`

## Escalation Path

| Level | Contact | When to Escalate |
|-------|---------|-----------------|
| L1 | `[TEAM_MEMBER]` | Duration exceeds SLA by 50% |
| L2 | `[SENIOR_ENGINEER]` | Repeated failures or stuck activities |
| L3 | `[PLATFORM_TEAM]` | Capacity issues or Fabric service problems |

## Performance History

Track performance over time:

| Date | Duration | Status | Notes |
|------|----------|--------|-------|
| `[DATE]` | `[DURATION]` | Success | Baseline |
| | | | |
| | | | |

## Change Log

| Date | Change | Impact | Changed By |
|------|--------|--------|------------|
| `[DATE]` | `[DESCRIPTION]` | `[IMPACT]` | `[PERSON]` |
| | | | |
