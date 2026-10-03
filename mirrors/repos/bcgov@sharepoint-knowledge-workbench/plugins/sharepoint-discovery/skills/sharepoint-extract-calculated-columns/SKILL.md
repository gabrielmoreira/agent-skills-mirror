---
name: sharepoint-extract-calculated-columns
plugin: sharepoint-discovery
description: Finds calculated-type fields across an exported SharePoint schema and reports each one's Formula and any [FieldName]-referenced field names, distinguishing "formula captured" from "formula not present in this export" rather than fabricating one. Use for migration planning, or for dependency analysis before renaming or removing a referenced field. Read-only; consumes an export, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from calculated_columns import find_calculated_columns; print(find_calculated_columns(export).columns)\""
---

# Extract Calculated Columns

Find which fields are calculated and which other fields their formulas depend on, by scanning an
exported schema's `fields.json` files for fields typed `Calculated`.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only by construction. Never connect to a tenant and never remove, rename or mutate a field. A
  test asserts the absence of any remediation or write capability.
- Never fabricate a formula. A calculated field without a `Formula` in the export is still reported,
  with `formula=None` and an entry in `ambiguities`.
- A missing export is `UNAVAILABLE`, never a clean pass.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_export import load_schema_export
from calculated_columns import find_calculated_columns
r = find_calculated_columns(load_schema_export('exports/baseline', label='baseline'))
for c in r.columns: print(c.list_key, c.internal_name, c.formula, c.referenced_fields)
print(r.ambiguities)"
```

## Workflow

1. Get an export directory; see [exports and outcomes](references/schema-export-sources-and-outcomes.md).
2. Load it with `load_schema_export` and call `find_calculated_columns`.
3. Report each column's list, internal name, formula and referenced fields, plus the `ambiguities`.

## Verification

Check the report status, and that every column reported without a formula has a matching entry in
`ambiguities`. `EMPTY` means no calculated fields were found, not that the export was unreadable.

## References

- [Exports and outcomes](references/schema-export-sources-and-outcomes.md): read for where exports
  come from and status meanings.
- [Calculated columns details](references/calculated-columns-details.md): read for formula presence,
  the script list and provenance.
