<#
.SYNOPSIS
    Diagnoses Power BI workspace and semantic model security configuration.

.DESCRIPTION
    Performs a comprehensive security audit of a Power BI workspace including:
    - Workspace role assignments
    - Semantic model permissions
    - RLS role configuration status
    - Service principal access
    - Capacity and license checks

.PARAMETER WorkspaceName
    The name of the Power BI workspace to diagnose.

.PARAMETER UserEmail
    Optional. The email (UPN) of a specific user to check permissions for.

.PARAMETER IncludeSemanticModels
    Optional. If specified, also checks semantic model-level permissions.

.EXAMPLE
    ./Get-PBISecurityDiagnostic.ps1 -WorkspaceName "Sales Analytics"

.EXAMPLE
    ./Get-PBISecurityDiagnostic.ps1 -WorkspaceName "Sales Analytics" -UserEmail "jane@contoso.com" -IncludeSemanticModels

.NOTES
    Requires: MicrosoftPowerBIMgmt PowerShell module
    Requires: Workspace Admin or Fabric Admin role
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory = $false)]
    [string]$UserEmail,

    [Parameter(Mandatory = $false)]
    [switch]$IncludeSemanticModels
)

#Requires -Modules MicrosoftPowerBIMgmt

$ErrorActionPreference = 'Stop'

# --- Helper Functions ---

function Write-DiagnosticHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Write-DiagnosticSection {
    param([string]$Title)
    Write-Host ""
    Write-Host "--- $Title ---" -ForegroundColor Yellow
}

function Write-Finding {
    param(
        [string]$Level, # INFO, WARN, ERROR, PASS
        [string]$Message
    )
    $colors = @{
        'INFO'  = 'White'
        'WARN'  = 'Yellow'
        'ERROR' = 'Red'
        'PASS'  = 'Green'
    }
    $prefix = @{
        'INFO'  = '[INFO] '
        'WARN'  = '[WARN] '
        'ERROR' = '[FAIL] '
        'PASS'  = '[PASS] '
    }
    Write-Host "$($prefix[$Level])$Message" -ForegroundColor $colors[$Level]
}

# --- Main Diagnostic ---

Write-DiagnosticHeader "Power BI Security Diagnostic"
Write-Host "Workspace: $WorkspaceName"
Write-Host "Target User: $(if ($UserEmail) { $UserEmail } else { '(all users)' })"
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# Step 1: Authenticate
Write-DiagnosticSection "Authentication"
try {
    $token = Get-PowerBIAccessToken -ErrorAction SilentlyContinue
    if (-not $token) {
        Write-Finding 'INFO' 'No existing session. Connecting to Power BI service...'
        Connect-PowerBIServiceAccount
    }
    Write-Finding 'PASS' 'Authenticated to Power BI service.'
}
catch {
    Write-Finding 'ERROR' "Authentication failed: $($_.Exception.Message)"
    Write-Host "Run 'Connect-PowerBIServiceAccount' manually and retry." -ForegroundColor Red
    exit 1
}

# Step 2: Get Workspace
Write-DiagnosticSection "Workspace Lookup"
try {
    $workspace = Get-PowerBIWorkspace -Name $WorkspaceName -ErrorAction Stop
    if (-not $workspace) {
        # Try with filter for exact match
        $workspace = Get-PowerBIWorkspace -Filter "name eq '$WorkspaceName'" -ErrorAction Stop
    }

    if (-not $workspace) {
        Write-Finding 'ERROR' "Workspace '$WorkspaceName' not found. Check the name or your access."
        exit 1
    }

    Write-Finding 'PASS' "Found workspace: $($workspace.Name) (ID: $($workspace.Id))"
    Write-Finding 'INFO' "Type: $($workspace.Type) | State: $($workspace.State)"

    if ($workspace.IsOnDedicatedCapacity) {
        Write-Finding 'PASS' "Workspace is on dedicated capacity (Premium/Fabric)."
    }
    else {
        Write-Finding 'WARN' "Workspace is on shared capacity. XMLA endpoints and some features require Premium."
    }
}
catch {
    Write-Finding 'ERROR' "Failed to retrieve workspace: $($_.Exception.Message)"
    exit 1
}

# Step 3: Workspace Role Assignments
Write-DiagnosticSection "Workspace Role Assignments"
$users = $workspace.Users

