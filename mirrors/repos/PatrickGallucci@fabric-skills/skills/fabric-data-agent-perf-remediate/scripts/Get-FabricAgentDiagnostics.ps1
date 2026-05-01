<#
.SYNOPSIS
    Collects diagnostic information for a Microsoft Fabric Data Agent workspace.

.DESCRIPTION
    Gathers workspace metadata, capacity details, Spark-related items, and
    Lakehouse properties to help diagnose Data Agent performance issues.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace to diagnose.

.PARAMETER IncludeLakehouseDetails
    When specified, fetches detailed properties for each Lakehouse in the workspace.

.EXAMPLE
    .\Get-FabricAgentDiagnostics.ps1 -WorkspaceId "fc67689a-442e-4d14-b3f8-085076f2f92f"

.EXAMPLE
    .\Get-FabricAgentDiagnostics.ps1 -WorkspaceId "fc67689a-..." -IncludeLakehouseDetails

.NOTES
    Requires: Az.Accounts module, authenticated Azure session (Connect-AzAccount)
    API Base: https://api.fabric.microsoft.com/v1
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$')]
    [string]$WorkspaceId,

    [switch]$IncludeLakehouseDetails
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $tokenResponse = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
    $headers = @{
        Authorization  = "Bearer $($tokenResponse.Token)"
        'Content-Type' = 'application/json'
    }
    Write-Host "[OK] Authenticated to Fabric API" -ForegroundColor Green
}
catch {
    Write-Error "Authentication failed. Run Connect-AzAccount first. Error: $_"
    return
}
#endregion

#region Helper
function Invoke-FabricApi {
    param([string]$Uri, [string]$Method = 'Get')
    try {
        Invoke-RestMethod -Uri $Uri -Headers $headers -Method $Method
    }
    catch {
        Write-Warning "API call failed: $Uri - $($_.Exception.Message)"
        return $null
    }
}
#endregion

$apiBase = "https://api.fabric.microsoft.com/v1"
$diagnostics = [ordered]@{
    Timestamp   = Get-Date -Format 'o'
    WorkspaceId = $WorkspaceId
}

#region Workspace Info
Write-Host "`n--- Workspace Information ---" -ForegroundColor Cyan
$workspace = Invoke-FabricApi -Uri "$apiBase/workspaces/$WorkspaceId"
if ($workspace) {
    $diagnostics.WorkspaceName = $workspace.displayName
    $diagnostics.CapacityId   = $workspace.capacityId
    Write-Host "  Name:        $($workspace.displayName)"
    Write-Host "  Capacity ID: $($workspace.capacityId)"
}
#endregion

#region List Items
Write-Host "`n--- Workspace Items ---" -ForegroundColor Cyan
$items = Invoke-FabricApi -Uri "$apiBase/workspaces/$WorkspaceId/items"
if ($items) {
    $itemList = $items.value

    $sparkTypes = @('Notebook', 'SparkJobDefinition', 'Lakehouse', 'Environment')
    $agentTypes = @('DataAgent', 'OperationsAgent')
    $allRelevant = $sparkTypes + $agentTypes

    $relevant = $itemList | Where-Object { $_.type -in $allRelevant }

    $summary = $relevant | Group-Object -Property type | ForEach-Object {
        [PSCustomObject]@{ ItemType = $_.Name; Count = $_.Count }
    }
    $summary | Format-Table -AutoSize

    $diagnostics.ItemCounts = @{}
    foreach ($s in $summary) {
        $diagnostics.ItemCounts[$s.ItemType] = $s.Count
    }

    # List agent items
    $agents = $itemList | Where-Object { $_.type -in $agentTypes }
    if ($agents) {
        Write-Host "  Agent Items:" -ForegroundColor Yellow
        foreach ($agent in $agents) {
            Write-Host "    - $($agent.displayName) ($($agent.type)) [ID: $($agent.id)]"
        }
        $diagnostics.Agents = $agents | Select-Object id, displayName, type
    }
    else {
        Write-Host "  No Data Agent or Operations Agent items found." -ForegroundColor Yellow
    }
}
#endregion

#region Lakehouse Details
if ($IncludeLakehouseDetails) {
    Write-Host "`n--- Lakehouse Details ---" -ForegroundColor Cyan
    $lakehouses = $itemList | Where-Object { $_.type -eq 'Lakehouse' }

    $diagnostics.Lakehouses = @()
    foreach ($lh in $lakehouses) {
        $lhDetail = Invoke-FabricApi -Uri "$apiBase/workspaces/$WorkspaceId/lakehouses/$($lh.id)"
        if ($lhDetail) {
            $props = $lhDetail.properties
            $info = [ordered]@{
                Name              = $lhDetail.displayName
                Id                = $lhDetail.id
                SqlEndpointStatus = $props.sqlEndpointProperties.provisioningStatus
                OneLakeTablesPath = $props.oneLakeTablesPath
            }
            Write-Host "  $($info.Name): SQL Endpoint = $($info.SqlEndpointStatus)"
            $diagnostics.Lakehouses += $info
        }
    }
}
#endregion

#region Output
Write-Host "`n--- Diagnostic Summary ---" -ForegroundColor Cyan
$diagnostics | ConvertTo-Json -Depth 5

$outPath = Join-Path $PWD "fabric-agent-diagnostics-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
$diagnostics | ConvertTo-Json -Depth 5 | Set-Content -Path $outPath -Encoding utf8
Write-Host "`nDiagnostics saved to: $outPath" -ForegroundColor Green
#endregion
