<#
.SYNOPSIS
    Generates a health report for all Dataflow Gen2 items in a Microsoft Fabric workspace.

.DESCRIPTION
    Audits dataflow configurations and recent refresh performance across a workspace.
    Checks for Fast Copy enablement, staging configuration, recent failures, and
    duration trends. Outputs a summary report to the console and optionally to a CSV file.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace to audit.

.PARAMETER OutputPath
    Optional. Path to save the CSV report. If not specified, outputs to console only.

.PARAMETER IncludeDefinitions
    Optional. If set, retrieves and analyzes dataflow definitions for Fast Copy and
    staging configuration. This makes additional API calls per dataflow.

.PARAMETER MaxRefreshHistory
    Optional. Maximum number of recent refresh instances to analyze per dataflow. Default: 10.

.EXAMPLE
    .\Get-DataflowHealthReport.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    .\Get-DataflowHealthReport.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -OutputPath "./report.csv" -IncludeDefinitions

.NOTES
    Requires: PowerShell 7+, Az.Accounts module
    Authentication: Run Connect-AzAccount before executing this script.
    Permissions: Requires Contributor or higher on the target workspace.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [switch]$IncludeDefinitions,

    [Parameter(Mandatory = $false)]
    [int]$MaxRefreshHistory = 10
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

# --- API Helper ---
function Invoke-FabricApi {
    param(
        [string]$Uri,
        [string]$Method = "Get",
        [hashtable]$Headers
    )
    try {
        $response = Invoke-RestMethod -Uri $Uri -Headers $Headers -Method $Method -ErrorAction Stop
        return $response
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Warning "API call failed [$statusCode]: $Uri - $($_.Exception.Message)"
        return $null
    }
}

# --- Main Logic ---
Write-Host "`n=== Dataflow Gen2 Health Report ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId"
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)`n"

$headers = Get-FabricHeaders

# Get all items in workspace and filter for Dataflows
Write-Host "Retrieving workspace items..." -ForegroundColor Yellow
$items = Invoke-FabricApi -Uri "$baseUri/workspaces/$WorkspaceId/items" -Headers $headers
if (-not $items) {
    Write-Error "Failed to retrieve workspace items."
    exit 1
}

$dataflows = $items.value | Where-Object { $_.type -eq "Dataflow" }
if ($dataflows.Count -eq 0) {
    Write-Host "No Dataflow Gen2 items found in workspace." -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($dataflows.Count) dataflow(s). Analyzing...`n" -ForegroundColor Green

$report = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($df in $dataflows) {
    Write-Host "  Analyzing: $($df.displayName)" -ForegroundColor White

    $entry = [ordered]@{
        DataflowName      = $df.displayName
        DataflowId        = $df.id
        FastCopyEnabled   = "N/A"
        MaxConcurrency    = "N/A"
        AllowNativeQuery  = "N/A"
        QueryCount        = "N/A"
        LastRefreshStatus = "N/A"
        LastRefreshDuration = "N/A"
        AvgDurationMin    = "N/A"
        FailureCount      = 0
        TotalRefreshes    = 0
    }

    # --- Definition Analysis ---
    if ($IncludeDefinitions) {
        $defUri = "$baseUri/workspaces/$WorkspaceId/dataflows/$($df.id)/getDefinition"
        $def = Invoke-FabricApi -Uri $defUri -Method Post -Headers $headers
        if ($def -and $def.definition.parts) {
            $metaPart = $def.definition.parts | Where-Object { $_.path -eq "queryMetadata.json" }
            if ($metaPart -and $metaPart.payload) {
                try {
                    $metaJson = [System.Text.Encoding]::UTF8.GetString(
                        [Convert]::FromBase64String($metaPart.payload)
                    )
                    $metadata = $metaJson | ConvertFrom-Json

                    $entry.FastCopyEnabled  = if ($null -ne $metadata.computeEngineSettings.allowFastCopy) {
                        $metadata.computeEngineSettings.allowFastCopy
                    } else { "Default (true)" }

                    $entry.MaxConcurrency   = if ($null -ne $metadata.computeEngineSettings.maxConcurrency) {
                        $metadata.computeEngineSettings.maxConcurrency
                    } else { "Default" }

                    $entry.AllowNativeQuery = if ($null -ne $metadata.allowNativeQueries) {
                        $metadata.allowNativeQueries
                    } else { "Default (true)" }

                    # Count queries
                    $queryNames = $metadata.queriesMetadata.PSObject.Properties.Name
                    $entry.QueryCount = $queryNames.Count
                }
                catch {
                    Write-Warning "    Could not parse definition for $($df.displayName): $_"
                }
            }
        }
    }

    # --- Refresh History ---
    $jobsUri = "$baseUri/workspaces/$WorkspaceId/items/$($df.id)/jobs/instances"
    $jobs = Invoke-FabricApi -Uri $jobsUri -Headers $headers
    if ($jobs -and $jobs.value) {
        $recentJobs = $jobs.value | Sort-Object startTimeUtc -Descending | Select-Object -First $MaxRefreshHistory
        $entry.TotalRefreshes = $recentJobs.Count

        # Latest refresh
        $latest = $recentJobs | Select-Object -First 1
        $entry.LastRefreshStatus = $latest.status

        if ($latest.endTimeUtc -and $latest.startTimeUtc) {
            $duration = ([datetime]$latest.endTimeUtc - [datetime]$latest.startTimeUtc).TotalMinutes
            $entry.LastRefreshDuration = "$([math]::Round($duration, 2)) min"
        }

        # Failure count
        $entry.FailureCount = ($recentJobs | Where-Object { $_.status -eq "Failed" }).Count

        # Average duration
        $completedJobs = $recentJobs | Where-Object {
            $_.status -eq "Completed" -and $_.endTimeUtc -and $_.startTimeUtc
        }
        if ($completedJobs.Count -gt 0) {
            $avgMin = ($completedJobs | ForEach-Object {
                ([datetime]$_.endTimeUtc - [datetime]$_.startTimeUtc).TotalMinutes
            } | Measure-Object -Average).Average
            $entry.AvgDurationMin = "$([math]::Round($avgMin, 2)) min"
        }
    }

    $report.Add([PSCustomObject]$entry)
}

# --- Output ---
Write-Host "`n=== Health Report Summary ===" -ForegroundColor Cyan
$report | Format-Table -AutoSize -Wrap

# Highlight issues
$failures = $report | Where-Object { $_.FailureCount -gt 0 }
if ($failures.Count -gt 0) {
    Write-Host "`n⚠ Dataflows with Recent Failures:" -ForegroundColor Red
    $failures | Select-Object DataflowName, FailureCount, LastRefreshStatus | Format-Table -AutoSize
}

$noFastCopy = $report | Where-Object { $_.FastCopyEnabled -eq $false }
if ($noFastCopy.Count -gt 0) {
    Write-Host "`n⚠ Dataflows with Fast Copy Disabled:" -ForegroundColor Yellow
    $noFastCopy | Select-Object DataflowName, FastCopyEnabled | Format-Table -AutoSize
}

# Export CSV
if ($OutputPath) {
    $report | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    Write-Host "`nReport saved to: $OutputPath" -ForegroundColor Green
}

Write-Host "`nHealth check complete.`n" -ForegroundColor Cyan
