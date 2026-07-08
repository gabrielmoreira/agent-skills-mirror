---
name: vibe-upgrade
description: Legacy update entry for existing Vibe-Skills installations.
---

This is a legacy compatibility entry owned by canonical `vibe`, the only governed runtime authority for this repository. Do not route it as a normal `vibe` task, do not launch specialist workflows, and do not write requirement or plan documents.

Use the simple installer update command for the skills directory that contains the installed `vibe` folder:

```bash
PYTHONPATH="$REPO_ROOT/apps/vgo-cli/src" python -m vgo_cli.main update --skills-dir "$SKILLS_DIR" --repo-root "$REPO_ROOT"
```

```powershell
$env:PYTHONPATH = Join-Path $repoRoot 'apps\vgo-cli\src'
py -3 -m vgo_cli.main update --skills-dir $skillsDir --repo-root $repoRoot
```

If the user did not provide a skills directory, ask for the directory that contains the installed `vibe` folder. The default is `~/.agents/skills`.

Request:
$ARGUMENTS
