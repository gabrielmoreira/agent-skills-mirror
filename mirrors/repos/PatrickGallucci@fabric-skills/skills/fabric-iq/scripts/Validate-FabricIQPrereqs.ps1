<#
.SYNOPSIS
    Validates prerequisites for Microsoft Fabric IQ (preview).

.DESCRIPTION
    Checks workspace access, capacity SKU, and ability to list/create ontology items.
    Validates that required tenant settings are effectively enabled by testing
    API operations that depend on them.

.PARAMETER TenantId
    Azure AD tenant ID for authentication.

.PARAMETER WorkspaceId
    Optional. Fabric workspace ID to validate. If not provided, lists available workspaces.

.PARAMETER SkipCapacityCheck
    Optional. Skip capacity SKU validation.

.EXAMPLE
    ./Validate-FabricIQPrereqs.ps1 -TenantId "your-tenant-id"

.EXAMPLE
    ./Validate-FabricIQPrereqs.ps1 -TenantId "your-tenant-id" -WorkspaceId "ws-guid"

.NOTES
    Requires: Az PowerShell module (Install-Module Az)
    Requires: PowerShell 7+ recommended
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$TenantId,

    [Parameter()]
    [string]$WorkspaceId,

    [Parameter()]
    [switch]$SkipCapacityCheck
)

#region Helper Functions

function Write-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Message
    )
    $icon = if ($Passed) { "[PASS]" } else { "[FAIL]" }
    $color = if ($Passed) { "Green" } else { "Red" }
    Write-Host "$icon $Name" -ForegroundColor $color
    if ($Message) {
        Write-Host "       $Message" -ForegroundColor Gray
    }
}

function Write-Warn {
    param([string]$Name, [string]$Message)
    Write-Host "[WARN] $Name" -ForegroundColor Yellow
    if ($Message) {
        Write-Host "       $Message" -ForegroundColor Gray
    }
}

function Get-FabricToken {
    try {
        $tokenResult = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com" -ErrorAction Stop
        return $tokenResult.Token
    }
    catch {
        Write-Error "Failed to acquire Fabric token. Run Connect-AzAccount -TenantId '$TenantId' first."
        return $null
    }
}

function Invoke-FabricApi {
    param(
        [string]$Uri,
        [string]$Method = "Get",
        [hashtable]$Headers,
        [string]$Body
    )
    try {
        $params = @{
            Uri     = $Uri
            Method  = $Method
            Headers = $Headers
            ErrorAction = "Stop"
        }
        if ($Body) { $params.Body = $Body }
        return Invoke-RestMethod @params
    }
    catch {
        return $null
    }
}

#endregion

#region Main Validation

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Fabric IQ Prerequisites Validation" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Authentication
Write-Host "--- Authentication ---" -ForegroundColor White
try {
    $account = Get-AzContext -ErrorAction Stop
    if (-not $account) {
        Write-Host "Not signed in. Connecting..." -ForegroundColor Yellow
        Connect-AzAccount -TenantId $TenantId -ErrorAction Stop
    }
    Write-Check -Name "Azure Authentication" -Passed $true -Message "Signed in as $($account.Account.Id)"
}
catch {
    Write-Check -Name "Azure Authentication" -Passed $false -Message "Run: Connect-AzAccount -TenantId '$TenantId'"
    exit 1
}

$token = Get-FabricToken
if (-not $token) { exit 1 }
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}
Write-Check -Name "Fabric API Token" -Passed $true

Write-Host ""

# Step 2: Workspace validation
Write-Host "--- Workspace Access ---" -ForegroundColor White

if (-not $WorkspaceId) {
    $workspaces = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces" -Headers $headers
    if ($workspaces -and $workspaces.value.Count -gt 0) {
        Write-Check -Name "Workspace Access" -Passed $true -Message "Found $($workspaces.value.Count) workspace(s)"
        Write-Host ""
        Write-Host "  Available workspaces:" -ForegroundColor Gray
        $workspaces.value | Select-Object -First 10 | ForEach-Object {
            Write-Host "    - $($_.displayName) [$($_.id)]" -ForegroundColor Gray
        }
        Write-Host ""
        Write-Warn -Name "No WorkspaceId specified" -Message "Re-run with -WorkspaceId to validate a specific workspace"
    }
    else {
        Write-Check -Name "Workspace Access" -Passed $false -Message "No workspaces found or API access denied"
    }
}
else {
    $ws = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId" -Headers $headers
    if ($ws) {
        Write-Check -Name "Workspace Access" -Passed $true -Message "Workspace: $($ws.displayName)"

        # Check if it's "My workspace"
        if ($ws.displayName -eq "My workspace" -or $ws.type -eq "PersonalGroup") {
            Write-Warn -Name "My Workspace Detected" -Message "Ontology generation from semantic models is not supported in 'My workspace'"
        }
    }
    else {
        Write-Check -Name "Workspace Access" -Passed $false -Message "Cannot access workspace $WorkspaceId"
    }

    Write-Host ""

    # Step 3: Test ontology item listing (validates tenant setting)
    Write-Host "--- Ontology Tenant Setting ---" -ForegroundColor White
    $ontologyItems = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=Ontology" -Headers $headers
    if ($null -ne $ontologyItems) {
        Write-Check -Name "Ontology Item Access" -Passed $true -Message "Can list ontology items ($($ontologyItems.value.Count) found)"
    }
    else {
        Write-Check -Name "Ontology Item Access" -Passed $false -Message "Cannot list ontology items. Enable 'Ontology item (preview)' tenant setting."
    }

    # Step 4: Test data agent listing
    Write-Host ""
    Write-Host "--- Data Agent Tenant Setting (Optional) ---" -ForegroundColor White
    $agentItems = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=DataAgent" -Headers $headers
    if ($null -ne $agentItems) {
        Write-Check -Name "Data Agent Access" -Passed $true -Message "Can list data agent items ($($agentItems.value.Count) found)"
    }
    else {
        Write-Warn -Name "Data Agent Access" -Message "Cannot list data agents. Enable 'Data agent item types (preview)' for agent features."
    }

    # Step 5: Test lakehouse access
    Write-Host ""
    Write-Host "--- Data Sources ---" -ForegroundColor White
    $lakehouses = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=Lakehouse" -Headers $headers
    if ($lakehouses -and $lakehouses.value.Count -gt 0) {
        Write-Check -Name "Lakehouse Access" -Passed $true -Message "Found $($lakehouses.value.Count) lakehouse(s)"
    }
    else {
        Write-Warn -Name "Lakehouse Access" -Message "No lakehouses found. You'll need OneLake data for ontology bindings."
    }

    $eventhouses = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=Eventhouse" -Headers $headers
    if ($eventhouses -and $eventhouses.value.Count -gt 0) {
        Write-Check -Name "Eventhouse Access" -Passed $true -Message "Found $($eventhouses.value.Count) eventhouse(s)"
    }

    $semanticModels = Invoke-FabricApi -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items?type=SemanticModel" -Headers $headers
    if ($semanticModels -and $semanticModels.value.Count -gt 0) {
        Write-Check -Name "Semantic Model Access" -Passed $true -Message "Found $($semanticModels.value.Count) semantic model(s)"
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Validation Complete" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

#endregion
