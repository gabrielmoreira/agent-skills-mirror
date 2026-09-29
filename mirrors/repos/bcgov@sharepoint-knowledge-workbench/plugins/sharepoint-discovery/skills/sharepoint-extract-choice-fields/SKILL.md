---
name: sharepoint-extract-choice-fields
plugin: sharepoint-schema
description: Inventories Choice and MultiChoice fields from an exported SharePoint schema and renders them as a list/internal-name keyed overrides mapping. Distinguishes "no options defined" from "options unknown". Read-only, group filter is opt-in with no default.
allowed-tools: Bash, Read
examples:
  - "python -c \"from choice_fields import inventory_choice_fields, to_overrides_mapping; print(to_overrides_mapping(inventory_choice_fields(export)))\""
---

# Extract Choice Fields

## Trigger and Purpose

Use this skill when you need the actual option sets behind a site's Choice
columns — for migration mapping, for validation rules, or to seed a
provisioning template. It inventories `Choice` and `MultiChoice` fields across
an exported schema and can emit them as an overrides mapping keyed by list and
internal field name.

## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.

## Unknown is not empty

The distinction this skill exists to preserve:

- A field with an **empty** choice list has genuinely no options defined.
- A field with **no `Choices` property at all** is `UNKNOWN` — the export
  simply did not carry the information.

These are reported differently and never conflated. `to_overrides_mapping`
**omits unknown option sets** rather than emitting an empty list for them,
so a downstream consumer cannot mistake "we don't know" for "there are none".

Both the plain array form and the OData `{"results": [...]}` envelope are
supported, since SharePoint exports vary.

## Group filter is opt-in

Filtering by field group is an explicit caller parameter with **no default** —
nothing is silently excluded from your inventory.

## Honest outcomes

A missing export is `UNAVAILABLE`, never an empty success. An export
containing no choice fields at all is `EMPTY`.

## Usage

```bash
python -c "
from schema_export import load_schema_export
from choice_fields import inventory_choice_fields, to_overrides_mapping
inv = inventory_choice_fields(load_schema_export('exports/baseline'))
print(inv.status)
print(to_overrides_mapping(inv))
"
```

## Scripts

- `scripts/choice_fields.py` -- `inventory_choice_fields`, `to_overrides_mapping`, `ChoiceField`, `ChoiceFieldInventory`
- `scripts/schema_export.py` -- export loading and shared status vocabulary

## Provenance

Adapted from `sp-extracting-choices` in the originating SharePoint migration
repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

