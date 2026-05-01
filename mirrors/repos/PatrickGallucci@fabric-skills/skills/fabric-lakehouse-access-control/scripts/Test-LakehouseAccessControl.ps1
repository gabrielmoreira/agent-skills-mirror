<#
.SYNOPSIS
    Validates a user's effective access across all Fabric Lakehouse security layers.

.DESCRIPTION
    Runs a diagnostic checklist against a Fabric Lakehouse to determine what access
    a specific user has across workspace roles, item permissions, OneLake security,
    and SQL analytics endpoint permissions.

    Uses the Fabric REST API and SQL analytics endpoint to gather information.

.PARAMETER WorkspaceId
    The GUID of the Fabric workspace containing the lakehouse.

.PARAMETER LakehouseId
    The GUID of the lakehouse to check.

.PARAMETER UserEmail
    The email address of the user to validate access for.

.PARAMETER SqlEndpoint
    The SQL analytics endpoint server name for the lakehouse.

.PARAMETER DatabaseName
    The database name for the SQL analytics endpoint.

.EXAMPLE
    .\Test-LakehouseAccessControl.ps1 `
        -WorkspaceId "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" `
        -LakehouseId "ffffffff-1111-2222-3333-444444444444" `
        -UserEmail "analyst@contoso.com" `
        -SqlEndpoint "ws.datawarehouse.fabric.microsoft.com" `
        -DatabaseName "MyLakehouse"

.NOTES
    Requires: Az.Accounts module for Fabric API authentication
    Requires: SqlServer module for SQL endpoint queries
    The executing user must have Admin or Member workspace role.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$WorkspaceId,

    [Parameter(Mandatory)]
    [string]$LakehouseId,

    [Parameter(Mandatory)]
    [string]$UserEmail,

    [Parameter()]
    [string]$SqlEndpoint,

    [Parameter()]
    [string]$DatabaseName
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Check {
    param(
        [string]$Label,
        [string]$Status,  # PASS, FAIL, WARN, INFO
        [string]$Detail
    )
    $color = switch ($Status) {
        'PASS' { 'Green' }
        'FAIL' { 'Red' }
        'WARN' { 'Yellow' }
        'INFO' { 'Cyan' }
        default { 'White' }
    }
    $icon = switch ($Status) {
        'PASS' { '[PASS]' }
        'FAIL' { '[FAIL]' }
        'WARN' { '[WARN]' }
        'INFO' { '[INFO]' }
        default { '[----]' }
    }
    Write-Host "$icon " -ForegroundColor $color -NoNewline
    Write-Host "$Label" -NoNewline
    if ($Detail) {
        Write-Host " - $Detail" -ForegroundColor Gray
    }
    else {
        Write-Host ""
    }
}

function Get-FabricAccessToken {
    try {
        $token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
        return $token
    }
    catch {
        Write-Warning "Failed to get Fabric access token. Run Connect-AzAccount first."
        throw
    }
}

# ============================================================
Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "  Fabric Lakehouse Access Control Validation" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "Workspace:  $WorkspaceId"
Write-Host "Lakehouse:  $LakehouseId"
Write-Host "User:       $UserEmail"
Write-Host "=====================================================`n" -ForegroundColor Cyan

$results = @()

# ============================================================
# CHECK 1: Workspace role
# ============================================================
Write-Host "--- Layer 1: Workspace Roles ---" -ForegroundColor Yellow

try {
    $token = Get-FabricAccessToken
    $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }

    $roleAssignments = Invoke-RestMethod `
        -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/roleAssignments" `
        -Headers $headers -Method Get

    $userRole = $roleAssignments.value | Where-Object {
        $_.principal.userDetails.userPrincipalName -eq $UserEmail
    }

    if ($userRole) {
        $roleName = $userRole.role
        Write-Check "Workspace role assigned" "PASS" "$UserEmail has '$roleName' role"
        $results += [PSCustomObject]@{ Check = 'Workspace Role'; Status = 'PASS'; Detail = $roleName }

        if ($roleName -in @('Admin', 'Member', 'Contributor')) {
            Write-Check "OneLake read/write access (via role)" "PASS" "$roleName grants full OneLake access"
        }
        else {
            Write-Check "OneLake read/write access (via role)" "WARN" "Viewer role does NOT grant OneLake access"
        }
    }
    else {
        Write-Check "Workspace role assigned" "INFO" "No workspace role found for $UserEmail"
        $results += [PSCustomObject]@{ Check = 'Workspace Role'; Status = 'NONE'; Detail = 'No workspace role' }
    }
}
catch {
    Write-Check "Workspace role check" "FAIL" $_.Exception.Message
}

# ============================================================
# CHECK 2: Item permissions (Lakehouse properties)
# ============================================================
Write-Host "`n--- Layer 2: Item Permissions ---" -ForegroundColor Yellow

