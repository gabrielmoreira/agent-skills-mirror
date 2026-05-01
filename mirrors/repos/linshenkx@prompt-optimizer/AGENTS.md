# Repository Guidelines

## Project Structure & Modules
- `packages/core` — TypeScript core library (built with `tsup`, tested with Vitest).
- `packages/ui` — Vue 3 component library used across apps (Vite build, ESLint enabled).
- `packages/web` — Vite web app (dev server, public assets in `public/`).
- `packages/extension` — Browser extension (Vite build, shares UI components).
- `packages/desktop` — Electron app; bundles `packages/web/dist` via `electron-builder`.
- `packages/mcp-server` — MCP server (Express + `@modelcontextprotocol/sdk`, `tsup` build).
- Support: `api/` (Vercel serverless functions), `docs/` & `mkdocs/`, `docker/`, `scripts/`, `tests/`.

## Build, Test, and Development
- Install deps (pnpm only): `pnpm install`
- Web dev: `pnpm dev` (builds core/ui, runs web)
- Desktop dev: `pnpm dev:desktop`
- Extension dev: `pnpm dev:ext`
- Build all: `pnpm build` | Desktop build: `pnpm build:desktop`
- Tests (all packages): `pnpm test` (Vitest) — per package: `pnpm -F @prompt-optimizer/core test`
- Lint UI: `pnpm lint` | fix: `pnpm lint:fix`

## Coding Style & Naming
- TypeScript + Vue 3. Use 2-space indentation and explicit typings where practical.
- Vue SFCs in PascalCase (e.g., `ConversationManager.vue`); directories in kebab-case when applicable.
- Tests end with `.test.ts` and live under `tests/unit` or `tests/integration`.
- Use `pnpm` exclusively. Do not add `package-lock.json` or `yarn.lock` (enforced by Husky).

## Testing Guidelines
- Framework: Vitest. Run all with `pnpm test`; coverage via `pnpm -F <pkg> test:coverage`.
- Prefer fast unit tests; add representative integration tests for cross-package flows.
- Example: `pnpm -F @prompt-optimizer/web test` or `pnpm -F @prompt-optimizer/core test:unit`.

## Commit & Pull Requests
- Follow Conventional Commits: `feat`, `fix`, `refactor`, `build` with optional scope.
  Example: `feat(ui): add template preview`.
- PRs must include: clear description, linked issues, test plan/steps; UI changes should include screenshots.
- Ensure `pnpm lint` and `pnpm test` pass before requesting review.

## Security & Configuration
- Do not commit secrets. Use `.env.local` (see `env.local.example`).
- Node 22.x is required. Local dev and deploy can use Docker/Vercel; see `dev.md` and `docs/`.
