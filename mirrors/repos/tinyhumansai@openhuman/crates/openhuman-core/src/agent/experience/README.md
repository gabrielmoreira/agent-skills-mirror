# agent_experience

Hermes-style **procedural experience memory** for agents. Captures what tool sequences worked (or failed) during a chat turn, redacts secrets, persists them as structured records in the memory store, and ranks/injects relevant past experiences back into future turns as a compact "Relevant Operating Experience" prompt block. The goal is cross-turn procedural learning: the agent remembers *how* it solved similar tasks before, not just facts.

## Responsibilities

- Define the `AgentExperience` record (task summary, tool sequence, outcome, lesson, reuse/avoid hints, confidence, tags, optional owning `profile_id`).
- Persist experiences (upsert by stable id) into the memory store under the `agent_experience` namespace, scrubbing free-text fields first.
- Retrieve and rank experiences for a given task query via lexical/tool/tag overlap scoring, partitioned by agent profile.
- Mark experiences as dismissed so retrieval skips them.
- Auto-derive experience candidates from a completed turn's tool calls (multi-tool success, repeated failures, partial recovery) via a `PostTurnHook`.
- Render ranked hits into a byte-capped markdown block and prepend it to the enriched user message before a turn.
- Expose capture/retrieve/list/dismiss over JSON-RPC.
- Provide `DriverMemory`, the `Memory`-trait view of the bound memory driver that the store (and the session builder) run on.

## Key files

| File | Role |
| --- | --- |
| `crates/openhuman-core/src/agent/experience/mod.rs` | Export-focused module root; re-exports the public surface. |
| `crates/openhuman-core/src/agent/experience/types.rs` | Serde types (`AgentExperience`, `ExperienceHit`, `ExperienceSource`, `ExperienceOutcome`), `redact_text` (Bearer / `sk-` / `token=secret` masking), `stable_experience_id` (SHA-256 over summary + tool sequence + outcome) and `stable_experience_id_for_profile` (same digest with a domain-separated profile segment appended when a profile is set). |
| `crates/openhuman-core/src/agent/experience/store.rs` | `AgentExperienceStore` over `Arc<dyn Memory>`: `put`/`list`/`list_for_profile`/`dismiss`/`dismiss_for_profile`/`retrieve`, `ExperienceQuery`, `retrieve_across_stores` (merge + dedupe over several physical stores), `experience_matches_profile`, the `AGENT_EXPERIENCE_NAMESPACE` const, base64 payload encode/decode, and the lexical/tool/tag overlap scoring (`score_experience`). |
| `crates/openhuman-core/src/agent/experience/capture.rs` | `AgentExperienceCaptureHook` — a `PostTurnHook` that mines `TurnContext.tool_calls` into experience candidates (`successful_multi_tool_experience`, `repeated_failure_experiences`, `partial_success_experience`), stamps the active profile, and persists them. |
| `crates/openhuman-core/src/agent/experience/prompt.rs` | `render_experience_hits` (byte-capped markdown under `AGENT_EXPERIENCE_HEADING = "## Relevant Operating Experience"`) and `prepend_experience_block`. |
| `crates/openhuman-core/src/agent/experience/ops.rs` | `DriverMemory` (implements `Memory` over the bound `MemoryProvider`; `for_config` / `for_subtree`), the RPC param types, and the entry points returning `RpcOutcome<T>` (`capture`/`retrieve`/`list`/`dismiss`). `open_store` / `open_query_stores` resolve the memory subtree(s) for a `profile_id` via `crate::agent::profiles` and bind them with `DriverMemory::for_subtree`. |
| `crates/openhuman-core/src/agent/experience/schemas.rs` | Controller schemas + `handle_*` dispatchers; `all_controller_schemas` / `all_registered_controllers`. |

## Public surface

From `mod.rs` re-exports:

