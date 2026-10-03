---
name: sharepoint-discover-sharepoint-site-inventory
plugin: sharepoint-migration-planning
status: implemented
description: >
  Validates and normalizes an already-produced source-site export directory (lists, fields, and critically
  lookup-column targets) into the raw object list that stage 3a needs. Use as stage 2 after exporting a source
  site. Live-tenant discovery itself is out of scope (design-only); this skill only validates an export a human
  already produced, and never invents lookup-target data that is not present.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from inventory_validation import validate_export_directory; print(validate_export_directory('export/').outcome)\""
---

# Discover SharePoint Site Inventory

Stage 2 of the migration-planning pipeline. Accept the raw site export that stage 3a analyzes: lists and, critically, lookup-column targets, which the dependency graph is built from.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Never fabricate a lookup target. A `Lookup` field with no `lookupList` is `FAILED`, not guessed.
- Never proceed on an incomplete export: a missing `site-inventory.json` is `UNAVAILABLE`; malformed JSON, a missing `lists` or `fields` array, or a duplicate list name is `FAILED` with the
  exact issue named. `EMPTY` only when `lists` is present and legitimately empty.
- Live-tenant discovery is out of scope (design-only, not authorized to build). No tenant I/O here.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from inventory_validation import validate_export_directory
result = validate_export_directory(export_dir)
print(result.outcome, result.issues)
```

## Workflow

1. Get an export directory containing `site-inventory.json` shaped `{"lists": [{"name", "fields": [{"name", "type", "lookupList"?}]}]}` (schema: `assets/site-inventory-export-schema.json`).
2. Call `validate_export_directory(export_dir)`.
3. Report the outcome and every issue. On `OBSERVED` or `EMPTY`, pass `result.matrix_objects` to the dependency-graph stage.

## Verification

`outcome` is `OBSERVED` with no `issues`. Any other outcome is reported as it is, with the exact problem; do not continue to stage 3a on a failed export.

## References

- [Validation details](references/site-inventory-validation-details.md): read for the blocked-vs-implemented split, the interface and the outcome rules.
- [Export schema](assets/site-inventory-export-schema.json): read when checking the export shape.
- [Pipeline and outcomes](references/migration-pipeline-and-outcomes.md): read for where this stage fits.
