---
mode: agent
description: Print the active DEPLOY_MODE, list available deployment modes, and optionally switch by writing a shell-export snippet. Always points to the authoritative .deployment/<mode>/.ai/instruct.md for the active mode.
---

# /ai-deploy-mode

Inspect or switch the active deployment-mode scope.

This command does **not** start, stop, or deploy anything. It only:

1. Reads `$DEPLOY_MODE` (POSIX) or `$env:DEPLOY_MODE` (PowerShell) from the current shell where Copilot runs.
2. Lists every directory under [`.deployment/`](../../.deployment/) and reports each mode's one-line summary (the first table row of its `.ai/instruct.md`).
3. Reports the path to the **authoritative** `.deployment/<active-mode>/.ai/instruct.md` so the user can open it.
4. If the user asks to switch, prints a shell-export snippet for both PowerShell and POSIX — the user runs it themselves; the AI never silently mutates the shell.

## Steps

1. **Detect platform** from [`.github/dev-specs.md`](../dev-specs.md). Use the matching `echo $DEPLOY_MODE` form.
2. **Inventory modes**: `list_dir .deployment/`. For each subdirectory, read its `.ai/instruct.md` and extract the **Mode Overview** row (Use case + Setup time).
3. **Compare** to the active `DEPLOY_MODE` value:
   - If unset: report "no mode active — defaults are workspace-root rules".
   - If set but the matching subdirectory is missing: report drift and propose either creating the mode (delegate to [`deployment-manager`](../agents/pds-man-deployment.agent.md)) or unsetting the variable.
   - If set and present: report the mode and the absolute path to its `.ai/instruct.md`.
4. **If the user requested a switch**:
   - Confirm the target mode exists. If not, propose `deployment-manager` add-flow; do not invent a mode.
   - Print the snippet:

     ```powershell
     # PowerShell
     $env:DEPLOY_MODE = "<target>"
     ```

     ```bash
     # POSIX
     export DEPLOY_MODE=<target>
     ```

   - Remind the user to restart any long-running services so they pick up the new value.
5. **Report**:

   ```
   Deploy Mode
     active:    <mode | none>
     modes:     <list with one-line descriptions>
     authority: <absolute path to active mode .ai/instruct.md, or "none">
   ```

## Hard rules

- Never call `docker compose`, `railway`, `kubectl`, `caddy`, or any deployment binary.
- Never write to `.env`.
- Never invent a mode that does not exist as a directory under `.deployment/`. To add a mode, delegate to [`deployment-manager`](../agents/pds-man-deployment.agent.md), which consults [`naming`](../agents/pds-man-naming.agent.md) Mode 3.
- Mode names are case-sensitive (kebab-case per [`.ai/conventions.md`](../../.ai/conventions.md)).
