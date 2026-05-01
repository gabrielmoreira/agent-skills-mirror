<#
.SYNOPSIS
    Generates a consolidated Fabric performance monitoring report.

.DESCRIPTION
    Orchestrates capacity health, Spark concurrency, and job history checks into
    a single HTML or Markdown performance report. Combines REST API data with
    contextual recommendations for capacity optimization.

.PARAMETER SubscriptionId
    Azure subscription ID for capacity ARM queries.

.PARAMETER ResourceGroupName
    Resource group containing the Fabric capacity.

.PARAMETER CapacityName
    Fabric capacity name.

.PARAMETER WorkspaceId
    Fabric workspace ID for workload analysis.

.PARAMETER OutputFormat
    Report format: 'HTML' or 'Markdown'. Default: HTML.

.PARAMETER OutputPath
    File path for the generated report. Default: ./FabricPerformanceReport_<timestamp>.<ext>

.EXAMPLE
    ./New-FabricPerformanceReport.ps1 -SubscriptionId "xxx" -ResourceGroupName "rg" -CapacityName "cap" -WorkspaceId "xxx"

.NOTES
    Requires: Az.Accounts, Az.Fabric modules
    Combines data from ARM and Fabric REST APIs
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SubscriptionId,

    [Parameter(Mandatory)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory)]
    [string]$CapacityName,

    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter()]
    [ValidateSet('HTML', 'Markdown')]
    [string]$OutputFormat = 'HTML',

    [Parameter()]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ext = if ($OutputFormat -eq 'HTML') { 'html' } else { 'md' }
if (-not $OutputPath) {
    $OutputPath = "./FabricPerformanceReport_$timestamp.$ext"
}

#region Authentication
try {
    $armToken = (Get-AzAccessToken -ResourceUrl 'https://management.azure.com').Token
    $fabricToken = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
}
catch {
    Write-Error "Authentication failed. Ensure you are logged in with Connect-AzAccount. Error: $_"
    exit 1
}

$armHeaders = @{ 'Authorization' = "Bearer $armToken"; 'Content-Type' = 'application/json' }
$fabricHeaders = @{ 'Authorization' = "Bearer $fabricToken"; 'Content-Type' = 'application/json' }
#endregion

#region Collect Data
Write-Host "Collecting capacity data..." -ForegroundColor Cyan

# Capacity info
$capUri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Fabric/capacities/$($CapacityName)?api-version=2023-11-01"
$capacity = Invoke-RestMethod -Method Get -Uri $capUri -Headers $armHeaders

$sku = $capacity.sku.name
$skuNumber = [int]($sku -replace '[^0-9]', '')
$sparkVCores = $skuNumber * 2
$state = $capacity.properties.state

Write-Host "Collecting workspace data..." -ForegroundColor Cyan

# Workspace info
$wsUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId"
$workspace = Invoke-RestMethod -Method Get -Uri $wsUri -Headers $fabricHeaders

# Items
$itemsUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
$items = (Invoke-RestMethod -Method Get -Uri $itemsUri -Headers $fabricHeaders).value

$sparkItems = $items | Where-Object { $_.type -in @('Notebook', 'SparkJobDefinition', 'Lakehouse', 'Environment') }
$itemCounts = $sparkItems | Group-Object -Property type -AsHashTable -AsString

Write-Host "Data collection complete." -ForegroundColor Green
#endregion

#region Build Report
$reportDate = Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC'

