---
name: sharepoint-setup-sharepoint-migration-project
plugin: sharepoint-migration-planning
status: implemented
description: >
  Confirms the workbench's own repository-root config.psd1 (produced by
  workbench-setup's initialize-workbench-config) already exists with a
  Connection block, then creates a per-migration working directory to hold
  this pipeline's later-stage outputs. Pure filesystem + text check -- no
  tenant I/O, never fabricates a config.
allowed-tools: Bash, Read, Write
---

# Setup SharePoint Migration Project

Stage 1 of the `sharepoint-migration-planning` pipeline (see
`../../references/pipeline-overview.mmd`). Confirms -- does not recreate -- that
`workbench-setup`'s `initialize-workbench-config` skill has already produced a
repository-root `config.psd1`. This skill never generates its own competing
connection config; `config.psd1` has exactly one source of truth.

## Public interface

```python
from project_setup import setup_migration_project

result = setup_migration_project(
    repo_root,
    source_site_url="https://contoso.sharepoint.com/sites/old",
    target_site_url="https://contoso.sharepoint.com/sites/new",
    project_slug="acme-migration",
)
# result.outcome: Outcome.OBSERVED (paths created) or Outcome.FAILED
# (config.psd1 missing/no Connection block, or a required argument missing)
```

`check_config_psd1(repo_root)` and `project_paths(repo_root, project_slug)` are
also exposed individually for callers that only need one half.

## Working directory convention

`runs/sharepoint-migration-planning/<project-slug>/`, holding:

- `export/` -- the source-site export directory stage 2 validates
- `generated-scripts/` -- stage 3b's generated wave scripts
- `dependency-matrix.json` -- stage 3a's output (path only; this skill does not write it)
- `wave-guide.md` -- stage 3b's output (path only; this skill does not write it)

This mirrors this repo's existing `runs/<doc-name>/` convention for the
content-pipeline plugins (root `CLAUDE.md`'s "Layout" section), adapted for
migration-planning runs. Directory creation is idempotent.

## Honest outcomes

A missing `config.psd1`, a `config.psd1` with no `Connection` key, or a
missing required argument (`source_site_url`/`target_site_url`/`project_slug`)
is reported as `Outcome.FAILED` with an actionable message -- and no working
directory is created in that case. This skill performs no tenant I/O itself
and never writes or edits `config.psd1`.

## Scripts

- `scripts/project_setup.py` -- `check_config_psd1`, `project_paths`,
  `create_project_directories`, `setup_migration_project`
- `scripts/provisioning_outcomes.py` -- reused via a managed file symlink (see `symlinks.json`)

## Provenance

New design work, generalizing a manual process (source: a human hand-configuring
`config/config.psd1` before running wave scripts) observed in a separate
SharePoint migration repository. Not a code port.

