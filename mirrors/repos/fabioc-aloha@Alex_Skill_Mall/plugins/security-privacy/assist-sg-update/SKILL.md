---
type: skill
lifecycle: stable
inheritance: inheritable
name: assist-sg-update
description: Generate assisted PRs to correct Security Group ownership for first-party apps flagged by S360 tenant-isolation policy (SFI-TI3.2.2)
tier: standard
applyTo: '**/*assist*,**/*update*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

> **This is the primary autofix skill in the s360-tenant-isolation plugin.**
> It generates assisted pull requests to the 1P apps repo that correct Security Group
> ownership for first-party applications flagged by S360 tenant-isolation policy.

---

## Scenarios Covered

### Scenario 1 — 1P App with invalid security group

**Violation title:** "1P App with invalid security group"

**What happened:**
A first-party application's Security Group Owner tenant is either `"Unknown"` or
`"Microsoft"` (the Corp tenant). Neither is a valid production tenant, so the app has
no production governance over its credential boundaries.

**Why this is dangerous:**
Without a production-tenant SG owner the app's lifecycle is ungoverned — credentials
may be accessible from non-production contexts, administrative rights are undefined,
and the app falls outside SFI Tenant Isolation policy.

**Typical underlying data signals:**

| Field | Value |
|---|---|
| SG owner tenant | `"Unknown"` or `"Microsoft"` |
| SG ownership state | Invalid / needs production owner |
| Expected tenant | The app's production tenant |

---

### Scenario 2 — 1P App Cert Tenant Mismatches Security Group Tenant (Option 1: Update SG)

**Violation title:** "1pApp certs Tenant mismatches the Tenant of the Security Group"

**What happened:**
A first-party application's certificate lives in Production Tenant A, but its Security
Group owner lives in Production Tenant B — both within the same cloud. The cert holder
in Tenant A can obtain tokens for resources governed by Tenant B, creating a cross-tenant
credential exposure.

**Why this is dangerous:**
Cross-tenant credential exposure breaks the isolation boundary. An actor with access to
the cert in Tenant A can impersonate the app in Tenant B's resource scope.

**Typical underlying data signals:**

| Field | Condition |
|---|---|
| SG tenant | Does not match the intended certificate/app tenant |
| Expected tenant | The production SG tenant |

