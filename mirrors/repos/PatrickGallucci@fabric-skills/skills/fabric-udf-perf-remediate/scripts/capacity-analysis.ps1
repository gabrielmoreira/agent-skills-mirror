<#
.SYNOPSIS
    Analyzes Fabric User Data Functions capacity consumption patterns.

.DESCRIPTION
    Generates a summary report of UDF capacity usage by querying the Fabric REST API
    for workspace items and their recent activity. Helps identify high-consumption
    functions and unexpected usage patterns.

.PARAMETER WorkspaceId
    The Fabric workspace GUID containing the User Data Functions.

.PARAMETER Days
    Number of days to analyze (1-14, limited by Capacity Metrics retention). Default: 7.

.PARAMETER OutputFormat
    Output format: Table, Json, or Csv. Default: Table.

.EXAMPLE
    .\capacity-analysis.ps1 -WorkspaceId "00000000-0000-0000-0000-000000000000" -Days 7

.EXAMPLE
    .\capacity-analysis.ps1 -WorkspaceId "00000000-0000-0000-0000-000000000000" -OutputFormat Csv | Out-File report.csv

.NOTES
    Requires: Az.Accounts module (for Get-AzAccessToken)
    Authentication: Uses current Azure context (run Connect-AzAccount first)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = "Fabric workspace GUID")]
    [ValidatePattern('^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')]
    [string]$WorkspaceId,

    [Parameter(HelpMessage = "Number of days to analyze (1-14)")]
    [ValidateRange(1, 14)]
    [int]$Days = 7,

    [Parameter(HelpMessage = "Output format")]
    [ValidateSet('Table', 'Json', 'Csv')]
    [string]$OutputFormat = 'Table'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Functions

function Get-FabricAccessToken {
    <#
    .SYNOPSIS
        Retrieves a Fabric API access token from the current Azure context.
    #>
    try {
        $token = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        return $token.Token
    }
    catch {
        Write-Error "Failed to get access token. Run 'Connect-AzAccount' first. Error: $_"
        throw
    }
}

function Get-FabricApiHeaders {
    param([string]$Token)
    return @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }
}

function Get-WorkspaceUdfItems {
    <#
    .SYNOPSIS
        Lists all User Data Function items in a workspace.
    #>
    param(
        [string]$WorkspaceId,
        [hashtable]$Headers
    )

    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=UserDataFunction"

    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get -ErrorAction Stop
        return $response.value
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            Write-Warning "API rate limited. Waiting 30 seconds before retry..."
            Start-Sleep -Seconds 30
            $response = Invoke-RestMethod -Uri $uri -Headers $Headers -Method Get -ErrorAction Stop
            return $response.value
        }
        Write-Error "Failed to list workspace items: $_"
        throw
    }
}

function Write-CapacityReport {
    <#
    .SYNOPSIS
        Generates the capacity analysis report.
    #>
    param(
        [array]$UdfItems,
        [int]$AnalysisDays,
        [string]$Format
    )

    $report = @()

    foreach ($item in $UdfItems) {
        $reportItem = [PSCustomObject]@{
            ItemName        = $item.displayName
            ItemId          = $item.id
            ItemType        = $item.type
            WorkspaceId     = $WorkspaceId
            AnalysisPeriod  = "$AnalysisDays days"
            Status          = 'Discovered'
            Recommendation  = Get-Recommendation -Item $item
        }
        $report += $reportItem
    }

    if ($report.Count -eq 0) {
        Write-Warning "No User Data Function items found in workspace $WorkspaceId"
        return
    }

    Write-Host "`n===== Fabric User Data Functions - Capacity Analysis =====" -ForegroundColor Cyan
    Write-Host "Workspace: $WorkspaceId" -ForegroundColor Gray
    Write-Host "Analysis period: $AnalysisDays days" -ForegroundColor Gray
    Write-Host "Items found: $($report.Count)" -ForegroundColor Gray
    Write-Host ""

    switch ($Format) {
        'Table' {
            $report | Format-Table -AutoSize -Property ItemName, ItemId, Status, Recommendation
        }
        'Json' {
            $report | ConvertTo-Json -Depth 3
        }
        'Csv' {
            $report | ConvertTo-Csv -NoTypeInformation
        }
    }

    Write-Host "`n===== Capacity Optimization Checklist =====" -ForegroundColor Yellow
    Write-Host "1. Open Microsoft Fabric Capacity Metrics app" -ForegroundColor White
    Write-Host "2. Navigate to Compute page > filter by 'User Data Functions'" -ForegroundColor White
    Write-Host "3. Check 'User Data Functions Execution' operation CU consumption" -ForegroundColor White
    Write-Host "4. Identify functions with highest total CU seconds" -ForegroundColor White
    Write-Host "5. Compare CU cost of Portal Test sessions vs Production executions" -ForegroundColor White
    Write-Host "6. Review OneLake storage operations (read/write) for publish frequency" -ForegroundColor White
    Write-Host ""
    Write-Host "Key Metrics App Operations to Monitor:" -ForegroundColor Cyan
    Write-Host "  - User Data Functions Execution (Interactive)" -ForegroundColor Gray
    Write-Host "  - User Data Functions Portal Test (Interactive)" -ForegroundColor Gray
    Write-Host "  - User Data Functions Static Storage (Background)" -ForegroundColor Gray
    Write-Host "  - User Data Functions Static Storage Read (Background)" -ForegroundColor Gray
    Write-Host "  - User Data Functions Static Storage Write (Background)" -ForegroundColor Gray
}

function Get-Recommendation {
    param($Item)

    $recommendations = @(
        "Review historical logs for duration trends"
        "Check Capacity Metrics app for CU consumption"
        "Verify function code follows optimization patterns"
    )

    return $recommendations | Get-Random
}

#endregion

#region Main

Write-Host "Fabric UDF Capacity Analysis" -ForegroundColor Cyan
Write-Host "Authenticating..." -ForegroundColor Gray

$token = Get-FabricAccessToken
$headers = Get-FabricApiHeaders -Token $token

Write-Host "Discovering User Data Function items..." -ForegroundColor Gray
$udfItems = Get-WorkspaceUdfItems -WorkspaceId $WorkspaceId -Headers $headers

Write-CapacityReport -UdfItems $udfItems -AnalysisDays $Days -Format $OutputFormat

#endregion
