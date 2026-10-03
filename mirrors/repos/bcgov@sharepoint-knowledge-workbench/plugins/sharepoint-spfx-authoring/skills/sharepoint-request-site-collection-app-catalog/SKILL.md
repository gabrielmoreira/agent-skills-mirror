---
name: sharepoint-request-site-collection-app-catalog
plugin: sharepoint-spfx-authoring
description: Guides the setup of Site Collection App Catalogs through ServiceNow ticket requests in a BC Gov enterprise tenancy, or through direct Admin Center and PnP PowerShell execution in trial and sandbox environments. Use before deploying custom SPFx web parts to a site that has no App Catalog.
allowed-tools: Bash, Read, Write
---

# Request Site Collection App Catalog

A Site Collection App Catalog is required on the target site before custom SPFx web parts can be deployed. Choose the path by tenancy.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Path A (enterprise tenancy): developers lack Tenant Admin rights (`-admin.sharepoint.com`), so submit a ServiceNow request to MySc / CSBC; do not attempt direct provisioning.
- Path B (trial or sandbox tenancy): the developer holds Global or Tenant Admin. Connect to the tenant admin site URL (`-admin.sharepoint.com`), not the target site collection, before `Add-PnPSiteCollectionAppCatalog -Site`.
- Provisioning is a tenant write the user (or administrator) performs. Do not run it unprompted.

## Quick start

Path B, with admin rights:

```powershell
Connect-PnPOnline -Url "https://<tenant>-admin.sharepoint.com" -ClientId "<clientId>" -Interactive
Add-PnPSiteCollectionAppCatalog -Site "https://<tenant>.sharepoint.com/sites/<TargetSite>"
```

## Workflow

1. Determine the tenancy (enterprise or trial) and list the target site URLs (for example test and production).
2. Enterprise: fill in and submit the ServiceNow template (it cites prior approved tickets). Trial: use PnP PowerShell or the Admin Center walkthrough.
3. After provisioning (within about 10 to 30 seconds for direct execution), verify the catalog and hand off to deployment.

## Verification

`https://<tenant>.sharepoint.com/sites/<SiteName>/AppCatalog/AppCatalog` opens and the Apps for SharePoint document library exists. Then deploy packages with `sharepoint-deploy-spfx-solution`.

## References

- [Request runbook](references/app-catalog-request-runbook.md): read for the ServiceNow template, both Path B options and the verification steps.
