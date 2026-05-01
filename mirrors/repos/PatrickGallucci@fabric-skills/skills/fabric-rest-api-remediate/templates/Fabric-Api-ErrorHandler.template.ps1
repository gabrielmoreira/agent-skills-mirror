<#
.SYNOPSIS
    Template: Fabric REST API error handling scaffold.
    Customize this file for your specific Fabric API integration.

.DESCRIPTION
    Provides a structured error handling pattern for Microsoft Fabric REST API calls.
    The AI agent will modify this template to fit your specific use case:
    - Insert your workspace/item IDs
    - Add your specific API endpoints
    - Customize retry behavior
    - Add your logging/alerting integration

.NOTES
    This is a TEMPLATE file. The AI agent will customize it based on your requirements.
    See SKILL.md for full remediate workflows.
#>

#region === CONFIGURATION (Customize for your environment) ===

$FabricConfig = @{
    BaseUrl       = "https://api.fabric.microsoft.com/v1"
    WorkspaceId   = "YOUR-WORKSPACE-ID"     # Replace with your workspace GUID
    MaxRetries    = 5
    BaseDelaySec  = 2
    MaxDelaySec   = 120
    TimeoutSec    = 300
}

#endregion

#region === TOKEN MANAGEMENT ===

function Get-FabricToken {
    <#
    .SYNOPSIS
        Acquire a fresh Fabric API token.
        TODO: Implement your preferred authentication method.
    #>
    [CmdletBinding()]
    param()

    # Option A: Interactive (for development)
    # $result = Get-MsalToken -ClientId $clientId -TenantId $tenantId `
    #     -Scopes @("https://api.fabric.microsoft.com/.default") -Interactive
    # return $result.AccessToken

    # Option B: Service Principal (for automation)
    # $body = @{
    #     grant_type    = "client_credentials"
    #     client_id     = $env:FABRIC_CLIENT_ID
    #     client_secret = $env:FABRIC_CLIENT_SECRET
    #     scope         = "https://api.fabric.microsoft.com/.default"
    # }
    # $response = Invoke-RestMethod -Method Post `
    #     -Uri "https://login.microsoftonline.com/$env:FABRIC_TENANT_ID/oauth2/v2.0/token" `
    #     -ContentType "application/x-www-form-urlencoded" -Body $body
    # return $response.access_token

    # Option C: Az.Accounts (if already connected)
    # $result = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
    # return $result.Token

    throw "TODO: Implement token acquisition for your environment"
}

#endregion

#region === ERROR HANDLING ===

function Invoke-FabricApi {
    <#
    .SYNOPSIS
        Call a Fabric REST API with structured error handling.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Endpoint,

        [ValidateSet('GET', 'POST', 'PUT', 'PATCH', 'DELETE')]
        [string]$Method = 'GET',

        [object]$Body,

        [string]$Token
    )

    if (-not $Token) {
        $Token = Get-FabricToken
    }

    $uri = "$($FabricConfig.BaseUrl)/$($Endpoint.TrimStart('/'))"
    $headers = @{
        Authorization  = "Bearer $Token"
        'Content-Type' = 'application/json'
    }

    for ($attempt = 0; $attempt -le $FabricConfig.MaxRetries; $attempt++) {
        try {
            $params = @{
                Uri     = $uri
                Method  = $Method
                Headers = $headers
            }
            if ($Body -and $Method -ne 'GET') {
                $params.Body = if ($Body -is [string]) { $Body } else { $Body | ConvertTo-Json -Depth 10 }
            }

            $response = Invoke-WebRequest @params -UseBasicParsing
            return ($response.Content | ConvertFrom-Json)
        }
        catch {
            $handled = Handle-FabricApiError -Exception $_ -Attempt $attempt -MaxRetries $FabricConfig.MaxRetries
            if (-not $handled) { throw }

            # If 401, try refreshing token
            $statusCode = [int]$_.Exception.Response.StatusCode
            if ($statusCode -eq 401) {
                try {
                    $Token = Get-FabricToken
                    $headers.Authorization = "Bearer $Token"
                }
                catch {
                    Write-Error "Token refresh failed: $($_.Exception.Message)"
                    throw
                }
            }
        }
    }

    throw "Exhausted all retries for: $Method $uri"
}

