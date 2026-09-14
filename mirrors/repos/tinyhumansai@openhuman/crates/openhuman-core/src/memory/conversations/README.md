# conversations

Workspace-backed conversation thread/message storage — transcript
persistence, not semantic indexing. This is the JSONL store of raw
thread/message records plus a trigram/CJK-bigram index for cross-thread
substring search; the summary-tree archival of the same transcripts is a
different index answering a different question and lives in
[`memory/tree/`](../tree/). See `mod.rs` for the full accounting of how this
code came back from `tinycortex::memory::conversations` in #5560 — it is not
repeated here.

## Three parts

- **`store/`** — the implementation: on-disk format, root lifecycle, sharded
  metadata/message locks, the warm index cache, and CRUD/search. Everything
  it exposes is re-exported from `mod.rs`, so callers always name
  `crate::memory::conversations::{…}`, never the `store` subtree directly.
- **`blocking.rs`** — `spawn_blocking` wrappers around every store entry
  point. The store is synchronous and takes `parking_lot` locks across
  fsync'd file I/O, so calling it from an `async fn` directly would park a
  tokio worker thread for the whole wait; request paths must go through
  `blocking` instead (#5156).
- **`bus.rs`** — the `core::bus` subscriber
  (`register_conversation_persistence_subscriber`) that mirrors inbound and
  processed channel turns into the store, so channel transcripts (Slack,
  Telegram, …) persist alongside the UI's own threads.

## On-disk layout

```text
<workspace>/memory/conversations/
├── threads.jsonl              # append-only upsert/delete log of thread metadata
└── threads/
    └── <hex(thread_id)>.jsonl # one file per thread, its messages in order
```

`store/` also builds a trigram/CJK-bigram inverted index over message content
in memory for cross-thread search (`inverted_index.rs`, `tokenize.rs`); the
index is not persisted. It is primed from the JSONL on the first search per
workspace root and then kept warm in a process-wide cache (`store_index.rs`,
`prime_index_if_cold`).

## Callers

Async request paths use the `blocking` wrappers. Grepping
`memory::conversations::` finds the store used directly by
[`threads/`](../../threads/) (`mod.rs`, `ops.rs`, `turn_state/store.rs`,
`welcome_migration.rs`), by
[`channels/`](../../channels/) (`host/adapters.rs`,
`providers/telegram/remote_control.rs`, `runtime/startup/start_channels.rs`) for
mirroring channel turns, and by the agent harness/orchestration layer
(`agent/harness/subagent_runner/`, `agent/orchestration/tools/`,
`agent/task_session.rs`, `agent/tinyagents/host/agent_memory.rs`) for
sub-agent and worker-thread transcripts.

## Tests

`store/*_tests.rs` covers the implementation (`store_tests.rs`,
`store_tests_late.rs`, `store_tests_more.rs`, `store_concurrency_tests.rs`,
`inverted_index_tests.rs`, `tokenize_tests.rs`, `types_tests.rs`);
`blocking_tests.rs` and `bus_tests.rs` cover the two wiring parts.
