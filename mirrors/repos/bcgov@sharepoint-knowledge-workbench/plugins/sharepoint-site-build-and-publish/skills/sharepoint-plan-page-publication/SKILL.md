---
name: sharepoint-plan-page-publication
plugin: sharepoint-site-build-and-publish
description: Builds a human-actionable publish plan (a PublishPlan) for rendered content as SharePoint modern pages. Use after rendering, before uploading. Performs no tenant writes and never attempts raw .aspx upload (blocked); execution belongs to sharepoint-apply-page-publication-plan.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_publish_plan import build_page_publish_plan_from_render; print(build_page_publish_plan_from_render('doc-1', 'rendered-output/', 'SitePages/MyDoc').to_dict())\""
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
- The input is the `content-render-sharepoint-pages` output directory: `page-manifest.json` (schema 1.0) plus the HTML fragments it lists.
  Refuse a missing directory, a missing or unsupported manifest, an empty page list, duplicate page identities, paths outside the
  directory, missing or unlisted fragments. Markdown renderer output is not page content: publish it with
  `sharepoint-publish-markdown-files` instead.
- Page order is the manifest order; each page's identity is its `chunk_id` (`<chunk_id>.aspx`). Media a fragment references is
  recorded per action (`media_refs`) but not uploaded or rewritten by this skill or by the executor: do that before publishing.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_publish_plan import build_page_publish_plan_from_render
plan = build_page_publish_plan_from_render(document_id, rendered_dir, target_site_relative_path)
```

## Workflow

1. Collect `document_id`, the rendered output directory (the one holding `page-manifest.json`) and the target site-relative path.
2. Call `build_page_publish_plan_from_render`. The plan records the HTML fragment for each page and its target page name, not an upload mechanism, and is tagged `source_format: html-fragment`.
3. Hand the plan to the `sharepoint-apply-page-publication-plan` skill, whose executor creates the pages (dry run first).

## Verification

Confirm the plan lists every page in the manifest, in manifest order, with its HTML fragment and target page name, and that nothing was written to a tenant. The older `build_aspx_publish_plan` (Markdown files to page names) is kept for compatibility, is tagged `source_format: markdown`, and is refused by the HTML executor.

## References

- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for why `.aspx` upload is blocked, the
  executor that consumes this plan, and the corrections history.
