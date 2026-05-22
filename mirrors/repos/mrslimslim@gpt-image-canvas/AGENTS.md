# Repository Notes

## Package Management

- Use `pnpm install`; the package manager is pinned to `pnpm@9.14.2`.
- Root scripts delegate to workspace packages: `pnpm dev`, `pnpm api:dev`, `pnpm web:dev`, `pnpm typecheck`, `pnpm build`, and `pnpm start`.

## Workspace Map

- API app: `apps/api`.
- Web app: `apps/web`.
- Shared contracts: `packages/shared`.

## Required Verification

- Before completing a story, run `pnpm typecheck` and `pnpm build`.
- UI stories require browser verification against the running app. Run `pnpm dev` and open the Vite web app, usually `http://localhost:5173`.
- Post-change verification must be delegated to a subagent running in an independent context whenever the agent environment supports subagents.
- The verification subagent should run the relevant checks, report exact commands and outcomes, and avoid editing implementation files unless explicitly assigned.
- Do not mark a story complete until the subagent verification has passed, or until any blocker is clearly documented with the failing command and error summary.
- If verification fails, fix the issue in the main implementation context, then ask the subagent to rerun the affected checks from a fresh independent context.

## Documentation Map

- Read `docs/PRODUCT_SENSE.md` before changing product behavior, onboarding, Gallery, provider configuration, or Agent workflows.
- Read `docs/DESIGN.md` and `docs/FRONTEND.md` before UI work in `apps/web`.
- Read `docs/design-docs/interaction-quality.md` for UI polish and micro-interaction work.
- Read `docs/PLANS.md` before writing product specs, execution plans, Ralph PRDs, or multi-story task breakdowns.
- Read `docs/RELIABILITY.md` and `docs/SECURITY.md` before API, storage, provider, Docker, SQLite, asset, secret, or local data work.

## Native Dependencies

- After switching Node versions, rebuild native API dependencies if `better-sqlite3` reports a `NODE_MODULE_VERSION` mismatch: `pnpm --filter @gpt-image-canvas/api rebuild better-sqlite3 --stream`.

## Docker

- For Docker verification with real `.env` credentials, run `docker compose config --quiet --no-env-resolution`; plain `docker compose config` expands env files and can print secrets.
- When Docker is available, run `docker compose up --build` and check the app on the configured `PORT` (default `8787`).

## Security And Local Files

- Keep local agent scratch files under `.codex-temp/`; do not commit local run logs or machine-specific paths.
- Do not commit `.env`, `.ralph`, `.codex-temp`, `data`, generated images, SQLite databases, or build output.
- Secrets must only be read from `.env` or the runtime environment and must never be logged.

## Ralph

- For Ralph-driven work, read `docs/ralph-execution.md` before creating or running a task.
- Keep Ralph PRDs under `.agents/tasks/`, runtime state under `.ralph/`, and extra wrapper logs under `.codex-temp/`.
- When invoking Ralph on Windows, prefer setting `PRD_PATH` and running `.agents/ralph/loop.sh` through Git Bash; avoid CLI flags that rewrite Windows paths unexpectedly.
