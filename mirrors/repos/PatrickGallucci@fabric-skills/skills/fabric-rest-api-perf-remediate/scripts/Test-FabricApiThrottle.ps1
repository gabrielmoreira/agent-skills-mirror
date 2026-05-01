<#
.SYNOPSIS
    Tests Microsoft Fabric REST API throttle behavior and measures rate limits.

.DESCRIPTION
    Sends controlled bursts of API requests to a Fabric endpoint to detect
    throttling thresholds and capture Retry-After header values. Use this to
    understand your per-user, per-API rate limits before building production
    automation.

.PARAMETER Token
    Bearer token for Fabric REST API authentication.

.PARAMETER WorkspaceId
    Target workspace GUID for test requests.

.PARAMETER BurstSize
    Number of rapid sequential requests per burst. Default: 20.

.PARAMETER DelayBetweenBurstsMs
    Milliseconds to wait between bursts. Default: 1000.

.PARAMETER MaxBursts
    Maximum number of bursts to attempt. Default: 5.

.EXAMPLE
    $token = Get-FabricToken
    .\Test-FabricApiThrottle.ps1 -Token $token -WorkspaceId "abc-123"

.EXAMPLE
    .\Test-FabricApiThrottle.ps1 -Token $token -WorkspaceId "abc-123" -BurstSize 50

.NOTES
    WARNING: This script intentionally triggers throttling for diagnostic purposes.
    Run against non-production workspaces when possible.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Token,

    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [int]$BurstSize = 20,

    [int]$DelayBetweenBurstsMs = 1000,

    [int]$MaxBursts = 5
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$baseUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
$headers = @{
    'Authorization' = "Bearer $Token"
    'Content-Type'  = 'application/json'
}

$results = [System.Collections.Generic.List[PSCustomObject]]::new()

Write-Host "`n=== Fabric REST API Throttle Diagnostic ===" -ForegroundColor Cyan
Write-Host "Target: $baseUri"
Write-Host "Burst Size: $BurstSize | Max Bursts: $MaxBursts"
Write-Host "============================================`n"

for ($burst = 1; $burst -le $MaxBursts; $burst++) {
    Write-Host "--- Burst $burst of $MaxBursts ---" -ForegroundColor Yellow

    for ($i = 1; $i -le $BurstSize; $i++) {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $statusCode = 0
        $retryAfter = $null

        try {
            $response = Invoke-WebRequest -Uri $baseUri -Headers $headers -Method Get -ErrorAction Stop
            $statusCode = $response.StatusCode
            $retryAfter = $response.Headers['Retry-After']
        }
        catch {
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
                $retryAfter = $_.Exception.Response.Headers['Retry-After']

                if ($statusCode -eq 429) {
                    Write-Host "  [$burst.$i] HTTP 429 - Retry-After: ${retryAfter}s" -ForegroundColor Red
                }
                else {
                    Write-Host "  [$burst.$i] HTTP $statusCode" -ForegroundColor DarkYellow
                }
            }
            else {
                $statusCode = -1
                Write-Host "  [$burst.$i] Connection error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }

        $sw.Stop()

        $record = [PSCustomObject]@{
            Burst       = $burst
            Request     = $i
            StatusCode  = $statusCode
            LatencyMs   = $sw.ElapsedMilliseconds
            RetryAfter  = $retryAfter
            Timestamp   = Get-Date -Format 'o'
        }
        $results.Add($record)

        if ($statusCode -eq 200) {
            Write-Host "  [$burst.$i] HTTP 200 - $($sw.ElapsedMilliseconds)ms" -ForegroundColor Green
        }

        # If throttled, honor Retry-After and stop this burst
        if ($statusCode -eq 429 -and $retryAfter) {
            $waitSeconds = [int]$retryAfter
            Write-Host "  Throttled. Waiting ${waitSeconds}s before next burst..." -ForegroundColor Magenta
            Start-Sleep -Seconds $waitSeconds
            break
        }
    }

    if ($burst -lt $MaxBursts) {
        Write-Host "  Cooling down ${DelayBetweenBurstsMs}ms..." -ForegroundColor DarkGray
        Start-Sleep -Milliseconds $DelayBetweenBurstsMs
    }
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan

$total = $results.Count
$throttled = ($results | Where-Object StatusCode -eq 429).Count
$succeeded = ($results | Where-Object StatusCode -eq 200).Count
$avgLatency = ($results | Where-Object StatusCode -eq 200 | Measure-Object -Property LatencyMs -Average).Average
$retryValues = $results | Where-Object { $null -ne $_.RetryAfter } | Select-Object -ExpandProperty RetryAfter -Unique

Write-Host "Total Requests: $total"
Write-Host "Succeeded (200): $succeeded" -ForegroundColor Green
Write-Host "Throttled (429): $throttled" -ForegroundColor $(if ($throttled -gt 0) { 'Red' } else { 'Green' })

if ($avgLatency) {
    Write-Host "Avg Latency (200s): $([math]::Round($avgLatency, 1))ms"
}

if ($retryValues) {
    Write-Host "Retry-After values seen: $($retryValues -join ', ')s" -ForegroundColor Yellow
}

Write-Host "`nThrottle Rate: $([math]::Round(($throttled / $total) * 100, 1))%"

# Output raw data
$results
