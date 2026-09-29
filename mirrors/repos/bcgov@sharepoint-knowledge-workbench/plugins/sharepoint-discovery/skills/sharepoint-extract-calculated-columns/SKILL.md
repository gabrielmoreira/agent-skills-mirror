---
name: sharepoint-extract-calculated-columns
plugin: sharepoint-schema
description: Finds calculated-type fields across an exported SharePoint schema and reports each one's Formula and any [FieldName]-referenced field names. Distinguishes "formula captured" from "formula not present in this export" rather than fabricating one. Read-only -- consumes an export, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from calculated_columns import find_calculated_columns; print(find_calculated_columns(export).columns)\""
---

# Extract Calculated Columns

## Trigger and Purpose

Use this skill when you need to know which fields on a site are calculated
(derive their value from a formula rather than direct input) and what other
fields those formulas depend on — for migration planning, dependency
analysis before renaming/removing a referenced field, or documenting a
site's schema. It scans an exported schema's `fields.json` files for fields
typed `Calculated` and reports each one's `Formula` and the field names
referenced inside it.

## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.

## Formula presence is not guaranteed by every export

Some SharePoint REST exports omit the `Formula` property for calculated
fields entirely. This skill never fabricates a formula to fill that gap: a
calculated field found without a `Formula` in the export is still reported
(so the field itself is not silently dropped), with `formula=None` and a
corresponding entry in `ambiguities` explaining the export did not carry it.
Only when a `Formula` string is present does the skill extract referenced
field names, using SharePoint's own `[FieldName]` bracket reference syntax.
A formula with no bracketed references (e.g. one that only calls built-in
functions like `TODAY()`) legitimately yields an empty reference tuple, not
an error.

## Honest outcomes

`SectionStatus` distinguishes the states a naive tool conflates:

| Status | Meaning |
|---|---|
| `OBSERVED` | Section read, content present |
| `EMPTY` | Read successfully, no calculated fields found |
| `PARTIAL` | Some lists unreadable; recorded, not hidden |
| `UNAVAILABLE` | Export missing entirely |

A missing export makes the report `UNAVAILABLE`, never a clean pass.

## Usage

```bash
python -c "
from schema_export import load_schema_export
from calculated_columns import find_calculated_columns
report = find_calculated_columns(load_schema_export('exports/baseline', label='baseline'))
for column in report.columns:
    print(column.list_key, column.internal_name, column.formula, column.referenced_fields)
print(report.ambiguities)
"
```

## Scripts

- `scripts/calculated_columns.py` -- `find_calculated_columns`, `CalculatedColumn`, `CalculatedColumnsReport`
- `scripts/schema_export.py` -- export loading and shared status vocabulary

## Read-only by construction

This module never connects to a tenant and never removes, renames, or
mutates a field. It only reads `fields.json` files an earlier, out-of-scope
collection step already exported. A test asserts the absence of any
remediation/write capability.

## Provenance

Generalized from `discover-calculated-columns.ps1` in a sibling SharePoint
migration repository, which scanned a hardcoded, project-specific export
path and left `Formula`/referenced fields as manual-fill placeholders
(noting the REST export it targeted did not capture formulas). This skill
generalizes the scan to any caller-supplied export root via
`ExportLayout`/`load_schema_export`, and — when an export's `fields.json`
does carry a `Formula` property — extracts referenced fields automatically
instead of leaving them for manual entry.

