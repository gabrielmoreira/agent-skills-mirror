<#
.SYNOPSIS
    Retrieves recent Fabric job execution history for audit and performance analysis.

.DESCRIPTION
    Queries the Fabric REST API to list recent item jobs (notebook runs, Spark job
    definitions, pipeline runs) within a workspace. Summarizes execution duration,
    status, and failure details for performance trending.

.PARAMETER WorkspaceId
    The Fabric workspace ID to audit.

.PARAMETER HoursBack
    Number of hours to look back for job history. Default: 24.

.PARAMETER ItemType
    Optional filter for item type (Notebook, SparkJobDefinition, Pipeline).

.PARAMETER ExportCsv
    Optional file path to export results as CSV.

.EXAMPLE
    ./Get-FabricJobHistory.ps1 -WorkspaceId "xxxxxxxx" -HoursBack 48

.EXAMPLE
    ./Get-FabricJobHistory.ps1 -WorkspaceId "xxxxxxxx" -ItemType "Notebook" -ExportCsv "./report.csv"

.NOTES
    Requires: Fabric API access token
    API Base: https://api.fabric.microsoft.com/v1
    Job statuses: NotStarted, InProgress, Completed, Failed, Cancelled
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter()]
    [int]$HoursBack = 24,

    [Parameter()]
    [ValidateSet('Notebook', 'SparkJobDefinition', 'Pipeline', 'Lakehouse')]
    [string]$ItemType,

    [Parameter()]
    [string]$ExportCsv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
}
catch {
    Write-Error "Failed to acquire Fabric API token. Error: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}
#endregion

#region Get Items and Jobs
$fabricApiBase = 'https://api.fabric.microsoft.com/v1'
$cutoffTime = (Get-Date).AddHours(-$HoursBack).ToUniversalTime()

Write-Host "`n=== Fabric Job History Audit ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId" -ForegroundColor Gray
Write-Host "Looking back: $HoursBack hours (since $($cutoffTime.ToString('yyyy-MM-ddTHH:mm:ssZ')))" -ForegroundColor Gray

# Get workspace items
try {
    $itemsResponse = Invoke-RestMethod -Method Get -Uri "$fabricApiBase/workspaces/$WorkspaceId/items" -Headers $headers
    $items = $itemsResponse.value
}
catch {
    Write-Error "Failed to list workspace items: $_"
    exit 1
}

# Filter by type if specified
if ($ItemType) {
    $items = $items | Where-Object { $_.type -eq $ItemType }
    Write-Host "Filtering by item type: $ItemType" -ForegroundColor Gray
}

# Only check job-capable items
$jobCapableTypes = @('Notebook', 'SparkJobDefinition', 'Pipeline', 'Lakehouse')
$items = $items | Where-Object { $_.type -in $jobCapableTypes }

Write-Host "Found $($items.Count) job-capable items to check.`n" -ForegroundColor Gray
#endregion

#region Collect Job Data
$allJobs = [System.Collections.Generic.List[PSObject]]::new()

foreach ($item in $items) {
    try {
        $jobsUri = "$fabricApiBase/workspaces/$WorkspaceId/items/$($item.id)/jobs/instances?limit=50"
        $jobsResponse = Invoke-RestMethod -Method Get -Uri $jobsUri -Headers $headers -ErrorAction SilentlyContinue

        if ($jobsResponse.value) {
            foreach ($job in $jobsResponse.value) {
                $startTime = if ($job.startTimeUtc) { [datetime]::Parse($job.startTimeUtc) } else { $null }
                $endTime = if ($job.endTimeUtc) { [datetime]::Parse($job.endTimeUtc) } else { $null }

                # Filter by time window
                if ($startTime -and $startTime -lt $cutoffTime) { continue }

                $duration = if ($startTime -and $endTime) {
                    ($endTime - $startTime).TotalMinutes
                } else { $null }

                $allJobs.Add([PSCustomObject]@{
                    ItemName   = $item.displayName
                    ItemType   = $item.type
                    JobId      = $job.id
                    Status     = $job.status
                    StartTime  = $startTime
                    EndTime    = $endTime
                    DurationMin = if ($duration) { [math]::Round($duration, 2) } else { 'Running' }
                    InvokeType = $job.invokeType
                    FailureReason = $job.failureReason.message
                })
            }
        }
    }
    catch {
        # Some items may not support jobs API - skip silently
        Write-Verbose "Skipping $($item.displayName) ($($item.type)): $_"
    }
}
#endregion

#region Format Output
if ($allJobs.Count -eq 0) {
    Write-Host "No jobs found in the specified time window." -ForegroundColor Yellow
    exit 0
}

# Summary statistics
$statusSummary = $allJobs | Group-Object -Property Status | ForEach-Object {
    [PSCustomObject]@{
        Status = $_.Name
        Count  = $_.Count
    }
}

Write-Host "--- Job Status Summary ---" -ForegroundColor Yellow
$statusSummary | Format-Table -AutoSize

# Failed jobs detail
$failedJobs = $allJobs | Where-Object { $_.Status -eq 'Failed' }
if ($failedJobs.Count -gt 0) {
    Write-Host "--- Failed Jobs ---" -ForegroundColor Red
    $failedJobs | Format-Table ItemName, ItemType, StartTime, DurationMin, FailureReason -AutoSize -Wrap
}

# Longest running jobs
$completedJobs = $allJobs | Where-Object { $_.Status -eq 'Completed' -and $_.DurationMin -ne 'Running' }
if ($completedJobs.Count -gt 0) {
    Write-Host "--- Top 10 Longest Running Jobs ---" -ForegroundColor Yellow
    $completedJobs | Sort-Object DurationMin -Descending | Select-Object -First 10 |
        Format-Table ItemName, ItemType, DurationMin, StartTime -AutoSize
}

# Full job list
Write-Host "--- All Jobs ($($allJobs.Count) total) ---" -ForegroundColor Yellow
$allJobs | Sort-Object StartTime -Descending |
    Format-Table ItemName, ItemType, Status, DurationMin, StartTime, InvokeType -AutoSize
#endregion

#region Export
if ($ExportCsv) {
    $allJobs | Export-Csv -Path $ExportCsv -NoTypeInformation -Encoding UTF8
    Write-Host "Results exported to: $ExportCsv" -ForegroundColor Green
}
#endregion

Write-Host "`nJob history audit complete." -ForegroundColor Green
