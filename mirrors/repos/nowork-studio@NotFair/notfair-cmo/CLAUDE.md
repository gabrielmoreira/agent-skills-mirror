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

- `openclaw` CLI subprocess: mock `@/server/openclaw/cli` `openclaw` function. Return whatever JSON shape the production CLI would return.
- MCP HTTP: mock `fetch` globally. The MCP responds with JSON-RPC envelope `{jsonrpc, id, result | error}`. See `src/server/mcp/rpc.ts` (when extracted) for the canonical request shape.
- SQLite: use the real better-sqlite3 against an in-memory DB or a tmpdir DB — better-sqlite3 is synchronous + fast enough that mocking adds friction without value.

### Prompt/LLM changes (eval suites required)

If you touch any of these files, an eval pass is required before shipping:

- `src/server/agent-templates.ts` (CMO + Google Ads + SEO system prompts)
- `src/server/agent-chat.tsx` chat orchestration if it adds new tool-call patterns
- Any new file under `src/server/onboarding/` that constructs prompt context (e.g., `audit.ts` writing `FIRST_TURN.md`)

Light eval harness lives at `tests/evals/`. Pattern: golden scenario JSON + expected-shape assertions. Run via `pnpm eval`. Skips entirely when `OPENAI_API_KEY` is absent. See `tests/evals/README.md` for details.

## Project structure conventions

- **Database**: SQLite via `better-sqlite3` at `~/.notfair-cmo/db.sqlite` (overridable via `NOTFAIR_CMO_DATA_DIR`). Migrations are forward-only in `src/server/db/migrations.ts` (mirrored in `src/server/db/migrations/`).
- **Agent state**: lives in OpenClaw at `~/.openclaw/`. We do NOT shadow-store agent state; OpenClaw is the source of truth.
- **MCP tokens**: stored project-scoped via `openclaw mcp set <project-slug>-<catalog-key>`. Never stored in our own DB.
- **Cron schedules**: stored in OpenClaw via `openclaw cron add` with naming convention `<project-slug>/<agent-slug>/<cron-slug>`. Frontend parses the prefix to organize the cron tab.
- **Project memory**: per-agent OpenClaw memory (REM). Tag conventions: `google-ads-baseline:<date>` for audit results, etc.

## Architectural tenets

- **Don't rebuild the wheels.** Before proposing any new abstraction, identify whether OpenClaw, AI SDK, the existing skill ecosystem, or another off-the-shelf tool already solves the sub-problem. Prefer thin attribution/glue layers over custom infrastructure.
- **Single-user local CLI.** V1 is a local Next.js process launched via `notfair-cmo` bin. No multi-tenant code paths, no auth, no multi-process state coordination.
- **OpenClaw is the agent runtime.** Our Next.js is a portal + MCP server. Agents themselves run in OpenClaw.

## Commit style

Conventional commits with type-scope-description: `feat(onboarding): add real audit stream`, `fix(cron): preserve agent prefix on rename`, `chore(deps): bump next to 16.2.7`.

Co-author trailer when AI-assisted:
```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
