# session_import

Host side of the one-time migration of legacy OpenHuman session transcripts
into TinyAgents `Store`/`AppendStore` records. The importer, the live
dual-write and the shadow read moved to
`tinyagents_session::transcript::import` (see its README for sources,
destination layout and idempotency).

What stays in OpenHuman:

- [`schemas.rs`](./schemas.rs): the explicit `session_import.run` controller
  (`openhuman-core session_import run`, JSON-RPC
  `openhuman.session_import_run`). Never run from a boot hook.
- [`live.rs`](./live.rs): whether the dual-write and shadow read run
  (`AgentConfig::session_dual_write` / `session_shadow_reads`, the
  `OPENHUMAN_SESSION_DUAL_WRITE` / `OPENHUMAN_SESSION_SHADOW_READS` kill
  switches) and the session KV store registered on `RunContext.stores`.
- [`projector.rs`](./projector.rs): `journal_message_from_transcript`, the
  `JournalProjector` handed to the upstream importer so journal records carry
  the host's reconstructed sidecar metadata.

## Further reading

- [Parent module README](../README.md)
- [Agent harness architecture](../../../../../gitbooks/developing/architecture/agent-harness.md)
- [Chat](../../../../../gitbooks/features/chat.md)