- `AgentExperienceCaptureHook` (capture)
- `prepend_experience_block`, `render_experience_hits`, `AGENT_EXPERIENCE_HEADING` (prompt)
- `all_agent_experience_controller_schemas`, `all_agent_experience_registered_controllers` (schemas)
- `retrieve_across_stores`, `AgentExperienceStore`, `ExperienceQuery`, `AGENT_EXPERIENCE_NAMESPACE` (store)
- `redact_text`, `stable_experience_id`, `AgentExperience`, `ExperienceHit`, `ExperienceOutcome`, `ExperienceSource` (types)

`ops::DriverMemory` is `pub` but reached by path (`crate::agent::experience::ops::DriverMemory`), not re-exported.

## RPC / controllers

Namespace `agent_experience` (registered into `crates/openhuman-core/src/core/all.rs`):

| Method | Inputs | Output |
| --- | --- | --- |
| `agent_experience.capture` | `experience: AgentExperience` | Stored `AgentExperience` (upserted, redacted). Written to the memory subtree of `experience.profile_id` (shared `memory` when unset). |
| `agent_experience.retrieve` | `query` (req), `tools[]`, `tags[]`, `agent_id?`, `entrypoint?`, `profile_id?`, `max_hits?` (default 5) | `hits: ExperienceHit[]` ranked, merged across the shared store and the queried profile store(s). |
| `agent_experience.list` | `profile_id?` | `experiences: AgentExperience[]` ordered by most-recent update, deduped by id across stores. |
| `agent_experience.dismiss` | `id`, `profile_id?` | `{ id, dismissed }`. |

Profile semantics (shared by list and retrieve): `profile_id` omitted sees every record; `profile_id = P` sees records stamped `P` plus unstamped legacy records, never a sibling profile's. All handlers delegate to `ops.rs` and wrap results in `RpcOutcome::single_log`.

## Agent hooks (not a tool)

This module owns no `tools.rs` agent tool. Instead it registers `AgentExperienceCaptureHook` as a **`PostTurnHook`** (`name() == "agent_experience_capture"`). On `on_turn_complete` it extracts candidates from the turn's tool calls, stamps each with the session's `profile_id`, re-derives the id with `stable_experience_id_for_profile`, and persists them. Candidate heuristics:

- **Multi-tool success**: ≥2 successful tool calls → `ExperienceOutcome::Success`, confidence 0.72.
- **Repeated failure**: a tool that failed ≥2 times in one turn → `Failure`, confidence 0.68, with an error class parsed from the output summary (`...(error_class)`).
- **Partial success**: a failure followed by a later success (≥2 calls total) → `Partial`, confidence 0.62; skipped when it would duplicate an earlier candidate's id or outcome.

## Events

None — no `bus.rs`; this module does not publish or subscribe to `DomainEvent`s.

## Persistence

Records are stored through the `Memory` trait (no dedicated DB), served by `DriverMemory` over the memory driver bound for the workspace subtree:

- Namespace: `agent_experience` (`AGENT_EXPERIENCE_NAMESPACE`).
- Key: `experience/<id>`; id is `stable_experience_id_for_profile(...)` (`exp_<24 hex>`) when not supplied. `profile_id == None` reproduces the legacy digest byte-for-byte.
- Value: **base64 of the `AgentExperience` JSON**, `MemoryCategory::Custom("agent_experience")`. Base64 keeps the memory layer's bare-numeric PII scrubber from rewriting a Luhn-valid millisecond timestamp and corrupting the JSON (#5209); reads fall back to plain JSON for legacy rows.
- `put` requires non-empty `task_summary` and `lesson`, preserves the original `created_at_ms` on update, stamps `updated_at_ms`, and runs `memory::safety::sanitize_text` over every free-text field (`task_fingerprint`, `task_summary`, `lesson`, `reuse_hint`, `avoid_hint`, `error_class`, `agent_id`, `entrypoint`, `tools_used`, `tool_sequence`, `tags`) before write. `id` and `profile_id` are keys and left intact.
- Dismiss is a soft flag (`dismissed = true`), retained in `list`, filtered out of `retrieve`. `dismiss_for_profile` refuses to flag a record owned by a different profile.
- Each memory subtree (`memory` for the shared tree, `memory<suffix>` such as `memory-1` for a profile with dedicated memory) is its own binding and therefore its own store.

