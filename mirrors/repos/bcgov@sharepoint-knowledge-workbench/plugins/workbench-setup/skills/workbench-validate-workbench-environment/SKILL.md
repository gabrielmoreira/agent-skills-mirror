---
name: workbench-validate-workbench-environment
plugin: workbench-setup
description: Confirms the app registration/connection actually works against a live tenant -- provides real, runnable network-reachability + interactive-authentication scripts, and validates the Entra ID app registration itself (OAuth2 device-code + _api/contextinfo REST smoke test, plus a permission-boundary proof). Also validates connection/profile configuration correctness before any of that (always PASS or FAIL, never WARN).
allowed-tools: Bash, Read
examples:
  - "python -c \"import workflow_validation as wv; print(wv.validate_document_workflow_profile(profile).status)\""
  - "python -c \"from app_registration_validation import validate_app_registration; print(validate_app_registration(connection, http_client).to_dict())\""
  - "pwsh -File test-network-connectivity.ps1 -ConfigPath ../../../../config.psd1"
---

# Validate Workbench Environment

## Trigger and Purpose

Use this skill to confirm the workbench environment is actually ready
before another plugin (or a live tenant operation) relies on it. It
covers three layers, from cheapest/pure to real live tenant I/O:

1. **Config/profile correctness** (pure, no I/O) — the Layer 1
   connection config (`config.psd1`), a document-workflow profile
   (`document-workflows/<DocumentId>.workflow.psd1`), or a publication
   profile (`publication-profiles/<DocumentId>.publication.psd1`).
2. **App-registration validity** (pure logic, opt-in injected transport)
   — does the Entra ID app registration actually authenticate and
   obtain usable SharePoint REST access, and is its effective access
   correctly bounded to the signed-in user's own permissions.
3. **Live network + interactive auth** (real tenant I/O, run by you) —
   can this host reach the required Microsoft endpoints, and does a
   real interactive sign-in against the live tenant succeed.

## 1. Config/profile correctness (pure dict validation)

**Scope boundary (deliberate, this version):** validates already-
PARSED Python dicts, not raw `.psd1` file text — see
`workflow_validation.py`'s module docstring for why raw `.psd1` parsing
is out of scope for this first version rather than attempted with a
fragile custom parser.

```python
from workflow_validation import (
    validate_connection_config, validate_document_workflow_profile,
    validate_publication_profile,
)

report = validate_document_workflow_profile(workflow_profile_dict)
# ValidationReport(status="PASS"|"FAIL", issues=[...])
```

Detections: missing required top-level keys; empty `Document.
DocumentId`; a renderer profile placed in `RequestedRendererProfiles`
(document-workflow) or `HumanPublication.PublicationProfile`
(publication profile) that is not one of this repo's implemented
renderer profiles. Every issue is `severity="error"` — status is
always `PASS` or `FAIL`, never `WARN`.

## 2. App-registration validity (pure logic, opt-in injected transport)

Confirms an Entra ID app registration (delegated, device-code auth) is
correctly configured for a target SharePoint site: acquires a bearer
token via the device-code flow, decodes the token's claims to report
who/what actually authenticated, then calls `_api/contextinfo` against
the site to confirm the token grants usable SharePoint REST access.
Failures (device-code request failure, token acquisition failure,
permission denial on `_api/contextinfo`, missing digest) are reported
as an honest partial result (`success=False` with a `detail` message),
never a false success.

**Zero tenant I/O by default.** This module ships no live HTTP
transport -- `validate_app_registration(connection, http_client)`
requires an injected `http_client` exposing `request_device_code`,
`poll_for_token`, and `get_context_info`. `make_device_code_connector
(http_client)` builds a `connector(connection) -> bool` callable
compatible with `config_setup.test_connection(connection,
connector=...)`'s existing opt-in-only contract (see
`initialize-workbench-config`'s SKILL.md) -- wiring this connector in
never becomes a default; `test_connection()` still raises
`NotImplementedError` when called without one.

```python
from app_registration_validation import (
    validate_app_registration,
    make_device_code_connector,
    validate_permission_boundary,
)

result = validate_app_registration(connection, http_client)
# AppRegistrationValidationResult(success, signed_in_as, app_id, detail)

# Wiring into initialize-workbench-config's opt-in -TestConnection path:
from config_setup import test_connection
connector = make_device_code_connector(http_client)
test_connection(connection, connector=connector)

# Prove Effective permissions = App ∩ User for a delegated registration --
# see references/delegated-permission-boundary-test.md for the full method.
boundary = validate_permission_boundary(authorized_connection, unauthorized_connection, http_client)
# PermissionBoundaryResult(boundary_proven, authorized_result, unauthorized_result, detail)
```

