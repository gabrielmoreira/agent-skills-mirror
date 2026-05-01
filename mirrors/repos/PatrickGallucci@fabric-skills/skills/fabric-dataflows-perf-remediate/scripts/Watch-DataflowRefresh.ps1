<#
.SYNOPSIS
    Monitors active Dataflow Gen2 refresh operations in real-time.

.DESCRIPTION
    Polls the Fabric REST API to track the status of a dataflow refresh.
    Triggers a refresh if requested, then monitors progress until completion,
    failure, or timeout. Outputs status updates to the console with timing.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace containing the dataflow.

.PARAMETER DataflowId
    The GUID of the dataflow to monitor.

.PARAMETER TriggerRefresh
    Optional. If set, triggers a new refresh before monitoring.

.PARAMETER PollIntervalSeconds
    Optional. Seconds between status checks. Default: 30.

.PARAMETER TimeoutMinutes
    Optional. Maximum minutes to wait before timing out. Default: 120.

.EXAMPLE
    .\Watch-DataflowRefresh.ps1 -WorkspaceId "xxx" -DataflowId "yyy"

.EXAMPLE
    .\Watch-DataflowRefresh.ps1 -WorkspaceId "xxx" -DataflowId "yyy" -TriggerRefresh -PollIntervalSeconds 15

.NOTES
    Requires: PowerShell 7+, Az.Accounts module
    Authentication: Run Connect-AzAccount before executing this script.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [string]$DataflowId,

    [Parameter(Mandatory = $false)]
    [switch]$TriggerRefresh,

    [Parameter(Mandatory = $false)]
    [int]$PollIntervalSeconds = 30,

    [Parameter(Mandatory = $false)]
    [int]$TimeoutMinutes = 120
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$baseUri = "https://api.fabric.microsoft.com/v1"

# --- Authentication ---
function Get-FabricHeaders {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com" -ErrorAction Stop
        return @{
            "Authorization" = "Bearer $($tokenResponse.Token)"
            "Content-Type"  = "application/json"
        }
    }
    catch {
        Write-Error "Authentication failed. Run 'Connect-AzAccount' first. Error: $_"
        exit 1
    }
}

# --- Get Dataflow Info ---
function Get-DataflowName {
    param([string]$WsId, [string]$DfId, [hashtable]$Headers)
    try {
        $uri = "$baseUri/workspaces/$WsId/dataflows/$DfId"
        $df = Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get
        return $df.displayName
    }
    catch {
        return "Unknown"
    }
}

# --- Get Latest Job Instance ---
function Get-LatestJobInstance {
    param([string]$WsId, [string]$DfId, [hashtable]$Headers)
    $uri = "$baseUri/workspaces/$WsId/items/$DfId/jobs/instances"
    $jobs = Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get
    if ($jobs.value) {
        return $jobs.value | Sort-Object startTimeUtc -Descending | Select-Object -First 1
    }
    return $null
}

# --- Main ---
$headers = Get-FabricHeaders
$dataflowName = Get-DataflowName -WsId $WorkspaceId -DfId $DataflowId -Headers $headers

Write-Host "`n=== Dataflow Refresh Monitor ===" -ForegroundColor Cyan
Write-Host "Dataflow : $dataflowName"
Write-Host "ID       : $DataflowId"
Write-Host "Workspace: $WorkspaceId"
Write-Host "Timeout  : $TimeoutMinutes minutes"
Write-Host "Poll     : Every $PollIntervalSeconds seconds`n"

# --- Trigger Refresh ---
if ($TriggerRefresh) {
    Write-Host "Triggering refresh..." -ForegroundColor Yellow
    try {
        $refreshUri = "$baseUri/workspaces/$WorkspaceId/dataflows/$DataflowId/refresh"
        Invoke-RestMethod -Uri $refreshUri -Headers $headers -Method Post
        Write-Host "Refresh triggered successfully." -ForegroundColor Green
        Start-Sleep -Seconds 5  # Brief wait for job to register
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 429) {
            Write-Warning "Rate limited (429). A refresh may already be in progress."
        }
        else {
            Write-Error "Failed to trigger refresh: $_"
            exit 1
        }
    }
}

