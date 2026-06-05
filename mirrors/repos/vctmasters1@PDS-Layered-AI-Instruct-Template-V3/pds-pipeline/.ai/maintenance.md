# Maintenance — archive, update, and safety for pds-pipeline

**Scope**: Authoritative for pds-pipeline/ directory
**Last Updated**: 2026-05-27

> This file extends the root .ai/maintenance.md with pds-pipeline-specific patterns.

> **→ [Master Maintenance Guide](../.ai/maintenance.md)** — project-wide archive and safety rules.

---

## Never Delete Rule

> **Archive instead of delete** — move files to .archive/ or use version control for history.

---

## Archive Pattern

| Old File/Directory | New Location |
|-------------------|--------------|

# Archive pattern: .archive/old-name/

# Or use date-stamped subdirectory: .archive/20250101-old-feature/

# Never delete files from version control history

---

## Never Reset Database

> **→ [Never Reset Database](../.ai/maintenance.md#never-reset-database)** — use migrations to evolve schema safely.

---

## Updating pds-pipeline

When updating pds-pipeline:

1. Update src/block-registry.ts with new block definitions

2. Mirror changes in pds-role/tools/blob_packer.py

3. Mirror struct changes in firmware headers (.h) and implementations (.c)

4. Rebuild the package: npm run build

5. Update consumer modules to use the new package version

6. Update Last Updated date in this .ai/instruct.md file

---

## .dev-docs Maintenance

When updating pds-pipeline documentation:

1. Keep primary docs at root: README.md, CHANGELOG.md

2. Dev notes go in .dev-docs/ with index.md navigation

3. Move stale docs to .dev-docs/.old/ instead of deleting

4. AI should ignore .dev-docs/.old/ contents unless explicitly asked
