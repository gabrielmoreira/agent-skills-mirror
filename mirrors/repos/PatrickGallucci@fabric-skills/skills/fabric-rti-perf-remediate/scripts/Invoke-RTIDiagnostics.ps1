<#
.SYNOPSIS
    Fabric Real-Time Intelligence Performance Diagnostic Helper
.DESCRIPTION
    Automates common diagnostic tasks for Fabric RTI performance remediate.
    Connects to Fabric REST APIs to retrieve Eventhouse and capacity information.
.PARAMETER WorkspaceId
    The Fabric workspace GUID.
.PARAMETER Action
    The diagnostic action to perform: ListEventhouses, CheckCapacity, ExportQueryLogs.
.PARAMETER OutputPath
    Directory to save diagnostic output. Defaults to current directory.
.EXAMPLE
    .\Invoke-RTIDiagnostics.ps1 -WorkspaceId "abc-123" -Action ListEventhouses
.EXAMPLE
    .\Invoke-RTIDiagnostics.ps1 -WorkspaceId "abc-123" -Action ExportQueryLogs -OutputPath "C:\Diag"
.NOTES
    Requires: Az.Accounts module for authentication
    Fabric REST API: https://learn.microsoft.com/en-us/rest/api/fabric/
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [ValidateSet('ListEventhouses', 'CheckCapacity', 'ExportQueryLogs', 'HealthCheck')]
    [string]$Action,

    [Parameter()]
    [string]$OutputPath = (Get-Location).Path
)

$ErrorActionPreference = 'Stop'

#region Authentication
function Get-FabricAccessToken {
    <#
    .SYNOPSIS
        Obtains an access token for Fabric REST API calls.
    #>
    try {
        $context = Get-AzContext
        if (-not $context) {
            Write-Host 'No Azure context found. Running Connect-AzAccount...' -ForegroundColor Yellow
            Connect-AzAccount | Out-Null
        }
        $token = (Get-AzAccessToken -ResourceUrl 'https://analysis.windows.net/powerbi/api').Token
        return $token
    }
    catch {
        Write-Error "Failed to obtain access token: $_"
        throw
    }
}
#endregion

#region API Helpers
function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Sends an authenticated request to the Fabric REST API.
    #>
    param(
        [string]$Method = 'GET',
        [string]$Uri,
        [string]$Token,
        [object]$Body
    )

    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }

    $params = @{
        Method  = $Method
        Uri     = $Uri
        Headers = $headers
    }

    if ($Body) {
        $params['Body'] = ($Body | ConvertTo-Json -Depth 10)
    }

    try {
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            $retryAfter = $_.Exception.Response.Headers['Retry-After']
            Write-Warning "Rate limited. Retry after $retryAfter seconds."
        }
        throw
    }
}
#endregion

#region Diagnostic Actions
function Get-Eventhouses {
    <#
    .SYNOPSIS
        Lists all Eventhouses in the workspace with basic metadata.
    #>
    param([string]$Token, [string]$WorkspaceId)

    $baseUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
    $response = Invoke-FabricApi -Uri $baseUri -Token $Token

    $eventhouses = $response.value | Where-Object { $_.type -eq 'Eventhouse' }
    $kqlDatabases = $response.value | Where-Object { $_.type -eq 'KQLDatabase' }

    Write-Host "`n=== Eventhouses ===" -ForegroundColor Cyan
    if ($eventhouses.Count -eq 0) {
        Write-Host 'No Eventhouses found in this workspace.' -ForegroundColor Yellow
    }
    else {
        $eventhouses | ForEach-Object {
            Write-Host "  Name: $($_.displayName)" -ForegroundColor Green
            Write-Host "    ID: $($_.id)"
            Write-Host "    Description: $($_.description)"
        }
    }

    Write-Host "`n=== KQL Databases ===" -ForegroundColor Cyan
    if ($kqlDatabases.Count -eq 0) {
        Write-Host 'No KQL Databases found.' -ForegroundColor Yellow
    }
    else {
        $kqlDatabases | ForEach-Object {
            Write-Host "  Name: $($_.displayName)" -ForegroundColor Green
            Write-Host "    ID: $($_.id)"
        }
    }

    return @{
        Eventhouses  = $eventhouses
        KQLDatabases = $kqlDatabases
    }
}

