---
name: sharepoint-request-site-collection-app-catalog
plugin: sharepoint-spfx-authoring
description: Guides the setup and provisioning of Site Collection App Catalogs via ServiceNow ticket requests in BC Gov enterprise tenancy or direct Admin GUI / PnP PowerShell execution in trial and sandbox environments.
allowed-tools: Bash, Read, Write
---

# request-site-collection-app-catalog

## Overview

Deploying custom SPFx web parts (like the Master-Detail briefing dashboard) requires a **Site Collection App Catalog** on the target SharePoint site.

Because admin permission models differ between enterprise production environments and isolated trial environments, this skill details two distinct provisioning paths:
- **Path A: Enterprise Tenancy (`contoso.sharepoint.com`)**: Developers do not have SharePoint Tenant Admin rights (`-admin.sharepoint.com`). Requires submitting a ServiceNow ticket to MySc / CSBC referencing approved ticket templates.
- **Path B: Isolated Trial / Sandbox Tenancy**: Developers possess Global/Tenant Admin rights and can provision the app catalog directly via PnP PowerShell or the SharePoint Admin Center GUI.

---

## Path A: Enterprise BC Government Tenancy (ServiceNow Request)

Submit a ServiceNow request to MySc / CSBC using the pre-filled template below.

### ServiceNow Ticket Template

```text
Title: Request for Site Collection App Catalog Provisioning for Target SPO Sites

ServiceNow Category: MySc / CSBC / SharePoint Online Administration

Description:
For the following SharePoint Online sites, we require the setup of a Site Collection App Catalog to enable deployment of custom SPFx web parts for the application modernization initiative:

Target SharePoint Online Sites:
1. https://contoso.sharepoint.com/sites/TargetSite-Test (Test Environment)
2. https://contoso.sharepoint.com/sites/TargetSite-Prod (Production Environment)

Business Justification:
To enable a like-for-like migration of the legacy SharePoint application, custom SPFx web parts are required to replicate the legacy multi-list URL-filtered briefing pages (Dossier_Briefing.aspx). Out-of-the-box SPO List Web Parts do not support query string filtering (?SelectedID=...).

Prior Approved Reference Tickets:
We understand similar requests were previously approved and submitted to MySc for BCPS with the following references:
- REQ0841030 (Request Item Number: RITM1239070)
- REQ0855248 (Request Item Number: RITM1259346)

Required Action by Tenant Administrator:
Execute `Add-PnPSiteCollectionAppCatalog` on the admin site endpoint or provision via SharePoint Admin Center -> More Features -> Apps -> Site Collection App Catalogs for both site URLs listed above.
```

---

## Path B: Trial / Dev Sandbox Tenancy (Direct Admin Provisioning)

If working in an isolated trial tenancy or dev sandbox where you possess SharePoint Tenant Admin credentials:

### Option 1: PnP PowerShell (Recommended)

> **Important**: You MUST connect to the tenant admin site URL (`-admin.sharepoint.com`), NOT the target site collection URL.

```powershell
# 1. Connect to Tenant Admin Endpoint using PowerShell 7 (pwsh)
Connect-PnPOnline -Url "https://<tenant>-admin.sharepoint.com" -ClientId "<clientId>" -Interactive

# 2. Enable Site Collection App Catalog on specific target sites
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Test"
Add-PnPSiteCollectionAppCatalog -Site "https://contoso.sharepoint.com/sites/TargetSite-Prod"
```

### Option 2: SharePoint Admin Center GUI Walkthrough

1. Open the SharePoint Admin Center:
   `https://<tenant>-admin.sharepoint.com`
2. In the left navigation bar, select **More features**.
3. Under the **Apps** section, click **Open** (opens classic Apps management page).
4. Select **Site Collection App Catalogs**.
5. Click **Add a site collection**.
6. Enter the target site URL (e.g. `https://contoso.sharepoint.com/sites/TargetSite-Test`).
7. Click **Confirm and create**.

*SharePoint automatically enables the feature and provisions the app catalog site at `https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog` within 10–30 seconds.*

---

## Verification & Handoff

After provisioning (either via ServiceNow fulfillment or direct admin execution):

1. Navigate to the App Catalog direct library URL:
   `https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog/AppCatalog`
   *(or `https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog/Forms/AllItems.aspx`)*
2. Confirm the **Apps for SharePoint** document library exists.
3. Proceed to deploy `.sppkg` packages using the `deploy-spfx-solution` skill.

