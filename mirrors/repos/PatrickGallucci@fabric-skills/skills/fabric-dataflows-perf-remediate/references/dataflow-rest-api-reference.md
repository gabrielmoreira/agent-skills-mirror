# Dataflow Gen2 REST API Reference

API operations for automating Dataflow Gen2 management, monitoring, and troubleshooting in Microsoft Fabric.

## Table of Contents

- [Authentication](#authentication)
- [Dataflow CRUD Operations](#dataflow-crud-operations)
- [Refresh Operations](#refresh-operations)
- [Scheduling](#scheduling)
- [Monitoring and Status](#monitoring-and-status)
- [Definition Management](#definition-management)
- [Common API Patterns](#common-api-patterns)

---

## Authentication

All Fabric REST API calls require a Bearer token from Azure AD.

### PowerShell Authentication

```powershell
# Interactive login
Connect-AzAccount

# Get token for Fabric API
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}
```

### Base URL

```
https://api.fabric.microsoft.com/v1
```

---

## Dataflow CRUD Operations

### List Dataflows in Workspace

```
GET /workspaces/{workspaceId}/dataflows
```

```powershell
$workspaceId = "<workspace-id>"
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/dataflows"
$dataflows = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
$dataflows.value | Format-Table id, displayName, description
```

### Get Dataflow Details

```
GET /workspaces/{workspaceId}/dataflows/{dataflowId}
```

### Create Dataflow

```
POST /workspaces/{workspaceId}/dataflows
```

Request body:
```json
{
  "displayName": "My Dataflow",
  "description": "Optional description"
}
```

### Update Dataflow

```
PATCH /workspaces/{workspaceId}/dataflows/{dataflowId}
```

### Delete Dataflow

```
DELETE /workspaces/{workspaceId}/dataflows/{dataflowId}
```

---

## Refresh Operations

### Trigger Refresh

```
POST /workspaces/{workspaceId}/dataflows/{dataflowId}/refresh
```

```powershell
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/dataflows/$dataflowId/refresh"
Invoke-RestMethod -Uri $uri -Headers $headers -Method Post
```

### Run On-Demand Dataflow Publish Job

For CI/CD-enabled dataflows that need to be published after Git sync or deployment pipeline changes:

```
POST /workspaces/{workspaceId}/dataflows/{dataflowId}/publishJob
```

---

## Scheduling

### Get Refresh Schedule

```
GET /workspaces/{workspaceId}/dataflows/{dataflowId}/getRefreshSchedule
```

### Update Refresh Schedule

```
PATCH /workspaces/{workspaceId}/dataflows/{dataflowId}/updateRefreshSchedule
```

Request body example:
```json
{
  "value": {
    "enabled": true,
    "frequency": "Daily",
    "times": ["08:00", "16:00"],
    "timeZone": "UTC"
  }
}
```

---

## Monitoring and Status

### Get Item Job Instances (Refresh History)

```
GET /workspaces/{workspaceId}/items/{dataflowId}/jobs/instances
```

```powershell
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items/$dataflowId/jobs/instances"
$jobs = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
$jobs.value | Select-Object id, status, startTimeUtc, endTimeUtc, 
    @{N='DurationMin'; E={
        if ($_.endTimeUtc -and $_.startTimeUtc) {
            [math]::Round(([datetime]$_.endTimeUtc - [datetime]$_.startTimeUtc).TotalMinutes, 2)
        } else { 'Running' }
    }} | Format-Table
```

### Workspace Item Status

```
GET /workspaces/{workspaceId}/items
```

Filter for dataflow items:
```powershell
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId/items"
$items = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
$dataflowItems = $items.value | Where-Object { $_.type -eq "Dataflow" }
```

---

## Definition Management

### Get Dataflow Definition

```
POST /workspaces/{workspaceId}/dataflows/{dataflowId}/getDefinition
```

Returns two definition parts:
- `queryMetadata.json` — Metadata ContentDetails (JSON): format version, compute engine settings, query metadata, connections
- `mashup.pq` — Mashup ContentDetails (PQ): Power Query M code with all transformation steps

### Key Definition Fields (queryMetadata.json)

| Field | Type | Description |
|-------|------|-------------|
| formatVersion | String | Must be "202502" |
| name | String | Mashup name |
| computeEngineSettings.allowFastCopy | Boolean | Fast Copy enabled (default: true) |
| computeEngineSettings.maxConcurrency | Integer | Max concurrent evaluations |
| fastCombine | Boolean | Fast combine enabled |
| allowNativeQueries | Boolean | Native queries allowed (default: true) |
| skipAutomaticTypeAndHeaderDetection | Boolean | Skip auto detection |
| queriesMetadata | Object | Per-query settings (ID, name, hidden, loadEnabled) |
| connections | Array | Connection paths, kinds, and IDs |

### Update Dataflow Definition

```
POST /workspaces/{workspaceId}/dataflows/{dataflowId}/updateDefinition
```

Request body:
```json
{
  "definition": {
    "parts": [
      {
        "path": "queryMetadata.json",
        "payload": "<base64-encoded-json>",
        "payloadType": "InlineBase64"
      },
      {
        "path": "mashup.pq",
        "payload": "<base64-encoded-pq>",
        "payloadType": "InlineBase64"
      }
    ]
  }
}
```

---

## Common API Patterns

### List All Dataflows Across Workspaces

```powershell
function Get-AllFabricDataflows {
    param([string]$Token)
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type"  = "application/json"
    }
    
    $workspaces = (Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces" -Headers $headers).value
    
    foreach ($ws in $workspaces) {
        try {
            $dfs = (Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$($ws.id)/dataflows" -Headers $headers).value
            foreach ($df in $dfs) {
                [PSCustomObject]@{
                    WorkspaceName = $ws.displayName
                    WorkspaceId   = $ws.id
                    DataflowName  = $df.displayName
                    DataflowId    = $df.id
                }
            }
        } catch {
            Write-Warning "Skipped workspace '$($ws.displayName)': $($_.Exception.Message)"
        }
    }
}
```

### Check If Fast Copy Is Enabled

```powershell
function Test-FastCopyEnabled {
    param(
        [string]$WorkspaceId,
        [string]$DataflowId,
        [hashtable]$Headers
    )
    
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/dataflows/$DataflowId/getDefinition"
    $def = Invoke-RestMethod -Uri $uri -Headers $Headers -Method Post
    
    $metaPart = $def.definition.parts | Where-Object { $_.path -eq "queryMetadata.json" }
    if ($metaPart) {
        $metaJson = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($metaPart.payload))
        $metadata = $metaJson | ConvertFrom-Json
        return $metadata.computeEngineSettings.allowFastCopy
    }
    return $null
}
```

### Trigger Refresh and Poll for Completion

```powershell
function Start-DataflowRefreshAndWait {
    param(
        [string]$WorkspaceId,
        [string]$DataflowId,
        [hashtable]$Headers,
        [int]$TimeoutMinutes = 60,
        [int]$PollIntervalSeconds = 30
    )
    
    # Trigger refresh
    $refreshUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/dataflows/$DataflowId/refresh"
    Invoke-RestMethod -Uri $refreshUri -Headers $Headers -Method Post
    
    Write-Host "Refresh triggered. Polling for completion..."
    $startTime = Get-Date
    $timeout = $startTime.AddMinutes($TimeoutMinutes)
    
    do {
        Start-Sleep -Seconds $PollIntervalSeconds
        $jobsUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$DataflowId/jobs/instances"
        $jobs = (Invoke-RestMethod -Uri $jobsUri -Headers $Headers).value
        $latest = $jobs | Sort-Object startTimeUtc -Descending | Select-Object -First 1
        
        $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
        Write-Host "  [$elapsed min] Status: $($latest.status)"
        
        if ($latest.status -in @("Completed", "Failed", "Cancelled")) {
            return $latest
        }
    } while ((Get-Date) -lt $timeout)
    
    Write-Warning "Timeout after $TimeoutMinutes minutes"
    return $latest
}
```
