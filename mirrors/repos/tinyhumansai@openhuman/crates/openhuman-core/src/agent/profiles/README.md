# profiles

Persistent, user-selectable agent "flavours". A profile carries a name,
description, an `agent_id`, runtime defaults (model override, temperature,
system-prompt suffix, SOUL.md), and configurable allowlists for tools, skills,
MCP servers, Composio integrations, and memory sources. Selecting a profile
changes how the agent introduces itself, what it remembers, and what it can do.
State persists under `<workspace>/agent_profiles.json`; the module also owns
each profile's on-disk "home" (identity/memory files under `workspace_dir`,
optional dedicated workspace under `action_dir`) and the guard that keeps
dedicated-workspace profiles from writing into a sibling's directory.

## Responsibilities

- Define the `AgentProfile` / `AgentProfilesState` serde types and the
  built-in profile set (`default`, `reasoning`, `research`, `planner`,
  `review`).
- Persist and normalise profile state (`AgentProfileStore`): merge built-ins
  into any loaded/saved state, slugify ids, drop empty allowlist entries to
  `None`, auto-assign a stable numeric `memory_dir_suffix` to new custom
  profiles, and pin non-dedicated built-ins back to the shared memory subtree
  on every load/save.
- Materialize and reconcile each profile's on-disk "home" — `SOUL.md`,
  `MEMORY.md`, a private `skills/` dir, and (opt-in) a dedicated workspace.
- Resolve profile-scoped paths for prompt building: which SOUL.md content and
  MEMORY.md to use, the effective memory subtree suffix, and a session
  signature that changes when a profile's resolved inputs change.
- Enforce the cross-profile write guard: block a dedicated-workspace profile's
  tool calls from targeting a sibling profile's workspace.
- Expose the `profiles` RPC namespace (list/select/upsert/delete), wired into
  the core registry.

## Key files

| File | Role |
| --- | --- |
| `mod.rs` | Module docs, `mod` decls, and the re-export surface. |
| `types.rs` | `AgentProfile`, `AgentProfilesState`, `DEFAULT_PROFILE_ID`, `profile_signature` (a serialized cache key for prompt construction). |
| `store.rs` | `AgentProfileStore` (load/save/select/upsert/delete/resolve) over `<workspace>/agent_profiles.json`; `built_in_profiles`, `load_profiles`, id normalisation/slugification (`normalise_profile_id`, applied before `validate_profile_id` on every `upsert`), and the numeric `memory_dir_suffix` allocator. `delete` refuses built-in ids. |
| `home.rs` | Per-profile home materialization: `profile_home`, `profile_action_workspace`, `profile_skills_dir`/`profile_skills_root`, `validate_profile_id`, `ensure_profile_home` (idempotent seed), `sync_soul_md_on_upsert` (reconcile an edited inline soul into the on-disk file), `dedicated_workspace_dir`. |
| `paths.rs` | Personality-scoped path/content resolution: `resolve_personality_soul` (home `SOUL.md` → `soul_md_path` → inline `soul_md` → `None`), `resolve_personality_memory_md`, `effective_memory_suffix`, the `*_subdir_for_suffix` helpers, `profile_session_signature`, `PersonalityContext`, `filter_integrations`/`HasToolkit`, and the `pub(crate)` `soul_md_file_path` shared with the channel runtime's identity fingerprint. |
| `guard.rs` | Cross-profile identity plumbing and write guard: `workspace_policy_id`/`profile_id_from_policy_id` (encode/decode the `openhuman.profile:<id>` `WorkspaceDescriptor::policy_id`; only the encoder has a non-test caller, in the session builder), `classify_cross_profile_target` (file tools), `scan_command_for_cross_profile` (shell/process tools, best-effort), `PROFILES_ROOT_SENTINEL`. |
| `prompt_section.rs` | `AgentProfilePromptSection` (a `PromptSection` named `agent_profile`), `render_agent_profile_block` (the same `## Agent profile` text for prompt paths without a `PromptContext`, used by `channels/system_prompt.rs`), and `cross_profile_workspace_notice`. |
| `ops.rs` | `list`/`select`/`upsert`/`delete` business logic: `agent_id` validation against the global agent registry, home materialization, SOUL.md reconciliation, and read-only path enrichment (`soulMdFile`, `skillsDir`, `workspaceDir`) on the returned payload. |
| `schemas.rs` | Controller schemas + thin handlers for the `profiles` namespace; re-exported as `all_profiles_controller_schemas` / `all_profiles_registered_controllers`. |
| `*_tests.rs` | Sibling test suites per file (via `#[path]`). |

## Profile home layout (hermes-agent style)

```text
<workspace>/personalities/<id>/SOUL.md              identity (hot-read each prompt)
<workspace>/personalities/<id>/MEMORY.md            curated per-profile memory
<workspace>/personalities/<id>/skills/              private skills (owner-only discovery)
<workspace>/{memory,memory_tree,session_raw}-<id>/  dedicated memory subtree (opt-in)
<action_dir>/profiles/<id>/                         agent-writable workspace (opt-in)
```

