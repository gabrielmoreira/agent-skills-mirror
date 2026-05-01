<#
.SYNOPSIS
    Collects Power BI workspace and semantic model metadata for performance analysis.

.DESCRIPTION
    Connects to the Power BI REST API and gathers workspace items, semantic model metadata,
    refresh history, and capacity information to support performance remediate.

.PARAMETER WorkspaceId
    The GUID of the Power BI workspace to analyze.

.PARAMETER OutputPath
    Optional. Directory to save the analysis output. Defaults to current directory.

.PARAMETER IncludeRefreshHistory
    Optional. Include refresh history for each semantic model. Defaults to $true.

.EXAMPLE
    .\Invoke-PBIPerformanceAnalysis.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    .\Invoke-PBIPerformanceAnalysis.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" -OutputPath "C:\Reports"

.NOTES
    Requires: MicrosoftPowerBIMgmt PowerShell module
    Install:  Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Get-Location).Path,

    [Parameter(Mandatory = $false)]
    [bool]$IncludeRefreshHistory = $true
)

#Requires -Modules MicrosoftPowerBIMgmt

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Finding {
    param(
        [string]$Category,
        [string]$Severity,
        [string]$Message
    )
    $color = switch ($Severity) {
        'Critical' { 'Red' }
        'Warning'  { 'Yellow' }
        'Info'     { 'Green' }
        default    { 'White' }
    }
    Write-Host "  [$Severity] $Category - $Message" -ForegroundColor $color
    [PSCustomObject]@{
        Category = $Category
        Severity = $Severity
        Message  = $Message
    }
}

