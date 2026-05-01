# Workspace Monitoring Setup

Configure and use workspace monitoring to track Microsoft Fabric Data Factory pipeline performance over time using KQL queries.

## Table of Contents

- [Enabling Workspace Monitoring](#enabling-workspace-monitoring)
- [Understanding the Monitoring Database](#understanding-the-monitoring-database)
- [KQL Queries for Pipeline Analysis](#kql-queries-for-pipeline-analysis)
- [Performance Dashboards](#performance-dashboards)
- [Alerting on Failures](#alerting-on-failures)

## Enabling Workspace Monitoring

### Prerequisites

- Workspace admin or contributor role
- Fabric capacity (not trial for full functionality)

### Setup Steps

1. Navigate to your Fabric workspace
2. Select **Workspace Settings**
3. Select the **Monitoring** tab
4. Toggle on **Log workspace activity**
5. Fabric creates a Monitoring Eventhouse and a read-only KQL database in your workspace

### What Gets Logged

The `ItemJobEventLogs` table captures pipeline-level events (L1 monitoring):

- Pipeline name
- Run status (Success, Failed, Cancelled)
- Start and end timestamps
- System diagnostics
- Error details for failed runs

**Note**: Activity-level (L2) monitoring is not yet available through workspace monitoring. Use the Monitoring Hub for activity-level details.

## Understanding the Monitoring Database

### Accessing the Database

1. Find the Monitoring Eventhouse in your workspace items
2. Or use the **Monitoring database** link in Workspace Settings > Monitoring

### Table Schema: ItemJobEventLogs

| Column | Type | Description |
|--------|------|-------------|
| Timestamp | datetime | Event timestamp |
| ItemKind | string | Item type (Pipeline, Notebook, etc.) |
| ItemName | string | Name of the item |
| JobId | string | Unique run identifier |
| JobStatus | string | Success, Failed, Cancelled |
| StartTime | datetime | Run start time |
| EndTime | datetime | Run end time |
| ErrorMessage | string | Error details for failed runs |
| DiagnosticsInfo | dynamic | System diagnostic data |

## KQL Queries for Pipeline Analysis

### Pipeline Success/Failure Summary

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline"
| where Timestamp > ago(7d)
| summarize
    TotalRuns = count(),
    Succeeded = countif(JobStatus == "Success"),
    Failed = countif(JobStatus == "Failed"),
    Cancelled = countif(JobStatus == "Cancelled")
    by ItemName
| extend FailureRate = round(100.0 * Failed / TotalRuns, 2)
| order by FailureRate desc
```

### Average Duration by Pipeline

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline"
| where JobStatus == "Success"
| where Timestamp > ago(30d)
| extend Duration = EndTime - StartTime
| summarize
    AvgDuration = avg(Duration),
    MaxDuration = max(Duration),
    MinDuration = min(Duration),
    RunCount = count()
    by ItemName
| order by AvgDuration desc
```

### Duration Trend Over Time

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline"
| where ItemName == "MyPipelineName"
| where JobStatus == "Success"
| where Timestamp > ago(30d)
| extend Duration = EndTime - StartTime
| summarize AvgDuration = avg(Duration) by bin(Timestamp, 1d)
| render timechart
```

### Failed Runs with Error Details

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline"
| where JobStatus == "Failed"
| where Timestamp > ago(7d)
| project Timestamp, ItemName, ErrorMessage, JobId
| order by Timestamp desc
```

### Peak Concurrency Analysis

```kql
ItemJobEventLogs
| where ItemKind in ("Pipeline", "Notebook")
| where Timestamp > ago(7d)
| extend StartTime = Timestamp
| summarize ConcurrentJobs = dcount(JobId) by bin(StartTime, 15m)
| render timechart
```

### Hourly Job Distribution

```kql
ItemJobEventLogs
| where ItemKind == "Pipeline"
| where Timestamp > ago(7d)
| extend HourOfDay = hourofday(Timestamp)
| summarize JobCount = count() by HourOfDay
| order by HourOfDay asc
| render columnchart
```

## Performance Dashboards

### Creating a KQL Dashboard

1. Open the Monitoring Eventhouse
2. Create a new KQL queryset
3. Add the queries above as dashboard tiles
4. Set auto-refresh interval (e.g., every 15 minutes)

### Recommended Dashboard Tiles

1. **Pipeline Health Summary**: Success/failure counts for last 24 hours
2. **Duration Trend**: Line chart of average duration over 30 days
3. **Failure Rate**: Bar chart of failure rates by pipeline
4. **Peak Concurrency**: Time chart of concurrent jobs
5. **Recent Failures**: Table of last 10 failed runs with error details

## Alerting on Failures

### Using Pipeline Activities

Add notification activities to your pipelines:

1. **Outlook Activity**: Send email on pipeline failure
2. **Teams Activity**: Post to Teams channel on failure
3. Use **If Condition** or **On Failure** path to trigger notifications

### Alert Configuration Pattern

```
Pipeline
├── Main Activity (Copy, Notebook, etc.)
│   ├── On Success → [continue or end]
│   └── On Failure → If Condition (check error severity)
│       ├── True → Teams Activity (critical alert)
│       └── False → Outlook Activity (warning email)
```

### KQL-Based Alerts

For proactive monitoring, create scheduled queries that check for:

- Pipelines running longer than 2x their average duration
- Failure rate exceeding a threshold (e.g., >10%)
- Capacity approaching queue limits
- No successful runs in the expected schedule window