try {
    $lakehouse = Invoke-RestMethod `
        -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId" `
        -Headers $headers -Method Get

    Write-Check "Lakehouse exists and accessible" "PASS" "Name: $($lakehouse.displayName)"
    $results += [PSCustomObject]@{ Check = 'Lakehouse Exists'; Status = 'PASS'; Detail = $lakehouse.displayName }
}
catch {
    Write-Check "Lakehouse accessible" "FAIL" $_.Exception.Message
}

# ============================================================
# CHECK 3: OneLake Security (via item definition)
# ============================================================
Write-Host "`n--- Layer 3: OneLake Security Data Access Roles ---" -ForegroundColor Yellow

try {
    # Attempt to get lakehouse item definition which includes data-access-roles
    $defUri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/lakehouses/$LakehouseId/getDefinition"
    try {
        $definition = Invoke-RestMethod -Uri $defUri -Headers $headers -Method Post
        Write-Check "Item definition retrieved" "PASS" "Checking for data access roles..."

        # Look for data-access-roles.json in the definition parts
        $darPart = $definition.definition.parts | Where-Object { $_.path -like '*data-access-roles*' }
        if ($darPart) {
            Write-Check "OneLake security roles detected" "INFO" "data-access-roles.json found in definition"
            Write-Host "  Review roles in the Fabric portal: Manage OneLake security" -ForegroundColor Gray
        }
        else {
            Write-Check "OneLake security roles" "INFO" "No data-access-roles.json in definition (may not be enabled)"
        }
    }
    catch {
        Write-Check "OneLake security check" "WARN" "Could not retrieve item definition: $($_.Exception.Message)"
    }
}
catch {
    Write-Check "OneLake security check" "WARN" $_.Exception.Message
}

# ============================================================
# CHECK 4: SQL Analytics Endpoint Permissions
# ============================================================
if ($SqlEndpoint -and $DatabaseName) {
    Write-Host "`n--- Layer 4: SQL Analytics Endpoint Permissions ---" -ForegroundColor Yellow

    $connectionString = "Server=$SqlEndpoint;Database=$DatabaseName;Authentication=Active Directory Interactive;Encrypt=True;TrustServerCertificate=False;"

    # Check if user has explicit SQL permissions
    $sqlCheck = @"
SELECT
    pr.name AS principal_name,
    pe.state_desc AS permission_state,
    pe.permission_name,
    CASE
        WHEN pe.class_desc = 'OBJECT_OR_COLUMN' THEN OBJECT_NAME(pe.major_id)
        WHEN pe.class_desc = 'SCHEMA' THEN SCHEMA_NAME(pe.major_id)
        ELSE pe.class_desc
    END AS target_object
FROM sys.database_principals AS pr
INNER JOIN sys.database_permissions AS pe
    ON pe.grantee_principal_id = pr.principal_id
WHERE pr.name = '$UserEmail'
ORDER BY pe.permission_name;
"@

    try {
        $sqlPerms = Invoke-Sqlcmd -ConnectionString $connectionString -Query $sqlCheck
        if ($sqlPerms) {
            Write-Check "SQL explicit permissions found" "PASS" "$($sqlPerms.Count) permission(s) for $UserEmail"
            $sqlPerms | Format-Table -AutoSize
        }
        else {
            Write-Check "SQL explicit permissions" "INFO" "No explicit SQL grants found for $UserEmail (may inherit from workspace role)"
        }
    }
    catch {
        Write-Check "SQL permission check" "WARN" $_.Exception.Message
    }

    # Check for RLS policies
    $rlsCheck = @"
SELECT COUNT(*) AS policy_count
FROM sys.security_policies
WHERE is_enabled = 1;
"@

    try {
        $rlsCount = Invoke-Sqlcmd -ConnectionString $connectionString -Query $rlsCheck
        if ($rlsCount.policy_count -gt 0) {
            Write-Check "Active RLS policies" "WARN" "$($rlsCount.policy_count) active RLS policy(ies) — may filter rows for $UserEmail"
        }
        else {
            Write-Check "Active RLS policies" "INFO" "No active RLS policies"
        }
    }
    catch {
        Write-Check "RLS policy check" "WARN" $_.Exception.Message
    }
}
else {
    Write-Host "`n--- Layer 4: SQL Analytics Endpoint (Skipped) ---" -ForegroundColor Yellow
    Write-Check "SQL endpoint check" "INFO" "Provide -SqlEndpoint and -DatabaseName to check SQL permissions"
}

# ============================================================
# Summary
# ============================================================
Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "  Validation Complete" -ForegroundColor Cyan
Write-Host "=====================================================`n" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review any FAIL or WARN items above."
Write-Host "  2. Check OneLake security roles in the Fabric portal."
Write-Host "  3. Allow up to 2 hours for permission changes to propagate."
Write-Host "  4. See references/workflow-diagnostics.md for detailed remediate.`n"
