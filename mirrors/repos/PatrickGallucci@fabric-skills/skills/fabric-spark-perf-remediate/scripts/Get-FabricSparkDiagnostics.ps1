<#
.SYNOPSIS
    Collects Apache Spark application diagnostics from a Microsoft Fabric workspace.

.DESCRIPTION
    Queries the Fabric REST API to retrieve Spark application metrics, session details,
    and resource utilization data for performance remediate. Outputs a structured
    diagnostic report to the console and optionally exports to JSON.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace to query.

.PARAMETER Token
    Bearer token for Fabric REST API authentication.
    Obtain via: (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token

.PARAMETER ItemType
    Filter by item type: Notebook, SparkJobDefinition, Lakehouse, or All.
    Default: All

.PARAMETER HoursBack
    Number of hours to look back for Spark applications. Default: 24

.PARAMETER ExportPath
    Optional file path to export the diagnostic report as JSON.

.PARAMETER TopN
    Number of top resource-consuming applications to display. Default: 10

.EXAMPLE
    # Basic usage with token
    ./Get-FabricSparkDiagnostics.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -Token $token

.EXAMPLE
    # Export diagnostics for the last 48 hours
    ./Get-FabricSparkDiagnostics.ps1 -WorkspaceId $wsId -Token $token -HoursBack 48 -ExportPath "./spark-diag.json"

.EXAMPLE
    # Filter to notebook sessions only
    ./Get-FabricSparkDiagnostics.ps1 -WorkspaceId $wsId -Token $token -ItemType Notebook

.NOTES
    Requires: PowerShell 7+
    API Reference: https://learn.microsoft.com/en-us/fabric/data-engineering/spark-monitoring-api-overview
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Token,

    [ValidateSet('Notebook', 'SparkJobDefinition', 'Lakehouse', 'All')]
    [string]$ItemType = 'All',

    [ValidateRange(1, 720)]
    [int]$HoursBack = 24,

    [string]$ExportPath,

    [ValidateRange(1, 50)]
    [int]$TopN = 10
)

#region Helper Functions

function Invoke-FabricApi {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Uri,
        [Parameter(Mandatory)]
        [string]$Token,
        [string]$Method = 'GET'
    )

    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }

    try {
        $response = Invoke-RestMethod -Uri $Uri -Headers $headers -Method $Method -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 429) {
            Write-Warning "Rate limited (429). Waiting 30 seconds..."
            Start-Sleep -Seconds 30
            return Invoke-RestMethod -Uri $Uri -Headers $headers -Method $Method
        }
        elseif ($statusCode -eq 430) {
            Write-Warning "Capacity throttled (430). Spark compute resources are fully consumed."
            return $null
        }
        else {
            Write-Error "API call failed: $($_.Exception.Message) (HTTP $statusCode)"
            return $null
        }
    }
}

function Format-Duration {
    param([TimeSpan]$Duration)
    if ($Duration.TotalHours -ge 1) {
        return "{0:N1}h" -f $Duration.TotalHours
    }
    elseif ($Duration.TotalMinutes -ge 1) {
        return "{0:N1}m" -f $Duration.TotalMinutes
    }
    else {
        return "{0:N0}s" -f $Duration.TotalSeconds
    }
}

function Format-Bytes {
    param([long]$Bytes)
    if ($Bytes -ge 1TB) { return "{0:N2} TB" -f ($Bytes / 1TB) }
    elseif ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    elseif ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    elseif ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    else { return "$Bytes B" }
}

#endregion

#region Main Execution

$baseUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId"
$cutoffTime = (Get-Date).AddHours(-$HoursBack).ToUniversalTime()

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Fabric Spark Performance Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace : $WorkspaceId"
Write-Host "Time Range: Last $HoursBack hours (since $($cutoffTime.ToString('yyyy-MM-dd HH:mm UTC')))"
Write-Host "Item Type : $ItemType"
Write-Host ""