if ($users -and $users.Count -gt 0) {
    Write-Finding 'INFO' "Total workspace members: $($users.Count)"

    # Categorize by role
    $admins = $users | Where-Object { $_.AccessRight -eq 'Admin' }
    $members = $users | Where-Object { $_.AccessRight -eq 'Member' }
    $contributors = $users | Where-Object { $_.AccessRight -eq 'Contributor' }
    $viewers = $users | Where-Object { $_.AccessRight -eq 'Viewer' }

    Write-Finding 'INFO' "  Admins: $($admins.Count) | Members: $($members.Count) | Contributors: $($contributors.Count) | Viewers: $($viewers.Count)"

    # RLS bypass warning
    $rlsBypassCount = ($admins.Count + $members.Count + $contributors.Count)
    if ($rlsBypassCount -gt 0) {
        Write-Finding 'WARN' "$rlsBypassCount users have roles that BYPASS RLS/OLS (Admin/Member/Contributor)."
    }

    # Check specific user
    if ($UserEmail) {
        $targetUser = $users | Where-Object {
            $_.UserPrincipalName -eq $UserEmail -or
            $_.Identifier -eq $UserEmail
        }

        if ($targetUser) {
            Write-Finding 'INFO' "User '$UserEmail' has role: $($targetUser.AccessRight)"

            if ($targetUser.AccessRight -in @('Admin', 'Member', 'Contributor')) {
                Write-Finding 'WARN' "User '$UserEmail' has $($targetUser.AccessRight) role - RLS/OLS will be BYPASSED."
            }
            else {
                Write-Finding 'PASS' "User '$UserEmail' has Viewer role - RLS/OLS will be ENFORCED."
            }
        }
        else {
            Write-Finding 'ERROR' "User '$UserEmail' is NOT a member of this workspace."
            Write-Finding 'INFO' "They may have access via item sharing or Power BI apps."
        }
    }

    # Service principal check
    $servicePrincipals = $users | Where-Object { $_.PrincipalType -eq 'App' }
    if ($servicePrincipals.Count -gt 0) {
        Write-Finding 'INFO' "$($servicePrincipals.Count) service principal(s) have workspace access."
        foreach ($sp in $servicePrincipals) {
            Write-Finding 'INFO' "  SP: $($sp.Identifier) | Role: $($sp.AccessRight)"
        }
    }
}
else {
    Write-Finding 'WARN' "No user assignments returned. You may need Fabric Admin scope to see all members."
    Write-Finding 'INFO' "Try: Get-PowerBIWorkspace -Scope Organization -Filter `"name eq '$WorkspaceName'`""
}

# Step 4: Semantic Model Analysis
if ($IncludeSemanticModels) {
    Write-DiagnosticSection "Semantic Model Analysis"

    try {
        $datasets = Invoke-PowerBIRestMethod -Url "groups/$($workspace.Id)/datasets" -Method Get |
            ConvertFrom-Json |
            Select-Object -ExpandProperty value

        Write-Finding 'INFO' "Found $($datasets.Count) semantic model(s) in workspace."

        foreach ($ds in $datasets) {
            Write-Host ""
            Write-Finding 'INFO' "Model: $($ds.name) (ID: $($ds.id))"
            Write-Finding 'INFO' "  Configured By: $($ds.configuredBy)"

            if ($ds.isEffectiveIdentityRequired) {
                Write-Finding 'INFO' "  RLS: Effective identity required (RLS likely configured)"
            }

            if ($ds.isEffectiveIdentityRolesRequired) {
                Write-Finding 'INFO' "  RLS Roles: Required for effective identity"
            }

            # Check if it's a DirectLake model
            if ($ds.directLakeConfig) {
                Write-Finding 'INFO' "  Mode: DirectLake"
                Write-Finding 'WARN' "  DirectLake models fall back to DirectQuery if SQL endpoint has RLS/OLS."
            }
        }
    }
    catch {
        Write-Finding 'WARN' "Could not retrieve semantic models: $($_.Exception.Message)"
    }
}

# Step 5: Summary
Write-DiagnosticHeader "Diagnostic Summary"
Write-Finding 'INFO' "Workspace: $($workspace.Name)"
Write-Finding 'INFO' "Dedicated Capacity: $($workspace.IsOnDedicatedCapacity)"
Write-Finding 'INFO' "Total Members: $(if ($users) { $users.Count } else { 'Unknown' })"

if ($UserEmail -and $targetUser) {
    Write-Finding 'INFO' "Target User Role: $($targetUser.AccessRight)"
    if ($targetUser.AccessRight -eq 'Viewer') {
        Write-Finding 'PASS' "RLS/OLS enforcement: ACTIVE for this user."
    }
    else {
        Write-Finding 'WARN' "RLS/OLS enforcement: BYPASSED for this user."
    }
}

Write-Host ""
Write-Host "For detailed RLS testing, use Test-PBIRowLevelSecurity.ps1" -ForegroundColor Gray
Write-Host "For full documentation, see SKILL.md and references/ folder." -ForegroundColor Gray
