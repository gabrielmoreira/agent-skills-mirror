# CLAUDE.md

Project-specific instructions for Claude Code.

## GitNexus — Always Use

**MUST always use GitNexus tools to optimize code exploration, impact analysis, and refactoring.** GitNexus is the primary tool for understanding the codebase — prefer it over manual grep/search.

- Before editing any symbol: run `gitnexus_impact` to check blast radius
- Before exploring code: run `gitnexus_query` to find execution flows
- Before refactoring: run `gitnexus_context` to see all callers/callees
- Before committing: run `gitnexus_detect_changes` to verify scope
- For renaming: use `gitnexus_rename` instead of find-and-replace
- **Note:** GitNexus CLI requires Node 20 (`source ~/.nvm/nvm.sh && nvm use 20`)

## Language Rules

**Always respond in English, regardless of the user's input language.**

- All responses must be in English
- All code changes, comments, and documentation must be in English
- Even if the user communicates in another language, respond in English

## Version Bump & Release

Two release channels: **stable** (`latest` npm tag) and **beta** (`beta` npm tag).

- Users install stable: `npm install -g claude-ws`
- Users install beta: `npm install -g claude-ws@beta`

### Beta Release (from `dev` branch)

1. Bump version in `package.json` to `X.Y.Z-beta.N` (e.g. `0.4.0-beta.1`)
2. Commit: `chore: bump version to X.Y.Z-beta.N`
3. Push to `dev`
4. Publish to npm: `npm publish --access public --tag beta`
5. Create GitHub prerelease: `gh release create vX.Y.Z-beta.N --target dev --title "vX.Y.Z-beta.N" --prerelease --notes "..."`
6. Stay on `dev`

### Stable Release (from `main` branch)

1. Bump version in `package.json` to `X.Y.Z` (remove `-beta.N` suffix)
2. Commit: `chore: bump version to X.Y.Z`
3. Push to `dev`, merge `dev` into `main`, push `main`
4. Publish to npm: `npm publish --access public`
5. Create GitHub release: `gh release create vX.Y.Z --target main --title "vX.Y.Z" --notes "..."`
6. Switch back to `dev`

### Release Notes Format

Use this exact format for GitHub release notes, categorized by emoji headers:

```
## What's New

### 🌐 Category Name (e.g., Internationalization)
- Change description
- Change description

### 🔧 Agent & SDK
- Change description

### 📝 Editor
- Change description

### 🖥️ UI/UX
- Change description

### 🐛 Bug Fixes
- Change description

### 📦 Dependencies
- Change description
```

**Category emojis reference:**
- 🌐 i18n / Localization
- 🔧 Agent, SDK, Backend
- 📝 Editor, Code
- 🖥️ UI/UX, Frontend
- 🐛 Bug Fixes
- 📦 Dependencies
- 🔒 Security
- ⚡ Performance
- 📖 Documentation
- 🏗️ Infrastructure, CI/CD

Only include categories that have changes. Each bullet should be concise (no full sentences needed).

## Plugins

**MUST use `agent-sdk-dev` plugin** when working with Claude Agent SDK (`@anthropic-ai/claude-agent-sdk`).

This plugin provides:
- `/new-sdk-app` command to scaffold new SDK applications
- `agent-sdk-verifier-ts` agent to verify TypeScript SDK apps
- `agent-sdk-verifier-py` agent to verify Python SDK apps

Use it for:
- Creating new Agent SDK projects
- Verifying SDK usage and best practices
- Debugging SDK integration issues

Dont try start run dev when finish a conversation only when you are asked to.

## Backend development

**Dont run `pnpm build` because we start pm2 npm run dev
**Any changes of backend, must run `pm2 restart claudews` to reload backend

## Frontend development

**Dont `pm2 restart claudews` if we change frontend only

## Agentic-SDK API Integration

**CRITICAL: ALL requests to the API domains below MUST go through `packages/agentic-sdk`. The SDK is the single source of truth for all business logic, database queries, validation, and routing. Next.js API routes are thin proxies that delegate to the SDK — they MUST NOT contain any business logic themselves.**

### Covered API Domains

ALL traffic for these routes goes through agentic-sdk:

