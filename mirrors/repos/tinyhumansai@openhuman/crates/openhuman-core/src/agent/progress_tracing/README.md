# progress_tracing

Turns the agent's real-time [`AgentProgress`](../progress.rs) event stream into
OpenTelemetry/Langfuse-style trace spans (`agent.turn` -> `agent.iteration` ->
`tool.*`/`subagent.*`), correlated by session id, for offline inspection and
debugging long multi-agent runs (issue #3886). The module doc on
`agent/progress_tracing.rs` has the full span-tree shape and the
content-capture privacy gate (`observability.agent_tracing.capture_content`,
default off; enforced once, in `SpanCollector`, so no exporter can leak
content).

## Key files

- `agent/progress_tracing.rs` (parent module file) declares the submodules
  below it. `collector/` — `SpanCollector` (pure state machine: feed it
  progress events plus a timestamp, it accumulates finished `TraceSpan`s).
  `types.rs` — `TraceContext`, `RunType`, `SpanKind`/`SpanStatus`.
  `serialize.rs` — `spans_to_ndjson`. `export.rs` — the local file/log
  exporter `export_spans`, and the two run-completion entry points
  `export_run_trace` / `export_run_trace_from_journal`. Each entry point runs
  two independent, best-effort paths: a Langfuse push when
  `observability.share_usage_data` is on (the default), and local NDJSON
  export to `export_path` or the app log when
  `observability.agent_tracing.enabled` is on (opt-in).
- `langfuse.rs` + `langfuse/` (`environment.rs`, `ingestion_batch.rs`,
  `span_export.rs`, `journal_export.rs`) — Langfuse
  ingestion exporter: `push_spans` (live spans) and `push_observations`
  (journal observations plus the run-ledger `RunTelemetry` aggregate). Both
  POST to the backend's `/telemetry/langfuse/ingestion` proxy, derived from
  `effective_backend_api_url`, authenticated with the session bearer; the
  backend injects the Langfuse project keys and forwards to
  `/api/public/ingestion`. `push_spans` builds a bare `reqwest` request and
  stamps `x-sdk-name` via `crate::api::product::product_identity_header`
  (AGENTS.md "Backend API"); `push_observations` sends through the vendored
  `tinyagents_harness::LangfuseClient::proxy`, splitting the batch at 500
  events. Pushes are allowlisted to `staging`/`development` hosts
  (`environment_for_base`, `LANGFUSE_PUSH_ENVIRONMENTS`) and skipped elsewhere
  with one `info` log per process. Failures are logged and swallowed so
  tracing never breaks a turn.
- `journal_projection.rs` — `spans_from_observations` rebuilds spans from the
  durable `AgentObservation` journal instead of the live stream, by folding
  journalled events through the same `SpanCollector`, so a UI/supervisor can
  attach after a run. Its match is exhaustive over
  `tinyagents_harness::events::AgentEvent`; the module doc lists the known
  parity gaps (estimated vs. charged cost, no subagent prompt/output content).

Tests live in this directory as `*_tests.rs` files, e.g.
`progress_tracing_tests.rs`, `progress_tracing_span_tree_tests.rs`,
`progress_tracing_attribution_tests.rs`, `progress_tracing_content_gate_tests.rs`,
`langfuse_tests.rs`, `langfuse_batch_tests.rs`, `langfuse_trace_fields_tests.rs`,
`journal_projection_tests.rs`, `journal_projection_cost_rollup_tests.rs`.

## Called by

- `web_chat/progress_bridge.rs` — the only caller. Builds a `SpanCollector`
  per run, feeds it `AgentProgress`, shadow-compares the live spans against
  `spans_from_observations` over the run journal, then calls
  `export_run_trace_from_journal` (journal available) or `export_run_trace`.

`flows/tinyflows/langfuse_export.rs` is the flow-run counterpart: it mirrors
the proxy route, bearer auth, and timeout of `push_spans` but has its own
copy and does not call this module.

## Related docs

- [gitbooks/developing/agent-observability.md](../../../../../gitbooks/developing/agent-observability.md)
