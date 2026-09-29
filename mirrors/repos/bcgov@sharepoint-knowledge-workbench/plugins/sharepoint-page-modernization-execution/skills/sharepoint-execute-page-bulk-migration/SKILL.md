---
name: sharepoint-execute-page-bulk-migration
plugin: sharepoint-content-publication
description: Orchestrates classic-to-modern page conversion across every page in a library, one subprocess per page with a resumable manifest and post-run validation. Dry-run by default; real writes gated behind -Execute and a confirmation token.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary \"ClassicPages\" -FieldMapping field-mapping.json -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK"
---

# Execute Page Bulk Migration

## Trigger and Purpose

Use this skill to convert every classic page in a library to modern
SharePoint pages in one run. Each page is converted by its own
`convert-page-to-modern` subprocess -- a failure on one page is recorded and
the run continues, it never aborts the whole batch.

## Resumable and throttled

Every page's result (Succeeded/Failed/Skipped, timing, error) is appended to
`-ManifestPath` as the run proceeds, so an interruption preserves everything
completed so far. Re-run with `-ResumeFromManifest` to skip pages already
recorded as Succeeded. A configurable delay (`-ThrottleDelaySeconds`,
default 2) runs between pages to avoid SharePoint Online rate limiting.

## Validates itself when done

Unless `-SkipValidation` is set, this skill calls `validate-page-migration`
against the manifest automatically once the bulk run completes, and exits
non-zero if any page fails validation.

## Not included: link remediation

This skill does not rewrite embedded links in converted page bodies --
`ConvertTo-PnPPage` doesn't do that for same-site conversions (see
`convert-page-to-modern`'s own "Real platform constraint recorded" note).
Run `sharepoint-link-remediation`'s remediation skill separately afterward
if the converted content contains embedded links that need fixing.

## Safety

Dry run by default -- prints the page-conversion plan, spawns zero
subprocesses, makes zero tenant writes. Real writes require
`-Execute -ConfirmToken CONVERT-SPO-PAGES-BULK`.

## Usage

```bash
# Dry run
pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages"

# Test with a single page first
pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -PageName "article.aspx" -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK

# Full bulk run
pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -FieldMapping field-mapping.json -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK

# Resume an interrupted run
pwsh -File scripts/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -ResumeFromManifest -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK
```

## Scripts

- `scripts/spo-convert-pages-bulk.ps1` -- real orchestrator (subprocess-per-page, manifest, resume, throttle)
- `scripts/spo-convert-page-to-modern.ps1` -- the per-page worker this skill invokes (shared with `convert-page-to-modern`)
- `scripts/spo-validate-page-conversion.ps1` -- the post-run validator this skill invokes (shared with `validate-page-migration`)

## Provenance

Generalized from the originating SharePoint migration repository's
`link-conversion/Invoke-LinkConversionBulk.ps1` -- removed hardcoded project
naming, kept the subprocess-per-page/manifest/resume/throttle pattern as-is
(it was already generic). The source's own link-repair step was dropped
here (that capability belongs to `sharepoint-link-remediation`, a different
plugin, not duplicated into this one) -- see "Not included" above.

