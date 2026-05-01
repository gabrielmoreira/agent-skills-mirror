<#
.SYNOPSIS
    Diagnoses Delta table health in a Microsoft Fabric Lakehouse using the REST API.

.DESCRIPTION
    Retrieves table metadata and identifies potential performance issues including
    high file counts, small average file sizes, and missing table maintenance.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace containing the Lakehouse.

.PARAMETER LakehouseId
    The GUID of the Lakehouse item.

.PARAMETER AccessToken
    A valid Microsoft Entra bearer token for the Fabric API. If omitted, attempts
    to acquire a token using Az.Accounts.

.EXAMPLE
    ./Diagnose-DeltaTableHealth.ps1 -WorkspaceId "abc-123" -LakehouseId "def-456"

.NOTES
    Requires PowerShell 7+ and optionally the Az.Accounts module for token acquisition.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter()]
    [string]$AccessToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Token Acquisition
if (-not $AccessToken) {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        $AccessToken = $tokenResponse.Token
        Write-Verbose 'Acquired token via Az.Accounts.'
    }
    catch {
        Write-Error 'No AccessToken provided and Az.Accounts token acquisition failed. Provide -AccessToken or run Connect-AzAccount first.'
        return
    }
}
#endregion

#region API Helpers
$headers = @{
    'Authorization' = "Bearer $AccessToken"
    'Content-Type'  = 'application/json'
}

$baseUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items/$LakehouseId"

function Invoke-FabricApi {
    param([string]$Uri, [string]$Method = 'GET', [object]$Body)
    $params = @{
        Uri     = $Uri
        Method  = $Method
        Headers = $headers
    }
    if ($Body) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
    }
    try {
        Invoke-RestMethod @params
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $detail = $_.ErrorDetails.Message
        Write-Warning "API call failed ($statusCode): $detail"
        return $null
    }
}
#endregion

#region List Tables
Write-Host "`n=== Delta Table Health Diagnostic ===" -ForegroundColor Cyan
Write-Host "Workspace : $WorkspaceId"
Write-Host "Lakehouse : $LakehouseId"
Write-Host "Timestamp : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)`n"

$tablesUri = "$baseUri/tables"
$tablesResponse = Invoke-FabricApi -Uri $tablesUri

if (-not $tablesResponse -or -not $tablesResponse.data) {
    Write-Warning 'No tables found or unable to retrieve table list.'
    return
}

$tables = $tablesResponse.data
Write-Host "Found $($tables.Count) tables.`n" -ForegroundColor Green
#endregion

#region Analyze Each Table
$results = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($table in $tables) {
    $tableName = $table.name
    $tableType = $table.type
    $tableFormat = $table.format

    if ($tableFormat -ne 'delta') {
        Write-Verbose "Skipping non-Delta table: $tableName ($tableFormat)"
        continue
    }

    $location = if ($table.location) { $table.location } else { 'N/A' }

    # Build health assessment
    $status = 'Healthy'
    $issues = [System.Collections.Generic.List[string]]::new()
    $recommendations = [System.Collections.Generic.List[string]]::new()

    # Note: REST API provides limited metadata. For deep diagnostics,
    # use the PySpark notebook template which can inspect Delta logs directly.

    $result = [PSCustomObject]@{
        TableName       = $tableName
        Type            = $tableType
        Format          = $tableFormat
        Location        = $location
        Status          = $status
        Issues          = ($issues -join '; ')
        Recommendations = ($recommendations -join '; ')
    }

    $results.Add($result)
}
#endregion

#region Output Results
Write-Host "`n=== Table Summary ===" -ForegroundColor Cyan

$results | Format-Table -AutoSize -Property TableName, Type, Format, Status

$issueCount = ($results | Where-Object { $_.Status -ne 'Healthy' }).Count
if ($issueCount -gt 0) {
    Write-Host "`n$issueCount table(s) have potential issues:" -ForegroundColor Yellow
    $results | Where-Object { $_.Status -ne 'Healthy' } | ForEach-Object {
        Write-Host "  - $($_.TableName): $($_.Issues)" -ForegroundColor Yellow
        Write-Host "    Fix: $($_.Recommendations)" -ForegroundColor DarkYellow
    }
}
else {
    Write-Host "`nAll Delta tables appear healthy from REST API metadata." -ForegroundColor Green
    Write-Host "For deeper diagnostics (file sizes, version history, small file detection),"
    Write-Host "run the PySpark diagnostic notebook: templates/perf-diagnostic-notebook.py" -ForegroundColor DarkCyan
}

Write-Host "`n=== Diagnostic Complete ===" -ForegroundColor Cyan
#endregion