if ($OutputFormat -eq 'Markdown') {
    $report = @"
# Microsoft Fabric Performance Report

**Generated:** $reportDate
**Capacity:** $CapacityName
**Workspace:** $($workspace.displayName)

---

## Capacity Overview

| Property | Value |
|----------|-------|
| SKU | $sku |
| State | $state |
| Spark VCores | $sparkVCores |
| Queue Limit | $skuNumber |
| Location | $($capacity.location) |
| Provisioning State | $($capacity.properties.provisioningState) |

## Workspace Inventory

| Item Type | Count |
|-----------|-------|
| Notebooks | $($itemCounts['Notebook'].Count) |
| Spark Job Definitions | $($itemCounts['SparkJobDefinition'].Count) |
| Lakehouses | $($itemCounts['Lakehouse'].Count) |
| Environments | $($itemCounts['Environment'].Count) |
| Total Items | $($items.Count) |

## Risk Assessment

$(if ($sparkItems.Count -gt ($skuNumber * 0.7)) {
"- **HIGH RISK**: Spark item count ($($sparkItems.Count)) is approaching queue limit ($skuNumber). Consider scaling capacity or consolidating workloads."
} elseif ($sparkItems.Count -gt ($skuNumber * 0.5)) {
"- **MODERATE RISK**: Spark item count ($($sparkItems.Count)) is at 50%+ of queue limit ($skuNumber). Monitor utilization closely."
} else {
"- **LOW RISK**: Spark item count ($($sparkItems.Count)) is well within queue limit ($skuNumber)."
})

## Recommendations

1. Install and review the **Fabric Capacity Metrics App** for historical CU trends
2. Use the **Monitoring Hub** to identify and terminate idle Spark sessions
3. Review Spark resource profiles -- ensure writeHeavy vs readHeavy aligns with workload patterns
4. Consider **Autoscale Billing for Spark** for bursty or unpredictable workloads
5. Schedule batch Spark jobs during off-peak hours to reduce concurrency pressure

## Next Steps

- Run ``Get-FabricJobHistory.ps1`` for detailed job execution analysis
- Run ``Get-FabricSparkConcurrency.ps1`` for real-time concurrency status
- Review Azure Cost Analysis for capacity spend optimization
"@
}
else {
    $report = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fabric Performance Report - $reportDate</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 40px; background: #f5f5f5; color: #333; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #0078d4; border-bottom: 3px solid #0078d4; padding-bottom: 10px; }
        h2 { color: #323130; margin-top: 30px; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th { background: #0078d4; color: white; padding: 10px 15px; text-align: left; }
        td { padding: 8px 15px; border-bottom: 1px solid #e1e1e1; }
        tr:hover { background: #f0f6ff; }
        .risk-high { color: #d13438; font-weight: bold; }
        .risk-moderate { color: #ca5010; font-weight: bold; }
        .risk-low { color: #107c10; font-weight: bold; }
        .recommendations li { margin: 8px 0; line-height: 1.6; }
        .meta { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
<div class="container">
    <h1>Microsoft Fabric Performance Report</h1>
    <p class="meta">Generated: $reportDate | Capacity: $CapacityName | Workspace: $($workspace.displayName)</p>

    <h2>Capacity Overview</h2>
    <table>
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>SKU</td><td>$sku</td></tr>
        <tr><td>State</td><td>$state</td></tr>
        <tr><td>Spark VCores</td><td>$sparkVCores</td></tr>
        <tr><td>Queue Limit</td><td>$skuNumber</td></tr>
        <tr><td>Location</td><td>$($capacity.location)</td></tr>
        <tr><td>Provisioning State</td><td>$($capacity.properties.provisioningState)</td></tr>
    </table>

    <h2>Workspace Inventory</h2>
    <table>
        <tr><th>Item Type</th><th>Count</th></tr>
        <tr><td>Notebooks</td><td>$($itemCounts['Notebook'].Count)</td></tr>
        <tr><td>Spark Job Definitions</td><td>$($itemCounts['SparkJobDefinition'].Count)</td></tr>
        <tr><td>Lakehouses</td><td>$($itemCounts['Lakehouse'].Count)</td></tr>
        <tr><td>Environments</td><td>$($itemCounts['Environment'].Count)</td></tr>
        <tr><td><strong>Total Items</strong></td><td><strong>$($items.Count)</strong></td></tr>
    </table>

    <h2>Risk Assessment</h2>
    $(if ($sparkItems.Count -gt ($skuNumber * 0.7)) {
        "<p class='risk-high'>HIGH RISK: Spark item count ($($sparkItems.Count)) is approaching queue limit ($skuNumber). Consider scaling capacity or consolidating workloads.</p>"
    } elseif ($sparkItems.Count -gt ($skuNumber * 0.5)) {
        "<p class='risk-moderate'>MODERATE RISK: Spark item count ($($sparkItems.Count)) is at 50%+ of queue limit ($skuNumber). Monitor utilization closely.</p>"
    } else {
        "<p class='risk-low'>LOW RISK: Spark item count ($($sparkItems.Count)) is well within queue limit ($skuNumber).</p>"
    })

    <h2>Recommendations</h2>
    <ol class="recommendations">
        <li>Install and review the <strong>Fabric Capacity Metrics App</strong> for historical CU trends</li>
        <li>Use the <strong>Monitoring Hub</strong> to identify and terminate idle Spark sessions</li>
        <li>Review Spark resource profiles -- ensure writeHeavy vs readHeavy aligns with workload patterns</li>
        <li>Consider <strong>Autoscale Billing for Spark</strong> for bursty or unpredictable workloads</li>
        <li>Schedule batch Spark jobs during off-peak hours to reduce concurrency pressure</li>
    </ol>
</div>
</body>
</html>
"@
}

$report | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Host "`nReport generated: $OutputPath" -ForegroundColor Green
#endregion
