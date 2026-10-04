---
name: sharepoint-compare-schema-definitions
plugin: sharepoint-site-build-and-publish
description: Compares schema DEFINITIONS (the declarative SiteSchemaDefinition shape) against each other, or a schema definition against an exported SchemaExport, answering what would change if a target definition were applied against current state. Use after generating or hand-authoring a target definition. Read-only; consumes local files and objects only, never contacts a tenant, never writes an apply plan.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from schema_definition import SiteSchemaDefinition; from schema_diff import compare_schema_definitions, render_markdown; print(render_markdown(compare_schema_definitions(SiteSchemaDefinition.load('baseline.json'), SiteSchemaDefinition.load('target.json'))))\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from schema_export import load_schema_export; from schema_definition import SiteSchemaDefinition; from schema_diff import compare_definition_to_export, render_markdown; print(render_markdown(compare_definition_to_export(SiteSchemaDefinition.load('target.json'), load_schema_export('exports/current'))))\""
---

# Diff SharePoint Schema

Answer "what would change?" when the thing compared is a declarative `SiteSchemaDefinition`, not a
raw export.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. Pure comparisons over local files and objects already loaded; never contact a tenant
  and never produce an apply or write plan, only a diff report.
- A degraded input side is never a clean pass. If either side is `UNAVAILABLE`, the report is
  `UNAVAILABLE`; if either is short of `OBSERVED`, it is `PARTIAL`.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_definition import SiteSchemaDefinition
from schema_diff import compare_schema_definitions, render_markdown
l = SiteSchemaDefinition.load('baseline-schema.json'); r = SiteSchemaDefinition.load('target-schema.json')
print(render_markdown(compare_schema_definitions(l, r, left_label='baseline', right_label='target')))"
```

## Workflow

1. Pick the mode: `compare_schema_definitions` (definition vs. definition) or
   `compare_definition_to_export` (target definition vs. an exported current state).
2. For export input, get an export directory first; see
   [exports and outcomes](references/schema-export-sources-and-outcomes.md).
3. Run the comparison and render the markdown. Both modes are in
   [diff modes](references/schema-diff-modes.md).

## Verification

Check the report status is `OBSERVED` before calling the result clean. Output is deterministic, so
identical inputs should diff to nothing.

## References

- [Diff modes](references/schema-diff-modes.md): read for both modes with full examples, status
  propagation and the script list.
- [Exports and outcomes](references/schema-export-sources-and-outcomes.md): read for where exports
  come from and comparison semantics.
