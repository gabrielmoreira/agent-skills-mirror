---
name: sharepoint-discover-sharepoint-site-inventory
plugin: sharepoint-migration-planning
status: implemented
description: >
  Validates and normalizes an already-produced source-site export directory
  (lists, fields, and critically lookup-column targets) into the raw object
  list stage 3a needs. Live-tenant discovery itself remains out of scope
  (sharepoint-collection, Part A, is design-only and not authorized to
  build) -- this skill only validates/normalizes an export a human already
  produced. Never invents lookup-target data that is not present.
allowed-tools: Bash, Read
---

# Discover SharePoint Site Inventory

Stage 2 of the `sharepoint-migration-planning` pipeline. Accepts the raw site
export that stage 3a analyzes: lists and, critically, **lookup-column
targets** (which list a lookup field points at) -- the relationship the
dependency graph is built from.

## Blocked half vs. implemented half

- **Real live-tenant discovery**: connecting to the source site and pulling
  this inventory directly is `sharepoint-collection`'s (Part A's) job --
  design-only, `REQUIRES_HUMAN_DECISION`, not authorized to build. See
  `docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md`.
- **Implemented**: accepting an export directory a human already produced
  (by hand, or with an existing script run outside this workbench), and
  validating/normalizing its shape for stage 3a.

## Public interface

```python
from inventory_validation import validate_export_directory

result = validate_export_directory(export_dir)
# result.outcome: Outcome.OBSERVED | Outcome.EMPTY | Outcome.UNAVAILABLE | Outcome.FAILED
# result.issues: exact problems found (missing file, malformed JSON, missing
#                fields, a Lookup field with no lookupList target, duplicate
#                list names) -- never a bare boolean
# result.matrix_objects: only populated on OBSERVED/EMPTY -- ready to pass
#                         directly to dependency_graph.load_matrix_objects
```

## Expected export shape

A single `site-inventory.json` file inside the export directory:
`{"lists": [{"name": ..., "fields": [{"name": ..., "type": ..., "lookupList": "..."}]}]}`
(`lookupList` required only on `type: "Lookup"` fields). See
`../../assets/site-inventory-export-schema.json` for the full JSON Schema.

## Honest outcomes

A missing `site-inventory.json` is `Outcome.UNAVAILABLE`. Malformed JSON, a
missing `lists`/`fields` array, a duplicate list name, or a `Lookup` field with
no `lookupList` target is `Outcome.FAILED` with the exact issue named --
this skill never silently proceeds on an incomplete export and never
fabricates a lookup target that is not present in the file. `Outcome.EMPTY`
is returned only when `lists` is present and legitimately empty.

## Scripts

- `scripts/inventory_validation.py` -- `validate_export_directory`, `InventoryValidationResult`
- `scripts/provisioning_outcomes.py` -- reused via a managed file symlink (see `symlinks.json`)

## Provenance

New design work. The source repository's equivalent
(`export-sharepoint-inventory-custom.ps1`) is a live-tenant collector out of
scope for this workbench's zero-tenant-I/O plugins -- not ported.