function Handle-FabricApiError {
    <#
    .SYNOPSIS
        Process a Fabric API error and decide whether to retry.
        Returns $true if the caller should retry, $false to throw.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        $Exception,

        [int]$Attempt,

        [int]$MaxRetries
    )

    $statusCode = $null
    $errorCode = $null
    $message = $null
    $requestId = $null
    $retryAfter = 0

    # Extract error details
    if ($Exception.Exception.Response) {
        $statusCode = [int]$Exception.Exception.Response.StatusCode

        try {
            $retryAfterHeader = $Exception.Exception.Response.Headers | Where-Object { $_.Key -eq 'Retry-After' }
            if ($retryAfterHeader) { $retryAfter = [int]$retryAfterHeader.Value[0] }
        }
        catch { }

        try {
            $stream = $Exception.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $errorBody = $reader.ReadToEnd() | ConvertFrom-Json
            $errorCode = $errorBody.errorCode
            $message = $errorBody.message
            $requestId = $errorBody.requestId
        }
        catch { }
    }

    # === ERROR ROUTING ===
    # TODO: Add your logging/alerting integration here

    switch ($statusCode) {
        401 {
            # Token expired or insufficient scopes
            Write-Warning "HTTP 401 ($errorCode): $message"
            if ($Attempt -lt $MaxRetries) {
                Write-Warning "  -> Attempting token refresh..."
                return $true  # Signal caller to refresh and retry
            }
            # TODO: Alert on persistent auth failures
            return $false
        }

        403 {
            # Permission denied - not retryable
            Write-Error "HTTP 403 ($errorCode): $message"
            Write-Error "  -> Check workspace role and API identity support"
            if ($requestId) { Write-Error "  -> requestId: $requestId" }
            # TODO: Alert on permission failures
            return $false
        }

        404 {
            # Resource not found - not retryable
            Write-Error "HTTP 404 ($errorCode): $message"
            Write-Error "  -> Verify workspace/item GUIDs"
            if ($requestId) { Write-Error "  -> requestId: $requestId" }
            return $false
        }

        429 {
            # Throttling - retryable with Retry-After
            if ($Attempt -lt $MaxRetries) {
                $delay = if ($retryAfter -gt 0) { $retryAfter } else { 60 }
                Write-Warning "HTTP 429: Throttled. Waiting ${delay}s (attempt $($Attempt + 1)/$($MaxRetries + 1))..."
                Start-Sleep -Seconds $delay
                return $true
            }
            Write-Error "HTTP 429: Throttling persists after $MaxRetries retries"
            # TODO: Alert on persistent throttling
            return $false
        }

        { $_ -in @(500, 502, 503, 504) } {
            # Server error - retryable with backoff
            if ($Attempt -lt $MaxRetries) {
                $delay = [Math]::Min(
                    [Math]::Pow(2, $Attempt) * $FabricConfig.BaseDelaySec * (Get-Random -Minimum 0.5 -Maximum 1.5),
                    $FabricConfig.MaxDelaySec
                )
                Write-Warning "HTTP ${statusCode}: Server error. Retrying in ${delay}s (attempt $($Attempt + 1)/$($MaxRetries + 1))..."
                if ($requestId) { Write-Verbose "  requestId: $requestId" }
                Start-Sleep -Seconds ([int]$delay)
                return $true
            }
            Write-Error "HTTP ${statusCode}: Server error persists after $MaxRetries retries"
            if ($requestId) { Write-Error "  -> requestId for support: $requestId" }
            # TODO: Alert on persistent server errors
            return $false
        }

        default {
            # Unknown or non-retryable error
            Write-Error "HTTP ${statusCode}: $errorCode - $message"
            if ($requestId) { Write-Error "  -> requestId: $requestId" }
            return $false
        }
    }
}

#endregion

#region === USAGE EXAMPLES (Uncomment and customize) ===

# # List workspaces
# $workspaces = Invoke-FabricApi -Endpoint "workspaces"
# $workspaces.value | Select-Object id, displayName

# # List items in a workspace
# $items = Invoke-FabricApi -Endpoint "workspaces/$($FabricConfig.WorkspaceId)/items"
# $items.value | Select-Object id, displayName, type

# # Create a lakehouse
# $lakehouse = Invoke-FabricApi `
#     -Endpoint "workspaces/$($FabricConfig.WorkspaceId)/lakehouses" `
#     -Method POST `
#     -Body @{ displayName = "MyLakehouse" }

# # Paginated retrieval
# $allItems = @()
# $endpoint = "workspaces/$($FabricConfig.WorkspaceId)/items"
# do {
#     $page = Invoke-FabricApi -Endpoint $endpoint
#     $allItems += $page.value
#     if ($page.continuationToken) {
#         $endpoint = "workspaces/$($FabricConfig.WorkspaceId)/items?continuationToken=$($page.continuationToken)"
#     } else {
#         $endpoint = $null
#     }
# } while ($endpoint)

#endregion
