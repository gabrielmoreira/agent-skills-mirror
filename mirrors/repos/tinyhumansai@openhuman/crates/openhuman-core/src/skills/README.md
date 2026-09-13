# Skills

Discovery and parsing of agentskills.io-style skills (a directory containing `SKILL.md` with YAML frontmatter and Markdown instructions). Owns scope resolution (User vs Project vs Legacy), trust-marker enforcement, resource reading, and install / uninstall. Skills are surfaced to agents via the compact `## Installed Skills` catalog and executed via `run_skill` in an isolated worker — bodies are no longer spliced into chat turns. Does NOT own runtime execution internals or general tool execution (`tools/` / `javascript/`).

## Public surface

- `pub enum SkillScope` — `ops.rs:42-58` — discovery scope (`User` / `Project` / `Legacy`); decides precedence on name collision.
- `pub const MAX_SKILL_RESOURCE_BYTES: u64 = 128 * 1024` — `ops.rs:39` — bound on per-resource RPC payload.
- `pub use ops::*` — `mod.rs:9` — re-exports skill discovery, parsing, install, uninstall, resource reading, and frontmatter types.
- `pub struct ToolResult` / `pub enum ToolContent` — `types.rs:7-60` — content blocks returned by skill / tool execution.
- `pub mod bus` — `bus.rs` — emits skill events on the global event bus.
- RPC `skills.{skills_list, skills_read_resource, skills_create, skills_install_from_url, skills_uninstall}` — `schemas.rs` (re-exported `all_skills_controller_schemas` / `all_skills_registered_controllers` via `mod.rs:10`).

## Calls into

- `crates/openhuman-core/src/config/` — workspace path resolution and trust-marker location.
- `crates/openhuman-core/src/agent/` — the `## Installed Skills` catalog rendered in `agent_registry/agents/orchestrator/prompt.rs`, fed by the skill list on `PromptContext` (`agent/harness/session/turn/context.rs`).
- `crates/openhuman-core/src/config/workspace/` — workspace-relative skill paths.
- `crates/openhuman-core/src/core/event_bus/` — emits `DomainEvent::Skill(*)` on install / uninstall.

## Called by

- `crates/openhuman-core/src/tools/traits.rs` — `ToolResult` / `ToolContent` shape shared with the tool registry.
- `crates/openhuman-core/src/config/workspace/ops.rs` — workspace bootstrap touches the skill directory layout.
- `crates/openhuman-core/src/agent/registry/agents/integrations_agent/prompt.rs` — integrations agent reads the skill catalog.
- `crates/openhuman-core/src/agent/harness/fork_context.rs` — fork context propagates injected skills.
- `crates/openhuman-core/src/agent/harness/session/turn.rs` — per-turn injection point.
- `crates/openhuman-core/src/agent/prompts/{mod,types}.rs` — render `## Available Skills` catalog section.
- `crates/openhuman-core/src/core/all.rs` — controller registry wiring.

## Tests

- Unit: tests live alongside `ops.rs`, `schemas.rs`, and `types.rs` as `#[cfg(test)] mod tests` blocks (no separate `*_tests.rs` files in this domain).
- Cross-cutting agent + skill behavior is covered indirectly by `crates/openhuman-core/src/agent/harness/session/{turn,runtime}_tests.rs`.
