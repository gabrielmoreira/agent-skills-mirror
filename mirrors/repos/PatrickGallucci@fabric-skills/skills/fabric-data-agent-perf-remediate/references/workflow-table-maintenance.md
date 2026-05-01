# Workflow: Lakehouse Table Maintenance

## Table of Contents

- [When to Run Maintenance](#when-to-run-maintenance)
- [Maintenance Operations](#maintenance-operations)
- [REST API Usage](#rest-api-usage)
- [Scheduling Maintenance](#scheduling-maintenance)

## When to Run Maintenance

Run table maintenance when:
- Delta table queries are progressively slower over time
- Small file problem: thousands of tiny Parquet files instead of fewer large ones
- Data Agent queries return stale or inconsistent results
- VOrder has never been applied to read-heavy tables
- Old unreferenced files are consuming storage

## Maintenance Operations

| Operation | What It Does | When to Use |
|-----------|-------------|-------------|
| Bin-compaction | Merges small files into optimal-sized files | After many small inserts/appends |
| V-Order | Applies Parquet column sorting for read performance | Tables queried by Power BI or Data Warehouse |
| Z-Order | Applies multi-column co-location sorting | Tables filtered on specific columns frequently |
| Vacuum | Removes unreferenced files older than retention period | Periodically to reclaim storage |

## REST API Usage

### Submit Table Maintenance Job

```
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance
```

**Request body (V-Order + Z-Order + Vacuum):**
```json
{
  "executionData": {
    "tableName": "{table_name}",
    "schemaName": "{schema_name}",
    "optimizeSettings": {
      "vOrder": "true",
      "zOrderBy": ["tipAmount"]
    },
    "vacuumSettings": {
      "retentionPeriod": "7.01:00:00"
    }
  }
}
```

**Request body (Bin-compaction only):**
```json
{
  "executionData": {
    "tableName": "{table_name}",
    "schemaName": "{schema_name}",
    "optimizeSettings": {
      "vOrder": "false"
    }
  }
}
```

### Track Job Status

The table maintenance API is asynchronous. After submitting, poll the operation status:

```powershell
# Poll until PercentComplete = 100
$statusUri = $response.Headers['Location']
do {
    Start-Sleep -Seconds 10
    $status = Invoke-RestMethod -Uri $statusUri -Headers $headers -Method Get
    Write-Host "Progress: $($status.PercentComplete)%"
} while ($status.PercentComplete -lt 100)

if ($status.Error) {
    Write-Error "Maintenance failed: $($status.Error)"
} else {
    Write-Host "Table maintenance completed successfully."
}
```

## Scheduling Maintenance

**Recommendation for Data Agent workloads:**

| Table Type | Frequency | Operations |
|-----------|-----------|------------|
| High-write tables (streaming ingestion) | Daily | Bin-compaction + Vacuum |
| Read-heavy analytics tables | Weekly | V-Order + Bin-compaction |
| Partitioned tables with Z-Order needs | Weekly | Z-Order + Vacuum |
| Archive/cold tables | Monthly | Vacuum only |

Use Fabric Pipelines or Azure Data Factory to schedule maintenance jobs on a recurring basis.
