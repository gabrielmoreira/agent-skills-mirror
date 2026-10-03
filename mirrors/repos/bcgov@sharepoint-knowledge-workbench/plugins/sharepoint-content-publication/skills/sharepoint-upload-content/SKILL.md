---
name: sharepoint-upload-content
plugin: sharepoint-content-publication
description: Executes a PublishPlan (built by sharepoint-publish-aspx-to-sharepoint or sharepoint-publish-markdown-to-sharepoint) either through an explicitly injected Python uploader or through a real PnP executor that creates and publishes modern pages. Use to carry out a page-publication plan. Zero tenant I/O by default.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl \"https://tenant.sharepoint.com/sites/Test\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_upload import upload_pages; upload_pages(plan, uploader)\""
---

# Upload Content

Execute a `PublishPlan`'s actions: create a modern page (or upload a site asset) per action.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O unless the caller explicitly injects a real `uploader`. `upload_pages` raises `NotImplementedError` without one,
  and stops on the first failed action rather than reporting partial success.
- The real executor `scripts/spo-upload-plan.ps1` is dry-run by default and writes nothing without
  `-Execute -ConfirmToken UPLOAD-SPO-PLAN`. A real run is a live tenant write that the user runs.
- Never attempt raw `.aspx` upload (blocked). Create pages with `Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage`.
- Page creation from pre-rendered HTML fragments only (the `content-render-sharepoint-aspx` skill's output). File and asset upload
  to a library is `sharepoint-publish-markdown-to-sharepoint`'s job.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test"
```

## Workflow

1. Get a `PublishPlan` JSON from `sharepoint-publish-aspx-to-sharepoint`.
2. Dry run the executor (above); review the planned pages.
3. After the user confirms, rerun with `-Execute -ConfirmToken UPLOAD-SPO-PLAN` (add `-Overwrite` only if replacing is intended).
4. Or, from Python, call `upload_pages(plan, uploader)` with an injected uploader.

## Verification

Confirm each planned page was created and published, then check with `sharepoint-validate-publication`.

## References

- [Upload details](references/upload-content-details.md): read for the two execution paths and the scope.
- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for the executor table, config note and
  provenance.
