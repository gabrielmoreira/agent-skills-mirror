---
name: sharepoint-extract-choice-columns
plugin: sharepoint-site-assessment
description: Inventories Choice and MultiChoice fields from an exported SharePoint schema and renders them as a list and internal-name keyed overrides mapping, distinguishing "no options defined" from "options unknown". Use when you need the real option sets behind a site's Choice columns for migration mapping, validation rules or seeding a provisioning template. Read-only; the group filter is opt-in with no default.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from choice_fields import inventory_choice_fields, to_overrides_mapping; print(to_overrides_mapping(inventory_choice_fields(export)))\""
---

# Extract Choice Fields

Inventory `Choice` and `MultiChoice` fields across an exported schema and emit them as an overrides
mapping keyed by list and internal field name.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Unknown is not empty. An empty choice list means no options are defined; a field with no `Choices`
  property is `UNKNOWN`. `to_overrides_mapping` omits unknown option sets rather than emitting an
  empty list for them.
- The group filter is an explicit caller parameter with no default. Exclude nothing silently.
- A missing export is `UNAVAILABLE`, never an empty success. An export with no choice fields is `EMPTY`.
- Read-only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_export import load_schema_export
from choice_fields import inventory_choice_fields, to_overrides_mapping
inv = inventory_choice_fields(load_schema_export('exports/baseline'))
print(inv.status); print(to_overrides_mapping(inv))"
```

## Workflow

1. Get an export directory; see [exports and outcomes](references/schema-export-sources-and-outcomes.md).
2. Load it and call `inventory_choice_fields`, adding a group filter only if the user asks.
3. Call `to_overrides_mapping` for the overrides mapping and report which fields were `UNKNOWN`.

## Verification

Check `inv.status`, and that every field missing a `Choices` property is reported as unknown rather
than empty. Both the plain array and the OData `{"results": [...]}` forms are accepted.

## References

- [Exports and outcomes](references/schema-export-sources-and-outcomes.md): read for where exports
  come from and status meanings.
- [Choice fields details](references/choice-fields-details.md): read for unknown-vs-empty, the group
  filter, scripts and provenance.