function Get-CapacityInfo {
    <#
    .SYNOPSIS
        Retrieves capacity information for the workspace.
    #>
    param([string]$Token, [string]$WorkspaceId)

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId"
    $workspace = Invoke-FabricApi -Uri $uri -Token $Token

    Write-Host "`n=== Workspace Capacity ===" -ForegroundColor Cyan
    Write-Host "  Workspace: $($workspace.displayName)"
    Write-Host "  Capacity ID: $($workspace.capacityId)"

    if ($workspace.capacityId) {
        try {
            $capUri = "https://api.fabric.microsoft.com/v1/capacities/$($workspace.capacityId)"
            $capacity = Invoke-FabricApi -Uri $capUri -Token $Token
            Write-Host "  SKU: $($capacity.sku)" -ForegroundColor Green
            Write-Host "  State: $($capacity.state)"
            Write-Host "  Region: $($capacity.region)"
        }
        catch {
            Write-Warning "Could not retrieve capacity details (may require admin permissions): $_"
        }
    }

    return $workspace
}

function Invoke-HealthCheck {
    <#
    .SYNOPSIS
        Performs a comprehensive health check and generates a summary report.
    #>
    param([string]$Token, [string]$WorkspaceId, [string]$OutputPath)

    $report = [System.Text.StringBuilder]::new()
    [void]$report.AppendLine('# Fabric RTI Health Check Report')
    [void]$report.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)")
    [void]$report.AppendLine("Workspace: $WorkspaceId")
    [void]$report.AppendLine('')

    # List items
    Write-Host 'Checking workspace items...' -ForegroundColor Cyan
    $items = Get-Eventhouses -Token $Token -WorkspaceId $WorkspaceId

    [void]$report.AppendLine('## Eventhouses')
    foreach ($eh in $items.Eventhouses) {
        [void]$report.AppendLine("- **$($eh.displayName)** (ID: $($eh.id))")
    }

    [void]$report.AppendLine('')
    [void]$report.AppendLine('## KQL Databases')
    foreach ($db in $items.KQLDatabases) {
        [void]$report.AppendLine("- **$($db.displayName)** (ID: $($db.id))")
    }

    # Capacity
    Write-Host 'Checking capacity...' -ForegroundColor Cyan
    $workspace = Get-CapacityInfo -Token $Token -WorkspaceId $WorkspaceId

    [void]$report.AppendLine('')
    [void]$report.AppendLine('## Capacity')
    [void]$report.AppendLine("- Capacity ID: $($workspace.capacityId)")

    [void]$report.AppendLine('')
    [void]$report.AppendLine('## Recommendations')
    [void]$report.AppendLine('- [ ] Verify workspace monitoring is enabled')
    [void]$report.AppendLine('- [ ] Run diagnose-slow-queries.kql against monitoring database')
    [void]$report.AppendLine('- [ ] Run diagnose-ingestion.kql for ingestion health')
    [void]$report.AppendLine('- [ ] Run diagnose-capacity.kql for resource utilization')
    [void]$report.AppendLine('- [ ] Check Fabric Capacity Metrics app for CU saturation')
    [void]$report.AppendLine('- [ ] Review cache policies against actual query time ranges')
    [void]$report.AppendLine('- [ ] Evaluate Always-On setting for latency-sensitive workloads')

    $reportPath = Join-Path $OutputPath "rti-health-check-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    $report.ToString() | Out-File -FilePath $reportPath -Encoding utf8
    Write-Host "`nHealth check report saved to: $reportPath" -ForegroundColor Green

    return $reportPath
}
#endregion

#region Main
$token = Get-FabricAccessToken

switch ($Action) {
    'ListEventhouses' {
        Get-Eventhouses -Token $token -WorkspaceId $WorkspaceId
    }
    'CheckCapacity' {
        Get-CapacityInfo -Token $token -WorkspaceId $WorkspaceId
    }
    'ExportQueryLogs' {
        Write-Host 'ExportQueryLogs requires running KQL scripts directly against the monitoring database.' -ForegroundColor Yellow
        Write-Host 'Use the diagnose-slow-queries.kql script in a KQL Queryset connected to your monitoring Eventhouse.' -ForegroundColor Yellow
        Write-Host "Scripts location: $(Split-Path $PSScriptRoot)\scripts\" -ForegroundColor Cyan
    }
    'HealthCheck' {
        Invoke-HealthCheck -Token $token -WorkspaceId $WorkspaceId -OutputPath $OutputPath
    }
}
#endregion
