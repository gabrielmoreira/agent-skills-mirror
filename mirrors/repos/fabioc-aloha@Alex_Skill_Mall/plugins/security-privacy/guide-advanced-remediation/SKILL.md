---
type: skill
lifecycle: stable
inheritance: inheritable
name: guide-advanced-remediation
description: >
tier: standard
applyTo: '**/*guide*,**/*advanced*,**/*remediation*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Advanced Remediation Guide

This skill covers **complex multi-step remediation scenarios** for S360 Tenant Isolation violations
that require code changes, Federated Identity Credential (FIC) setup, and/or bilateral coordination
between service teams. These scenarios **cannot be auto-fixed** — they require deliberate action by
service owners.

> **All scenarios require SDP (Safe Deployment Practices).** See:
> <https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi>
>
> **SDP Requirements for ALL scenarios:**
> - Use Safe Deployment Orchestrators — [Deploying Change Safely](https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi)
> - C+AI services: submit R2D request at [aka.ms/R2Drequest](https://aka.ms/R2Drequest)
> - Honor CCOA banners: [aka.ms/ccoa](https://aka.ms/ccoa)
> - Complete end-to-end testing including KPI impact test cases
> - Verify rollback functionality for each change
> - Livesite mitigations bypassing SDP require executive leader approval

---

## Violation-to-Scenario Routing

| Violation Title | Scenario |
|---|---|
| AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud auth scenarios | [Scenario A](#scenario-a-cross-cloud-auth-infrastructure-apps) |
| AAD Entra Apps cloud mismatches with Cert Cloud - Cross-cloud 1P scenarios | [Scenario B](#scenario-b-cross-cloud-1p-scenarios) |
| AAD Entra apps with cross-tenant violations | [Scenario C](#scenario-c-cross-tenant-violations) |
| Connector domain OWNER should not use shared subjectName for authentication across tenant | [Scenario D](#scenario-d-connector-domain-owner-shared-subjectname) |
| Connector domain CONSUMER should not use shared subjectName for authentication across tenant | [Scenario E](#scenario-e-connector-domain-consumer-shared-subjectname) |

---

## Reference Tables

These tables are used across multiple scenarios. Keep them handy.

### Cloud Hostnames

| Cloud | Hostname |
|---|---|
| Public (Azure Commercial) | `login.microsoftonline.com` |
| Fairfax (Azure Government) | `login.microsoftonline.us` |
| Mooncake (Azure China / 21Vianet) | `login.partner.microsoftonline.cn` |

### Infrastructure Tenant IDs

| Tenant | Tenant ID |
|---|---|
| AME | `33e01921-4d64-4f8c-a055-5bdaffd5e33d` |
| PME | `975f013f-7f24-47e8-a7d3-abc4752bf346` |
| GME | `124edf19-b350-4797-aefc-3206115ffdb3` |
| CME | `a55a4d5b-9241-49b1-b4ff-befa8db00269` |
| USME | `cab8a31a-1906-4287-a0d8-4eef66b95f6e` |
| Torus | `cdc5aeea-15c5-4db6-b079-fcadd2505dc2` |
| Torus ITAR | `a972b02b-2e02-4381-9dda-f8c703e9d5b9` |
| Torus Gallatin | `d294a672-1e15-47e3-b224-84ff4f6f24d5` |

### MSS (Microsoft Services) Tenant IDs

| Cloud | Tenant ID |
|---|---|
| Public MSS | `f8cdef31-a31e-4b4a-93e4-5f571e91255a` |
| Fairfax MSS | `f8cdef31-a31e-4b4a-93e4-5f571e91255a` |
| Mooncake MSS | `0b4a31a2-c1a0-475d-b363-5f26668660a3` |

### Base64url-Encoded Tenant IDs (for Connector Scenarios D & E)

| Encoded Value | Tenant (Tenant ID) |
|---|---|
| `IRngM2RNjE-gVVva_9XjPQ` | AME (`33e01921-4d64-4f8c-a055-5bdaffd5e33d`) |
| `PwFflyR_6Een06vEdSvzRg` | PME (`975f013f-7f24-47e8-a7d3-abc4752bf346`) |
| `v4j5cvGGr0GRqy180BHbRw` | MSIT (`72f988bf-86f1-41af-91ab-2d7cd011db47`) |
| `6q7FzcUVtk2wefyt0lBdwg` | Torus (`cdc5aeea-15c5-4db6-b079-fcadd2505dc2`) |

### Token Exchange Audiences

| Cloud | Audience URI |
|---|---|
| Public | `api://AzureADTokenExchange` |
| Fairfax (US Gov) | `api://AzureADTokenExchangeUSGov` |
| Mooncake (China) | `api://AzureADTokenExchangeChina` |

---

## Scenario A: Cross-Cloud Auth — Infrastructure Apps

> **Violation**: "AAD Entra Apps cloud mismatches with Cert Cloud – Cross-cloud auth scenarios"
> (applies to infrastructure tenants: \*ME and Torus)

### What Happened

An infrastructure app (in an \*ME or Torus tenant) shares SN+I (Subject Name + Issuer)
configuration across clouds. The same certificate credential is used to authenticate in
multiple cloud environments.

### Threat

Cross-cloud lateral movement across sovereign boundaries. An attacker who compromises a
credential in one cloud could pivot to another sovereign cloud.

### Allowed Cross-Cloud Combinations (Infrastructure Tenants ONLY)

Only these combinations are permitted for infrastructure tenants:

| Source Cloud | Target Cloud |
|---|---|
| Public \*ME | Mooncake CME |
| Public \*ME | Fairfax USME |
| Torus Public | Torus Mooncake / Gallatin |
| Torus Public | Torus ITAR |

Any other cross-cloud combination is **not allowed** and must be remediated differently
(e.g., separate credentials per cloud, no cross-cloud auth).

### 5-Step FIC Resolution Process

#### Step 1: Create a Multi-Tenanted Application in the Source Cloud

The source cloud is **where your compute lives** (where the workload runs).

- Register a new application (or use your existing one) in the source cloud's Entra ID.
- The application **must be configured as multi-tenant** so it can issue tokens recognized
  across tenant boundaries.

#### Step 2: Configure Target Identity in the Target Cloud

The target cloud is **where the resource you need to access lives**.

Choose one of these options:

| Option | Description | When to Use |
|---|---|---|
| **Option A: Managed Identity** (preferred) | Use an Azure Managed Identity in the target cloud | When your target workload runs on Azure compute that supports MI |
| **Option B: Single-Tenant Application (STA)** | Register a single-tenant app in the target cloud | When MI is not available or the target resource requires an app registration |

#### Step 3: Register Identities on the Entra ID Allowlist

Submit a PR to the Entra ID allowlist via the **Self-Service Guide for XCloud FIC**:

- **Portal**: <https://identitydivision.visualstudio.com/IdentityWiki/_wiki/wikis/IdentityWiki.wiki/69678/Self-Service-Guide-Managing-XCloud-FIC-Allow-Listed-Identities-in-Infra-Tenants>
- Include both the source identity and target identity in the PR.
- **Timeline**: Allowlist PRs take **3–4 weeks** to complete due to STS re-deployment cycles.

> ⚠️ **Plan ahead.** The 3–4 week lead time is the longest step in this process.

#### Step 4: Configure FIC Entry on the Target Identity

Once the allowlist PR is merged and deployed, configure the Federated Identity Credential
on the **target identity** (the MI or STA from Step 2):

| FIC Field | Value |
|---|---|
| **Issuer** | `https://<Source Cloud Hostname>/<Source Tenant ID>/v2.0` |
| **Subject** | Source Identity's Service Principal **ObjectID** |
| **Audience** | Target cloud's token exchange URL (see [Token Exchange Audiences](#token-exchange-audiences)) |

**Example** — Source in Public AME, Target in Mooncake CME:

```
Issuer:   https://login.microsoftonline.com/33e01921-4d64-4f8c-a055-5bdaffd5e33d/v2.0
Subject:  <Source app's Service Principal ObjectID>
Audience: api://AzureADTokenExchangeChina
```

> 🔒 **Constraint**: Only **ONE** FIC entry is allowed per target identity for cross-cloud
> scenarios. If you need multiple source identities, you need multiple target identities.

#### Step 5: Grant Permissions to Target Identity

- Assign the necessary RBAC roles and/or API permissions to the **target identity** for
  accessing the target resource.
- Validate with least-privilege principles.

### Code Change Required

Your application code must implement a **two-step MSAL token exchange**:

1. **Step 1 — Get source cloud token**: Authenticate as the source identity in the source
   cloud using MSAL. This returns an access token scoped to the source cloud.
2. **Step 2 — Redeem for target cloud token**: Use the source cloud token as a client
   assertion to request a token from the target cloud's STS, targeting the FIC-configured
   target identity.

```text
[Source Cloud]                          [Target Cloud]
     |                                       |
     |  1. MSAL: get token (source MI/app)   |
     |-------------------------------------->|
     |  2. Use source token as assertion     |
     |     to redeem for target cloud token  |
     |-------------------------------------->|
     |  3. Access target resource             |
     |-------------------------------------->|
```

Refer to MSAL library documentation for the specific API calls for cross-cloud token exchange.

---

## Scenario B: Cross-Cloud 1P Scenarios

> **Violation**: "AAD Entra Apps cloud mismatches with Cert Cloud – Cross-cloud 1P scenarios"

### What Happened

A first-party (1P) application in one cloud has SN+I referencing a certificate from another
cloud. Unlike Scenario A (infrastructure tenants), this involves 1P apps operating across
cloud boundaries.

### Eligible Cross-Cloud Directions

#### GCC (Government Community Cloud) Scenarios

| Source Cloud | Target Cloud |
|---|---|
| Fairfax USME | Public — GCC-marked tenant |
| Torus ITAR | Public — GCC-marked tenant |

#### Generic 1P Cross-Cloud Scenarios

| Source Cloud | Target Cloud |
|---|---|
| Public | Mooncake — customer tenant |
| Public | Fairfax — customer tenant |
| Mooncake — customer tenant | Public |
| Fairfax — customer tenant | Public |

### 5-Step Resolution

#### Step 1: Promote / Register Target Identity App to Source Cloud

Use the **1P apps repo** to promote or register the target identity application into the
source cloud:

- **1P apps promotion portal**: <https://eng.ms/docs/microsoft-security/identity/entra-developer-application-platform/app-vertical/aad-first-party-apps/identity-platform-and-access-management/microsoft-identity-platform/apps-repo/repo-national-clouds-author-promotion>
- This ensures the target identity is recognized in the source cloud's directory.

#### Step 2: Register Identity on the Entra ID Allowlist

Submit a PR to the Entra ID allowlist:

- Categorize the entry correctly: **GCC** or **cross-cloud** (this determines routing).
- **Portal**: <https://identitydivision.visualstudio.com/IdentityWiki/_wiki/wikis/IdentityWiki.wiki/72932/Self-Service-Guide-Managing-XCloud-FIC-for-1P-apps>
- **Timeline**: **3–4 weeks** for STS re-deployment.

#### Step 3: Configure FIC for Target Identity (in Git Repo Manifest)

This is the **key difference from Scenario A**: 1P scenarios use `claimsMatchingExpression`
(flexible FIC) instead of the standard `subject` identifier.

**Option A — Git repo manifest (preferred for 1P)**:

Configure FIC in the 1P app's Git repo manifest using a `claimsMatchingExpression`:

```json
{
  "name": "<scenario-name, e.g. x-cloud-fic-fpa-gcc>",
  "issuer": "https://login.microsoftonline.com/<SourceTenantId>/v2.0",
  "claimsMatchingExpression": {
    "value": "claims['azp'] eq '<1P_App_Client_ID>'",
    "languageVersion": 1
  },
  "description": "Cross cloud FIC for first party app",
  "audiences": ["<TargetCloudTokenExchangeAudience>"]
}
```

This matches on the `azp` (authorized party) claim, which identifies the calling 1P app.

> 🔒 **Constraint**: Only **ONE** FIC entry of this sort can be configured on the target identity.
> It is solely dedicated to a particular cross-cloud scenario and cannot be reused to establish
> connectivity with other clouds.

**Option B — PowerShell cmdlet**:

```powershell
Set-ApplicationProperty -AppId <TargetAppId> `
  -Env Production `
  -Property federatedIdentityCredentials `
  -NewValue '{"name":"x-cloud-fic","issuer":"https://login.microsoftonline.com/<SourceTenantId>/v2.0","claimsMatchingExpression":{"value":"claims[''azp''] eq ''<1P_App_Client_ID>''","languageVersion":1},"description":"Cross cloud FIC","audiences":["<TargetCloudTokenExchangeAudience>"]}' `
  -ChangeType Add
```

#### Step 4: Confirm Target Identity Has Required Permissions

- Verify that the target identity has all necessary API permissions and RBAC roles for the
  target resource.
- For GCC scenarios, ensure the GCC-marked tenant grants consent.

#### Step 5: Update Source Identity App Code

Implement the same **two-step MSAL token exchange** as Scenario A:

1. Acquire a token as the source identity in the source cloud.
2. Redeem that token for a target cloud token via the FIC-configured target identity.

> ⚠️ **Important**: The first request must be made in the context of the MSS (Microsoft Services)
> tenant. It should be performed in the tenant in which the application compute (and Key Vault)
> are located.

### Key Differences from Scenario A (Infrastructure)

| Aspect | Scenario A (Infrastructure) | Scenario B (1P) |
|---|---|---|
| FIC matching | `subject` (Service Principal ObjectID) | `claimsMatchingExpression` (`azp` claim) |
| App registration | Standard multi-tenant app | 1P apps repo promotion |
| Allowlist categorization | Cross-cloud | GCC or cross-cloud |
| Tenant scope | \*ME / Torus tenants | MSS and customer tenants |

---

## Scenario C: Cross-Tenant Violations

> **Violation**: "AAD Entra apps with cross-tenant violations"

### What Happened

A certificate stored in Azure Key Vault in **Production Tenant A** is used as a credential
for an application registered in **Production Tenant B**. The same cert is shared across
tenant boundaries.

### Threat

Cross-tenant lateral movement. Compromise of the certificate in Tenant A could allow an
attacker to authenticate as the app in Tenant B.

### Remediation

#### Step 1: Create a New App Registration in Tenant A

Register a new application in **Tenant A** (the tenant where the Azure Key Vault with the
certificate resides). This app will be the source identity.

#### Step 2: Configure the App as Multi-Tenant

Set the app's `signInAudience` to `AzureADMultipleOrgs` so it can authenticate across
tenant boundaries via a legitimate, controlled mechanism.

#### Step 3: Review the Entra Application Layering Policy

Before proceeding, review the **Entra Application Layering Policy** to ensure your
cross-tenant architecture is compliant. This policy governs how applications can layer
across tenant boundaries.

#### Step 4: Create a Service Principal in Tenant B

Cross-tenant Service Principals can **only be created via an approved request process**.

**Information to gather before submitting**:

| Field | Description |
|---|---|
| App ID | Client ID of the app from Step 1 |
| App home tenant | Tenant A's tenant ID |
| Target tenant | Tenant B's tenant ID |
| Resources needed | Which APIs/resources in Tenant B the app needs to access |
| RBAC roles | Required Azure RBAC role assignments |
| Graph permissions | Required Microsoft Graph API permissions |
| Scenario description | Business justification for cross-tenant access |

**Contact**: [ptmcontact@microsoft.com](mailto:ptmcontact@microsoft.com) for cross-tenant
and cross-cloud topics. The PTM team manages the approved request process.
Refer to the [App consent and permissions request](https://eng.ms/docs/microsoft-security/digital-security-and-resilience/iamprotect/production-tenant-management-and-security/production-tenant-management/production-tenant-docs/forserviceandserviceowners/production/appconsentandperms) guidance to start the process.

> ⚠️ **Key constraint**: Cross-tenant SPs can **only** be created by approved request —
> follow the PTM process. Do not attempt to create them directly.

#### Step 5: Follow JIT Guidance for Production Changes

Apply **Just-In-Time (JIT)** access principles for all production changes:

- Use PIM (Privileged Identity Management) for role activation.
- Scope permissions to the minimum required.
- Set expiration on elevated access.

---

## Scenario D: Connector Domain OWNER — Shared SubjectName

> **Violation**: "Connector domain OWNER should not use shared subjectName for authentication
> across tenant"

### What Happened

A service **Owner** uses a shared SN+I (Subject Name + Issuer) to impersonate Consumer
partner applications across tenants. The same credential chain is shared between the Owner
and Consumer, creating a cross-tenant trust relationship via shared SN+I.

### Threat

Cross-tenant impersonation via shared SN+I. The Owner can authenticate as if it were the
Consumer's app, or vice versa.

### Owner Resolution Process

#### Step 1: Contact the Consumer Team

**Do this first.** Bilateral coordination is required. The Consumer team needs to configure
FIC on their side (see [Scenario E](#scenario-e-connector-domain-consumer-shared-subjectname)).

Agree on:
- Timeline for migration
- The unique subject identifier (you will provide this in Step 2)
- Testing and validation plan

#### Step 2: Provide Unique Subject Identifier to Consumer

Generate and share the following unique subject identifier with the Consumer team:

```
/eid1/c/pub/t/{Base64url(TenantB)}/a/{Base64url(OwnerAppId)}/{YOUR_APP_ID}
```

Where:
- `{Base64url(TenantB)}` — Base64url-encoded Tenant ID of the **Consumer's** tenant (Tenant B)
  (see [Base64url-Encoded Tenant IDs](#base64url-encoded-tenant-ids-for-connector-scenarios-d--e))
- `{Base64url(OwnerAppId)}` — Base64url-encoded Application ID of the Owner's app
- `{YOUR_APP_ID}` — The literal Application (Client) ID assigned to the Owner app

**Example** (Owner in AME tenant):

```
/eid1/c/pub/t/IRngM2RNjE-gVVva_9XjPQ/a/{Base64url(OwnerAppId)}/{OwnerAppClientId}
```

#### Step 3: Consumer Configures FIC

The Consumer team configures FIC on their side using the subject identifier you provided.
See [Scenario E](#scenario-e-connector-domain-consumer-shared-subjectname) for their steps.

Wait for the Consumer to confirm that FIC is configured before proceeding to update your code.

#### Step 4: Update Owner Code

Modify your application code to use the new FIC-based authentication flow.
The Owner service can continue to use their existing authentication method (SN+I or MSI+FIC)
for Request 1. MSI+FIC is the most recommended method. Request 2 uses the token from
Request 1 (`<token t1>`) as the `client_assertion`:

**Request 2 (new)** — Get FIC token from STS:

```http
POST https://login.microsoftonline.com/<ConsumerTenantB_Id>/oauth2/v2.0/token

grant_type=client_credentials
&client_id=<OwnerAppId>
&client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
&client_assertion=<token t1>
&scope=api://AzureADTokenExchange/.default
&fmi_path=/eid1/c/pub/t/{Base64url(TenantB)}/a/{Base64url(OwnerAppId)}/{YOUR_APP_ID}
```

The `fmi_path` parameter tells STS to issue a token that can be used as a FIC assertion
for the Consumer's target identity.

**Request 3** — Redeem FIC token for Consumer's token:

Use the FIC token from Request 2 as a client assertion to get a token for the Consumer's
resource in the Consumer's tenant.

> ⚠️ **Scope constraint**: Request 3 **cannot** use `api://AzureADTokenExchange` as the scope.
> At this point no more FIC tokens can be issued. The scope must be the actual target resource
> (e.g., `https://graph.microsoft.com/.default`).

#### Step 5: Handle MSAL Cache Partitioning

> ⚠️ **Known Issue**: MSAL's token cache does **not** use `fmi_path` as a cache partition
> key. This means tokens acquired with different `fmi_path` values may collide in the cache.

**Required**: Implement **custom cache partitioning** that includes the `fmi_path` value
in the cache key. Without this, your application may return incorrect cached tokens when
communicating with multiple Consumer partners.

```text
Cache Key = {client_id}:{tenant_id}:{scope}:{fmi_path}
```

---

## Scenario E: Connector Domain CONSUMER — Shared SubjectName

> **Violation**: "Connector domain CONSUMER should not use shared subjectName for
> authentication across tenant"

### What Happened

A service **Consumer** uses the Owner's shared SN+I certificate to authenticate. The
Consumer relies on a credential controlled by the Owner, creating a dependency and a
cross-tenant trust vulnerability.

### Consumer Resolution Process

#### Step 1: Prerequisites — Owner Must Initiate

This is a **bilateral process**. The Owner team must:

1. Contact the Consumer team first.
2. Provide the unique subject identifier (see
   [Scenario D, Step 2](#step-2-provide-unique-subject-identifier-to-consumer)).

**Do not proceed** until you have received the subject identifier from the Owner team.

#### Step 2: Configure FIC on AAD Single-Tenant Application

Configure a Federated Identity Credential on your application. You can do this via the
**Azure Portal** or the **Microsoft Graph API**.

##### Azure Portal Method

1. Navigate to your application in **Entra ID → App registrations**.
2. Go to **Certificates & secrets → Federated credentials → Add credential**.
3. Select **Federated credential scenario**: `Other issuer`.
4. Fill in the fields:

| Field | Value |
|---|---|
| **Issuer** | `https://login.microsoftonline.com/<TenantB_ID>/v2.0` |
| **Subject** | `/eid1/c/pub/t/{Base64url(TenantB)}/a/{Base64url(OwnerAppId)}/{assigned_id}` |
| **Audience** | `api://AzureADTokenExchange` |

Where:
- `<TenantB_ID>` — The Consumer's Tenant ID (Tenant B — provided by the Owner team)
- The **Subject** value is the exact string provided by the Owner team in Step 1
- **Audience** is `api://AzureADTokenExchange` (fixed value per TSG — do **not** use cloud-specific variants for connector scenarios)

#### Step 3: Or Configure FIC for Managed Identity

If using a Managed Identity instead of an app registration:

1. Navigate to your Managed Identity in the Azure Portal.
2. Go to **Federated credentials** under the **Settings** blade.
3. Add a federated credential with the same **Issuer**, **Subject**, and **Audience**
   values as Step 2.

#### Step 4: Graph API Options

For automation or programmatic setup, use the Microsoft Graph API:

**For App Registrations**:

```http
POST https://graph.microsoft.com/v1.0/applications/{ObjectId}/federatedIdentityCredentials

{
  "name": "fic-owner-connector",
  "issuer": "https://login.microsoftonline.com/<TenantB_ID>/v2.0",
  "subject": "/eid1/c/pub/t/{Base64url(TenantB)}/a/{Base64url(OwnerAppId)}/{assigned_id}",
  "audiences": ["api://AzureADTokenExchange"],
  "description": "FIC for Owner connector migration from shared SNI"
}
```

**For Managed Service Identities (MSI)**:

```http
POST https://graph.microsoft.com/v1.0/servicePrincipals/{ObjectId}/federatedIdentityCredentials

{
  "name": "fic-owner-connector-msi",
  "issuer": "https://login.microsoftonline.com/<TenantB_ID>/v2.0",
  "subject": "/eid1/c/pub/t/{Base64url(TenantB)}/a/{Base64url(OwnerAppId)}/{assigned_id}",
  "audiences": ["api://AzureADTokenExchange"],
  "description": "FIC for Owner connector migration (MSI target)"
}
```

#### Step 5: Remove Old Shared SN+I Configuration

After FIC is configured and validated, **remove the old shared SN+I configuration** from
your trust settings. Without this step, the cross-tenant vulnerability persists because the
shared certificate credential remains active.

#### Step 6: Notify the Owner Service Team

Contact the Owner service team and provide them with confirmation that FIC is configured
and operational. The Owner team will update their code to acquire the FIC token, completing
the entire process.

---

## Common Links & Resources

| Resource | Link |
|---|---|
| Entra ID allowlist self-service (infra tenants) | <https://identitydivision.visualstudio.com/IdentityWiki/_wiki/wikis/IdentityWiki.wiki/69678/Self-Service-Guide-Managing-XCloud-FIC-Allow-Listed-Identities-in-Infra-Tenants> |
| Entra ID allowlist self-service (1P apps) | <https://identitydivision.visualstudio.com/IdentityWiki/_wiki/wikis/IdentityWiki.wiki/72932/Self-Service-Guide-Managing-XCloud-FIC-for-1P-apps> |
| 1P apps promotion | <https://eng.ms/docs/microsoft-security/identity/entra-developer-application-platform/app-vertical/aad-first-party-apps/identity-platform-and-access-management/microsoft-identity-platform/apps-repo/repo-national-clouds-author-promotion> |
| PTM contact (cross-tenant & cross-cloud) | [ptmcontact@microsoft.com](mailto:ptmcontact@microsoft.com) |
| SDP guidance | <https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi> |
| Error code lookup | `https://login.microsoftonline.com/error?code=AADSTSxxxxxxx` (replace with actual code) |
| FIC troubleshooting | Refer to Entra ID FIC documentation for common errors and resolution steps |

---

## Important Notes

1. **All scenarios require SDP** — Safe Deployment Practices must be followed for every
   production change. No exceptions.

2. **Cross-cloud allowlist PRs take 3–4 weeks** — This is due to STS re-deployment cycles.
   Plan your remediation timeline accordingly and submit the PR as early as possible.

3. **FIC constraint: ONE entry per target identity for cross-cloud** — If you need
   multiple source identities to access the same target, you must create separate target
   identities (one per source).

4. **MSAL cache partitioning is a known issue** — For connector scenarios (D & E), the
   MSAL library does not use `fmi_path` as a cache key. You **must** implement custom
   cache partitioning to avoid token confusion.

5. **These scenarios CANNOT be auto-fixed** — Every scenario in this guide requires
   service owner code changes and/or bilateral coordination between teams. There is no
   automated remediation path.

6. **Bilateral coordination is mandatory for connector scenarios** — Scenarios D and E
   are two halves of the same remediation. The Owner and Consumer teams must coordinate
   timing, share subject identifiers, and validate together.

7. **Test in a non-production environment first** — Especially for cross-cloud FIC and
   connector migrations, validate the full token exchange flow in a test tenant before
   applying changes to production.
