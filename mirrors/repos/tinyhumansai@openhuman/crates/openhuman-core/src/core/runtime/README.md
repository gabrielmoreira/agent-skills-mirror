# core/runtime

The embeddable composition surface: `CoreBuilder` → `CoreRuntime`. This is
what `openhuman-embed`'s `Harness` and the standalone `openhuman-core`
binary both build on to host the core without duplicating
`run_server_inner`.

## Two-phase model

1. **`CoreBuilder::build()` — initialization only.** Registers controllers,
   loads the master key, seeds the RPC bearer, initializes the
   workspace-bound stores, and runs the pure-registration part of
   `bootstrap_core_runtime`. No port is bound. After `build()` returns,
   `CoreRuntime::invoke` can dispatch any RPC method in-process and agent
   turns can run — a harness-only embedder using `ServiceSet::none()` needs
   nothing more.
2. **`CoreRuntime::serve()` — transport + background services.** Binds the
   HTTP listener (when `ServiceSet::rpc_http` is set), mounts the router,
   fires the readiness signal, spawns the selected background services, and
   serves until shutdown. When `rpc_http` is unset it just spawns the
   selected background services and returns immediately — the caller owns
   the process lifetime. In a build compiled without the `http-server`
   feature, requesting `rpc_http` returns an `Err` rather than silently
   binding nothing.

`CoreRuntime::invoke(method, params)` dispatches an RPC method in-process
through `jsonrpc::invoke_method` — the same path the HTTP `/rpc` handler and
the CLI use, wrapped in `CoreContext::scope` so the ambient context resolves
correctly. `openhuman_embed::Harness` goes through this call, never through
domain operations directly.

## `ServiceSet` — which background services and transports run

Each flag is independent. Presets:

| Preset | Shape |
| --- | --- |
| `ServiceSet::desktop()` | Everything on — the Tauri shell and standalone `openhuman-core run`. |
| `ServiceSet::headless_api()` | HTTP JSON-RPC only (`rpc_http`) — no Socket.IO, cron, channels, or heartbeat; a single-core cloud/server deployment. |
| `ServiceSet::none()` | No transport, no background services — a library/harness embedder driving only `CoreRuntime::invoke`. |
| `ServiceSet::embedded()` | No transport (`rpc_http: false`), but the background work a long-lived embedded session expects: cron, heartbeat, memory queue, harness init, skill catalog refresh, memory sync. `socketio`/`channels` stay off because such a host reads state through the facade and owns its own networking. |

Individual services still honor their own runtime gates inside
`runtime/services.rs` regardless of `ServiceSet` selection: `cron` checks
`config.cron.enabled`; `channels` returns early on
`OPENHUMAN_DISABLE_CHANNEL_LISTENERS=1` or when
`config.channels_config.has_listening_integrations()` is false; `heartbeat`
(`spawn_login_gated_services`) defers the login-gated services until a user
session exists on disk. `ServiceSet` picks *whether a service is spawned at
all*; the gate picks *whether it runs for this user*.

## `DomainSet` — which domain families exist at runtime

Sibling of `ServiceSet`: where `ServiceSet` selects background services and
transports, `DomainSet` selects which controller/tool/store/subscriber
surfaces are live, one flag per `DomainGroup` (see
[`../all.rs`](../all.rs)'s `DomainGroup` for the full family list and the
harness/gate/platform split). `DomainSet::allows(group)` is the query the
registry filters on.

| Preset | Shape |
| --- | --- |
| `DomainSet::full()` | Every family on — today's default, byte-identical to registration with no runtime narrowing. |
| `DomainSet::harness()` | `agent` + `memory` + `threads` + `config` + `security` only; every gate family and `platform` off. The embeddable agent core (`examples/embed_headless.rs`). |
| `DomainSet::embedded()` | The harness families plus `medulla`, `flows` (the engine `medulla_workflows` runs on; boot reconciliation keys off `ctx.domains().flows`), `skills`, `channels` (`channel.web_chat` is tagged `Channels` and is how an embedded host drives chat turns), `inference`, `integrations`, `automation`, `runtimes`, and `platform`. `mcp`/`web3`/`voice`/`media`/`desktop`/`hosted`/`modules` stay off — an embedded host supplies its own routing and presentation. |
| `DomainSet::kernel()` | The floor: `threads` + `config` + `security` only. Distinct from `none()` — this is "opt a subsystem back in from nothing," so `agent` and `memory` (the two largest, most replaceable subsystems) are deliberately off. See `examples/embed_kernel.rs`. |
| `DomainSet::none()` | Every family off. |

