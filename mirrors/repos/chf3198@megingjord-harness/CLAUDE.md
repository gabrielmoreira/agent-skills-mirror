# Megingjord — Claude Code Governance

This project uses a structured Agile baton workflow, GitHub ticketing standards,
and AI agent governance. All instructions below are binding for Claude Code sessions.

> **Megingjord governance harness** — Rebranded from DevEnv Ops (2026-04-29).

## Instructions

@instructions/role-baton-routing.instructions.md
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
@instructions/repo-health-onboarding.instructions.md
@instructions/visual-qa-governance.instructions.md
@instructions/playwright-mcp-low-resource.instructions.md
@instructions/wiki-knowledge.instructions.md

## Runtime Context

- Skills (slash commands): `.claude/commands/`
- Agents: `.claude/agents/`
- Hook scripts: `~/.claude/hooks/scripts/` (after deploy)
- Deploy: `npm run deploy:claude` or `npm run deploy:apply` (both runtimes)
- Lint: `npm run lint` — all files must be ≤ 100 lines

## Concurrent session safety

- Do not share this checkout with Copilot or Codex while Claude Code is active.
- Use a dedicated worktree + branch for Claude Code work and merge via PR.
- See `research/concurrent-agent-worktrees-2026-04-24.md`.
