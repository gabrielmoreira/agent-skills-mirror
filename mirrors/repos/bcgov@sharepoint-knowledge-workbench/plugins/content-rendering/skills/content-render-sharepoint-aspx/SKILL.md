---
name: content-render-sharepoint-aspx
plugin: structured-content-rendering
description: Renders a validated structured content package into SharePoint modern-page-ready artifacts (an HTML fragment per chunk plus a page-manifest.json) for the confirmed-working Add-PnPPage/Add-PnPPageTextPart route. Does not upload to SharePoint, does not attempt raw .aspx file upload (confirmed Access denied), and does not extract source documents or determine topic boundaries.
allowed-tools: Bash, Read
examples:
  - "python -c \"from renderers.sharepoint_aspx import SharePointAspxRenderer; SharePointAspxRenderer().render(package, output_dir)\""
---

# Render SharePoint ASPX

## Trigger and Purpose

Use this skill to load an already-accepted structured content package
from disk (built and validated by `structured-content-assembly`) and
render it into artifacts staged for SharePoint's supported modern-page
creation API: one HTML fragment per chunk (suitable for a single
`Add-PnPPageTextPart` call), a `page-manifest.json` describing page
order/titles/media, and a local copy of the package's media.

This renderer never uploads anything to SharePoint and never produces a
raw `.aspx` file for direct upload — Phase 3.0's tenant experiment
confirmed raw `.aspx` upload to Site Pages is `Access denied` (a platform
boundary, not a permissions gap), while `Add-PnPPage` +
`Add-PnPPageTextPart` with generated HTML pushed and rendered correctly.
See `docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md`
§15 and `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1` for
the confirming evidence.

Uploading the rendered artifacts and calling the page-creation API is a
separate, later skill (`sharepoint-content-publication`'s
`publish-aspx-to-sharepoint`) — this skill performs zero SharePoint
tenant I/O.

## Public Interface

```python
from renderers.sharepoint_aspx import SharePointAspxRenderer, render_to_staging

renderer = SharePointAspxRenderer()
result = renderer.render(package, output_dir)
# RenderResult: {renderer_name: "sharepoint-aspx", ..., output_files: [...]}

# Or, to stage without promoting (mirrors render-multipage-markdown):
result, staging_dir = render_to_staging(package, output_root)
```

- `package` — an already-loaded `CanonicalPackage`
  (`structured-content-assembly`'s `build_canonical_package` output,
  loaded via `canonical_package.CanonicalPackage.load()`).
- `output_dir` — path under which the render is staged:
  ```
  rendered-output/
    page-manifest.json   # ordered list of {chunk_id, title, html_file, media_refs}
    pages/
      <chunk_id>.html      # one HTML fragment per chunk
    media/
      <asset files>         # copied from the package's media
  ```
- A `FAIL` (pandoc unavailable/errors) raises `PandocConversionError`
  rather than returning a partial render.

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

`pandoc` on `PATH` (already a repository-wide dependency — see
`DEPENDENCIES.md`), used to convert each chunk's canonical Markdown to
an HTML fragment. No other dependency beyond the Python standard
library.

