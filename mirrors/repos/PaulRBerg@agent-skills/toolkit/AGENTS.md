# Toolkit

This workspace lives at `toolkit/` inside the agent-skills catalog repository. The catalog skill rules in the root
`AGENTS.md` govern `skills/`, not the toolkit. The toolkit follows this file and its package-local AGENTS.md files.
Toolkit commits use the catalog's natural-language commit format.

## Workspace boundaries

- The nightly Rust workspace contains the `ai-commit`, `ai-coord`, `ai-handoff`, `ai-notify`, and `ai-skillet` crates.
  Keep shared Rust configuration at the workspace root (`toolkit/`) and crate behavior within its crate.
- `apps/coord-dashboard` is an independent Bun package with its own lock and package-local validation. Do not combine
  its dependencies, scripts, or build outputs with the Rust workspace.
- `xtask` is unpublished maintainer tooling for changelog validation and releases. It is not a CLI, and the installation
  recipe never installs it.
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

`just rust-check` checks formatting, Clippy with warnings denied, tests, builds, changelog consistency, and
platform-specific installation tests for the locked Rust workspace. Installation tests use mock commands and do not
install binaries. The dashboard gate checks lint, formatting, types, tests, and the production build. UI changes also
need the owning package's rendered verification. `just check` runs both gates. None of these checks installs CLI
binaries. Documentation-only edits follow the root formatting and factual-verification rules.

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

## Versioning and releases

### Model

- Each CLI has an independent SemVer version. The `[package] version` in its `Cargo.toml` is the source of truth. The
  top entry of its `CHANGELOG.md` mirrors that version.
- `CHANGELOG.md` follows [Common Changelog](https://common-changelog.org/). Write each entry in imperative mood (Add,
  Fix, Bump). Write one line per change. Give at most two references and keep the best. Do not add an Unreleased section
  or authors.
- Each release has the tag `<crate>-v<version>`, for example `ai-coord-v1.0.0`, and one GitHub release for that tag. Do
  not publish prereleases.
- Never edit a version by hand. Only `just release-prepare` changes versions.
- `just changelog-check` enforces these rules, and `just rust-check` runs it:
  - The file starts with `# Changelog`.
  - Release headings are `## [X.Y.Z] - YYYY-MM-DD`. Use stable versions only, newest first.
  - Each version is the exact next major, minor, or patch step. A `**Breaking:**` item requires a major step. An
    `### Added` group requires at least a minor step.
  - A release body has an optional single-line italic notice first. Groups follow in this order: `### Changed`,
    `### Added`, `### Removed`, `### Fixed`.
  - A group holds only one-line `- ` items. An item may start with `**Breaking:**`. Breaking items come first in the
    group.
  - Each item starts with an uppercase letter and ends with a references parenthetical. The parenthetical holds at least
    one commit link, for example ``([`abc1234`](https://github.com/PaulRBerg/agent-skills/commit/abc1234))``.
  - The file ends with one definition per release:
    `[X.Y.Z]: https://github.com/PaulRBerg/agent-skills/releases/tag/<crate>-vX.Y.Z`.

### SemVer for CLIs

- Major: a breaking change to a documented command, flag, output, exit code, hook, or persisted-data contract. This
  includes rejecting previously accepted persisted data.
- Minor: a backward-compatible new command, flag, output field, or capability.
- Patch: a fix, a performance change, or a runtime dependency bump with no contract change.

### When to release

Before a task ends, release each CLI that the task changed in a user-facing way. A change is user-facing when it changes
installed-binary behavior or a documented contract. One release may cover several commits from the task.

- Tests, internal refactors, docs, and routine dependency bumps do not trigger a release. Notable ones ride along in the
  next entry. Omit dev-only changes.
- A shared workspace change that alters runtime behavior releases every affected CLI.

### Steps

1. Commit the change normally.
2. Acquire ai-coord scopes for `toolkit/<dir>/CHANGELOG.md`, `toolkit/<dir>/Cargo.toml`, and `toolkit/Cargo.lock`. After
   `READY`, re-read the changelog.
3. Draft from the history since the tag of the current version. Run this command from `toolkit/`:
   `git log --format='%h %s' <crate>-v<current>..HEAD -- <dir> Cargo.toml Cargo.lock rust-toolchain.toml`. Include only
   commits that no entry references yet.
4. Write the entry at the top with today's date. Add its link definition at the top of the definitions.
5. Run `just release-prepare <crate>`.
6. Commit the three files with the message `Release <crate> <version>`, then push.
7. Run `just release-publish <crate>`. A rerun completes a partial publish.
8. Follow the `install-cli` rules in [Compatibility and safety](#compatibility-and-safety).

Pushing release tags and creating GitHub releases with `just release-publish` is pre-authorized, as is installation.
