# `openhuman-embed`

`openhuman-embed` is the host-facing library package for products that run the
OpenHuman core in-process, including Medulla and OpenCompany. It re-exports the
runtime builder from `openhuman-core` and owns the typed embedding facade.

Use the default contributor feature set:

```toml
[dependencies]
openhuman-embed = { git = "https://github.com/tinyhumansai/openhuman", package = "openhuman-embed" }
```

Or select a narrow host build:

```toml
[dependencies]
openhuman-embed = { git = "https://github.com/tinyhumansai/openhuman", package = "openhuman-embed", default-features = false, features = ["inference", "mcp"] }
```

```rust,no_run
use std::sync::Arc;

use openhuman_embed::{Core, CoreBuilder, DomainSet, HostKind, ServiceSet};

# async fn run() -> Result<(), Box<dyn std::error::Error>> {
let runtime = CoreBuilder::new(HostKind::Library)
    .domains(DomainSet::embedded())
    .services(ServiceSet::none())
    .build()
    .await?;
let core = Core::from_runtime(Arc::new(runtime));
let flags = core.config().runtime_flags().await?;
println!("log_prompts={}", flags.log_prompts);
# Ok(())
# }
```

Embedding products should set their product identity once during startup,
before constructing backend clients:

```rust
use openhuman_embed::{set_product_identity, ProductIdentity};

if let Some(identity) = ProductIdentity::new("opencompany") {
    set_product_identity(identity);
}
```

Use `Core::raw()` only as a temporary escape hatch when the typed facade does
not yet model a required call. A repeated raw call is a candidate for a typed
embedding method in `openhuman-embed`.

## Two entry points

`Harness` builds its own runtime from typed inputs — the right choice for a
host that has no `CoreRuntime` of its own yet:

```rust,no_run
use openhuman_embed::{Access, Harness, Provider, Workspace};

# async fn demo() -> Result<(), Box<dyn std::error::Error>> {
let harness = Harness::builder()
    .provider(Provider::openai_compatible("https://api.example/v1", "sk-…").model("gpt-5"))
    .workspace(Workspace::Ephemeral)
    .access(Access::readonly())
    .build()
    .await?;

let first = harness.run("Summarize what you can see.").await?;
println!("{}", first.reply);

let second = harness
    .turn("Now list the risks.")
    .session(&first.session_id)
    .send()
    .await?;
println!("{}", second.reply);
# Ok(())
# }
```

`Core` is the typed facade shown above: a host that already built a
`CoreRuntime` wraps it with `Core::from_runtime` and reaches sub-facades —
`config()`, `auth()`, `agent()`, and, behind the `medulla` feature,
`medulla()`.

Only one `Harness` may run per process. The keyring master key, the RPC
bearer, the global event bus and the `Once`-guarded domain subscribers are
process-scoped (`openhuman_core::core::runtime::context::CoreContext::init`
runs that sequence), so a second harness would silently share them while
believing it had a separate workspace. `HarnessBuilder::build` returns
`HarnessError::AlreadyRunning` instead. `Core::from_runtime` is not guarded —
it only wraps a runtime the host already built — but the same constraint
applies to the `CoreRuntime` beneath it.

Build the tokio runtime yourself — a turn is a large async state machine that
overflows tokio's default 2 MiB worker stack once a sub-agent nests inside it —
using `AGENT_WORKER_STACK_BYTES` and `MAX_BLOCKING_THREADS` from
[`openhuman_core::core::runtime`](../openhuman-core/src/core/runtime/README.md):

```rust,no_run
use openhuman_core::core::runtime::{AGENT_WORKER_STACK_BYTES, MAX_BLOCKING_THREADS};

let runtime = tokio::runtime::Builder::new_multi_thread()
    .enable_all()
    .thread_stack_size(AGENT_WORKER_STACK_BYTES)
    .max_blocking_threads(MAX_BLOCKING_THREADS)
    .build()
    .expect("tokio runtime");
```

Other invariants worth knowing before wiring either entry point:

