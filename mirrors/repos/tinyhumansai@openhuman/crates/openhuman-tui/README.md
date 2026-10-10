# openhuman-tui

The standalone terminal client for OpenHuman, built on [ratatui]. It boots the
core inside its own process, with no HTTP server and no sockets, and gives you
four tabs (Logs, Chat, Config, Settings) plus a slash-command cockpit for
threads, models, permissions, approvals, plan review, agents, skills, MCP
servers, artifacts and Git review. Chat uses the same `web_chat` surface the
desktop app drives, so a turn here behaves like a turn in the app. It ships as
the `openhuman-tui` binary next to `openhuman-core`.

## How it works

### Startup

`main.rs` calls `init_crash_reporting()` (a Sentry client when the
`crash-reporting` feature is on) and keeps its guard alive, then calls
`run_from_cli` with the arguments. `runner.rs` does the rest, in order:

1. Loads `.env` (`embed::process::load_dotenv_for_cli`) and applies any
   startup restart delay.
2. Parses flags. `--help` prints usage and returns before anything boots; an
   unknown `-` flag is an error.
3. Sets transient provider and model overrides
   (`embed::process::set_transient_inference_overrides`).
4. Starts file-only logging under the data dir
   (`embed::process::init_for_tui`). The TUI owns the terminal, so nothing is
   written to stderr from here on.
5. Initializes the keyring master key.
6. Builds `embed::process::tokio_runtime()`, a multi-thread runtime with the
   core's `AGENT_WORKER_STACK_BYTES` stack size, so nested agent turns do not
   overflow the default 2 MiB stack.
7. Inside the runtime (`async_main`): boots the core with
   `openhuman_rpc::host::tui()` — the embed `tui` preset (every domain, no
   background services), connected to the TinyHumans backend, with the
   on-disk session store — and keeps the returned `Runtime` alive for the
   session. The screens drive it through `Runtime::core_runtime()`
   (`CoreRuntime::invoke`).

   Every domain is needed because `channel.web_chat` lives in the
   Channels domain group. `ServiceSet::none()` skips background services,
   including channel startup, so the runner registers the approval and
   artifact surface subscribers itself
   (`embed::chat_surface::register_approval_surface_subscriber`,
   `register_artifact_surface_subscriber`).
8. Picks a client id (`tui-<12 hex>`), resolves the thread, subscribes to the
   web-channel broadcast before the first turn, and hands off to `app::run`.

Thread resolution: `--thread <id>` attaches to that thread unless `--new` is
also given. `--last` or `--resume` picks the first thread from
`openhuman.threads_list`. Otherwise, or if listing fails, it creates one with
`openhuman.threads_create_new`.

### The event loop

```text
 crossterm reader thread           core (in-process)
 (event::poll every 100 ms)        web_chat broadcast
          |                               |
          | mpsc                          | broadcast::Receiver<WebChannelEvent>
          v                               v
 +--------------------- app::run: tokio::select! ----------------------+
 |  key / paste  -> handle_key -> composer, tabs, overlays, commands   |
 |  web event    -> TranscriptState::apply_event (state.rs)            |
 |  120 ms tick  -> spinner                                            |
 +-----------------------------+---------------------------------------+
                               |
                               v
                 render::draw(frame, &TranscriptState, &UiState)

 send:   runtime.invoke("openhuman.channel_web_chat",
                        { client_id, thread_id, message, queue_mode, ... })
 cancel: runtime.invoke("openhuman.channel_web_cancel",
                        { client_id, thread_id })
```

Before entering the loop, `app::run` loads the thread's existing transcript
(`openhuman.threads_transcript_get`), refreshes config, auth and agent paths,
and opens the thread picker if `--resume` was given. It then enters the
terminal through `TerminalGuard` and sends the positional prompt, if any.

Sending a message spawns a task that calls `openhuman.channel_web_chat`
through `CoreRuntime::invoke`. The reply streams back as `WebChannelEvent`s on
the broadcast channel, which `TranscriptState::apply_event` folds into the
transcript. Events for another `client_id` or thread are ignored. If the
invoke itself fails, the TUI publishes a synthetic `chat_error` so the
streaming state clears. `Enter` sends with `queue_mode: "interrupt"`; `Tab`
while a turn is streaming queues the text as a follow-up. `Esc` cancels the
in-flight turn.

Logging in or out from Settings sets `identity_changed`, and the loop starts a
new thread afterwards.

### Login

`session.rs` is the TUI's session owner. It wraps
`openhuman_tinyhumans::SessionManager` around an `InProcessLink`, a `CoreLink`
that calls `CoreRuntime::invoke` directly (no HTTP, no bearer). Login-token
exchange and `/auth/me` happen in the TUI process; the core only receives the
resulting credential through `auth.set_credential`. The Settings tab drives
it: "Log in with one-time token" takes a pasted token (zeroized on cancel),
and "Log out" asks for confirmation.

## Usage

