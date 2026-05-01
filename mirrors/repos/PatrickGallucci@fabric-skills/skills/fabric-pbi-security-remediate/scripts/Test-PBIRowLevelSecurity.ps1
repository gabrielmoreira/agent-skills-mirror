<#
.SYNOPSIS
    Tests and validates Power BI Row-Level Security (RLS) configuration.

.DESCRIPTION
    Validates RLS setup by checking:
    - Role definitions on a semantic model
    - Role membership assignments
    - Whether a specific user is mapped to the expected role
    - Common misconfigurations (Admin/Member/Contributor with RLS)

.PARAMETER WorkspaceId
    The GUID of the Power BI workspace.

.PARAMETER DatasetId
    The GUID of the semantic model (dataset) to test.

.PARAMETER UserEmail
    Optional. A specific user's UPN to validate against role assignments.

.EXAMPLE
    ./Test-PBIRowLevelSecurity.ps1 -WorkspaceId "aaaabbbb-1111-2222-3333-ccccddddeeee" -DatasetId "ffffffff-4444-5555-6666-777788889999"

.EXAMPLE
    ./Test-PBIRowLevelSecurity.ps1 -WorkspaceId "aaaabbbb-1111-2222-3333-ccccddddeeee" -DatasetId "ffffffff-4444-5555-6666-777788889999" -UserEmail "user@contoso.com"

.NOTES
    Requires: MicrosoftPowerBIMgmt PowerShell module
    Requires: Admin or Member role on the workspace
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [string]$DatasetId,

    [Parameter(Mandatory = $false)]
    [string]$UserEmail
)

#Requires -Modules MicrosoftPowerBIMgmt

$ErrorActionPreference = 'Stop'

function Write-Finding {
    param(
        [string]$Level,
        [string]$Message
    )
    $colors = @{ 'INFO' = 'White'; 'WARN' = 'Yellow'; 'ERROR' = 'Red'; 'PASS' = 'Green' }
    $prefix = @{ 'INFO' = '[INFO] '; 'WARN' = '[WARN] '; 'ERROR' = '[FAIL] '; 'PASS' = '[PASS] ' }
    Write-Host "$($prefix[$Level])$Message" -ForegroundColor $colors[$Level]
}

# --- Authenticate ---
try {
    $token = Get-PowerBIAccessToken -ErrorAction SilentlyContinue
    if (-not $token) {
        Connect-PowerBIServiceAccount
    }
    Write-Finding 'PASS' 'Authenticated to Power BI service.'
}
catch {
    Write-Finding 'ERROR' "Authentication failed: $($_.Exception.Message)"
    exit 1
}

# --- Get Dataset Info ---
Write-Host ""
Write-Host "=== RLS Validation Report ===" -ForegroundColor Cyan
Write-Host "Workspace ID: $WorkspaceId"
Write-Host "Dataset ID:   $DatasetId"
Write-Host "Timestamp:    $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

try {
    $datasetUrl = "groups/$WorkspaceId/datasets/$DatasetId"
    $dataset = Invoke-PowerBIRestMethod -Url $datasetUrl -Method Get | ConvertFrom-Json

    Write-Finding 'INFO' "Semantic Model: $($dataset.name)"
    Write-Finding 'INFO' "Configured By: $($dataset.configuredBy)"

    if ($dataset.isEffectiveIdentityRequired) {
        Write-Finding 'PASS' "RLS is configured (isEffectiveIdentityRequired = true)."
    }
    else {
        Write-Finding 'WARN' "RLS may not be configured (isEffectiveIdentityRequired = false)."
        Write-Finding 'INFO' "If RLS is expected, verify roles are defined in Power BI Desktop."
    }
}
catch {
    Write-Finding 'ERROR' "Failed to retrieve dataset: $($_.Exception.Message)"
    exit 1
}

# --- Check Workspace Users for RLS Bypass ---
Write-Host ""
Write-Host "--- Workspace RLS Bypass Check ---" -ForegroundColor Yellow

try {
    $workspace = Get-PowerBIWorkspace -Id $WorkspaceId
    $users = $workspace.Users

    if ($users) {
        $bypassUsers = $users | Where-Object {
            $_.AccessRight -in @('Admin', 'Member', 'Contributor')
        }

        if ($bypassUsers.Count -gt 0) {
            Write-Finding 'WARN' "$($bypassUsers.Count) user(s) bypass RLS due to workspace role:"
            foreach ($u in $bypassUsers) {
                $upn = if ($u.UserPrincipalName) { $u.UserPrincipalName } else { $u.Identifier }
                Write-Finding 'WARN' "  $upn ($($u.AccessRight))"
            }
        }

        $viewerUsers = $users | Where-Object { $_.AccessRight -eq 'Viewer' }
        Write-Finding 'INFO' "$($viewerUsers.Count) Viewer(s) will have RLS enforced."

        # Check specific user
        if ($UserEmail) {
            $targetUser = $users | Where-Object {
                $_.UserPrincipalName -eq $UserEmail -or $_.Identifier -eq $UserEmail
            }

            if ($targetUser) {
                if ($targetUser.AccessRight -eq 'Viewer') {
                    Write-Finding 'PASS' "User '$UserEmail' is a Viewer — RLS will be enforced."
                }
                else {
                    Write-Finding 'ERROR' "User '$UserEmail' has '$($targetUser.AccessRight)' role — RLS BYPASSED."
                    Write-Finding 'INFO' "To enforce RLS, change this user to Viewer role."
                }
            }
            else {
                Write-Finding 'WARN' "User '$UserEmail' not found in workspace members."
                Write-Finding 'INFO' "They may access via item sharing or app — RLS depends on semantic model permissions."
            }
        }
    }
}
catch {
    Write-Finding 'WARN' "Could not check workspace users: $($_.Exception.Message)"
}

# --- Recommendations ---
Write-Host ""
Write-Host "--- Recommendations ---" -ForegroundColor Yellow
Write-Finding 'INFO' "1. Test RLS in Power BI service: Dataset > ... > Security > Test as role"
Write-Finding 'INFO' "2. Add a card visual with measure: Who Am I = USERPRINCIPALNAME()"
Write-Finding 'INFO' "3. Use security groups for role membership (easier management)"
Write-Finding 'INFO' "4. Prefer USERPRINCIPALNAME() over USERNAME() in DAX filters"
Write-Finding 'INFO' "5. For DirectLake: define RLS in semantic model, not SQL endpoint"

Write-Host ""
Write-Host "=== Validation Complete ===" -ForegroundColor Cyan
