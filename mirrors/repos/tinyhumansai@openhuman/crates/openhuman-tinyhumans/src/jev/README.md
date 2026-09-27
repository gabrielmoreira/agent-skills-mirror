# jev

Installs Jev as the core's `tool_search` ranker for a TinyHumans-connected
process. See [`gitbooks/developing/jev.md`](../../../../gitbooks/developing/jev.md)
for what Jev is, the benchmark numbers, and how it compares to plain BM25
retrieval.

## Contents

- `mod.rs`: `install_jev_ranker()`, the one entry point. It builds a
  `TinyHumansJevRanker` and registers it as the process-wide `tool_search`
  ranker through `openhuman_core::agent::tinyagents::discovery`. Idempotent:
  calling it again replaces the previous ranker in place.
- `ranker.rs`: `TinyHumansJevRanker`, the `ToolRanker` implementation. It
  resolves the current backend credential and base URL on every search
  (not once at install time, since a desktop process signs in and out while
  it runs), embeds the tool catalogue through the process's own embedding
  provider to retrieve a shortlist, and asks one `tinytools_jev::JevRanker`
  Choice evaluation to pick from it. The built Jev client is cached by
  credential and base URL fingerprint so a stable session does not rebuild
  an HTTP client on every search.
- `evaluator.rs`: `TinyJevEvaluator`, the `tinytools_jev::JevEvaluator` that
  reaches Jev through the backend's `/agent-integrations/openrouter/systemone`
  proxy with the same credential every other backend call uses.

## Fallback behavior

A process with no usable backend credential, or no embedding provider that
can actually embed, does not run a Jev search at all: `current()` /
`retriever_for` return an error, and the harness's `tool_search` bridge
falls back to its own BM25 catalogue. This is deliberate. A lexical
shortlist would cap Jev's decision at BM25's recall, and the bench in
`docs/plans/jev-tool-search-baseline.md` measured that recall well below
what embeddings retrieve. So `auto` ranking costs nothing extra when the
process is signed out or has no embedding provider configured, and Jev
never makes a decision over a shortlist it distrusts.

## Where to look next

- `vendor/tinyagents/vendor/tinytools/crates/tinytools-jev/`: the generic
  `JevRanker` / `JevEvaluator` / `JevStrategy` types this module configures.
- `crates/openhuman-core/src/config/schema/agent.rs`: `ToolSearchConfig`,
  where a config chooses `ranker = "jev"` (the default), `"bm25"`,
  `"auto"`, or `"compare"`.
- `cargo run -p openhuman-cli --bin tool-search-bench`: the ranker
  comparison harness; see
  [`../../../openhuman-cli/src/bin/README.md`](../../../openhuman-cli/src/bin/README.md).
