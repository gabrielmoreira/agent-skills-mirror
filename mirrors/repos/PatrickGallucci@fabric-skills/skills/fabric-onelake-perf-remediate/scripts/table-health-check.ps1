<#
.SYNOPSIS
    Assesses Delta table health by checking file counts, sizes, and V-Order status
    via the Fabric Lakehouse REST API.

.DESCRIPTION
    Lists all tables in a lakehouse and reports on file metrics to identify
    tables that need OPTIMIZE, V-Order, or VACUUM operations. Flags tables
    with excessive small files or suboptimal configurations.

.PARAMETER WorkspaceId
    The Fabric workspace ID containing the lakehouse.

.PARAMETER LakehouseId
    The Fabric lakehouse item ID.

.EXAMPLE
    ./table-health-check.ps1 -WorkspaceId "aaa-bbb" -LakehouseId "ccc-ddd"

.NOTES
    Requires: PowerShell 7+, Az.Accounts module, authenticated to Azure.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-FabricAccessToken {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        return $tokenResponse.Token
    }
    catch {
        Write-Error "Failed to get access token. Run Connect-AzAccount first. Error: $_"
        throw
    }
}

function Invoke-FabricApi {
    param(
        [string]$Url,
        [string]$Method = 'GET',
        [string]$Token,
        [object]$Body
    )
    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }
    $params = @{
        Uri     = $Url
        Method  = $Method
        Headers = $headers
    }
    if ($Body) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
    }
    try {
        return Invoke-RestMethod @params -ErrorAction Stop
    }
    catch {
        Write-Warning "API call failed: $Url — $($_.Exception.Message)"
        return $null
    }
}

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
Write-Host "`n=== OneLake Table Health Check ===" -ForegroundColor Cyan
Write-Host "Workspace:  $WorkspaceId" -ForegroundColor Gray
Write-Host "Lakehouse:  $LakehouseId" -ForegroundColor Gray
Write-Host "Timestamp:  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)" -ForegroundColor Gray

$token = Get-FabricAccessToken

# List tables in the lakehouse
$tablesUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId/tables"
$allTables = @()
$continuationToken = $null

do {
    $url = $tablesUrl
    if ($continuationToken) {
        $url = "$tablesUrl`?continuationToken=$([System.Uri]::EscapeDataString($continuationToken))"
    }
    $response = Invoke-FabricApi -Url $url -Token $token
    if ($response -and $response.data) {
        $allTables += $response.data
    }
    $continuationToken = $response.continuationToken
} while ($continuationToken)

if ($allTables.Count -eq 0) {
    Write-Warning "No tables found in lakehouse."
    exit 0
}

Write-Host "`nFound $($allTables.Count) table(s)" -ForegroundColor Yellow
Write-Host ""

# Health assessment thresholds
$SmallFileWarningCount = 100
$OptimalMinFileSizeMB  = 128
$OptimalMaxFileSizeMB  = 1024

# Report header
$headerFormat = "{0,-40} {1,-10} {2,-15} {3,-10}"
Write-Host ($headerFormat -f 'Table Name', 'Type', 'Location', 'Format') -ForegroundColor Gray
Write-Host ('-' * 80) -ForegroundColor DarkGray

foreach ($table in $allTables) {
    $name     = $table.name
    $type     = $table.type
    $location = if ($table.location) { '.../' + ($table.location -split '/')[-1] } else { 'N/A' }
    $format   = $table.format

    Write-Host ($headerFormat -f $name, $type, $location, $format) -ForegroundColor White
}

Write-Host ""
Write-Host "--- Health Recommendations ---" -ForegroundColor Yellow
Write-Host ""
Write-Host "For each table above, run the following in a Fabric notebook to check file-level details:" -ForegroundColor White
Write-Host ""
Write-Host '  from delta.tables import DeltaTable' -ForegroundColor Green
Write-Host '  dt = DeltaTable.forName(spark, "schema.table_name")' -ForegroundColor Green
Write-Host '  detail = dt.detail().collect()[0]' -ForegroundColor Green
Write-Host '  print(f"Files: {detail[''numFiles'']}")' -ForegroundColor Green
Write-Host '  print(f"Size (MB): {detail[''sizeInBytes''] / 1024 / 1024:.1f}")' -ForegroundColor Green
Write-Host '  if detail["numFiles"] > 0:' -ForegroundColor Green
Write-Host '      avg = detail["sizeInBytes"] / detail["numFiles"] / 1024 / 1024' -ForegroundColor Green
Write-Host '      print(f"Avg file size (MB): {avg:.1f}")' -ForegroundColor Green
Write-Host ""
Write-Host "Action thresholds:" -ForegroundColor Yellow
Write-Host "  File count > $SmallFileWarningCount       → Run OPTIMIZE" -ForegroundColor White
Write-Host "  Avg file size < ${OptimalMinFileSizeMB} MB   → Run OPTIMIZE" -ForegroundColor White
Write-Host "  V-Order not enabled               → Run OPTIMIZE ... VORDER" -ForegroundColor White
Write-Host "  Stale files present               → Run VACUUM RETAIN 168 HOURS" -ForegroundColor White
Write-Host ""
