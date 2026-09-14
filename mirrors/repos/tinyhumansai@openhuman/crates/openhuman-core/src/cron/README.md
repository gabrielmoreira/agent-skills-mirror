# Cron

Scheduled-job runtime. Owns cron-expression and human-delay parsing, the persistent job + run store, the polling scheduler that fires due jobs (`shell`, `agent`, and `flow` types), and the delivery layer that publishes events into the agent / channel pipelines. Does NOT own shell sandboxing (`security::SecurityPolicy`) or flow trigger dispatch (`flows::bus::FlowTriggerSubscriber`).

## Public surface

- `pub struct CronJob` / `pub struct CronJobPatch` / `pub struct CronRun` / `pub struct ActiveHours` / `pub enum JobType` / `pub enum Schedule` (`Cron` / `At` / `Every`) / `pub enum SessionTarget` / `pub struct DeliveryConfig` — `types.rs` — durable job + run model.
- `pub fn add_once` / `pub fn add_once_at` / `pub fn parse_human_delay` / `pub fn pause_job` / `pub fn resume_job` / `pub fn update_cron_job` — `ops.rs` (also re-exported as `pub use ops as rpc`).
- `pub fn schedule_cron_expression` / `pub fn next_run_for_schedule` / `pub fn normalize_expression` / `pub fn validate_schedule` / `pub fn validate_agent_schedule` / `pub fn runs_closer_than` / `pub struct TooFrequent` / `pub const MIN_AGENT_JOB_INTERVAL` — `schedule.rs`.
- `pub fn add_job` / `pub fn add_agent_job` / `pub fn add_agent_job_with_definition` / `pub fn add_shell_job` / `pub fn add_flow_schedule_job` / `pub fn find_flow_schedule_job` / `pub fn due_jobs` / `pub fn get_job` / `pub fn list_jobs` / `pub fn list_runs` / `pub fn record_last_run` / `pub fn record_run` / `pub fn remove_job` / `pub fn reschedule_after_run` / `pub fn update_job` — `store.rs`, split into submodules `store/jobs.rs`, `store/runs.rs`, `store/schema.rs`.
- `pub mod scheduler` (`pub async fn run(config: Config)`, `pub async fn execute_job_now` for the `cron.run` "Run Now" path) — `scheduler.rs`, split into submodules `scheduler/failure_classification.rs` (failure classifiers), `scheduler/retry.rs` (`execute_job_now`, `execute_job_with_retry`), `scheduler/agent_run.rs` (`run_agent_job`, `build_agent_for_cron_job`, `run_flow_schedule_job`), `scheduler/delivery.rs` (`deliver_if_configured`), `scheduler/shell_job.rs` (`run_job_command_with_timeout`), and `scheduler/run_record.rs`; the poll loop and `run` stay in `scheduler.rs` itself.
- `pub mod scheduler_gate` — throttles *background* LLM work (memory digests, embeddings, summarisation) on host power / CPU signals via `current_policy()` / `wait_for_capacity()`. It lives here for historical reasons; the cron poll loop does not consult it, and its consumers are `modules/memory_host.rs` and `security/credentials/`. See its own [README](scheduler_gate/README.md).
- `pub mod seed` — `seed.rs` — `seed_proactive_agents` installs the built-in proactive jobs when onboarding flips to completed (`config/ops/ui.rs`); `prune_retired_jobs` removes rows for removed features on boot and workspace activation.
- `pub mod bus` — `bus.rs` — `CronDeliverySubscriber` (`cron::delivery`) consumes `CronDeliveryRequested` and sends through the named `tinychannels_bus::Channel`.
- `pub mod tools` — `tools.rs` + `tools/` — agent-facing tools: `CronAddTool`, `CronListTool`, `CronUpdateTool`, `CronRemoveTool`, `CronRunTool`, `CronRunsTool`, and the collapsed `CronTool` / `CRON_TOOL_NAME`. `tools/collapsed.rs` explains why the six stay registered as hidden schemas behind the one advertised tool; see also [tools/README.md](tools/README.md).
- RPC namespace `cron`: `add`, `list`, `update`, `remove`, `run`, `runs` — `schemas.rs` (aggregated as `all_cron_controller_schemas` / `all_cron_registered_controllers`).

