# memory

The host side of TinyMemory's agent memory lifecycle. The spec is
[`docs/specs/memory-v2.md`](../../../../docs/specs/memory-v2.md); the engine
contract, the lifecycle and the engines live in `vendor/tinymemory`
(`tinymemory-api`, `tinymemory-tools`, `tinymemory-integrations`). This
directory binds an engine, decides who is acting, calls the lifecycle around
every turn, queues the slow work, and adapts it all to OpenHuman's
controllers, tool, cron and event bus under OpenHuman policy (credentials,
consent, scrubbing, scheduling).

Chat thread persistence is not memory: see [`threads/store`](../threads/store/README.md).

## Responsibilities

- Bind the configured engine (`tinyhumans` over the host backend credential
  and attribution headers, or `cortexdb` with the key stored as
  `memory-cortexdb`); memory is **off** when neither is usable: the tool is
  not registered, the hooks do nothing and RPCs answer `MEMORY_OFF`.
- Scrub every write (`guard`).
- Resolve the acting identity to a layout root and memory agent id (`scope`).
- Before each turn, log the user turn and recall its pack; after the commit,
  log the reply; on compaction, recall what was folded away (`lifecycle`).
- Queue and run belief builds and deferred ingests (`lifecycle::jobs`).
- File synced sources into the brain (`sources`, `brain`).
- Store past chats and import a v1 store, each after explicit consent.
- Delete for good (`deletion`). This covers a deleted thread's conversations,
  a disconnected connector's items, a forgotten channel's threads and a removed
  source's items.
  - A connector's own `source:<toolkit>` scope is erased outright when it
    holds only that connection's items.
  - Everything else is forgotten by `memory_ids` with an explicit
    `redact_events` cascade (the engine's default keeps the events).
  - Anything that cannot run now, because memory is off or the call failed,
    is queued and drained on the next sign-in (`CredentialChanged`) and on
    every background tick.

## Key files

| File | Role |
| --- | --- |
| `engine.rs` | `resolve` binds the `[memory]` engine or says why memory is off; engines are cached per config fingerprint. |
| `guard.rs` | `ScrubbingEngine`, wrapped around every bound engine. |
| `scope.rs` | `MemoryIdentity`, `ResolvedIdentity` and their resolution order; `within_agent` / `within`. |
| `lifecycle/mod.rs` | `AgentMemory` for an identity under the `[memory.recall]` policy. |
| `lifecycle/hooks.rs` | `pre_turn`, `post_turn`, `compaction`; `TurnPack` and `MemoryTurn`. |
| `lifecycle/jobs.rs` | The persisted job queue (`<workspace>/memory/jobs.json`) and the `memory_background` run. |
| `lifecycle/views.rs` | Policy get/set, pack preview, agents list, jobs list/run. |
| `brain.rs` | Brain source mapping and the brain ops. |
| `sources/` | Source registry, state and sync (folder, file, link, github, rss). |
| `channels.rs` | Channel → thread records for forgetting a channel. |
| `deletion.rs` | Hard deletes that must reach the engine: thread forget, the pending-deletion queue (`<workspace>/memory/pending_deletions.json`) and its drain. |
| `backfill.rs` | Past chats from the thread store, resumable, with consent. |
| `import.rs` | Consent-gated, resumable v1 import. |
| `tools.rs` | The single `memory` agent tool and the turn's memory citations. |
| `ops.rs`, `explore.rs` | Engine selection, recall, fetch, learn, forget, listing; the explorer. |
| `bus.rs` | The `memory_sources_sync` / `memory_background` cron subscriber; the `memory::pending_deletions` sign-in subscriber. |
| `schemas.rs`, `schemas/` | The `openhuman.memory_*` controllers. |
| `status.rs`, `error.rs`, `types.rs` | Subsystem status, error codes, shared types. |
| `*_tests.rs`, `test_fixtures.rs` | Sibling unit tests. |

## Persistence

No local database: items live in the engine. Local files under
`<workspace>/memory/`: `jobs.json`, `channel_threads.json`,
`conversations_backfill.json`, `import_state.json`, `sources_state.json`,
`pending_deletions.json`. The
sources registry is `[[memory.sources]]` in `config.toml`; the CortexDB key is
in the OS keychain.

## Tests

`tests/memory_v2_e2e.rs` (JSON-RPC and a full web-chat turn against the mock
backend), `tests/memory_cortexdb_live.rs` (live CortexDB, opt-in),
`app/test/playwright/specs/memory-v2.spec.ts` (UI), and the sibling
`*_tests.rs`.
