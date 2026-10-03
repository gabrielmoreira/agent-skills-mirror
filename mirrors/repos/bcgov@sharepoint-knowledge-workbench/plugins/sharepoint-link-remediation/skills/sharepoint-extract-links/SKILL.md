---
name: sharepoint-extract-links
plugin: sharepoint-link-remediation
description: Extracts and classifies every hyperlink from SharePoint page or document content (absolute, server-relative, protocol-relative, mailto, anchor, malformed) into a LinkInventory with an honest outcome (OBSERVED, EMPTY, PARTIAL, FAILED). Use first, to build a complete link inventory before deciding what needs rewriting. Read-only; reads content you pass it and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_extraction import extract_links_from_text; print(extract_links_from_text(html, source='page.aspx').to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_extraction import extract_links_from_paths; print(extract_links_from_paths(['export/page1.aspx']).to_dict())\""
---

# Extract Links

Build a complete, classified inventory of the links inside SharePoint content. Stage one of
`sharepoint-extract-links` -> `sharepoint-remediate-links` -> `sharepoint-validate-link-integrity`.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. No writes and no network access; read only content you are given or local paths you name. Export tenant content first.
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

1. Get exported content: a string per document, or local file paths.
2. Call `extract_links_from_text(content, source=...)` or `extract_links_from_paths(paths)`.
3. Report the `LinkInventory`: each `ExtractedLink` (`url`, `source`, `kind`) and the `outcome`.
4. Pass the inventory to `sharepoint-remediate-links` or `sharepoint-validate-link-integrity`.

## Verification

Check `inv.outcome`. `OBSERVED` has links; anything else is reported as what it is, with `problems` for `PARTIAL`. Kinds are `absolute`,
`server_relative`, `protocol_relative`, `mailto`, `anchor` and `malformed`.

## References

- [Extraction details](references/extract-links-details.md): read for the API, link kinds, outcome semantics and provenance.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the shared outcome vocabulary.
