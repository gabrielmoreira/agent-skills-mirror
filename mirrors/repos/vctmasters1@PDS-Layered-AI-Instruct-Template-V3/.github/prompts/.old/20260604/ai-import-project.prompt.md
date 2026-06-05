---
mode: agent
description: "[deprecated -> /ai-onboard] Import an existing project and adopt it to AI-INSTRUCT V5 standards. Two-phase: analyze compliance, then fix with interactive or auto modes."
---

# /ai-import-project (DEPRECATED)

> **Superseded by `/ai-onboard`** (which now detects existing projects and walks the import path automatically).
> See [.github/prompts/ai-onboard.prompt.md](ai-onboard.prompt.md).
> This file is commented out during verification and will be removed after sign-off.

<!-- DEPRECATED-CONTENT-BEGIN

Imports an existing project and transforms it to comply with AI-INSTRUCT V5 standards.

## Phases

### Phase 1: Analyze

Scans the project directory and identifies compliance violations:

- **Directory structure** — Missing `.ai/instruct.md`, module-level `README.md`
- **File naming** — Python files not snake_case, shell scripts not kebab-case
- **Security** — Credential files (`.env`, `.pem`, `.key`) not gitignored
- **Standards** — Missing documentation, unconventional patterns

```powershell
pwsh .github/debug/import-project.ps1 -Phase analyze -ProjectPath "C:\path\to\project"
```

Output: Human-readable report + JSON export (`.compliance-report.json`)

### Phase 2: Fix

Apply compliance fixes with two modes:

**Interactive** — Ask for each fix:
```powershell
pwsh .github/debug/import-project.ps1 -Phase fix -ProjectPath "C:\path\to\project" -Mode interactive
```

Output: For each finding, you choose:
- `y` — Apply this fix
- `n` — Skip
- `q` — Quit

**Automatic** — Apply all recommended fixes:
```powershell
pwsh .github/debug/import-project.ps1 -Phase fix -ProjectPath "C:\path\to\project" -Mode auto
```

## What it fixes

| Category | Action |
|---|---|
| **Naming** | Rename files to kebab-case (shell) / snake_case (Python) |
| **Structure** | Create missing `.ai/` directories, `README.md`, `.ai/instruct.md` |
| **Security** | Add credential files to `.gitignore` |
| **Documentation** | Generate module-level documentation stubs |

## Example workflow

```powershell
# 1. Analyze the project
pwsh .github/debug/import-project.ps1 -Phase analyze -ProjectPath "C:\MyProject"

# Review the report (human-readable on screen + .compliance-report.json)

# 2. Fix interactively
pwsh .github/debug/import-project.ps1 -Phase fix -ProjectPath "C:\MyProject" -Mode interactive

# Or auto-fix everything:
pwsh .github/debug/import-project.ps1 -Phase fix -ProjectPath "C:\MyProject" -Mode auto
```

## Output

After Phase 1:
- Screen report with findings grouped by severity (error, warning, info)
- `.compliance-report.json` in the project root (for programmatic processing)

After Phase 2:
- Renamed files (backed up originals)
- Created missing directories/files
- Updated `.gitignore`
- Summary of applied fixes

## Current Limitations

- Actual fix logic (Phase 2) is a **placeholder** — shows what would be done, doesn't apply yet
- Fix implementation will be added in next iteration
- Safe to run in "analyze-only" mode on any project

## Next Steps After Import

1. Run `/ai-validate` to check compliance
2. Update `.ai/instruct.md` files with project-specific rules
3. Commit the adoption changes

DEPRECATED-CONTENT-END -->
