<#
.SYNOPSIS
    Executes table maintenance (OPTIMIZE + V-Order + VACUUM) on a lakehouse
    table via the Fabric REST API.

.DESCRIPTION
    Submits an asynchronous table maintenance job for a specified lakehouse table
    and polls until completion. Supports V-Order, Z-Order, and VACUUM operations.

.PARAMETER WorkspaceId
    The Fabric workspace ID.

.PARAMETER LakehouseId
    The Fabric lakehouse item ID.

.PARAMETER TableName
    The Delta table name to maintain.

.PARAMETER SchemaName
    The schema name (default: "dbo").

.PARAMETER EnableVOrder
    Apply V-Order optimization (default: true).

.PARAMETER ZOrderColumns
    Columns to apply Z-Order on (optional).

.PARAMETER VacuumRetentionDays
    VACUUM retention period in days (default: 7). Minimum 7 recommended.

.PARAMETER SkipVacuum
    Skip the VACUUM operation.

.PARAMETER PollIntervalSeconds
    Seconds between status checks (default: 15).

.PARAMETER TimeoutMinutes
    Maximum wait time in minutes (default: 60).

.EXAMPLE
    ./run-table-maintenance.ps1 -WorkspaceId "aaa" -LakehouseId "bbb" -TableName "fact_orders"

.EXAMPLE
    ./run-table-maintenance.ps1 -WorkspaceId "aaa" -LakehouseId "bbb" -TableName "fact_orders" -ZOrderColumns @("customer_id","order_date") -VacuumRetentionDays 14

.NOTES
    Requires: PowerShell 7+, Az.Accounts module, authenticated to Azure.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [string]$TableName,

    [Parameter()]
    [string]$SchemaName = 'dbo',

    [Parameter()]
    [bool]$EnableVOrder = $true,

    [Parameter()]
    [string[]]$ZOrderColumns,

    [Parameter()]
    [ValidateRange(1, 365)]
    [int]$VacuumRetentionDays = 7,

    [Parameter()]
    [switch]$SkipVacuum,

    [Parameter()]
    [int]$PollIntervalSeconds = 15,

    [Parameter()]
    [int]$TimeoutMinutes = 60
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-FabricAccessToken {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        return $tokenResponse.Token
    }
    catch {
        Write-Error "Failed to get access token. Run Connect-AzAccount first. Error: $_"
        throw
    }
}

function Invoke-FabricApi {
    param(
        [string]$Url,
        [string]$Method = 'GET',
        [string]$Token,
        [object]$Body
    )
    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }
    $params = @{
        Uri     = $Url
        Method  = $Method
        Headers = $headers
    }
    if ($Body) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
    }
    return Invoke-WebRequest @params -ErrorAction Stop
}

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
Write-Host "`n=== OneLake Table Maintenance ===" -ForegroundColor Cyan
Write-Host "Workspace:  $WorkspaceId" -ForegroundColor Gray
Write-Host "Lakehouse:  $LakehouseId" -ForegroundColor Gray
Write-Host "Table:      $SchemaName.$TableName" -ForegroundColor Gray
Write-Host "V-Order:    $EnableVOrder" -ForegroundColor Gray
Write-Host "Z-Order:    $(if ($ZOrderColumns) { $ZOrderColumns -join ', ' } else { 'None' })" -ForegroundColor Gray
Write-Host "Vacuum:     $(if ($SkipVacuum) { 'Skipped' } else { "$VacuumRetentionDays day(s) retention" })" -ForegroundColor Gray
Write-Host "Timestamp:  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)" -ForegroundColor Gray

if ($VacuumRetentionDays -lt 7 -and -not $SkipVacuum) {
    Write-Warning "Retention period less than 7 days may break Delta time travel and cause reader failures."
    Write-Warning "Consider using -VacuumRetentionDays 7 or higher."
}

$token = Get-FabricAccessToken

# Build the request body
$executionData = @{
    tableName      = $TableName
    schemaName     = $SchemaName
    optimizeSettings = @{
        vOrder = $EnableVOrder.ToString().ToLower()
    }
}

if ($ZOrderColumns -and $ZOrderColumns.Count -gt 0) {
    $executionData.optimizeSettings.zOrderBy = $ZOrderColumns
}

if (-not $SkipVacuum) {
    $retentionSpan = [TimeSpan]::FromDays($VacuumRetentionDays).Add([TimeSpan]::FromHours(1))
    $executionData.vacuumSettings = @{
        retentionPeriod = $retentionSpan.ToString()
    }
}

$body = @{ executionData = $executionData }

# Submit the maintenance job
$submitUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances?jobType=TableMaintenance"

Write-Host "`nSubmitting table maintenance job..." -ForegroundColor Yellow

try {
    $response = Invoke-FabricApi -Url $submitUrl -Method 'POST' -Token $token -Body $body
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 430) {
        Write-Error "HTTP 430: Capacity is at maximum utilization. Cancel active jobs or scale up the SKU."
    }
    else {
        Write-Error "Failed to submit maintenance job: $($_.Exception.Message)"
    }
    throw
}

# Extract operation ID from Location header
$locationHeader = $response.Headers['Location']
if (-not $locationHeader) {
    Write-Error "No Location header in response. Unable to track operation."
    exit 1
}

$locationUri = if ($locationHeader -is [array]) { $locationHeader[0] } else { $locationHeader }
$operationId = ($locationUri -split '/')[-1]

Write-Host "Job submitted. Operation ID: $operationId" -ForegroundColor Green

# Poll for completion
$statusUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId/jobs/instances/$operationId"
$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$finalStatuses = @('Completed', 'Failed', 'Canceled', 'Deduped')

Write-Host "Polling for completion (timeout: $TimeoutMinutes minutes)..." -ForegroundColor Yellow

do {
    Start-Sleep -Seconds $PollIntervalSeconds

    try {
        $statusResponse = Invoke-FabricApi -Url $statusUrl -Token $token
        $statusBody = $statusResponse.Content | ConvertFrom-Json
        $jobStatus = $statusBody.status
    }
    catch {
        Write-Warning "Status check failed: $($_.Exception.Message). Retrying..."
        continue
    }

    $elapsed = [math]::Round(((Get-Date) - (Get-Date).AddMinutes(-$TimeoutMinutes)).TotalMinutes, 1)
    Write-Host "  Status: $jobStatus (polling...)" -ForegroundColor Gray

} while ($jobStatus -notin $finalStatuses -and (Get-Date) -lt $deadline)

# Final result
Write-Host ""
switch ($jobStatus) {
    'Completed' {
        Write-Host "Table maintenance completed successfully." -ForegroundColor Green
    }
    'Failed' {
        Write-Host "Table maintenance FAILED." -ForegroundColor Red
        if ($statusBody.failureReason) {
            Write-Host "Reason: $($statusBody.failureReason)" -ForegroundColor Red
        }
    }
    'Canceled' {
        Write-Host "Table maintenance was canceled." -ForegroundColor Yellow
    }
    'Deduped' {
        Write-Host "Job was deduped — another maintenance job for the same table is already running." -ForegroundColor Yellow
    }
    default {
        Write-Warning "Timed out after $TimeoutMinutes minutes. Current status: $jobStatus"
        Write-Warning "Check the Monitoring Hub for the operation: $operationId"
    }
}

Write-Host ""
