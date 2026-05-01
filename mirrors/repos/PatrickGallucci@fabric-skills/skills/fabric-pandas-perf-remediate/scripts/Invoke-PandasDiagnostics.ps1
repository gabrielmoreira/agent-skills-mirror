<#
.SYNOPSIS
    Diagnoses pandas-related performance issues in Microsoft Fabric Spark notebooks.

.DESCRIPTION
    Collects Spark session configuration, capacity utilization, environment settings,
    and memory-related metrics to help troubleshoot pandas performance problems in
    Microsoft Fabric notebooks. Outputs a structured diagnostic report.

.PARAMETER WorkspaceId
    The Fabric workspace ID containing the notebooks to diagnose.

.PARAMETER CapacityId
    Optional. The Fabric capacity ID to check utilization metrics.

.PARAMETER OutputPath
    Path for the diagnostic report. Defaults to current directory.

.EXAMPLE
    ./Invoke-PandasDiagnostics.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    ./Invoke-PandasDiagnostics.ps1 -WorkspaceId $wsId -CapacityId $capId -OutputPath "./reports"

.NOTES
    Requires: Az.Accounts module, Fabric REST API access
    License: Apache 2.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$')]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $false)]
    [ValidatePattern('^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$')]
    [string]$CapacityId,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Authentication
function Get-FabricAccessToken {
    <#
    .SYNOPSIS
        Retrieves a Fabric API access token using Az.Accounts.
    #>
    try {
        $token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com" -AsSecureString)
        $plainToken = [System.Net.NetworkCredential]::new("", $token.Token).Password
        return $plainToken
    }
    catch {
        Write-Error "Failed to get access token. Run Connect-AzAccount first. Error: $_"
        throw
    }
}

function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Makes an authenticated REST call to the Fabric API.
    #>
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [string]$Token
    )
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type"  = "application/json"
    }
    $uri = "https://api.fabric.microsoft.com/v1$Endpoint"
    try {
        $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers
        return $response
    }
    catch {
        Write-Warning "API call failed for $uri : $_"
        return $null
    }
}
#endregion

#region Data Collection
function Get-WorkspaceEnvironments {
    param([string]$WorkspaceId, [string]$Token)
    Write-Host "  Collecting environment configurations..." -ForegroundColor Cyan
    $items = Invoke-FabricApi -Endpoint "/workspaces/$WorkspaceId/environments" -Token $Token
    if ($null -eq $items) { return @() }
    return $items.value
}

function Get-WorkspaceNotebooks {
    param([string]$WorkspaceId, [string]$Token)
    Write-Host "  Collecting notebook inventory..." -ForegroundColor Cyan
    $items = Invoke-FabricApi -Endpoint "/workspaces/$WorkspaceId/notebooks" -Token $Token
    if ($null -eq $items) { return @() }
    return $items.value
}

function Get-SparkPools {
    param([string]$WorkspaceId, [string]$Token)
    Write-Host "  Collecting Spark pool configurations..." -ForegroundColor Cyan
    $items = Invoke-FabricApi -Endpoint "/workspaces/$WorkspaceId/spark/pools" -Token $Token
    if ($null -eq $items) { return @() }
    return $items.value
}

function Get-WorkspaceCapacity {
    param([string]$WorkspaceId, [string]$Token)
    Write-Host "  Checking workspace capacity assignment..." -ForegroundColor Cyan
    $workspace = Invoke-FabricApi -Endpoint "/workspaces/$WorkspaceId" -Token $Token
    if ($null -eq $workspace) { return $null }
    return $workspace
}
#endregion

