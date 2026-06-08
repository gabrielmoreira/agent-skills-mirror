# AGENTS.md — Megingjord baseline

> **Cross-team contract**: see `governance/README.md` for the canonical entry point covering Team&Model signing, baton order, ticket-first workflow, and dedicated worktree (the 4 invariants). This file is the generic-AGENTS.md adapter.

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

## Review guidelines

- In Codex PR reviews, treat ticket lifecycle, baton order, signer
  fidelity, isolated worktrees, and runtime-home edits as release-blocking
  governance risks.
- Verify governed changes include matching docs, research, wiki, or drift
  notes when behavior or operator workflow changes.
- When Codex behavior is uncertain, use official OpenAI Codex docs instead of
  inferring from Claude or Copilot compatibility.

## HAMR cross-team routing

- All 3 teams route governed provider calls through HAMR (`https://hamr.chf3198.workers.dev`).
- Activate per-checkout: `npm run hamr:activate`. Verify: `npm run hamr:sync-verify`.
- Canonical + provider-neutral contracts: `instructions/hamr-routing.instructions.md`, `instructions/provider-neutral-governance.instructions.md`.

## Skill index

Auto-derived from `skills/<name>/SKILL.md` — see [`docs/skills-agents.md`](docs/skills-agents.md). Regenerate via `node scripts/global/skill-views-derive.js`.

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
- No build step; Cloudflare Pages for production deployment

## Merge-evidence

Use `merge-evidence-deferred-final: #N` in PR body (or `Closes #N`). See `governance-carve-outs/index.md`.

## Role Taxonomy

The harness uses a 7-role canonical taxonomy: Manager / Collaborator / Admin /
Consultant / IT / Red-Team / Client. Guest-Collaborator is reserved but not active.
Operator is a meta-term for the AI agent — not a distinct role.
Canonical definition: `instructions/role-baton-routing.instructions.md` §"Role Taxonomy".

## Key contracts (2026-H1)

- **Doc-coverage gate**: `COLLABORATOR_HANDOFF` must include `doc-coverage:` block for `lane:code-change`. See `docs/howto/merge-time-doc-governance.md`.
- **Baton builders**: Use `baton-comment-build.js`, `pr-comment-build.js`, `changelog-fragment-build.js` for governed artifacts.
- **Governance chains**: Run `npm run governance:chains:check` on governance path changes. See `docs/howto/governance-chains.md`.
- **OTel GenAI**: `isValidGenAI()` from `scripts/global/otel-genai-conformance.js`; validate telemetry fields before emit.
- **Fleet-call-guard**: All fleet calls must use bounded timeout (see `docs/howto/fleet-call-guard.md`; PR #2697).
- **Credential guard**: Check `credential-availability.js` before prompting user for secrets; `.env` may already have them.
- **Admin-merge-exception**: Override merges require `merge-bypass:admin-exception` label per Epic #2517.
