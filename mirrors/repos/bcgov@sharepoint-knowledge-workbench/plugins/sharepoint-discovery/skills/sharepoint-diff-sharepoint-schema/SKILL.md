---
name: sharepoint-diff-sharepoint-schema
plugin: sharepoint-schema
description: Compares schema DEFINITIONS (the declarative SiteSchemaDefinition shape) against each other, or a schema definition against a live SchemaExport ("what would change if this target definition were applied against this current state"). Read-only -- consumes local files/objects only, never contacts a tenant, never writes an apply plan.
allowed-tools: Bash, Read
examples:
  - "python -c \"from schema_definition import SiteSchemaDefinition; from schema_diff import compare_schema_definitions, render_markdown; print(render_markdown(compare_schema_definitions(SiteSchemaDefinition.load('baseline.json'), SiteSchemaDefinition.load('target.json'))))\""
  - "python -c \"from schema_export import load_schema_export; from schema_definition import SiteSchemaDefinition; from schema_diff import compare_definition_to_export, render_markdown; print(render_markdown(compare_definition_to_export(SiteSchemaDefinition.load('target.json'), load_schema_export('exports/current'))))\""
---

# Diff SharePoint Schema

## Trigger and Purpose

Use this skill to answer "what would change?" when the thing being compared
is a declarative schema **definition** (the `SiteSchemaDefinition` shape from
`generate-sharepoint-schema-from-export`), not a raw export. This is
distinct from `audit-schema`'s `compare_schema_exports`, which only compares
two loaded exports directly -- this skill adds two new comparison modes
built on top of the declarative shape:

1. **Definition vs. definition** -- `compare_schema_definitions(left, right,
   left_label=..., right_label=...)` compares two `SiteSchemaDefinition`
   objects (e.g. two hand-authored target definitions, or a definition
   captured at two points in time).
2. **Definition vs. export** -- `compare_definition_to_export(definition,
   export, definition_label=..., export_label=...)` compares a target
   `SiteSchemaDefinition` against a live `SchemaExport`, i.e. "what would
   change if I applied this target definition against this current state".
   Internally this converts the export to a definition via
   `generate_schema_definition` (already a pure, existing transform) and
   reuses `compare_schema_definitions` -- one place owns the declarative
   diff logic rather than two copies of the same named-set/per-list logic.

Both modes are pure, read-only comparisons over local files/objects already
loaded in memory. Neither mode contacts a tenant, and neither produces an
apply/write plan -- only a diff report, same as `audit-schema`.

## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.

## Honest outcomes -- a degraded input side is never a clean pass

Both new comparison modes reuse `SectionStatus` from `schema_export.py` and
propagate it exactly as `compare_schema_exports` already does: if either
side's `SiteSchemaDefinition.status` is `UNAVAILABLE`, the report's overall
`status` is `UNAVAILABLE` (never a clean pass); if either side is anything
short of `OBSERVED`, the report's status is `PARTIAL`. This applies whether
the degraded side is a hand-built definition or one converted from a
degraded export (`compare_definition_to_export` calls
`generate_schema_definition`, which already carries the export's honest
status through unchanged -- see `generate-sharepoint-schema-from-export`).

The same named-set semantics established for `compare_schema_exports` are
unchanged here: additions/removals/changes are reported per section,
duplicate keys are surfaced as an ambiguity rather than resolved by
guessing, items missing the comparison key are recorded rather than
skipped, a list present on only one side is reported rather than dropped,
and `render_markdown` output is deterministic (no timestamp or host
identifier).

## Usage

Definition vs. definition:

```bash
python -c "
from schema_definition import SiteSchemaDefinition
from schema_diff import compare_schema_definitions, render_markdown

left = SiteSchemaDefinition.load('baseline-schema.json')
right = SiteSchemaDefinition.load('target-schema.json')
report = compare_schema_definitions(left, right, left_label='baseline', right_label='target')
print(render_markdown(report))
"
```

Definition vs. export (target vs. current tenant state, already exported):

```bash
python -c "
from schema_export import load_schema_export
from schema_definition import SiteSchemaDefinition
from schema_diff import compare_definition_to_export, render_markdown

target = SiteSchemaDefinition.load('target-schema.json')
current = load_schema_export('exports/current', label='current')
report = compare_definition_to_export(target, current, definition_label='target')
print(render_markdown(report))
"
```

## Scripts

- `scripts/schema_diff.py` -- `compare_schema_definitions`, `compare_definition_to_export` (new in this skill), plus the pre-existing `compare_schema_exports`, `compare_named_sets`, `render_markdown`
- `scripts/schema_definition.py` -- `SiteSchemaDefinition`, `generate_schema_definition` (used internally by `compare_definition_to_export`)
- `scripts/schema_export.py` -- `load_schema_export`, `SectionStatus`, `SchemaExport`

## Provenance

New-build work for this repository, extending the existing `schema_diff.py`
module (originally built for `audit-schema`'s export-vs-export comparison)
with two new definition-aware comparison modes -- not extracted or adapted
from any prior source, and not a rewrite of the existing module's
export-vs-export behavior, which is unchanged.

