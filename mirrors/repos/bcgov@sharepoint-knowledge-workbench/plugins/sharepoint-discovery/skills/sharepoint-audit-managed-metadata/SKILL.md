---
name: sharepoint-audit-managed-metadata
plugin: sharepoint-discovery
description: Audits a live SharePoint site for Managed Metadata (Taxonomy) usage -- term group/term-set discovery plus every list/library and site column bound to a Taxonomy field -- for modern SPO (PnP.PowerShell) or legacy on-prem SP2016 (NTLM/Kerberos REST + CSOM) sites.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/audit-sharepoint-managed-metadata.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -TermGroupName \"Enterprise Taxonomy\" -OutputPath managed-metadata-audit.json"
  - "pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -TermGroupName \"Enterprise Taxonomy\" -OutputPath managed-metadata-audit.json -UseDefaultCredentials"
---

# Audit Managed Metadata

## Trigger and Purpose

Use this skill when you need to know whether -- and where -- a SharePoint
site uses Managed Metadata (Taxonomy) columns, ahead of a migration or
schema-design decision. It resolves a named Term Group's term sets and scans
every list/library and site column for `TaxonomyField`/
`TaxonomyFieldTypeMulti` fields, for either a modern SPO site (via
PnP.PowerShell) or a legacy on-premises SP2016 site (via NTLM/Kerberos REST +
CSOM, since on-prem has no Entra app-registration path in general use here).

## Read-only guarantee

Both scripts perform tenant/site **reads only** -- `Get-PnP*` cmdlets,
`Invoke-RestMethod` GET calls, or CSOM `ExecuteQuery()` calls that only load
and read term-store objects. Zero writes.

## Honest outcomes

Failed REST calls, PnP cmdlet errors, or an unresolvable Term Group are
recorded as `Error`/`Found: false` fields in the JSON output -- never
fabricated or silently dropped. A CSOM assembly/version failure on-prem is
likewise recorded as a non-fatal finding, not thrown.

## Usage

### Modern SPO

```bash
pwsh -File scripts/audit-sharepoint-managed-metadata.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json
```

### On-prem SP2016

```bash
pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json -UseDefaultCredentials
pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/subsite" -ParentSiteUrl "https://sp2016.example.org" -OutputPath managed-metadata-audit.json
```

## Scripts

- `scripts/audit-sharepoint-managed-metadata.ps1` -- modern SPO PnP.PowerShell audit (term group/term-set lookup + list/library + site column Taxonomy-field scan)
- `scripts/audit-onprem-sharepoint-managed-metadata.ps1` -- on-prem SP2016 NTLM/REST + CSOM audit (same checks, plus optional `-ParentSiteUrl` second site and CSOM `TaxonomySession` term-store lookup)

## Provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/inventory/check-managed-metadata-custom.ps1` and `plugins/sharepoint-migration/scripts/utilities/check-managed-metadata-spo-prod.ps1` in the originating SharePoint migration repository. All hardcoded site URLs, project codenames, and output defaults were removed in favor of explicit `-SiteUrl`/`-ParentSiteUrl`/`-TermGroupName` parameters, and console-only (`Write-Host`/`Format-Table`) output was replaced with structured JSON via a required `-OutputPath` parameter.

