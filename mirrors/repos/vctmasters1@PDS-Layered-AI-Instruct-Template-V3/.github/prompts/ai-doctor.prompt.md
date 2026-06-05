---
mode: agent
description: Read-only health check — runs all validators, verifies hook installation, surfaces Project Mode and surface-area inventory in one report.
---

# /ai-doctor

One-screen template health report. **Read-only.** Does not edit, install, or commit.

Use after cloning, after a major upgrade, or whenever something feels off.

## Steps

1. **Project Mode** — Read [.github/dev-specs.md](../dev-specs.md). Report the active Project Mode (Template Development vs Production / Adoption). If neither checkbox is marked, flag as a warning and suggest running `/ai-onboard`.

2. **Hook installation** — Run `git config --get core.hooksPath`.
   - Expected value: `.github/hooks`
   - If unset or different, report as a finding and suggest `pwsh .github/hooks/install-hooks.ps1` (or `bash .github/hooks/install-hooks.sh`).
   - List the hook scripts present in `.github/hooks/` (`pre-commit`, `commit-msg`).

3. **Validators** — Run all three; capture exit codes and a one-line summary each:
   - Instruction drift: `pwsh -NoProfile -File .github/scripts/validate-instructions.ps1`
   - Tool schema:      `python .ai/engine/validate_tools.py`
   - Engine tests:     `python -m pytest .ai/engine/tests -q`

4. **Surface-area inventory** — Count and list:
   - Slash commands: `Get-ChildItem .github/prompts -Filter *.prompt.md -File | Measure-Object`
   - Custom agents: `Get-ChildItem .github/agents -Filter *.agent.md -File | Measure-Object`
   - Skills: `Get-ChildItem .github/skills -Directory | Measure-Object`
   - Plugins: `Get-ChildItem .ai/plugins -Directory -ErrorAction SilentlyContinue | Measure-Object`

5. **Index freshness** — Check whether `.ai/index.md` is at least as recent as the newest `instruct.md` it indexes. (The validator in step 3 already covers this; surface it explicitly here.)

6. **Output format** — single fenced block, one line per check, prefixed with `[ok]` / `[warn]` / `[fail]`. End with a one-sentence overall verdict and (if anything failed) the highest-priority next action.

Example shape:

```
Project Mode    [ok]   Template Development
Hooks installed [ok]   core.hooksPath = .github/hooks (pre-commit, commit-msg)
Drift validator [ok]   55 files, 1 plugin
Tool schema     [ok]   23 files
Engine tests    [ok]   6 passed
Slash commands  [ok]   24
Agents          [ok]   21 (3 namespaces)
Skills          [ok]   1
Plugins         [ok]   1
Index freshness [ok]   .ai/index.md current

Verdict: healthy.
```

## Notes

- This prompt **must not** modify any file, install dependencies, or invoke `git`. If a tool is missing (e.g., `python`, `pytest`, `pwsh`), report it as a finding and recommend the install step rather than running it.
- Failures are reported, not auto-fixed. For each failure, point to the relevant slash command (`/ai-validate`, `/ai-update-index`, `/ai-onboard`).
