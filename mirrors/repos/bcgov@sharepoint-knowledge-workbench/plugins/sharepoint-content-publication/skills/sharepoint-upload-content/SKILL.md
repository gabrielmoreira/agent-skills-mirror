---
name: sharepoint-upload-content
description: Executes a PublishPlan (built by publish-aspx-to-sharepoint or publish-markdown-to-sharepoint) via an explicitly injected uploader -- zero SharePoint tenant I/O by default, matching this plugin's Phase 3 package-only architecture.
---

# upload-content

## Purpose

Executes a `PublishPlan`'s actions -- creates a modern page or uploads a
site asset per action. Two execution paths exist:

1. **`sharepoint_upload.py::upload_pages(plan, uploader)`** -- a
   Python plan-execution loop requiring an injected `uploader(action) ->
   UploadResult` callable. Zero tenant I/O of its own; raises
   `NotImplementedError` without one.
2. **`scripts/spo-upload-plan.ps1`** -- a real, working PowerShell executor
   for the modern-page-creation path described below. Reads a `PublishPlan`
   JSON file directly and creates/publishes each page for real, gated behind
   `-Execute -ConfirmToken UPLOAD-SPO-PLAN`. See "Real executor" below.

## Real platform constraint recorded

Same confirmed mechanism as `publish-aspx-to-sharepoint`'s SKILL.md: the
`Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage` modern-page-creation
call pattern is the only confirmed-working mechanism on this tenant (raw
`.aspx` upload is blocked). Any real `uploader` a caller injects should
follow that pattern (or the equivalent SharePoint REST calls), not attempt
raw file upload.

## Real executor

`scripts/spo-upload-plan.ps1` implements the constraint above directly: it
reads a `PublishPlan.to_dict()`-shaped JSON file and, per action, creates a
modern page via `Add-PnPPage`, injects the `source_path` file's content via
`Add-PnPPageTextPart`, and publishes via `Publish-PnPPage`. Dry run by
default; real writes require `-Execute -ConfirmToken UPLOAD-SPO-PLAN`.

```bash
pwsh -File scripts/spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
```

**Scope:** page creation from pre-rendered HTML only (`source_path` should
point at an HTML fragment file, matching `structured-content-rendering`'s
`render-sharepoint-aspx` output). Raw file/asset upload to a document
library (`Add-PnPFile`, with checkout/checkin discipline) is provided by
`spo-publish-markdown-plan.ps1` (see line 118).

It is not wired in as `sharepoint_upload.py`'s injected `uploader`
automatically -- Python cannot call a PowerShell script as an in-process
callback, so the two paths are used independently rather than composed.

## Input boundaries

- A `PublishPlan` (from `sharepoint_publish_plan.py`).
- An `uploader(action) -> UploadResult` callable, supplied by the caller.
  Without one, `upload_pages()` raises `NotImplementedError` -- this module
  ships no live PnP/REST client itself.

## Prohibited scope

- Zero tenant I/O unless the caller explicitly injects a real `uploader`.
- Stops on the first failed action rather than reporting partial success as
  full success.

## Scripts

- `../../scripts/sharepoint_upload.py` (`upload_pages`, `UploadResult`, `UploadError`)
- `../../scripts/spo-upload-plan.ps1` -- real, working PnP.PowerShell executor (page-creation path)

## Tests

- `../../tests/unit/test_sharepoint_upload.py`

## Provenance

Authoritative publication and upload skill
(`scripts/upload/upload-modern-page.ps1`,
`scripts/upload/upload-modern-page-rest.ps1`) -- see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`
for the full source-to-destination record.

