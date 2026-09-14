# bin

Auxiliary binaries declared as `[[bin]]` targets in
`crates/openhuman-core/Cargo.toml` next to the primary `openhuman-core`
binary (`src/main.rs`). None of these ship in the desktop product.

## Primary binary (not in this directory)

`src/main.rs` is the `openhuman-core` entry point. It restores default
`SIGPIPE` handling on unix, loads `.env` before Sentry init so a dotenv-only
DSN is visible at startup (the CLI dispatcher later re-runs
`load_dotenv_for_cli`, which honors `OPENHUMAN_DOTENV_PATH`), initializes
Sentry under the `crash-reporting` feature with a `before_send` that drops
known-noise event classes (`core::observability::is_*` predicates) and scrubs
secrets via `openhuman_core::core::log_redaction::scrub_secrets`, then hands
the arguments to `openhuman_core::run_core_from_args`.

## Binaries in this directory

| Binary | Source | Required features | Purpose |
| --- | --- | --- | --- |
| `test-mcp-stub` | `test_mcp_stub.rs` | none (built by every `cargo test`) | Tiny stdio MCP server for tests |
| `openhuman-fleet` | `fleet.rs` | `http-server`, `bin-tools` | Process-per-user supervisor + reverse proxy |
| `rss-bench` | `rss_bench.rs` | `rss-bench` | Steady-state RSS benchmark for an embedded agent roster |
| `library-profile` | `library_profile/main.rs` (+ `harness.rs`, `mock.rs`, `scenarios/`) | `rss-bench` (add `rss-bench-dhat` for heap profiles) | Hermetic library-embedding profiling scenarios |

`http-server` is in `default`; `bin-tools`, `rss-bench` and `rss-bench-dhat`
are not, so a plain `cargo build` produces only `openhuman-core` and
`test-mcp-stub`. Cargo skips the gated targets rather than failing to link.

### `test-mcp-stub`

Speaks just enough MCP to satisfy `initialize`, `tools/list` and `tools/call`
for one `echo` tool over newline-delimited JSON-RPC on stdin/stdout, exiting
when stdin closes. `initialize` reports `PROTOCOL_VERSION` (`2025-11-25`).
Dependency-free beyond `serde_json`. Tests spawn it through
`env!("CARGO_BIN_EXE_test-mcp-stub")`: `tests/mcp_registry_e2e.rs`,
`tests/mcp_registry_multi_server.rs`, `tests/mcp_setup_e2e.rs`,
`tests/json_rpc_e2e.rs` and
`tests/raw_coverage/tool_registry_approval_raw_coverage_e2e.rs`.

### `openhuman-fleet`

Hosts one `openhuman-core` process per user/workspace and fronts them behind
a single endpoint, so a team server can manage many members' assistants
while every existing client (`CloudHttpTransport`) keeps working unchanged.

Design is **process-per-user, not in-process multi-tenancy**:

- Each tenant runs as its own OS process (`openhuman-core run
  --headless-api`) with its own workspace volume
  (`OPENHUMAN_WORKSPACE`) and its own core bearer
  (`OPENHUMAN_CORE_TOKEN`). Tenants are not yet isolated under distinct OS
  users or containers, so this MVP is **not a production multi-tenant
  security boundary** for arbitrary agent tools.
- The supervisor mints a distinct edge token (`EdgeToken`) per tenant for
  clients and is the only holder of the tenants' core bearers
  (`CoreBearer`); the two newtypes are kept deliberately distinct so they
  cannot be confused with each other. Minted edge tokens are written to the
  file named by `--edge-token-output`.
- The reverse proxy forwards `POST /{user_id}/rpc` verbatim to that tenant's
  core at `http://127.0.0.1:<port>/rpc`, so the JSON-RPC wire contract is
  unchanged end to end.

