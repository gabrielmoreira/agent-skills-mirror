<#
.SYNOPSIS
    Collects diagnostic information for Microsoft Fabric Data Factory pipeline performance remediate.

.DESCRIPTION
    Gathers pipeline run history, activity durations, capacity utilization indicators,
    and generates a diagnostic report for performance analysis. Uses the Fabric REST API
    to retrieve pipeline run details and activity run information.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace containing the pipeline.

.PARAMETER PipelineName
    The name of the pipeline to diagnose. If omitted, retrieves data for all pipelines.

.PARAMETER LookbackHours
    Number of hours to look back for pipeline runs. Default is 24.

.PARAMETER OutputPath
    Path for the diagnostic report output. Default is current directory.

.PARAMETER AccessToken
    Bearer token for Fabric API authentication. If omitted, attempts to use Az PowerShell module.

.EXAMPLE
    ./Get-FabricPipelineDiagnostics.ps1 -WorkspaceId "12345678-abcd-1234-abcd-123456789012" -PipelineName "MyPipeline"

.EXAMPLE
    ./Get-FabricPipelineDiagnostics.ps1 -WorkspaceId "12345678-abcd-1234-abcd-123456789012" -LookbackHours 72 -OutputPath "C:\Reports"

.NOTES
    Requires PowerShell 7+ and either:
    - A valid Fabric API access token, or
    - Az PowerShell module with active login (Connect-AzAccount)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $false)]
    [string]$PipelineName,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 720)]
    [int]$LookbackHours = 24,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Get-Location).Path,

    [Parameter(Mandatory = $false)]
    [string]$AccessToken
)

#region Helper Functions

function Get-FabricAccessToken {
    <#
    .SYNOPSIS
        Obtains a Fabric API access token using Az PowerShell module.
    #>
    [CmdletBinding()]
    param()

    try {
        $token = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com" -ErrorAction Stop
        return $token.Token
    }
    catch {
        Write-Error "Failed to obtain access token. Run Connect-AzAccount first or provide -AccessToken parameter."
        throw
    }
}

function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Makes an authenticated REST call to the Fabric API.
    #>
    [CmdletBinding()]
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [string]$Token,
        [object]$Body
    )

    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type"  = "application/json"
    }

    $params = @{
        Uri     = $Uri
        Method  = $Method
        Headers = $headers
    }

    if ($Body) {
        $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
    }

    try {
        $response = Invoke-RestMethod @params -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Warning "API call failed with status $statusCode`: $($_.Exception.Message)"
        return $null
    }
}

function Format-Duration {
    <#
    .SYNOPSIS
        Formats a TimeSpan or milliseconds into a human-readable duration string.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        $Duration
    )

    if ($Duration -is [TimeSpan]) {
        $ts = $Duration
    }
    elseif ($Duration -is [int] -or $Duration -is [long] -or $Duration -is [double]) {
        $ts = [TimeSpan]::FromMilliseconds($Duration)
    }
    else {
        return "N/A"
    }

    if ($ts.TotalHours -ge 1) {
        return "{0:D2}h {1:D2}m {2:D2}s" -f [int]$ts.TotalHours, $ts.Minutes, $ts.Seconds
    }
    elseif ($ts.TotalMinutes -ge 1) {
        return "{0:D2}m {1:D2}s" -f [int]$ts.TotalMinutes, $ts.Seconds
    }
    else {
        return "{0:D2}s" -f [int]$ts.TotalSeconds
    }
}

#endregion

#region Main Execution

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Fabric Data Factory Pipeline Diagnostics" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Obtain access token
if (-not $AccessToken) {
    Write-Host "No access token provided. Attempting to use Az PowerShell module..." -ForegroundColor Yellow
    $AccessToken = Get-FabricAccessToken
}

$baseUrl = "https://api.fabric.microsoft.com/v1"
$cutoffTime = (Get-Date).AddHours(-$LookbackHours).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

Write-Host "Workspace ID  : $WorkspaceId" -ForegroundColor Gray
Write-Host "Pipeline      : $($PipelineName ?? 'All pipelines')" -ForegroundColor Gray
Write-Host "Lookback      : $LookbackHours hours (since $cutoffTime)" -ForegroundColor Gray
Write-Host ""

