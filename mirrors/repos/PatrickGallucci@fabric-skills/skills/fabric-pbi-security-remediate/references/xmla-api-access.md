# XMLA & API Access remediate Guide

Diagnostic workflow for XMLA endpoint and Power BI REST API access issues in Microsoft Fabric.

## Table of Contents

- [Common Symptoms](#common-symptoms)
- [XMLA Endpoint Configuration](#xmla-endpoint-configuration)
- [Service Principal Setup](#service-principal-setup)
- [Authentication remediate](#authentication-remediate)
- [Impersonation](#impersonation)
- [Model Roles via XMLA](#model-roles-via-xmla)
- [Capacity Requirements](#capacity-requirements)

## Common Symptoms

| Symptom | Probable Cause | First Check |
|---------|---------------|-------------|
| XMLA connection refused | Endpoint not enabled in tenant | Tenant Integration settings |
| API returns 401 Unauthorized | Invalid or expired token | Refresh auth token |
| API returns 403 Forbidden | Insufficient permissions | Check workspace role + tenant settings |
| Service principal can't access workspace | SP not added to workspace | Add SP to workspace |
| "Service principals not allowed" | Tenant setting disabled | Enable SP API access setting |
| Impersonation fails | Missing Read + Build on semantic model | Grant both permissions |
| "User not found" error on XMLA | Role membership mismatch | Check user is in specified role |

## XMLA Endpoint Configuration

### Enable XMLA Endpoints

1. Go to **Fabric Admin Portal** → **Tenant Settings**
2. Navigate to **Integration settings**
3. Enable **Allow XMLA endpoints and Analyze in Excel with on-premises datasets**
4. Set scope (entire organization or specific security groups)

### Connection String Format

```
powerbi://api.powerbi.com/v1.0/myorg/<workspace-name>
```

For Premium Per User workspaces:
```
powerbi://api.powerbi.com/v1.0/myorg/<workspace-name>
```

### Required Permissions for XMLA

| Operation | Minimum Permission |
|-----------|-------------------|
| Read data (queries) | Viewer role + Read on semantic model |
| Write data (processing) | Contributor role or higher |
| Define/modify roles | Admin or Member role |
| Impersonate users | Read + Build on semantic model |

## Service Principal Setup

### Step 1: Register Entra ID Application

1. Go to **Azure Portal** → **Microsoft Entra ID** → **App Registrations**
2. Select **New Registration**
3. Provide a name and select supported account types
4. Register and note the **Application (client) ID**
5. Create a client secret under **Certificates & secrets**

### Step 2: Enable Service Principal API Access

1. Go to **Fabric Admin Portal** → **Tenant Settings**
2. Find **Developer settings** section
3. Enable **Allow service principals to use Fabric APIs**
4. Scope to a specific security group containing the service principal
5. Enable **Allow service principals to use Power BI APIs** (if separate setting exists)

### Step 3: Add Service Principal to Security Group

```powershell
# Verify the security group contains the service principal
Connect-MgGraph -Scopes "Group.Read.All"
$group = Get-MgGroup -Filter "displayName eq 'Fabric API Service Principals'"
Get-MgGroupMember -GroupId $group.Id | Select-Object Id, AdditionalProperties
```

### Step 4: Add Service Principal to Workspace

```powershell
# Using PowerShell
Connect-PowerBIServiceAccount

$SPObjectID = "<service-principal-object-id>"
$workspace = Get-PowerBIWorkspace -Filter "name eq 'Target Workspace'"

Add-PowerBIWorkspaceUser -Id $workspace.Id `
    -AccessRight Member `
    -PrincipalType App `
    -Identifier $SPObjectID
```

Or using REST API:

```powershell
$body = @{
    groupUserAccessRight = "Member"
    identifier = "<service-principal-object-id>"
    principalType = "App"
} | ConvertTo-Json

Invoke-PowerBIRestMethod -Url "groups/$($workspace.Id)/users" `
    -Method Post `
    -Body $body
```

### Step 5: Authenticate as Service Principal

```powershell
# Interactive authentication (user context)
Connect-PowerBIServiceAccount

# Service principal authentication
$credential = New-Object System.Management.Automation.PSCredential(
    $clientId,
    (ConvertTo-SecureString $clientSecret -AsPlainText -Force)
)
Connect-PowerBIServiceAccount -ServicePrincipal `
    -TenantId $tenantId `
    -Credential $credential
```

## Authentication remediate

### Token Issues

```powershell
# Verify current authentication context
Get-PowerBIAccessToken | ConvertFrom-Json | Select-Object -ExpandProperty @odata.context

# Force re-authentication
Connect-PowerBIServiceAccount -Force
```

### Common Auth Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `AADSTS700016` | App not found in tenant | Verify app registration in correct tenant |
| `AADSTS7000215` | Invalid client secret | Regenerate secret, check expiry |
| `AADSTS50034` | User account doesn't exist | Verify UPN, check guest access |
| `AADSTS65001` | User hasn't consented | Grant admin consent for API permissions |
| `AADSTS90002` | Tenant not found | Verify tenant ID |

### Required API Permissions (Entra ID App)

For Power BI Service API (`00000009-0000-0000-c000-000000000000`):

| Permission | Type | Purpose |
|-----------|------|---------|
| `Tenant.Read.All` | Application | Read all tenant metadata |
| `Tenant.ReadWrite.All` | Application | Full admin operations |
| `Dataset.Read.All` | Delegated | Read semantic models |
| `Workspace.Read.All` | Delegated | Read workspace metadata |

## Impersonation

### EffectiveUserName

Allows an admin to connect as another user via XMLA:

```
Data Source=powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName;
Initial Catalog=SemanticModelName;
EffectiveUserName=user@contoso.com
```

**Requirements**:
- The specified user must exist in the tenant's Entra ID
- The specified user must have **both** Read and Build permissions on the semantic model
- If either permission is missing, impersonation fails with a connection error

### Roles Connection String Property

For testing RLS via XMLA:

```
Data Source=powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName;
Initial Catalog=SemanticModelName;
Roles=SalesRole
```

**Permission rules**:
- Workspace admin: Does not need to be a member of the specified role
- Non-workspace admin: Must belong to one or more of the specified roles

## Model Roles via XMLA

With XMLA endpoints, you can manage:

- Role definitions (RLS filter expressions)
- Role membership (user/group assignments)
- Object-level security (table/column permissions)

**Important**: Model roles in Power BI are used **only** for RLS and OLS. Use the Power BI permission model (workspace roles, item sharing) for all other access control.

## Capacity Requirements

XMLA endpoints require Premium capacity:

| Feature | Minimum SKU |
|---------|-------------|
| XMLA Read | F64 / P1 or higher |
| XMLA Read/Write | F64 / P1 or higher |
| Service Principal API access | Any Fabric capacity |
| REST API (non-admin) | Pro license minimum |
| REST API (admin) | Fabric admin role |

**Note**: Trial capacities (F SKU trial) have limited XMLA support. Use paid F64+ or P1+ for production XMLA workloads.
