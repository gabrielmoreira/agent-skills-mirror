---
description: >-
  High-level shape of the OpenHuman system (desktop shell, Rust core, Memory
  Tree, agent loop). Pointer to the deep developer architecture in the repo.
icon: code-branch
---

# Architecture

OpenHuman is open-sourced under GNU GPL3. This page is the high-level shape of the system; the deep developer architecture lives in [deep architecture reference](../architecture.md) in the repo.

## The shape

OpenHuman is a **React + Tauri v2 desktop app** with a **Rust core** doing the heavy lifting, in the same process rather than as a separate service.

```text
┌──────────────────────────────────────────────────────────────────┐
│ Tauri shell (crates/openhuman-app/)                              │
│ • windowing, OS integration, embedded core lifecycle (tokio task)│
│ • global hotkeys, PTT/dictation overlays, deep links             │
└──────────────────────────────────────────────────────────────────┘
                     │ JSON-RPC (loopback HTTP) ↕
┌──────────────────────────────────────────────────────────────────┐
│ Rust core (crates/openhuman-core/, in-process, no binary)        │
│ • Memory v2 (engine binding, recall/fetch/store, turn lifecycle) │
│ • Integration adapters + memory source sync                      │
│ • Provider router (model routing)                                │
│ • TokenJuice compression                                         │
│ • Native tools (search, fetch, fs, git, …)                       │
│ • Voice (STT in, TTS out, live voice agent)                      │
└──────────────────────────────────────────────────────────────────┘
                     │
┌──────────────────────────────────────────────────────────────────┐
│ React frontend (app/src/)                                        │
│ • Screens, navigation                                            │
│ • Talks to core over `coreRpcClient`                             │
│ • No business logic - presentation only                          │
└──────────────────────────────────────────────────────────────────┘
```

**Where logic lives:**

- **Rust core**. All business logic: Memory, integrations, model routing, tools, voice. Authoritative.
- **Tauri shell**. Windowing, process lifecycle, IPC. A delivery vehicle, not where features live.
- **React frontend**. UI and orchestration. Calls into core via JSON-RPC: `coreRpcClient` `fetch()`es `http://127.0.0.1:<port>/rpc` directly; only non-loopback plain-`http://` runtimes go through the shell's `relay_http_rpc` command (the `openhuman-rpc` HTTP client).

Running the core in-process instead of behind a socket is also why it's cheap to run many agents at once: no per-agent OS process, no per-agent socket. See [Performance](../performance.md) for the measurements and [Embedding OpenHuman](../embedding.md) for using the same core as a library outside the desktop app.

## Crates

- `crates/openhuman-app/` - Tauri v2 desktop host; excluded from the root workspace, built from its own manifest.
- `crates/openhuman-core/` - Cargo package `openhuman`: business domains, the controller contract and in-process dispatch, `CoreBuilder`/`CoreRuntime`. It is a library: no binary, no JSON-RPC server, and no dependency on `tinyhumans-sdk`.
- `crates/openhuman-embed/` - typed library facade (`openhuman_embed::Runtime` / `Agent`, with `Harness` as a one-agent shorthand) for embedding the core in another product.
- `crates/openhuman-rpc/` - JSON-RPC 2.0 over the core: the envelopes, the browser-origin allowlist, the HTTP client used by the app and TUI, and the whole server (axum router, auth middleware, Socket.IO, `/dev/connect`, the listener bind). The contract types themselves (`Outcome`, `ControllerSchema`, `StructuredRpcError`) live in the core.
- `crates/openhuman-tinyhumans/` - the TinyHumans layer: the SDK-backed backend transport, the hosted RPC proxy domains, a `RuntimeBuilder` that boots connected, and the host-side login and session owner. The only crate allowed to depend on `tinyhumans-sdk`, and the first thing every host installs.
- `crates/openhuman-cli/` - the `openhuman-core` binary, the developer and benchmark bins, and every root `tests/` and `examples/` target.
- `crates/openhuman-tui/` - standalone terminal frontend that boots the core in-process.

The full table is under "Repository layout" in the [deep architecture reference](../architecture.md).

## Data flow

1. **Connect**. OAuth into an [integration](../../features/integrations/README.md). Backend stores the token; core never sees it in plaintext.
2. **Sync**. A [memory source](../../features/memory.md) (folder, file, link, GitHub, RSS, or a connected Composio toolkit) syncs on demand and on its own schedule.
3. **Read**. `tinymemory-sources` turns the source into documents, with an SSRF guard on links.
4. **Scrub**. Every engine the host binds is wrapped in `memory::guard::ScrubbingEngine`, which uses the `safety` feature of `tinymemory-integrations` to strip secrets and personal identifiers before a write leaves the process. The wrap happens where the engine is resolved, so it covers the tool, the RPC surface, source sync, backfill and import; a caller holding a `BoundEngine` and reaching past it is not covered, which is why resolution is the only sanctioned way to get one.
5. **Store**. The item goes to the selected engine (hosted TinyHumans or your CortexDB). Conversation turns are logged as they happen, learnings when the agent or you add one.
6. **Recall / Fetch**. The agent's `memory` tool asks the engine a question (with citations) or runs a raw hybrid search.
7. **Pack**. Before every turn, a token-budgeted memory pack is recalled and added to that turn's model request only, never to the transcript.
8. **Forget**. Items are removed by id from the Memory page or the tool.
9. **Compress**. Tool output and large source data go through [TokenJuice](../../features/token-compression.md) before entering LLM context.
10. **Route**. The [router](../../features/model-routing/README.md) picks the right provider and model for the task hint, one of several [pluggable engines](../engines.md) the core chooses at runtime.

## Privacy boundary

Stays on your machine:

- Workspace config and persona files.
- Audio capture buffers and any local model state.

Goes through the OpenHuman backend (under one subscription, and one TinyHumans API key for embedders):

- LLM calls (model providers).
- Web search proxy.
- Integration OAuth and tool proxying.
- TTS streaming.

See [Privacy & Security](../../features/privacy-and-security.md) for the full picture, and [One TinyHumans API key](../tinyhumans-api-key.md) for what that single key covers.

## Open source

- **Repo:** [github.com/tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman). GNU GPL3.
- **Issues and PRs** are welcome. The project is in early beta.
- For contributors, the canonical developer guide is [deep architecture reference](../architecture.md).
