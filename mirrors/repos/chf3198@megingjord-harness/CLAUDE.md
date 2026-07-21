# Megingjord — Claude Code Governance

This project uses a structured Agile baton workflow, GitHub ticketing standards,
and AI agent governance. All instructions below are binding for Claude Code sessions.

> **Megingjord governance harness** — Rebranded from DevEnv Ops (2026-04-29).
> **Cross-team contract**: see `governance/README.md` for the canonical entry point (4 invariants: Team&Model signing, baton order, ticket-first, dedicated worktree). This file is the Claude Code adapter.

## Instructions

@instructions/role-baton-routing.instructions.md
@instructions/test-methodology-matrix.instructions.md
@instructions/ticket-driven-work.instructions.md
@instructions/operator-identity-context.instructions.md
@instructions/team-model-signing.instructions.md
@instructions/global-standards.instructions.md
@instructions/global-task-router.instructions.md
@instructions/github-governance.instructions.md
@instructions/epic-governance.instructions.md
@instructions/feature-completion-governance.instructions.md
@instructions/workflow-resilience.instructions.md
@instructions/release-docs-hygiene.instructions.md
@instructions/wiki-knowledge.instructions.md
@instructions/hamr-routing.instructions.md
@instructions/observability.instructions.md
@instructions/cross-team-artifact-write.instructions.md
@instructions/cross-team-communication-tiers.instructions.md
@instructions/credential-prompt-guard.instructions.md
@instructions/worktree-tool-boundary.instructions.md

## On-demand instructions (Epic #3137 T1 — situational, not always-resident)

These remain in `instructions/` and are loaded on demand (via the read-router / `Read`) only when the
relevant work occurs — they carry no always-on binding rule, so keeping them resident every turn wastes
tokens (G3). Classifier: `scripts/global/instructions-split-classifier.js` (fail-open: any binding
signal or core-identity → resident). Resident-load budget + **fail-closed** on-demand loading (a
migrated rule that cannot load when its operation needs it BLOCKS/warns — no silent rule-loss):
`scripts/global/resident-load-budget.js` (Epic #3807 C4, #3812).

- `instructions/visual-qa-governance.instructions.md` — load when modifying HTML/CSS/JS or releasing a web surface.
- `instructions/playwright-mcp-low-resource.instructions.md` — load for Playwright / browser automation.
- `instructions/owasp-agentic-mapping.instructions.md` — reference table; load for security-mapping work.
- `instructions/repo-health-onboarding.instructions.md` — load for new-repo onboarding / health audits.
- `instructions/resource-tier-portability.instructions.md` — resource-tier *taxonomy* (tiers 0–5); load when declaring/choosing a feature's resource tier or its baseline-absent fallback (#3812; migrated resident→on-demand — its binding G5 partner `harness-goals.instructions.md` was already on-demand). Loader operation key: `resource-tier-selection`.

## Runtime Context

- Skills (slash commands): `.claude/commands/`
- Agents: `.claude/agents/`
- Hook scripts: `~/.claude/hooks/scripts/` (after deploy)
- Deploy: `npm run deploy:apply` deploys the two script-mirror runtimes (Copilot `~/.copilot` + Codex `~/.codex`); `npm run deploy:claude:apply` deploys the Claude Code runtime (`~/.claude`). Run both for full coverage. (Per #2950: `deploy:apply` previously targeted Copilot only, silently drifting Codex; it now targets `both`.)
- Lint: `npm run lint` — all files must be ≤ 100 lines

## Governance mechanisms — key references

Two machine-guaranteed governance mechanisms underpin the baton workflow; consult these when authoring artifacts or adding a governed link:

- **Governance chains** (no link may depend on operator discretion; every link is auto-emitted or fail-closed) — `docs/howto/governance-chains.md` (Epic #2709).
- **Baton-artifact builders** (PR body, CHANGELOG fragment, commit trailers, and the six comment artifacts are built deterministically with derived signers — the default path, env-flag rollback) — `docs/howto/baton-builders.md` (Epic #2037).

## Concurrent session safety

- Do not share this checkout with Copilot or Codex while Claude Code is active.
- Use a dedicated worktree + branch for Claude Code work and merge via PR.
- See `research/concurrent-agent-worktrees-2026-04-24.md`.
- New worktrees auto-link `node_modules` from main checkout via `scripts/worktree-session-start.sh` — no manual `npm install` needed (per #1378). For pre-existing worktrees missing `node_modules`, run `npm run worktree:bootstrap`.
