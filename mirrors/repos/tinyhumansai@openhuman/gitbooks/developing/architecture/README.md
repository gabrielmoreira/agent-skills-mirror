---
description: >-
  High-level shape of the OpenHuman system (desktop shell, Rust core, Memory
  Tree, agent loop). Pointer to the deep developer architecture in the repo.
icon: code-branch
---

# Architecture

OpenHuman is open-sourced under GNU GPL3. This page is the high-level shape of the system; the deep developer architecture lives in [deep architecture reference](../architecture.md) in the repo.

## The shape

OpenHuman is a **React + Tauri v2 desktop app** with a **Rust core** that does the heavy lifting.

```
┌──────────────────────────────────────────────────────────────────┐
│ Tauri shell (crates/openhuman-app/)                              │
│ • windowing, OS integration, embedded core lifecycle (tokio task)│
│ • global hotkeys, PTT/dictation overlays, deep links             │
└──────────────────────────────────────────────────────────────────┘
                     │ JSON-RPC (loopback HTTP) ↕
┌──────────────────────────────────────────────────────────────────┐
│ Rust core (crates/openhuman-core/, binary `openhuman-core`)      │
│ • Memory Tree pipeline                                           │
│ • Integration adapters + auto-fetch scheduler                    │
│ • Provider router (model routing)                                │
│ • TokenJuice compression                                         │
│ • Native tools (search, fetch, fs, git, …)                       │
│ • Voice (STT in, TTS out, Meet agent)                            │
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

- **Rust core**. all business logic. Memory Tree, integrations, model routing, tools, voice. Authoritative.
- **Tauri shell**. windowing, process lifecycle, IPC. A delivery vehicle, not where features live.
- **React frontend**. UI and orchestration. Calls into core via JSON-RPC: `coreRpcClient` `fetch()`es `http://127.0.0.1:<port>/rpc` directly; only non-loopback plain-`http://` runtimes go through the shell's `relay_http_rpc` command (the `openhuman-rpc` HTTP client).

## Crates

- `crates/openhuman-app/` — Tauri v2 desktop host; excluded from the root workspace, built from its own manifest.
- `crates/openhuman-core/` — Cargo package `openhuman`: business domains, JSON-RPC server, CLI, `CoreBuilder`/`CoreRuntime`.
- `crates/openhuman-embed/` — typed library facade (`openhuman_embed::Harness`) for embedding the core in another product.
- `crates/openhuman-rpc/` — shared RPC contracts (`RpcOutcome`, `unwrap_rpc`, `StructuredRpcError`) and the HTTP client used by the app and TUI.
- `crates/openhuman-tui/` — standalone terminal frontend that boots the core in-process.

The full table is under "Repository layout" in the [deep architecture reference](../architecture.md).

## Data flow

1. **Connect**. OAuth into a [integration](../../features/integrations/README.md). Backend stores the token; core never sees it in plaintext.
2. **Auto-fetch**. Every twenty minutes the [scheduler](../../features/obsidian-wiki/auto-fetch.md) walks every active connection and asks each native provider to sync.
3. **Canonicalize**. Provider output (an email page, a GitHub diff, a Slack channel dump) is normalized into provenance-tagged Markdown.
4. **Chunk**. Markdown is split into ≤3k-token deterministic chunks.
5. **Store**. Chunks land in SQLite (`<workspace>/memory_tree/chunks.db`) and as `.md` files in `<workspace>/wiki/`.
6. **Score**. Background workers run embeddings, entity extraction, hotness scoring.
7. **Summarize**. Source / topic / global summary trees are built and refreshed from the chunk pool.
8. **Retrieve**. When you ask a question, the agent queries the Memory Tree (search / drill down / topic / global / fetch).
9. **Compress**. Tool output and large source data go through [TokenJuice](../../features/token-compression.md) before entering LLM context.
10. **Route**. The [router](../../features/model-routing/) picks the right provider+model for the task hint.

## Privacy boundary

Stays on your machine:

- The Memory Tree SQLite DB.
- The Obsidian Markdown vault.
- Audio capture buffers and any local model state.

Goes through the OpenHuman backend (under one subscription):

- LLM calls (model providers).
- Web search proxy.
- Integration OAuth and tool proxying.
- TTS streaming.

See [Privacy & Security](../../features/privacy-and-security.md) for the full picture.

## Open source

- **Repo:** [github.com/tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman). GNU GPL3.
- **Issues and PRs** are welcome. The project is in early beta.
- For contributors, the canonical developer guide is [deep architecture reference](../architecture.md).