#region Analysis
function Test-PandasOptimalConfig {
    <#
    .SYNOPSIS
        Analyzes collected configurations against pandas performance best practices.
    #>
    param(
        [object[]]$Environments,
        [object]$Workspace
    )

    $findings = [System.Collections.ArrayList]::new()

    # Check 1: Resource Profile
    foreach ($env in $Environments) {
        $sparkProps = $env.properties.computeConfiguration.sparkProperties
        if ($null -ne $sparkProps) {
            $profile = $sparkProps.'spark.fabric.resourceProfile'
            if ($profile -eq 'writeHeavy') {
                [void]$findings.Add(@{
                    Severity = "WARNING"
                    Category = "Resource Profile"
                    Finding  = "Environment '$($env.displayName)' uses writeHeavy profile"
                    Impact   = "Not optimized for notebook read operations and pandas conversions"
                    Fix      = "Switch to readHeavyForSpark for pandas-heavy notebooks"
                })
            }

            # Check 2: Arrow transfer
            $arrowEnabled = $sparkProps.'spark.sql.execution.arrow.pyspark.enabled'
            if ($arrowEnabled -ne 'true') {
                [void]$findings.Add(@{
                    Severity = "CRITICAL"
                    Category = "Arrow Transfer"
                    Finding  = "Arrow not enabled in environment '$($env.displayName)'"
                    Impact   = "toPandas() and createDataFrame() run 3-100x slower without Arrow"
                    Fix      = "Set spark.sql.execution.arrow.pyspark.enabled = true"
                })
            }

            # Check 3: Autotune
            $autotuneEnabled = $sparkProps.'spark.ms.autotune.enabled'
            if ($autotuneEnabled -ne 'true') {
                [void]$findings.Add(@{
                    Severity = "INFO"
                    Category = "Autotune"
                    Finding  = "Autotune not enabled in environment '$($env.displayName)'"
                    Impact   = "Manual tuning required for shuffle partitions and join thresholds"
                    Fix      = "Set spark.ms.autotune.enabled = true (requires Runtime 1.1/1.2)"
                })
            }

            # Check 4: Driver maxResultSize
            $maxResultSize = $sparkProps.'spark.driver.maxResultSize'
            if ($null -eq $maxResultSize -or $maxResultSize -eq '1g') {
                [void]$findings.Add(@{
                    Severity = "WARNING"
                    Category = "Driver Config"
                    Finding  = "spark.driver.maxResultSize is at default 1g"
                    Impact   = "Large toPandas() calls may fail with result size limit errors"
                    Fix      = "Increase to 4g-8g for pandas-heavy workloads"
                })
            }
        }
    }

    return $findings
}
#endregion

