---
name: sharepoint-publish-spfx-package
plugin: sharepoint-spfx-authoring
description: Publishes an SPFx .sppkg package to a Site Collection App Catalog or Tenant App Catalog using config.psd1-driven connection settings, then performs basic catalog verification.
allowed-tools: Bash, Read, Write
---

# publish-spfx-package

## Overview

Use this skill to publish an already-built SPFx package (`.sppkg`) to
SharePoint App Catalog without manual browser upload.

This skill uses `scripts/publish-spfx-package.ps1`, supports:
- **Site scope** publication (site collection app catalog)
- **Tenant scope** publication (tenant app catalog)
- Nested or flat `config.psd1` schema resolution

## Prerequisites

- PowerShell 7 (`pwsh`)
- `PnP.PowerShell` module
- Existing `.sppkg` package
- Valid `config.psd1` containing:
  - `Connection.SiteUrl`
  - `Connection.ClientId`
  - `Connection.TenantId`
  - `Authentication.TenantAdminUrl` (required for tenant scope)

## Core Workflow

### Step 1: Confirm the package path

Example package path:

```text
temp\bcps-webparts\Technical Documentation\crownnet-my-fav-apps\crownnet-my-fav-apps\sharepoint\solution\my-fav-apps-dev.sppkg
```

### Step 2: Publish to Site Collection App Catalog & Auto-Install (Recommended)

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/publish-spfx-package.ps1 `
  -PackagePath "temp\bcps-webparts\Technical Documentation\crownnet-my-fav-apps\crownnet-my-fav-apps\sharepoint\solution\my-fav-apps-dev.sppkg" `
  -Scope Site `
  -Install
```

> [!TIP]
> The `-Install` switch automatically runs `Install-PnPApp` after publication so the app becomes immediately available in the SharePoint modern page `+` toolbox without requiring manual Site Contents steps.

### Step 3: Ensure App Catalog, Publish, and Install (First-Time Site Setup)

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/publish-spfx-package.ps1 `
  -PackagePath "temp\bcps-webparts\Technical Documentation\crownnet-my-fav-apps\crownnet-my-fav-apps\sharepoint\solution\my-fav-apps-dev.sppkg" `
  -Scope Site `
  -EnsureSiteAppCatalog `
  -Install
```

### Step 4: Publish to Tenant App Catalog with Tenant-Wide Deployment

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/publish-spfx-package.ps1 `
  -PackagePath "temp\bcps-webparts\Technical Documentation\crownnet-my-fav-apps\crownnet-my-fav-apps\sharepoint\solution\my-fav-apps-dev.sppkg" `
  -Scope Tenant `
  -SkipFeatureDeployment
```

### Step 5: Publish with Explicit Connection Overrides (No config.psd1 dependency)

```powershell
pwsh -File plugins/sharepoint-spfx-authoring/scripts/publish-spfx-package.ps1 `
  -PackagePath "path/to/solution.sppkg" `
  -Scope Site `
  -SiteUrl "https://contoso.sharepoint.com/sites/my-site" `
  -ClientId "d7231fef-4a83-4b4f-85ba-b210d1d36018" `
  -TenantId "2321de1b-bcfa-4353-a8a3-63718910e698" `
  -Install
```

### Step 6: Validate Result

The script prints:
- upload/publish status
- app metadata (`Title`, `Id`, `Deployed`)
- catalog readback verification via `Get-PnPApp`
- site installation verification (when `-Install` is specified)

If publish fails, the script exits non-zero with explicit error output.

## SPFx Naming Architecture: Package vs. Web Part Selector

When authoring and deploying SPFx solutions, three distinct naming levels exist:

| Layer | Defined In | Purpose & Where Displayed | Example |
| :--- | :--- | :--- | :--- |
| **Package File** | `package-solution.json` (`paths.zippedPackage`) | Physical `.sppkg` archive on disk | `my-fav-apps-dev.sppkg` |
| **Solution / App Name** | `package-solution.json` (`solution.name`) | Displayed in **App Catalog** and **Site Contents > Add an App** | `crownnet-my-fav-apps-dev` |
| **Web Part Title** | `*WebPart.manifest.json` (`preconfiguredEntries[0].title.default`) | 🌟 Displayed in modern page editor **`+` Web Part Selector / Toolbox** | `MyFavApps` |
| **Web Part Category** | `*WebPart.manifest.json` (`preconfiguredEntries[0].group.default`) | Category heading in the toolbox | `Advanced` or `Under Development` |

> [!NOTE]
> To change the name that end-users/authors see in the SharePoint page toolbox, modify `preconfiguredEntries[0].title.default` in `<WebPart>.manifest.json` and rebuild the package using the `sharepoint-package-spfx-solution` skill.

## Toolbox Visibility & Site Activation Requirement

Deploying a package to a **Site Collection App Catalog** (`-Scope Site`) makes the app available to that site collection, but if `Added to all sites` is `No` (the default for site catalogs), the app must also be **activated/installed into the site** before SharePoint will expose its web parts in the page editor toolbox:

- **Via PowerShell**:
  ```powershell
  Install-PnPApp -Identity <AppId> -Scope Site
  ```
- **Via SharePoint UI**: Go to **Site Contents** > **`+ New`** > **`App`** > Select the app.

