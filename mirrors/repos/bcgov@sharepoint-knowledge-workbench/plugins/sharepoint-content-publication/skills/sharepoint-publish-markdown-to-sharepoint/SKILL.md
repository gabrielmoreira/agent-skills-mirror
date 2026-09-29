---
name: sharepoint-publish-markdown-to-sharepoint
description: Builds a human-actionable publish plan for rendered Markdown + media to an exact SharePoint library/folder, then a real PnP executor uploads it (Add-PnPFile with checkout/checkin discipline). Dry-run by default.
---

# publish-markdown-to-sharepoint

## Purpose

Produces a `PublishPlan` — an exact list of source file → target library/folder/filename
mappings — via `sharepoint_publish_plan.py`. The real executor,
`scripts/spo-publish-markdown-plan.ps1`, then uploads it: `Add-PnPFile`, with
`Set-PnPFileCheckedOut`/`Set-PnPFileCheckedIn -CheckinType MajorCheckIn` around any overwrite of
an existing file. Dry-run by default; real writes require `-Execute -ConfirmToken
PUBLISH-SPO-MARKDOWN`.

**Correction (2026-08-17):** this SKILL.md previously said upload "remain[s] gated behind Stage
3.4.3's approved-write-identity decision." That was a stale/incorrect blocker — Stage 3.4.3
concerns a separate, not-yet-approved write identity; this plugin's other real executors
(`spo-upload-plan.ps1`, `spo-convert-page-to-modern.ps1`, etc.) already run today under the same
interactive `Connect-PnPOnline` convention every plugin in this workbench uses, with no Stage
3.4.3 dependency. The real gap was simply that no `Add-PnPFile` executor had been built yet — now
fixed.

## Input boundaries

- `document_id`, a local rendered source directory, and an explicit target library/folder — no
  default target.
- Refuses to build a plan from a missing or empty source directory.

## Prohibited scope

- The planning module itself performs zero tenant I/O — it only builds the plan.
- The real executor performs no write without `-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN`.

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_markdown_publish_plan`)
- Real executor: `../../scripts/spo-publish-markdown-plan.ps1`

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py`

