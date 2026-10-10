# tests

End-to-end suites for `openhuman-embed`. Each file builds a real `Runtime`
(or `Harness`) in-process and drives turns against `wiremock` servers that
stand in for the model provider and, where needed, the backend. No suite
calls a live LLM or a real service. Cargo discovers these files on its own;
this crate declares no `[[test]]` entries.

## How the suites are shaped

A runtime claims a process-wide slot (the core's keyring, event bus and
domain subscribers are process-scoped), so each file is its own test binary
and usually holds a single `#[test]` that builds one runtime and checks
everything against it. Splitting the assertions into separate tests would
either race for the slot or need a mutex. [`attached_tools.rs`](attached_tools.rs) holds a static
`RUNTIME_LOCK` for the same reason.

Each `#[test]` builds its tokio runtime with `common::runtime()`, which sets
the large worker stack a turn needs, instead of using `#[tokio::test]`.

Routing assertions come from the mocks: each agent gets its own provider
mock, so a turn that leaked to another agent's endpoint shows up as a request
recorded on the wrong server.

## Layout

| File | What it proves |
| --- | --- |
| [`common/mod.rs`](common/mod.rs) | Shared helpers: `runtime()`, `offline_config()`, `provider(reply)`, `stub_backend()`, `chat_completion`, `tool_call_completion`, and request inspectors (`chat_requests`, `tool_names`, `tool_results`). |
| [`facades.rs`](facades.rs) | The runtime-free curated facades (`artifacts`, `chat_surface`, `identity`, `config` helpers, `modules`), the compile-status constants and `schema_for_rpc_method`. |
| [`seams_runtime.rs`](seams_runtime.rs) | A controller extension is invokable after a real `build()`, a `live_policy` is applied after boot, and hooks are removed on drop while the extension outlives the runtime. |
| [`harness_embed.rs`](harness_embed.rs) | A `Harness` runs a real turn with no transport and no background services, routes it to the mock provider, and binds nothing. |
| [`runtime_agents.rs`](runtime_agents.rs) | Several agents on one runtime keep their own provider, access tier, skills, MCP servers and working directory, and the runtime's API key reaches a mocked managed backend as a bearer. |
| [`session_store.rs`](session_store.rs) | On a `Stateless` workspace with `InMemorySessionStores`, transcripts, journal and run status land in the store per agent, a reopened agent resumes from the store, and nothing durable is written to the scratch directory. |
| [`attached_tools.rs`](attached_tools.rs) | `Agent::attach_tools` sources survive clones and session resume, and name collisions are refused. |
| [`composio_agents.rs`](composio_agents.rs) | Two agents with their own `ComposioHostCredential` reach Composio with their own key only. |
| [`memory_facade.rs`](memory_facade.rs) | `Runtime::memory` over TinyMemory's in-memory reference engine keeps two tenant roots apart. |
| [`public_api.rs`](public_api.rs) | Compile-time check that the host-facing types and signatures stay exported. |

## Running

[`runtime_agents.rs`](runtime_agents.rs) gates its skills and MCP assertions on the `skills` and
`mcp` features, so run with them on:

```bash
cargo test -p openhuman-embed --features inference,mcp,skills
cargo test -p openhuman-embed --features inference,mcp,skills --test session_store
pnpm debug rust session_store
```

Add a new scenario as a new file rather than a second `#[test]` in an
existing one, and reuse [`common/`](common/) for mocks.

## Further reading

- [`gitbooks/developing/embedding.md`](../../../gitbooks/developing/embedding.md): embedding the core in another product.
- [`gitbooks/developing/testing-strategy.md`](../../../gitbooks/developing/testing-strategy.md): testing strategy.
- [`crates/openhuman-embed/README.md`](../README.md): the openhuman-embed crate README.