## Dependencies

- `crate::memory` — `Memory` trait, `MemoryCategory`, `memory::binding::{for_config, for_subtree}` (driver binding behind `DriverMemory`), `memory::api::{provider, recall, types, health}` (the provider contract `DriverMemory` adapts), `memory::safety::sanitize_text` (store-time scrub), `memory::source_scope::as_bus_scope` (explicit recall scope), `memory::preferences::recall_by_vector_over`.
- `crate::config` — `Config::load_or_init` for `workspace_dir` and `subsystems.memory` when the RPC handlers bind a store.
- `crate::agent::profiles` — `load_profiles`, `effective_memory_suffix`, `memory_subdir_for_suffix` to map a `profile_id` to its memory subtree.
- `crate::agent::hooks` — `PostTurnHook`, `TurnContext`, `ToolCallRecord` (capture hook contract / turn inputs).
- `crate::core::all` — `ControllerFuture`, `RegisteredController` for RPC registration.
- `crate::core` — `ControllerSchema`, `FieldSchema`, `TypeSchema` (schema types); `crate::rpc::RpcOutcome`.
- `crate::memory::tool_memory::test_helpers::MockMemory` and `crate::memory::guard::test_support::RecordingProvider` — tests only.

## Used by

- `crates/openhuman-core/src/core/all.rs` — registers controllers/schemas and the namespace description.
- `crates/openhuman-core/src/agent/mod.rs` — declares `pub mod experience`.
- `crates/openhuman-core/src/agent/harness/session/builder/factory.rs` — binds the session's `Arc<dyn Memory>` with `DriverMemory::for_subtree`, resolves `shared_experience_memory` with `DriverMemory::for_config` for dedicated-memory profiles, and registers `AgentExperienceCaptureHook::with_profile(...)` when `config.learning.enabled && config.learning.tool_memory_capture_enabled`.
- `crates/openhuman-core/src/agent/harness/session/turn/core/experience_context.rs` — defines `Agent::inject_agent_experience_context`, which queries the session store plus the shared store with `retrieve_across_stores` (max 3 hits, 2048-byte block, gated on `learning_enabled`) and prepends the block to the enriched user message. Called from `turn/core_turn.rs`.
- `crates/openhuman-core/src/agent/tinyagents/host/experience_store.rs` — host adapter implementing `tinyagents_harness::host::ExperienceStore` over `AgentExperienceStore`.
- `crates/openhuman-core/src/config/migration_helpers/core.rs` — uses `DriverMemory::for_config` to bind the import target.

## Notes / gotchas

- **Two redaction layers at write time**: `capture::build_experience` masks `Bearer …`, `sk-…`, and `token=/password:` pairs with `types::redact_text`; `store::put` then runs the full `memory::safety::sanitize_text` scrubber (private keys, vendor secrets, national-ID / phone / card PII) over the free-text fields. The base64 payload means the memory layer's own content scrub is a no-op, so the store-level scrub is what preserves the invariant.
- Retrieval scoring is **lexical, not embedding-based**: term sets keep only tokens length > 2, normalized lowercase; score combines tool overlap (weighted highest), tag overlap, query-term overlap over summary+lesson+hints, plus small agent/entrypoint match boosts and a confidence prior. `max_hits == 0` short-circuits to empty. The live-turn path additionally drops hits with no `match_reasons`.
- `render_experience_hits` is hard byte-capped (`max_bytes`) with UTF-8-boundary-safe truncation, so the injected prompt block can't blow the context budget.
- The capture hook is gated by an `enabled` flag passed at construction; when disabled `on_turn_complete` is a no-op, and capture failures only `log::warn!` (never fail the turn).
- `DriverMemory` wraps the driver, not `MemoryGuard`, on purpose: the guard truncates `store` content at `capture_max_chars`, and truncated base64 does not decode. Its `ops.rs` rustdoc notes it belongs next to `memory::binding` and only sits here because both callers do.
