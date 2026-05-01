# RLS remediate Guide

Comprehensive diagnostic workflow for Row-Level Security issues in Microsoft Fabric Power BI.

## Table of Contents

- [Common Symptoms](#common-symptoms)
- [Diagnostic Workflow](#diagnostic-workflow)
- [Root Cause Analysis](#root-cause-analysis)
- [Testing RLS](#testing-rls)
- [DirectQuery vs Import Considerations](#directquery-vs-import-considerations)
- [DAX Functions for RLS](#dax-functions-for-rls)
- [Performance Optimization](#performance-optimization)
- [Common Mistakes](#common-mistakes)

## Common Symptoms

| Symptom | Probable Cause |
|---------|---------------|
| User sees all data | User has Admin/Member/Contributor role (RLS bypassed) |
| User sees no data | UPN not stored or entered incorrectly in role mapping |
| Partial data missing | User mapped to wrong role or multiple role interaction |
| Data changes after name change | User account UPN changed; role mapping is stale |
| RLS works in Desktop but not service | Role members not assigned in the Power BI service |

## Diagnostic Workflow

### Step 1: Verify User's Workspace Role

RLS **only** restricts data for users with the **Viewer** role. Admin, Member, and Contributor roles bypass RLS entirely.

```powershell
Connect-PowerBIServiceAccount

$workspace = Get-PowerBIWorkspace -Name "Sales Analytics"
$workspace | Select-Object -ExpandProperty Users | Where-Object {
    $_.UserPrincipalName -like "*targetuser*"
} | Format-Table UserPrincipalName, AccessRight
```

**Expected**: User should have `Viewer` access if RLS must be enforced.

### Step 2: Verify Semantic Model Role Membership

Check that the user is assigned to the correct RLS role on the semantic model.

```powershell
# Use REST API to check role assignments
$datasetId = "<semantic-model-id>"
$workspaceId = "<workspace-id>"

$url = "groups/$workspaceId/datasets/$datasetId"
$dataset = Invoke-PowerBIRestMethod -Url $url -Method Get | ConvertFrom-Json
Write-Output "Dataset: $($dataset.name)"
Write-Output "IsEffectiveIdentityRequired: $($dataset.isEffectiveIdentityRequired)"
```

### Step 3: Test the Role in Power BI Service

1. Navigate to the semantic model in the Power BI service
2. Select **More options (...)** → **Security**
3. Select the role → **Test as role**
4. Use **Now viewing as** to test as a specific user
5. Compare data visibility between roles

### Step 4: Verify DAX Filter Expressions

Common issues with RLS DAX expressions:

```dax
// CORRECT: Uses USERPRINCIPALNAME() which returns user@contoso.com
[SalesRegion] = LOOKUPVALUE(
    UserRegionMapping[Region],
    UserRegionMapping[UserEmail],
    USERPRINCIPALNAME()
)

// ISSUE: USERNAME() returns DOMAIN\User in Desktop but UPN in service
// Use USERPRINCIPALNAME() for consistency
```

### Step 5: Check Relationship Filter Direction

RLS filters only propagate through **active** relationships. If the filter does not reach a table:

1. Verify the relationship is active (not dotted line in model view)
2. Check the cross-filter direction — set "Apply security filter in both directions" if needed
3. Ensure no broken relationship chain exists

## Root Cause Analysis

### User Has Edit Permissions

If a user has **Build** permission on the semantic model (even as a Viewer with Build), RLS still applies. However, Admin/Member/Contributor workspace roles always bypass RLS.

**Resolution**: Ensure content consumers only have the Viewer workspace role.

### Multiple Role Membership

Users can belong to multiple RLS roles. Roles are **additive** — a user in both "Sales" and "Marketing" roles sees data for both.

**Resolution**: This is by design. To restrict, consolidate into a single role with appropriate filters.

### UPN Mismatch

When a user's account changes (name change, alias change), the UPN stored in role mappings may become stale.

**Resolution**: 
1. Add a `USERNAME()` measure to verify identity: `Who Am I = USERPRINCIPALNAME()`
2. Update role mappings with the new UPN
3. Use security groups instead of individual users (recommended)

### Dynamic RLS with USERPRINCIPALNAME()

```dax
// Recommended pattern: Dynamic RLS with a security table
VAR CurrentUser = USERPRINCIPALNAME()
RETURN
    CONTAINS(SecurityTable, SecurityTable[UserEmail], CurrentUser)
```

## DirectQuery vs Import Considerations

| Mode | RLS Source | Behavior |
|------|-----------|----------|
| Import | Power BI semantic model | RLS defined in Desktop/service, data source roles ignored |
| DirectQuery | Data source + semantic model | Source security roles apply via user credentials |
| DirectLake | Semantic model (preferred) | SQL endpoint RLS causes DirectQuery fallback |
| Live Connection | Analysis Services model | Configure RLS in AS model, not Power BI |

### DirectLake-Specific

- If RLS is defined in the SQL analytics endpoint, DirectLake falls back to DirectQuery
- Define RLS in the semantic model only to avoid fallback
- For app-based distribution: switch from SSO to fixed identity credential

## DAX Functions for RLS

| Function | Desktop Return | Service Return | Recommendation |
|----------|---------------|----------------|----------------|
| `USERNAME()` | `DOMAIN\User` | `user@contoso.com` | Avoid |
| `USERPRINCIPALNAME()` | `user@contoso.com` | `user@contoso.com` | **Preferred** |
| `CUSTOMDATA()` | Custom string | Custom string | For embedded scenarios |

## Performance Optimization

1. Apply RLS filters on **dimension tables**, not fact tables
2. Rely on model relationships to propagate filters — avoid `LOOKUPVALUE()` when relationships exist
3. Design proper star schema with well-defined relationships
4. For DirectQuery: optimize source database indexes
5. Measure RLS impact using **Performance Analyzer** in Power BI Desktop

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| RLS on fact table | Poor performance | Move filter to dimension table |
| Using `USERNAME()` | Inconsistent behavior between Desktop and service | Switch to `USERPRINCIPALNAME()` |
| Not assigning role members | RLS defined but no users mapped | Add members via Security page |
| Giving Build permission unnecessarily | Users can create reports but still see filtered data | Only grant Build when needed |
| Testing only in Desktop | RLS behaves differently in Desktop vs service | Always test in service with "Test as role" |
| Aggregation tables without RLS | Aggregated data leaks unfiltered | Apply consistent RLS to aggregation tables |
