# Agent todos

TinyAgents owns todo types, persistence, normalization, status transitions,
claims, dispatch, and markdown rendering. This directory contains only
OpenHuman agent-runtime adapters:

- `ops.rs`: maps OpenHuman execution locations onto TinyAgents stores.
- `tools.rs`: exposes the model-facing todo tools.
- `types.rs`: re-exports TinyAgents types and normalizes timestamps at the
  OpenHuman transcript boundary.

There is no frontend task board and no `openhuman.todos_*` JSON-RPC API.
