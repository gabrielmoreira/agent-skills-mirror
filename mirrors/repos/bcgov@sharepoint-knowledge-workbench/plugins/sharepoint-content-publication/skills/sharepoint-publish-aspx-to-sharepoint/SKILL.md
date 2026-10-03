---
name: sharepoint-publish-aspx-to-sharepoint
plugin: sharepoint-content-publication
description: Builds a human-actionable publish plan (a PublishPlan) for rendered content as SharePoint modern pages. Use after rendering, before uploading. Performs no tenant writes and never attempts raw .aspx upload (blocked); execution belongs to sharepoint-upload-content.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_publish_plan import build_aspx_publish_plan; print(build_aspx_publish_plan('doc-1', 'rendered/', '/sites/Test/SitePages'))\""
---

# Publish ASPX to SharePoint (plan)

Produce a `PublishPlan` for publishing rendered content as SharePoint modern pages. It does not upload or create any page.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. This skill only builds the plan.
- Never plan or attempt raw `.aspx` file upload: it is confirmed `Access denied`. The only working mechanism is the modern-page
  API (`Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage`).
- Refuse to build a plan from a missing source directory or one with no `.md` files.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_publish_plan import build_aspx_publish_plan
plan = build_aspx_publish_plan(document_id, source_dir, target_site_relative_path)
```

## Workflow

1. Collect `document_id`, the local rendered source directory and the target site-relative path.
2. Call `build_aspx_publish_plan`. The plan records source content and target page names, not an upload mechanism.
3. Hand the plan to the `sharepoint-upload-content` skill, whose executor creates the pages (dry run first).

## Verification

Confirm the plan lists every expected source file with its target page name, and that nothing was written to a tenant.

## References

- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for why `.aspx` upload is blocked, the
  executor that consumes this plan, and the corrections history.
