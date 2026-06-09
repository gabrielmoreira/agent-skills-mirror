# Copilot Instructions — devenv-ops

**devenv-ops**: Development workbench for the DevEnv Ops Harness runtime assets deployed to `~/.copilot/`, `~/.codex/`, and `~/.agents/skills/`.

> **Cross-team contract**: see `governance/README.md` for the canonical entry point (4 invariants: Team&Model signing, baton order, ticket-first, dedicated worktree). This file is the Copilot adapter; the generic baseline lives in `AGENTS.md`.

## Execution Model

Every task follows the **role baton sequence**: Manager → Collaborator → Admin → Consultant.
See `role-baton-routing` for rules. Local repos may override via `.github/copilot-instructions.md`.
Shared governance is provider-neutral; runtime-specific setup belongs in adapters.
See `instructions/provider-neutral-governance.instructions.md`.
Completion intent is strict: when the active role identifies complete/finish/ship terminal-delivery intent in task scope, execute full baton delivery through Admin and Consultant gates; do not stop at implementation unless blocked by evidence or explicit design/UAT input.

## Repo Purpose

This repo is the **source of truth** for the DevEnv Ops Harness:

1. **skills/** → source skills for Copilot runtime and Codex user skill layer
2. **instructions/** → global markdown instructions for the harness
3. **hooks/** → shared hook logic and governance policies
4. **scripts/global/** → bootstrap, routing, governance, and runtime utilities
5. **.codex/** → Codex `AGENTS.md`, config, hooks, and rules install assets
6. **agents/** → custom agent definitions
7. **dashboard/** → fleet monitoring web app
8. **research/** and **inventory/** → operational knowledge and state

## Architecture

```text
This Repo (develop)          Runtime targets
skills/          ──deploy──▶  ~/.copilot/skills + ~/.agents/skills
instructions/    ──deploy──▶  ~/.copilot/instructions
hooks/           ──deploy──▶  ~/.copilot/hooks + ~/.codex/devenv-ops/hooks
scripts/global/  ──deploy──▶  ~/.copilot/scripts + ~/.codex/devenv-ops/scripts
.codex/          ──deploy──▶  ~/.codex/AGENTS.md + config.toml + hooks.json + rules/
agents/          ──deploy──▶  ~/.copilot/agents
```

**Rule**: Never edit deployed runtimes directly. All changes flow through this repo.
Fleet is auto-detected via `scripts/global/fleet-config.js` (`inventory/devices.json`).

## Constraints

- **≤100 lines per file** (lint-enforced; split into linked files — never
  compress content — see `docs/howto/100-line-design-contract.md`)
- **JSON for structured data** and **Markdown for prose**
- **No build step** — dashboard is static HTML/JS/CSS
- **One live worktree per agent** — see `research/concurrent-agent-worktrees-2026-04-24.md`

## Commands

```bash
npm start                   # Dashboard on :8090
npm run lint                # 100-line file check
npm run sync                # Pull default runtime → repo
npm run sync:codex          # Pull Codex runtime → repo
npm run deploy              # Preview deploy (dry-run)
npm run deploy:apply        # Deploy repo → Copilot runtime
npm run deploy:codex:apply  # Deploy repo → Codex runtime
npm run deploy:both:apply   # Deploy repo → Copilot + Codex runtimes
npm test                    # E2E tests
```

## Git Workflow

1. Use a dedicated agent worktree, then `git checkout -b skill/<name>` or `feat/<topic>`
2. Make changes and test them in the target runtime
3. `git checkout main && git merge feat/... --no-ff`
4. Deploy the affected runtime(s) after merge
5. Delete feature branch

## Environment

Chromebook dev environment; agent has root/sudo access. Install tools as needed.

## User Interaction Rules

- **DO consult user**: Design decisions, architecture choices
- **DO NOT ask user**: Git practices, lint fixes, test execution
- **NEVER ask user to run tests**: Agent runs all automated checks

## Team&Model Signing

Every AI-authored baton artifact, PR evidence block, and governance doc must
carry a `Signed-by: <human-alias>` line and a `Team&Model: <team>:<model>@<host>`
provenance line. Aliases are derived from `inventory/team-model-signatures.json`.
See `instructions/team-model-signing.instructions.md` for the full contract.

## HAMR Cross-Team Routing

All governed provider calls route through HAMR (`https://hamr.chf3198.workers.dev`).
Activate per-checkout: `npm run hamr:activate`. Lane: free → fleet → haiku →
premium; HAMR handles cost levers and observability.
Canonical contract: `instructions/hamr-routing.instructions.md`.

## Advanced Governance Contracts

Goal Constitution, Cross-Team Artifact-Write, Hooks, OWASP, Skill Index, Role
Taxonomy, Merge-evidence: [copilot-instructions-advanced.md](copilot-instructions-advanced.md)
