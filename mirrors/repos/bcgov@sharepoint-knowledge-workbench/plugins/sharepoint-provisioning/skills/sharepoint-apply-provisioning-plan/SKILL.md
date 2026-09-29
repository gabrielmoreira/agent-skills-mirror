---
name: sharepoint-apply-provisioning-plan
plugin: sharepoint-provisioning
description: The real PnP.PowerShell executor for sharepoint-provisioning's plan JSON output -- create/update/delete for lists, libraries, site columns, and content types, plus content-type-to-list attach/detach. Dry-run by default; every write gated behind -Execute and an operation-specific -ConfirmToken. This is the "injected executor" sharepoint-provisioning's SKILL.md files reference but do not themselves ship.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -SiteUrl https://contoso.sharepoint.com/sites/pilot -ClientId <id> -TenantId <tenant>"
  - "pwsh -File scripts/spo-update-site-column.ps1 -PlanPath update-plan.json -Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS -ConfigPath config.psd1"
---

# Apply SharePoint Provisioning Plan

## Trigger and Purpose

Use this skill once `sharepoint-provisioning`'s Python planning modules
(`list_provisioning.py`, `field_provisioning.py`, `content_type_provisioning.py`)
have produced an approved plan with a `confirmation_token`. Each script below
is the real tenant-facing counterpart for one plan JSON shape:

| Script | Plan input from | PnP verb |
|---|---|---|
| `spo-provision-list.ps1` | `list_provisioning.plan_provisioning` | `New-PnPList` / `Remove-PnPList` |
| `spo-provision-content-types.ps1` | `content_type_provisioning` | `Add-PnPContentType` / `Add-PnPFieldToContentType` / `Remove-PnPFieldFromContentType` / `Add-PnPContentTypeToList` |
| `spo-provision-site-columns.ps1` | `field_provisioning` | `Add-PnPField` / `Add-PnPFieldFromXml` |
| `spo-update-site-column.ps1` | *(custom/manual plan JSON)* | `Set-PnPField` |
| `spo-remove-site-column.ps1` | *(custom/manual plan JSON)* | `Remove-PnPField` |
| `spo-update-content-type.ps1` | *(custom/manual plan JSON)* | `Set-PnPContentType` |
| `spo-remove-content-type.ps1` | *(custom/manual plan JSON)* | `Remove-PnPContentType` |
| `spo-detach-content-type-from-list.ps1` | *(custom/manual plan JSON)* | `Remove-PnPContentTypeFromList` |
| `spo-add-list-column.ps1` | *(custom/manual plan JSON)* | `Add-PnPField` (list scoped) |
| `spo-update-list-column.ps1` | *(custom/manual plan JSON)* | `Set-PnPField` (list scoped) |
| `spo-remove-list-column.ps1` | *(custom/manual plan JSON)* | `Remove-PnPField` (list scoped) |
| `spo-provision-list-view.ps1` | *(custom/manual plan JSON)* | `Add-PnPView` |
| `spo-add-list-item.ps1` | *(custom/manual plan JSON)* | `Add-PnPListItem` |
| `spo-provision-site.ps1` | *(custom/manual plan JSON)* | `New-PnPSite` / `Set-PnPRegionalSettings` |
| `spo-provision-branding.ps1` | *(custom/manual plan JSON)* | `Set-PnPWebTheme` / `Set-PnPSite -LogoFilePath` |
| `spo-manage-hub-site.ps1` | *(custom/manual plan JSON)* | `Register-PnPHubSite` / `Add-PnPHubSiteAssociation` |
| `spo-create-modern-page.ps1` | *(custom/manual plan JSON)* | `Add-PnPPage` / `Add-PnPPageSection` |
| `spo-configure-webparts.ps1` | *(custom/manual plan JSON)* | `Add-PnPPageWebPart` |
| `spo-configure-library-settings.ps1` | *(custom/manual plan JSON)* | `Set-PnPList` (versioning/approval) |
| `spo-provision-permissions.ps1` | *(custom/manual plan JSON)* | `New-PnPGroup` / `Set-PnPGroupPermissions` / `Add-PnPUserToGroup` |
| `spo-configure-item-permissions.ps1` | *(custom/manual plan JSON)* | `Set-PnPListItemPermission` |
| `spo-configure-column-formatting.ps1` | *(custom/manual plan JSON)* | `Set-PnPField -Values CustomFormatter` |
| `spo-provision-navigation.ps1` | *(custom/manual plan JSON)* | `Add-PnPNavigationNode` |
| `spo-provision-term-set.ps1` | *(custom/manual plan JSON)* | `New-PnPTermGroup` / `New-PnPTermSet` / `New-PnPTerm` |
| `spo-trigger-reindex.ps1` | *(custom/manual plan JSON)* | `Request-PnPReIndexWeb` / `Request-PnPReIndexList` |

These scripts cover the complete spectrum of SharePoint tenant provisioning and configuration operations. Each script validates its specific confirmation token, operates in dry-run mode by default, and requires `-Execute` to execute against live tenant infrastructure.

## Every script shares the same safety contract

`Get-WorkbenchConnectionConfig.ps1` is a shared dot-sourced connection-resolution
helper used by all the scripts in the table above -- it is not a standalone
executor and has no plan JSON shape of its own, which is why it does not
appear as a table row.

Dry-run by default, `-Execute` plus an operation-specific `-ConfirmToken`
required for any real write, connection resolved via
`Get-WorkbenchConnectionConfig.ps1` or explicit `-SiteUrl`/`-ClientId`/
`-TenantId`/`-TenantAdminUrl` parameters, `Connect-PnPOnline -Interactive`
per `.agent/rules/sharepoint-ps1-authentication-convention.md`. See each
script's own `.SYNOPSIS`/`.DESCRIPTION` for its exact plan JSON shape and
confirmation token string.

## No tenant writes without -Execute

Every script here prints a dry-run JSON action summary (including the exact
PnP cmdlet call it would run) when `-Execute` is omitted. Nothing is written
to the tenant until you pass both `-Execute` and the correct
`-ConfirmToken`.

