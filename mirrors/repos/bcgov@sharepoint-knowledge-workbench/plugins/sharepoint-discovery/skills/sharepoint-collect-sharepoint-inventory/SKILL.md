---
name: sharepoint-collect-sharepoint-inventory
plugin: sharepoint-discovery
description: Collects a live SharePoint inventory -- lists/libraries, list fields, library files, content-type/schema exports (modern SPO via PnP.PowerShell), and full site crawls or quick item/storage counts plus bulk .aspx page downloads (legacy on-prem SP2016 via NTLM/Kerberos REST) -- for consumption by this plugin's read-only analysis skills or ad hoc review.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -Mode Lists -OutputPath lists.json"
  - "pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -OutputDir .\\inventory -UseDefaultCredentials"
  - "pwsh -File scripts/collect-sharepoint-schema-export.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -OutputDir .\\schema-export"
---

# Collect SharePoint Inventory

## Trigger and Purpose

Use this skill when you need a fresh, real inventory of a SharePoint site --
either a modern SPO site (via PnP.PowerShell) or a legacy on-premises SP2016
site (via NTLM/Kerberos REST, since on-prem has no Entra app-registration
path in general use here). This is this plugin's first **collector** skill --
every other skill in `sharepoint-discovery` is read-only analysis of an
export you already have; these scripts are what actually connect to a
tenant/site and produce that export.

## Read-only guarantee

All three scripts perform tenant/site **reads only** -- `Get-PnP*` cmdlets or
`Invoke-RestMethod`/`Invoke-WebRequest` GET calls. Zero writes.

## Honest outcomes

Failed REST calls or PnP cmdlet errors emit `Write-Warning` and the affected
record set is left empty -- never fabricated or silently skipped without a
warning.

## Scripts and what each subsumes

Three scripts consolidate seven source collectors from the originating
migration repository. Nothing below was silently dropped -- see each
script's own header for the detailed per-source mapping. A fourth script,
`collect-sharepoint-schema-export.ps1`, is this plugin's own orchestrator
(not ported from a source collector) that assembles the directory-tree
shape `sharepoint-schema`'s analysis tools expect out of several
`collect-sharepoint-inventory.ps1` invocations.

| Script | Target | Subsumes (source file) |
| --- | --- | --- |
| `collect-sharepoint-inventory.ps1` | Modern SPO, PnP.PowerShell | `export-sharepoint-inventory.ps1` / `-custom.ps1` (list/library enumeration value only, `-Mode Lists`); `export-persons-picture-description.ps1` (`-Mode ListFields`, generalized from hardcoded Persons/Comment); `export-images-library-inventory.ps1` (`-Mode LibraryFiles`, generalized from hardcoded Images1); `discover-sandbox-definitions.ps1` (`-Mode ContentTypes`, generalized from hardcoded Sandbox/NTT site URLs and list names) |
| `collect-onprem-sharepoint-inventory.ps1` | On-prem SP2016, NTLM/Kerberos REST | `export-sharepoint-inventory.ps1` and `export-sharepoint-inventory-custom.ps1` (full crawl -- default mode, generalized: no hardcoded site URL/output path); `get-source-item-counts.ps1` (`-QuickCountsOnly`, generalized: no hardcoded config-only SiteUrl) |
| `collect-onprem-sharepoint-aspx-pages.ps1` | On-prem SP2016, NTLM/Kerberos REST | `extract-all-aspx-pages.ps1` (generalized: no hardcoded `legacy-sharepoint.domain.local` default, no hardcoded `01_source_sharepoint` output path) |
| `collect-sharepoint-schema-export.ps1` | Modern SPO, PnP.PowerShell | Not ported -- new orchestrator. Drives `collect-sharepoint-inventory.ps1` once per mode/per-list to assemble `summary/{lists,content_types}.json` + `lists/<name>/{fields,content_types}.json`. Does **not** produce `summary/site_columns.json` -- `collect-sharepoint-inventory.ps1` has no site-columns-only mode; see the orchestrator's own header for the full gap description. |

## Usage

### Modern SPO -- lists/libraries, list fields, library files, content types

```bash
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode Lists -OutputPath lists.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ListFields -ListName "Persons" -FieldNames "Comment" -OutputPath persons-comment.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode LibraryFiles -ListName "Images1" -OutputPath images1-files.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ContentTypes -ContentTypeNameFilter "Modern_*" -ListNames "MyList" -OutputPath schema.json
```

### On-prem SP2016 -- full crawl or quick counts

```bash
pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\inventory -UseDefaultCredentials
pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\quick-counts.csv -QuickCountsOnly -UseDefaultCredentials
```

### On-prem SP2016 -- bulk .aspx page download

```bash
pwsh -File scripts/collect-onprem-sharepoint-aspx-pages.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials
```

### Modern SPO -- full schema-export directory tree (for sharepoint-schema)

```bash
pwsh -File scripts/collect-sharepoint-schema-export.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputDir .\schema-export
```

## Scripts

- `scripts/collect-sharepoint-inventory.ps1` -- modern SPO PnP.PowerShell collector (`-Mode Lists|ListFields|LibraryFiles|ContentTypes`)
- `scripts/collect-onprem-sharepoint-inventory.ps1` -- on-prem SP2016 NTLM/REST full-crawl or quick-counts collector
- `scripts/collect-onprem-sharepoint-aspx-pages.ps1` -- on-prem SP2016 NTLM/REST bulk `.aspx` downloader
- `scripts/collect-sharepoint-schema-export.ps1` -- orchestrates `collect-sharepoint-inventory.ps1` into the `summary/`+`lists/<name>/` directory tree `sharepoint-schema`'s tools consume

## Provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/{inventory,diagnostics,utilities,content-migration,page-migration}/` in the originating SharePoint migration repository. All hardcoded site URLs, project codenames, and output-path defaults were removed in favor of explicit parameters.