- When building a `CoreRuntime` yourself, set `config_path` together with
  `workspace_dir` (`CoreBuilder::workspace(dir)` does both). Credentials,
  auth profiles and the keyring file resolve beside `config_path`, so a
  workspace-only override reads the operator's real credentials. `Harness`
  sets both for `Workspace::Ephemeral` and `Workspace::Dir`.
- A turn runs under the access tier *and* the turn origin. `Access::full()`
  sets both (`AutonomyLevel::Full` plus a `TrustedAutomation` origin);
  `Access::readonly()` and `Access::supervised()` set no origin and leave the
  approval gate on.
- Supply skills through `HarnessBuilder::skills_dir`, which copies the
  bundles into the workspace. Skill discovery rejects symlinked bundles, so
  linking them in does not work.

## Feature flags

Every feature on this crate is a pass-through to the same-named feature on
`openhuman-core` (package `openhuman`): `default`, `http-server`,
`inference`, `documents`, `hosting`, `modules`, `voice`, `web3`,
`runtime-node`, `contacts`, `media`, `flows`, `skills`, `mcp`,
`crash-reporting`, `medulla`, `channels`, `sandbox-landlock`,
`sandbox-bubblewrap`, `peripheral-rpi`, `browser-native`, `whatsapp-web`,
`file-logging`, `scheduler-gate`.

Three of them also gate items on this crate's own public surface:

- `medulla` — `Core::medulla()`, `HarnessCore::medulla()`, and the Medulla
  session types (`Medulla`, `MedullaStatus`, `SessionSummary`,
  `SessionDetail`, `SessionCreated`, `Message`, `SendResult`, `AbortResult`,
  `RosterWorker`, `WireEventEnvelope`).
- `mcp` — `HttpHeader`, `McpAuthConfig`, `McpServer` and
  `HarnessBuilder::mcp`.
- `skills` — `HarnessBuilder::skills_dir`.

See [`docs/library-minimal-recipe.md`](../../docs/library-minimal-recipe.md)
for a measured minimal-footprint feature set.

## Examples and tests

```bash
# Against any OpenAI-compatible endpoint:
OPENHUMAN_EXAMPLE_BASE_URL=https://api.openai.com/v1 \
OPENHUMAN_EXAMPLE_API_KEY=sk-… \
OPENHUMAN_EXAMPLE_MODEL=gpt-5 \
  cargo run -p openhuman-embed --example run_turn -- "What can you see in this directory?"

# Or against the machine's own configured inference, in its real workspace:
OPENHUMAN_EXAMPLE_INHERIT=1 cargo run -p openhuman-embed --example run_turn -- "Hello."
```

Optional: `OPENHUMAN_EXAMPLE_BACKEND_URL` points non-inference backend calls
somewhere specific, and `OPENHUMAN_EXAMPLE_SKILLS_DIR` supplies skill bundles.

The repository-root `examples/embed_headless.rs` (`DomainSet::harness()`,
`ServiceSet::none()`, RPC through `CoreRuntime::invoke`) and
`examples/embed_kernel.rs` (`DomainSet::kernel()`, then opt one family back
in) drive `CoreBuilder` from `openhuman_core` directly, without this crate;
they are `[[example]]` entries of the `openhuman` package, so run them with
`cargo run --example embed_headless`.

`tests/harness_embed.rs` is the end-to-end proof that `Harness` runs a real
turn against a `wiremock` provider with nothing bound; `tests/public_api.rs`
pins the host-facing embedding contract at compile time. Run them with
`cargo test -p openhuman-embed`.

## Relationship to other crates

Its only in-repo dependency is `openhuman-core` (package `openhuman`) with
`default-features = false` — every capability comes from a feature forwarded
above. It does not depend on `openhuman-rpc` directly; the shared
`RpcOutcome` and `StructuredRpcError` types reach it through
`openhuman_core::rpc`. `openhuman-app` and `openhuman-tui` depend on
`openhuman-rpc` for its HTTP client and on `openhuman-core`; neither uses
`openhuman-embed`.
