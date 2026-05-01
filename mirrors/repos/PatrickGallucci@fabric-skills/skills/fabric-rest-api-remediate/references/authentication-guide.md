# Authentication Guide for Microsoft Fabric REST APIs

Step-by-step token acquisition and remediate for all supported identity types.

## Table of Contents

- [Identity Types Overview](#identity-types-overview)
- [PowerShell Token Acquisition](#powershell-token-acquisition)
- [C# Token Acquisition](#c-token-acquisition)
- [Service Principal Setup](#service-principal-setup)
- [Managed Identity Setup](#managed-identity-setup)
- [Token Validation Checklist](#token-validation-checklist)
- [Common Authentication Errors](#common-authentication-errors)

---

## Identity Types Overview

Fabric REST APIs support three identity types:

| Identity Type | Use Case | Tenant Setting Required |
|---------------|----------|------------------------|
| User (interactive) | Developer/admin tasks, debugging | No |
| Service Principal | Automated pipelines, CI/CD | Yes — "Service principals can use Fabric APIs" |
| Managed Identity | Azure-hosted automation (VMs, Functions, AKS) | Yes — same tenant setting as service principal |

---

## PowerShell Token Acquisition

### Interactive User Token (MSAL.PS)

```powershell
# Install MSAL.PS if needed
Install-Module -Name MSAL.PS -Scope CurrentUser -Force

$clientId   = "<your-app-client-id>"
$tenantId   = "<your-tenant-id>"
$scopes     = @("https://api.fabric.microsoft.com/Workspace.ReadWrite.All",
                "https://api.fabric.microsoft.com/Item.ReadWrite.All")

$tokenResult = Get-MsalToken `
    -ClientId $clientId `
    -TenantId $tenantId `
    -Scopes $scopes `
    -Interactive

$token = $tokenResult.AccessToken
Write-Host "Token acquired, expires: $($tokenResult.ExpiresOn)"
```

### Interactive User Token (Az.Accounts)

```powershell
# Install Az.Accounts if needed
Install-Module -Name Az.Accounts -Scope CurrentUser -Force

Connect-AzAccount -TenantId "<your-tenant-id>"

$tokenResult = Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com"
$token = $tokenResult.Token
Write-Host "Token acquired, expires: $($tokenResult.ExpiresOn)"
```

### Service Principal Token (Client Secret)

```powershell
$clientId     = "<your-app-client-id>"
$clientSecret = "<your-client-secret>"
$tenantId     = "<your-tenant-id>"

$body = @{
    grant_type    = "client_credentials"
    client_id     = $clientId
    client_secret = $clientSecret
    scope         = "https://api.fabric.microsoft.com/.default"
}

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $body

$token = $response.access_token
Write-Host "Service principal token acquired"
```

### Service Principal Token (Certificate)

```powershell
$clientId   = "<your-app-client-id>"
$tenantId   = "<your-tenant-id>"
$certPath   = "<path-to-pfx>"
$certPassword = "<certificate-password>"

$tokenResult = Get-MsalToken `
    -ClientId $clientId `
    -TenantId $tenantId `
    -ClientCertificate (Get-PfxCertificate -FilePath $certPath -Password (ConvertTo-SecureString $certPassword -AsPlainText -Force)) `
    -Scopes @("https://api.fabric.microsoft.com/.default")

$token = $tokenResult.AccessToken
```

---

## C# Token Acquisition

### Interactive User Token (MSAL.NET)

```csharp
using Microsoft.Identity.Client;

string clientId  = "YourApplicationId";
string authority = "https://login.microsoftonline.com/organizations";
string redirect  = "http://localhost";

string[] scopes = new[] {
    "https://api.fabric.microsoft.com/Workspace.ReadWrite.All",
    "https://api.fabric.microsoft.com/Item.ReadWrite.All"
};

var app = PublicClientApplicationBuilder
    .Create(clientId)
    .WithAuthority(authority)
    .WithRedirectUri(redirect)
    .Build();

var result = await app.AcquireTokenInteractive(scopes)
    .ExecuteAsync()
    .ConfigureAwait(false);

string token = result.AccessToken;
```

### Confidential Client (Service Principal)

```csharp
using Microsoft.Identity.Client;

string clientId     = "YourApplicationId";
string clientSecret = "YourClientSecret";
string tenantId     = "YourTenantId";

string[] scopes = new[] { "https://api.fabric.microsoft.com/.default" };

var app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithClientSecret(clientSecret)
    .WithAuthority($"https://login.microsoftonline.com/{tenantId}")
    .Build();

var result = await app.AcquireTokenForClient(scopes)
    .ExecuteAsync()
    .ConfigureAwait(false);

string token = result.AccessToken;
```

---

## Service Principal Setup

### Step 1: Register an Entra ID App

1. Sign in to Azure Portal > Microsoft Entra ID > App registrations
2. Click "New registration"
3. Enter a display name, select account types, add redirect URI if needed
4. Click Register
5. Copy the Application (client) ID

### Step 2: Create a Client Secret or Certificate

- Client Secret: App registrations > Your app > Certificates & secrets > New client secret
- Certificate: Upload a certificate under the same section

### Step 3: Grant Fabric API Permissions

1. App registrations > Your app > API permissions > Add a permission
2. Select "Power BI Service" (Fabric permissions are under this registration)
3. Select the required permissions (Workspace.ReadWrite.All, Item.ReadWrite.All, etc.)
4. Click "Grant admin consent" if required by your organization

### Step 4: Enable Tenant Setting

A Fabric Administrator must enable:
**Admin Portal > Tenant settings > Developer settings > Service principals can use Fabric APIs**

This setting controls access for both service principals and managed identities.

---

## Managed Identity Setup

For Azure-hosted applications (Azure Functions, VMs, AKS):

1. Enable managed identity on the Azure resource
2. Ensure the same tenant setting is enabled as for service principals
3. Assign the managed identity to a Fabric workspace with appropriate role

Token acquisition is automatic — no secrets needed:

```csharp
// Using Azure.Identity
var credential = new DefaultAzureCredential();
var token = await credential.GetTokenAsync(
    new TokenRequestContext(new[] { "https://api.fabric.microsoft.com/.default" })
);
```

---

## Token Validation Checklist

When authentication fails, decode the JWT and check:

| Claim | Expected Value | Issue If Wrong |
|-------|---------------|----------------|
| `aud` | `https://api.fabric.microsoft.com` | Wrong resource/audience requested |
| `iss` | `https://sts.windows.net/{tenantId}/` | Wrong tenant |
| `exp` | Future timestamp | Token expired |
| `scp` (user tokens) | Required scopes | Missing permissions |
| `roles` (app tokens) | Required app roles | Missing app-level permissions |
| `tid` | Your Fabric tenant ID | Cross-tenant mismatch |
| `appid` or `azp` | Your registered app ID | Wrong app registration |

---

## Common Authentication Errors

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `AADSTS700016: Application not found` | Incorrect client ID or wrong tenant | Verify app registration exists in the correct tenant |
| `AADSTS65001: User hasn't consented` | API permissions not consented | Admin-consent the permissions in Azure Portal |
| `AADSTS7000218: Invalid client secret` | Secret expired or wrong value | Rotate the client secret |
| `AADSTS50011: Reply URL mismatch` | Redirect URI doesn't match registration | Update redirect URI in app registration |
| `AADSTS50076: MFA required` | Conditional access policy | Use device code flow or handle MFA in interactive flow |
| `401 InsufficientScopes` | Token missing required Fabric scopes | Update `scopes` parameter in MSAL call |
| `403 after successful auth` | Workspace role missing | Assign identity to workspace with Contributor role |
