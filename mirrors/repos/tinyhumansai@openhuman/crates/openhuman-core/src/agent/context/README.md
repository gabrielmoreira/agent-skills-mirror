# Agent context defaults

This module exposes the host's default for how many recent tool results the
TinyAgents microcompact middleware keeps. Prompt composition belongs to
[`agent::prompts`](../prompts/README.md), configuration is mapped into turn
middleware in [`agent::tinyagents`](../tinyagents/README.md), and the harness
owns transcript reduction and middleware execution.

## Files

| File | Role |
| --- | --- |
| [`mod.rs`](./mod.rs) | Module documentation and `DEFAULT_KEEP_RECENT_TOOL_RESULTS`. |

There is no per-session `ContextManager` here. The former manager, statistics,
session-memory state, tool-result budget constant, and cleared-placeholder
constant were removed as their responsibilities moved to the config schema,
TinyAgents middleware, and `tinyagents-harness`.

## Consumers

The TinyAgents host maps configured context options into harness middleware.
Channel and agent prompts use `agent::prompts`; live transcript compaction and
tool-result clearing run in TinyAgents. This module owns no persistence,
controllers, tools, or event subscribers.
