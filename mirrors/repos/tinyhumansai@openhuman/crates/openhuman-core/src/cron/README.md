# Cron

Scheduled-job runtime. Owns cron-expression and human-delay parsing, the persistent job + run store, the polling scheduler that fires due jobs (`shell`, `agent`, and `flow` types), and the delivery layer that publishes events into the agent / channel pipelines. Does NOT own shell sandboxing (`security::SecurityPolicy`) or flow trigger dispatch (`flows::bus::FlowTriggerSubscriber`).

## Public surface

- `pub struct CronJob` / `pub struct CronJobPatch` / `pub struct CronRun` / `pub struct ActiveHours` / `pub enum JobType` / `pub enum Schedule` (`Cron` / `At` / `Every`) / `pub enum SessionTarget` (`Isolated` / `Current` / `Main`) / `pub enum JobOrigin` (`Web` / `Channel`) / `pub enum DeliveryStatus` / `pub struct DeliveryConfig`: `types.rs`: durable job + run model.
- `pub fn add_once` / `pub fn add_once_at` / `pub fn parse_human_delay` / `pub fn pause_job` / `pub fn resume_job` / `pub fn update_cron_job`: `ops.rs` (also re-exported as `pub use ops as rpc`).
- `pub fn schedule_cron_expression` / `pub fn next_run_for_schedule` / `pub fn normalize_expression` / `pub fn validate_schedule` / `pub fn validate_agent_schedule` / `pub fn runs_closer_than` / `pub struct TooFrequent` / `pub const MIN_AGENT_JOB_INTERVAL`: `schedule.rs`.
- `pub fn add_job` / `pub fn add_agent_job` / `pub fn add_agent_job_with_definition` / `pub fn add_shell_job` / `pub fn add_flow_schedule_job` / `pub fn find_flow_schedule_job` / `pub fn due_jobs` / `pub fn get_job` / `pub fn list_jobs` / `pub fn list_runs` / `pub fn record_last_run` / `pub fn record_run` / `pub fn remove_job` / `pub fn reschedule_after_run` / `pub fn update_job`: `store.rs`, a thin `Config` -> `CronStoreOptions` wrapper over `tinyflows_sqlite::schedule` (schema, job CRUD and run history live upstream).
- `pub mod scheduler` (`pub async fn run(config: Config)`, `pub async fn execute_job_now` for the `cron.run` "Run Now" path): `scheduler.rs`, split into submodules `scheduler/failure_classification.rs` (failure classifiers), `scheduler/retry.rs` (`execute_job_now`, `execute_job_with_retry`), `scheduler/agent_run.rs` (`run_agent_job`, `build_agent_for_cron_job`, `run_flow_schedule_job`), `scheduler/delivery.rs` (`deliver_run`, `deliver_job`), `scheduler/origin_context.rs` (the prompt of a `current` run), `scheduler/origin_delivery.rs` (`delivery.mode = "origin"`), `scheduler/shell_job.rs` (`run_job_command_with_timeout`), and `scheduler/run_record.rs`; the poll loop and `run` stay in `scheduler.rs` itself.
- `pub mod scheduler_gate`: throttles *background* LLM work (memory digests, embeddings, summarisation) on host power / CPU signals via `current_policy()` / `wait_for_capacity()`. It lives here for historical reasons; the cron poll loop does not consult it, and its consumers are `modules/memory_host.rs` and `security/credentials/`. See its own [README](scheduler_gate/README.md).
- `pub mod seed`: `seed.rs`: `seed_proactive_agents` installs the built-in proactive jobs when onboarding flips to completed (`config/ops/ui.rs`); `prune_retired_jobs` removes rows for removed features on boot and workspace activation.
- `pub mod origin` / `pub mod job_builder` / `pub mod channel_bridge`: the conversation a job was created from. `origin.rs` captures a `JobOrigin` from the live `AgentTurnOrigin`, decides whether a creation call may skip the approval gate, and picks the turn origin a run executes under; `job_builder.rs` is the one path (`create_agent_job`) the `cron` and `schedule` tools both use to build agent jobs with origin-aware defaults and delivery validation; `channel_bridge.rs` is cron's handle on the channel runtime (per-chat history and live channels, registered by `start_channels`).
- `pub mod bus`: `bus.rs`: `CronDeliverySubscriber` (`cron::delivery`) consumes `CronDeliveryRequested` and sends through the named `tinychannels_bus::Channel`.
- `pub mod tools`: `tools.rs` + `tools/`: agent-facing tools: `CronAddTool`, `CronListTool`, `CronUpdateTool`, `CronRemoveTool`, `CronRunTool`, `CronRunsTool`, and the collapsed `CronTool` / `CRON_TOOL_NAME`. `tools/collapsed.rs` explains why the six stay registered as hidden schemas behind the one advertised tool; see also [tools/README.md](tools/README.md).
- RPC namespace `cron`: `add`, `list`, `update`, `remove`, `run`, `runs`: `schemas.rs` (aggregated as `all_cron_controller_schemas` / `all_cron_registered_controllers`).

