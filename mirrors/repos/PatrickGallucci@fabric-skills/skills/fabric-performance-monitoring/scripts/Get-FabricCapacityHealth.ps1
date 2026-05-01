<#
.SYNOPSIS
    Retrieves Microsoft Fabric capacity health status and key metrics.

.DESCRIPTION
    Queries the Azure Resource Manager REST API to get Fabric capacity details
    including SKU, state, provisioning status, and administration members.
    Useful for quick capacity health checks and inventory audits.

.PARAMETER SubscriptionId
    The Azure subscription ID containing the Fabric capacity.

.PARAMETER ResourceGroupName
    The resource group name containing the Fabric capacity.

.PARAMETER CapacityName
    The name of the Fabric capacity to check. If omitted, lists all capacities
    in the resource group.

.EXAMPLE
    ./Get-FabricCapacityHealth.ps1 -SubscriptionId "xxxxxxxx" -ResourceGroupName "rg-fabric" -CapacityName "fabriccap01"

.EXAMPLE
    ./Get-FabricCapacityHealth.ps1 -SubscriptionId "xxxxxxxx" -ResourceGroupName "rg-fabric"

.NOTES
    Requires: Az.Fabric module or Az.Accounts for authentication
    API Version: 2023-11-01
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SubscriptionId,

    [Parameter(Mandatory)]
    [string]$ResourceGroupName,

    [Parameter()]
    [string]$CapacityName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region Authentication
try {
    $context = Get-AzContext
    if (-not $context) {
        Write-Host "Not logged in to Azure. Running Connect-AzAccount..." -ForegroundColor Yellow
        Connect-AzAccount | Out-Null
        $context = Get-AzContext
    }
    $token = (Get-AzAccessToken -ResourceUrl 'https://management.azure.com').Token
}
catch {
    Write-Error "Authentication failed. Ensure Az.Accounts module is installed and you are logged in. Error: $_"
    exit 1
}
#endregion

#region API Call
$apiVersion = '2023-11-01'
$baseUri = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Fabric/capacities"

if ($CapacityName) {
    $uri = "$baseUri/$($CapacityName)?api-version=$apiVersion"
}
else {
    $uri = "$baseUri`?api-version=$apiVersion"
}

$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}

try {
    $response = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Error "API request failed with status $statusCode. Error: $_"
    exit 1
}
#endregion

#region Format Output
function Format-CapacityInfo {
    param([PSObject]$Capacity)

    $sku = $Capacity.sku.name
    $skuTier = $Capacity.sku.tier
    $state = $Capacity.properties.state
    $provisioningState = $Capacity.properties.provisioningState
    $admins = ($Capacity.properties.administration.members -join ', ')

    # Calculate Spark VCores from SKU
    $skuNumber = [int]($sku -replace '[^0-9]', '')
    $sparkVCores = $skuNumber * 2

    [PSCustomObject]@{
        Name              = $Capacity.name
        Location          = $Capacity.location
        SKU               = $sku
        Tier              = $skuTier
        State             = $state
        ProvisioningState = $provisioningState
        SparkVCores       = $sparkVCores
        QueueLimit        = [math]::Min($skuNumber, 2048)
        Administrators    = $admins
        ResourceId        = $Capacity.id
    }
}

if ($CapacityName) {
    $result = Format-CapacityInfo -Capacity $response
    Write-Host "`n=== Fabric Capacity Health Check ===" -ForegroundColor Cyan
    $result | Format-List
}
else {
    $capacities = $response.value
    if ($capacities.Count -eq 0) {
        Write-Host "No Fabric capacities found in resource group '$ResourceGroupName'." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "`n=== Fabric Capacities in '$ResourceGroupName' ===" -ForegroundColor Cyan
    $results = $capacities | ForEach-Object { Format-CapacityInfo -Capacity $_ }
    $results | Format-Table Name, SKU, State, SparkVCores, QueueLimit, Location -AutoSize
}
#endregion

Write-Host "`nHealth check complete." -ForegroundColor Green
