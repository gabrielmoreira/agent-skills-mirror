<#
.SYNOPSIS
    Tests connectivity and authentication to the Microsoft Fabric REST API.

.DESCRIPTION
    Performs a series of diagnostic checks against api.fabric.microsoft.com:
    1. DNS resolution
    2. HTTPS connectivity
    3. Token acquisition (interactive or service principal)
    4. API call to a specified endpoint
    5. Token validation (decodes and checks claims)

.PARAMETER TestEndpoint
    The Fabric API endpoint to test (relative to /v1/). Default: "workspaces"

.PARAMETER ClientId
    The Entra ID application (client) ID. If omitted, prompts for input.

.PARAMETER TenantId
    The Entra ID tenant ID. If omitted, uses "organizations" (multi-tenant).

.PARAMETER ClientSecret
    Client secret for service principal authentication. If omitted, uses interactive auth.

.PARAMETER Token
    Pre-acquired bearer token. If provided, skips token acquisition.

.PARAMETER Scopes
    OAuth scopes to request. Default: Workspace.ReadWrite.All, Item.ReadWrite.All

.EXAMPLE
    # Interactive authentication test
    ./Test-FabricApiConnection.ps1 -ClientId "your-app-id" -TestEndpoint "workspaces"

.EXAMPLE
    # Service principal test
    ./Test-FabricApiConnection.ps1 -ClientId "your-app-id" -TenantId "your-tenant" -ClientSecret "secret"

.EXAMPLE
    # Test with pre-acquired token
    ./Test-FabricApiConnection.ps1 -Token $myToken -TestEndpoint "workspaces"
#>
[CmdletBinding()]
param(
    [string]$TestEndpoint = "workspaces",
    [string]$ClientId,
    [string]$TenantId = "organizations",
    [string]$ClientSecret,
    [string]$Token,
    [string[]]$Scopes = @(
        "https://api.fabric.microsoft.com/Workspace.ReadWrite.All",
        "https://api.fabric.microsoft.com/Item.ReadWrite.All"
    )
)

$ErrorActionPreference = 'Stop'
$baseUrl = "https://api.fabric.microsoft.com/v1"
$results = @{}

function Write-DiagResult {
    param([string]$Test, [string]$Status, [string]$Detail)
    $color = switch ($Status) {
        'PASS' { 'Green' }
        'FAIL' { 'Red' }
        'WARN' { 'Yellow' }
        'INFO' { 'Cyan' }
    }
    Write-Host "[$Status] " -ForegroundColor $color -NoNewline
    Write-Host "$Test" -NoNewline
    if ($Detail) { Write-Host " - $Detail" } else { Write-Host "" }
    $results[$Test] = @{ Status = $Status; Detail = $Detail }
}

Write-Host ""
Write-Host "=== Microsoft Fabric REST API Connection Diagnostic ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC' -AsUTC)"
Write-Host "Target:    $baseUrl/$TestEndpoint"
Write-Host ""

# --- Test 1: DNS Resolution ---
Write-Host "--- Step 1: DNS Resolution ---" -ForegroundColor White
try {
    $dns = [System.Net.Dns]::GetHostAddresses("api.fabric.microsoft.com")
    Write-DiagResult "DNS Resolution" "PASS" "api.fabric.microsoft.com -> $($dns[0].IPAddressToString)"
}
catch {
    Write-DiagResult "DNS Resolution" "FAIL" "Cannot resolve api.fabric.microsoft.com: $($_.Exception.Message)"
    Write-Host "`nDNS resolution failed. Check your network/proxy settings." -ForegroundColor Red
    exit 1
}

# --- Test 2: HTTPS Connectivity ---
Write-Host "--- Step 2: HTTPS Connectivity ---" -ForegroundColor White
try {
    $tcpTest = Test-NetConnection -ComputerName "api.fabric.microsoft.com" -Port 443 -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-DiagResult "HTTPS Port 443" "PASS" "TCP connection successful"
    }
    else {
        Write-DiagResult "HTTPS Port 443" "FAIL" "TCP connection refused or timed out"
    }
}
catch {
    # Test-NetConnection may not be available on all systems
    try {
        $response = Invoke-WebRequest -Uri "https://api.fabric.microsoft.com/v1/" `
            -Method GET -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
        Write-DiagResult "HTTPS Connectivity" "PASS" "HTTP $($response.StatusCode)"
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-DiagResult "HTTPS Connectivity" "PASS" "HTTP $statusCode (expected for unauthenticated)"
        }
        else {
            Write-DiagResult "HTTPS Connectivity" "FAIL" $_.Exception.Message
        }
    }
}

# --- Test 3: Token Acquisition ---
Write-Host "--- Step 3: Token Acquisition ---" -ForegroundColor White

if ($Token) {
    Write-DiagResult "Token Source" "INFO" "Using pre-acquired token"
}
elseif ($ClientId -and $ClientSecret) {
    # Service principal flow
    Write-DiagResult "Auth Method" "INFO" "Service Principal (client credentials)"
    try {
        $body = @{
            grant_type    = "client_credentials"
            client_id     = $ClientId
            client_secret = $ClientSecret
            scope         = "https://api.fabric.microsoft.com/.default"
        }
        $tokenResponse = Invoke-RestMethod `
            -Method Post `
            -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" `
            -ContentType "application/x-www-form-urlencoded" `
            -Body $body
        $Token = $tokenResponse.access_token
        Write-DiagResult "Token Acquisition" "PASS" "Service principal token acquired (expires_in: $($tokenResponse.expires_in)s)"
    }
    catch {
        Write-DiagResult "Token Acquisition" "FAIL" $_.Exception.Message
        Write-Host "`nToken acquisition failed. Check ClientId, ClientSecret, and TenantId." -ForegroundColor Red
        exit 1
    }
}
elseif ($ClientId) {
    # Interactive flow
    Write-DiagResult "Auth Method" "INFO" "Interactive user authentication"
    try {
        if (Get-Module -ListAvailable -Name MSAL.PS) {
            Import-Module MSAL.PS
            $tokenResult = Get-MsalToken -ClientId $ClientId -TenantId $TenantId -Scopes $Scopes -Interactive
            $Token = $tokenResult.AccessToken
            Write-DiagResult "Token Acquisition" "PASS" "Interactive token acquired (expires: $($tokenResult.ExpiresOn))"
        }
        elseif (Get-Module -ListAvailable -Name Az.Accounts) {
            Connect-AzAccount -TenantId $TenantId | Out-Null
            $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
            $Token = $tokenResult.Token
            Write-DiagResult "Token Acquisition" "PASS" "Az.Accounts token acquired"
        }
        else {
            Write-DiagResult "Token Acquisition" "FAIL" "Install MSAL.PS or Az.Accounts module"
            exit 1
        }
    }
    catch {
        Write-DiagResult "Token Acquisition" "FAIL" $_.Exception.Message
        exit 1
    }
}
else {
    Write-DiagResult "Token" "WARN" "No ClientId or Token provided. Skipping authenticated tests."
    Write-Host "`nUsage: ./Test-FabricApiConnection.ps1 -ClientId <app-id> [-TenantId <tenant>] [-ClientSecret <secret>]" -ForegroundColor Yellow
    Write-Host "   or: ./Test-FabricApiConnection.ps1 -Token <bearer-token>" -ForegroundColor Yellow
    exit 0
}

