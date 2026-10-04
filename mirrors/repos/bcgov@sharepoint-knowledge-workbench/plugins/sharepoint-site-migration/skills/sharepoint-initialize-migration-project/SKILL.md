---
name: sharepoint-initialize-migration-project
plugin: sharepoint-site-migration
status: implemented
description: >
  Confirms the workbench's own repository-root config.psd1 (produced by sharepoint-workbench-setup's
  initialize-connection-config) already exists with a Connection block, then creates a per-migration
  working directory for this pipeline's later-stage outputs. Use as stage 1 before planning a
  migration. A pure filesystem and text check: no tenant I/O, and it never fabricates a config.
allowed-tools: Bash, Read, Write
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from project_setup import setup_migration_project; print(setup_migration_project('.', source_site_url='https://contoso.sharepoint.com/sites/old', target_site_url='https://contoso.sharepoint.com/sites/new', project_slug='acme-migration'))\""
---

# Setup SharePoint Migration Project

Stage 1 of the migration-planning pipeline. Confirm, never recreate, the repository-root `config.psd1`, then create the per-migration working directory.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- `config.psd1` has exactly one source of truth: produced by `sharepoint-workbench-setup`'s `initialize-connection-config`. Never generate a competing connection config and never write or edit `config.psd1`.
- A missing `config.psd1`, one with no `Connection` key, or a missing `source_site_url`, `target_site_url` or `project_slug` is `Outcome.FAILED` with an actionable message, and no
  directory is created.
- No tenant I/O. Directory creation is idempotent.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from project_setup import setup_migration_project
result = setup_migration_project(repo_root, source_site_url="...", target_site_url="...", project_slug="acme-migration")
print(result.outcome)
```

## Workflow

1. Confirm `sharepoint-workbench-setup` has produced `config.psd1`; if not, route to `workbench-initialize-connection-config` first.
2. Collect the source URL, target URL and a project slug.
3. Call `setup_migration_project`. It creates `runs/sharepoint-site-migration/<project-slug>/` with `export/` and `generated-scripts/`.
4. Report the outcome and the created paths.

## Verification

`result.outcome` is `OBSERVED` and the working directory exists with its subfolders. On `FAILED`, report the exact issue and create nothing.

## References

- [Setup details](references/migration-project-setup-details.md): read for the full interface, the directory layout and provenance.
- [Pipeline and outcomes](references/migration-pipeline-and-outcomes.md): read to see where this stage fits and the shared outcome vocabulary.
- [Pipeline diagram](references/pipeline-overview.mmd): read for the stage flow.
