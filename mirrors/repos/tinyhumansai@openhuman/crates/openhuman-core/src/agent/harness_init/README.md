# harness_init

First-run provisioning orchestration. Several setup steps (managed Python
runtime, spaCy + model, Kompress/torch, the runtime Python server, managed
Node) used to run lazily on first use with no user-visible feedback. This
domain runs them eagerly at core startup without blocking the ready signal,
tracks per-step progress in an in-memory snapshot, and exposes it over
`openhuman.harness_init_status` / `openhuman.harness_init_run` for the
frontend's initialization screen (`app/src/services/harnessInitService.ts`).

Steps delegate to existing idempotent provisioning code — `runtime::python`
(`PythonBootstrap`), `runtime::node` (`NodeBootstrap`), and
`runtime::python_server` (`ensure_spacy`, `ensure_kompress`, `ensure_started`)
— this module only orchestrates and reports; it does not reimplement downloads.

## Files

- `mod.rs` — module doc and re-exports.
- `registry.rs` — the ordered `HarnessInitStep` list from `all_steps()`:
  `python_runtime`, `spacy`, `kompress`, `runtime_python_server`, and
  `node_runtime` (only when the `runtime-node` feature is compiled in). Each
  step is a durable, network-free `is_done` probe plus a `run` closure, and a
  `provisioning` flag that says whether the step may download/install (and so
  justify the blocking first-run overlay) or is routine startup that must run
  silently (relaunching an already-installed local server). All steps are
  `required: false`; a failure degrades to a fallback.
- `ops.rs` — `run_harness_init` / `run_harness_init_with(config, force)`:
  walks the registry, marks steps `Done` instantly when already satisfied,
  otherwise runs them. `provisioning_required` decides up front whether any
  *provisioning* step still needs work, so an already-provisioned host never
  flashes the overlay on a warm restart (GH-5047). Also hosts the RPC handlers
  `handle_status` / `handle_run` (`force` re-runs satisfied steps).
- `store.rs` — process-lifetime `HarnessInitSnapshot` behind a mutex.
  `set_overall` and `update_step` mutate it; `update_step` publishes
  `DomainEvent::HarnessInitProgress` and `publish_completed` publishes
  `DomainEvent::HarnessInitCompleted` (both in `core/events.rs`).
- `types.rs` — `HarnessInitSnapshot`, `StepStatus`, `OverallState`,
  `StepState` (serialized `snake_case`).
- `bus.rs` — placeholder; progress is published directly from `store`, so
  there is no subscriber today.
- `schemas.rs` — `harness_init` namespace controller schemas (`status`,
  `run`).
- `*_tests.rs` — focused behavior tests beside each file.

## Wiring

- `core::runtime::services::start_boot_once_jobs` spawns `run_harness_init`
  (fire-and-forget) when `ServiceSet.harness_init` is true. It is called from
  `start_core_runtime_services` in `core/jsonrpc.rs`, deliberately outside
  `bootstrap_core_runtime`, so a build-only embedder never starts it.
- `ServiceSet` (`core/runtime/builder.rs`) turns it on in the `desktop()` and
  `embedded()` presets and off in `headless_api()` and `none()`.
- Controllers are registered under `DomainGroup::Agent` via
  `agent::harness_init::all_harness_init_registered_controllers` in
  `core/all.rs`.
