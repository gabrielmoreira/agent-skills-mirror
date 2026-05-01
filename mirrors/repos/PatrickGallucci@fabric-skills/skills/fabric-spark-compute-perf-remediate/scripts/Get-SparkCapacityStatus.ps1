<#
.SYNOPSIS
    Checks Microsoft Fabric Spark capacity utilization and queue status.

.DESCRIPTION
    Queries the Fabric Admin API to retrieve capacity metrics and provides
    guidance on whether the current SKU is appropriately sized for the workload.

.PARAMETER CapacityId
    The GUID of the Fabric capacity to check.

.PARAMETER AccessToken
    A valid Microsoft Entra bearer token for the Fabric Admin API.

.EXAMPLE
    ./Get-SparkCapacityStatus.ps1 -CapacityId "abc-123"

.NOTES
    Requires PowerShell 7+ and Fabric Admin or Capacity Admin permissions.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$CapacityId,

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
        Write-Error 'No AccessToken provided and Az.Accounts token acquisition failed.'
        return
    }
}
#endregion

$headers = @{
    'Authorization' = "Bearer $AccessToken"
    'Content-Type'  = 'application/json'
}

#region SKU Reference Data
$skuLimits = @{
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
#endregion

#region Get Capacity Info
Write-Host "`n=== Fabric Spark Capacity Status ===" -ForegroundColor Cyan
Write-Host "Capacity ID : $CapacityId"
Write-Host "Timestamp   : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)`n"

try {
    $capacityUri = "https://api.fabric.microsoft.com/v1/admin/capacities/$CapacityId"
    $capacity = Invoke-RestMethod -Uri $capacityUri -Headers $headers -Method GET

    $skuName = $capacity.sku
    $displayName = $capacity.displayName
    $state = $capacity.state
    $region = $capacity.region

    Write-Host "Capacity Name : $displayName"
    Write-Host "SKU           : $skuName"
    Write-Host "State         : $state"
    Write-Host "Region        : $region"

    if ($skuLimits.ContainsKey($skuName)) {
        $limits = $skuLimits[$skuName]
        Write-Host "Spark VCores  : $($limits.VCores)"
        Write-Host "Queue Limit   : $($limits.QueueLimit)"
    }
    else {
        Write-Host "SKU '$skuName' not in reference table. Check Fabric documentation." -ForegroundColor Yellow
    }
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 403) {
        Write-Warning 'Access denied. This endpoint requires Fabric Admin or Capacity Admin permissions.'
    }
    else {
        Write-Warning "Failed to retrieve capacity info ($statusCode): $($_.ErrorDetails.Message)"
    }
}
#endregion

#region Recommendations
Write-Host "`n=== Recommendations ===" -ForegroundColor Cyan

if ($skuLimits.ContainsKey($skuName)) {
    $limits = $skuLimits[$skuName]
    $ql = $limits.QueueLimit

    Write-Host @"

Queue Limit for $skuName is $ql concurrent Spark jobs.

If you are experiencing HTTP 430 (TooManyRequestsForCapacity) errors:

  1. Check Monitoring Hub for idle sessions and cancel them
  2. Stagger scheduled job start times
  3. Reduce pipeline ForEach parallelism
  4. Enable High Concurrency mode to share sessions
  5. Scale to a larger SKU if consistently at capacity

Next SKU options:
"@

    $skuOrder = @('F2','F4','F8','F16','F32','F64','F128','F256','F512','F1024','F2048')
    $currentIdx = $skuOrder.IndexOf($skuName)

    if ($currentIdx -lt ($skuOrder.Count - 1)) {
        $nextSku = $skuOrder[$currentIdx + 1]
        $nextLimits = $skuLimits[$nextSku]
        Write-Host "  $nextSku -> $($nextLimits.QueueLimit) queue slots, $($nextLimits.VCores) VCores" -ForegroundColor Green
    }

    if ($currentIdx -lt ($skuOrder.Count - 2)) {
        $skipSku = $skuOrder[$currentIdx + 2]
        $skipLimits = $skuLimits[$skipSku]
        Write-Host "  $skipSku -> $($skipLimits.QueueLimit) queue slots, $($skipLimits.VCores) VCores" -ForegroundColor Green
    }
}

Write-Host "`n=== Status Check Complete ===" -ForegroundColor Cyan
#endregion
