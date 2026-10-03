---
name: sharepoint-generate-sharepoint-schema-from-export
plugin: sharepoint-discovery
description: Transforms an already-loaded SharePoint schema export (site columns, content types, lists with fields) into a declarative, JSON-serializable schema definition. Use when you need a definition suitable for later comparison or provisioning-input translation. A pure, read-only transform; consumes an export, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from schema_export import load_schema_export; from schema_definition import generate_schema_definition; d = generate_schema_definition(load_schema_export('exports/baseline'), label='baseline'); print(d.to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from schema_definition import SiteSchemaDefinition; SiteSchemaDefinition.load('baseline.json')\""
---

# Generate SharePoint Schema From Export

Turn one loaded schema export into a declarative `SiteSchemaDefinition` JSON describing what that
export contains.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Pure and read-only. Never contact a tenant, never provision or write anything, and do not compare two
  exports (that is `sharepoint-audit-schema`).
- A degraded export never produces a clean-looking definition. The definition carries the export's
  overall status unchanged, with only the `OBSERVED` sections populated. A list whose `fields.json`
  could not be read keeps an honest `fields_status` and empty `fields`.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_export import load_schema_export
from schema_definition import generate_schema_definition
d = generate_schema_definition(load_schema_export('exports/baseline', label='baseline'), label='baseline')
d.save('baseline-schema.json'); print(d.status)"
```

## Workflow

1. Get an export directory; see [exports and outcomes](references/schema-export-sources-and-outcomes.md).
2. Load it with `load_schema_export`, call `generate_schema_definition`, and `save` the result.
3. Report the definition's status and the counts of site columns, content types and lists.

## Verification

Check `definition.status` is `OBSERVED` before treating the definition as complete. Round-trip it with
`SiteSchemaDefinition.load` to confirm it parses.

## References

- [Exports and outcomes](references/schema-export-sources-and-outcomes.md): read for where exports come
  from and status meanings.
- [Definition generation](references/schema-definition-generation.md): read for degraded-export
  behavior, the round trip, scripts and provenance.
