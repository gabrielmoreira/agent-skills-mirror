# AGENTS.md — Megingjord baseline

> **Cross-team contract**: see `governance/README.md` for the canonical entry
> point (4 invariants: Team&Model signing, baton order, ticket-first, dedicated
> worktree). This file is the generic-AGENTS.md adapter.
>
> Governance detail: [`docs/agents-governance.md`](docs/agents-governance.md)
> Workflow and deploy detail: [`docs/agents-workflow.md`](docs/agents-workflow.md)

## Agent startup protocol (required)

1. Read `governance/README.md` — the 4 invariants are non-negotiable.
2. Load `.github/copilot-instructions.md` (Copilot) or `CLAUDE.md` (Claude Code)
   before planning any edits.
3. Global skills, instructions, hooks, and Codex assets in this repo are the
   **development source**. Never edit deployed runtimes directly.
4. Never edit `~/.copilot/`, `~/.codex/`, or `~/.agents/skills/` directly.
5. Run `npm run lint && npm test` before claiming completion on any change.
6. Check `/memories/repo/` and `/memories/session/` for prior context first.

## Repo purpose

Development workbench for the DevEnv Ops Harness:

- `skills/` → deploy to `~/.copilot/skills/` and `~/.agents/skills/`
- `instructions/` → deploy to `~/.copilot/instructions/`
- `hooks/` → deploy to `~/.copilot/hooks/` and `~/.codex/devenv-ops/hooks/`
- `scripts/global/` → deploy to `~/.copilot/scripts/` and `~/.codex/devenv-ops/scripts/`
- `.codex/` → develop Codex AGENTS.md, config, hooks, and rules here
- `agents/` → deploy to `~/.copilot/agents/`
- `dashboard/` → standalone web app; treat with full web-app engineering rigor
- `research/` → living docs; update when runtime behaviour changes

## Edit discipline

- Less than or equal to 100 lines per file (lint-enforced); split into linked
  files — never compress content. See `docs/howto/100-line-design-contract.md`.
- **Branch before editing**: create a feat/N-slug or fix/N-slug branch (one ticket per branch)
- **Ticket first**: open an issue before any file edits — governance rule number 1
- JSON for structured data; Markdown for prose
- Test before deploying: verify behaviour in the target runtime

## Concurrent session safety

- Never share one live checkout between Copilot, Claude Code, and Codex
- Give each agent its own worktree and branch; merge changes through PRs
- Quarantine conflicts in a rescue worktree; never clean collisions in place
- See `research/concurrent-agent-worktrees-2026-04-24.md`

## Quick reference

| Topic                                                   | File                                                                   |
| ------------------------------------------------------- | ---------------------------------------------------------------------- |
| Team&Model signing, role taxonomy, key contracts        | [`docs/agents-governance.md`](docs/agents-governance.md)               |
| Dev to deploy workflow, Layer-2, skill index, dashboard | [`docs/agents-workflow.md`](docs/agents-workflow.md)                   |
| Baton model (roles, artifacts, CI gates)                | [`docs/architecture-baton-model.md`](docs/architecture-baton-model.md) |
| Contributing guide                                      | [`CONTRIBUTING.md`](CONTRIBUTING.md)                                   |
