---
name: workbench-request-app-registration
plugin: workbench-setup
description: Guides the pre-work before any SharePoint use case that connects to a live tenant. Two distinct app-registration types exist for two distinct purposes (unattended App-Only/certificate for scheduled jobs, interactive/delegated for human-operator provisioning) -- this skill documents both, generates a filled service-request document for your tenant/cloud administrator, and provides the step-by-step setup sequence once granted (Entra API permissions, admin consent, Enterprise Application user assignment, and the separate PnP PowerShell site-level grant). No network I/O -- pure templating and reference data only.
allowed-tools: Bash, Read
examples:
  - "python -c \"from app_registration_request import REGISTRATION_TYPES; print(REGISTRATION_TYPES[0]['key'])\""
---

# Request App Registration

## Trigger and Purpose

Use this skill **before** `initialize-workbench-config` or `validate-workbench-environment`'s
live checks -- it answers "what do I even ask my tenant administrator for,
and what do they need to do once they grant it," not "is my connection
working." No SharePoint use case that touches a live tenant can proceed
without this groundwork.

Three capabilities, all pure (no I/O):

1. **`REGISTRATION_TYPES`** -- two distinct app-registration types exist
   for two distinct purposes. Requesting the wrong one is a real source
   of confusing Access Denied errors later.
2. **Generate a filled service-request document** from caller-supplied
   answers, ready to submit to a cloud/IT team.
3. **`SETUP_STEPS`** -- the generalized, step-by-step sequence for
   configuring the registration once your tenant administrator creates
   one.

## ⚠️ Read this before trusting any tier/capability claim below

An earlier version of this skill claimed the PnP site-grant tier
(`Write` vs `Manage`) reliably predicts whether an app can create lists/
libraries -- `Write` blocking it, `Manage` allowing it. **Production
testing disproved this.** A tenant administrator confirmed via
`Get-PnPAzureADAppSitePermission` that the interactive registration's
stored grant role is `write` on the tested production sites, yet an
interactive session using that same registration successfully created
and removed lists, document libraries, pages, items, and files.

**`CreateList` succeeding is not proof of a `Manage` grant.** Two
explanations, not yet fully disambiguated:

1. Microsoft's current Sites.Selected documentation defines `write` as
   "read and modify metadata and content of the resource" -- it does
   not document list/library creation as excluded. The stricter
   Write-excludes-structure mapping this skill previously encoded came
   from older, possibly outdated or context-specific community
   guidance, not Microsoft's own current model.
2. For delegated (interactive) sessions specifically, Microsoft's
   documented model is that effective access is the **intersection** of
   the app's consented permission and the signed-in user's own
   SharePoint permission on the site. If the signed-in user already
   holds elevated rights (e.g. Site Collection Administrator)
   independent of the app's own grant, that alone could explain the
   observed capabilities -- and in fact, the signed-in test account
   couldn't even *read* the stored grant (`Get-PnPAzureADAppSitePermission`
   returned `403 Forbidden` without tenant-admin rights), which is
   itself evidence its effective permissions come from somewhere other
   than a queried app grant. Worth noting: the intersection model is
   specifically documented for Graph token enforcement, while
   `Connect-PnPOnline -Interactive` requests a SharePoint-resource token
   via a different, older OAuth path -- and this app's `Sites.Selected`
   permission is Application-type only (no Delegated-type SharePoint
   permission exists on it). Whether that path even consults an
   Application-type grant at all is itself unconfirmed.

**A single test cannot disambiguate these -- neither explanation should
be presented as settled.** Doing so requires re-running the same probe
as a user with genuinely low/no elevated permission on the site, or in
`-AuthMode Certificate` (isolates the app grant alone, no user-permission
variable) -- neither has been done yet. **Do not treat list/library
creation as a tier signal for any registration.** Use
`scripts/test-pnp-effective-capability-probe.ps1` to observe actual
behavior, and always report the stored grant role and the observed
capabilities as two separate things -- never conflated, and never as
proof of which explanation above is correct.

## 1. Two registration types -- pick the right one

```python
from app_registration_request import REGISTRATION_TYPES

for t in REGISTRATION_TYPES:
    print(t["key"], "-", t["purpose"])
    print("  capability_testing_status:", t["capability_testing_status"])
```

### `etl` -- unattended App-Only, certificate auth

| | |
|---|---|
| Purpose | Scheduled/unattended jobs (nightly ETL, sync) with no human present |
| Auth | X.509 certificate, no MFA, runs as the app's own service principal |
| Graph / SharePoint permission | `Sites.Selected` (Application) / `Sites.Selected` (Application) |
| PnP site grant tier | `Write` (intended/requested) |
| Licensing | **None** -- authenticates as the app itself, not a signed-in user |
| Capability status | **UNVERIFIED against production.** Intended for pure item CRUD against pre-provisioned lists, not structural provisioning -- but whether `Write` actually enforces that boundary has not been tested with this app's own certificate. Run the probe in `-AuthMode Certificate` before trusting any specific claim. |

