<#
.SYNOPSIS
    Measures OneLake cross-region access latency by performing HEAD requests
    against the OneLake DFS endpoint.

.DESCRIPTION
    Tests connectivity and response time to OneLake endpoints to help diagnose
    performance issues caused by cross-region data access. Compares latency
    across multiple requests to establish a baseline.

.PARAMETER OneLakePath
    The OneLake ABFSS path to test (e.g., "abfss://workspace@onelake.dfs.fabric.microsoft.com/lakehouse/Tables/my_table").

.PARAMETER Iterations
    Number of test requests to send (default: 10).

.EXAMPLE
    ./region-latency-test.ps1 -OneLakePath "abfss://ws-guid@onelake.dfs.fabric.microsoft.com/lh-guid/Tables/sales"

.NOTES
    Requires: PowerShell 7+, Az.Accounts module, authenticated to Azure.
    The OneLake DFS endpoint is onelake.dfs.fabric.microsoft.com.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$OneLakePath,

    [Parameter()]
    [ValidateRange(1, 100)]
    [int]$Iterations = 10
)

#Requires -Version 7.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-OneLakeToken {
    try {
        $tokenResponse = Get-AzAccessToken -ResourceUrl 'https://storage.azure.com' -ErrorAction Stop
        return $tokenResponse.Token
    }
    catch {
        Write-Error "Failed to get storage access token. Run Connect-AzAccount first. Error: $_"
        throw
    }
}

function Parse-AbfssPath {
    <#
    .SYNOPSIS
        Parses an ABFSS path into components for REST API calls.
    #>
    param([string]$Path)

    # abfss://container@account.dfs.fabric.microsoft.com/path
    if ($Path -match '^abfss://([^@]+)@([^/]+)/(.+)$') {
        return @{
            Container = $Matches[1]
            Account   = $Matches[2]
            FilePath  = $Matches[3]
        }
    }
    else {
        Write-Error "Invalid ABFSS path format. Expected: abfss://container@account.dfs.fabric.microsoft.com/path"
        throw
    }
}

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
Write-Host "`n=== OneLake Region Latency Test ===" -ForegroundColor Cyan
Write-Host "Path:       $OneLakePath" -ForegroundColor Gray
Write-Host "Iterations: $Iterations" -ForegroundColor Gray
Write-Host "Timestamp:  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)" -ForegroundColor Gray

$token = Get-OneLakeToken
$parsed = Parse-AbfssPath -Path $OneLakePath

$baseUrl = "https://$($parsed.Account)/$($parsed.Container)/$($parsed.FilePath)"
Write-Host "Target URL: $baseUrl" -ForegroundColor Gray

$headers = @{
    'Authorization'  = "Bearer $token"
    'x-ms-version'   = '2021-08-06'
}

$latencies = @()

Write-Host "`nRunning $Iterations latency tests..." -ForegroundColor Yellow

for ($i = 1; $i -le $Iterations; $i++) {
    $testUrl = "${baseUrl}?resource=filesystem&maxResults=1"
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $null = Invoke-WebRequest -Uri $testUrl -Headers $headers -Method Head -ErrorAction Stop
        $stopwatch.Stop()
        $latencyMs = $stopwatch.ElapsedMilliseconds
        $status = 'OK'
    }
    catch {
        $stopwatch.Stop()
        $latencyMs = $stopwatch.ElapsedMilliseconds
        $statusCode = $_.Exception.Response.StatusCode.value__
        $status = "HTTP $statusCode"
    }

    $latencies += $latencyMs
    $bar = '#' * [math]::Min(($latencyMs / 10), 50)
    Write-Host ("  [{0,3}] {1,6} ms  {2,-6} {3}" -f $i, $latencyMs, $status, $bar) -ForegroundColor White
    Start-Sleep -Milliseconds 200
}

# Calculate statistics
$sorted   = $latencies | Sort-Object
$minMs    = $sorted[0]
$maxMs    = $sorted[-1]
$avgMs    = [math]::Round(($latencies | Measure-Object -Average).Average, 1)
$medianMs = $sorted[[math]::Floor($sorted.Count / 2)]
$p95Index = [math]::Floor($sorted.Count * 0.95)
$p95Ms    = $sorted[[math]::Min($p95Index, $sorted.Count - 1)]

Write-Host "`n--- Latency Summary ---" -ForegroundColor Yellow
Write-Host "  Minimum:  $minMs ms" -ForegroundColor White
Write-Host "  Maximum:  $maxMs ms" -ForegroundColor White
Write-Host "  Average:  $avgMs ms" -ForegroundColor White
Write-Host "  Median:   $medianMs ms" -ForegroundColor White
Write-Host "  P95:      $p95Ms ms" -ForegroundColor White

Write-Host "`n--- Assessment ---" -ForegroundColor Yellow
if ($avgMs -lt 50) {
    Write-Host "  Excellent — Data appears to be in the same region as your client." -ForegroundColor Green
}
elseif ($avgMs -lt 150) {
    Write-Host "  Good — Latency is within acceptable range for most workloads." -ForegroundColor Green
}
elseif ($avgMs -lt 300) {
    Write-Host "  Warning — Moderate latency detected. Verify data and capacity are co-located." -ForegroundColor Yellow
}
else {
    Write-Host "  Critical — High latency detected. Data is likely in a different region." -ForegroundColor Red
    Write-Host "  Action: Move data to the same region as your Fabric capacity," -ForegroundColor Red
    Write-Host "          or keep only small dimension tables in the remote region." -ForegroundColor Red
}

Write-Host ""