## `TokenSource` — how the RPC bearer is seeded

- `TokenSource::Fixed(Arc<String>)` — an in-memory bearer supplied by the
  embedder (the Tauri shell's `CoreProcessHandle.rpc_token`), seeded via
  `auth::init_rpc_token_with_value`; never crosses the process environment.
- `TokenSource::EnvOrFile` — the standalone fallback: read
  `OPENHUMAN_CORE_TOKEN` from the environment if present, otherwise generate
  a fresh token and write `{root}/core.token` (0o600 on Unix).

## `CoreBuilder` setters

`CoreBuilder::new(host_kind)` defaults to `TokenSource::EnvOrFile`,
`ServiceSet::desktop()`, `DomainSet::full()`, and `ToolGroups::default()`
(every group withheld behind `use_skill`, the desktop app's shape). The
three capability axes only narrow — a group set to `Advertised` whose tools
are compiled out, or whose `DomainGroup` is off, stays absent.

- `.services(ServiceSet)`, `.domains(DomainSet)`, `.tool_groups(ToolGroups)`
  — the three independent narrowing axes: which services run, which domain
  families exist, and how the tools of the families that do exist are
  disclosed (advertised on the wire, withheld behind the pack proxy, or not
  registered at all).
- `.token(TokenSource)`, `.host(impl Into<String>)`, `.port(u16)`.
- `.config(Config)` — supply the config outright instead of letting
  `build()` discover one from `config.toml` + environment; used verbatim, no
  env overlay applied automatically.
- `.workspace(dir)` — sugar over `.config()`: roots `workspace_dir` at `dir`
  and sets `config_path` to `dir/config.toml` so credentials and sessions
  resolve beside the workspace rather than a previous config root.
- `.action_dir(dir)` — sugar over `.config()` for the agent's read/write
  root.
- `.backend_url(url)`.

## `CoreContext` and initialization order

`runtime/context.rs`'s `CoreContext` owns the core's initialization
*order*: register controllers, load the master key, seed the RPC bearer,
initialize the workspace-bound stores, and run the pure-registration part of
`bootstrap_core_runtime`. `init_stores` gates each store on its owning
`DomainGroup` via `StoreInitPlan` — the memory driver binding (`Memory`), the
image-attachment sidecar dir (`Agent`), and the legacy-workflow prune
(`Skills`) — while the keyring-path log and the boot-time Sentry user bind run
unguarded for every `DomainSet`. The WhatsApp store moved to the Tauri
shell and the people store is owned by the bound memory driver, so neither
is seeded here. It also
holds the `DomainSet` for its scope and, when supplied, the embedder's
`Config` — RPC handlers otherwise re-resolve config independently per
dispatch, so an embedder-supplied config would be silently ignored without
this seam.

The "wrong-workspace guard" (Sentry OPENHUMAN-CORE-48 / TAURI-RUST-8NM)
lives in `CoreContext::init_with_config`: when no config was supplied and
`Config::load_or_init()` fails, it logs an error and skips `init_stores`
entirely — memory stays explicitly uninitialised for the run and callers get
a "memory client not ready" error — rather than falling back to
`Config::default()` and seeding stores against the wrong workspace.

`CoreContext::scope(ctx, fut)` establishes the ambient context for the
duration of a future (used at the `try_invoke_registered_rpc` chokepoint and
by `CoreRuntime::invoke`); `CoreContext::current` falls back to a
process-wide default context when no scope is active, which is what lets
existing single-tenant call sites keep working unmodified.

## Shared tokio tuning constants

`runtime/mod.rs` declares two constants every multi-thread runtime that may
host an agent turn must set:

- `AGENT_WORKER_STACK_BYTES` (16 MiB) — a single agent turn is a very large
  async state machine (system prompt + hundreds of tool specs + the nested
  provider/tool loop), and delegating to a sub-agent nests another one. That
  overflows tokio's default 2 MiB worker stack and aborts the process.
- `MAX_BLOCKING_THREADS` (64) — tokio defaults this to 512, which combined
  with the raised stack size could pin up to `512 × 16 MiB` of idle stack.
  `spawn_blocking` on these runtimes backs SQLite, filesystem grep/glob,
  document parsing, and URL guarding: bounded, bursty concurrency, so 64
  leaves headroom while capping the idle footprint.

## Related docs

- [../README.md](../README.md) — the rest of `core/`: dispatch, registry,
  event bus, transport, CLI.