# Step 1: List workspace items to find pipelines
Write-Host "[1/4] Retrieving workspace items..." -ForegroundColor Yellow
$items = Invoke-FabricApi -Uri "$baseUrl/workspaces/$WorkspaceId/items?type=DataPipeline" -Token $AccessToken

if (-not $items -or -not $items.value) {
    Write-Error "No pipeline items found in workspace $WorkspaceId."
    exit 1
}

$pipelines = $items.value
if ($PipelineName) {
    $pipelines = $pipelines | Where-Object { $_.displayName -eq $PipelineName }
    if (-not $pipelines) {
        Write-Error "Pipeline '$PipelineName' not found in workspace."
        exit 1
    }
}

Write-Host "  Found $($pipelines.Count) pipeline(s)" -ForegroundColor Green

# Step 2: Get job history for each pipeline
Write-Host "[2/4] Retrieving pipeline run history..." -ForegroundColor Yellow
$allRuns = @()

foreach ($pipeline in $pipelines) {
    $jobsUrl = "$baseUrl/workspaces/$WorkspaceId/items/$($pipeline.id)/jobs"
    $jobs = Invoke-FabricApi -Uri $jobsUrl -Token $AccessToken

    if ($jobs -and $jobs.value) {
        foreach ($job in $jobs.value) {
            $allRuns += [PSCustomObject]@{
                PipelineName = $pipeline.displayName
                PipelineId   = $pipeline.id
                JobId        = $job.id
                Status       = $job.status
                StartTime    = if ($job.startTimeUtc) { [datetime]::Parse($job.startTimeUtc) } else { $null }
                EndTime      = if ($job.endTimeUtc) { [datetime]::Parse($job.endTimeUtc) } else { $null }
                Duration     = if ($job.startTimeUtc -and $job.endTimeUtc) {
                    ([datetime]::Parse($job.endTimeUtc) - [datetime]::Parse($job.startTimeUtc))
                } else { $null }
                FailureReason = $job.failureReason
            }
        }
    }
}

Write-Host "  Found $($allRuns.Count) run(s) across all pipelines" -ForegroundColor Green

# Step 3: Analyze performance
Write-Host "[3/4] Analyzing performance metrics..." -ForegroundColor Yellow

$report = @()

$groupedByPipeline = $allRuns | Group-Object PipelineName

foreach ($group in $groupedByPipeline) {
    $runs = $group.Group
    $successful = $runs | Where-Object { $_.Status -eq "Completed" }
    $failed = $runs | Where-Object { $_.Status -eq "Failed" }
    $durations = $successful | Where-Object { $null -ne $_.Duration } | ForEach-Object { $_.Duration.TotalSeconds }

    $stats = [PSCustomObject]@{
        Pipeline       = $group.Name
        TotalRuns      = $runs.Count
        Succeeded      = $successful.Count
        Failed         = $failed.Count
        FailureRate    = if ($runs.Count -gt 0) { [math]::Round(100.0 * $failed.Count / $runs.Count, 2) } else { 0 }
        AvgDuration    = if ($durations.Count -gt 0) { Format-Duration ([TimeSpan]::FromSeconds(($durations | Measure-Object -Average).Average)) } else { "N/A" }
        MaxDuration    = if ($durations.Count -gt 0) { Format-Duration ([TimeSpan]::FromSeconds(($durations | Measure-Object -Maximum).Maximum)) } else { "N/A" }
        MinDuration    = if ($durations.Count -gt 0) { Format-Duration ([TimeSpan]::FromSeconds(($durations | Measure-Object -Minimum).Minimum)) } else { "N/A" }
        LastRunStatus  = ($runs | Sort-Object StartTime -Descending | Select-Object -First 1).Status
        LastRunTime    = ($runs | Sort-Object StartTime -Descending | Select-Object -First 1).StartTime
    }

    $report += $stats
}

# Step 4: Generate report
Write-Host "[4/4] Generating diagnostic report..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path $OutputPath "FabricPipelineDiag_$timestamp.txt"

