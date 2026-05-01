# REST API Table Maintenance Reference

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [API Endpoints](#api-endpoints)
- [Request Examples](#request-examples)
- [Monitoring Operations](#monitoring-operations)
- [Operation Statuses](#operation-statuses)
- [PowerShell Automation](#powershell-automation)

## Overview

The Fabric REST API enables programmatic table maintenance for Lakehouse Delta tables. This is the recommended approach for scheduling and automating OPTIMIZE, V-Order, Z-Order, and VACUUM operations across multiple tables.

The API is asynchronous: submit a maintenance request, then poll for completion status.

## Prerequisites

- Microsoft Entra token for Fabric service
- Fabric REST API endpoint: `https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items`
- Workspace ID and Lakehouse ID (GUIDs)
- Contributor or higher role on the workspace

## API Endpoints

### Submit Table Maintenance

```
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances?jobType=TableMaintenance
```

### Monitor Operation Status

```
GET https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{lakehouseId}/jobs/instances/{operationId}
```

The `operationId` is returned in the `Location` header of the POST response.

## Request Examples

### OPTIMIZE with V-Order Only

```json
{
  "executionData": {
    "tableName": "sales_fact",
    "schemaName": "dbo",
    "optimizeSettings": {
      "vOrder": "true"
    }
  }
}
```

### OPTIMIZE with V-Order and Z-Order

```json
{
  "executionData": {
    "tableName": "sales_fact",
    "schemaName": "dbo",
    "optimizeSettings": {
      "vOrder": "true",
      "zOrderBy": ["customer_id", "order_date"]
    }
  }
}
```

### OPTIMIZE with V-Order, Z-Order, and VACUUM

```json
{
  "executionData": {
    "tableName": "sales_fact",
    "schemaName": "dbo",
    "optimizeSettings": {
      "vOrder": "true",
      "zOrderBy": ["customer_id"]
    },
    "vacuumSettings": {
      "retentionPeriod": "7.01:00:00"
    }
  }
}
```

The `retentionPeriod` format is `d.hh:mm:ss`. The minimum safe value is `7.00:00:00` (7 days). Shorter retention impacts Delta time travel and may cause failures without disabling the retention check.

### VACUUM Only

```json
{
  "executionData": {
    "tableName": "sales_fact",
    "schemaName": "dbo",
    "vacuumSettings": {
      "retentionPeriod": "7.01:00:00"
    }
  }
}
```

## Monitoring Operations

### Response Format

```json
{
  "id": "{operationId}",
  "itemId": "431e8d7b-4a95-4c02-8ccd-6faef5ba1bd7",
  "jobType": "DefaultJob",
  "invokeType": "Manual",
  "status": "Completed",
  "rootActivityId": "8c2ee553-53a4-7edb-1042-0d8189a9e0ca",
  "startTimeUtc": "2025-01-22T06:35:00.7812154",
  "endTimeUtc": "2025-01-22T06:35:00.8033333",
  "failureReason": null
}
```

## Operation Statuses

| Status | Description |
|--------|-------------|
| NotStarted | Job has not started |
| InProgress | Job is currently running |
| Completed | Job finished successfully |
| Failed | Job encountered an error |
| Canceled | Job was canceled |
| Deduped | Another maintenance job is already running on this table; this instance was skipped |

Key behaviors:
- Only one maintenance job can run per table at a time (concurrent submissions return Deduped)
- Maintenance jobs on different tables can execute in parallel
- Jobs consume Fabric capacity of the workspace/user that submitted them
- Track jobs in the Monitoring Hub under "TableMaintenance" activity name

## PowerShell Automation

See the [Invoke-FabricTableMaintenance.ps1](../scripts/Invoke-FabricTableMaintenance.ps1) script for a complete implementation that:
- Authenticates using `Az.Accounts` module
- Iterates over multiple tables in a Lakehouse
- Submits maintenance jobs with configurable V-Order, Z-Order, and VACUUM settings
- Polls for job completion with timeout handling
- Logs results for operational visibility

### Quick PowerShell Example

```powershell
# Get auth token
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token

# Submit maintenance
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

$body = @{
    executionData = @{
        tableName        = "my_table"
        schemaName       = "dbo"
        optimizeSettings = @{ vOrder = "true" }
        vacuumSettings   = @{ retentionPeriod = "7.01:00:00" }
    }
} | ConvertTo-Json -Depth 5

$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items/$lakehouseId/jobs/instances?jobType=TableMaintenance"

$response = Invoke-WebRequest -Uri $uri -Method Post -Headers $headers -Body $body
$operationId = ($response.Headers['Location'] -split '/')[-1]

Write-Host "Maintenance submitted. Operation ID: $operationId"
```
