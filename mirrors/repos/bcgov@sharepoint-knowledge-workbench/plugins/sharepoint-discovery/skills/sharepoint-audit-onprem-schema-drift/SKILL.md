---
name: sharepoint-audit-onprem-schema-drift
plugin: sharepoint-discovery
description: Compares field schemas between a set of source lists and a set of destination lists on a legacy on-prem SP2016 site -- missing fields, type mismatches, required-field mismatches, broken lookup references, and workflow associations -- for schema-drift root-cause analysis ahead of a migration or workflow investigation.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 -SiteUrl \"https://sp2016.example.org/sites/Legacy\" -SourceListNames @('Requests') -DestinationListPattern \"Archive_*\" -OutputDir .\\schema-drift-report"
---

# Audit On-Prem Schema Drift

## Trigger and Purpose

Use this skill when you need to know whether field-schema drift between a
"source of record" list and a set of downstream/destination lists explains
a data-copy or workflow failure on a legacy on-premises SP2016 site, or
ahead of planning a migration that depends on those schemas matching. It
compares field schemas (by internal name) between caller-supplied source
lists and caller-supplied destination lists -- missing fields, type
mismatches, required-field mismatches in either direction -- and also
validates lookup-field references and inspects workflow associations across
every list on the site.

## Read-only guarantee

The script performs site reads only -- `Get-PnP*` cmdlets and CSOM
`ExecuteQuery()` calls that only load and read list/field/workflow objects.
Zero writes. This is enforced as a hard rule in the script's own header.

## Honest outcomes

Failed `Get-PnPField`/`Get-PnPContentType` calls or workflow-association
reads emit `Write-Warning` and the affected record set is left empty --
never fabricated or silently skipped without a warning.

## Usage

```bash
pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 \
  -SiteUrl "https://sp2016.example.org/sites/Legacy" \
  -SourceListNames @('Matches_Received','All_Appearances') \
  -DestinationListPattern "Cal_*" \
  -OutputDir .\schema-drift-report

pwsh -File scripts/audit-onprem-sharepoint-schema-drift.ps1 \
  -SiteUrl "https://sp2016.example.org/sites/Legacy" \
  -SourceListNames @('Requests') \
  -DestinationListNames @('Archive_2024','Archive_2025') \
  -WatchFieldNames @('Case_ID','Status') \
  -UseCredential
```

`-SiteUrl` falls back to `SiteUrl` in this plugin's `config.psd1` if
omitted, the same way other scripts in this plugin do. Auth is via
`Connect-PnPOnline -UseWebLogin` (or `-Credentials` with `-UseCredential`) --
a documented exception to this repo's modern-SPO `-Interactive` convention,
since PnP.PowerShell supports on-prem SP2016 via CSOM/web-login rather than
Entra app registrations. See
`.agent/rules/sharepoint-ps1-authentication-convention.md`.

`-WatchFieldNames` is optional and only narrows the dedicated "Field Types"
report section in the markdown output -- the field-schema CSV and the
source/destination mismatch comparison always cover every field on every
list regardless of this parameter.

## Output

Five CSVs (`SchemaDrift-ListSchema.csv`, `SchemaDrift-FieldSchema.csv`,
`SchemaDrift-ContentTypes.csv`, `SchemaDrift-SchemaMismatches.csv`,
`SchemaDrift-WorkflowDependencies.csv`) plus one markdown summary report
(`SchemaDrift-Report.md`) combining all findings with a recommended-
remediation section, written to `-OutputDir`.

## Scripts

- `scripts/audit-onprem-sharepoint-schema-drift.ps1` -- on-prem SP2016 PnP.PowerShell field-schema drift comparison, lookup validation, and workflow inspection

## Related asset (does not directly consume this skill's output)

`plugins/sharepoint-discovery/assets/master-discovery-meta-review-template.md`
is a generalized migration-readiness catalog template ported from the same
source project as this skill's script. It is a much broader 13-domain
site-modernization summary (page inventory, web part scans, navigation,
permissions, link surfaces, etc.) fed by many discovery passes, not just
schema comparison -- this skill's CSV/markdown output does not map onto its
placeholders in any direct way, so it is ported here as a standalone asset
for whoever assembles that broader catalog, not as an integrated output
format of this skill.

## Provenance

Ported and generalized from
`plugins/sharepoint-migration/scripts/diagnose-onprem-schema-drift.ps1` in
the originating SharePoint migration repository. All hardcoded sentinel
field names, source/destination list names, wildcard patterns, and
project-specific report prose were removed in favor of explicit
`-SourceListNames`/`-DestinationListNames`/`-DestinationListPattern`/
`-WatchFieldNames` parameters.