# --- Monitor Loop ---
$startTime = Get-Date
$timeout = $startTime.AddMinutes($TimeoutMinutes)
$lastStatus = ""
$refreshStartTime = $null

Write-Host "Monitoring refresh status..." -ForegroundColor Yellow
Write-Host ("-" * 60)

do {
    # Re-authenticate periodically (tokens expire)
    $elapsed = ((Get-Date) - $startTime).TotalMinutes
    if ($elapsed -gt 45) {
        $headers = Get-FabricHeaders
    }

    $latest = Get-LatestJobInstance -WsId $WorkspaceId -DfId $DataflowId -Headers $headers

    if ($latest) {
        $status = $latest.status
        $jobStart = if ($latest.startTimeUtc) { [datetime]$latest.startTimeUtc } else { $null }
        $jobEnd = if ($latest.endTimeUtc) { [datetime]$latest.endTimeUtc } else { $null }

        # Track refresh start
        if (-not $refreshStartTime -and $jobStart) {
            $refreshStartTime = $jobStart
        }

        # Calculate running duration
        $runningDuration = if ($jobEnd -and $jobStart) {
            [math]::Round(($jobEnd - $jobStart).TotalMinutes, 2)
        }
        elseif ($jobStart) {
            [math]::Round(((Get-Date).ToUniversalTime() - $jobStart).TotalMinutes, 2)
        }
        else { 0 }

        $timestamp = Get-Date -Format "HH:mm:ss"

        # Status-specific formatting
        $statusColor = switch ($status) {
            "Completed" { "Green" }
            "Failed"    { "Red" }
            "Cancelled" { "Yellow" }
            "InProgress" { "White" }
            "NotStarted" { "DarkYellow" }
            default     { "Gray" }
        }

        if ($status -ne $lastStatus) {
            Write-Host "[$timestamp] Status changed: " -NoNewline
            Write-Host "$status" -ForegroundColor $statusColor -NoNewline
            Write-Host " (Duration: $runningDuration min)"
            $lastStatus = $status
        }
        else {
            Write-Host "[$timestamp] $status - $runningDuration min elapsed" -ForegroundColor $statusColor
        }

        # Terminal states
        if ($status -in @("Completed", "Failed", "Cancelled")) {
            Write-Host ("-" * 60)
            Write-Host "`nRefresh finished." -ForegroundColor Cyan

            $resultColor = switch ($status) {
                "Completed" { "Green" }
                "Failed"    { "Red" }
                default     { "Yellow" }
            }
            Write-Host "  Status   : " -NoNewline
            Write-Host "$status" -ForegroundColor $resultColor
            Write-Host "  Started  : $jobStart"
            Write-Host "  Ended    : $jobEnd"
            Write-Host "  Duration : $runningDuration minutes"

            if ($status -eq "Failed") {
                Write-Host "`n  Troubleshooting:" -ForegroundColor Red
                Write-Host "  1. Check refresh history in Fabric UI for error details"
                Write-Host "  2. Download detailed logs from the refresh details page"
                Write-Host "  3. Verify data source connectivity and credentials"
                Write-Host "  4. Check capacity utilization in Monitoring Hub"
                Write-Host "  5. Review staging artifact permissions`n"
            }

            return $latest
        }
    }
    else {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] No job instances found. Waiting..." -ForegroundColor DarkGray
    }

    Start-Sleep -Seconds $PollIntervalSeconds

} while ((Get-Date) -lt $timeout)

Write-Host ("-" * 60)
Write-Warning "Monitoring timed out after $TimeoutMinutes minutes."
Write-Host "The refresh may still be running. Check Monitoring Hub for status.`n"
return $latest
