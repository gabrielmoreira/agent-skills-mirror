---
name: sharepoint-validate-page-modernization
plugin: sharepoint-site-migration
description: Read-only validation of converted modern pages against a run manifest, checking page existence, mapped-field population and literal field values. Use after a conversion run, to confirm every page landed with its metadata. Writes a pass/fail test report and exits non-zero on any failure, for use in a pipeline.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -ReportPath test-report.csv"
---

# Validate Page Migration

Independently confirm every converted page landed with the metadata it should have. It never trusts the conversion run's own exit code.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: REST and PnP read cmdlets only, so there is no `-Execute` or token. It does re-query the live site, so the user runs it.
- Use the same `-FieldMapping` and `-LiteralFieldValues` files as the conversion run being validated.
- Exit non-zero on any failure, and never report success from the conversion run's own result.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -LiteralFieldValues literals.json -ReportPath test-report.csv
```

## Workflow

Page arrival/metadata checks do not establish embedded-link correctness. After this validation,
export modern stored fields with `sharepoint-extract-links`, run the Python CSV extractor and
validate resulting destinations separately with `sharepoint-validate-link-integrity`.
See [bulk content workflow](references/bulk-content-link-workflow.md).

1. Get the run manifest from `sharepoint-convert-page-library-to-modern` and the mapping files used.
2. Run the script; add `-IncludeSkipped` to include pages recorded as Skipped.
3. Report the pass/fail results from the report file.

## Verification

Every manifest page exists in `-TargetLibrary`, every mapped target field is non-empty, and every literal field equals its expected value exactly. A non-zero exit means the migration is not validated.

## References

- [Validation details](references/page-migration-validation-details.md): read for what is checked, usage and provenance.
- [Gates, tokens and config](references/page-execution-gates-and-config.md): read for the `-ConfigPath` note.