Identity/memory files live under `workspace_dir`, which the agent's write
tools cannot reach; the writable working dir lives under `action_dir`, which
acting tools are allowed to touch. `SOUL.md` is re-read on every prompt build
so identity edits take effect live. `dedicated_memory` derives a `-<id>`
suffix and wins over the auto-assigned numeric suffix; `dedicated_workspace`
roots a per-profile default cwd for acting tools. `ensure_profile_home` never
overwrites a user's edited files.

## RPC / controllers

Namespace `profiles`, registered via `all_profiles_registered_controllers()`.
On the JSON-RPC wire the methods are `openhuman.profiles_list`,
`openhuman.profiles_select`, `openhuman.profiles_upsert`, and
`openhuman.profiles_delete` (`core::all::rpc_method_name`).

| Controller | Inputs | Output |
| --- | --- | --- |
| `profiles.list` | — | `{ profiles, activeProfileId }`, each profile enriched with `soulMdFile`/`skillsDir`/`workspaceDir` when present on disk |
| `profiles.select` | `profile_id: string` | updated state payload |
| `profiles.upsert` | `profile: AgentProfile` (camelCase JSON) | updated state payload |
| `profiles.delete` | `profile_id: string` | updated state payload; built-in ids are rejected |

`upsert` fails closed on a non-empty, non-`orchestrator` `agent_id` when the
global `AgentDefinitionRegistry` is not yet initialised, rather than persist a
reference it cannot validate. Built-in profiles have their home materialized
on first `select`; custom profiles are materialized on `upsert`. Soul edits are
reconciled into the on-disk `SOUL.md` on every `upsert`, built-in included.

## Cron attribution

A cron job may carry a `profile_id` (`cron::CronJob::profile_id`). When set and
the profile still exists, the scheduled run is built under that profile (soul,
memory scope, dedicated workspace, allowlists) via the same profile-aware
session path the task dispatcher uses; a deleted profile falls back to a
profile-less run rather than failing the job.

## Used by

- `crates/openhuman-core/src/core/all.rs` registers the controllers.
- `agent/harness/session/builder/factory.rs` is the primary consumer: resolves
  memory suffix/subdirs, soul/memory content, the dedicated workspace
  descriptor (`workspace_policy_id`), the cross-profile prompt notice, and
  integration filtering when building a session.
- `agent/harness/session/turn/tools.rs` resolves `profile_skills_root` for
  workflow discovery.
- `security/policy/path_checks.rs` (file tools) calls
  `classify_cross_profile_target` once the session builder has armed
  `SecurityPolicy::with_active_profile(profile_id, action_dir)`;
  `tools/impl/system/mod.rs` (process tools) classifies the cwd and then adds
  `scan_command_for_cross_profile`. Both map `PROFILES_ROOT_SENTINEL` to a
  root-specific `[policy-blocked]` denial.
- `cron/scheduler/agent_run.rs` resolves a job's attributed profile via
  `load_profiles` and builds the run with
  `Agent::from_config_for_agent_with_profile`.
- `agent/task_dispatcher/executor.rs` and
  `agent/tools/delegate_to_personality.rs` build a `PersonalityContext` for the
  target profile; `agent/tools/run_workflow.rs`, `skills/tools.rs`,
  `skills/runtime/run_machinery.rs`, and `tools/ops.rs` thread the active
  `AgentProfile` through skill listing and execution. `skills/ops_discover.rs`
  does not import this module: it receives the already-resolved
  `profile_skills_root` path (`discover_workflows_with_profile`,
  `load_workflow_metadata_for_profile`).
- `agent/experience/ops.rs` maps profiles to memory subdirs with
  `effective_memory_suffix` / `memory_subdir_for_suffix`.
- `channels/system_prompt.rs` resolves soul/memory content and
  `soul_md_file_path` for the native channel runtime and renders the block via
  `render_agent_profile_block`; `web_chat/session.rs` stores
  `profile_session_signature` for cache invalidation; `web_chat/run_task.rs`
  reads the store.
- `agent/tinyagents/host/definition_registry.rs` reads
  `AgentProfile::model_override` through its `ModelResolver` adapter.

## Notes / gotchas

- `validate_profile_id` (hermes grammar `^[a-z0-9][a-z0-9_-]{0,63}$`) gates
  every home read/write path and every store `upsert`; a legacy id that fails
  validation still loads from the JSON store but gets no home, no dedicated
  workspace, no dedicated-memory suffix, and no profile-local skills — reads
  and writes stay symmetric. The `home.rs` doc comment saying it is "only
  enforced when creating a new custom profile" understates this.
- `scan_command_for_cross_profile` is explicitly best-effort defense in depth
  for process tools (static token scan, not a real shell parser); the hard
  boundary for file mutations is `SecurityPolicy::validate_path`.
- The mod-level doc comment's "Relocated from `openhuman::agent::profiles` /
  `::personality_paths`" line dates from the original domain split (#3632),
  when `agent/profiles.rs` and `agent/personality_paths.rs` were merged into
  this directory; it predates the crate flattening. The module is addressed as
  `crate::agent::profiles` in-crate (`openhuman::agent::profiles` from outside).
