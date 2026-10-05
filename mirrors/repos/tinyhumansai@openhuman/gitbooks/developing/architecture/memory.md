---
description: >-
  The memory host layer in crates/openhuman-core/src/memory/: TinyMemory's
  agent lifecycle bound to OpenHuman's turns, RPC and UI.
icon: diagram-project
---

# Memory (`crates/openhuman-core/src/memory/`)

OpenHuman drives TinyMemory's agent memory lifecycle around every turn: a
memory pack recalled before the model runs, the turn logged on both sides,
memory recalled into compaction checkpoints, and belief builds run in the
background. The behaviour is specified in `docs/specs/memory-v2.md`; the
user-facing feature is [Memory](../../features/memory.md).

## TinyMemory crates (`vendor/tinymemory/crates/`)

| Crate | Owns |
| --- | --- |
| `tinymemory-api` | The engine contract: `MemoryEngine` (recall, fetch, store, forget, list, consolidate, beliefs), `StoreItem`, `MemoryMeta`, `MetaFilter`, `Namespace`/`Reach`, `EngineDescriptor`, `Error`. No I/O. Its `conformance` feature adds the suite every engine passes and the in-memory `ReferenceEngine` the unit tests use. |
| `tinymemory-tools` | The agent surface over any engine: `AgentMemory` (`start_session`, `pre_turn`, `post_turn`, `recall_for_compaction`, `recall`), `MemoryLayout`, `Brain`, holistic recall (`ContextPack`), `BackgroundJob`/`BackgroundRunner`. |
| `tinymemory-integrations` | Everything that touches the outside world: the CortexDB engine on both wires (`cortexdb` direct, `tinyhumans` behind the backend), the registry, document conversion and the brain filer, source readers (SSRF-guarded), secret/PII scrubbing, the v1 importer. |

## Host modules

| Module | Role |
| --- | --- |
| `engine` | Binds `[memory] engine`: `tinyhumans` over the host's backend credential (resolved per request) with the transport's attribution headers, or `cortexdb` with the key stored as `memory-cortexdb`. Off when neither is usable. |
| `guard` | `ScrubbingEngine`: every write is scrubbed under the host policy, whichever path makes it. |
| `scope` | `MemoryIdentity` scoped around every turn, resolved to a layout root and a memory agent id (host binding, definition pin, team, default). |
| `lifecycle::hooks` | `pre_turn`, `post_turn`, `compaction`: bounded, never fail a turn. |
| `lifecycle::jobs` | The persisted background queue and the `memory_background` cron job. |
| `lifecycle::views` | Policy, pack preview, agents list, job views for the RPCs. |
| `brain` | Brain source mapping for synced items and the `memory_brain_*` ops. |
| `sources` | The `[[memory.sources]]` registry and sync into the brain. |
| `channels` | Which channel each logged thread arrived on, for forgetting a channel. |
| `backfill` | Consent-gated storing of past chats in the lifecycle's shape. |
| `import` | Consent-gated, resumable v1 import. |
| `tools` | The single `memory` agent tool (`recall`, `fetch`, `learn`, `forget`), confined to the identity's layout. |
| `ops`, `explore` | Engine selection, recall, fetch, learn, forget, listing, the explorer. |
| `bus` | The cron subscriber (`memory_sources_sync`, `memory_background`). |
| `schemas` | The `openhuman.memory_*` controllers. |
| `status`, `error`, `types` | Subsystem status, error codes, shared types. |

## Where the agent loop calls memory

| Hook | File |
| --- | --- |
| Pre-turn (log + recall), first turn after a compaction also `start_session` | `agent/session_host/runtime_session/memory_ingest.rs`, from `before_turn` in `runtime_session.rs` |
| Pack injection, ephemeral, every model request of the turn | `agent/tinyagents/middleware/memory_pack.rs` |
| Post-turn (log the reply, queue builds), after the durable commit | `memory_ingest.rs`, from `finalize_after_durable_commit` |
| Compaction recall into the checkpoint | `agent/tinyagents/memory_summarizer.rs`, wrapped around the summarizer in `harness_context_ladder.rs` |

The turn's `MemoryTurn` (config, identity, thread, pack) rides
`OpenHumanRunContext::memory_turn`; a child run has its own.

Chat thread persistence is not memory: it is `tinyagents_session::threads`,
wrapped by `crates/openhuman-core/src/threads/store`.

The MCP server exposes `memory.recall`, `memory.fetch`, `memory.list`,
`memory.learn` and `memory.forget` (`mcp/server/tools/specs.rs`).

## Tests

- Unit tests beside each module (`*_tests.rs`), against `ReferenceEngine`.
- `tests/memory_v2_e2e.rs`: every `memory_*` RPC against the mock backend, and
  a web-chat turn whose inference request carries the pack, whose turns are
  logged with `x-sdk-name`, and whose transcript holds no pack.
- `crates/openhuman-embed/tests/runtime_agents.rs`: `AgentSpec::memory`.
- `app/test/playwright/specs/memory-v2.spec.ts` (UI).

Against a real CortexDB server, `scripts/test-memory-cortexdb-live.sh` boots
the pinned harness in Docker (`vendor/tinymemory/integration/cortexdb/`) and
runs `tests/memory_cortexdb_live.rs`: learnings, a synced folder source,
web-chat turn logging, recall, the pack preview, the pack injected into a
turn's inference request, and belief builds. It skips unless
`OPENHUMAN_LIVE_CORTEXDB_URL` is set.
