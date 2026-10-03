---
name: content-render-sharepoint-aspx
plugin: content-rendering
description: Renders an accepted structured content package into SharePoint modern-page-ready artifacts (an HTML fragment per chunk plus a page-manifest.json) for the confirmed Add-PnPPage and Add-PnPPageTextPart route. Use when preparing content for SharePoint publication. Does not upload to SharePoint, does not attempt raw .aspx upload (confirmed Access denied), and does not extract source documents or determine topic boundaries.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from renderers.sharepoint_aspx import SharePointAspxRenderer; SharePointAspxRenderer().render(package, output_dir)\""
---

# Render SharePoint ASPX

Render an accepted structured content package into HTML fragments and a page manifest staged for
SharePoint's modern-page API.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero SharePoint tenant I/O. Never upload, and never produce a raw `.aspx` file for direct upload:
  that is a confirmed `Access denied` platform boundary. Uploading belongs to
  `sharepoint-publish-aspx-to-sharepoint`.
- Consume only an already-loaded `CanonicalPackage` from an accepted package.
- A pandoc failure raises `PandocConversionError`; never return a partial render.
- `pandoc` must be on `PATH`. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from renderers.sharepoint_aspx import SharePointAspxRenderer, render_to_staging
result = SharePointAspxRenderer().render(package, output_dir)
```

## Workflow

1. Load the accepted package with `canonical_package.CanonicalPackage.load()`.
2. Render with `SharePointAspxRenderer().render(package, output_dir)`, or stage without promoting with
   `render_to_staging(package, output_root)`.
3. Report the `RenderResult` and the `rendered-output/` layout: `page-manifest.json`, `pages/<chunk_id>.html`
   and `media/`. Validate and promote with `content-validate-rendered-output`.

## Verification

Confirm `page-manifest.json` lists every chunk in order and each referenced HTML fragment exists. Run the
validation skill before treating the render as accepted.

## References

- [ASPX rendering details](references/render-aspx-details.md): read for why fragments and not `.aspx`
  files, the full interface, the output layout and failure behavior.
- [Rendered output profile](references/contracts/rendered-output-profile.md): read when checking the
  profile contract.
