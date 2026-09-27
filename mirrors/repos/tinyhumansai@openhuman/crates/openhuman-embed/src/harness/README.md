# harness

`Harness`: the one-call front door over the library API in
`../runtime/` and `../agent/`. One `Runtime` plus exactly one `Agent` named
`harness`, built from a single set of inputs. See
[`gitbooks/developing/embedding.md`](../../../../gitbooks/developing/embedding.md)
for the full walkthrough; reach for `Runtime` and `AgentSpec` directly once a
host needs more than one agent.

## Contents

- `mod.rs`: `Harness` itself (`run()`, `turn()`, `runtime()`, `agent()`,
  `core()`, `workspace_dir()`, `action_dir()`) and `HarnessCore`, a
  deliberately narrow facade over non-turn domains (config, auth) that
  exposes neither the raw runtime nor the orchestrator agent, so nothing can
  start a turn that skips the harness's provider route and access tier.
- `builder.rs`: `HarnessBuilder`: provider, workspace, access, `backend_url`
  (for non-inference backend calls when the embedding product has its own
  backend), and `session` (installing a backend identity when required).
- `access.rs`: `Access`: the tier a turn runs under (`readonly`, `full`,
  `trust`).
- `provider.rs`: `Provider`: which model answers and where the request
  goes, including `Provider::openai_compatible` for a caller-supplied
  endpoint and `Provider::inherit` to run exactly as the installed app does.
- `workspace.rs`: `Workspace`: `Ephemeral`, `dir(path)`, or `Inherit` (the
  operator's real `~/.openhuman` workspace and session).
- `mcp.rs` (`mcp` feature): `HttpHeader`, `McpAuthConfig`, `McpServer`.
- `skills.rs` (`skills` feature): skill bundle discovery and copying for a
  harness-owned agent.
- `error.rs`: `HarnessError`.

## Running on your own endpoint

A harness identifies as `HostKind::Library` by default, so supplying a
`Provider` is enough for inference: the library host is trusted to bring its
own endpoint and credentials, without an OpenHuman app login. Managed
TinyHumans inference needs the runtime's API key instead
(`RuntimeBuilder::api_key`); see
[`gitbooks/developing/tinyhumans-api-key.md`](../../../../gitbooks/developing/tinyhumans-api-key.md).
Neither path applies to `Provider::inherit` with `Workspace::Inherit`, which
runs exactly as the installed app does, session included.

## Two things the harness cannot do for you

- **The tokio runtime is the host's**, and its stack size matters: an agent
  turn is a deep async state machine, delegation nests another one inside
  it, and the default 2 MiB worker stack can overflow. Build it with
  `AGENT_WORKER_STACK_BYTES` and `MAX_BLOCKING_THREADS`.
- **One runtime per process.** The keyring master key, the RPC bearer, the
  event bus and the domain subscribers are all process-scoped. A harness
  owns a runtime, so a second `HarnessBuilder::build` call in the same
  process returns `HarnessError::AlreadyRunning`. Put more agents on the
  existing runtime with `Runtime::agent` instead of building a second
  harness.

## Where to look next

- [`../runtime/README.md`](../runtime/README.md) and
  [`../agent/README.md`](../agent/README.md): the two types `Harness`
  wraps.