## Job types

- `shell`: `run_job_command_with_timeout` refuses the command unless the `SecurityPolicy` (`SecurityPolicy::from_config`, built once in `scheduler::run` and per call in `execute_job_now`) passes `can_act`, `is_rate_limited`, and `is_command_allowed`; a `blocked by security policy:` result is never retried.
- `agent`: the scheduler builds an `Agent` directly and runs a turn (see below); it does not go through `agent::triage`.
- `flow`: a `flows::Flow` schedule-trigger binding, the mechanism behind a workflow's [schedule trigger](../../../../gitbooks/features/workflows.md). `flows/ops/triggers.rs::bind_schedule_trigger` creates it via `add_flow_schedule_job` (idempotent through `find_flow_schedule_job`) from both `flows_set_enabled` and `reconcile_schedule_triggers_on_boot`. Its `command` column carries the bound flow's id; on fire `run_flow_schedule_job` publishes `DomainEvent::FlowScheduleTick { flow_id }` instead of running anything itself. `flows::bus::FlowTriggerSubscriber` does the actual dispatch. Never created via the `cron_add` agent tool, whose `job_type` enum is `shell` / `agent` only.

### Agent jobs

`run_agent_job` prefixes the prompt (`[cron:<id> <name>] <prompt>`), applies a per-job `model` override to a cloned `Config`, and, when `job.agent_id` names a definition in `AgentDefinitionRegistry`, resolves that definition's `ModelSpec` onto the cloned config (the iteration cap is left to the session builder, see #4868). `build_agent_for_cron_job` uses `Agent::from_config_for_agent` for a recognized `agent_id`, falling back to `Agent::from_config` when it cannot build a definition or no id was supplied.

`execute_job_with_retry` wraps every job type with `config.reliability.scheduler_retries` attempts and exponential backoff. For agent jobs it classifies failures before retrying: backend session-expired, provider insufficient-credits (402), managed-backend budget-exhausted (400), API-key-unset, and local-LLM-unreachable all halt the loop immediately and suppress the retries-exhausted error report. The user-facing message is a canned string from `classify_agent_anyhow_for_user`; the raw error goes only to observability.

## Event bus

Cron publishes through `core/bus.rs` using variants declared in `core/events.rs`: `DomainEvent::CronJobTriggered` and `CronJobCompleted` (around each execution), `CronDeliveryRequested` and `ProactiveMessageRequested` (from `deliver_if_configured`; the latter is shared with the proactive-message pipeline), and `FlowScheduleTick`.

## Calls into

- `crates/openhuman-core/src/agent/`: `Agent::from_config_for_agent` for agent jobs and `agent::harness::definition::AgentDefinitionRegistry` to resolve `agent_id`.
- `crates/openhuman-core/src/security/`: `SecurityPolicy::from_config` gates shell jobs.
- `crates/openhuman-core/src/config/`: `Config` provides poll interval, workspace dir, autonomy policy, retry counts, and per-job model overrides.
- `crates/openhuman-core/src/inference/`: `provider::create_chat_model_with_model_id` resolves workload-hint model specs on agent-definition overrides.
- `crates/openhuman-core/src/platform/health/`: `health::bus::register_health_subscriber` on scheduler startup.
- `crates/openhuman-core/src/core/bus.rs` / `core/events.rs`: the process-wide event bus and `DomainEvent` variants cron publishes.

## Called by

- `crates/openhuman-core/src/core/runtime/services.rs`: spawns `cron::scheduler::run` as the `cron` background service (`ServiceSet::cron`).
- `crates/openhuman-core/src/core/all.rs`: controller registry wires `all_cron_registered_controllers`.
- `crates/openhuman-core/src/tools/impl/system/schedule.rs`: the `schedule` tool exposes recurring and one-shot scheduling to agents on top of `cron::{list_jobs, get_job, …}`.
- `crates/openhuman-core/src/channels/runtime/startup/start_channels.rs`: registers `cron::bus::CronDeliverySubscriber` with the channel map; `channels::proactive::ProactiveMessageSubscriber` handles `ProactiveMessageRequested`.
- `crates/openhuman-core/src/flows/ops/triggers.rs`: `bind_schedule_trigger` / `unbind_schedule_trigger` create and remove flow schedule jobs; `flows::bus::FlowTriggerSubscriber` consumes `FlowScheduleTick`.
- `crates/openhuman-core/src/config/ops/ui.rs`, `desktop/app_state/`, `security/credentials/`: call `seed::seed_proactive_agents` / `seed::prune_retired_jobs`.

## Delivery modes