## Job types

- **`shell`** — `run_job_command_with_timeout` refuses the command unless the `SecurityPolicy` (`SecurityPolicy::from_config`, built once in `scheduler::run` and per call in `execute_job_now`) passes `can_act`, `is_rate_limited`, and `is_command_allowed`; a `blocked by security policy:` result is never retried.
- **`agent`** — the scheduler builds an `Agent` directly and runs a turn (see below); it does not go through `agent::triage`.
- **`flow`** — a `flows::Flow` schedule-trigger binding. `flows/ops/triggers.rs::bind_schedule_trigger` creates it via `add_flow_schedule_job` (idempotent through `find_flow_schedule_job`) from both `flows_set_enabled` and `reconcile_schedule_triggers_on_boot`. Its `command` column carries the bound flow's id; on fire `run_flow_schedule_job` publishes `DomainEvent::FlowScheduleTick { flow_id }` instead of running anything itself. `flows::bus::FlowTriggerSubscriber` does the actual dispatch. Never created via the `cron_add` agent tool, whose `job_type` enum is `shell` / `agent` only.

### Agent jobs

`run_agent_job` prefixes the prompt (`[cron:<id> <name>] <prompt>`), applies a per-job `model` override to a cloned `Config`, and, when `job.agent_id` names a definition in `AgentDefinitionRegistry`, resolves that definition's `ModelSpec` onto the cloned config (the iteration cap is left to the session builder, see #4868). `build_agent_for_cron_job` then picks the constructor: `Agent::from_config_for_agent_with_profile` when `job.profile_id` still resolves through `agent::profiles::load_profiles` (the same profile-aware path the task dispatcher uses, so the run inherits the profile's SOUL, memory scope, and tool/skill/MCP allowlists), `Agent::from_config_for_agent` when only `agent_id` is set (falling back to `Agent::from_config` if the definition fails to build), or `Agent::from_config` otherwise. A deleted profile is warned about and the job runs profile-less.

`execute_job_with_retry` wraps every job type with `config.reliability.scheduler_retries` attempts and exponential backoff. For agent jobs it classifies failures before retrying: backend session-expired, provider insufficient-credits (402), managed-backend budget-exhausted (400), API-key-unset, and local-LLM-unreachable all halt the loop immediately and suppress the retries-exhausted error report. The user-facing message is a canned string from `classify_agent_anyhow_for_user`; the raw error goes only to observability.

## Event bus

Cron publishes through `core/bus.rs` using variants declared in `core/events.rs`: `DomainEvent::CronJobTriggered` and `CronJobCompleted` (around each execution), `CronDeliveryRequested` and `ProactiveMessageRequested` (from `deliver_if_configured`; the latter is shared with the proactive-message pipeline), and `FlowScheduleTick`.

## Calls into

- `crates/openhuman-core/src/agent/` — `Agent::from_config[_for_agent[_with_profile]]` for agent jobs; `agent::harness::definition::AgentDefinitionRegistry` to resolve `agent_id`; `agent::profiles::load_profiles` to resolve `profile_id`.
- `crates/openhuman-core/src/security/` — `SecurityPolicy::from_config` gates shell jobs.
- `crates/openhuman-core/src/config/` — `Config` provides poll interval, workspace dir, autonomy policy, retry counts, and per-job model overrides.
- `crates/openhuman-core/src/inference/` — `provider::create_chat_model_with_model_id` resolves workload-hint model specs on agent-definition overrides.
- `crates/openhuman-core/src/platform/health/` — `health::bus::register_health_subscriber` on scheduler startup.
- `crates/openhuman-core/src/core/bus.rs` / `core/events.rs` — the process-wide event bus and `DomainEvent` variants cron publishes.

## Called by

