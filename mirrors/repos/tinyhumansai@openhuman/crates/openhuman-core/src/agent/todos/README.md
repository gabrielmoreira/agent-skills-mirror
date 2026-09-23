# Agent todos

TinyAgents owns todo types, persistence, normalization, status transitions,
and markdown rendering (`tinyagents_graph::todos`). This directory contains
only OpenHuman agent-runtime adapters:

- `ops.rs`: maps OpenHuman execution scopes (agent session, scratch) onto the
  one in-process TinyAgents store.
- `types.rs`: re-exports the TinyAgents types.

The model-facing `todo` tool lives in `crate::agent::tools::todo`. The list
reaches the frontend through the `todo` tool call in the turn's progress
events; there is no `openhuman.todos_*` JSON-RPC API.