MVP scope uses explicit sequential port assignment (`--base-core-port`, tenant
N on `base + N`) with an authenticated JSON-RPC readiness probe before
registering a tenant; a production supervisor would read each core's bound
port from a ready file / `EmbeddedReadySignal` and reconcile membership
against `tinyhumansai/backend`. It requires `http-server` because it embeds
the axum control-plane server, and `bin-tools` for `clap` and `env_logger`:

```
cargo build -p openhuman --features bin-tools --bin openhuman-fleet
```

### `rss-bench`

Steady-state RSS benchmark for an embedded `openhuman_core` agent roster
(#5046). Mirrors the OpenCompany embedding contract: a bare `Agent` built
directly via `Agent::builder` (no `CoreBuilder`, no RPC, no background
services) with an injected mock model, a hand-rolled no-op `Memory`
(`NoopMemory`; `create_memory` with `backend: "none"` still builds a full
`UnifiedMemory`, which would inflate the reading) and a per-agent temp
workspace. Builds a 1-agent and an 8-agent roster, runs one deterministic
warm-up turn per agent, settles, then samples
`/proc/self/{status,smaps_rollup}`.

Two modes: `--child --roster N` builds one roster in a fresh process and
prints a single `ProcSample` JSON line (the isolated measured workload); the
default (parent) mode re-execs itself `--repeat` times per roster size for
independent cold samples, aggregates them, writes the raw JSON report
(`--out`), and prints a human summary. The pure sampling/aggregation logic
lives in `openhuman_core::platform::proc_metrics`; this binary is the
fixture and process driver. Build:

```
cargo build --release --features rss-bench --bin rss-bench
```

### `library-profile`

Hermetic, Rust-only library profiling workloads that measure production code
paths in fresh processes with network inference replaced by a deterministic
provider (`library_profile/mock.rs`).

Scenarios (`library-profile <scenario>`, one module each under
`library_profile/scenarios/`):

- `agent-turn` — a single cold agent turn (minimal library unit).
- `long-agent` — N warmed sequential turns with a per-turn checkpoint series.
- `workflow` — a real flows trigger -> transform -> agent graph, end to end.
- `fleet` — N live agents: marginal RSS, idle CPU, fd/thread growth, turn latency.
- `skill-run` — a skill step executing on a real `node` child: process-tree RSS.
- `subagent-storm` — K parallel researcher subagents in one instance: marginal RSS per subagent.

`memory-ingest` and `cold-phases` were removed with the in-process memory
engine (openhuman#6161); re-adding them means measuring the memory module
over the bus, a different scenario (see `scenarios/mod.rs`).

stdout is always a single pretty-printed JSON object (the pinned schema in
`harness::ProfileResult`); every diagnostic goes to stderr with the stable
`[library-profile]` prefix. `OPENHUMAN_PROFILE_WORKER_THREADS` pins the tokio
worker count (set `2` to simulate the 2 vCPU box). With the `rss-bench-dhat`
feature, dhat's global allocator and profiler are active: RSS/time numbers
are perturbed, the result carries `"dhat": true`, and a
`dhat-<scenario>.json` heap profile is written under
`target/profile/rust-library/` (override via `OPENHUMAN_PROFILE_DHAT_OUT`).

The driver scripts under `scripts/profile/` build it with
`cargo build --release --features rss-bench --bin library-profile`
(`library-heap.sh` uses `--features rss-bench-dhat`). The slim recipe from
`docs/library-benchmarking.md` (`library-bench.sh --slim`) builds both
benchmark binaries without the contributor default features:

```
cargo build --release -p openhuman --no-default-features --features rss-bench \
  --bin library-profile --bin rss-bench
```

## See also

- [`docs/library-benchmarking.md`](../../../../docs/library-benchmarking.md) —
  the benchmark environment, driver scripts under `scripts/profile/`, and
  results, covering `rss-bench` and `library-profile`.
- [`scripts/profile/README.md`](../../../../scripts/profile/README.md) — the
  driver scripts themselves.
