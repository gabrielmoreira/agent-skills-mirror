---
name: migrating-sharepoint-sites
description: >
  Guides interactive sequencing of SharePoint site migrations from inventory
  through dependency-safe wave execution. Use when asked to migrate list
  content, plan migration waves, audit migration, perform dependency analysis,
  or validate link integrity.
---

# Migrating SharePoint Sites

Use this wizard for exported inventories and caller-supplied migration
matrices. Planning is deterministic and local; tenant-facing writes remain
dry-run by default and require the mode's explicit execution token.

## Wizard

1. **Discover dependencies**: initialize the project, normalize the source
   inventory, and identify lookup, content, page, and link dependencies.
2. **Check matrix completeness**: compare source coverage, orphan entries,
   unresolved targets, and destination-name collisions before ordering work.
3. **Topologically sort**: compute dependency-safe waves from names, never
   hand-assigned stage numbers; stop on cycles or unresolved dependencies.
4. **Execute the ledger**: scaffold discrete wave scripts, run one wave at a
   time, record validation results, and require human confirmation before the
   next wave.

## Mode contracts

Read the applicable instruction before running a mode. These preserve the
original flags, prompts, and parameter contracts:

- [Initialize project](references/modes/init-project.md)
- [Normalize inventory](references/modes/normalize-inventory.md)
- [Dependency analysis](references/modes/dependency-analysis.md)
- [Wave plan](references/modes/wave-plan.md)
- [Scaffold wave scripts](references/modes/scaffold-wave-scripts.md)
- [Migrate list content](references/modes/migrate-list-content.md)
- [Audit migration](references/modes/audit-migration.md)
- [Validate link integrity](references/modes/validate-link-integrity.md)
- [Plan page modernization](references/modes/plan-page-modernization.md)
- [Wave migration orchestration](references/modes/wave-migration-orchestration.md)
- [Library upload orchestration & ledger](references/modes/library-upload-orchestration.md)
- [Reconciliation contract](references/modes/reconciliation-contract.md)

The complete migration planning, content migration, link remediation, and
page-planning implementations are inlined as regular files under `scripts/`;
this hub has no symlink or dependency on another installed skill.
