# `openhuman-app`

Thin Tauri v2 desktop host for OpenHuman on Windows, macOS, and Linux (Wry
webview; no CEF). It links `openhuman_core` in-process and runs the core's
HTTP/JSON-RPC server as a tokio task (`core_process.rs`) instead of spawning a
sidecar binary — the core's lifetime is tied to the GUI process. Identities:
Cargo package `openhuman-app`, library `openhuman`, binary `OpenHuman`. Only
the Cargo package was renamed for the `crates/` layout; the library and
executable names are shipped identities and are unchanged.

See [`gitbooks/developing/architecture/tauri-shell.md`](../../gitbooks/developing/architecture/tauri-shell.md)
for the full IPC command reference, window/tray behavior, and UI-to-core
data flow. This README covers what is specific to building and depending on
this crate.

## Separate Cargo world

The root `Cargo.toml` `exclude`s this directory: this crate has its own
`Cargo.lock` and `target/`, so root-only Cargo commands never resolve
GTK/WebKit/Tauri. Build and check it explicitly:

```bash
cargo check --manifest-path crates/openhuman-app/Cargo.toml
pnpm dev:app
pnpm build
```

Its `[patch]` tables mirror the root manifest's entries (`tinymemory-api`,
`tinyinference`, `motosan-ai-oauth`, `tinyflows`, `tinychannels`) and add a
`tinytools` path patch matching the core crate's path dependency. Keep them in
sync with the root `Cargo.toml`: drift resolves two copies of the same crate
as distinct Rust types.

## Crate relationships

- **`openhuman-rpc`** (`http-client` feature): `core_rpc.rs` re-exports
  `bearer_header` (as `relay_bearer_header`), `redact_url_for_log`, and
  `HttpRpcResponse` (as `RelayHttpResponse`) crate-wide, and wraps
  `openhuman_rpc::post_json_rpc` for the `relay_http_rpc` command, which the
  frontend's `coreRpcClient` uses only when `rpcUrlNeedsShellRelay()` says a
  non-loopback plain-`http://` runtime would be blocked as mixed content
  (#3865); loopback and `https://` URLs are fetched directly from the webview.
- **`openhuman_core`** (path dependency, package `openhuman`,
  `default-features = false`): the embedded core does not inherit the core
  crate's default feature set, so every product gate
  (`channels`, `media`, `inference`, `voice`, `web3`, `documents`, `modules`,
  `flows`, `skills`, `mcp`, `crash-reporting`, `http-server`,
  `scheduler-gate`, `file-logging`, `contacts`, `runtime-node`, `hosting`)
  must be forwarded explicitly in `Cargo.toml`. A gate missing from that list
  vanishes from the shipped app silently — no build error, no test failure.
  `scripts/ci/check-feature-forwarding.mjs` compares this list against
  `scripts/ci/product-features.txt` and fails CI on drift.
- `lib.rs` carries two `const _: () = assert!(...)` guards
  (`VOICE_COMPILED_IN`, `HTTP_SERVER_COMPILED_IN`) that fail the build if
  `voice` or `http-server` is ever dropped from the forwarded list — both
  failure modes are otherwise silent and runtime-only.

## Feature flags

Shell-local gates from `[features]` in `Cargo.toml`. These are unrelated to
the `openhuman_core` product-feature forwarding above and do not belong in
`scripts/ci/product-features.txt`.

| Feature | Meaning |
| --- | --- |
| `gateways` (default) | Routing the frontend to a core in a Docker container, over SSH, or both, via `tinybox`. |
| `custom-protocol` | Serve the bundled `frontendDist` via `tauri://localhost` instead of the Vite dev server. Set automatically by `cargo tauri build`; never add to `default`. |
| `sandbox-bubblewrap` | Empty in this crate (`= []`); it does not forward `openhuman_core/sandbox-bubblewrap`, so enabling it here changes nothing. |
| `e2e-test-support` | Forwards `openhuman_core/e2e-test-support` to expose `openhuman.test_reset`. Flipped on by the E2E build (`app/scripts/e2e-build.sh`). |

## Entry points

- `openhuman::run()` — starts the Tauri application (window, tray, plugins,
  embedded core).
- `openhuman::run_core_from_args(args)` — dispatches directly into
  `openhuman_core`'s CLI without shelling out to a separate binary.
- `main.rs` routes `OpenHuman core <args>` and `OpenHuman mcp` /
  `OpenHuman mcp-server` to `run_core_from_args`; everything else starts the
  GUI via `run()`.

## Module map

| Area | Modules |
| --- | --- |
| Core lifecycle | `core_process.rs`, `core_rpc.rs`, `process_kill.rs`, `process_recovery.rs`, `workspace_paths.rs` |
| Gateways (feature-gated) | `gateway/` (`types`, `store`, `ops`, `provision`, `registry`, `commands`) |
| Platform integration | `deep_link_ipc.rs` (Linux), `deep_link_ipc_windows.rs`, `deep_link_registration_check.rs`, `native_notifications/`, `imessage_scanner/` (macOS `chat.db` reader), `mascot_native_window.rs` and `notch_window.rs` (macOS), `ptt_hotkeys.rs`/`ptt_overlay.rs`, `dictation_hotkeys.rs`, `window_state.rs` |
| Updates / reset | `app_update.rs`, `local_data_reset.rs`, `reset_reboot_schedule.rs` (Windows) |
| Misc | `artifact_commands.rs`, `claude_code.rs`, `mcp_commands.rs`, `loopback_oauth.rs`, `directory_picker.rs`, `file_logging.rs`, `stderr_panic_hook.rs` |

## Tests

Behavior tests are `*_tests.rs` siblings: `lib_tests.rs`,
`core_process_tests.rs`, `local_data_reset_tests.rs`, and
`gateway/{ops,registry,store,types}_tests.rs`. Because this crate is outside
the root workspace, `pnpm test:rust` (`scripts/test-rust-with-mock.sh`, which
runs `cargo test --manifest-path Cargo.toml --workspace`) does not reach them.
Run them directly, as CI does (`.github/workflows/test-reusable.yml`):

```bash
cargo test --manifest-path crates/openhuman-app/Cargo.toml
```

## Rules

- Keep this crate thin. New behavior belongs in Rust-side IPC hooks, not
  JavaScript injected into child webviews — audit new Tauri plugins for
  `js_init_script`.
- The `generate_handler!` call in `lib.rs` is the authoritative IPC command
  list.
- Do not restore CEF or CDP-scanner assumptions; the app runs on Wry. The
  native iMessage scanner stays separate because it reads `chat.db` directly.
