# Workspace Monitoring Setup for Real-Time Intelligence

## Table of Contents

1. [Overview](#overview)
2. [Enabling Workspace Monitoring](#enabling-workspace-monitoring)
3. [Monitoring Tables for Eventhouse](#monitoring-tables-for-eventhouse)
4. [Monitoring Dashboard Templates](#monitoring-dashboard-templates)
5. [Key Queries for RTI Monitoring](#key-queries-for-rti-monitoring)

---

## Overview

Workspace monitoring in Microsoft Fabric provides end-to-end observability for Eventhouse by collecting metrics, query logs, command logs, ingestion result logs, and data operation logs. These logs are stored in a monitoring Eventhouse within your workspace and can be queried using KQL.

---

## Enabling Workspace Monitoring

1. Navigate to your Fabric workspace
2. Open **Workspace settings**
3. Select **Monitoring**
4. Toggle **Enable workspace monitoring** to On
5. A monitoring Eventhouse and KQL database are automatically created in the workspace

Once enabled, data begins flowing into the monitoring tables within minutes.

---

## Monitoring Tables for Eventhouse

| Table | Contents |
|-------|----------|
| **Metrics** | Eventhouse resource utilization: CPU, memory, cache, ingestion volume |
| **QueryLogs** | Individual query executions: text, duration, CPU time, memory peak, cache stats, status |
| **CommandLogs** | Management commands: `.alter`, `.create`, `.drop`, policy changes |
| **DataOperationLogs** | Data operations: exports, moves, purges |
| **IngestionResultLogs** | Per-ingestion-batch results: success/failure, row counts, error details |

---

## Monitoring Dashboard Templates

Microsoft provides two pre-built monitoring dashboard templates:

### Real-Time Dashboard Template

Available from the [fabric-toolbox GitHub repository](https://github.com/microsoft/fabric-toolbox/tree/main/monitoring/workspace-monitoring-dashboards). This dashboard provides:

- Eventhouse overview tab with query count, status trends, and top databases
- Detailed query analysis tab with filtering by CPU, duration, memory, and user
- Ingestion monitoring with success/failure trends

### Power BI Report Template

Also available from the same repository. Use this for scheduled reporting and sharing with stakeholders who prefer Power BI.

### Deploying templates

1. Download the template JSON from the GitHub repository
2. Follow the [Visualize your Workspace Monitoring Data](https://learn.microsoft.com/en-us/fabric/fundamentals/sample-gallery-workspace-monitoring) guide
3. Connect the dashboard to your monitoring Eventhouse
4. Customize filters and time ranges for your environment

---

## Key Queries for RTI Monitoring

### Top queries by CPU time (last 24 hours)

```kql
QueryLogs
| where TimeGenerated > ago(24h)
| where State == "Completed"
| project User, QueryText = substring(Text, 0, 200), 
    DurationMs = Duration / 1ms, 
    TotalCPUMs = TotalCPU / 1ms, 
    MemoryPeakMB = MemoryPeak / 1MB
| order by TotalCPUMs desc
| take 25
```

### Failed queries trend

```kql
QueryLogs
| where TimeGenerated > ago(7d)
| summarize 
    Total = count(),
    Failed = countif(State == "Failed"),
    Throttled = countif(State == "Throttled")
    by bin(TimeGenerated, 1h)
| extend FailRate = round(100.0 * Failed / Total, 1)
| order by TimeGenerated asc
```

### Ingestion success rate

```kql
IngestionResultLogs
| where TimeGenerated > ago(24h)
| summarize 
    Total = count(),
    Succeeded = countif(Status == "Succeeded"),
    Failed = countif(Status == "Failed")
    by bin(TimeGenerated, 1h), Database, Table
| extend SuccessRate = round(100.0 * Succeeded / Total, 1)
| order by TimeGenerated desc
```

### Ingestion volume by table

```kql
IngestionResultLogs
| where TimeGenerated > ago(24h)
| where Status == "Succeeded"
| summarize 
    TotalRows = sum(RowCount),
    TotalSizeMB = sum(OriginalSize) / 1MB,
    BatchCount = count()
    by Database, Table
| order by TotalSizeMB desc
```

### Eventhouse resource utilization

```kql
Metrics
| where TimeGenerated > ago(6h)
| where MetricName in ("CpuUsage", "MemoryUsage", "CacheUtilization")
| summarize AvgValue = avg(Value), MaxValue = max(Value)
    by MetricName, bin(TimeGenerated, 5m)
| order by TimeGenerated asc
```

These queries can be saved in a KQL Queryset for repeated use, or embedded into the monitoring dashboard templates.