See [Building the Rust Core](../../gitbooks/developing/building-rust-core.md)
for toolchain setup.

```bash
cargo build --manifest-path Cargo.toml -p openhuman-tui
cargo run -p openhuman-tui -- [OPTIONS] [PROMPT]
```

| Flag | Effect |
| --- | --- |
| `--thread <id>` | Attach to an existing conversation thread. |
| `--new` | Force a new thread (the default when `--thread` is omitted). |
| `--resume` | Open the saved-thread picker, starting on the latest thread. |
| `--last` | Resume the most recent thread. |
| `--no-alt-screen` | Draw in the current terminal buffer instead of the alternate screen. |
| `-p`, `--provider <id>` | Override the inference provider for this session (also `--provider-id`, `--provider=<id>`). |
| `-m`, `--model <id>` | Override the model for this session (also `--model-id`, `--model=<id>`). |
| `-v`, `--verbose` | Debug-level logging, written to the log file only. |
| `-h`, `--help` | Print usage and exit. |
| positional words | Joined into a prompt and sent right after startup. |

`OPENHUMAN_WORKSPACE` overrides the data dir (default `~/.openhuman`), which
holds the `logs/` the TUI writes to.

Keys: `Ctrl+Tab` / `Ctrl+Shift+Tab` or `Alt+1` to `Alt+4` switch tabs,
`Enter` sends, `Shift+Enter` or `Alt+Enter` inserts a newline, `Tab`
completes a command or opens the file picker, `Up`/`Down` walk composer
history, `Ctrl+R` searches it, `Ctrl+W` deletes a word, `Esc` cancels a
running turn, and `Ctrl+C` / `Ctrl+D` quit.

Slash commands (the full list with descriptions is `COMMANDS` in
[`src/composer.rs`](src/composer.rs)): `/help`, `/new`, `/resume`, `/rename`, `/delete`,
`/model`, `/permissions`, `/status`, `/usage`, `/agents`, `/skills`, `/mcp`,
`/artifacts`, `/approvals`, `/diff`, `/review`, `/copy`, `/export`, `/clear`,
`/logs`, `/config`, `/settings`, `/logout`, `/quit`. `/diff` runs `git` in the
agent's action directory and fails cleanly when that is not a repository.

## Layout

| File | What it does |
| --- | --- |
| [`src/main.rs`](src/main.rs) | Binary entry: crash reporting, then `run_from_cli`. |
| [`src/lib.rs`](src/lib.rs) | Module declarations and the public surface. |
| [`src/runner.rs`](src/runner.rs) | `run_from_cli`: flags, logging, runtime, core boot, thread resolution. |
| [`src/app.rs`](src/app.rs) | The `tokio::select!` event loop, key handling, slash commands, overlays, sending and cancelling turns, the file picker and Git diff. |
| [`src/state.rs`](src/state.rs) | `TranscriptState`, the pure reducer that folds `WebChannelEvent`s into transcript entries. No terminal or I/O dependencies. |
| [`src/ui_state.rs`](src/ui_state.rs) | `UiState`: active tab, composer, scroll, overlays, Config items and Settings actions. Pure data. |
| [`src/render.rs`](src/render.rs) | `draw`, a pure view over `TranscriptState` and `UiState`. The Logs tab reads `core::logging::tui_log_lines`. |
| [`src/composer.rs`](src/composer.rs) | The multiline composer: editing, history, command completion, and the `COMMANDS` table. |
| [`src/cockpit.rs`](src/cockpit.rs) | Overlay types (`OverlayKind`, `Overlay`, `OverlayRow`), pending approval and plan-review records, and JSON helpers; re-exports `openhuman_rpc::unwrap_rpc`. |
| [`src/controls.rs`](src/controls.rs) | Config tab edits (API URL, inference URL, default model, autonomy level, privacy mode) and Settings actions (view account, log in, log out). |
| [`src/session.rs`](src/session.rs) | `InProcessLink` and the process-wide `SessionManager`. |
| [`src/terminal.rs`](src/terminal.rs) | `TerminalGuard` (raw mode, alternate screen, mouse capture, bracketed paste) and a panic hook that restores the terminal first. |
| [`src/crash_reporting.rs`](src/crash_reporting.rs) | `init_crash_reporting`, a no-op without the `crash-reporting` feature. |
| [`tests/cli_e2e.rs`](tests/cli_e2e.rs) | Spawns the built binary to check `--help` output and that flags are validated before the core boots. |

## Key types and entry points

- `run_from_cli(args)` ([`src/runner.rs`](src/runner.rs)) is the public entry point.
- `init_crash_reporting()` ([`src/crash_reporting.rs`](src/crash_reporting.rs)) returns a
  `sentry::ClientInitGuard` that must live for the whole process.
- `TranscriptState`, `Entry`, `EntryKind` ([`src/state.rs`](src/state.rs)) are exported so the
  reducer can be tested without a terminal. `apply_event` is the single
  transition entry point.
