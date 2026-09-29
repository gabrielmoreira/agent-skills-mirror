---
name: sharepoint-migrate-sharepoint-list-content
plugin: sharepoint-content-migration
description: Migrates SharePoint list-item content in batches with retry, and resolves lookup-column values via a two-pass ID-mapping technique (record source-to-destination IDs during a content pass, resolve lookup fields against that mapping once all target lists exist). Gates any real write behind dry-run-by-default, an explicitly injected executor, and a plan-derived confirmation token.
allowed-tools: Bash, Read
examples:
  - "python -c \"from item_migration import plan_item_migration; print(plan_item_migration(items, batch_size=100).to_dict())\""
  - "python -c \"from id_mapping import record_id_mapping, resolve_lookup_ids; ...\""
---

# Migrate SharePoint List Content

## Trigger and Purpose

Use this skill to migrate list-item content into lists that already exist
with the correct schema (created by `sharepoint-provisioning`), including
lists with lookup columns whose targets are migrated in the same run.

## The two-pass sequencing rule — this is the skill's core contract, not a comment

Lookup columns cannot be populated in the same pass that creates the items
they target: a lookup field stores a reference to a specific destination
item ID, and that ID does not exist until the target item has already been
migrated.

1. **Content pass.** Migrate every list's non-lookup fields via
   `plan_item_migration` / `apply_item_migration`. As each item migrates,
   record its source ID → destination ID (and, for its own lookup fields,
   the raw source IDs they reference) via `record_id_mapping`.
2. **Backfill pass.** Once a target list's content pass is complete, use
   `resolve_lookup_ids` against the accumulated mapping to translate each
   recorded source ID into its destination ID, then write the resolved
   lookup values back.

**Sequencing order:** parent lists (lookup targets) must complete their
content pass before any list with a lookup pointing at them starts its
backfill pass. Self-referential lookups (a list whose lookup field points
at itself) must backfill last, after every other item in that same list
has already been migrated and has a destination ID.

**Unresolvable lookup values are quarantined, not dropped.** If
`resolve_lookup_ids` returns fewer IDs than were requested, the missing
source IDs had no mapping entry — report which ones, do not silently write
a shorter list and call it success.

## Write safety — same three-gate contract as every write-capable module here

1. **Dry-run is the default.** `apply_item_migration(plan)` with no further
   arguments changes nothing.
2. **An executor must be injected.** This module ships no tenant
   transport. Without an `executor(item) -> dest_id` callable, a real
   apply raises `ExecutorRequired`.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | Every item in the plan migrated successfully |
| `PARTIAL` | Some items migrated, some failed after exhausting retries; both lists populated |
| `FAILED` | Every item failed after exhausting retries |
| `EMPTY` | Nothing to migrate |

## Usage

```python
from item_migration import MigrationItem, plan_item_migration, apply_item_migration
from id_mapping import record_id_mapping, resolve_lookup_ids

# Pass 1: content
items = [MigrationItem(source_id=sid, fields=fields) for sid, fields in source_rows]
plan = plan_item_migration(items, batch_size=100)
result = apply_item_migration(plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token)

mapping = {}
for source_id, dest_id in result.migrated:
    mapping = record_id_mapping(mapping, list_name="TargetList", source_id=source_id, dest_id=dest_id)

# Pass 2: backfill (once every target list's content pass is done)
dest_ids = resolve_lookup_ids(mapping, target_list="TargetList", source_ids=[10322, 14647])
```

## Scripts

- `scripts/id_mapping.py` -- `record_id_mapping`, `resolve_lookup_ids`
- `scripts/item_migration.py` -- `MigrationItem`, `plan_item_migration`, `apply_item_migration`, `ExecutorRequired`, `ConfirmationRequired`
- `scripts/provisioning_outcomes.py` -- shared `Outcome` vocabulary (reused from `sharepoint-provisioning`)
- `scripts/spo-migrate-list-items.ps1` -- real PnP executor, see "Real executor" below
- `scripts/Get-WorkbenchConnectionConfig.ps1` -- symlink to the canonical
  `workbench-setup`-owned `config.psd1` reader shared by every write-capable
  plugin

## Real executor

`scripts/spo-migrate-list-items.ps1` is the real tenant-facing counterpart
to `apply_item_migration`'s injected `executor(item) -> dest_id` callable
-- Python cannot inject a PowerShell callback across the process boundary,
so this script instead reads a plan JSON file directly and performs the
real writes itself.

Per item, it chooses one of two real PnP cmdlets based on whether the plan
entry carries a `dest_id`:

- **No `dest_id` -> create.** Non-batched
  `Add-PnPListItem -List $TargetList -Values $fields -ErrorAction Stop`
  (not `-Batch` -- confirmed against a source-repository migration
  library's own comment: `Add-PnPListItem -Batch` does not reliably
  return a usable lazy item reference in the installed PnP.PowerShell
  version, so the source falls back to non-batched per-item creates
  whenever the real created ID is needed immediately, which this
  workflow always needs for `record_id_mapping`). The real created
  item's `Id` becomes the result's `dest_id`.
- **Present `dest_id` -> backfill (update).**
  `Set-PnPListItem -List $TargetList -Identity <dest_id> -Values $fields
  -ErrorAction Stop` -- pass 2, writing an already-resolved lookup value
  onto an item this same two-pass technique already created in an
  earlier content pass.

Retry: every item always gets at least one real write attempt --
`-RetryAttempts 0` is clamped to 1, never allowed to silently skip an
item (mirrors the fix already applied on the Python side, where
`apply_item_migration` now raises `ValueError` for `retry_attempts < 1`
instead of silently dropping every item).

Result JSON matches `ItemMigrationResult.to_dict()`'s field names exactly
(`outcome`, `dry_run`, `migrated: [{source_id, dest_id}]`,
`failed: [{source_id, error}]`) so a Python caller can feed
`result.migrated` straight into `record_id_mapping` without reshaping.

By default performs no tenant I/O; `-Execute` plus
`-ConfirmToken MIGRATE-SPO-LIST-ITEMS` runs the real writes.

### Design seam -- plan JSON is not a literal `MigrationItem`/`ItemMigrationPlan` serialization

Neither `MigrationItem` nor `ItemMigrationPlan` defines a `to_dict()`/
`from_dict()` method in `item_migration.py` (only `ItemMigrationResult`
does), and `MigrationItem` itself has no `dest_id`/"is this a backfill"
field -- it only carries `source_id` and `fields`. That means the two-pass
distinction this script's plan JSON needs (create vs. backfill) has no
native representation in the Python dataclass today. The plan JSON is
therefore this script's own contract: a caller producing it from Python
augments each item dict with `dest_id` itself when it's a backfill entry
(the same division of labor `spo-remediate-document-content-links.ps1`
uses for its own `remediated_content` augmentation). This was flagged
rather than silently assumed to already exist -- giving `MigrationItem` a
native optional `dest_id` field is real, undone follow-up work if a
caller wants the Python plan object itself to represent both passes
without a manual augmentation step.

## Provenance

Generalized from a source-repository content-migration library's
`Read-IdMappings` / `Write-IdMappingBatch` / `Resolve-LookupIdsFromMap`
functions and `Invoke-ListMigration`'s batched-migration-with-retry shape,
identified during the Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`). The source's field-
catalog-driven, matrix-driven, calendar-aware per-schema logic was
deliberately not ported — only the two reusable mechanisms were.

