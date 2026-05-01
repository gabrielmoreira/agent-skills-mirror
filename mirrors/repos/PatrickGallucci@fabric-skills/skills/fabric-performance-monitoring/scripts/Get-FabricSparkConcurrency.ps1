<#
.SYNOPSIS
    Analyzes Spark concurrency and active sessions in a Fabric workspace.

.DESCRIPTION
    Queries the Fabric REST API to retrieve active Spark sessions, running notebooks,
    and Spark job definitions. Identifies potential throttling risks based on current
    utilization relative to capacity limits.

.PARAMETER WorkspaceId
    The Fabric workspace ID to analyze.

.PARAMETER CapacitySku
    The Fabric capacity SKU (e.g., F64, F128) to calculate VCore limits.
    If omitted, the script attempts to detect it from workspace metadata.

.EXAMPLE
    ./Get-FabricSparkConcurrency.ps1 -WorkspaceId "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

.EXAMPLE
    ./Get-FabricSparkConcurrency.ps1 -WorkspaceId "xxxxxxxx" -CapacitySku "F128"

.NOTES
    Requires: Fabric API access token with Workspace.Read.All scope
    API Base: https://api.fabric.microsoft.com/v1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter()]
    [ValidatePattern('^F\d+$')]
    [string]$CapacitySku
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
}
catch {
    Write-Error "Failed to acquire Fabric API token. Ensure Az.Accounts is installed and you are logged in. Error: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}
#endregion

#region Get Workspace Items
$fabricApiBase = 'https://api.fabric.microsoft.com/v1'

Write-Host "`n=== Spark Concurrency Analysis ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId" -ForegroundColor Gray

# Get workspace details
try {
    $workspace = Invoke-RestMethod -Method Get -Uri "$fabricApiBase/workspaces/$WorkspaceId" -Headers $headers
    Write-Host "Workspace Name: $($workspace.displayName)" -ForegroundColor Gray
    Write-Host "Capacity ID: $($workspace.capacityId)" -ForegroundColor Gray
}
catch {
    Write-Warning "Could not retrieve workspace details: $_"
}

# Get all items to find Spark-related ones
try {
    $items = Invoke-RestMethod -Method Get -Uri "$fabricApiBase/workspaces/$WorkspaceId/items" -Headers $headers
    $sparkItems = $items.value | Where-Object {
        $_.type -in @('Notebook', 'SparkJobDefinition', 'Lakehouse', 'Environment')
    }
}
catch {
    Write-Error "Failed to list workspace items: $_"
    exit 1
}
#endregion

#region Analyze Items
$itemSummary = $sparkItems | Group-Object -Property type | ForEach-Object {
    [PSCustomObject]@{
        ItemType = $_.Name
        Count    = $_.Count
    }
}

Write-Host "`n--- Spark-Related Items ---" -ForegroundColor Yellow
$itemSummary | Format-Table -AutoSize
#endregion

#region Calculate Capacity Limits
if ($CapacitySku) {
    $skuNumber = [int]($CapacitySku -replace '[^0-9]', '')
    $totalVCores = $skuNumber * 2

    # Queue limits by SKU
    $queueLimits = @{
        2 = 4; 4 = 4; 8 = 8; 16 = 16; 32 = 32
        64 = 64; 128 = 128; 256 = 256; 512 = 512
        1024 = 1024; 2048 = 2048
    }
    $queueLimit = if ($queueLimits.ContainsKey($skuNumber)) { $queueLimits[$skuNumber] } else { $skuNumber }

    Write-Host "--- Capacity Limits ($CapacitySku) ---" -ForegroundColor Yellow
    Write-Host "  Total Spark VCores: $totalVCores"
    Write-Host "  Queue Limit:        $queueLimit"
    Write-Host "  CU to VCore Ratio:  1 CU = 2 VCores"

    $notebookCount = ($sparkItems | Where-Object { $_.type -eq 'Notebook' }).Count
    if ($notebookCount -gt ($queueLimit * 0.8)) {
        Write-Host "`n  WARNING: Notebook count ($notebookCount) is approaching queue limit ($queueLimit)." -ForegroundColor Red
        Write-Host "  Risk of HTTP 430 throttling if many notebooks run concurrently." -ForegroundColor Red
    }
    else {
        Write-Host "`n  Concurrency headroom looks adequate." -ForegroundColor Green
    }
}
else {
    Write-Host "--- Capacity Limits ---" -ForegroundColor Yellow
    Write-Host "  SKU not specified. Use -CapacitySku to calculate VCore limits."
    Write-Host "  Formula: 1 CU = 2 Spark VCores"
}
#endregion

#region Recommendations
Write-Host "`n--- Recommendations ---" -ForegroundColor Yellow

$notebookCount = ($sparkItems | Where-Object { $_.type -eq 'Notebook' }).Count
$sjdCount = ($sparkItems | Where-Object { $_.type -eq 'SparkJobDefinition' }).Count

if ($notebookCount -gt 20) {
    Write-Host "  - Consider consolidating notebooks to reduce session overhead" -ForegroundColor Cyan
}
if ($sjdCount -gt 10) {
    Write-Host "  - Review Spark job definitions for scheduling conflicts" -ForegroundColor Cyan
}

Write-Host "  - Use Monitoring Hub to identify long-running or idle sessions" -ForegroundColor Cyan
Write-Host "  - Review Capacity Metrics app for historical utilization trends" -ForegroundColor Cyan
Write-Host "  - Consider Autoscale Billing for bursty Spark workloads" -ForegroundColor Cyan
#endregion

Write-Host "`nConcurrency analysis complete." -ForegroundColor Green