`validate_permission_boundary` runs `validate_app_registration` against two
connections sharing the same `ClientId`/`TenantId` but different
`SiteUrl`s — one the signed-in user can reach, one they cannot.
`boundary_proven` is only `True` when the authorized site succeeds AND the
unauthorized site is denied; an unauthorized site unexpectedly succeeding
is reported as a security finding in `detail`, not a passing result. This
is the one capability here with no equivalent in the live PowerShell tools
below -- neither proves the permission *boundary*, only that a given site
connects.

## 3. Live network + interactive authentication (real tenant I/O, run by you)

Three pieces, in increasing order of directness:

1. **`network_connectivity.py`** — pure, TDD-tested TCP-reachability
   checklist logic (Entra ID, SharePoint Online, Microsoft Graph,
   CRL/OCSP endpoints; no project-specific endpoint is included). Ships
   no transport itself -- requires an injected `connector(host, port) ->
   bool` callable, same "zero tenant I/O unless the caller explicitly
   supplies one" contract as `app_registration_validation.py`.

   ```python
   from network_connectivity import check_network_connectivity
   result = check_network_connectivity(connection, my_connector)
   # NetworkConnectivityResult(success, required_failures, optional_failures, checked)
   ```

2. **`test-network-connectivity.ps1`** — the full live tool: Phase 1
   runs the network-reachability checklist via a cross-platform TCP
   connect (works under macOS/Linux `pwsh`, not just Windows'
   `Test-NetConnection`); Phase 2 runs a real `Connect-PnPOnline`
   interactive/device-code sign-in against the site in this repository's
   root `config.psd1` and confirms `Get-PnPWeb`/`CurrentUser` resolve.

   ```bash
   pwsh -File test-network-connectivity.ps1                    # network + browser sign-in
   pwsh -File test-network-connectivity.ps1 -SkipAuthTest       # network reachability only
   pwsh -File test-network-connectivity.ps1 -DeviceLogin        # device-code sign-in instead of browser
   ```

3. **`test-spo-connection.ps1`** — a minimal connection-only test (no
   network pre-flight): `Connect-PnPOnline -Interactive` + `Get-PnPWeb`.
   Subsumed by `test-network-connectivity.ps1`'s Phase 2, kept as a
   quicker standalone check when you only want the connection result.

   ```bash
   pwsh -File test-spo-connection.ps1
   ```

4. **`test-grant-tier-probe.ps1`** — empirically determine the actual
   granted PnP site permission tier (`Write` vs `Manage`) on one or more
   sites, using list creation as the confirmed differentiator (`Write`
   blocks it, `Manage` allows it -- page create/delete passes under
   either, so it's a baseline sanity check, not a signal). Creates and
   immediately removes a temporary probe list/page per site -- no
   residue left behind. `-Sites` is required, no default.

   ```bash
   pwsh -File test-grant-tier-probe.ps1 -Sites "https://<tenant>.sharepoint.com/sites/<site-a>", "https://<tenant>.sharepoint.com/sites/<site-b>"
   ```

All PowerShell scripts read `SiteUrl`/`ClientId`/`TenantId` from
`-ConfigPath` (defaults to this repository's root `config.psd1`) --
supporting both `initialize-workbench-config`'s nested `Connection =
@{...}` schema and a flat top-level `ClientId`/`TenantId`/`SiteUrl`
schema.

**These are the only places in `workbench-setup` that perform live
tenant I/O and prompt for interactive sign-in by default when run — run
them yourself; none are invoked automatically by any skill.**

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

Python: none beyond the standard library -- `http_client`/`connector`
callables are supplied by the caller, not shipped here. The live
PowerShell tools additionally require `pwsh` and the `PnP.PowerShell`
module on PATH — see `DEPENDENCIES.md`.

## References and assets

- `references/effective-permissions-matrix.md` -- **start here for any
  "why did/didn't this operation work" question.** Synthesizes all
  three independent axes that determine effective access (SharePoint
  site-level user permissions, Entra/Graph app API permissions, PnP
  site-grant tiers), the role-vocabulary mismatch between them, the
  documented delegated-access intersection model, and a checklist for
  reasoning through an unexpected pass/fail result.
- `references/app-registration-overview.md` -- two-scenario (App-Only /
  Interactive) pre-request verification test plan for a trial or
  sandbox tenant.
- `references/delegated-permission-boundary-test.md` -- the empirical
  boundary-proof method behind `validate_permission_boundary`.
- `assets/service-request-application-registration-template.md`,
  `assets/service-request-interactive-registration-template.md` --
  fill-in-the-blanks templates for requesting the two registration types
  from a cloud/IT team, once the corresponding scenario above has passed.

## Provenance

`app_registration_validation.py` provides tenant validation (device-code REST
auth smoke test, `scripts/diagnostics/test-spo-auth.ps1`). `validate_permission_boundary`
and the reference/asset files above were added to provide comprehensive validation.
`network_connectivity.py`/`test-network-connectivity.ps1` were adapted
the same day from a real project's network-connectivity script, with
its project-specific gateway endpoint and all other project-specific
references removed.

