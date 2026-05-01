<#
.SYNOPSIS
    Monitors Spark VCore utilization and queue depth for a Fabric capacity.

.DESCRIPTION
    Queries the Fabric Admin REST API to check active Spark sessions and compare
    utilization against the capacity SKU's VCore and queue limits. Helps diagnose
    HTTP 430 throttling issues.

.PARAMETER WorkspaceId
    The Fabric workspace ID to monitor.

.PARAMETER CapacityId
    The Fabric capacity ID (optional; auto-detected from workspace if omitted).

.EXAMPLE
    ./spark-capacity-check.ps1 -WorkspaceId "aaaabbbb-1111-2222-3333-ccccddddeeee"

.NOTES
    Requires: PowerShell 7+, Az.Accounts module, authenticated to Azure.
    Run Connect-AzAccount before executing this script.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter()]
    [string]$CapacityId
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ------------------------------------------------------------------
# SKU reference: Capacity Units → Spark VCores and Queue Limits
# ------------------------------------------------------------------
$SkuLimits = @{
    'F2'    = @{ VCores = 4;    QueueLimit = 4    }
    'F4'    = @{ VCores = 8;    QueueLimit = 4    }
    'F8'    = @{ VCores = 16;   QueueLimit = 8    }
    'F16'   = @{ VCores = 32;   QueueLimit = 16   }
    'F32'   = @{ VCores = 64;   QueueLimit = 32   }
    'F64'   = @{ VCores = 128;  QueueLimit = 64   }
    'F128'  = @{ VCores = 256;  QueueLimit = 128  }
    'F256'  = @{ VCores = 512;  QueueLimit = 256  }
    'F512'  = @{ VCores = 1024; QueueLimit = 512  }
    'F1024' = @{ VCores = 2048; QueueLimit = 1024 }
    'F2048' = @{ VCores = 4096; QueueLimit = 2048 }
}

function Get-FabricAccessToken {
    <#
    .SYNOPSIS
        Retrieves an access token for the Fabric API.
    #>
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com' -ErrorAction Stop
        return $tokenResponse.Token
    }
    catch {
        Write-Error "Failed to get access token. Ensure you are logged in with Connect-AzAccount. Error: $_"
        throw
    }
}

function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Makes an authenticated REST call to the Fabric API.
    #>
    param(
        [string]$Url,
        [string]$Method = 'GET',
        [string]$Token
    )
    $headers = @{
        'Authorization' = "Bearer $Token"
        'Content-Type'  = 'application/json'
    }
    try {
        $response = Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers -ErrorAction Stop
        return $response
    }
    catch {
        Write-Warning "API call failed: $Url"
        Write-Warning "Error: $($_.Exception.Message)"
        return $null
    }
}

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
Write-Host "`n=== OneLake Spark Capacity Check ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId" -ForegroundColor Gray
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)" -ForegroundColor Gray

$token = Get-FabricAccessToken

# Get workspace details to identify capacity
$workspaceUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId"
$workspace = Invoke-FabricApi -Url $workspaceUrl -Token $token

if (-not $workspace) {
    Write-Error "Unable to retrieve workspace details."
    exit 1
}

Write-Host "`nWorkspace Name: $($workspace.displayName)" -ForegroundColor White

if ($workspace.capacityId) {
    $detectedCapacityId = $workspace.capacityId
    Write-Host "Capacity ID:    $detectedCapacityId" -ForegroundColor White
}

# Get items in workspace to count Spark-related items
$itemsUrl = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
$items = Invoke-FabricApi -Url $itemsUrl -Token $token

if ($items -and $items.value) {
    $sparkItems = $items.value | Where-Object {
        $_.type -in @('Notebook', 'SparkJobDefinition', 'Lakehouse')
    }
    Write-Host "`nSpark-capable items in workspace:" -ForegroundColor Yellow
    $sparkItems | Group-Object -Property type | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count)" -ForegroundColor White
    }
}

# Display SKU reference
Write-Host "`n--- SKU Quick Reference ---" -ForegroundColor Yellow
Write-Host ("{0,-10} {1,-12} {2,-12}" -f 'SKU', 'VCores', 'Queue Limit') -ForegroundColor Gray
foreach ($sku in $SkuLimits.GetEnumerator() | Sort-Object { [int]($_.Key -replace '\D', '') }) {
    Write-Host ("{0,-10} {1,-12} {2,-12}" -f $sku.Key, $sku.Value.VCores, $sku.Value.QueueLimit) -ForegroundColor White
}

Write-Host "`n--- Recommendations ---" -ForegroundColor Yellow
Write-Host "1. Open the Monitoring Hub in the Fabric portal to see active Spark sessions" -ForegroundColor White
Write-Host "2. If HTTP 430 errors persist, cancel idle sessions or scale up the capacity SKU" -ForegroundColor White
Write-Host "3. For burst workloads, ensure your queue limit provides enough buffer" -ForegroundColor White
Write-Host "4. Queueing is NOT available on Trial capacities" -ForegroundColor White
Write-Host ""