**Pros:** no human/MFA dependency, no licence cost, narrowest tier
*requested* for the job (actual enforced boundary unverified).
**Cons:** certificate lifecycle is an operational burden (expiry,
rotation, secure key storage), harder to audit "who did this" (every
action attributed to the service principal), and its actual capability
boundary is unproven -- don't assume it's limited to item CRUD just
because that's what was requested.

### `interactive` -- human-operator, delegated auth

| | |
|---|---|
| Purpose | Provisioning/migration work by a person (or service account acting on a person's behalf) |
| Auth | Interactive sign-in (browser or device code), MFA on every session, no certificate |
| Graph / SharePoint permission | `Sites.Selected` (Application) + `User.Read` (Delegated) / `Sites.Selected` (Application) |
| PnP site grant tier | `write` -- confirmed by a tenant administrator via `Get-PnPAzureADAppSitePermission` against production |
| Licensing | M365 E3 or E5 required for whichever account signs in |
| Capability status | **Corrected 2026-08-09.** Observed in production on tested target sites: list/library/page creation, item and file CRUD, **and site-column and content-type creation** all succeeded -- every content/schema-provisioning operation `sharepoint-provisioning` needs, despite the stored grant being `write`, not `manage`. Group/permission-management operations remain the one category still observed blocked (trial-tenant testing only, unverified against production). See the warning banner above for why this doesn't prove `write` is broader than documented; it may instead mean the signed-in user's own permissions are doing the work, not the app's grant -- see `references/effective-permissions-matrix.md`'s Test A/B/C for how to actually disambiguate. |

**Same Entra-level API permission as the ETL type** -- confirmed on a
real production tenant, both registrations show `Sites.Selected`
(Application). The two types are differentiated by auth mechanism, not
by a different Entra permission.

**Group operations (create/membership/delete) were observed blocked**
in earlier trial-tenant testing, treated as a deliberate design decision
(site permission groups managed manually by admins) rather than a
permission gap -- but this finding predates the write-vs-capability
correction above and has not been independently re-verified against
production. Treat as plausible, not confirmed.

**Pros:** in production, interactive sessions with this registration
have performed the full provisioning/migration surface (though whether
that's the app's own grant or the signed-in user's permissions is
unresolved); delegated auth means effective access is at most the
signed-in user's own SharePoint permissions -- the app can never exceed
what the user could already do. **Cons:** every operation needs a human
+ MFA (not for unattended jobs), recurring per-account licence cost, and
the stored grant role does not reliably predict what the app can
actually do -- don't rely on the Entra/PnP-recorded tier alone.

## 2. Generate a service-request document

```python
from app_registration_request import render_service_request, AppRegistrationRequestError

with open("assets/service-request-interactive-registration-template.md") as f:
    template = f.read()

rendered = render_service_request(template, answers)
# raises AppRegistrationRequestError naming every <PLACEHOLDER> missing an answer
```

Two templates available in `assets/`, one per registration type above:

- `service-request-interactive-registration-template.md`
- `service-request-application-registration-template.md`

`render_service_request` is pure string templating -- it never leaves an
unfilled `<PLACEHOLDER>` token in a document meant to be submitted; it
raises `AppRegistrationRequestError` naming exactly what's missing
instead.

## 3. The setup sequence (`SETUP_STEPS`)

Covers **two separate control planes** that are easy to conflate but both
required:

```python
from app_registration_request import SETUP_STEPS

for step in SETUP_STEPS:
    print(f"{step['number']}. {step['title']}")
    print(f"   {step['detail']}")
```

1. Decide which registration type you need (see `REGISTRATION_TYPES` above).
2. Request the app registration (redirect URI for interactive; certificate for App-Only).
3. Request the API permissions matching your type.
4. Assign users/service accounts to the Enterprise Application entry --
   **interactive only**, before admin consent. A user missing from this
   list can often still sign in successfully and only fail later with
   access-denied/app-assignment errors that look like a permissions
   problem -- check this list first if that happens.
5. Grant admin consent.
6. Tenant admin (a SharePoint Admin specifically -- non-admin gets
   Access Denied, the correct security boundary) runs
   `Grant-PnPAzureADAppSitePermission` once per target site, requesting
   the tier matching your type's intended purpose. This is the second
   control plane -- step 3's Entra permission only enables this
   mechanism to exist, and it must be repeated per site. **Do not
   assume the tier requested here predicts the actual capability
   boundary** -- see the warning banner above.
7. **Populate this repository's root `config.psd1` with the new registration**
   -- run `initialize-workbench-config` (`config_setup.write_config`),
   don't hand-edit the file. Easy to skip because it feels like a
   detour, but step 8's live scripts default to reading `ClientId`/
   `TenantId` from `config.psd1` -- skip this and step 8 either fails
   outright or silently validates the wrong registration against a
   stale config. For a certificate-based (ETL) registration, pass
   `-ClientId`/`-TenantId`/`-CertThumbprint` explicitly to the probe
   instead -- this repo's `config.psd1` schema has no canonical
   certificate-thumbprint field yet.
8. Validate end-to-end via `test-pnp-effective-capability-probe.ps1` --
   report the stored grant role and observed capabilities separately,
   and test an App-Only registration with `-AuthMode Certificate` and
   its own credentials; an interactive-session probe never validates a
   different, certificate-based registration.

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library. The live PowerShell probe
additionally requires `pwsh` and the `PnP.PowerShell` module on PATH.

## References and assets

- `references/effective-permissions-matrix.md` -- **start here for any
  "why did/didn't this operation work" question.** Synthesizes all
  three independent axes that determine effective access (SharePoint
  site-level user permissions, Entra/Graph app API permissions, PnP
  site-grant tiers), the role-vocabulary mismatch between them, the
  documented delegated-access intersection model, and a checklist for
  reasoning through an unexpected pass/fail result.
- `references/app-registration-overview.md` -- two-scenario (App-Only /
  Interactive) pre-request verification test plan for a trial or sandbox
  tenant, to empirically validate a configuration before requesting it
  for real.
- `references/resource-specific-consent-summary.md` -- summary of
  Microsoft's own Resource Specific Consent (RSC) documentation:
  confirms `Sites.Selected` as the modern, official replacement for the
  deprecated ACS site-scoped permission model, the two-step grant
  process, the four permission tiers and their actual documented
  definitions (the source that disproved this skill's earlier
  Write-excludes-structure assumption), and the companion cmdlets
  (`Get-`/`Set-`/`Revoke-PnPAzureADAppSitePermission`).
- `references/graph-selected-permissions-overview-summary.md` -- summary
  of Microsoft Graph's own Selected-permissions reference: the four
  `.Selected` scopes (not just `Sites.Selected`), the official `write`
  role definition, a **role-name vocabulary mismatch worth knowing
  about** (Graph API roles are `read`/`write`/`owner`/`fullcontrol` --
  PnP's `-Permissions` parameter uses `Read`/`Write`/`Manage`/
  `FullControl`; `Manage` and `owner` are presumed but not confirmed
  equivalent), and Microsoft's own explicit statement of the delegated
  intersection model (`min(app role, user permission)`) that
  `capability_testing_status` weighs against the "user permission alone
  explains the observed capabilities" explanation.
- `scripts/test-pnp-effective-capability-probe.ps1` -- tests effective
  SharePoint capabilities for a given app registration and auth mode
  (Interactive or Certificate). Reports the stored Sites.Selected grant
  role (best-effort, via `Get-PnPAzureADAppSitePermission`) and observed
  capabilities as two separate results, never inferring one from the
  other. Real tenant I/O, run by you -- not invoked automatically.
  Renamed from `test-grant-tier-probe.ps1` when its tier-inference logic
  was removed as disproven.
- `assets/service-request-interactive-registration-template.md`,
  `assets/service-request-application-registration-template.md` --
  the fill-in-the-blanks templates `render_service_request` fills.

## Provenance

Generalized from a real project's app-registration JIRA requests,
`CLAUDE.md` architecture notes describing both registration types, live
Entra portal screenshots and a live tenant-administrator-run
`Get-PnPAzureADAppSitePermission` query against the real **production**
tenant, and Microsoft's own current Sites.Selected/RSC documentation --
see `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`
for the sibling `validate-app-registration` extraction this skill's
reference/asset files were originally onboarded alongside.

**Correction history (2026-08-09) -- three real corrections, in order,
worth knowing about if this drifts again:**

1. An early draft incorrectly generalized a single "empirical finding"
   (`Write` alone sufficient for list creation) from a misremembered
   summary -- corrected against trial-tenant test-suite result tables,
   which showed the opposite: `Write` blocks list creation, `Manage`
   allows it.
2. A second draft then assumed the interactive registration uses
   `AllSites.Manage` (Delegated) at the Entra level, based on that same
   trial-tenant documentation -- corrected against live production-tenant
   Entra screenshots, which show `Sites.Selected` (Application) on
   **both** registrations.
3. A third draft still asserted the trial-tenant's Write-vs-Manage
   capability-tier boundary (list creation blocked under Write) as a
   confirmed fact for production. **A tenant administrator's live
   `Get-PnPAzureADAppSitePermission` query disproved this**: the
   interactive registration's production grant is `write`, yet list/
   library creation succeeded. This is the correction reflected
   throughout this document now -- `REGISTRATION_TYPES` no longer
   asserts fixed capability booleans, only `capability_testing_status`
   prose describing what's actually known, unresolved, or unverified.

