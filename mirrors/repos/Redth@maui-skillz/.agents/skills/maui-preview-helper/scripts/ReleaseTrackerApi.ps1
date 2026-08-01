#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

# Public entry point for the .NET Release Tracker. Resolves in public DNS and
# fronts the API at /api/* through Azure Front Door.
$script:ReleaseTrackerBaseUri = "https://release.dot.net/api"

# Display name of the Azure AD app registration protecting the API. The resource
# id is resolved from this at runtime, so no tenant-specific GUID is checked in.
$script:ReleaseTrackerAppName = "ReleaseTracker"

$script:ReleaseTrackerResource = $null

function Get-ReleaseTrackerAccess {
    <#
    .SYNOPSIS
        Report whether the .NET Release Tracker API is usable by the current user.
    .DESCRIPTION
        The tracker is a Microsoft-internal service. This never throws, so callers
        can degrade to public release metadata instead of hard-failing for users
        outside the Microsoft tenant. Returns Available / Reason / Detail.
    #>
    [CmdletBinding()]
    param()

    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        return [pscustomobject]@{
            Available = $false
            Reason    = "NoAzCli"
            Detail    = "Azure CLI (az) is not installed."
        }
    }

    az account show --only-show-errors 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        return [pscustomobject]@{
            Available = $false
            Reason    = "NotSignedIn"
            Detail    = "Not signed in to Azure. Run 'az login'."
        }
    }

    if (-not $script:ReleaseTrackerResource) {
        # Sibling service principals share the name prefix but are managed identities
        # exposing https://identity.azure.net/... SPNs. The API is the one with api://.
        $resource = az ad sp list `
            --filter "displayName eq '$($script:ReleaseTrackerAppName)'" `
            --query "[].servicePrincipalNames[] | [?starts_with(@,'api://')] | [0]" `
            -o tsv --only-show-errors 2>$null

        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($resource)) {
            return [pscustomobject]@{
                Available = $false
                Reason    = "NoTenantAccess"
                Detail    = "Signed in, but the Release Tracker app registration isn't visible to this account. It is a Microsoft-internal service."
            }
        }

        $script:ReleaseTrackerResource = $resource
    }

    return [pscustomobject]@{ Available = $true; Reason = "Ok"; Detail = $null }
}

function Invoke-ReleaseTrackerRestMethod {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string] $Endpoint,
        [string] $Method = "GET",
        [hashtable] $Body
    )

    # Get an access token for the Release Tracker API.
    $access = Get-ReleaseTrackerAccess
    if (-not $access.Available) {
        throw "Release Tracker unavailable ($($access.Reason)): $($access.Detail)"
    }

    $token = az account get-access-token --resource $script:ReleaseTrackerResource --query accessToken -o tsv --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Release Tracker unavailable (NoToken): could not acquire a token for the current account."
    }

    # Put together the API request
    $headers = @{
        Authorization  = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $uri = "$($script:ReleaseTrackerBaseUri)/$($Endpoint)"

    $params = @{
        Uri     = $uri
        Headers = $headers
        Method  = $Method
    }

    if ($Body) {
        $params.Body = $Body | ConvertTo-Json -Depth 10
    }

    # Submit request
    return Invoke-RestMethod @params
}
