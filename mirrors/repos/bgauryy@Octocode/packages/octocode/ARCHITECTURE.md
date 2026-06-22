# Octocode CLI Architecture

`octocode` is the user-facing **CLI and installer** package. It is a thin
presentation layer: it parses input, routes to a handler, and renders output.
All tool logic — schemas, execution, pagination, security — lives in
`@octocodeai/octocode-tools-core` (which in turn calls the native
`@octocodeai/octocode-engine` and reads metadata from `@octocodeai/octocode-core`).
Nothing in this package shapes tool data; it only formats it for a terminal.

## Boundary

- `src/index.ts` is the binary entry (`bin: out/octocode.js`). It calls
  `runCLI()`, falls back to top-level help, and owns process signals/exit.
- `src/cli/index.ts` (`runCLI`) is the dispatcher: parse args → handle global
  flags (`--help`, `--version`, `--context`, `--no-color`) → route to a command,
  the `tools`/`context` surface, or interactive install.
- Keep dispatch thin. New behavior belongs in a command or feature module, not
  in `runCLI`.

## Layers

- `src/cli/` — argument parsing (`parser.ts`), routing (`routing.ts`, the
  local-vs-GitHub ref resolver), validation, help rendering, and exit codes
  (`exit-codes.ts`).
- `src/cli/commands/` — one file per command. Two groups:
  - **Quick commands** (`cat`, `ls`, `find`, `grep`, `pr`, `history`, `repo`,
    `pkg`, `lsp`, `binary`, `unzip`, `clone`) — Unix-style shortcuts that resolve
    a target ref and call the underlying tool. Lazy-loaded via `commands/index.ts`.
  - **Management commands** (`install`, `auth`/`login`/`logout`, `status`) —
    eagerly loaded; manage setup, credentials, and environment state.
- `src/cli/tool-command.ts` — the raw `tools <name>` / `context` surface. Bridges
  directly to `octocode-tools-core/direct` (`executeDirectTool`, schema text,
  display fields) for power users and agents.
- `src/ui/` — interactive TUI: the menu loop (`menu.ts`), install flow
  (`install/`), config inspector (`config/`), and skills marketplace
  (`skills-menu/`). Reached via `octocode install` → `runInteractiveMode`.
- `src/features/` — stateful operations behind commands/UI: MCP `install`,
  GitHub `github-oauth` / `gh-auth`, `skills` install, registry `sync`, and
  `node-check`.
- `src/configs/` — static, Zod-validated catalogs: `mcp-registry.ts` (installable
  MCP servers) and `skills-marketplace.ts` (skill sources). Validated by
  `scripts/validate-*.ts`.
- `src/utils/` — terminal primitives (colors, spinner, prompts), MCP config I/O,
  token storage, platform/shell/fs helpers, and frontmatter parsing.

## Build

- `build.mjs` bundles `src/index.ts` with esbuild → `out/octocode.js`
  (ESM, minified, code-split, with a CJS-compat banner and a `#!/usr/bin/env node`
  shebang).
- All runtime `dependencies`, plus transitive native packages
  (`octocode-engine`, `octocode-core`, `zod`), stay **external** — never inlined —
  so `.node` binaries are resolved by the package manager at runtime.
- `__APP_VERSION__` is injected at build time from `package.json`.

## Rules

- The CLI renders; it does not compute. Push any data-shaping into
  `octocode-tools-core`.
- Lazy-load command and tool modules (dynamic `import`) to keep startup fast and
  tolerate a missing tool runtime gracefully.
- Keep `mcp-registry` / `skills-marketplace` schema-valid; run `yarn verify`
  (lint + typecheck + test + registry/skills validation) before publishing.
