# Copilot Instructions — devenv-ops

**devenv-ops**: Development workbench for the DevEnv Ops Harness runtime assets deployed to `~/.copilot/`, `~/.codex/`, and `~/.agents/skills/`.

## Execution Model

Every task follows the **role baton sequence**: Manager → Collaborator → Admin → Consultant.
See `role-baton-routing` for rules. Local repos may override via `.github/copilot-instructions.md`.

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

## Fleet Topology

Auto-detected via `scripts/global/fleet-config.js`. Devices live in `inventory/devices.json`.
IPs resolve from `.env` overrides or Tailscale discovery.

## Constraints

- **≤100 lines per file** (lint-enforced)
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

Chromebook dev environment. Agent has root/sudo access.
Install tools via CLI as needed. Don’t ask permission.

## User Interaction Rules

- **DO consult user**: Design decisions, architecture choices
- **DO NOT ask user**: Git practices, lint fixes, test execution
- **NEVER ask user to run tests**: Agent runs all automated checks

## Team&Model Signing

AI-authored baton artifacts, PR evidence, and governance docs must include human alias + structured `Team&Model` provenance.

## HAMR Cross-Team Routing

All governed provider calls route through HAMR (`https://hamr.chf3198.workers.dev`). Activate per-checkout: `npm run hamr:activate`. Canonical contract: `instructions/hamr-routing.instructions.md`. The Global Task Router (lane selection) and HAMR (cost/observability mechanics) are complementary — HAMR does not duplicate lane policy.

## Harness Goal Constitution (priority)

Apply this decision order for governed work:
Governance > Quality > Zero Cost > Privacy > Portability > Resilience > Throughput > Observability > Interoperability.
If a lower-priority goal wins, record rationale in ticket/PR evidence.

## Skill Index

Auto-derived from `skills/<name>/SKILL.md` frontmatter — see [`docs/skills-copilot.md`](../docs/skills-copilot.md). Regenerate via `node scripts/global/skill-views-derive.js`.
