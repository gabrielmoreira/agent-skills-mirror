---
name: sharepoint-validate-page-migration
plugin: sharepoint-content-publication
description: Read-only validation of converted modern pages against a run manifest -- page existence, mapped-field population, and literal field values. Writes a pass/fail test report and exits non-zero on any failure, for use in a pipeline.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -ReportPath test-report.csv"
---

# Validate Page Migration

## Trigger and Purpose

Use this skill after `execute-page-bulk-migration` (or a manual
`convert-page-to-modern` run) to independently confirm every converted page
actually landed with the metadata it was supposed to get. It never trusts
the conversion run's own exit code -- it re-queries the live site.

## What is checked

- The modern page exists in `-TargetLibrary`.
- Every target field named as a value in `-FieldMapping` is non-empty.
- Every field named in `-LiteralFieldValues` equals its expected value
  exactly.

Both `-FieldMapping` and `-LiteralFieldValues` should be the same JSON files
passed to the conversion run being validated.

## Read-only guarantee

No writes to any tenant -- REST/PnP read cmdlets only.

## Usage

```bash
pwsh -File scripts/spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -LiteralFieldValues literals.json -ReportPath test-report.csv
```

## Scripts

- `scripts/spo-validate-page-conversion.ps1` -- real, read-only PnP.PowerShell validator

## Provenance

Generalized from the originating SharePoint migration repository's
`link-conversion/Test-LinkConversion.ps1` -- removed hardcoded expected
field names, replaced with the same caller-supplied `-FieldMapping`/
`-LiteralFieldValues` JSON files `convert-page-to-modern` accepts.

