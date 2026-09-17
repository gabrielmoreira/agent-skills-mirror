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

## Two steps: a `Runtime`, then any number of `Agent`s

The library API. Initialise one runtime — features, services, backend URL,
the TinyHumans API key — then instantiate agents on it, each fully described
and independent of the others:

```rust,no_run
use openhuman_embed::{Access, AgentSpec, McpServer, Provider, Runtime, Workspace};

# async fn demo() -> Result<(), Box<dyn std::error::Error>> {
let runtime = Runtime::builder()
    .workspace(Workspace::dir("/var/lib/my-product/openhuman"))
    .api_key("th_live_…")                     // the only credential in library mode
    .build()
    .await?;

let reviewer = runtime.agent(
    AgentSpec::new("reviewer")
        .system_prompt("You review pull requests and never edit files.")
        .access(Access::readonly())
        .skills_dir("./skills/review")        // copied into this agent's own skills root
        .action_dir("/srv/checkouts/pr-42"),
)?;

let fixer = runtime.agent(
    AgentSpec::new("fixer")
        .provider(Provider::openai_compatible("https://api.example/v1", "sk-…").model("gpt-5"))
        .access(Access::full())
        .mcp(McpServer::stdio("github", "gh-mcp", ["stdio"]))
        .action_dir("/srv/checkouts/pr-42"),
)?;

let review = reviewer.run("Summarise the risks in this change.").await?;
let fix = fixer
    .turn(format!("Address these findings:\n{}", review.reply))
    .send()
    .await?;
println!("{}", fix.reply);

// Continue a conversation with the same agent.
let again = fixer.turn("Now run the tests.").session(&fix.session_id).send().await?;
println!("{}", again.reply);
# Ok(())
# }
```

What each agent owns: its provider route and model, its access tier and
turn origin, its `action_dir`, its MCP servers, its skills root
(`<workspace>/personalities/<id>/skills/`), its system prompt, tool scope and
sandbox mode (`AgentDefinitionSpec`), its allowlists (`allowed_tools`,
`allowed_skills`), and a narrowed `DomainSet` / `ToolGroups`. Every turn is
dispatched under the agent's own `CoreContext`, so the core's config loader,
domain gate, tool-group filter and skill discovery all read that agent's
settings and never another's. Transcripts are keyed by agent id and a turn
resumes only its own thread.

What the runtime owns: the workspace and credential store, the event bus,
the keyring, the background `ServiceSet`, the registered `DomainSet` (agents
can only narrow it — enable `mcp` / `skills` at runtime build time if any
agent will use them; the default does), and the API key.

Layout under a runtime-owned root:

```text
<root>/config.toml, auth-profiles.json, core.token
<root>/workspace/session_db/, session_raw/<ts>_<agent>.jsonl, personalities/<agent>/skills/
<root>/agents/<agent>/action/                  default action_dir
```

### Authentication

Library mode has no user login. `RuntimeBuilder::api_key` installs a
TinyHumans API key into the runtime's credential store before the core boots;
managed inference then sends it as `Authorization: Bearer <key>` to the
TinyHumans OpenAI-compatible endpoint, backend REST calls send it as
`x-api-key`, and the scheduler gate treats the runtime as signed in. No
`/auth/me` round trip, no session JWT, nothing to expire. An agent that names
its own `Provider` (BYOK) never touches the key. `HarnessBuilder::session`
remains for hosts that drive backend features on behalf of a signed-in user;
the core stores that session as handed over (`auth.set_credential`) and never
validates it — obtaining and validating a JWT is the host's job (see
`crates/openhuman-session`).

### `Harness`: the one-agent shorthand

`Harness` is a `Runtime` plus exactly one `Agent` (id `harness`), built from
one set of inputs. Existing callers keep working; `harness.runtime()` and
`harness.agent()` hand out the two halves, so a host that outgrows one agent
creates more on the same runtime.

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
let second = harness
    .turn("Now list the risks.")
    .session(&first.session_id)
    .send()
    .await?;
