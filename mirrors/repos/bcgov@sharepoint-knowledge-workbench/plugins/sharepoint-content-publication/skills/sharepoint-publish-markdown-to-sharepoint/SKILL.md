---
name: sharepoint-publish-markdown-to-sharepoint
plugin: sharepoint-content-publication
description: Builds a human-actionable publish plan mapping rendered Markdown and media files to an exact SharePoint library and folder, then a real PnP executor uploads it with Add-PnPFile and checkout/checkin discipline. Use to publish rendered Markdown output to a document library. Dry-run by default.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_publish_plan import build_markdown_publish_plan; print(build_markdown_publish_plan('doc-1', 'rendered/', 'KnowledgeLibrary', 'Manual'))\""
  - "pwsh -File scripts/spo-publish-markdown-plan.ps1 -PlanPath plan.json -SiteUrl \"https://tenant.sharepoint.com/sites/Test\""
---

# Publish Markdown to SharePoint

Build a `PublishPlan` (source file to target library, folder and filename) and upload it with the real executor.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Planning performs zero tenant I/O. The executor `scripts/spo-publish-markdown-plan.ps1` is dry-run by default and writes
  nothing without `-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN`. A real run is a live tenant write that the user runs.
- Overwriting an existing file uses `Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType MajorCheckIn` around
  `Add-PnPFile`.
- Require an explicit target library and folder; there is no default target. Refuse a missing or empty source directory.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`); the default config path
  does not resolve there.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_publish_plan import build_markdown_publish_plan
plan = build_markdown_publish_plan(document_id, source_dir, target_library, target_folder)
```

## Workflow

1. Build the plan from `document_id`, the rendered source directory, `target_library` and `target_folder`.
2. Save `plan` as JSON and run the executor as a dry run: `pwsh -File scripts/spo-publish-markdown-plan.ps1 -PlanPath plan.json`.
3. After the user confirms, rerun with `-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN`.

## Verification

Confirm the dry run lists every expected source-to-target mapping. After a real run, validate with
`sharepoint-validate-publication`; roll back with `sharepoint-rollback-sharepoint-publication` if needed.

## References

- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for the full executor table, the
  connection and config note, and the corrections history.
