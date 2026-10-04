---
name: sharepoint-collect-site-inventory
plugin: sharepoint-site-assessment
description: Collects a live SharePoint inventory: lists and libraries, list fields, library files and content-type/schema exports (modern SPO via PnP.PowerShell), plus full site crawls, quick item and storage counts and bulk .aspx page downloads (legacy on-prem SP2016 via NTLM/Kerberos REST). Use when you need a fresh export for this plugin's read-only analysis skills or for ad hoc review.
allowed-tools: Bash, Read
examples:
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
   - `collect-sharepoint-inventory.ps1`: modern SPO, `-Mode Lists|ListFields|LibraryFiles|ContentTypes`.
   - `collect-onprem-sharepoint-inventory.ps1`: on-prem full crawl, or `-QuickCountsOnly`.
   - `collect-onprem-sharepoint-aspx-pages.ps1`: on-prem bulk `.aspx` download.
   - `collect-sharepoint-schema-export.ps1`: modern SPO schema-export directory tree for the schema
     skills (no `summary/site_columns.json`; see the orchestrator's header).
2. Hand the user the command with their parameters; examples are in
   [collectors](references/inventory-collectors.md).
3. Pass the resulting export to the matching analysis skill.

## Verification

Confirm the output file or directory exists and list every `Write-Warning` as a gap rather than a
clean result.

## References

- [Collectors](references/inventory-collectors.md): read for the full per-mode usage, which source
  collector each script subsumes, and provenance.
