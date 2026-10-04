---
name: sharepoint-setup-spfx-hosted-workbench
plugin: sharepoint-spfx-development
description: Sets up and validates a local SPFx web part development workflow that can be tested in the SharePoint Online hosted workbench (workbench.aspx). Use when preparing an SPFx project to debug against localhost manifests in a real tenant.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/setup-spfx-workbench.ps1 -ProjectPath path/to/spfx-solution-root -SiteUrl https://contoso.sharepoint.com/sites/test-site"
---

# Setup SPFx Workbench

Prepare an SPFx project for local development and test it in the hosted workbench (`/_layouts/15/workbench.aspx`) with debug manifests served from localhost.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Local only: `setup-spfx-workbench.ps1` validates the project, trusts the local dev certificate and prints URLs; it writes nothing to the tenant. `gulp serve` must stay running while you debug.
- Confirm `config.psd1` points at the intended tenant profile and the connection works before debugging against the hosted workbench (use `workbench-validate-sharepoint-connection`).
- Run `scripts/check-spfx-toolchain.ps1` first, or let the setup script call it.

## Quick start

```powershell
pwsh -File scripts/setup-spfx-workbench.ps1 -ProjectPath "path/to/spfx-solution-root" -SiteUrl "https://contoso.sharepoint.com/sites/test-site"
```

## Workflow

1. Confirm the tenant profile and connectivity, then validate the toolchain.
2. Run the setup script; it prints the local workbench URL, the hosted workbench URL and the hosted debug URL (`loadSPFX=true` plus `debugManifestsFile`).
3. In the project folder run `npx gulp serve --nobrowser`, then open the hosted debug URL in the browser.

## Verification

The web part appears in the hosted workbench with the debug manifest served from `https://localhost:4321/temp/manifests.js`.

## References

- [Workbench setup details](references/spfx-workbench-setup-details.md): read for the full steps and the common failures (certificate, missing web part, 401/403).
- [Acceptance criteria](references/acceptance-criteria.md): read when checking expected behavior.
