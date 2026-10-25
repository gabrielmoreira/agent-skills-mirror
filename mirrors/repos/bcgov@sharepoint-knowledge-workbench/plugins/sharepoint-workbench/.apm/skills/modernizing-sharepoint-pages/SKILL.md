---
name: modernizing-sharepoint-pages
description: >
  Guides interactive modernization of exported classic SharePoint pages into
  reviewable modern-page plans and conversion artifacts. Use when asked to
  modernize page, convert classic page to modern, preview modernized page,
  fix page links, or decide webpart mapping.
---

# Modernizing SharePoint Pages

Use this wizard for exported page content and local conversion artifacts. It
does not silently read from or write to a tenant; live PowerShell commands are
shown for the user to run with their own connection and confirmation token.

## Wizard

1. **Intake scope**: identify the page/library, exported inputs, desired
   output, and whether the work is analysis-only or a gated conversion.
2. **Analyze web parts**: run `aspx_inventory.py` and
   `component_classification.py`; report `Unknown`, `Empty`, `Partial`, and
   `Unavailable` findings honestly.
3. **Mapping decision gate**: review `references/spo-webparts.json`,
   `references/webpart-mapping-guidance.json`, and
   `references/layout-translation.json`. Ask the human to accept, override,
   or defer each non-obvious mapping and every custom exception.
4. **Preview canvas**: select a layout, map components, and compose the
   self-contained preview before any tenant write.
5. **Rewrite links**: extract links, create explicit source-to-target rules,
   then apply page, document, or rich-text image remediation as appropriate.
6. **Validate and report**: validate page conversion and link integrity, then
   produce the modernization report with gaps and unresolved decisions.

## Mode contracts

Read the applicable instruction before running a mode. These preserve the
original flags, prompts, confirmation tokens, and parameter contracts:

- [ASPX to HTML](references/modes/aspx-to-html.md)
- [Convert modern](references/modes/convert-modern.md)
- [Convert library](references/modes/convert-library.md)
- [Page preview](references/modes/page-preview.md)
- [Extract links](references/modes/extract-links.md)
- [Update links](references/modes/update-links.md)
- [Update page links](references/modes/update-page-links.md)
- [Image-link rewrite](references/modes/image-link-rewrite.md)
- [Validate modernization](references/modes/validate-modernization.md)
- [Modernization report](references/modes/modernization-report.md)
- [Dynamic conversion rules](references/modes/dynamic-conversion-rules.md)
- [Dynamic webpart mapping](references/modes/dynamic-webpart-mapping.md)
- [Dynamic layout & columns](references/modes/dynamic-layout-columns.md)
- [Webpart content extraction](references/modes/webpart-content-extraction.md)
- [Single page orchestration](references/modes/single-page-orchestration.md)
- [Document migration orchestration](references/modes/document-migration-orchestration.md)
- [Static ASPX lessons](references/modes/static-aspx-lessons.md)
- [RTE sanitization](references/modes/rte-sanitization.md)

The supporting analysis and layout contracts are [web-part
analysis](references/modes/webpart-analysis.md) and [layout
mapping](references/modes/layout-mapping.md). All executable files under
`scripts/` are inlined regular files so this hub is independently installable.
