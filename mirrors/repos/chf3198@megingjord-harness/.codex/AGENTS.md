# Megingjord — Global Governance Harness

- Cross-team contract entry point: `governance/README.md` (4 invariants: Team&Model signing, baton order, ticket-first workflow, dedicated worktree per concurrent agent). This file is the Codex adapter.
- Treat this file as the global Megingjord baseline for Codex runtime.
- Apply the baton order: Manager → Collaborator → Admin → Consultant; one role active at a time per ticket.
- Repo-local `AGENTS.md` files override this baseline when they conflict.
- Respect Megingjord governance from `~/.codex/config.toml`, `~/.codex/hooks.json`, and `~/.codex/rules/`.
- Treat repo `.codex/config.toml` and `.codex/runtime.config.toml` as source
  assets; deploy or install them through governed workflow only.
- Keep project-local Codex guidance in `AGENTS.md`; use
  `project_doc_fallback_filenames` only for compatibility when `AGENTS.md` is
  missing.
- Preserve Team&Model signing on governed issue, PR, commit, and doc artifacts.
- Use installed Megingjord skills from `$HOME/.agents/skills/` when relevant.
- Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, ChatGPT Apps SDK, Codex, or related docs without me having to explicitly ask.
- Apply harness goal priority for decisions: Governance > Quality > Zero Cost > Privacy > Portability > Resilience > Throughput > Observability > Interoperability > Maintainability.
- HAMR routing canonical contract: `instructions/hamr-routing.instructions.md` (cost levers, /quota, /mcp, cache-hit gate). Complementary to the Global Task Router lane policy.
- OWASP Agentic security mapping: `instructions/owasp-agentic-mapping.instructions.md` (OA1-OA10 risk-to-goal mapping; G1-G10 coverage classification).
- Cross-team artifact-write contract: `instructions/cross-team-artifact-write.instructions.md` (target-runtime team owns schema/contract test; required before manager-handoff on cross-runtime config writes).
- **2026-H1 key contracts**: doc-coverage gate (COLLABORATOR_HANDOFF must include `doc-coverage:` block for lane:code-change), baton builders (`baton-comment-build.js`), governance chains (`npm run governance:chains:check`), fleet-call-guard (bounded timeout required, PR #2697), credential-prompt-guard (check `.env` before prompting), admin-merge-exception (Epic #2517 gate), worktree-tool-boundary (file-editing tools restricted to registered workspace; shell-only for worktrees — #3243). Mirror AGENTS.md §Key contracts.
