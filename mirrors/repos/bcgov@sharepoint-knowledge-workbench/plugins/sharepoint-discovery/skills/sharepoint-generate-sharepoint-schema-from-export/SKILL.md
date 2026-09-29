---
name: sharepoint-generate-sharepoint-schema-from-export
plugin: sharepoint-schema
description: Transforms an already-loaded SharePoint schema export (site columns, content types, lists with fields) into a declarative, JSON-serializable schema definition. Pure, read-only transform -- consumes an export, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from schema_export import load_schema_export; from schema_definition import generate_schema_definition; d = generate_schema_definition(load_schema_export('exports/baseline'), label='baseline'); print(d.to_dict())\""
  - "python -c \"from schema_definition import SiteSchemaDefinition; SiteSchemaDefinition.load('baseline.json')\""
---

# Generate SharePoint Schema From Export

## Trigger and Purpose

Use this skill to turn an already-loaded schema export into a declarative
schema definition -- one JSON-serializable shape describing site columns,
content types, and lists (each with its own fields) -- suitable for later
comparison or, in a future and separate step, provisioning-input
translation. This skill does not compare two exports (see `audit-schema` for
that) and does not provision or write anything to a tenant; it only
transforms one export it is given into a declarative description of what
that export contains.

## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.

## Honest outcomes -- a degraded export never produces a clean-looking definition

`generate_schema_definition` reuses `schema_export.SectionStatus` rather than
inventing a second status vocabulary. The resulting `SiteSchemaDefinition`
carries the source export's overall `status` unchanged: an `UNAVAILABLE`,
`FORBIDDEN`, `FAILED`, or `PARTIAL` export produces a definition with that
same status and only the sections that were actually `OBSERVED` populated --
never a silently empty-but-`OBSERVED`-looking definition assembled from a
broken export. The same discipline applies per-list: a list whose own
`fields.json` could not be read cleanly keeps that list's `fields_status`
honest and its `fields` tuple empty, rather than guessing.

## Usage

```bash
python -c "
from schema_export import load_schema_export
from schema_definition import generate_schema_definition

export = load_schema_export('exports/baseline', label='baseline')
definition = generate_schema_definition(export, label='baseline')
definition.save('baseline-schema.json')
print(definition.status)
"
```

Round-trip a saved definition:

```bash
python -c "
from schema_definition import SiteSchemaDefinition
d = SiteSchemaDefinition.load('baseline-schema.json')
print(len(d.site_columns), len(d.content_types), len(d.lists))
"
```

## Scripts

- `scripts/schema_export.py` -- `load_schema_export`, `SectionStatus`, `SchemaExport` (input to this skill)
- `scripts/schema_definition.py` -- `generate_schema_definition`, `FieldDefinition`, `ContentTypeDefinition`, `ListDefinition`, `SiteSchemaDefinition`

## Provenance

New-build work for this repository, not extracted or adapted from any prior
source. No provenance record is needed in the Phase 9 provenance ledger.

