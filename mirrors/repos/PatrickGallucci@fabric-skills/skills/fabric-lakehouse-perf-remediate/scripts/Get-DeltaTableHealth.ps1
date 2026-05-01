<#
.SYNOPSIS
    Assesses Delta table health in a Microsoft Fabric Lakehouse via REST API.

.DESCRIPTION
    Lists all tables in a Fabric Lakehouse and retrieves basic metadata to help
    identify tables that may need maintenance. Outputs a summary with table names
    and recommends maintenance actions based on table listing data.

.PARAMETER WorkspaceId
    The Fabric workspace GUID.

.PARAMETER LakehouseId
    The Lakehouse item GUID within the workspace.

.PARAMETER OutputFormat
    Output format: 'Table' (console table) or 'Json' (JSON for piping). Default: Table.

.EXAMPLE
    .\Get-DeltaTableHealth.ps1 -WorkspaceId '<guid>' -LakehouseId '<guid>'

.EXAMPLE
    .\Get-DeltaTableHealth.ps1 -WorkspaceId '<guid>' -LakehouseId '<guid>' -OutputFormat Json | ConvertFrom-Json

.NOTES
    Requires Az.Accounts module for authentication.
    Run Connect-AzAccount before executing this script.

    This script uses the Lakehouse List Tables API to retrieve table metadata.
    For deeper file-level analysis (file count, sizes, V-Order status), use the
    perf-diagnostic-notebook.py PySpark template in a Fabric notebook.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [ValidateSet('Table', 'Json')]
    [string]$OutputFormat = 'Table'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Functions

function Get-FabricToken {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com'
        return $tokenResponse.Token
    }
    catch {
        throw "Failed to obtain Fabric API token. Ensure you have run Connect-AzAccount. Error: $_"
    }
}

function Get-LakehouseProperties {
    [CmdletBinding()]
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId
    )

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId"
    $headers = @{ 'Authorization' = "Bearer $Token" }

    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
        return $response
    }
    catch {
        Write-Warning "Failed to get Lakehouse properties: $_"
        return $null
    }
}

function Get-LakehouseTables {
    [CmdletBinding()]
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId
    )

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId/tables"
    $headers = @{ 'Authorization' = "Bearer $Token" }

    $allTables = @()
    $continuationUri = $uri

    do {
        try {
            $response = Invoke-RestMethod -Uri $continuationUri -Headers $headers -Method Get

            if ($response.data) {
                $allTables += $response.data
            }

            $continuationUri = $response.continuationUri
        }
        catch {
            Write-Warning "Failed to list tables: $_"
            $continuationUri = $null
        }
    } while ($continuationUri)

    return $allTables
}

#endregion Functions

#region Main

Write-Host "`n=== Fabric Lakehouse Delta Table Health Assessment ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId"
Write-Host "Lakehouse: $LakehouseId"
Write-Host ""

# Authenticate
Write-Host "Authenticating..." -ForegroundColor Yellow
$token = Get-FabricToken
Write-Host "Authentication successful.`n" -ForegroundColor Green

# Get Lakehouse info
Write-Host "Retrieving Lakehouse properties..." -ForegroundColor Yellow
$lakehouse = Get-LakehouseProperties -Token $token -WorkspaceId $WorkspaceId -LakehouseId $LakehouseId

if ($lakehouse) {
    Write-Host "Lakehouse: $($lakehouse.displayName)" -ForegroundColor Green
    if ($lakehouse.properties.sqlEndpointProperties) {
        Write-Host "SQL Endpoint: $($lakehouse.properties.sqlEndpointProperties.connectionString)" -ForegroundColor Gray
    }
    Write-Host ""
}

# List tables
Write-Host "Listing Delta tables..." -ForegroundColor Yellow
$tables = Get-LakehouseTables -Token $token -WorkspaceId $WorkspaceId -LakehouseId $LakehouseId

if ($tables.Count -eq 0) {
    Write-Host "No tables found in this Lakehouse." -ForegroundColor Yellow
    return
}

Write-Host "Found $($tables.Count) table(s).`n" -ForegroundColor Green

# Build assessment
$assessment = @()

foreach ($table in $tables) {
    $tableInfo = @{
        Name     = $table.name
        Type     = $table.type
        Format   = $table.format
        Location = $table.location
    }

    # Recommendations based on table metadata
    $recommendations = @()

    if ($table.format -ne 'delta') {
        $recommendations += 'Convert to Delta format for best performance'
    }
    else {
        $recommendations += 'Run OPTIMIZE VORDER if not recently maintained'
        $recommendations += 'Run VACUUM to clean unreferenced files'
    }

    $tableInfo.Recommendations = $recommendations -join '; '
    $assessment += [PSCustomObject]$tableInfo
}

# Output
if ($OutputFormat -eq 'Json') {
    $assessment | ConvertTo-Json -Depth 3
}
else {
    Write-Host "=== Table Inventory ===" -ForegroundColor Cyan
    $assessment | Format-Table -Property Name, Type, Format -AutoSize

    Write-Host "`n=== Recommendations ===" -ForegroundColor Cyan
    foreach ($item in $assessment) {
        Write-Host "`n  $($item.Name):" -ForegroundColor White
        $item.Recommendations -split '; ' | ForEach-Object {
            Write-Host "    - $_" -ForegroundColor Gray
        }
    }

    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "  For detailed file-level analysis (file count, sizes, V-Order status),"
    Write-Host "  run the perf-diagnostic-notebook.py template in a Fabric notebook."
    Write-Host "  To automate maintenance, use Invoke-FabricTableMaintenance.ps1."
}

Write-Host "`nDone." -ForegroundColor Cyan

#endregion Main