#region Report Generation
function Export-DiagnosticReport {
    param(
        [object[]]$Environments,
        [object[]]$Notebooks,
        [object[]]$Findings,
        [object]$Workspace,
        [string]$OutputPath
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $reportFile = Join-Path $OutputPath "pandas-diagnostics-$timestamp.md"

    $report = [System.Text.StringBuilder]::new()
    [void]$report.AppendLine("# Fabric Pandas Performance Diagnostic Report")
    [void]$report.AppendLine("")
    [void]$report.AppendLine("**Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')")
    [void]$report.AppendLine("**Workspace**: $($Workspace.displayName) ($WorkspaceId)")
    if ($Workspace.capacityId) {
        [void]$report.AppendLine("**Capacity**: $($Workspace.capacityId)")
    }
    [void]$report.AppendLine("")

    # Findings Summary
    $critical = ($Findings | Where-Object { $_.Severity -eq "CRITICAL" }).Count
    $warnings = ($Findings | Where-Object { $_.Severity -eq "WARNING" }).Count
    $info = ($Findings | Where-Object { $_.Severity -eq "INFO" }).Count

    [void]$report.AppendLine("## Summary")
    [void]$report.AppendLine("")
    [void]$report.AppendLine("| Severity | Count |")
    [void]$report.AppendLine("|----------|-------|")
    [void]$report.AppendLine("| CRITICAL | $critical |")
    [void]$report.AppendLine("| WARNING  | $warnings |")
    [void]$report.AppendLine("| INFO     | $info |")
    [void]$report.AppendLine("")

    # Detailed Findings
    [void]$report.AppendLine("## Findings")
    [void]$report.AppendLine("")

    foreach ($finding in ($Findings | Sort-Object { switch ($_.Severity) { "CRITICAL" { 0 } "WARNING" { 1 } "INFO" { 2 } } })) {
        $icon = switch ($finding.Severity) {
            "CRITICAL" { "🔴" }
            "WARNING"  { "🟡" }
            "INFO"     { "🔵" }
        }
        [void]$report.AppendLine("### $icon [$($finding.Severity)] $($finding.Category)")
        [void]$report.AppendLine("")
        [void]$report.AppendLine("**Finding**: $($finding.Finding)")
        [void]$report.AppendLine("")
        [void]$report.AppendLine("**Impact**: $($finding.Impact)")
        [void]$report.AppendLine("")
        [void]$report.AppendLine("**Recommended Fix**: $($finding.Fix)")
        [void]$report.AppendLine("")
    }

    # Environment Details
    [void]$report.AppendLine("## Environment Configurations")
    [void]$report.AppendLine("")
    foreach ($env in $Environments) {
        [void]$report.AppendLine("### $($env.displayName)")
        [void]$report.AppendLine("")
        [void]$report.AppendLine("| Property | Value |")
        [void]$report.AppendLine("|----------|-------|")
        if ($env.properties.computeConfiguration) {
            $cc = $env.properties.computeConfiguration
            [void]$report.AppendLine("| Runtime Version | $($cc.runtimeVersion) |")
            [void]$report.AppendLine("| Driver Cores | $($cc.driverCores) |")
            [void]$report.AppendLine("| Driver Memory | $($cc.driverMemory) |")
            [void]$report.AppendLine("| Executor Cores | $($cc.executorCores) |")
            [void]$report.AppendLine("| Executor Memory | $($cc.executorMemory) |")
        }
        [void]$report.AppendLine("")
    }

    # Notebook Inventory
    [void]$report.AppendLine("## Notebooks ($($Notebooks.Count) total)")
    [void]$report.AppendLine("")
    [void]$report.AppendLine("| Name | ID |")
    [void]$report.AppendLine("|------|-----|")
    foreach ($nb in $Notebooks) {
        [void]$report.AppendLine("| $($nb.displayName) | $($nb.id) |")
    }
    [void]$report.AppendLine("")

    # Recommendations
    [void]$report.AppendLine("## Quick Optimization Steps")
    [void]$report.AppendLine("")
    [void]$report.AppendLine("1. Enable Arrow transfer in all environments")
    [void]$report.AppendLine("2. Switch pandas-heavy environments to readHeavyForSpark profile")
    [void]$report.AppendLine("3. Increase spark.driver.maxResultSize to 4g+")
    [void]$report.AppendLine("4. Add memory monitoring cells to notebooks (see template)")
    [void]$report.AppendLine("5. Review notebooks for toPandas() anti-patterns")
    [void]$report.AppendLine("6. Enable autotune for repetitive analytical queries")

    $report.ToString() | Out-File -FilePath $reportFile -Encoding utf8
    return $reportFile
}
#endregion

#region Main
Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Fabric Pandas Performance Diagnostics" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Authenticate
Write-Host "[1/5] Authenticating..." -ForegroundColor Yellow
$token = Get-FabricAccessToken

# Collect workspace info
Write-Host "[2/5] Collecting workspace metadata..." -ForegroundColor Yellow
$workspace = Get-WorkspaceCapacity -WorkspaceId $WorkspaceId -Token $token

# Collect configurations
Write-Host "[3/5] Collecting Spark configurations..." -ForegroundColor Yellow
$environments = Get-WorkspaceEnvironments -WorkspaceId $WorkspaceId -Token $token
$notebooks = Get-WorkspaceNotebooks -WorkspaceId $WorkspaceId -Token $token

# Analyze
Write-Host "[4/5] Analyzing configurations..." -ForegroundColor Yellow
$findings = Test-PandasOptimalConfig -Environments $environments -Workspace $workspace

# Report
Write-Host "[5/5] Generating diagnostic report..." -ForegroundColor Yellow
if (-not (Test-Path $OutputPath)) { New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null }
$reportFile = Export-DiagnosticReport `
    -Environments $environments `
    -Notebooks $notebooks `
    -Findings $findings `
    -Workspace $workspace `
    -OutputPath $OutputPath

Write-Host ""
Write-Host "Diagnostic report saved to: $reportFile" -ForegroundColor Green

$criticalCount = ($findings | Where-Object { $_.Severity -eq "CRITICAL" }).Count
if ($criticalCount -gt 0) {
    Write-Host ""
    Write-Host "⚠️  $criticalCount CRITICAL finding(s) detected — review report for immediate actions." -ForegroundColor Red
}

Write-Host ""
#endregion
