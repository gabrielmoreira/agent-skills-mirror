---
name: sharepoint-deploy-spfx-solution
plugin: sharepoint-spfx-development
description: Provides PnP PowerShell runbooks and scripts to upload, deploy and verify .sppkg packages in Site Collection or Tenant App Catalogs. Use after packaging an SPFx solution, to get it into an App Catalog and confirm it is valid and enabled.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/deploy-spfx-package.ps1 -PackagePath \"path/to/solution.sppkg\" -Scope Site -Install"
  - "pwsh -File scripts/verify-app-catalog.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/site\" -AdminUrl \"https://tenant-admin.sharepoint.com\""
---

# Deploy SPFx Solution

Upload, deploy and verify a compiled `.sppkg` in a SharePoint Online App Catalog (site collection or tenant).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- `scripts/deploy-spfx-package.ps1` has no dry-run or confirmation gate: it uploads and publishes (`Add-PnPApp`), and with `-Install` installs the app, as soon as it runs. Confirm the target site and package with the user first;
  the user runs it. `scripts/verify-app-catalog.ps1` is read-only.
- A Site Collection App Catalog must exist on the target site before a site-scope deploy; add it with `-EnsureSiteAppCatalog` or follow `sharepoint-request-site-collection-app-catalog`.
- Requires PowerShell 7 (`pwsh`) and `PnP.PowerShell`. When running an installed copy, pass `-ConfigPath` or explicit `-SiteUrl`, `-ClientId`, `-TenantId`.

## Quick start

```powershell
pwsh -File scripts/deploy-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -Install
```

## Workflow

1. Verify the site's App Catalog exists (`scripts/verify-app-catalog.ps1`).
2. Deploy with the script above, or upload through the browser or `Add-PnPApp` (see the runbook).
3. Check the App Catalog entry, then refresh the target modern page.

## Verification

The App Catalog list shows Enabled = Yes, Valid App Package = Yes and App Package Error Message = No errors, and the SPFx component renders updated data on the page without being re-added.

## References

- [Deploy runbook](references/spfx-deploy-runbook.md): read for the browser and PnP flows and the verification checklist.
- [Live-write scripts](references/spfx-live-write-scripts.md): read for which SPFx scripts have gates and their parameters.
