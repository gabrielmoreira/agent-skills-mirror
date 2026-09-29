---
name: sharepoint-extract-links
plugin: sharepoint-link-remediation
description: Extracts and classifies every hyperlink from SharePoint page or document content -- absolute, server-relative, protocol-relative, mailto, anchor, and malformed -- into a LinkInventory carrying an honest outcome (OBSERVED / EMPTY / PARTIAL / FAILED). Read-only; reads content you pass it and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from link_extraction import extract_links_from_text; print(extract_links_from_text(html, source='page.aspx').to_dict())\""
  - "python -c \"from link_extraction import extract_links_from_paths; print(extract_links_from_paths(['export/page1.aspx']).to_dict())\""
---

# Extract Links

## Trigger and Purpose

Use this skill to build a complete, classified inventory of the links
inside SharePoint content before deciding what needs rewriting. It is
the read-only first stage of the link-remediation pipeline:
`extract-links` -> `remediate-links` -> `validate-link-integrity`.

`extract_links_from_text(content, source=...)` parses one document's
content. `extract_links_from_paths(paths)` reads a set of local files
already exported from a tenant. Each returns a `LinkInventory` whose
`links` are `ExtractedLink` records (`url`, `source`, `kind`) and whose
`outcome` distinguishes states that are otherwise easy to conflate.

## Honest outcomes -- an empty result is never a silent pass

| Outcome | Meaning |
|---|---|
| `OBSERVED` | Links were found |
| `EMPTY` | Content read successfully, genuinely contained no links |
| `PARTIAL` | Some sources failed to read; `problems` lists them |
| `FAILED` | Every attempted source failed |

`EMPTY` and `FAILED` are deliberately distinct: "no links found" and
"nothing could be read" must never look alike (Phase 9 spec section 13).
When `extract_links_from_paths` is given `sources_attempted`, an
all-sources-failed run reports `FAILED`, not an empty success.

## Read-only guarantee

This skill performs no writes and opens no network connections. It reads
only content passed to it or local paths you name. Tenant retrieval is
deliberately out of scope -- export content first, then extract.

## Usage

```bash
python -c "
from link_extraction import extract_links_from_text
inv = extract_links_from_text(open('page.aspx').read(), source='page.aspx')
print(inv.outcome, len(inv.links))
"
```

Link kinds are reported by `classify(url)`: `absolute`, `server_relative`,
`protocol_relative`, `mailto`, `anchor`, `malformed`.

## Scripts

- `scripts/link_extraction.py` -- `extract_links_from_text`, `extract_links_from_paths`, `classify`, `ExtractedLink`, `LinkInventory`
- `scripts/link_outcomes.py` -- the shared `Outcome` vocabulary

## Provenance

Adapted from `sp-extracting-links` in the originating SharePoint migration
repository (see `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).
Ported to Python and stripped of all project-specific literals; the plugin
carries no dependency on that repository.

