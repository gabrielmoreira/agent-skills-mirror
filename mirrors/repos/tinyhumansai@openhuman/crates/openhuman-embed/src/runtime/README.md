# runtime

The first of the two-step library API described in the crate README:
initialize one `Runtime`, then put any number of independently configured
agents on it. See [`gitbooks/developing/embedding.md`](../../../../gitbooks/developing/embedding.md)
for the walkthrough and [`gitbooks/developing/performance.md`](../../../../gitbooks/developing/performance.md)
for what running many agents on one runtime costs in memory.

## Contents

- `mod.rs`: `Runtime` itself: `agent()` to instantiate an `Agent` from an
  `AgentSpec`, `agent_ids()`, `core()` for non-turn access (config, auth),
  `root_dir()` / `workspace_dir()`, and the process-scoped `CoreGuard` that
  tears the embedded core down (and, for an ephemeral workspace, deletes it)
  once the last `Runtime` or `Agent` handle referencing it drops.
- `builder.rs`: `RuntimeBuilder`: workspace choice, feature/service/domain
  selection, provider and access defaults, and `api_key()` for managed
  TinyHumans inference.
- `api_key.rs`: `ApiKey`, the newtype the builder stores the TinyHumans key
  as before it reaches the credential store.

## What is runtime-wide versus per-agent

The runtime owns everything process-scoped in the core: the event bus, the
keyring and credential store, the RPC bearer, the background `ServiceSet`,
the compiled `DomainSet`, and the API key. An agent owns everything the core
reads through its own ambient context: its `Config` (provider route, model,
MCP servers, autonomy tier, `action_dir`), its `AgentDefinition` (system
prompt, tool scope, sandbox mode), its skills root, and its narrowed
`DomainSet` and `ToolGroups`. A handful of settings, such as
`autonomy.auto_approve` and the memory guard's autonomy tier, are still read
from the runtime's boot config by every agent regardless of its own
overlay; see the crate README's "still runtime-wide" list before assuming an
agent-level override reaches them.

## One runtime per process

`CoreContext::init` seeds the process-scoped state exactly once.
`RuntimeBuilder::build` returns `RuntimeError::AlreadyRunning` for a second
runtime rather than letting two runtimes share a keyring and event bus while
each believes it owns a separate workspace. Agents, not runtimes, are the
unit of multiplicity: build one runtime and put every agent the host needs on
it with `Runtime::agent`.

## The tokio runtime is the host's job

An agent turn is a deep async state machine, and delegating to a sub-agent
nests another one inside it. Build the host's tokio runtime with
`AGENT_WORKER_STACK_BYTES` and `MAX_BLOCKING_THREADS`
(`openhuman_core::core::runtime`) or the default 2 MiB worker stack can
overflow.

## Where to look next

- [`../agent/README.md`](../agent/README.md): what `Runtime::agent` builds.
- [`../harness/README.md`](../harness/README.md): the one-agent shorthand
  built on top of a `Runtime` and an `Agent`.
- `openhuman-tinyhumans`'s `RuntimeBuilder` extension
  (`crates/openhuman-tinyhumans/src/lib.rs`) boots a runtime already connected
  to the hosted backend; see
  [`gitbooks/developing/tinyhumans-api-key.md`](../../../../gitbooks/developing/tinyhumans-api-key.md).
