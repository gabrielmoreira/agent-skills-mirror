<#
.SYNOPSIS
    Runs OPTIMIZE and VACUUM on a Fabric Lakehouse Delta table via REST API.

.DESCRIPTION
    Submits a table maintenance job (bin-compaction with V-Order and optional Z-Order,
    plus VACUUM) and polls for completion.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace.

.PARAMETER LakehouseId
    The GUID of the Lakehouse item.

.PARAMETER TableName
    The Delta table name to maintain.

.PARAMETER SchemaName
    The schema name (default: "dbo").

.PARAMETER EnableVOrder
    Apply V-Order during compaction (default: true).

.PARAMETER ZOrderColumns
    Optional array of column names for Z-Order optimization.

.PARAMETER VacuumRetentionDays
    Retention period in days for VACUUM (default: 7).

.PARAMETER AccessToken
    A valid Microsoft Entra bearer token.

.PARAMETER PollIntervalSeconds
    Seconds between status polls (default: 15).

.PARAMETER TimeoutMinutes
    Maximum minutes to wait for completion (default: 60).

.EXAMPLE
    ./Invoke-TableMaintenance.ps1 -WorkspaceId "abc" -LakehouseId "def" `
        -TableName "sales_fact" -ZOrderColumns @("date_key","store_key")

.NOTES
    Requires PowerShell 7+.
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
    [int]$VacuumRetentionDays = 7,

    [Parameter()]
    [string]$AccessToken,

    [Parameter()]
    [int]$PollIntervalSeconds = 15,

    [Parameter()]
    [int]$TimeoutMinutes = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Token Acquisition
if (-not $AccessToken) {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        $AccessToken = $tokenResponse.Token
    }
    catch {
        Write-Error 'No AccessToken provided and Az.Accounts token acquisition failed.'
        return
    }
}
#endregion

$headers = @{
    'Authorization' = "Bearer $AccessToken"
    'Content-Type'  = 'application/json'
}

$baseUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId"

#region Build Request Body
$retentionPeriod = "$VacuumRetentionDays.01:00:00"

$executionData = @{
    tableName        = $TableName
    schemaName       = $SchemaName
    optimizeSettings = @{
        vOrder = $EnableVOrder.ToString().ToLower()
    }
    vacuumSettings   = @{
        retentionPeriod = $retentionPeriod
    }
}

if ($ZOrderColumns -and $ZOrderColumns.Count -gt 0) {
    $executionData.optimizeSettings['zOrderBy'] = $ZOrderColumns
}

$body = @{ executionData = $executionData }
#endregion

#region Submit Maintenance Job
Write-Host "`n=== Table Maintenance ===" -ForegroundColor Cyan
Write-Host "Table     : $SchemaName.$TableName"
Write-Host "V-Order   : $EnableVOrder"
if ($ZOrderColumns) {
    Write-Host "Z-Order   : $($ZOrderColumns -join ', ')"
}
Write-Host "VACUUM    : $VacuumRetentionDays days retention"
Write-Host "Timestamp : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)`n"

$submitUri = "$baseUri/jobs/instances?jobType=TableMaintenance"
Write-Host "Submitting maintenance job..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $submitUri -Method POST -Headers $headers `
        -Body ($body | ConvertTo-Json -Depth 10) -UseBasicParsing

    # Extract operation ID from Location header
    $locationHeader = $response.Headers['Location']
    if ($locationHeader) {
        $locationStr = if ($locationHeader -is [array]) { $locationHeader[0] } else { $locationHeader }
        $operationId = ($locationStr -split '/')[-1]
    }
    else {
        # Try to get from response body
        $responseBody = $response.Content | ConvertFrom-Json
        $operationId = $responseBody.id
    }

    if (-not $operationId) {
        Write-Error 'Could not extract operation ID from response.'
        return
    }

    Write-Host "Job submitted. Operation ID: $operationId" -ForegroundColor Green
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $detail = $_.ErrorDetails.Message
    Write-Error "Failed to submit maintenance job ($statusCode): $detail"
    return
}
#endregion

#region Poll for Completion
$statusUri = "$baseUri/jobs/instances/$operationId"
$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$finalStatuses = @('Completed', 'Failed', 'Canceled')

Write-Host "`nPolling for completion (timeout: $TimeoutMinutes min)..." -ForegroundColor Yellow

do {
    Start-Sleep -Seconds $PollIntervalSeconds

    try {
        $status = Invoke-RestMethod -Uri $statusUri -Headers $headers -Method GET
        $jobStatus = $status.status
        $elapsed = if ($status.startTimeUtc) {
            $start = [datetime]::Parse($status.startTimeUtc)
            [math]::Round(((Get-Date) - $start).TotalSeconds)
        }
        else { '?' }

        Write-Host "  Status: $jobStatus (${elapsed}s elapsed)" -ForegroundColor DarkGray
    }
    catch {
        Write-Warning "Poll failed: $($_.Exception.Message)"
        continue
    }
} while ($jobStatus -notin $finalStatuses -and (Get-Date) -lt $deadline)
#endregion

#region Report Result
Write-Host ""
switch ($jobStatus) {
    'Completed' {
        Write-Host "Table maintenance completed successfully." -ForegroundColor Green
        if ($status.startTimeUtc -and $status.endTimeUtc) {
            $duration = [datetime]::Parse($status.endTimeUtc) - [datetime]::Parse($status.startTimeUtc)
            Write-Host "Duration: $($duration.TotalSeconds.ToString('N0')) seconds"
        }
    }
    'Failed' {
        Write-Host "Table maintenance FAILED." -ForegroundColor Red
        if ($status.failureReason) {
            Write-Host "Reason: $($status.failureReason)" -ForegroundColor Red
        }
    }
    'Canceled' {
        Write-Host "Table maintenance was canceled." -ForegroundColor Yellow
    }
    default {
        Write-Host "Timed out waiting for completion. Last status: $jobStatus" -ForegroundColor Yellow
        Write-Host "Check Monitoring Hub for job ID: $operationId"
    }
}

Write-Host "`n=== Maintenance Complete ===" -ForegroundColor Cyan
#endregion
