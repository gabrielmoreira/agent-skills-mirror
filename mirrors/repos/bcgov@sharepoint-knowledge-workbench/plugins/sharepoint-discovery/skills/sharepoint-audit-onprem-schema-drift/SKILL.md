---
name: sharepoint-audit-onprem-schema-drift
plugin: sharepoint-discovery
description: Compares field schemas between a set of source lists and a set of destination lists on a legacy on-prem SP2016 site, reporting missing fields, type mismatches, required-field mismatches, broken lookup references and workflow associations. Use for schema-drift root-cause analysis when a data copy or workflow fails, or ahead of a migration that depends on matching schemas.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -SourceListNames @('Requests') -DestinationListPattern \"Archive_*\" -OutputDir .\\schema-drift-report"
---

# Audit On-Prem Schema Drift

Find out whether field-schema drift between a source-of-record list and its destination lists
explains a failure or blocks a migration.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Site reads only: `Get-PnP*` cmdlets and CSOM `ExecuteQuery()` calls that load and read
  list, field and workflow objects. Zero writes; the script's own header enforces this as a hard rule.
- Never fabricate or silently skip. Failed `Get-PnPField` or `Get-PnPContentType` calls and
  workflow-association reads emit `Write-Warning` and leave the affected record set empty.
- Source and destination lists are always caller-supplied. No list names or sentinel fields are
  built in.
- The script performs live site I/O and the user runs it.

## Quick start

```bash
pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 \
  -SiteUrl "https://sp2016.example.org/sites/Legacy" \
  -SourceListNames @('Requests') -DestinationListPattern "Archive_*" \
  -OutputDir .\schema-drift-report
```

## Workflow

1. Choose the source lists (`-SourceListNames`) and the destinations (`-DestinationListNames` or
   `-DestinationListPattern`). Optionally narrow the field report with `-WatchFieldNames`.
2. Run the script; auth, `-UseCredential` and a second example are in
   [usage and output](references/schema-drift-usage-and-output.md).
3. Read `SchemaDrift-Report.md` in `-OutputDir` and report the mismatches, lookup problems and
   workflow dependencies.

## Verification

Confirm the five CSVs and `SchemaDrift-Report.md` exist in `-OutputDir`, and list every
`Write-Warning` as a gap rather than a clean result.

## References

- [Usage and output](references/schema-drift-usage-and-output.md): read for auth, more examples,
  the output files, and the related meta-review template.
- [Meta-review template](assets/master-discovery-meta-review-template.md): a standalone catalog
  template for a broader site-modernization summary; this skill's output does not map onto it.