- `/api/attempts/*` — attempts CRUD, streaming, sub-resources
- `/api/projects/*` — projects CRUD
- `/api/tasks/*` — tasks CRUD
- `/api/checkpoints/*` — checkpoints CRUD
- `/api/files/*` — file read/write, tree, content
- `/api/search/*` — code/file search
- `/api/shells/*` — shell sessions
- `/api/uploads/*` — file uploads
- `/api/commands/*` — command execution
- `/api/agent-factory/*` — agent creation/management
- `/api/auth/*` — authentication/authorization

### Rules

1. **SDK owns these 11 domains** — All database queries, validation, business logic, error handling for the domains listed above live in `packages/agentic-sdk`. Next.js route handlers for these domains only parse the request and call the SDK.
2. **No bypassing** — NEVER write direct database queries, inline validation, or business logic in `src/app/api/` route handlers for these domains. Always import and call SDK services/routes.
3. **SSE streaming** — The only SSE endpoint is `GET /api/attempts/:id/stream`, handled by `packages/agentic-sdk/src/routes/attempt-sse-routes.ts`. Do NOT create duplicate SSE endpoints.
4. **New features** — When adding new endpoints or modifying existing ones for these domains, implement the logic in `packages/agentic-sdk` first, then wire it up in the Next.js route handler.
5. **Modifications** — When fixing bugs or changing behavior for these domains, the fix goes in the SDK, not in the Next.js route handler.

## Dependencies Management

**Runtime packages go in `dependencies`. Build/dev-only tools go in `devDependencies`.**

- Packages imported by production code (`src/`, `server.ts`) **MUST** be in `dependencies`
- Packages only used at dev time (CLI tools, type-only imports, code generators) **MAY** be in `devDependencies`
- The `scripts/check-dependencies.sh` script validates no production code imports from `devDependencies`
- When in doubt, put it in `dependencies`

**Current devDependencies (approved):**
- `@types/js-yaml` — type definitions only
- `drizzle-kit` — CLI tool for `db:generate`, only type-imported in `drizzle.config.ts`

**Why:** This is a published npm package. When users install via npm, `devDependencies` are not installed. Any runtime import from `devDependencies` will fail. Build/dev tools that are never imported at runtime are safe in `devDependencies`.

## Data Migrations (CRITICAL)

**ALL data-layer changes MUST go through the incremental migration system.** This includes:
- **DB schema changes** (new tables, new columns, index changes)
- **Config folder changes** (symlinks, file moves, config restructuring in `data/`)
- **Data folder changes** (session file moves, cache restructuring, data format upgrades)

Migrations run automatically on every server startup via `runMigrations()` in `server.ts`. Version tracked in `app_settings` table (`migration_version` key).

### How to Add a Migration

1. Create `src/lib/migrations/NNN-descriptive-name.ts` (increment NNN from last migration)
2. Export a `Migration` object: `{ version: N, name: string, run: () => void }`
3. Import and append to `migrations` array in `src/lib/migrations/migration-runner.ts`
4. For DB schema changes, also update `src/lib/db/schema.ts` (Drizzle types) and `src/lib/db/index.ts` (`initDb()` for fresh installs)
5. Run `pnpm db:generate` if DB schema changed

### Migration File Template

```typescript
// src/lib/migrations/NNN-descriptive-name.ts
import type { Migration } from './migration-runner';

export const migration: Migration = {
  version: NNN,
  name: 'descriptive-name',
  run: () => {
    // Migration logic here — must be idempotent as safety net
  },
};
```

### Rules

- Migrations run in order, exactly once per version number
- Each migration must be **idempotent** (safe if re-run)
- On failure: migration halts, server logs error — fix and restart
- **NEVER** modify an already-released migration — create a new one
- Keep migration logic self-contained (don't import app services that may change)
- For DB schema: still update `schema.ts` + `initDb()` for fresh installs (migrations handle upgrades)

### Current Migrations

| # | Name | Description |
|---|------|-------------|
| 001 | shared-session-directory-symlink | Symlinks SDK projects/ → ~/.claude/projects/ for cross-provider session resume |

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **claude-ws** (6054 symbols, 13904 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/claude-ws/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/claude-ws/context` | Codebase overview, check index freshness |
| `gitnexus://repo/claude-ws/clusters` | All functional areas |
| `gitnexus://repo/claude-ws/processes` | All execution flows |
| `gitnexus://repo/claude-ws/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