# Retrieve Spark sessions
Write-Host "Fetching Spark applications..." -ForegroundColor Yellow
$sessionsUri = "$baseUri/spark/livySessions"
$sessionsResponse = Invoke-FabricApi -Uri $sessionsUri -Token $Token

if (-not $sessionsResponse) {
    Write-Error "Failed to retrieve Spark sessions. Verify workspace ID and token."
    exit 1
}

$sessions = @($sessionsResponse.value)
Write-Host "  Found $($sessions.Count) total Spark application(s)." -ForegroundColor Green

# Filter by time range
$recentSessions = $sessions | Where-Object {
    $startTime = if ($_.startedAt) { [DateTime]::Parse($_.startedAt) } else { $null }
    $startTime -and $startTime -ge $cutoffTime
}

# Filter by item type
if ($ItemType -ne 'All') {
    $recentSessions = $recentSessions | Where-Object { $_.itemType -eq $ItemType }
}

Write-Host "  $($recentSessions.Count) application(s) match filters.`n" -ForegroundColor Green

if ($recentSessions.Count -eq 0) {
    Write-Host "No Spark applications found for the specified criteria." -ForegroundColor Yellow
    exit 0
}

# Categorize sessions
$statusGroups = $recentSessions | Group-Object -Property state

Write-Host "--- Session Status Summary ---" -ForegroundColor Cyan
foreach ($group in $statusGroups) {
    $color = switch ($group.Name) {
        'running'   { 'Yellow' }
        'success'   { 'Green' }
        'dead'      { 'Red' }
        'killed'    { 'Red' }
        default     { 'Gray' }
    }
    Write-Host "  $($group.Name): $($group.Count)" -ForegroundColor $color
}
Write-Host ""

# Analyze duration distribution
$completedSessions = $recentSessions | Where-Object {
    $_.state -in @('success', 'dead', 'killed') -and $_.startedAt -and $_.endedAt
}

if ($completedSessions.Count -gt 0) {
    Write-Host "--- Duration Analysis (Completed Jobs) ---" -ForegroundColor Cyan

    $durations = $completedSessions | ForEach-Object {
        $start = [DateTime]::Parse($_.startedAt)
        $end = [DateTime]::Parse($_.endedAt)
        ($end - $start)
    }

    $sortedDurations = $durations | Sort-Object TotalSeconds
    $avgDuration = [TimeSpan]::FromSeconds(($durations | Measure-Object -Property TotalSeconds -Average).Average)
    $medianDuration = $sortedDurations[[int]($sortedDurations.Count / 2)]
    $p90Duration = $sortedDurations[[int]($sortedDurations.Count * 0.9)]
    $maxDuration = $sortedDurations[-1]

    Write-Host "  Average : $(Format-Duration $avgDuration)"
    Write-Host "  Median  : $(Format-Duration $medianDuration)"
    Write-Host "  P90     : $(Format-Duration $p90Duration)"
    Write-Host "  Max     : $(Format-Duration $maxDuration)"
    Write-Host ""
}

# Top N longest-running applications
Write-Host "--- Top $TopN Longest-Running Applications ---" -ForegroundColor Cyan

$topSessions = $recentSessions | ForEach-Object {
    $start = if ($_.startedAt) { [DateTime]::Parse($_.startedAt) } else { $null }
    $end = if ($_.endedAt) { [DateTime]::Parse($_.endedAt) } elseif ($_.state -eq 'running') { Get-Date } else { $null }
    $duration = if ($start -and $end) { $end - $start } else { [TimeSpan]::Zero }

    [PSCustomObject]@{
        SessionId  = $_.id
        ItemName   = $_.itemName
        ItemType   = $_.itemType
        State      = $_.state
        Duration   = $duration
        DurationStr = Format-Duration $duration
        StartedAt  = $start
        Executors  = $_.executorCount
    }
} | Sort-Object { $_.Duration.TotalSeconds } -Descending | Select-Object -First $TopN

$topSessions | Format-Table -Property ItemName, ItemType, State, DurationStr, Executors, StartedAt -AutoSize
Write-Host ""

