# Repository Guidelines

## Project Structure & Module Organization
- This repo is an npm workspace with independent packages in `packages/*`.
- Each package follows a consistent layout:
  - `extensions/index.ts` for the pi extension entry point.
  - `__tests__/` for Vitest tests (e.g., `index.test.ts`, `helpers.test.ts`).
  - `README.md`, `package.json`, and `LICENSE` per package.
- Root-level configs live in `biome.json`, `tsconfig.json`, and `vitest.config.ts`.

## Build, Test, and Development Commands
Run these from the repo root unless noted:
- `npm run lint` — Biome lint/format checks.
- `npm run lint:fix` — auto-fixable Biome issues.
- `npm run typecheck` — TypeScript type checking only.
- `npm run test` — Vitest test suite.
- `npm run check` — lint + typecheck.
- `npm run check:ci` — CI-friendly Biome + typecheck.

Local package testing:
- `cd packages/<package-name>`
- `pi -e .` — run the package in pi without installing.

## Coding Style & Naming Conventions
- Language: TypeScript.
- Formatting: Biome with **tabs** for indentation and `lineWidth` 120.
- File naming: tests live in `__tests__` and use `*.test.ts`.
- Package naming: `packages/pi-<name>` with npm scope `@benvargas/pi-<name>`.

## Testing Guidelines
- Framework: Vitest (see `vitest.config.ts`).
- Tests are per-package under `packages/*/__tests__/`.
- Keep unit tests focused on extension behavior and helpers; prefer fast, isolated tests.

## Commit & Pull Request Guidelines
- Commit messages generally follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`. Older commits may use `Add …`; new commits should prefer the conventional style.
- PRs should include:
  - A short summary and the affected package(s).
  - Tests run (e.g., `npm run test`, `npm run check`).
  - Linked issues or context for behavior changes.
  - Notes on any new configuration or environment variables.

## Security & Configuration Tips
- Do not commit API keys. Use environment variables or the config file locations documented in each package README (e.g., under `~/.pi/agent/extensions/`).
- If you change defaults or CLI flags, update the package README accordingly.
- Tool schemas: avoid `Type.Unknown()` in tool parameters. It serializes to `{}`, which some inference backends reject as invalid JSON Schema. Prefer `Type.Object({}, { additionalProperties: true })`.