# --- Test 4: Token Validation ---
Write-Host "--- Step 4: Token Validation ---" -ForegroundColor White
try {
    $parts = $Token.Split('.')
    $payload = $parts[1]
    $padding = 4 - ($payload.Length % 4)
    if ($padding -lt 4) { $payload += '=' * $padding }
    $decoded = [System.Text.Encoding]::UTF8.GetString(
        [System.Convert]::FromBase64String($payload)
    ) | ConvertFrom-Json

    $expiry = [DateTimeOffset]::FromUnixTimeSeconds($decoded.exp).UtcDateTime
    $now = [DateTime]::UtcNow

    if ($expiry -gt $now) {
        Write-DiagResult "Token Expiry" "PASS" "Expires: $($expiry.ToString('yyyy-MM-dd HH:mm:ss')) UTC ($(($expiry - $now).TotalMinutes.ToString('N0')) min remaining)"
    }
    else {
        Write-DiagResult "Token Expiry" "FAIL" "Token EXPIRED at $($expiry.ToString('yyyy-MM-dd HH:mm:ss')) UTC"
    }

    if ($decoded.aud -like "*api.fabric.microsoft.com*") {
        Write-DiagResult "Token Audience" "PASS" "aud: $($decoded.aud)"
    }
    else {
        Write-DiagResult "Token Audience" "FAIL" "aud: $($decoded.aud) (expected: https://api.fabric.microsoft.com)"
    }

    $scopeClaim = if ($decoded.scp) { $decoded.scp } elseif ($decoded.roles) { $decoded.roles -join ', ' } else { '(none)' }
    Write-DiagResult "Token Scopes" "INFO" $scopeClaim
    Write-DiagResult "Token Tenant" "INFO" "tid: $($decoded.tid)"
    Write-DiagResult "Token App" "INFO" "appid: $($decoded.appid ?? $decoded.azp ?? 'N/A')"
}
catch {
    Write-DiagResult "Token Decode" "WARN" "Could not decode token: $($_.Exception.Message)"
}

# --- Test 5: API Call ---
Write-Host "--- Step 5: API Call ---" -ForegroundColor White
$uri = "$baseUrl/$($TestEndpoint.TrimStart('/'))"
try {
    $headers = @{ Authorization = "Bearer $Token" }
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    $itemCount = if ($response.value) { $response.value.Count } else { "N/A" }
    Write-DiagResult "API Call ($TestEndpoint)" "PASS" "HTTP 200 - Items returned: $itemCount"
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorBody = $null
    try {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $errorBody = $reader.ReadToEnd() | ConvertFrom-Json
    }
    catch { }

    if ($errorBody) {
        Write-DiagResult "API Call ($TestEndpoint)" "FAIL" "HTTP $statusCode - errorCode: $($errorBody.errorCode) - $($errorBody.message)"
        if ($errorBody.requestId) {
            Write-DiagResult "Request ID" "INFO" $errorBody.requestId
        }
    }
    else {
        Write-DiagResult "API Call ($TestEndpoint)" "FAIL" "HTTP $statusCode - $($_.Exception.Message)"
    }
}

# --- Summary ---
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
$pass = ($results.Values | Where-Object { $_.Status -eq 'PASS' }).Count
$fail = ($results.Values | Where-Object { $_.Status -eq 'FAIL' }).Count
$warn = ($results.Values | Where-Object { $_.Status -eq 'WARN' }).Count
Write-Host "PASS: $pass  FAIL: $fail  WARN: $warn" -ForegroundColor $(if ($fail -gt 0) { 'Red' } elseif ($warn -gt 0) { 'Yellow' } else { 'Green' })
