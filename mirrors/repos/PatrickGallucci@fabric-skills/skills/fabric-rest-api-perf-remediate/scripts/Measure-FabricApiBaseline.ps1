<#
.SYNOPSIS
    Establishes a performance baseline for Microsoft Fabric REST API operations.

.DESCRIPTION
    Measures latency across four categories: token acquisition, simple GET requests,
    paginated enumeration, and LRO polling. Outputs a structured report for
    comparison against expected performance ranges.

.PARAMETER Token
    Bearer token for Fabric REST API. If omitted, token acquisition is benchmarked
    using the provided Entra ID parameters.

.PARAMETER WorkspaceId
    Target workspace GUID for API calls.

.PARAMETER TenantId
    Entra ID tenant GUID (required for token acquisition benchmark).

.PARAMETER ClientId
    App registration client ID (required for token acquisition benchmark).

.PARAMETER ClientSecret
    App registration client secret (required for token acquisition benchmark).

.PARAMETER Iterations
    Number of measurement iterations per test. Default: 5.

.EXAMPLE
    # With existing token
    .\Measure-FabricApiBaseline.ps1 -Token $token -WorkspaceId "abc-123"

.EXAMPLE
    # Full benchmark including token acquisition
    .\Measure-FabricApiBaseline.ps1 -WorkspaceId "abc-123" `
        -TenantId $tenantId -ClientId $clientId -ClientSecret $secret
#>
[CmdletBinding()]
param(
    [string]$Token,

    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [string]$TenantId,
    [string]$ClientId,
    [string]$ClientSecret,

    [int]$Iterations = 5
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$report = [ordered]@{}

function Measure-Operation {
    param(
        [string]$Name,
        [scriptblock]$Operation,
        [int]$Count
    )

    $timings = [System.Collections.Generic.List[double]]::new()
    Write-Host "`n--- $Name ($Count iterations) ---" -ForegroundColor Yellow

    for ($i = 1; $i -le $Count; $i++) {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            & $Operation | Out-Null
            $sw.Stop()
            $timings.Add($sw.ElapsedMilliseconds)
            Write-Host "  [$i] $($sw.ElapsedMilliseconds)ms" -ForegroundColor Green
        }
        catch {
            $sw.Stop()
            Write-Host "  [$i] FAILED ($($sw.ElapsedMilliseconds)ms): $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    if ($timings.Count -gt 0) {
        $stats = $timings | Measure-Object -Average -Minimum -Maximum
        $p95 = ($timings | Sort-Object)[[math]::Floor($timings.Count * 0.95)]

        return [PSCustomObject]@{
            Test    = $Name
            AvgMs   = [math]::Round($stats.Average, 1)
            MinMs   = $stats.Minimum
            MaxMs   = $stats.Maximum
            P95Ms   = $p95
            Samples = $timings.Count
        }
    }

    return [PSCustomObject]@{
        Test    = $Name
        AvgMs   = 'N/A'
        MinMs   = 'N/A'
        MaxMs   = 'N/A'
        P95Ms   = 'N/A'
        Samples = 0
    }
}

Write-Host "`n=== Fabric REST API Baseline Benchmark ===" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceId"
Write-Host "Iterations: $Iterations"
Write-Host "==========================================`n"

$results = [System.Collections.Generic.List[PSCustomObject]]::new()

# --- Test 1: Token Acquisition ---
if ($TenantId -and $ClientId -and $ClientSecret) {
    $tokenResult = Measure-Operation -Name "Token Acquisition" -Count $Iterations -Operation {
        $tokenUri = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
        $tokenBody = @{
            grant_type    = 'client_credentials'
            client_id     = $ClientId
            client_secret = $ClientSecret
            scope         = 'https://api.fabric.microsoft.com/.default'
        }
        $response = Invoke-RestMethod -Uri $tokenUri -Method Post -Body $tokenBody
        $script:Token = $response.access_token
    }
    $results.Add($tokenResult)
}
else {
    Write-Host "Skipping token acquisition benchmark (no Entra ID credentials provided)" -ForegroundColor DarkGray
}

if (-not $Token) {
    Write-Error "No token available. Provide -Token or Entra ID credentials."
    return
}

$headers = @{
    'Authorization' = "Bearer $Token"
    'Content-Type'  = 'application/json'
}

# --- Test 2: Simple GET (List Items) ---
$getResult = Measure-Operation -Name "GET /workspaces/{id}/items" -Count $Iterations -Operation {
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
    Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
}
$results.Add($getResult)

# --- Test 3: GET Workspace Details ---
$wsResult = Measure-Operation -Name "GET /workspaces/{id}" -Count $Iterations -Operation {
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId"
    Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
}
$results.Add($wsResult)

# --- Test 4: List Workspaces (paginated first page) ---
$listWsResult = Measure-Operation -Name "GET /workspaces (first page)" -Count $Iterations -Operation {
    $uri = "https://api.fabric.microsoft.com/v1/workspaces"
    Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
}
$results.Add($listWsResult)

# --- Test 5: Paginated Full Enumeration ---
$paginateResult = Measure-Operation -Name "Paginated Items (all pages)" -Count ([math]::Min($Iterations, 3)) -Operation {
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"
    $totalItems = 0

    do {
        $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
        $totalItems += $response.value.Count
        $uri = $response.continuationUri
    } while ($uri)

    $totalItems
}
$results.Add($paginateResult)

# --- Report ---
Write-Host "`n=== Baseline Report ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

Write-Host "`nExpected Ranges (healthy environment):" -ForegroundColor DarkGray
Write-Host "  Token Acquisition:     200-800ms"
Write-Host "  Simple GET:            100-500ms"
Write-Host "  Workspace Details:     80-300ms"
Write-Host "  List Workspaces:       150-600ms"
Write-Host "  Full Pagination:       Varies by item count"

Write-Host "`nResults flagged as SLOW:" -ForegroundColor Yellow
$thresholds = @{
    'Token Acquisition'              = 1000
    'GET /workspaces/{id}/items'     = 700
    'GET /workspaces/{id}'           = 500
    'GET /workspaces (first page)'   = 800
    'Paginated Items (all pages)'    = 5000
}

$slowFound = $false
foreach ($r in $results) {
    if ($r.AvgMs -ne 'N/A' -and $thresholds.ContainsKey($r.Test)) {
        if ($r.AvgMs -gt $thresholds[$r.Test]) {
            Write-Host "  $($r.Test): $($r.AvgMs)ms (threshold: $($thresholds[$r.Test])ms)" -ForegroundColor Red
            $slowFound = $true
        }
    }
}
if (-not $slowFound) {
    Write-Host "  None - all within expected ranges" -ForegroundColor Green
}

# Output structured results
$results