A cron job's `DeliveryConfig.mode` decides where its output ends up. `DeliveryConfig::default()` is `none`; the `cron` / `schedule` tools substitute `origin` when an agent job is created inside a conversation and `proactive` otherwise.

- `proactive`: `deliver_if_configured` publishes
  `DomainEvent::ProactiveMessageRequested`. The proactive subscriber
  (`channels::proactive`) always pushes to the in-app web stream and additionally
  mirrors to `channels_config.active_channel` when set. Use for jobs whose
  natural surface is the desktop UI (briefings, app-pushed notifications).
- `announce`: explicit channel-targeted delivery. Requires `channel` and
  `to`; publishes `DomainEvent::CronDeliveryRequested` and lands only in that
  channel. The agent layer should pick this mode when a cron is created from a
  non-web channel (Telegram, Discord, Slack, …) so the reminder ends up where
  the user asked for it. The `cron_add` tool validates `to` against the
  channel's `allowed_users` to reject cross-tenant targets.
- `origin`: commit the run's reply into the conversation that created the job
  and send it there once (`scheduler/origin_delivery.rs`). Requires
  `CronJob.origin`. Output that is blank or exactly `NO_REPLY` is
  `Suppressed`: nothing is sent and no alert is raised. A web origin stores the
  reply in the origin thread under `run_reply_message_id("cron:<job>:<run>")`,
  then emits the web-channel `proactive_message` event with `thread_id` set to
  that thread and `request_id = "cron:<job>:<run>"`, then appends it to the
  thread's agent transcript (`append_to_origin_transcript`, idempotent on the
  same key, waits out a live turn of the session). A channel origin sends to
  the origin's `reply_target` through `cron::channel_bridge` and appends the
  reply to that chat's `conversation_histories` entry. Each run records a
  `DeliveryStatus` (`delivered` / `suppressed` / `failed` / `not_requested`)
  on its `CronRun`.
- `none`: silent; output is stored in `last_output` only.

## Origin and session targets

A job created by an agent inside a conversation records that conversation
(`JobOrigin::Web { thread_id }` from a `WebChat` turn, `JobOrigin::Channel {
channel, reply_target, history_key, sender }` from the channel processor's
`ExternalChannel` turn; other origins record none). With an origin, an agent job
defaults to `session_target: current` and `delivery: origin`; without one it
keeps `isolated` + `proactive`. An explicit `delivery` or `session_target`
always wins, and an `announce` whose `to` is the origin's reply target on the
same channel skips the `allowed_users` check.

- `isolated`: a fresh run, prompt `[cron:<id> <name>] <prompt>`.
- `current`: a fresh run whose prompt carries an unattended-run preamble
  (final reply is delivered as-is; `NO_REPLY` skips delivery) and a bounded
  tail of the origin conversation (last 10 messages, 1400 characters, newest
  kept; web from the thread store, channel from the chat history).
- `main`: runs like `current` for now (not yet a distinct main session).

**Trust.** A job with a channel origin runs under
`AgentTurnOrigin::ExternalChannel { message_id: "cron:<job>:<run>" }`, not
`TrustedAutomation`, so its external-effect tools stay gated like its creator's.
Creating such a job needs no approval only when the turn is a channel
conversation, the job is an agent job with no shell `command`, and its delivery
resolves to that same conversation (no `delivery`, `origin`, or a matching
`announce`); `CronAddTool` / `ScheduleTool` express that through
`external_effect_with_args`. Everything else (shell jobs, other recipients,
`proactive`/`none`, non-channel turns) is gated as before (GHSA-f46p-6vf9-64mm).
Web-origin and origin-less jobs keep `TrustedAutomation { Cron }`.

The scheduler loop skips a job already in `ACTIVE_RUNS` (and holds the claim
for scheduled runs), so Run Now and a tick never overlap. The `[Channel context]`
block in `channels/runtime/dispatch/helpers.rs` only tells the model that
reminders created in the chat come back to it automatically.

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

- Unit: `ops_tests.rs`, `scheduler_tests.rs` (shared fixtures; `#[path]`-includes `scheduler_profile_and_shell_tests.rs`, `scheduler_halt_and_persist_tests.rs`, `scheduler_classifier_and_delivery_tests.rs`, `scheduler_frequency_tests.rs`), `store_tests.rs` (Config-to-options mapping; the store itself is tested in `tinyflows-sqlite`), `schedule_tests.rs`, `types_tests.rs`, `seed_tests.rs`, `bus_tests.rs`.
- Schema/parsing coverage lives in `schemas_tests.rs`.
- Tool coverage: `tools/{add,list,remove,run,runs,update}_tests.rs` (announce-mode `allowed_users` checks live in `add_tests.rs`) and `tools/collapsed_tests.rs` (action enum, merged schema, per-action permission resolution).
