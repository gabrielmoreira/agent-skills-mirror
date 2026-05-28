---
description: Bootstrap OPSX architecture map from existing codebase using structured five-phase workflow
---

Run the CLI-backed /opsx:bootstrap workflow to bootstrap the OPSX architecture map.

**Phases**: init → scan → map → review → promote

**Quick Start**
```bash
# Check current state
openspec bootstrap status

# Initialize (if no workspace)
openspec bootstrap init --mode full

# Or use refresh when formal OPSX already exists
openspec bootstrap init --mode refresh

# If a completed retained workspace already exists, start a fresh run explicitly
openspec bootstrap init --mode refresh --restart

# Get instructions for current phase
openspec bootstrap instructions

# Validate gates after each phase
openspec bootstrap validate

# Promote to formal OPSX (after review)
openspec bootstrap promote -y
```

Each phase produces intermediate artifacts in `openspec/bootstrap/`.
The workspace is retained after promote as audit history.
Use `openspec bootstrap init --mode refresh --restart` for the next run; it snapshots the retained workspace into `openspec/bootstrap-history/` before creating a fresh workspace.

**Key Commands**
- /opsx:bootstrap — user-facing agent command that drives the CLI-backed workflow
- `openspec bootstrap init [--mode full|opsx-first|refresh] [--scope src/] [--restart]` — create workspace or explicitly restart from a completed retained workspace
- `openspec bootstrap status [--json]` — phase progress + per-domain status
- `openspec bootstrap instructions [phase] [--json]` — phase-specific guidance
- `openspec bootstrap validate [--json]` — gate validation + auto-advance
- `openspec bootstrap promote [-y]` — re-validate, write formal OPSX, then retain the workspace as audit history
