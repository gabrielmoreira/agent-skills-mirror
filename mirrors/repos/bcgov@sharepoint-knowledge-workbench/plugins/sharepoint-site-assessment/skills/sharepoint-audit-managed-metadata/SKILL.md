---
name: sharepoint-audit-managed-metadata
plugin: sharepoint-site-assessment
description: Audits a live SharePoint site for Managed Metadata (Taxonomy) usage, covering term group and term-set discovery plus every list, library and site column bound to a Taxonomy field, for modern SPO (PnP.PowerShell) or legacy on-prem SP2016 (NTLM/Kerberos REST plus CSOM). Use ahead of a migration or schema-design decision to learn whether and where a site uses Managed Metadata.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/audit-sharepoint-managed-metadata.ps1 -SiteUrl \"https://tenant.sharepoint.com/sites/Test\" -TermGroupName \"Enterprise Taxonomy\" -OutputPath managed-metadata-audit.json"
  - "pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -TermGroupName \"Enterprise Taxonomy\" -OutputPath managed-metadata-audit.json -UseDefaultCredentials"
---

# Audit Managed Metadata

Resolve a named Term Group's term sets and scan every list, library and site column for
`TaxonomyField` and `TaxonomyFieldTypeMulti` fields. Pick the script by site type.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Reads only. Both scripts use `Get-PnP*` cmdlets, `Invoke-RestMethod` GET calls, or CSOM
  `ExecuteQuery()` calls that only load and read term-store objects. Zero writes.
- Never fabricate or silently drop a failure. Failed REST calls, PnP errors and an unresolvable Term
  Group are recorded as `Error` or `Found: false` fields in the JSON. A CSOM assembly or version
  failure on-prem is a non-fatal finding, not an exception.
- Both scripts perform live tenant I/O and the user runs them. On-prem uses NTLM/Kerberos because
  there is no Entra app-registration path in general use there.

## Quick start

```bash
pwsh -File scripts/audit-sharepoint-managed-metadata.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json
```

## Workflow

1. Choose the script: `scripts/audit-sharepoint-managed-metadata.ps1` for modern SPO (term group,
   term-set lookup, list/library and site-column Taxonomy scan), or
   `scripts/audit-onprem-sharepoint-managed-metadata.ps1` for on-prem SP2016 (same checks, plus an
   optional `-ParentSiteUrl` second site and a CSOM `TaxonomySession` term-store lookup).
2. On-prem examples:

   ```bash
   pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -TermGroupName "Enterprise Taxonomy" -OutputPath managed-metadata-audit.json -UseDefaultCredentials
   pwsh -File scripts/audit-onprem-sharepoint-managed-metadata.ps1 -SiteUrl "https://sp2016.example.org/subsite" -ParentSiteUrl "https://sp2016.example.org" -OutputPath managed-metadata-audit.json
   ```
3. Read the JSON written to `-OutputPath` and report the term sets and every Taxonomy-bound field.

## Verification

Confirm the JSON exists at `-OutputPath`, then list any `Error` or `Found: false` entries as
findings rather than treating the audit as clean.

## References

- [Provenance](references/managed-metadata-audit-provenance.md): read to see what was removed from
  the source scripts when they were generalized.
