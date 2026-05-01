<#
.SYNOPSIS
    Executes table maintenance (bin-compaction, V-Order, vacuum) on a Lakehouse table.

.DESCRIPTION
    Submits a table maintenance job via the Fabric REST API and polls for completion.
    Supports V-Order, Z-Order, and vacuum operations individually or combined.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace.

.PARAMETER LakehouseId
    The GUID of the Lakehouse containing the table.

.PARAMETER TableName
    The name of the Delta table to maintain.

.PARAMETER SchemaName
    The schema name (default: "dbo").

.PARAMETER EnableVOrder
    Apply V-Order optimization for read performance.

.PARAMETER ZOrderColumns
    Array of column names to apply Z-Order sorting.

.PARAMETER VacuumRetention
    Vacuum retention period in ISO 8601 duration format (default: "7.01:00:00" = 7 days 1 hour).

.PARAMETER SkipVacuum
    Skip the vacuum operation.

.PARAMETER PollIntervalSeconds
    Seconds between status polls (default: 15).

.PARAMETER TimeoutMinutes
    Maximum minutes to wait for completion (default: 60).

.EXAMPLE
    .\Invoke-TableMaintenance.ps1 -WorkspaceId "fc67..." -LakehouseId "daaa..." `
        -TableName "Orders" -EnableVOrder

.EXAMPLE
    .\Invoke-TableMaintenance.ps1 -WorkspaceId "fc67..." -LakehouseId "daaa..." `
        -TableName "Events" -ZOrderColumns @("eventDate","eventType") -VacuumRetention "14.00:00:00"

.NOTES
    Requires: Az.Accounts module, authenticated Azure session
    API: POST .../jobs/instances?jobType=TableMaintenance
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [string]$TableName,

    [string]$SchemaName = 'dbo',

    [switch]$EnableVOrder,

    [string[]]$ZOrderColumns,

    [string]$VacuumRetention = '7.01:00:00',

    [switch]$SkipVacuum,

    [int]$PollIntervalSeconds = 15,

    [int]$TimeoutMinutes = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $tokenResponse = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
    $headers = @{
        Authorization  = "Bearer $($tokenResponse.Token)"
        'Content-Type' = 'application/json'
    }
    Write-Host "[OK] Authenticated" -ForegroundColor Green
}
catch {
    Write-Error "Authentication failed. Run Connect-AzAccount first. Error: $_"
    return
}
#endregion

#region Build Request Body
$executionData = [ordered]@{
    tableName       = $TableName
    schemaName      = $SchemaName
    optimizeSettings = [ordered]@{
        vOrder = $EnableVOrder.ToString().ToLower()
    }
}

if ($ZOrderColumns -and $ZOrderColumns.Count -gt 0) {
    $executionData.optimizeSettings.zOrderBy = $ZOrderColumns
}

if (-not $SkipVacuum) {
    $executionData.vacuumSettings = @{
        retentionPeriod = $VacuumRetention
    }
}

$body = @{ executionData = $executionData } | ConvertTo-Json -Depth 5
#endregion

#region Submit Job
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances?jobType=TableMaintenance"

Write-Host "`nSubmitting table maintenance job..." -ForegroundColor Cyan
Write-Host "  Table: $SchemaName.$TableName"
Write-Host "  V-Order: $($EnableVOrder.ToString())"
if ($ZOrderColumns) { Write-Host "  Z-Order: $($ZOrderColumns -join ', ')" }
if (-not $SkipVacuum) { Write-Host "  Vacuum: $VacuumRetention retention" }

if (-not $PSCmdlet.ShouldProcess("$SchemaName.$TableName", "Table Maintenance")) {
    Write-Host "WhatIf: Would submit maintenance job." -ForegroundColor Yellow
    return
}

try {
    $response = Invoke-WebRequest `
        -Uri $uri `
        -Headers $headers `
        -Method Post `
        -Body $body `
        -UseBasicParsing

    $statusCode = $response.StatusCode
    Write-Host "  Submitted (HTTP $statusCode)" -ForegroundColor Green
}
catch {
    $errMsg = $_.Exception.Message
    if ($errMsg -match '430') {
        Write-Error "Capacity throttled (HTTP 430). Cancel active jobs or resize SKU."
    }
    else {
        Write-Error "Failed to submit: $errMsg"
    }
    return
}
#endregion

#region Poll for Completion
$locationHeader = $response.Headers['Location']
if (-not $locationHeader) {
    Write-Warning "No Location header returned. Job may have completed synchronously."
    return
}

# Handle array vs string for Location header
$pollUri = if ($locationHeader -is [array]) { $locationHeader[0] } else { $locationHeader }

Write-Host "`nPolling for completion (timeout: $TimeoutMinutes min)..." -ForegroundColor Cyan

$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$lastPercent = -1

while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds $PollIntervalSeconds

    try {
        $status = Invoke-RestMethod -Uri $pollUri -Headers $headers -Method Get
    }
    catch {
        Write-Warning "Poll failed: $($_.Exception.Message). Retrying..."
        continue
    }

    $percent = $status.PercentComplete
    if ($percent -ne $lastPercent) {
        Write-Host "  Progress: $percent%" -ForegroundColor $(if ($percent -ge 100) { 'Green' } else { 'White' })
        $lastPercent = $percent
    }

    if ($percent -ge 100) {
        if ($status.Error) {
            Write-Error "Table maintenance failed: $($status.Error | ConvertTo-Json -Compress)"
        }
        else {
            Write-Host "`n[OK] Table maintenance completed successfully." -ForegroundColor Green
        }
        return
    }
}

Write-Warning "Timed out after $TimeoutMinutes minutes. Job may still be running."
Write-Host "Poll URI for manual checking: $pollUri"
#endregion