> **This skill handles Option 1 only** — updating the Security Group to the correct
> tenant. If the SG is already correct and the *cert* needs to move, redirect the user
> to the `guide-cert-rehoming` skill instead.
>
> **Alternative paths (from TSGs)**:
> - **Scenario 1** (invalid SG — [aka.ms/entraQ9](https://aka.ms/entraQ9)): Option 2 is updating
>   the OneCert domain registration details to match the correct SG tenant.
> - **Scenario 2** (SG/cert mismatch — [aka.ms/entraQ6](https://aka.ms/entraQ6)): Option 2 is
>   moving the certificate to the correct tenant via `guide-cert-rehoming`.

---

## Skill Logic

### Step 1 — Validate the Violation Is SG-Fixable

1. Confirm `Title` / `ViolationTitle` matches one of the two scenarios above.
2. These violation titles are already 1P-specific, so no separate `AppType` check is
   required at runtime.
3. **For Scenario 2 — determine the correct fix direction:**
   - If the user or repo context confirms the **SG is wrong** → proceed with this skill. ✓
   - If the user confirms the **cert is wrong** → redirect to `guide-cert-rehoming`. ✗
   - If the action item alone does not make the direction clear → ask the user to confirm
     before generating any change.

If the violation does not pass validation, stop and explain which condition failed and
what alternative skill or manual process applies.

---

### Step 2 — Extract Target State from Violation Data

Read the following fields from the **normalized violation object** produced by
`fetch-violations` when available:

| Field | Purpose |
|---|---|
| `AppId` | Application (client) ID being fixed |
| `AppDisplayName` | Human-readable app name |
| `TargetId` | S360 target ID for the action item |
| `cloudType` | Cloud context (Public / Fairfax / Mooncake) |
| `ADOWorkItemHTMLUrl` | Reference link for the underlying work item |
| `ActionOwnerAlias` | Current action owner |

The MCP response does **not** include the exact Security Group object or target tenant
name. Treat the SG identity and target tenant as **user-confirmed inputs** if they are
not already known from repo context or the linked work item.

---

### Step 3 — Check Prerequisites

Determine whether the application is **enabled for 1P apps repo management**.

- **If yes** → proceed to Step 4.
- **If no** → surface this as a **blocker** with the following guidance:

> ⚠️ **Blocker — Repo Management Not Enabled**
>
> This application is not yet enabled for 1P apps repo management. SG ownership
> changes can only be submitted as PRs to the 1P apps repo once the app is migrated.
>
> **Action required:** Enable repo management for this app first:
> **https://aka.ms/migrate-1p-repo**
>
> Once migration is complete, re-run this skill to generate the autofix PR.

Do not proceed past this step until the prerequisite is met.

---

### Step 4 — Identify the Correct Security Group

The action item provides app context but usually **not** the specific Security Group object.

1. If the 1P apps repo or first-party portal already identifies the owning SG, use that.
2. If **multiple SGs** are plausible → present the options and ask the user to confirm.
3. If the SG cannot be determined from the available context → ask the user to provide the
   correct SG display name and object ID.

**⚠️ Always surface this caveat to the user:**

> "The action item indicates an SG ownership problem, but the exact Security Group must be
> confirmed before changing governance metadata. Please verify the correct SG name, object
> ID, and owning tenant before proceeding."

Never auto-select an SG without explicit user confirmation. This is a governance-critical
change.

---

### Step 5 — Generate the Assisted Autofix

Produce the 1P apps repo pull request content:

**File to modify:** The app's manifest file in the 1P apps repo (located by `AppId`).

**Change:** Update the Security Group owner field to the confirmed production SG in the
target tenant.

**PR content must include:**

| Section | Content |
|---|---|
| App ID | `{AppId}` |
| App display name | `{AppDisplayName}` |
| Current SG | Existing SG name / object ID if known |
| Target SG | The confirmed Security Group name and object ID |
| Target tenant | The confirmed production tenant |

**PR description must include:**

- The violation title and S360 action item reference (ID / link)
- Current state (wrong SG tenant) → target state (correct SG tenant)
- Policy reference from the SFI-TI-overview policy table (see table below)
- Link to the relevant TSG documentation

Present the full PR content to the user for review **before** submission. Do not
auto-submit.

---

### Step 6 — Post-Fix Validation Guidance

After the PR is merged and Gradual Rollouts propagation completes, instruct the user to
verify the fix:

1. The app's owning Security Group now matches the confirmed production SG.
2. The violation **no longer appears** in the PowerBI dashboard after the next S360 refresh.
3. The repo manifest / app registration reflects the intended governance owner.

> ℹ️ S360 data refreshes every **24 hours**. Allow up to one full refresh cycle before
> expecting dashboard updates.

---

## Policy Reference — SG Owner → Expected Tenant Mapping

Use this table to validate the target tenant against the app's cloud setting and OneCert
configuration.

| 1P App SG Owner Tenant | App Cloud Setting | OneCert Cloud / Environment / Tenant | OneCert Private Issuer | Allowed Vaults | Cert Can Exist on Corp Devices |
|---|---|---|---|---|---|
| AME | Public | Public + Prod + AME | AME | KV and dSMS | No |
| CME / AME / PME | Mooncake | MoonCake + Prod + CME | AME | KV and dSMS | No |
| GME | Public | Public + Prod + GME | AME | KV and dSMS | No |
| MPA | Public | Public + Prod + MPA | AME | KV and dSMS | No |
| PME | Public | Public + Prod + PME | AME | KV and dSMS | No |
| Torus | Public | Public + Prod + Torus | AME | KV and dSMS | No |
| Torus Gallatin / Torus | Mooncake | MoonCake + Prod + Torus Gallatin | AME | KV and dSMS | No |
| Torus ITAR / Torus | Fairfax | FairFax + Prod + Torus ITAR | AME | KV and dSMS | No |
| USME / AME / PME | Fairfax | FairFax + Prod + USME | AME | KV and dSMS | No |

---

## Links

| Resource | URL |
|---|---|
| First-party apps portal | https://aka.ms/firstpartyportal |
| Security Group diagnostics | https://review.learn.microsoft.com/identity/microsoft-identity-platform/security-group-diagnostics-repo |
| Migrate to repo management | https://aka.ms/migrate-1p-repo |
| Gradual Rollouts v2 guidance | https://eng.ms/docs/microsoft-security/identity/entra-developer-application-platform/app-vertical/aad-first-party-apps/identity-platform-and-access-management/microsoft-identity-platform/apps-repo/howto-enable-gradual-rollout-v2 |
| S360 Dashboard | https://vnext.s360.msftcloudes.com/blades/security?blade=KPI:dc1c236d-e85a-413e-bdea-7fc89b096f9f |
| PowerBI violation dashboard | https://msit.powerbi.com/groups/me/apps/ef910c43-608c-4805-97f1-2be4a9e0b65c/reports/18473fb3-640b-44b1-b609-aa9729ea1a12/ReportSection27a0a42071e5023c9da9 |

---

## Important Notes

- **Gradual Rollouts apply.** The 1P apps repo uses Gradual Rollouts — even metadata-only
  changes (like SG ownership) go through staged review and propagation.
- **Repo management must be enabled first.** Apps that have not been migrated to repo
  management cannot have SG changes submitted via PR. Direct the user to
  `aka.ms/migrate-1p-repo` before attempting autofix.
- **SG ownership = administrative rights.** The Security Group controls who can manage the
  application's lifecycle, credentials, and data access. Incorrect SG assignment is a
  governance and security boundary violation.
- **Always confirm the SG with the service owner.** Never auto-select a Security Group.
  The service owner must verify the correct SG before the PR is submitted.
- **Dashboard refresh lag.** S360 data refreshes every 24 hours. Instruct users to wait
  at least one full cycle after PR merge before validating the fix on the dashboard.

## SDP Requirements

> ⚠️ **All production changes must follow SDP:**
> - Use Safe Deployment Orchestrators — [Deploying Change Safely](https://eng.ms/docs/quality/zero-self-inflicted-sev1s/sdpforsfi)
> - C+AI services: submit R2D request at [aka.ms/R2Drequest](https://aka.ms/R2Drequest)
> - Honor CCOA banners: [aka.ms/ccoa](https://aka.ms/ccoa)
> - Use [Gradual Rollouts v2](https://eng.ms/docs/microsoft-security/identity/entra-developer-application-platform/app-vertical/aad-first-party-apps/identity-platform-and-access-management/microsoft-identity-platform/apps-repo/howto-enable-gradual-rollout-v2) for 1P apps repo changes. If not possible, use [Gradual Rollouts (legacy)](https://eng.ms/docs/microsoft-security/identity/entra-developer-application-platform/app-vertical/aad-first-party-apps/identity-platform-and-access-management/microsoft-identity-platform/apps-repo/gradual-rollout-first-party-repo).
> - Livesite mitigations bypassing SDP require executive leader approval.
