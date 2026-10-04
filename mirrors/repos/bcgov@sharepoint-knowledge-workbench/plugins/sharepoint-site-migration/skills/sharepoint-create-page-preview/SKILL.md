---
name: sharepoint-create-page-preview
plugin: sharepoint-site-migration
description: Merges a site's structural chrome (navigation, header, logo, ancestors) with an already-extracted page's content (modern-preview.html plus metadata.json) into a single self-contained offline preview HTML file. Use so a reviewer can see a converted page in context. Disk-only; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/preview_composition.py --page-folder ./destination/My-Page --chrome-folder ./site-chrome/Example --output ./destination/My-Page/full-preview.html"
---

# Compose Page Preview

Show a converted page the way it would look with the site's own navigation, header, logo and breadcrumb trail in place.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Disk-only. Read the two folders given and write the one output file. No network calls and no tenant I/O.
- Never fabricate. A missing logo is not replaced by a placeholder image, and missing ancestors or navigation never invent breadcrumb or menu entries. Name every gap in the outcome.
- Required inputs: a page folder with `metadata.json` and `modern-preview.html`, and a chrome folder with `site-chrome.json`. A missing required file is `Unavailable` and nothing is written.
- Run from this skill's root. Standard library only.

## Quick start

```bash
python3 scripts/preview_composition.py --page-folder ./destination/My-Page --chrome-folder ./site-chrome/Example
```

If `--output` is omitted, the preview is written to `full-preview.html` inside the page folder.

## Workflow

1. Confirm both folders hold their required files (see the details reference for the exact shape).
2. Run `preview_composition.py`.
3. Report the outcome and any missing parts, and where the preview was written.

## Verification

`Observed` means full chrome and content were present. `Partial` names what chrome was missing (output still written); `Empty` (no page content) and `Unavailable` write nothing.

## References

- [Preview details](references/page-preview-composition-details.md): read for the input file shapes, the outcome table and provenance.