- `crates/openhuman-core/src/core/runtime/services.rs` — spawns `cron::scheduler::run` as the `cron` background service (`ServiceSet::cron`).
- `crates/openhuman-core/src/core/all.rs` — controller registry wires `all_cron_registered_controllers`.
- `crates/openhuman-core/src/tools/impl/system/schedule.rs` — the `schedule` tool exposes recurring and one-shot scheduling to agents on top of `cron::{list_jobs, get_job, …}`.
- `crates/openhuman-core/src/channels/runtime/startup/start_channels.rs` — registers `cron::bus::CronDeliverySubscriber` with the channel map; `channels::proactive::ProactiveMessageSubscriber` handles `ProactiveMessageRequested`.
- `crates/openhuman-core/src/flows/ops/triggers.rs` — `bind_schedule_trigger` / `unbind_schedule_trigger` create and remove flow schedule jobs; `flows::bus::FlowTriggerSubscriber` consumes `FlowScheduleTick`.
- `crates/openhuman-core/src/config/ops/ui.rs`, `desktop/app_state/`, `security/credentials/` — call `seed::seed_proactive_agents` / `seed::prune_retired_jobs`.

## Delivery modes

A cron job's `DeliveryConfig.mode` decides where its output ends up. `DeliveryConfig::default()` is `none`; the `cron_add` tool substitutes `proactive` when an agent job is created without a `delivery` block.

- **`proactive`** — `deliver_if_configured` publishes
  `DomainEvent::ProactiveMessageRequested`. The proactive subscriber
  (`channels::proactive`) always pushes to the in-app web stream and additionally
  mirrors to `channels_config.active_channel` when set. Use for jobs whose
  natural surface is the desktop UI (briefings, app-pushed notifications).
- **`announce`** — explicit channel-targeted delivery. Requires `channel` and
  `to`; publishes `DomainEvent::CronDeliveryRequested` and lands only in that
  channel. The agent layer should pick this mode when a cron is created from a
  non-web channel (Telegram, Discord, Slack, …) so the reminder ends up where
  the user asked for it. The `cron_add` tool validates `to` against the
  channel's `allowed_users` to reject cross-tenant targets.
- **`none`** — silent; output is stored in `last_output` only.

The `[Channel context]` block built in `channels/runtime/dispatch/helpers.rs`
for non-web inbound turns instructs the model to default to `announce` with the
current channel + reply target — that is the routing path for the Telegram
"remind me to drink water" use case in #928.

## Agent-job minimum interval

An agent job is a full inference turn per run, so `schedule.rs` enforces a floor
of `MIN_AGENT_JOB_INTERVAL` (5 minutes) between consecutive runs of an agent job.
`validate_agent_schedule` is applied in `store.rs` by `add_agent_job*` and by
`update_job` whenever an agent job's schedule is set, so every creation path
(`cron_add` tool, `cron.add` / `cron.update` RPC, the `schedule` tool) gets the
same rejection, and the message names the two runs that would be too close.
Shell and flow jobs are not subject to it.

The check is `runs_closer_than`: it walks consecutive occurrences (bounded) and
reports the first pair closer than the floor, so an irregular expression such as
`1,2,30 * * * *` is judged by its tightest gap and the verdict does not depend
on the instant it runs at. Wrap-around gaps count: `*/7 * * * *` fires at :56
and then at :00. Rows that predate the floor keep running; the scheduler logs
`Cron agent job '<id>' is scheduled more frequently than every 5 minutes` with
that evidence on each run instead (#6158).

## Tests

- Unit: `ops_tests.rs`, `scheduler_tests.rs` (shared fixtures; `#[path]`-includes `scheduler_profile_and_shell_tests.rs`, `scheduler_halt_and_persist_tests.rs`, `scheduler_classifier_and_delivery_tests.rs`, `scheduler_frequency_tests.rs`), `store_tests.rs` (+ `store_agent_floor_tests.rs`), `schedule_tests.rs`, `types_tests.rs`, `seed_tests.rs`, `bus_tests.rs`.
- Schema/parsing coverage lives in `schemas_tests.rs`.
- Tool coverage: `tools/{add,list,remove,run,runs,update}_tests.rs` (announce-mode `allowed_users` checks live in `add_tests.rs`) and `tools/collapsed_tests.rs` (action enum, merged schema, per-action permission resolution).
