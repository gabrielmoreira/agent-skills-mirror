---
name: sharepoint-publish-spfx-package
plugin: sharepoint-spfx-development
description: Publishes an SPFx .sppkg package to a Site Collection App Catalog or Tenant App Catalog using config.psd1-driven connection settings, then performs basic catalog verification. Use to publish (and optionally install) a built package without manual browser upload.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/publish-spfx-package.ps1 -PackagePath \"path/to/solution.sppkg\" -Scope Site -Install"
---

# Publish SPFx Package

Publish an already-built `.sppkg` to the Site or Tenant App Catalog without manual browser upload.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- `scripts/publish-spfx-package.ps1` has no dry-run or confirmation gate: it publishes (and with `-Install` installs) as soon as it runs. Confirm the package, scope and target with the user first; the user runs it.
- Requires PowerShell 7, `PnP.PowerShell` and a built `.sppkg`. Connection comes from `config.psd1` (`Connection.SiteUrl`, `ClientId`, `TenantId`; `Authentication.TenantAdminUrl` for tenant scope) or explicit `-SiteUrl`, `-ClientId`, `-TenantId`.
  When running an installed copy, pass `-ConfigPath` or the explicit parameters.
- A Site Catalog app with "Added to all sites" = No must also be installed into the site (`-Install`) before its web parts appear in the toolbox.

## Quick start

```powershell
pwsh -File scripts/publish-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -Install
```

## Workflow

1. Confirm the `.sppkg` path and the scope (`Site` or `Tenant`). Use `-EnsureSiteAppCatalog` on first-time site setup.
2. Run the script. For tenant scope add `-SkipFeatureDeployment` unless tenant-wide deployment is intended.
3. Read the output: publish status, app metadata (`Title`, `Id`, `Deployed`), catalog readback via `Get-PnPApp`, and install verification when `-Install` was used.

## Verification

The script exits non-zero with explicit errors on failure. On success, confirm `Deployed` and that the app appears in the page `+` toolbox. To change the toolbox name, edit `preconfiguredEntries[0].title.default` and repackage.

## References

- [Publish details](references/spfx-publish-details.md): read for all five example invocations and the toolbox/activation requirement.
- [Naming and versioning](references/spfx-naming-and-versioning.md): read for package, solution and toolbox names.
- [Live-write scripts](references/spfx-live-write-scripts.md): read for which SPFx scripts have gates.
