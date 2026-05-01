<#
.SYNOPSIS
    Audits explicit SQL permissions on a Fabric Lakehouse SQL analytics endpoint.

.DESCRIPTION
    Connects to a Fabric Lakehouse SQL analytics endpoint and retrieves:
    - All explicit database-level permissions (GRANT/DENY)
    - Column-level permission grants
    - Active row-level security policies and predicates
    - Dynamic data masking rules
    Outputs results as formatted tables for review.

.PARAMETER SqlEndpoint
    The SQL analytics endpoint connection string or server name.
    Example: "your-workspace.datawarehouse.fabric.microsoft.com"

.PARAMETER DatabaseName
    The name of the lakehouse SQL analytics endpoint database.

.PARAMETER OutputPath
    Optional. Path to export results as a CSV file.

.EXAMPLE
    .\Audit-SqlEndpointPermissions.ps1 -SqlEndpoint "ws.datawarehouse.fabric.microsoft.com" -DatabaseName "MyLakehouse"

.EXAMPLE
    .\Audit-SqlEndpointPermissions.ps1 -SqlEndpoint "ws.datawarehouse.fabric.microsoft.com" -DatabaseName "MyLakehouse" -OutputPath "./audit-results"

.NOTES
    Requires: SqlServer PowerShell module (Install-Module SqlServer)
    Authentication: Uses Azure AD integrated authentication via the current user context.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$SqlEndpoint,

    [Parameter(Mandatory)]
    [string]$DatabaseName,

    [Parameter()]
    [string]$OutputPath
)

#Requires -Modules SqlServer

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Section {
    param([string]$Title)
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "$('=' * 60)" -ForegroundColor Cyan
}

# Build connection string with Azure AD authentication
$connectionString = "Server=$SqlEndpoint;Database=$DatabaseName;Authentication=Active Directory Interactive;Encrypt=True;TrustServerCertificate=False;"

Write-Host "Connecting to: $SqlEndpoint / $DatabaseName" -ForegroundColor Yellow
Write-Host "Using Azure AD Interactive authentication..." -ForegroundColor Yellow

# 1. Explicit database-level permissions
Write-Section "Explicit Database Permissions (GRANT/DENY)"

$permQuery = @"
SELECT DISTINCT
    pr.principal_id,
    pr.name AS principal_name,
    pr.type_desc AS principal_type,
    pr.authentication_type_desc,
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
WHERE pr.name NOT IN ('public', 'guest', 'INFORMATION_SCHEMA', 'sys')
ORDER BY pr.name, pe.permission_name;
"@

try {
    $permissions = Invoke-Sqlcmd -ConnectionString $connectionString -Query $permQuery
    if ($permissions) {
        $permissions | Format-Table -AutoSize
        Write-Host "Found $($permissions.Count) explicit permission entries." -ForegroundColor Green
    }
    else {
        Write-Host "No explicit permissions found." -ForegroundColor Yellow
    }
}
catch {
    Write-Warning "Failed to query permissions: $($_.Exception.Message)"
}

# 2. Column-level permissions
Write-Section "Column-Level Permission Grants"

$colQuery = @"
SELECT
    pr.name AS principal_name,
    OBJECT_SCHEMA_NAME(pe.major_id) AS schema_name,
    OBJECT_NAME(pe.major_id) AS table_name,
    c.name AS column_name,
    pe.permission_name,
    pe.state_desc AS permission_state
FROM sys.database_permissions AS pe
JOIN sys.database_principals AS pr
    ON pe.grantee_principal_id = pr.principal_id
JOIN sys.columns AS c
    ON pe.major_id = c.object_id
    AND pe.minor_id = c.column_id
WHERE pe.minor_id > 0
ORDER BY pr.name, table_name, column_name;
"@

try {
    $colPerms = Invoke-Sqlcmd -ConnectionString $connectionString -Query $colQuery
    if ($colPerms) {
        $colPerms | Format-Table -AutoSize
        Write-Host "Found $($colPerms.Count) column-level grants." -ForegroundColor Green
    }
    else {
        Write-Host "No column-level permission grants found." -ForegroundColor Yellow
    }
}
catch {
    Write-Warning "Failed to query column permissions: $($_.Exception.Message)"
}

# 3. Row-level security policies
Write-Section "Row-Level Security Policies"

$rlsQuery = @"
SELECT
    sp.name AS policy_name,
    sp.is_enabled,
    sp.is_schema_bound,
    OBJECT_SCHEMA_NAME(spred.target_object_id) AS target_schema,
    OBJECT_NAME(spred.target_object_id) AS target_table,
    spred.predicate_type_desc,
    OBJECT_NAME(spred.predicate_id) AS predicate_function,
    OBJECT_DEFINITION(spred.predicate_id) AS predicate_definition
FROM sys.security_policies AS sp
JOIN sys.security_predicates AS spred
    ON sp.object_id = spred.object_id
ORDER BY sp.name;
"@

try {
    $rlsPolicies = Invoke-Sqlcmd -ConnectionString $connectionString -Query $rlsQuery
    if ($rlsPolicies) {
        $rlsPolicies | Format-Table -AutoSize -Wrap
        Write-Host "Found $($rlsPolicies.Count) RLS predicate(s)." -ForegroundColor Green
    }
    else {
        Write-Host "No row-level security policies found." -ForegroundColor Yellow
    }
}
catch {
    Write-Warning "Failed to query RLS policies: $($_.Exception.Message)"
}

# 4. Dynamic data masking
Write-Section "Dynamic Data Masking Rules"

$maskQuery = @"
SELECT
    OBJECT_SCHEMA_NAME(mc.object_id) AS schema_name,
    OBJECT_NAME(mc.object_id) AS table_name,
    mc.name AS column_name,
    mc.masking_function
FROM sys.masked_columns AS mc
WHERE mc.is_masked = 1
ORDER BY table_name, column_name;
"@

try {
    $masks = Invoke-Sqlcmd -ConnectionString $connectionString -Query $maskQuery
    if ($masks) {
        $masks | Format-Table -AutoSize
        Write-Host "Found $($masks.Count) masked column(s)." -ForegroundColor Green
    }
    else {
        Write-Host "No dynamic data masking rules found." -ForegroundColor Yellow
    }
}
catch {
    Write-Warning "Failed to query masking rules: $($_.Exception.Message)"
}

# Export results if OutputPath specified
if ($OutputPath) {
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'

    if ($permissions) {
        $permissions | Export-Csv -Path (Join-Path $OutputPath "permissions-$timestamp.csv") -NoTypeInformation
    }
    if ($colPerms) {
        $colPerms | Export-Csv -Path (Join-Path $OutputPath "column-permissions-$timestamp.csv") -NoTypeInformation
    }
    if ($rlsPolicies) {
        $rlsPolicies | Export-Csv -Path (Join-Path $OutputPath "rls-policies-$timestamp.csv") -NoTypeInformation
    }
    if ($masks) {
        $masks | Export-Csv -Path (Join-Path $OutputPath "masking-rules-$timestamp.csv") -NoTypeInformation
    }

    Write-Host "`nResults exported to: $OutputPath" -ForegroundColor Green
}

Write-Host "`nAudit complete." -ForegroundColor Green
