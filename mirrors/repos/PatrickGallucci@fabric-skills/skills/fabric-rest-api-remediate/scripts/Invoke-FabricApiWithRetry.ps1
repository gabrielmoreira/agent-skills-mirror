<#
.SYNOPSIS
    Invokes a Microsoft Fabric REST API call with automatic retry and exponential backoff.

.DESCRIPTION
    Wraps Invoke-RestMethod with:
    - Automatic retry on HTTP 429 (throttling) honoring Retry-After header
    - Exponential backoff with jitter on transient 5xx errors
    - Token refresh callback support for long-running pagination
    - Detailed logging of retry attempts

.PARAMETER Uri
    The full Fabric API URI to call.

.PARAMETER Token
    The bearer token for authentication.

.PARAMETER Method
    HTTP method. Default: GET

.PARAMETER Body
    Request body (for POST/PUT/PATCH).

.PARAMETER MaxRetries
    Maximum number of retry attempts. Default: 5

.PARAMETER BaseDelaySeconds
    Base delay for exponential backoff. Default: 2

.PARAMETER MaxDelaySeconds
    Maximum delay cap. Default: 120

.PARAMETER TokenRefreshScript
    Optional ScriptBlock that returns a fresh token. Called on 401 during retries.

.EXAMPLE
    # Simple GET with retry
    $result = ./Invoke-FabricApiWithRetry.ps1 `
        -Uri "https://api.fabric.microsoft.com/v1/workspaces" `
        -Token $token

.EXAMPLE
    # POST with body and token refresh
    $result = ./Invoke-FabricApiWithRetry.ps1 `
        -Uri "https://api.fabric.microsoft.com/v1/workspaces/$wsId/items" `
        -Token $token `
        -Method POST `
        -Body '{"displayName":"MyItem","type":"Notebook"}' `
        -TokenRefreshScript { Get-FreshToken }

.EXAMPLE
    # Paginated retrieval with retry on each page
    $allItems = @()
    $uri = "https://api.fabric.microsoft.com/v1/workspaces/$wsId/items"
    do {
        $page = ./Invoke-FabricApiWithRetry.ps1 -Uri $uri -Token $token
        $allItems += $page.value
        $uri = $page.continuationUri
    } while ($uri)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Uri,

    [Parameter(Mandatory)]
    [string]$Token,

    [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
    [string]$Method = 'GET',

    [string]$Body,

    [int]$MaxRetries = 5,

    [int]$BaseDelaySeconds = 2,

    [int]$MaxDelaySeconds = 120,

    [ScriptBlock]$TokenRefreshScript
)

$ErrorActionPreference = 'Stop'

function Get-RetryDelay {
    param([int]$Attempt, [int]$BaseDelay, [int]$MaxDelay, [int]$RetryAfterSeconds)

    if ($RetryAfterSeconds -gt 0) {
        return $RetryAfterSeconds
    }

    # Exponential backoff with jitter
    $exponential = [Math]::Pow(2, $Attempt) * $BaseDelay
    $jitter = Get-Random -Minimum 0.5 -Maximum 1.5
    $delay = [Math]::Min($exponential * $jitter, $MaxDelay)
    return [int]$delay
}

function Test-RetryableStatus {
    param([int]$StatusCode)
    return $StatusCode -in @(429, 500, 502, 503, 504)
}

$currentToken = $Token

for ($attempt = 0; $attempt -le $MaxRetries; $attempt++) {
    try {
        $headers = @{
            Authorization  = "Bearer $currentToken"
            'Content-Type' = 'application/json'
        }

        $params = @{
            Uri                = $Uri
            Method             = $Method
            Headers            = $headers
            UseBasicParsing    = $true
        }

        if ($Body -and $Method -ne 'GET') {
            $params.Body = $Body
        }

        # Use Invoke-WebRequest to access response headers
        $response = Invoke-WebRequest @params
        $content = $response.Content | ConvertFrom-Json

        if ($attempt -gt 0) {
            Write-Verbose "Request succeeded after $attempt retry(ies)"
        }

        return $content
    }
    catch {
        $statusCode = $null
        $retryAfter = 0
        $errorBody = $null

        # Extract status code
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode

            # Extract Retry-After header
            $retryAfterHeader = $_.Exception.Response.Headers | Where-Object { $_.Key -eq 'Retry-After' }
            if ($retryAfterHeader) {
                $retryAfter = [int]$retryAfterHeader.Value[0]
            }

            # Extract error body
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($stream)
                $errorBody = $reader.ReadToEnd() | ConvertFrom-Json
            }
            catch { }
        }

        # Handle 401 with token refresh
        if ($statusCode -eq 401 -and $TokenRefreshScript -and $attempt -lt $MaxRetries) {
            Write-Warning "HTTP 401 on attempt $($attempt + 1). Refreshing token..."
            try {
                $currentToken = & $TokenRefreshScript
                Write-Verbose "Token refreshed successfully"
                continue
            }
            catch {
                Write-Error "Token refresh failed: $($_.Exception.Message)"
                throw
            }
        }

        # Check if retryable
        if ($statusCode -and (Test-RetryableStatus $statusCode) -and $attempt -lt $MaxRetries) {
            $delay = Get-RetryDelay -Attempt $attempt -BaseDelay $BaseDelaySeconds `
                -MaxDelay $MaxDelaySeconds -RetryAfterSeconds $retryAfter

            $errorCode = if ($errorBody.errorCode) { " ($($errorBody.errorCode))" } else { "" }
            Write-Warning "HTTP $statusCode$errorCode on attempt $($attempt + 1)/$($MaxRetries + 1). Retrying in ${delay}s..."

            if ($errorBody.requestId) {
                Write-Verbose "requestId: $($errorBody.requestId)"
            }

            Start-Sleep -Seconds $delay
            continue
        }

        # Non-retryable or exhausted retries
        if ($errorBody) {
            $errMsg = "Fabric API error: HTTP $statusCode - $($errorBody.errorCode): $($errorBody.message)"
            if ($errorBody.requestId) {
                $errMsg += " (requestId: $($errorBody.requestId))"
            }
            Write-Error $errMsg
        }
        else {
            Write-Error "Fabric API error: HTTP $statusCode - $($_.Exception.Message)"
        }

        throw
    }
}

Write-Error "Exhausted all $MaxRetries retries for $Uri"
throw "Max retries exceeded"