# Check for currently running sessions (potential idle consumers)
$runningSessions = $recentSessions | Where-Object { $_.state -eq 'running' }
if ($runningSessions.Count -gt 0) {
    Write-Host "--- Active Sessions (Consuming VCores) ---" -ForegroundColor Yellow
    Write-Host "  $($runningSessions.Count) session(s) currently running." -ForegroundColor Yellow
    Write-Host "  Review for idle sessions that can be cancelled to free capacity." -ForegroundColor Yellow

    foreach ($session in $runningSessions) {
        $start = [DateTime]::Parse($session.startedAt)
        $runTime = (Get-Date) - $start
        $idle = if ($runTime.TotalHours -gt 2) { " [POTENTIALLY IDLE]" } else { "" }
        Write-Host "    - $($session.itemName) | Running $(Format-Duration $runTime)$idle" -ForegroundColor $(if ($idle) { 'Red' } else { 'Yellow' })
    }
    Write-Host ""
}

# Build diagnostic report object
$report = [PSCustomObject]@{
    GeneratedAt     = (Get-Date).ToUniversalTime().ToString('o')
    WorkspaceId     = $WorkspaceId
    TimeRangeHours  = $HoursBack
    TotalSessions   = $recentSessions.Count
    StatusSummary   = $statusGroups | ForEach-Object {
        @{ State = $_.Name; Count = $_.Count }
    }
    DurationStats   = if ($completedSessions.Count -gt 0) {
        @{
            AverageSeconds = [Math]::Round($avgDuration.TotalSeconds, 1)
            MedianSeconds  = [Math]::Round($medianDuration.TotalSeconds, 1)
            P90Seconds     = [Math]::Round($p90Duration.TotalSeconds, 1)
            MaxSeconds     = [Math]::Round($maxDuration.TotalSeconds, 1)
        }
    } else { $null }
    TopApplications = $topSessions | ForEach-Object {
        @{
            SessionId = $_.SessionId
            ItemName  = $_.ItemName
            ItemType  = $_.ItemType
            State     = $_.State
            DurationSeconds = [Math]::Round($_.Duration.TotalSeconds, 1)
            Executors = $_.Executors
        }
    }
    ActiveSessions  = $runningSessions.Count
    Recommendations = @()
}

# Generate recommendations
if ($runningSessions.Count -gt 3) {
    $report.Recommendations += "HIGH: $($runningSessions.Count) active sessions detected. Review for idle sessions consuming VCores."
}

if ($completedSessions.Count -gt 0 -and $p90Duration.TotalMinutes -gt 60) {
    $report.Recommendations += "MEDIUM: P90 duration exceeds 60 minutes. Review longest-running jobs for optimization opportunities."
}

$failedSessions = $recentSessions | Where-Object { $_.state -in @('dead', 'killed') }
if ($failedSessions.Count -gt 0) {
    $failRate = [Math]::Round(($failedSessions.Count / $recentSessions.Count) * 100, 1)
    if ($failRate -gt 10) {
        $report.Recommendations += "HIGH: $failRate% failure rate detected. Check driver/executor logs for root cause."
    }
}

if ($report.Recommendations.Count -eq 0) {
    $report.Recommendations += "No critical issues detected in the analyzed time window."
}

# Output recommendations
Write-Host "--- Recommendations ---" -ForegroundColor Cyan
foreach ($rec in $report.Recommendations) {
    $color = if ($rec.StartsWith("HIGH")) { 'Red' } elseif ($rec.StartsWith("MEDIUM")) { 'Yellow' } else { 'Green' }
    Write-Host "  $rec" -ForegroundColor $color
}
Write-Host ""

# Export if requested
if ($ExportPath) {
    $report | ConvertTo-Json -Depth 5 | Set-Content -Path $ExportPath -Encoding UTF8
    Write-Host "Diagnostic report exported to: $ExportPath" -ForegroundColor Green
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Diagnostics complete." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

#endregion
