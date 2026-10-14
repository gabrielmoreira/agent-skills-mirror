# Toolkit

This workspace lives at `toolkit/` inside the agent-skills catalog repository. The catalog skill rules in the root
`AGENTS.md` govern `skills/`, not the toolkit. The toolkit follows this file and its package-local AGENTS.md files.
Toolkit commits use the catalog's natural-language commit format.

## Workspace boundaries

- The nightly Rust workspace contains the `ai-commit`, `ai-coord`, `ai-handoff`, `ai-notify`, and `ai-skillet` crates.
  Keep shared Rust configuration at the workspace root (`toolkit/`) and crate behavior within its crate.
- `apps/coord-dashboard` is an independent Bun package with its own lock and package-local validation. Do not combine
  its dependencies, scripts, or build outputs with the Rust workspace.
- Context is source-owned. This file describes workspace-wide behavior. Package-local AGENTS.md files own product and
  workflow guidance. Update the owning package rather than duplicating its guidance here.

## Validation

Use `toolkit/justfile` for local validation (`just <recipe>` inside `toolkit/`, or `just toolkit::<recipe>` from the
catalog root). Run focused tests while iterating, then the complete affected gate before committing:

| Change scope                                  | Final local gate             |
| --------------------------------------------- | ---------------------------- |
| Rust code, Cargo dependencies, Rust toolchain | `just rust-check`            |
| Coordination dashboard                        | `just coord-dashboard-check` |
| Shared workspace wiring or Rust/app contracts | `just check`                 |

`just rust-check` checks formatting, Clippy with warnings denied, tests, builds, and platform-specific installation
tests for the locked Rust workspace. Installation tests use mock commands and do not install binaries. The dashboard
gate checks lint, formatting, types, tests, and the production build. UI changes also need the owning package's rendered
verification. `just check` runs both gates. None of these checks installs CLI binaries. Documentation-only edits follow
the root formatting and factual-verification rules.

In Linux containers, preserve Git repository metadata and use an init process, such as Docker's `--init` option. The
ignore-rule fixtures require repository metadata. Process-group tests require orphaned child processes to be reaped.

## Compatibility and safety

- Maintain macOS and Linux support for `ai-commit`, `ai-coord`, `ai-handoff`, and `ai-skillet`. Keep `ai-notify`
  macOS-only. The installation recipe selects supported packages and restarts an existing launchd service only on macOS.
- Preserve each tool's documented command, output, and persisted-data contracts. Do not add compatibility paths,
  migrations, aliases, or dual formats unless explicitly requested. Reject incompatible persisted versions with
  actionable errors.
- Changes that can invalidate live ai-coord agents, state, hooks, or CLI installation require explicit authorization and
  an isolated `AI_COORD_STATE_DIR` for development and validation. Never reset coordination state or replace global
  hooks from this checkout implicitly.
- Updating the installed CLIs (`just install-cli`, or `just toolkit::install-cli` from the catalog root) is
  pre-authorized when the committed changes preserve the documented command, output, and persisted-data contracts. It is
  also pre-authorized when `ai-coord` shows no other live agent sessions on this machine. Otherwise ask the user to
  close the other agents before installing.
- Keep the dashboard local-only and bound to loopback, with no external requests. Its handoffs view must remain
  read-only.