try {
    # Ensure authenticated
    Write-Step "Checking Power BI authentication..."
    try {
        $profile = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/me" -Method Get | ConvertFrom-Json
        Write-Host "  Authenticated as: $($profile.displayName)" -ForegroundColor Green
    }
    catch {
        Write-Host "  Not authenticated. Connecting..." -ForegroundColor Yellow
        Connect-PowerBIServiceAccount
    }

    $findings = [System.Collections.Generic.List[PSObject]]::new()
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

    # Get workspace details
    Write-Step "Retrieving workspace details..."
    $workspace = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId" -Method Get | ConvertFrom-Json
    Write-Host "  Workspace: $($workspace.name)" -ForegroundColor White
    Write-Host "  Capacity ID: $($workspace.capacityId)" -ForegroundColor White
    Write-Host "  Is on Dedicated Capacity: $($workspace.isOnDedicatedCapacity)" -ForegroundColor White

    if (-not $workspace.isOnDedicatedCapacity) {
        $findings.Add((Write-Finding -Category 'Capacity' -Severity 'Warning' -Message 'Workspace is on shared capacity. Performance monitoring is limited. Consider Premium/Fabric capacity.'))
    }

    # Get all datasets (semantic models) in workspace
    Write-Step "Retrieving semantic models..."
    $datasets = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets" -Method Get | ConvertFrom-Json
    Write-Host "  Found $($datasets.value.Count) semantic model(s)" -ForegroundColor White

    $modelAnalysis = foreach ($ds in $datasets.value) {
        Write-Host "`n  Analyzing: $($ds.name)" -ForegroundColor White

        # Basic metadata
        $modelInfo = [ordered]@{
            Name                = $ds.name
            Id                  = $ds.id
            ConfiguredBy        = $ds.configuredBy
            IsRefreshable       = $ds.isRefreshable
            IsOnPremGateway     = $ds.IsOnPremGatewayRequired
            TargetStorageMode   = $ds.targetStorageMode
            CreatedDate         = $ds.createdDate
            ContentProviderType = $ds.ContentProviderType
        }

        # Check storage mode
        if ($ds.targetStorageMode -eq 'PremiumFiles') {
            Write-Host "    Storage: Large model format (Premium Files)" -ForegroundColor White
        }

        # Check for gateway dependency
        if ($ds.IsOnPremGatewayRequired) {
            $findings.Add((Write-Finding -Category 'Gateway' -Severity 'Info' -Message "Model '$($ds.name)' requires on-premises gateway. Check gateway performance."))
        }

        # Refresh history
        if ($IncludeRefreshHistory -and $ds.isRefreshable) {
            Write-Host "    Retrieving refresh history..." -ForegroundColor Gray
            try {
                $refreshes = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/datasets/$($ds.id)/refreshes?`$top=10" -Method Get | ConvertFrom-Json

                $recentRefreshes = $refreshes.value | Select-Object -First 5
                foreach ($refresh in $recentRefreshes) {
                    if ($refresh.status -eq 'Failed') {
                        $findings.Add((Write-Finding -Category 'Refresh' -Severity 'Critical' -Message "Model '$($ds.name)' refresh failed on $($refresh.endTime): $($refresh.serviceExceptionJson)"))
                    }

                    if ($refresh.startTime -and $refresh.endTime) {
                        $duration = [DateTime]$refresh.endTime - [DateTime]$refresh.startTime
                        if ($duration.TotalMinutes -gt 30) {
                            $findings.Add((Write-Finding -Category 'Refresh' -Severity 'Warning' -Message "Model '$($ds.name)' refresh took $([math]::Round($duration.TotalMinutes, 1)) minutes on $($refresh.startTime)"))
                        }
                    }
                }

                $modelInfo['LastRefreshStatus'] = $recentRefreshes[0].status
                $modelInfo['LastRefreshTime'] = $recentRefreshes[0].endTime
                if ($recentRefreshes[0].startTime -and $recentRefreshes[0].endTime) {
                    $lastDuration = [DateTime]$recentRefreshes[0].endTime - [DateTime]$recentRefreshes[0].startTime
                    $modelInfo['LastRefreshDurationMinutes'] = [math]::Round($lastDuration.TotalMinutes, 1)
                }
            }
            catch {
                Write-Host "    Could not retrieve refresh history: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }

        [PSCustomObject]$modelInfo
    }

    # Get reports
    Write-Step "Retrieving reports..."
    $reports = Invoke-PowerBIRestMethod -Url "https://api.powerbi.com/v1.0/myorg/groups/$WorkspaceId/reports" -Method Get | ConvertFrom-Json
    Write-Host "  Found $($reports.value.Count) report(s)" -ForegroundColor White

    # Summary output
    Write-Step "Generating analysis report..."

    $report = [ordered]@{
        AnalysisTimestamp = $timestamp
        Workspace         = [ordered]@{
            Name                   = $workspace.name
            Id                     = $WorkspaceId
            CapacityId             = $workspace.capacityId
            IsOnDedicatedCapacity  = $workspace.isOnDedicatedCapacity
        }
        SemanticModels    = $modelAnalysis
        ReportCount       = $reports.value.Count
        Findings          = $findings
    }

    # Save to JSON
    $outputFile = Join-Path $OutputPath "pbi-perf-analysis_$timestamp.json"
    $report | ConvertTo-Json -Depth 10 | Set-Content -Path $outputFile -Encoding UTF8
    Write-Host "`n  Report saved to: $outputFile" -ForegroundColor Green

    # Print summary
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " PERFORMANCE ANALYSIS SUMMARY" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Workspace:       $($workspace.name)"
    Write-Host "  Semantic Models:  $($datasets.value.Count)"
    Write-Host "  Reports:          $($reports.value.Count)"
    Write-Host "  Findings:"
    $criticalCount = ($findings | Where-Object Severity -eq 'Critical').Count
    $warningCount = ($findings | Where-Object Severity -eq 'Warning').Count
    $infoCount = ($findings | Where-Object Severity -eq 'Info').Count
    Write-Host "    Critical: $criticalCount" -ForegroundColor $(if ($criticalCount -gt 0) { 'Red' } else { 'Green' })
    Write-Host "    Warning:  $warningCount" -ForegroundColor $(if ($warningCount -gt 0) { 'Yellow' } else { 'Green' })
    Write-Host "    Info:     $infoCount" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
}
catch {
    Write-Error "Analysis failed: $($_.Exception.Message)"
    Write-Host "`nStack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
