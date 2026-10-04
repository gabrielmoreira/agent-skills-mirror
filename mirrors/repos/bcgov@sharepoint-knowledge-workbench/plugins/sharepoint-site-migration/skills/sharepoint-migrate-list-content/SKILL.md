---
name: sharepoint-migrate-list-content
plugin: sharepoint-site-migration
description: Migrates SharePoint list-item content in batches with retry, and resolves lookup-column values with a two-pass ID-mapping technique (record source-to-destination IDs during a content pass, resolve lookup fields against that mapping once all target lists exist). Use to migrate item content into lists already provisioned with the right schema. Gates any real write behind dry-run-by-default, an explicitly injected executor, and a plan-derived confirmation token.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from item_migration import plan_item_migration, apply_item_migration; print(apply_item_migration(plan_item_migration(items, batch_size=100)).to_dict())\""
  - "pwsh -File scripts/spo-migrate-list-items.ps1 -PlanPath plan.json"
---

# Migrate SharePoint List Content

Migrate list-item content into lists that already exist with the correct schema (created by `sharepoint-site-build-and-publish`),
including lists whose lookup targets are migrated in the same run.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Two passes, always. A lookup cannot be written until its target item exists, so migrate non-lookup content first,
  record source-to-destination IDs, then backfill lookups. Parent (target) lists finish their content pass before any
  list that points at them backfills; self-referential lookups backfill last.
- Quarantine, never drop. If `resolve_lookup_ids` returns fewer IDs than requested, report the unmapped source IDs;
  do not write a shorter list and call it success.
- Three write gates: dry-run is the default, an executor must be injected (`ExecutorRequired` otherwise), and a real
  apply needs `confirm=plan.confirmation_token` (`ConfirmationRequired` otherwise). The PowerShell executor needs
  `-Execute -ConfirmToken MIGRATE-SPO-LIST-ITEMS`. A real run is a live tenant write that the user runs.
- Run from this skill's root with `scripts/` on `sys.path`. Target lists and their schema must already exist.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from item_migration import MigrationItem, plan_item_migration, apply_item_migration
plan = plan_item_migration([MigrationItem(source_id=1, fields={"Title": "A"})], batch_size=100)
print(apply_item_migration(plan).to_dict())  # dry run by default: dry_run True, migrated empty
```

## Workflow

1. Plan the content pass with `plan_item_migration` and review it as a dry run.
2. Apply it only when the user confirms: `apply_item_migration(plan, executor=..., dry_run=False,
   confirm=plan.confirmation_token)`, or the PowerShell executor with its plan JSON.
3. Record each `(source_id, dest_id)` with `record_id_mapping`.
4. When every target list's content pass is done, resolve lookups with `resolve_lookup_ids` and write them back.

## Verification

Check the outcome: `OBSERVED` (all migrated), `PARTIAL`, `FAILED` or `EMPTY`. A dry run reports `dry_run: true` with
nothing migrated, so do not read its outcome as a completed migration. Treat `PARTIAL` and `FAILED` as incomplete,
and list any unresolved lookup source IDs.

## References

- [API and sequencing](references/list-content-migration-api.md): read before planning or applying a migration, for
  the outcome table, usage, and the sequencing rule in full.
- [Real executor](references/list-content-migration-executor.md): read before using
  `spo-migrate-list-items.ps1`, or when asked about the plan JSON shape and create-vs-backfill.
