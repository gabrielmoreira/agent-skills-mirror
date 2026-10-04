---
name: workbench-validate-sharepoint-connection
plugin: sharepoint-workbench-setup
description: Confirms the app registration and connection work against a live tenant. Validates config and profile correctness (always PASS or FAIL), validates the Entra ID app registration (device-code auth plus an _api/contextinfo REST smoke test and a permission-boundary proof), and provides network-reachability and interactive sign-in scripts. Use before another plugin or a live tenant operation relies on the workbench environment.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import workflow_validation as wv; print(wv.validate_document_workflow_profile(profile).status)\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from app_registration_validation import validate_app_registration; print(validate_app_registration(connection, http_client).to_dict())\""
  - "pwsh -File scripts/test-network-connectivity.ps1 -SkipAuthTest"
---

# Validate Workbench Environment

Confirm the workbench environment is ready, from cheapest to most real: config correctness,
app-registration validity, then live network and sign-in.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O by default. `validate_app_registration`, `check_network_connectivity` and
  `test_connection` need an injected `http_client` or `connector`; this skill ships none.
- Never report a false success. Failures return `success=False` with a `detail` message.
- Config and profile validation returns only `PASS` or `FAIL`, never `WARN`.
- The PowerShell tools perform live tenant I/O and prompt for sign-in. The user runs them;
  no skill invokes them automatically.
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only;
  the `.ps1` tools need `pwsh` and the `PnP.PowerShell` module.

## Quick start

Validate a parsed profile with no I/O:

```python
import sys; sys.path.insert(0, "scripts")
from workflow_validation import validate_document_workflow_profile
print(validate_document_workflow_profile(profile).status)  # PASS or FAIL
```

## Workflow

1. **Config and profiles** (pure): validate the parsed connection config, document-workflow
   profile or publication profile. See [config and profiles](references/validation-config-and-profiles.md).
2. **App registration** (injected transport): run `validate_app_registration`; for a
   delegated registration, prove the boundary with `validate_permission_boundary`. See
   [app registration](references/validation-app-registration.md).
3. **Live network and sign-in** (real tenant I/O, the user runs it): hand the user the right
   `.ps1` command. See [live tenant tools](references/validation-live-tenant-tools.md).
4. For "why did or didn't this operation work", read the permissions matrix first.

## Verification

Confirm each layer's result: `ValidationReport.status`, `AppRegistrationValidationResult.success`,
`PermissionBoundaryResult.boundary_proven` (true only when the authorized site succeeds and the
unauthorized site is denied), and `NetworkConnectivityResult.success`. An unauthorized site
unexpectedly succeeding is a security finding, not a pass.

## References

- [Config and profiles](references/validation-config-and-profiles.md): read before validating
  a `config.psd1`, workflow profile or publication profile.
- [App registration](references/validation-app-registration.md): read before calling
  `validate_app_registration` or `validate_permission_boundary`.
- [Live tenant tools](references/validation-live-tenant-tools.md): read before running any
  `.ps1` script or `network_connectivity.py`.
- [Effective permissions matrix](references/effective-permissions-matrix.md): start here for
  any "why did or didn't this operation work" question.
- [App registration overview](references/app-registration-overview.md): two-scenario pre-request
  verification test plan for a trial or sandbox tenant.
- [Delegated permission boundary test](references/delegated-permission-boundary-test.md): the
  method behind `validate_permission_boundary`.
- Request templates in `assets/`: `service-request-application-registration-template.md` and
  `service-request-interactive-registration-template.md`, for requesting the two registration
  types once the matching scenario has passed.
