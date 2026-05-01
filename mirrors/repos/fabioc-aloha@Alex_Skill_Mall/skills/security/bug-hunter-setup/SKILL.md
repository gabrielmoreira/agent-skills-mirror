---
type: skill
lifecycle: stable
inheritance: inheritable
name: setup
description: Scaffold .bug-hunter/ config directory in the current repo. Creates config.yaml with template values that you must edit before running live scans.
tier: standard
applyTo: '**/*bug*,**/*hunter*,**/*setup*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Bug Hunter Setup

Scaffold the `.bug-hunter/` configuration directory in the current repository.

## What to do

1. Run the setup script to create the config directory:

```bash
powershell "${PLUGIN_ROOT}/scripts/setup.ps1" -TargetPath .
```

On Unix/Mac:
```bash
bash "${PLUGIN_ROOT}/scripts/setup.sh" .
```

2. After setup completes, remind the user:

> ⚠️ **REQUIRED**: Review `.bug-hunter/config.yaml` with your ADO settings before running any scans. At minimum set:
> - `ado.organization` — your ADO org (e.g., "microsoft")
> - `ado.project` — your ADO project (e.g., "OSGS")
>
> If `es-metadata.yml` exists at the repo root, these values are auto-detected and pre-filled.
> Check `repo.is_production` — non-production repos skip ADO filing by default.

## Error Handling

- **Directory already exists**: If `.bug-hunter/` already exists, warn the user and ask if they want to overwrite. Do NOT silently overwrite existing `config.yaml` — it may contain customized settings.
- **Script not found**: If `setup.ps1`/`setup.sh` is missing from `${PLUGIN_ROOT}/scripts/`, the plugin may not be installed correctly. Suggest reinstalling the plugin.
- **Permission errors**: If the script cannot create directories or files, report the error. On Unix, suggest checking directory permissions.
- **Script execution policy** (Windows): If PowerShell blocks the script, suggest: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## Examples

**Successful setup:**
```
✅ Created .bug-hunter/config.yaml
✅ Created .bug-hunter/knowledge.json
✅ Created .bug-hunter/scan-history.json
✅ Created .bug-hunter/last-scan-output.json

⚠️ REQUIRED: Edit .bug-hunter/config.yaml with your ADO settings before scanning.
```

**Directory already exists:**
```
⚠️ .bug-hunter/ already exists. Overwrite config? (y/n)
```

## Safety Boundaries

- **ONLY** create files inside `.bug-hunter/` in the current repo. Do NOT modify any source code files.
- **NEVER** overwrite existing config without user confirmation.
- **NEVER** write to directories outside the current repository root.
