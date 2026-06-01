# CLAUDE.md

Project conventions and notes for AI assistants working on notfair-cmo.

## Testing

Test runner: **vitest** (added 2026-05-19 as part of the onboarding rework, the first test infrastructure in the repo).

- Run tests once: `pnpm test`
- Watch mode: `pnpm test:watch`
- Vitest UI: `pnpm test:ui`

Test files live next to the code they test: `src/lib/slug.ts` → `src/lib/slug.test.ts`.

Environment selection (configured in `vitest.config.ts`):
- Default: `node` (server modules, libs)
- Components under `src/components/**`: `jsdom`
- Page tests `src/app/**/*.test.tsx`: `jsdom`

Setup file `vitest.setup.ts` imports `@testing-library/jest-dom/vitest` so jest-dom matchers (`toBeInTheDocument`, etc.) are available in component tests.

### What to test

- **Server modules** (anything under `src/server/`): unit-test pure functions, integration-test handlers with mocked subprocess (`openclaw`) and mocked `fetch` (MCP).
- **Lib utilities** (`src/lib/`): pure-function unit tests with full branch coverage.
- **Components** (`src/components/`): user-facing interaction tests via `@testing-library/react` (render → fire events → assert visible state). Avoid implementation-detail assertions.
- **API routes** (`src/app/api/`): integration tests that POST to the handler with mocked dependencies.

### Mocking external systems

- **Harness adapters**: under `src/server/adapters/`. The `claude-code-local` and `codex-local` execute paths spawn a real subprocess; in tests, mock the parser modules (`parse.ts`) for unit coverage, or stub `child_process.spawn` in integration tests.
- **MCP HTTP**: mock `fetch` globally. The MCP responds with JSON-RPC envelope `{jsonrpc, id, result | error}`.
- **SQLite**: use the real better-sqlite3 against an in-memory DB or a tmpdir DB — better-sqlite3 is synchronous + fast enough that mocking adds friction without value.

### Prompt/LLM changes (eval suites required)

If you touch any of these files, an eval pass is required before shipping:

- `src/server/agent-templates.ts` (CMO + Google Ads + SEO system prompts)
- `src/server/agent-chat.tsx` chat orchestration if it adds new tool-call patterns
- Any new file under `src/server/onboarding/` that constructs prompt context (e.g., `audit.ts` writing `FIRST_TURN.md`)

Light eval harness lives at `tests/evals/`. Pattern: golden scenario JSON + expected-shape assertions. Run via `pnpm eval`. Skips entirely when `OPENAI_API_KEY` is absent. See `tests/evals/README.md` for details.

## Project structure conventions

- **Database**: SQLite via `better-sqlite3` at `~/.notfair-cmo/db.sqlite` (overridable via `NOTFAIR_CMO_DATA_DIR`). Migrations are forward-only in `src/server/db/migrations.ts` (mirrored in `src/server/db/migrations/`).
- **Agent state**: agent workspaces live at `~/.notfair-cmo/agents/<agent-id>/`. notfair-cmo owns the workspace; the chosen harness adapter writes whatever files it expects (CLAUDE.md for Claude Code, AGENTS.md for Codex, plus the shared IDENTITY.md / SKILL.md / PROJECT.md notfair-cmo writes).
- **Sessions / transcripts**: stored in SQLite (`sessions`, `transcript_events`). Replaces the OpenClaw JSONL transcript files. The chat route persists every adapter event there; the UI replays them on attach.
- **MCP tokens**: stored project-scoped in the `mcp_tokens` SQLite table. Adapters expose `registerMcp` / `unregisterMcp` to wire the chosen harness's MCP config to point at the right tokens.
- **Cron schedules**: stored in the `scheduled_jobs` SQLite table. A node-cron-style tick loop in `src/server/scheduler/tick.ts` polls due jobs every 30s and dispatches them through the project's adapter.
- **Project memory**: per-agent workspace files (e.g. files the agent writes in its workspace dir). No proprietary REM/memory layer yet; if an agent needs durable memory across sessions it writes to its workspace.

## Architectural tenets

- **Harness-agnostic.** notfair-cmo runs on top of any local AI coding agent that conforms to the `HarnessAdapter` contract under `src/server/adapters/`. Today: Claude Code (`claude-code-local`) and Codex (`codex-local`). Recommended path mirrors paperclip's adapter-registry pattern.
- **notfair-cmo owns the runtime services.** Cron scheduling, MCP token storage, agent provisioning, session/transcript persistence — all in SQLite + Node. Adapters only handle: (1) spawning the harness to stream a turn, (2) writing harness-specific workspace config, (3) registering MCP servers for the harness to find.
- **Single-user local CLI.** V1 is a local Next.js process launched via `notfair-cmo` bin. No multi-tenant code paths, no auth, no multi-process state coordination.
- **Don't rebuild the wheels.** Before proposing any new abstraction, identify whether AI SDK, the existing skill ecosystem, or another off-the-shelf tool already solves the sub-problem. Prefer thin attribution/glue layers over custom infrastructure.

## Commit style

Conventional commits with type-scope-description: `feat(onboarding): add real audit stream`, `fix(cron): preserve agent prefix on rename`, `chore(deps): bump next to 16.2.7`.

Co-author trailer when AI-assisted:
```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
