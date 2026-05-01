# AGENTS.md — Megingjord baseline

## Agent startup protocol (required)

1. Load `.github/copilot-instructions.md` before planning edits.
2. Global skills, instructions, hooks, and Codex assets in this repo are the **development source**.
3. Never edit deployed runtimes directly: `~/.copilot/`, `~/.codex/`, or `~/.agents/skills/`.
4. Validate changes with lint and tests before claiming completion.

## Repo purpose

This repo is the **development workbench** for the DevEnv Ops Harness runtimes:
- `skills/` → develop here, deploy to `~/.copilot/skills/` and `~/.agents/skills/`
- `instructions/` → develop global instructions here, deploy to `~/.copilot/instructions/`
- `hooks/` → develop hook logic here, deploy to `~/.copilot/hooks/` and `~/.codex/devenv-ops/hooks/`
- `scripts/global/` → develop runtime scripts here, deploy to `~/.copilot/scripts/` and `~/.codex/devenv-ops/scripts/`
- `.codex/` → develop Codex `AGENTS.md`, config, hooks, and rules install assets here
- `agents/` → develop custom Copilot agents here, deploy to `~/.copilot/agents/`
- `dashboard/` is a standalone web app — treat with full web-app rigor.
- `research/` docs are living — update them when runtime behavior changes.

## Edit discipline

- Keep changes minimal and localized.
- ≤100 lines per file (lint-enforced).
- JSON for structured data (inventory/, config).
- Markdown for prose (research/, ADRs).
- **Branch before editing global resources**: `git checkout -b skill/<name>` or `feat/<topic>`
- **Test before deploying**: verify behavior in the target runtime.

## Concurrent session safety

- Never share one live checkout between Copilot, Claude Code, and Codex.
- Give each agent its own worktree + branch, then merge through PRs.
- Quarantine collisions in a rescue worktree instead of cleaning in place.
- See `research/concurrent-agent-worktrees-2026-04-24.md`.

## Team&Model signing

- AI-authored governed artifacts must include human alias + structured `Team&Model` provenance.
- Repo-local overrides may tighten the format, but must not remove provenance.
- See `instructions/team-model-signing.instructions.md`.

## Development → Deploy workflow

```
1. Branch:  git checkout -b skill/<name>-change
2. Edit:    skills/<name>/SKILL.md (or instructions/, hooks/, `.codex/`)
3. Test:    Verify behavior in the target runtime
4. Merge:   git checkout main && git merge --no-ff
5. Deploy:  run the affected runtime deploy command
```

## Dashboard conventions

- Alpine.js for state, vanilla JS for logic
- No build step — static files served directly
- Cloudflare Pages for production deployment
