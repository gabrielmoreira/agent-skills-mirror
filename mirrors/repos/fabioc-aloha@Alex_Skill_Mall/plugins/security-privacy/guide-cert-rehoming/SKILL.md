---
type: skill
lifecycle: stable
inheritance: inheritable
name: guide-cert-rehoming
description: >
tier: standard
applyTo: '**/*guide*,**/*cert*,**/*rehoming*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Guide: Certificate Rehoming

This skill walks engineers through the end-to-end process of rehoming (moving or
reissuing) certificates so that every production Entra app's credential lives in
the **same tenant and cloud** as the app itself. It covers two primary violation
categories and provides concrete, value-filled remediation steps drawn from the
policy tables below.

---

## Decision Tree

Follow this sequence to determine the correct remediation path:

1. **Confirm violation type** — inspect `Title` / `ViolationTitle` to verify this is a
   cert-rehoming scenario (tenant mismatch or cloud mismatch).
2. **Determine whether this should follow a 1P or 3P path**:
   - If the violation title explicitly says `1P`, use the [1P Policy Table](#1p-applications).
   - Otherwise, use user context or repo ownership to determine whether the app is 1P or 3P.
   - If it is still unclear, ask the user before continuing.
3. **Identify the intended target tenant/cloud** using the action item context, the linked
   TSG, or user confirmation.
4. **Look up OneCert settings** in the appropriate policy table using that target tenant.
5. **Generate step-by-step instructions** with the specific values filled in
   from the table (cloud, environment, issuer, vault type).

---

## Scenario 1 — AAD Entra Apps in Prod Tenants Using Certificates in Non-Prod Tenant

### What Happened

A certificate stored in a **Non-Prod** Azure Key Vault (AKV) or dSMS folder
(e.g., in the Corp tenant) has a `subjectName` that is authorized to an
application registration in a **Production** tenant.

### Threat

An attacker who compromises the non-prod environment can use the certificate to
authenticate as the production app, enabling **lateral movement from non-prod
into production**.

### Fix Paths — 3P Applications

#### Option A — Move the Certificate to the Production Tenant (Recommended)

1. **Create a new Key Vault or dSMS folder** in the correct production tenant
   that matches the app registration.
   - Use ARM/Bicep deployed via Ev2 Managed SDP when possible.
   - Reference the [3P Policy Table](#3p-applications) for the correct tenant
     and allowed vault types.
2. **Update OneCert domain registration subscriptions** to include the new
   Key Vault or dSMS target.
   - Set **Cloud** to the value in the policy table's *OneCert Cloud Setting*
     column.
   - Set **Environment** to the value in the *OneCert Environment Settings*
     column.
3. **Issue a new certificate** in the correct production tenant via OneCert.
   - Private Issuer: **AME** (all tenants use AME as the private issuer).
4. **Modify app configuration** to reference the new certificate.
   - Follow SDP with a **gradual rollout** (canary → pilot → broad).
   - If the service is C+AI, submit an R2D request at <https://aka.ms/R2Drequest>.
   - Honor any active CCOA banners (<https://aka.ms/ccoa>).
5. **Complete end-to-end testing** to confirm the new certificate works in all
   dependent flows.
6. **Verify rollback functionality** — ensure you can revert to the old
   certificate if an issue is discovered during rollout.
7. **Validate the old certificate is no longer in use**, then **revoke** it.
   > ⚠️ Certificate changes are flagged as **top contributors to customer-visible
   > outages**. Never revoke until you have confirmed zero active usage.

#### Option B — Move the App / Resources to the Non-Prod Tenant

Use this path only when moving the certificate is infeasible (e.g., the app
legitimately belongs in a non-prod context).

1. **Transfer the Azure subscription** to the non-prod directory, **OR**
2. **Use the App Rehoming TSG** to migrate the app registration to the tenant
   where the certificate already resides.

### Fix Paths — 1P Applications

#### Option A — Move the Certificate to the SG Owner's Tenant

1. **Create a new Key Vault or dSMS folder** in the SG Owner's tenant.
   - Reference the [1P Policy Table](#1p-applications) for the correct tenant,
     cloud, and vault type.
2. **Update OneCert domain registration** subscriptions to point to the new
   vault.
   - Set **Cloud**, **Environment**, and **Tenant** per the policy table's
     *OneCert Cloud/Environment/Tenant Settings* column.
3. **Issue a new certificate** via OneCert.
   - Private Issuer: **AME**.
4. **Remove the non-prod cert's `subjectName` and `authorityId`** from
   `trustedCertificateSubjects` on the 1P app's service principal.
5. **Validate the old certificate is no longer in use**, then **revoke** it.

> ⚠️ **IMPORTANT**: Moving certificates to a different Key Vault or dSMS folder
> requires a code/configuration change. Ensure the certificate is available in
> **both** environments during the deployment process to prevent downtime.

#### Option B — Move to NPE (Non-Production Environment)

1. Follow the [Test environments and apps](https://review.learn.microsoft.com/identity/microsoft-identity-platform/secure-test-environments?branch=pr-en-us-940) process to migrate the app and its
   certificate into a sanctioned non-production environment.

---

## Scenario 2 — AAD Entra Apps Cloud Mismatches with Cert Cloud

### What Happened

A certificate is stored in **Cloud A** (e.g., Public / Commercial) but the
Entra app registration lives in **Cloud B** (e.g., Fairfax / Mooncake).

### Threat

An attacker who compromises the certificate in Cloud A can authenticate as the
app in Cloud B, enabling **cross-cloud lateral movement**.

### Fix Paths

#### Option 1 — Reissue in the Same Tenant (Key Vault Already Exists in Correct Cloud)

1. **Issue a new certificate** via OneCert / Key Vault or dSMS **in the correct
   cloud**.
   - Use the policy table to confirm the right Cloud and Environment settings.
2. **Revoke / delete the old certificate** following SDP.
   - Validate zero active usage before revocation.

#### Option 2 — Create New Key Vault / dSMS in the Correct Cloud

1. **Create a new Key Vault or dSMS folder** in the correct cloud and tenant.
   - Use ARM/Bicep deployed via Ev2 Managed SDP.
2. **Update OneCert domain registration subscriptions** to include the new
   vault.
3. **Issue a new certificate** in the correct cloud via OneCert.
4. **Update app configuration** to use the new certificate.
   - Follow SDP with a **gradual rollout**.
   - Submit an R2D request for C+AI services (<https://aka.ms/R2Drequest>).
   - Honor CCOA banners (<https://aka.ms/ccoa>).
5. **Validate the old certificate is no longer in use**, then **revoke** it.

#### Option 3 — Legitimate Cross-Cloud Need

If the service **legitimately requires cross-cloud access** (e.g., a data
replication pipeline that spans Public and Fairfax), this skill cannot resolve the violation
directly. Note: cross-cloud FIC is approved for **data-flow scenarios only** — control
plane operations across cloud boundaries are not permitted.

> **→ Redirect to `guide-advanced-remediation`** for Federated Identity
> Credential (FIC) setup guidance, which is the approved pattern for
> cross-cloud authentication without sharing raw certificates.

---

## Cert-Move Option for SG Scenarios

When `assist-sg-update` determines that **Option 2 (move cert)** is the correct
remediation instead of Option 1 (update the Security Group), it delegates to
this skill. In that case:

1. The SG update skill will pass through whatever context it has available
   (typically the violation title, app ID, app display name, cloud, and any user-confirmed
   target tenant or cloud).
2. Enter the [Decision Tree](#decision-tree) at step 2 and proceed as normal.

---

## Policy Tables

### 3P Applications

| 3P App Tenant   | OneCert Cloud Setting | OneCert Environment Settings | OneCert Private Issuer | Allowed Vaults | Cert Can Exist on Corp Devices |
| --------------- | --------------------- | ---------------------------- | ---------------------- | -------------- | ------------------------------ |
| AME             | Public                | Prod + AME                   | AME                    | KV and dSMS    | No                             |
| CME             | Mooncake              | Prod + CME                   | AME                    | KV and dSMS    | No                             |
| GME             | Public                | Prod + GME                   | AME                    | KV and dSMS    | No                             |
| MPA             | Public                | Prod + MPA                   | AME                    | KV and dSMS    | No                             |
| PME             | Public                | Prod + PME                   | AME                    | KV and dSMS    | No                             |
| Torus           | Public                | Prod + Torus                 | AME                    | KV and dSMS    | No                             |
| Torus Gallatin  | Mooncake              | Prod + Torus Gallatin        | AME                    | KV and dSMS    | No                             |
| Torus ITAR      | Fairfax               | Prod + Torus ITAR            | AME                    | KV and dSMS    | No                             |
| USME            | Fairfax               | Prod + USME                  | AME                    | KV and dSMS    | No                             |

### 1P Applications

| 1P App SG Owner Tenant | App Cloud Setting | OneCert Cloud/Environment/Tenant Settings | OneCert Private Issuer | Allowed Vaults | Cert Can Exist on Corp Devices |
| ----------------------- | ----------------- | ----------------------------------------- | ---------------------- | -------------- | ------------------------------ |
| AME                     | Public            | Public + Prod + AME                       | AME                    | KV and dSMS    | No                             |
| CME / AME / PME         | Mooncake          | MoonCake + Prod + CME                     | AME                    | KV and dSMS    | No                             |
| GME                     | Public            | Public + Prod + GME                       | AME                    | KV and dSMS    | No                             |
| MPA                     | Public            | Public + Prod + MPA                       | AME                    | KV and dSMS    | No                             |
| PME                     | Public            | Public + Prod + PME                       | AME                    | KV and dSMS    | No                             |
| Torus                   | Public            | Public + Prod + Torus                     | AME                    | KV and dSMS    | No                             |
| Torus Gallatin / Torus  | Mooncake          | MoonCake + Prod + Torus Gallatin          | AME                    | KV and dSMS    | No                             |
| Torus ITAR / Torus      | Fairfax           | FairFax + Prod + Torus ITAR               | AME                    | KV and dSMS    | No                             |
| USME / AME / PME        | Fairfax           | FairFax + Prod + USME                     | AME                    | KV and dSMS    | No                             |

---

## Key Requirements

> These requirements apply to **every** remediation path above. Do not skip them.

- **SDP (Safe Deployment Practices)** — ALL production changes MUST follow SDP.
  See: <https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi>
- **R2D Approval** — C+AI Services production changes must be submitted through
  R2D at <https://aka.ms/R2Drequest>.
- **Infrastructure as Code** — Use ARM/Bicep deployed via Ev2 Managed SDP when
  creating or modifying Key Vaults and dSMS folders.
- **CCOA Compliance** — Honor Critical Change Only Advisory banners when
  applicable. Check <https://aka.ms/ccoa> before executing changes.
- **Outage Risk** — Certificate changes are flagged as **top contributors to
  customer-visible outages**. Always validate that the old certificate is no
  longer in active use **before** revoking.
- **Gradual Rollout** — Never switch 100% of traffic to a new certificate in a
  single deployment. Use canary → pilot → broad ring progression.
- **Livesite Mitigations** — Livesite mitigations bypassing SDP require executive
  leader approval.

---

## Useful Links

| Resource | URL |
| --- | --- |
| OneCert Portal | <https://onecert.microsoft.com> |
| dSMS Basics | <https://aka.ms/dsmsbasics> |
| ARM/Bicep Key Vault Reference | <https://learn.microsoft.com/azure/templates/microsoft.keyvault/vaults> |
| SDP Guidance | <https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi> |
| S360 Dashboard | <https://vnext.s360.msftcloudes.com/blades/security?blade=KPI:dc1c236d-e85a-413e-bdea-7fc89b096f9f> |
| PowerBI Dashboard Access | CoreIdentity Entitlement → S360ESTSEntraAppsToCertViolationsDashboard |
| R2D Request | <https://aka.ms/R2Drequest> |
| CCOA Status | <https://aka.ms/ccoa> |
| OneCert domain registration | <https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/onecert/docs/registering-a-domain-in-onecert> |
| Create cert from Key Vault | <https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/onecert/docs/requesting-a-onecert-certificate-with-keyvault> |
| Create cert from dSMS | <https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/onecert/docs/requesting-a-onecert-certificate-with-dsms> |
| Internal Stack Overflow | Tags: `[certificate]` + `[entra-apps]` |
