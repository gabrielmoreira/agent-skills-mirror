<#
.SYNOPSIS
    Measures long running operation (LRO) polling efficiency for Fabric REST APIs.

.DESCRIPTION
    Initiates an LRO-capable operation and profiles the polling cycle to identify
    wasted calls, missed Retry-After hints, and suboptimal polling intervals.
    Outputs a timeline of poll attempts with latency and status progression.

.PARAMETER Token
    Bearer token for Fabric REST API authentication.

.PARAMETER OperationUrl
    The Location header URL from an HTTP 202 response. If not provided, the script
    creates a test item to generate an LRO.

.PARAMETER WorkspaceId
    Workspace GUID (required if OperationUrl is not provided).

.PARAMETER MaxPollMinutes
    Maximum minutes to poll before giving up. Default: 10.

.PARAMETER InitialRetryAfterSeconds
    Initial polling interval if Retry-After header is absent. Default: 5.

.EXAMPLE
    # Poll an existing operation
    .\Measure-FabricLroPolling.ps1 -Token $token -OperationUrl $locationHeader

.EXAMPLE
    # Profile a workspace item creation LRO
    .\Measure-FabricLroPolling.ps1 -Token $token -WorkspaceId "abc-123"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Token,

    [string]$OperationUrl,

    [string]$WorkspaceId,

    [int]$MaxPollMinutes = 10,

    [int]$InitialRetryAfterSeconds = 5
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$headers = @{
    'Authorization' = "Bearer $Token"
    'Content-Type'  = 'application/json'
}

$pollLog = [System.Collections.Generic.List[PSCustomObject]]::new()
$overallSw = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "`n=== Fabric LRO Polling Benchmark ===" -ForegroundColor Cyan

# If no OperationUrl, create a test notebook to trigger an LRO
if (-not $OperationUrl) {
    if (-not $WorkspaceId) {
        Write-Error "Provide either -OperationUrl or -WorkspaceId."
        return
    }

    Write-Host "Creating test notebook to trigger LRO..."
    $createUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/notebooks"
    $body = @{
        displayName = "LRO-Perf-Test-$(Get-Date -Format 'yyyyMMddHHmmss')"
        description = "Temporary notebook for LRO performance measurement"
    } | ConvertTo-Json

    try {
        $createResponse = Invoke-WebRequest -Uri $createUri -Headers $headers -Method Post -Body $body -ErrorAction Stop
        $statusCode = $createResponse.StatusCode

        if ($statusCode -eq 202) {
            $OperationUrl = $createResponse.Headers['Location']
            $retryAfter = $createResponse.Headers['Retry-After']
            $operationId = $createResponse.Headers['x-ms-operation-id']

            Write-Host "LRO initiated. Operation ID: $operationId"
            Write-Host "Location: $OperationUrl"
            Write-Host "Initial Retry-After: ${retryAfter}s"

            if ($retryAfter) {
                $InitialRetryAfterSeconds = [int]$retryAfter
            }
        }
        elseif ($statusCode -in 200, 201) {
            Write-Host "Operation completed synchronously (HTTP $statusCode). No LRO to profile." -ForegroundColor Yellow
            return
        }
    }
    catch {
        Write-Error "Failed to create test item: $($_.Exception.Message)"
        return
    }
}

Write-Host "`nPolling: $OperationUrl"
Write-Host "Max duration: ${MaxPollMinutes} minutes"
Write-Host "Initial interval: ${InitialRetryAfterSeconds}s`n"

$pollCount = 0
$currentWaitSeconds = $InitialRetryAfterSeconds
$deadline = (Get-Date).AddMinutes($MaxPollMinutes)
$terminalStatuses = @('Succeeded', 'Failed', 'Skipped', 'Completed')

do {
    Start-Sleep -Seconds $currentWaitSeconds

    $pollCount++
    $pollSw = [System.Diagnostics.Stopwatch]::StartNew()
    $status = 'Unknown'
    $percentComplete = $null
    $httpStatus = 0
    $nextRetryAfter = $null

    try {
        $pollResponse = Invoke-WebRequest -Uri $OperationUrl -Headers $headers -Method Get -ErrorAction Stop
        $httpStatus = $pollResponse.StatusCode
        $nextRetryAfter = $pollResponse.Headers['Retry-After']

        $body = $pollResponse.Content | ConvertFrom-Json
        $status = $body.status
        $percentComplete = $body.percentComplete
    }
    catch {
        if ($_.Exception.Response) {
            $httpStatus = [int]$_.Exception.Response.StatusCode
        }
        $status = "Error: $($_.Exception.Message)"
    }

    $pollSw.Stop()

    $record = [PSCustomObject]@{
        Poll            = $pollCount
        Status          = $status
        PercentComplete = $percentComplete
        HttpStatus      = $httpStatus
        LatencyMs       = $pollSw.ElapsedMilliseconds
        WaitedSeconds   = $currentWaitSeconds
        RetryAfter      = $nextRetryAfter
        ElapsedTotal    = $overallSw.Elapsed.ToString('mm\:ss\.fff')
        Timestamp       = Get-Date -Format 'HH:mm:ss.fff'
    }
    $pollLog.Add($record)

    $statusColor = switch ($status) {
        'Succeeded'  { 'Green' }
        'Failed'     { 'Red' }
        'Running'    { 'Yellow' }
        default      { 'Gray' }
    }
    Write-Host "  Poll $pollCount | $status $(if ($percentComplete) { "($percentComplete%)" }) | $($pollSw.ElapsedMilliseconds)ms | Total: $($record.ElapsedTotal)" -ForegroundColor $statusColor

    # Update wait interval
    if ($nextRetryAfter) {
        $currentWaitSeconds = [int]$nextRetryAfter
    }
    else {
        # Exponential backoff with cap
        $currentWaitSeconds = [math]::Min($currentWaitSeconds * 2, 60)
    }

} while ($status -notin $terminalStatuses -and (Get-Date) -lt $deadline)

$overallSw.Stop()

# Summary
Write-Host "`n=== LRO Polling Summary ===" -ForegroundColor Cyan
Write-Host "Final Status: $status" -ForegroundColor $(if ($status -eq 'Succeeded') { 'Green' } else { 'Red' })
Write-Host "Total Polls: $pollCount"
Write-Host "Total Duration: $($overallSw.Elapsed.ToString('mm\:ss\.fff'))"

$avgPollLatency = ($pollLog | Measure-Object -Property LatencyMs -Average).Average
$totalWaitTime = ($pollLog | Measure-Object -Property WaitedSeconds -Sum).Sum

Write-Host "Avg Poll Latency: $([math]::Round($avgPollLatency, 1))ms"
Write-Host "Total Wait Time: ${totalWaitTime}s"
Write-Host "Polling Overhead: $([math]::Round(($pollCount * $avgPollLatency) / 1000, 2))s"

if ($pollCount -gt 20) {
    Write-Host "`n[WARNING] High poll count ($pollCount). Consider increasing initial Retry-After or using exponential backoff." -ForegroundColor Yellow
}

# Output raw data
$pollLog
