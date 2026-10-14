# ai-handoff

`ai-handoff` is a stateless Rust workspace member. It runs native `git` as a subprocess for repository discovery and
ignore checks. Do not introduce libgit2 or persisted CLI state.

## Architecture

- `src/cli.rs` defines the public command line. `src/error.rs` and `src/main.rs` map failures to stable exit classes.
- `src/create.rs` validates handoff metadata and publishes new handoffs atomically.
- `src/clipboard.rs` selects the desktop clipboard backend and verifies copied commands byte-for-byte.
- `src/archive.rs` moves completed handoffs into the user archive.
- `src/git.rs` is the only subprocess boundary for Git operations.

## Invariants

- Frontmatter has exactly the six documented keys in contract order.
- Creation never overwrites a target or traverses symlinked handoff directories.
- Failed creation removes its staged file, published target, and any directories created by that invocation.
- Tests isolate repositories, `HOME`, clipboard commands, and archive storage in temporary directories.

## Validation

From `toolkit/`, run the narrowest relevant `cargo test -p ai-handoff` filter first, then `just rust-check` for the
aggregate Rust gate.

## CLI reference

`ai-handoff` creates immutable task-handoff Markdown files. It emits the exact Codex launch command for them. It
archives completed handoffs without changing the rest of a document.

### Installation

Installation requires Git, Cargo, and the rolling Rust nightly toolchain:

```sh
cargo install --git https://github.com/PaulRBerg/agent-skills ai-handoff --locked --root "$HOME/.local"
```

For local development, install the current checkout instead:

```sh
cargo install --path . --locked --force --root "$HOME/.local"
```

`ai-handoff` supports macOS and Linux. On macOS, clipboard copying requires `pbcopy` and `pbpaste`. On Linux, it prefers
`wl-copy` and `wl-paste` from `wl-clipboard` when `WAYLAND_DISPLAY` is nonempty and both tools are executable.
Otherwise, it uses `xclip` when `DISPLAY` is nonempty and `xclip` is executable. Use `--no-clipboard` on headless
systems or when clipboard tools are unavailable.

### Commands

```text
ai-handoff create [--check] --repo <dir>... [--launch-repo <dir>]
                  --category <category> --task <task> [--draft <body.md>]
                  [--before-work-skill <dir>] [--no-clipboard] <FILENAME.md>
ai-handoff archive <handoff-path>
```

`create` canonicalizes and deduplicates Git worktrees. ai-handoff publishes a single-repository handoff below that
repository's ignored `.ai/task-handoffs/` directory. It publishes a cross-repository handoff below
`$HOME/Desktop/.ai/task-handoffs/` and requires an explicit launch repository plus a `## Repository order` section.
Cross-repository creation requires a physical `$HOME/Desktop` directory on both supported operating systems. Publication
descends through no-follow directory handles. It is atomic and never overwrites a target. Unless `--no-clipboard` is
passed, ai-handoff copies the launch command through the selected clipboard backend and verifies the exact bytes.
Clipboard failures remove the published handoff and any directories created by that invocation.

Except with `--check`, `--draft` is required. That check validates placement without reading a draft or writing files.
`--before-work-skill` requires an absolute directory with a readable `SKILL.md`. It appends an instruction to the
generated Codex prompt to load that skill before any task work.

Generated handoff files abbreviate every occurrence of the active home directory as `~`. Reported paths and launch
commands remain absolute.

`archive` moves a handoff to `$HOME/.local/share/task-handoffs/archive/<origin>/`, adding a UTC timestamp when the name
is occupied.