println!("{}", second.reply);
# Ok(())
# }
```

`Core` is the typed facade shown at the top: a host that already built a
`CoreRuntime` wraps it with `Core::from_runtime` and reaches sub-facades —
`config()`, `auth()`, `agent()` (a `CoreAgent` running the orchestrator),
and, behind the `medulla` feature, `medulla()`.

### One runtime per process

The keyring master key, the RPC bearer, the global event bus and the
`Once`-guarded domain subscribers are process-scoped
(`openhuman_core::core::runtime::context::CoreContext::init` runs that
sequence), so a second runtime would silently share them while believing it
had a separate workspace. `RuntimeBuilder::build` returns
`RuntimeError::AlreadyRunning` instead; agents are the unit of multiplicity.
`Core::from_runtime` is not guarded — it only wraps a runtime the host
already built — but the same constraint applies to the `CoreRuntime` beneath
it.

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

### Still runtime-wide

These are read from the runtime's boot config by every agent today. They
are documented rather than hidden; each is a candidate follow-up in the core.

- `autonomy.auto_approve` / `auto_approve_all` and the memory guard's
  autonomy tier come from the runtime's boot config (`security::live_policy`),
  not the agent's. Path and command policy *do* use the agent's own tier.
- The approval gate is on or off process-wide; parked approvals are not
  labelled with the agent id. A per-agent "no approvals" is `Access::full()`,
  whose `TrustedAutomation` origin the gate honours per turn.
- The sub-agent catalogue is runtime-wide (built-ins plus
  `<workspace>/agents/*.toml`). Embedded agents cannot be `delegate_*`
  targets of one another. Do not reuse built-in ids (`orchestrator`,
  `summarizer`, …) for your agents.
- Sub-agents an agent spawns, the tinyagents journal and the experience store
  re-read the runtime's on-disk config rather than the agent's overlay.
- Agents sharing a workspace share the dynamic (`use_mcp_server`) MCP
  registry; `[[mcp_client.servers]]` declared through `AgentSpec::mcp` are
  per agent. The host-seeded documentation server is visible to every agent.
- `install_skill` / `create_skill` still write to `~/.openhuman`. With
  `include_user_skills(false)` (the default) an agent does not *discover* the
  operator's skills, but an install by the agent lands there.
- `AgentSpec::dedicated_memory` opens a separate memory store through the
  memory module, which a library runtime only has when its host preloads
  modules (`ServiceSet::memory_queue`). Without it the open times out; leave
  the default (shared memory, per-agent transcripts) unless the module runs.
- One API key (or session) is shared by all agents.
- `IntegrationClient` (backend-proxied Composio/search/media tools) only
  ever reads the app-session JWT (`api::jwt::get_session_token`), never the
  runtime's API key. A library runtime that authenticates with only
  `.api_key(...)` gets no integration tools at all rather than the key
  being sent as the wrong header.

Other invariants worth knowing before wiring any entry point:

- When building a `CoreRuntime` yourself, set `config_path` together with
  `workspace_dir` (`CoreBuilder::workspace(dir)` does both). Credentials,
  auth profiles and the keyring file resolve beside `config_path`, so a
  workspace-only override reads the operator's real credentials. `Runtime`
  and `Harness` set both for `Workspace::Ephemeral` and `Workspace::Dir`.
- A turn runs under the access tier *and* the turn origin. `Access::full()`
  sets both (`AutonomyLevel::Full` plus a `TrustedAutomation` origin);
  `Access::readonly()` and `Access::supervised()` set no origin and leave the
  approval gate on.
- Supply skills through `AgentSpec::skills_dir` / `HarnessBuilder::skills_dir`,
  which copy the bundles. Skill discovery rejects symlinked bundles, so
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
- `mcp` — `HttpHeader`, `McpAuthConfig`, `McpServer`, `AgentSpec::mcp` and
  `HarnessBuilder::mcp`.
- `skills` — `AgentSpec::skills_dir` and `HarnessBuilder::skills_dir`.

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

Two agents on one runtime — BYOK with the same variables as above, or managed
inference with `OPENHUMAN_EXAMPLE_TINYHUMANS_API_KEY`:

```bash
OPENHUMAN_EXAMPLE_BASE_URL=https://api.openai.com/v1 \
OPENHUMAN_EXAMPLE_API_KEY=sk-… \
OPENHUMAN_EXAMPLE_MODEL=gpt-5 \
  cargo run -p openhuman-embed --example two_agents -- "Describe this directory."

# Or managed inference, no BYOK endpoint needed:
OPENHUMAN_EXAMPLE_TINYHUMANS_API_KEY=th_… \
  cargo run -p openhuman-embed --example two_agents -- "Describe this directory."
```

The repository-root `examples/embed_headless.rs` (`DomainSet::harness()`,
`ServiceSet::none()`, RPC through `CoreRuntime::invoke`) and
`examples/embed_kernel.rs` (`DomainSet::kernel()`, then opt one family back
in) drive `CoreBuilder` from `openhuman_core` directly, without this crate;
they are `[[example]]` entries of the `openhuman` package, so run them with
`cargo run --example embed_headless`.

`tests/harness_embed.rs` is the end-to-end proof that `Harness` runs a real
turn against a `wiremock` provider with nothing bound;
`tests/runtime_agents.rs` runs three agents with different providers, access
tiers, skills, MCP servers and working directories on one runtime and shows
the API key reaching a mocked managed backend as a bearer;
`tests/public_api.rs` pins the host-facing embedding contract at compile
time. Run them with `cargo test -p openhuman-embed --features inference,mcp,skills`.

## Relationship to other crates

Its only in-repo dependency is `openhuman-core` (package `openhuman`) with
`default-features = false` — every capability comes from a feature forwarded
above. It does not depend on `openhuman-rpc` directly; the shared
`RpcOutcome` and `StructuredRpcError` types reach it through
`openhuman_core::rpc`. `openhuman-app` and `openhuman-tui` depend on
`openhuman-rpc` for its HTTP client and on `openhuman-core`; neither uses
`openhuman-embed`.