$reportContent = @"
============================================================
 FABRIC DATA FACTORY PIPELINE DIAGNOSTIC REPORT
============================================================
 Generated : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
 Workspace : $WorkspaceId
 Pipeline  : $($PipelineName ?? 'All')
 Lookback  : $LookbackHours hours
 Total Runs: $($allRuns.Count)
============================================================

PIPELINE PERFORMANCE SUMMARY
------------------------------------------------------------
"@

foreach ($stat in $report) {
    $reportContent += @"

Pipeline      : $($stat.Pipeline)
  Total Runs  : $($stat.TotalRuns)
  Succeeded   : $($stat.Succeeded)
  Failed      : $($stat.Failed)
  Failure Rate: $($stat.FailureRate)%
  Avg Duration: $($stat.AvgDuration)
  Max Duration: $($stat.MaxDuration)
  Min Duration: $($stat.MinDuration)
  Last Status : $($stat.LastRunStatus)
  Last Run    : $($stat.LastRunTime)
"@
}

$reportContent += @"

============================================================
FAILED RUNS DETAIL
------------------------------------------------------------
"@

$failedRuns = $allRuns | Where-Object { $_.Status -eq "Failed" } | Sort-Object StartTime -Descending | Select-Object -First 10

if ($failedRuns.Count -eq 0) {
    $reportContent += "`nNo failed runs in the lookback period.`n"
}
else {
    foreach ($run in $failedRuns) {
        $reportContent += @"

Pipeline : $($run.PipelineName)
Job ID   : $($run.JobId)
Start    : $($run.StartTime)
End      : $($run.EndTime)
Duration : $(if ($run.Duration) { Format-Duration $run.Duration } else { 'N/A' })
Reason   : $($run.FailureReason ?? 'Not specified')
"@
    }
}

$reportContent += @"

============================================================
RECOMMENDATIONS
------------------------------------------------------------
"@

# Generate recommendations based on analysis
$recommendations = @()

foreach ($stat in $report) {
    if ($stat.FailureRate -gt 20) {
        $recommendations += "HIGH: Pipeline '$($stat.Pipeline)' has a $($stat.FailureRate)% failure rate. Review error details and fix recurring issues."
    }
    if ($stat.FailureRate -gt 5 -and $stat.FailureRate -le 20) {
        $recommendations += "MEDIUM: Pipeline '$($stat.Pipeline)' has a $($stat.FailureRate)% failure rate. Add retry logic and error handling."
    }
}

if ($allRuns.Count -eq 0) {
    $recommendations += "INFO: No pipeline runs found in the lookback period. Verify the pipeline is scheduled or check a longer timeframe."
}

if ($recommendations.Count -eq 0) {
    $reportContent += "`nAll pipelines appear healthy based on available data.`n"
}
else {
    foreach ($rec in $recommendations) {
        $reportContent += "`n- $rec"
    }
    $reportContent += "`n"
}

$reportContent += @"

============================================================
NEXT STEPS
------------------------------------------------------------
1. For copy activity tuning, review: references/copy-activity-tuning.md
2. For stuck activities, review: references/pipeline-stuck-resolution.md
3. For throttling issues, review: references/capacity-throttling-guide.md
4. Enable workspace monitoring for long-term trend analysis
5. Use the Monitoring Hub duration breakdown for activity-level details
============================================================
"@

# Output report
$reportContent | Out-File -FilePath $reportFile -Encoding utf8

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Diagnostic Report Generated Successfully" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "  File: $reportFile" -ForegroundColor White
Write-Host ""

# Also display summary to console
Write-Host "PIPELINE SUMMARY:" -ForegroundColor Cyan
$report | Format-Table Pipeline, TotalRuns, Succeeded, Failed, FailureRate, AvgDuration, MaxDuration -AutoSize

if ($failedRuns.Count -gt 0) {
    Write-Host "RECENT FAILURES:" -ForegroundColor Red
    $failedRuns | Format-Table PipelineName, StartTime, @{N='Duration';E={if ($_.Duration) { Format-Duration $_.Duration } else { 'N/A' }}}, FailureReason -AutoSize
}

#endregion