- `app::run` ([`src/app.rs`](src/app.rs)) owns the loop; `LaunchOptions` carries the initial
  prompt, `resume_picker` and `no_alt_screen`.

## Core methods used

All calls go through `CoreRuntime::invoke`:

| Area | Methods |
| --- | --- |
| Chat | `openhuman.channel_web_chat`, `openhuman.channel_web_cancel`, `openhuman.channel_web_queue_status` |
| Threads | `openhuman.threads_list`, `openhuman.threads_create_new`, `openhuman.threads_transcript_get`, `openhuman.threads_update_title`, `openhuman.threads_delete`, `openhuman.threads_token_usage` |
| Approvals and plans | `openhuman.approval_list_pending`, `openhuman.approval_decide`, `openhuman.plan_review_decide` |
| Browsing | `openhuman.agent_list_definitions`, `openhuman.skills_list`, `openhuman.mcp_clients_installed_list`, `openhuman.ai_list_artifacts` |
| Config | `openhuman.config_get_client_config`, `openhuman.config_get_agent_paths`, `openhuman.config_update_model_settings`, `openhuman.config_get_autonomy_settings`, `openhuman.config_update_autonomy_settings`, `openhuman.config_get_privacy_mode`, `openhuman.config_set_privacy_mode` |
| Account | `openhuman.auth_get_state` (login and logout go through `session.rs`) |

## Feature flags

| Feature | Meaning |
| --- | --- |
| `crash-reporting` (default) | Forwards `openhuman-rpc/crash-reporting`. `init_crash_reporting` loads `.env`, then starts a Sentry client from `embed::process::sentry::client_options`: the shared filter chain, secret scrubbing and the core's Sentry transport, as the CLI and the desktop shell use. |
| `media`, `skills`, `flows`, `mcp`, `channels`, `scheduler-gate`, `file-logging`, `modules` (default) | The core's contributor gates, forwarded to `openhuman-rpc`. Named explicitly: they used to arrive implicitly through a bare `openhuman-core` workspace dependency. `http-server` is not in the set; the TUI never serves. |
| every other product gate, `jev`, `e2e-test-support` | Forwarded 1:1 to `openhuman-rpc`, off by default (`scripts/ci/check-feature-forwarding.mjs` checks the link). |

## Boundaries

- `openhuman-rpc` is the TUI's only OpenHuman dependency
  (`scripts/ci/check-crate-chain.mjs`). The core runs in-process through
  `host::tui`; there is no `openhuman-core` binary to spawn or connect to.
  The TUI also uses `unwrap_rpc` (strips the optional `result`/`data`
  envelopes around RPC payloads) and the `embed` facades; it does not use the
  server or the HTTP client.
- `openhuman_rpc::tinyhumans` provides the backend transport and the
  `SessionManager`; auth endpoint behavior belongs there.
- The ratatui and crossterm dependencies live only in this crate, which keeps
  the core free of terminal code.
- Chat semantics (queueing, cancellation, streaming events) belong to the
  core's `web_chat` and channel domains. The TUI only renders them.

## Gotchas

- Never print to stdout or stderr after the terminal is entered; use `log::`
  with a `[tui]` prefix, which goes to the log file. A stray `println!` corrupts
  the display.
- Subscribe to `web_chat::subscribe_web_channel_events` before the first turn.
  The runner does this before `app::run`, so streamed events of an initial
  prompt are not lost.
- With `ServiceSet::none()`, anything that normally starts as a background
  service (channel listeners, schedulers) is off. If a new surface needs
  events bridged onto the web channel, register its subscriber in
  `async_main` the way the approval and artifact subscribers are.

## Tests

Unit tests are `*_tests.rs` siblings (`state_tests.rs` needs no terminal).
[`tests/cli_e2e.rs`](tests/cli_e2e.rs) spawns the built binary.

```bash
cargo test -p openhuman-tui
```

## Packaging

`openhuman-tui` ships alongside `openhuman-core` in the CLI tarball
([`scripts/release/package-cli-tarball.sh`](../../scripts/release/package-cli-tarball.sh)) and the apt packages
([`scripts/release/build-apt-packages.sh`](../../scripts/release/build-apt-packages.sh)).

[ratatui]: https://ratatui.rs

## Further reading

- [`gitbooks/developing/architecture.md`](../../gitbooks/developing/architecture.md): architecture overview.
- [`gitbooks/developing/architecture/agent-harness.md`](../../gitbooks/developing/architecture/agent-harness.md): the agent harness.
- [`gitbooks/developing/embedding.md`](../../gitbooks/developing/embedding.md): embedding the core in another product.
- [`gitbooks/developing/building-rust-core.md`](../../gitbooks/developing/building-rust-core.md): building the Rust core.
- [`crates/README.md`](../README.md): crates overview.
- [`gitbooks/developing/testing-strategy.md`](../../gitbooks/developing/testing-strategy.md): testing strategy.
