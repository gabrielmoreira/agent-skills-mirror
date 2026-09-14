# `openhuman-tui`

`openhuman-tui` is the standalone terminal client, embedding the core
in-process. It is a [ratatui]-based agent cockpit with Chat, Logs, Config, and
Settings tabs, persistent thread resume, command/file pickers, approvals, plan
review, task/goal/agent/skill/MCP/artifact views, Git review, and a multiline
composer. Chat uses the same `web_chat` surface the desktop app drives
(`openhuman.channel_web_chat` / `openhuman.channel_web_cancel` +
`web_chat::subscribe_web_channel_events`). It boots the core in-process — no
HTTP, no sockets — via
`CoreBuilder::new(HostKind::Cli).domains(DomainSet::full()).services(ServiceSet::none())`
and streams a live transcript in the terminal.

## Run / build

See [Building the Rust Core](../../gitbooks/developing/building-rust-core.md)
for toolchain setup.

```bash
cargo build --manifest-path Cargo.toml -p openhuman-tui
cargo run -p openhuman-tui -- [OPTIONS] [PROMPT]
```

| Flag | Effect |
| --- | --- |
| `--thread <id>` | Attach to an existing conversation thread. |
| `--new` | Force a new thread (default when `--thread` is omitted). |
| `--resume` | Open the saved-thread picker (starts on the latest thread). |
| `--last` | Resume the most recent thread. |
| `--no-alt-screen` | Draw in the current terminal buffer. |
| `-p`, `--provider <id>` | Override the inference provider for this session (also `--provider-id`, `--provider=<id>`). |
| `-m`, `--model <id>` | Override the model for this session (also `--model-id`, `--model=<id>`). |
| `-v`, `--verbose` | Debug-level logging, written to the log file and never the UI (the TUI owns the terminal). |
| `-h`, `--help` | Print usage and exit. |
| a positional prompt | Sent immediately after startup. |

Any other `-`-prefixed argument is rejected before the core boots.

`Ctrl+Tab`/`Alt+1-4` switch tabs, `/` opens the command picker (see
`COMMANDS` in `src/composer.rs` for the full list), `Enter` sends,
`Shift+Enter` inserts a newline, `Ctrl+C`/`Ctrl+D` quit.

## Feature flags

- `crash-reporting` (default on) — pulls in `sentry` and `dotenvy`, forwards
  `openhuman-core/crash-reporting`, and makes `init_crash_reporting` install a
  Sentry client and panic integration before the TUI takes over the terminal.
  Without it, `init_crash_reporting` compiles to a no-op at the same call
  site.

## Crate relationships

- Depends on `openhuman-core` directly and runs it in-process — there is no
  need to spawn or connect to an `openhuman-core` binary.
- Depends on `openhuman-rpc` only for `unwrap_rpc` (re-exported from
  `src/cockpit.rs`), which strips the optional `result`/`data` envelopes core
  RPC handlers wrap around their payloads before the TUI reads them.
- The ratatui/crossterm terminal dependencies live only in this crate.
  `crates/openhuman-core/Cargo.toml` calls this out explicitly: "The
  terminal-specific ratatui/crossterm cohort lives in the separate
  `openhuman-tui` package," keeping the shared core free of UI dependencies.

## Module map

| File | Purpose |
| --- | --- |
| `app.rs` | Terminal chat event loop — bridges keyboard input, the web-channel broadcast, and a spinner ticker over `tokio::select!`. |
| `cockpit.rs` | OpenHuman-native overlays and structured control-plane state. |
| `composer.rs` | Keyboard-first, terminal-independent chat composer. |
| `controls.rs` | Config and account actions for the tabbed terminal UI. |
| `crash_reporting.rs` | Crash-reporting client ownership for the standalone terminal binary. |
| `render.rs` | Ratatui rendering — a pure view over `TranscriptState` + `UiState`. |
| `runner.rs` | CLI entry point (`run_from_cli`) — flag parsing, logging setup, and core boot. |
| `state.rs` | Pure, terminal-free transcript reducer for the Chat tab. |
| `terminal.rs` | Terminal setup/teardown with panic-safe restoration. |
| `ui_state.rs` | Pure navigation and form state for the four terminal pages. |

## Tests

Unit tests sit beside each module. The `state.rs` reducer tests run without a
terminal since `TranscriptState` has no ratatui/crossterm/IO dependencies.
`tests/cli_e2e.rs` covers process-boundary behavior (`--help` output, flag
validation before the core boots) by spawning the built binary.

```bash
cargo test -p openhuman-tui
```

## Packaging

`openhuman-tui` ships as the `openhuman-tui` binary alongside `openhuman-core`
in the CLI tarball (`scripts/release/package-cli-tarball.sh`) and the apt
packages (`scripts/release/build-apt-packages.sh`).

[ratatui]: https://ratatui.rs
