---
name: sharepoint-extract-links
plugin: sharepoint-site-migration
description: Use when inventorying embedded links across local SharePoint pages and documents before or after migration. Python bulk CSV extraction supports static HTML/HTM/ASPX, DOCX/XLSX/PPTX external relationships and exported modern-page fields, preserving source URLs. Includes an Online stored-page-field collector; live reads are user-run. Does not rewrite, upload or silently claim coverage of unsupported formats.
allowed-tools: Bash, Read
examples:
  - "python scripts/export_link_inventory.py --manifest-csv downloads/downloads.csv --output-dir links"
  - "Inventory links across downloaded pages and Office documents, then compare after migration"
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_extraction import extract_links_from_text; print(extract_links_from_text(html, source='page.aspx').to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_extraction import extract_links_from_paths; print(extract_links_from_paths(['export/page1.aspx']).to_dict())\""
---

# Extract Links

Build a complete, classified inventory of the links inside SharePoint content. Stage one of
`sharepoint-extract-links` -> `sharepoint-update-page-links` -> `sharepoint-validate-link-integrity`.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Extraction is offline and never mutates sources. Python CSV export writes only local reports.
  `collect-sharepoint-page-content.ps1` is a separate Online live-read collector that the user runs.
- Never let an empty result pass silently. `EMPTY` (read fine, no links) and `FAILED` (nothing could be read) must stay distinct, and a
  partial read is `PARTIAL` with `problems` listed.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from link_extraction import extract_links_from_text
inv = extract_links_from_text(open("page.aspx").read(), source="page.aspx")
print(inv.outcome, len(inv.links))
```

## Workflow

For bulk CSV inventory, use `export_link_inventory.py --manifest-csv <downloads.csv>
--output-dir <folder>` or `--source-dir <local-tree> --base-url <original-directory-url>`.
It writes `links.csv`, `sources.csv` and `manifest.json`. Keep the manifest to preserve
source/subsite identity. Modern pages require stored-field exports, not only downloaded `.aspx`.
See [bulk content and link workflow](references/bulk-content-link-workflow.md).

1. Get exported content: a string per document, or local file paths.
2. Call `extract_links_from_text(content, source=...)` or `extract_links_from_paths(paths)`.
3. Report the `LinkInventory`: each `ExtractedLink` (`url`, `source`, `kind`) and the `outcome`.
4. Pass the inventory to `sharepoint-update-page-links` or `sharepoint-validate-link-integrity`.

The older text/path API records basenames and filters non-navigation URLs and platform artifacts
by default. Prefer the CSV exporter for multi-subsite work; it retains full source identity and
counts repeated link occurrences. The exporter does not change the existing API contract.

## Verification

Check `inv.outcome`. `OBSERVED` has links; anything else is reported honestly, with `problems`
for `PARTIAL`. The text API classifies asset references, masterpage assets, form actions, page
links and hyperlinks. For CSV runs, inspect sources.csv coverage and manifest status; unsupported
PDFs and failed reads make a run PARTIAL/FAILED and exit nonzero. Extraction is not link validation.

## References

- [Extraction details](references/extract-links-details.md): read for the API, link kinds, outcome semantics and provenance.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the shared outcome vocabulary.
