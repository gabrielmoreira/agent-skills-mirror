---
name: workbench-request-app-registration
plugin: workbench-setup
description: Guides the pre-work before any SharePoint use case that connects to a live tenant. Documents the two app-registration types (unattended App-Only/certificate for scheduled jobs, interactive/delegated for human-operator provisioning), generates a filled service-request document for your tenant or cloud administrator, and gives the setup sequence once granted (Entra API permissions, admin consent, Enterprise Application user assignment, and the separate PnP PowerShell site-level grant). Use before initializing config or running live checks. No network I/O; templating and reference data only.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from app_registration_request import REGISTRATION_TYPES; print(REGISTRATION_TYPES[0]['key'])\""
---

# Request App Registration

Answer "what do I ask my tenant administrator for, and what must they do once they grant it".
Do this before `workbench-initialize-workbench-config` or any live check.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Do not treat a PnP site-grant tier (`Write`/`Manage`) as a predictor of capability.**
  Production testing disproved the claim that `Write` blocks list/library creation. A
  successful `CreateList` does not prove a `Manage` grant.
- Report the stored grant role and the observed capabilities as two separate results, never
  conflated. Neither unresolved explanation (Microsoft's `write` definition vs. the
  user-permission intersection) is settled.
- Observe behavior with `scripts/test-pnp-effective-capability-probe.ps1`. It does real tenant
  I/O and the user runs it; never invoke it automatically.
- Pick the registration type deliberately. The wrong one causes confusing Access Denied errors.
- No network I/O here. Run from this skill's root with `scripts/` on `sys.path`; standard
  library only. The probe needs `pwsh` and `PnP.PowerShell`.

## Quick start

List the two registration types and their status:

```python
import sys; sys.path.insert(0, "scripts")
from app_registration_request import REGISTRATION_TYPES
for t in REGISTRATION_TYPES:
    print(t["key"], "-", t["purpose"], "-", t["capability_testing_status"])
```

## Workflow

1. Choose the type: `etl` (unattended App-Only/certificate) or `interactive` (delegated).
2. Fill the matching `assets/` template with `render_service_request`; it raises
   `AppRegistrationRequestError` naming every unfilled placeholder. See
   [request and setup](references/app-registration-request-and-setup.md).
3. Once granted, follow `SETUP_STEPS` in that file: Entra permissions, user assignment
   (interactive only), admin consent, then the per-site `Grant-PnPAzureADAppSitePermission`.
4. Populate `config.psd1` via `workbench-initialize-workbench-config`; don't hand-edit.
5. Validate with the probe (`-AuthMode Certificate` for App-Only).

## Verification

Confirm no `<PLACEHOLDER>` is left, `ClientId` and `TenantId` are in `config.psd1`, and the
probe lists the stored grant role and observed capabilities separately.

## References

- [Capability caution](references/app-registration-capability-caution.md): read before claiming
  what a grant tier or registration can do.
- [Registration types](references/app-registration-types.md): read when choosing a type.
- [Request and setup](references/app-registration-request-and-setup.md): read when generating
  a request or walking the setup sequence.
- [Effective permissions matrix](references/effective-permissions-matrix.md): start here for any
  "why did or didn't this operation work" question.
- [App registration overview](references/app-registration-overview.md): pre-request test plan
  for a trial or sandbox tenant.
- [Resource-specific consent](references/resource-specific-consent-summary.md) and
  [Graph selected permissions](references/graph-selected-permissions-overview-summary.md):
  Microsoft's `Sites.Selected` model, tier definitions, and Graph vs. PnP role names.
- [Provenance and corrections](references/app-registration-provenance.md): read if claims drift.
- Templates in `assets/`: `service-request-interactive-registration-template.md` and
  `service-request-application-registration-template.md`.
