---
name: sharepoint-setup-spfx-workbench
plugin: sharepoint-spfx-authoring
description: Sets up and validates a local SPFx web part development workflow that can be tested in SharePoint Online hosted workbench.aspx.
allowed-tools: Bash, Read, Write
---

# setup-spfx-workbench

## Identity

Use this skill when a user wants to prepare an SPFx project for local development and test it in the hosted SharePoint Online workbench (`/_layouts/15/workbench.aspx`) with debug manifests served from localhost.

## Steps

### Step 1: Confirm tenant profile and connectivity

From repository root, confirm `config.psd1` points at the intended tenant profile, then run:

```powershell
pwsh -File plugins/workbench-setup/skills/workbench-validate-workbench-environment/scripts/test-spo-connection.ps1
```

### Step 2: Validate SPFx toolchain

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/check-spfx-toolchain.ps1
```

### Step 3: Prepare hosted workbench URLs and dev cert

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/setup-spfx-workbench.ps1 `
  -ProjectPath "path/to/spfx-solution-root" `
  -SiteUrl "https://contoso.sharepoint.com/sites/test-site"
```

The script verifies project prerequisites, ensures the dev certificate is trusted, and prints:
- local workbench URL
- hosted workbench URL
- hosted debug URL (`loadSPFX=true` + `debugManifestsFile`)

### Step 4: Start local serve and open hosted workbench debug URL

```powershell
cd path/to/spfx-solution-root
npx gulp serve --nobrowser
```

In browser, use the hosted debug URL printed in Step 3.

## Common Failures

- `ERR_CERT_AUTHORITY_INVALID` on localhost: rerun `setup-spfx-workbench.ps1` without `-SkipCertInstall`.
- Web part not appearing in hosted workbench: ensure `gulp serve` is still running and URL includes `debugManifestsFile=https://localhost:4321/temp/manifests.js`.
- 401/403 on hosted workbench: verify tenant/site URL and rerun SharePoint connection validation from Step 1.
