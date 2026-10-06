---
name: sharepoint-collect-site-inventory
plugin: sharepoint-site-assessment
description: >-
  Use when you need a live SharePoint inventory of all site contents: files, documents, images, pages and libraries across all subsites, exported to CSV; or lists, fields, content types, schema exports, on-prem full site crawls, item/storage counts or bulk .aspx downloads. Supports SharePoint Online and on-prem SP2016. Use for fresh discovery exports and read-only content inventories.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/collect-sharepoint-content-inventory.ps1 -ConfigPath config-spo-prod.psd1 -OutputDir temp/content-inventory"
  - "Inventory every document, image and page across all libraries and subsites as CSV, excluding ordinary list items"
  - "pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -Mode Lists -OutputPath lists.json"
  - "pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -OutputDir .\\inventory -UseDefaultCredentials"
  - "pwsh -File scripts/collect-sharepoint-schema-export.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -OutputDir .\\schema-export"
---

# Collect SharePoint Inventory

The plugin's collector skill. Every other discovery skill analyses an export you already have; these
scripts connect to a site and produce that export.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Reads only. All scripts use `Get-PnP*` cmdlets or `Invoke-RestMethod`/`Invoke-WebRequest` GET
  calls. Zero writes.
- Never fabricate or silently skip. Failed REST calls and PnP errors emit `Write-Warning` and leave
  the affected record set empty.
- The scripts perform live tenant I/O and the user runs them. On-prem uses NTLM/Kerberos REST,
  since there is no Entra app-registration path in general use there.

## Quick start

```bash
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode Lists -OutputPath lists.json
```

## Workflow

1. Pick the script by target and need:
   - **All files/documents/images/pages across libraries and subsites**:
     `collect-sharepoint-content-inventory.ps1 -ConfigPath <config.psd1> -OutputDir <directory>`.
     `-SiteUrl` overrides the config target. `-Platform Auto` (default) recognizes standard
     SharePoint Online hostnames (`*.sharepoint.com`, plus
     `.us/.de/.cn`); other hosts select on-prem. Override with `-Platform Online|OnPrem`
     for custom/ambiguous hosts. Online uses browser-based interactive authentication; on-prem
     prompts for credentials unless `-Credential` is supplied. The new collector never uses
     default Windows session credentials. Config client/tenant IDs apply only to Online auth.
     Includes hidden/system libraries, nested files, empty libraries and direct web-root files.
     Excludes ordinary list items/attachments, generated list forms/views and historical versions.
     Exports `files.csv`, `libraries.csv`, `errors.csv`, `manifest.json`; see the collector reference
     for column definitions and scope limitations. This is the file inventory route, not `Lists`
     mode or the single-library `LibraryFiles` mode.
   - `collect-sharepoint-inventory.ps1`: modern SPO, `-Mode Lists|ListFields|LibraryFiles|ContentTypes`.
   - `collect-onprem-sharepoint-inventory.ps1`: on-prem full crawl, or `-QuickCountsOnly`.
   - `collect-onprem-sharepoint-aspx-pages.ps1`: on-prem bulk `.aspx` download.
   - `collect-sharepoint-schema-export.ps1`: modern SPO schema-export directory tree for the schema
     skills (no `summary/site_columns.json`; see the orchestrator's header).
2. Before live collection, follow `workbench-validate-sharepoint-connection` for the selected
   profile/target. Hand the user the command with their parameters; examples are in
   [collectors](references/inventory-collectors.md).
3. Pass the resulting export to the matching analysis skill.

## Verification

Confirm the output file or directory exists and list every `Write-Warning` as a gap rather than a
clean result. For content inventories, check `manifest.json`: `COMPLETE` means collection succeeded
within its declared scope; `EMPTY` means no files; `PARTIAL`/`FAILED` means inspect `errors.csv`.
Partial/failed content collection exits nonzero and retains successful rows. Permission-trimmed
objects can remain invisible even without errors; do not claim tenant-wide completeness.

## References

- [Collectors](references/inventory-collectors.md): read for the full per-mode usage, which source
  collector each script subsumes, and provenance.
