---
name: sharepoint-execute-page-bulk-migration
plugin: sharepoint-page-modernization-execution
description: Orchestrates classic-to-modern page conversion across every page in a library, one subprocess per page, with a resumable manifest and post-run validation. Use to convert a whole library in one run. Dry-run by default; real writes are gated behind -Execute and a confirmation token.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary \"ClassicPages\" -FieldMapping field-mapping.json -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK"
---

# Execute Page Bulk Migration

Convert every classic page in a library to a modern page in one run, recording each page's result as it goes.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: it prints the conversion plan, spawns zero subprocesses and makes zero tenant writes. A real run needs `-Execute -ConfirmToken CONVERT-SPO-PAGES-BULK` and is a live tenant write that the user runs.
- A failure on one page is recorded and the run continues; it never aborts the batch. Every page's result is appended to `-ManifestPath`, so an interruption keeps what is done.
- It does not rewrite embedded links in converted pages; use the `sharepoint-link-remediation` skills afterward if needed.
- Try a single page first (`-PageName`). When running from an installed copy, pass `-ConfigPath`.

## Quick start

```bash
pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages"
```

## Workflow

1. Dry run the whole library, then test one page with `-PageName "article.aspx" -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK`.
2. After the user confirms, run the full library with `-Execute -ConfirmToken CONVERT-SPO-PAGES-BULK` (add `-FieldMapping`).
3. If interrupted, rerun with `-ResumeFromManifest` to skip pages already recorded as Succeeded. `-ThrottleDelaySeconds` (default 2) paces requests.
4. Validation runs automatically unless `-SkipValidation` is set; the run exits non-zero if any page fails.

## Verification

Read `-ManifestPath` for Succeeded, Failed and Skipped counts, and the validation report. Do not call the migration done while any page is Failed or failed validation.

## References

- [Bulk details](references/bulk-page-migration-details.md): read for resume, throttle, usage examples and provenance.
- [Gates, tokens and config](references/page-execution-gates-and-config.md): read for the token table and the `-ConfigPath` note.
