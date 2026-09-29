---
name: sharepoint-deploy-spfx-solution
plugin: sharepoint-spfx-authoring
description: Provides PnP PowerShell runbooks and scripts to upload, deploy, and verify .sppkg packages in Site Collection or Tenant App Catalogs.
allowed-tools: Bash, Read, Write
---

# deploy-spfx-solution

## Overview

This skill guides the deployment and verification of compiled SPFx solution packages (`.sppkg`) into a SharePoint Online App Catalog (Site Collection App Catalog or Tenant App Catalog).

## Toolchain Requirements

- **PowerShell**: PowerShell 7 (`pwsh`)
- **Module**: `PnP.PowerShell`

## Core Workflow

### Step 1: Verify Site Collection App Catalog

Ensure the App Catalog exists on the target site collection:

```powershell
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<site>" -Interactive
Add-PnPSiteCollectionAppCatalog
```

### Step 2: Upload and Deploy Package via Browser

1. Navigate to the App Catalog direct library view:
   `https://<tenant>.sharepoint.com/sites/<site>/AppCatalog/AppCatalog`
2. Drag and drop the `.sppkg` file.
3. Confirm **Replace / Overwrite**.
4. In the trust panel, select **Enable app** / **Deploy**.

### Step 3: Automated Upload via PnP PowerShell

Alternatively, deploy directly via PowerShell script:

```powershell
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<site>" -Interactive
Add-PnPApp -Path "path/to/solution.sppkg" -Publish -Overwrite
```

### Step 4: Verification

1. Confirm the App Catalog list displays:
   - **Enabled = Yes**
   - **Valid App Package = Yes**
   - **App Package Error Message = No errors**
2. Refresh the target modern page (`.../SitePages/<page>.aspx?SelectedID=1`).
3. Verify that the SPFx Master-Detail component renders updated data without requiring page re-addition.

