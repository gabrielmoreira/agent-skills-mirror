# Sandbox

Per-session sandbox backend selection and routed execution for agent tool
commands. Separates three concerns that used to be conflated: **where** a
tool runs (this module), **which** tools are allowed (security / tool
policy), and **whether** a tool needs host access (elevated ops, also owned
here). The gateway/core process itself always runs on the host; only
selected tool families (shell, filesystem, process) execute through a
sandbox backend.

This is a distinct layer from `crate::security::traits::Sandbox` (the older
`Command`-wrapping backends in `security/{docker,bubblewrap,firejail,landlock}.rs`
used by `security::create_sandbox`). That trait wraps a `Command` in-place;
this domain resolves a per-session `SandboxPolicy`, owns its own Docker
backend, and delegates local OS-level confinement to `cwd_jail`.

## Public surface

- `pub enum SandboxBackendKind { None, Local, Docker }` — `types.rs` — which
  backend a session resolved to.
- `pub struct SandboxPolicy` — `types.rs` — `backend`, `workspace_root`,
  `read_only_mounts`, `allow_network`, `env_passthrough`,
  `docker_overrides`.
- `pub struct DockerOverrides` — `types.rs` — per-session image/network/
  resource-limit overrides layered on `RuntimeConfig`'s `[runtime.docker]`.
- `pub struct ElevatedOp` / `pub const ELEVATED_TOOLS` — `types.rs` — tools
  (`git_operations`, `install_tool`, `docker_management`,
  `process_management`) that always require host access and must be audited
  via `build_elevated_op` rather than silently bypassing the sandbox. No
  code outside this domain calls `is_elevated_op`/`build_elevated_op` yet.
- `pub const SANDBOX_ENV_PASSTHROUGH` — `ops.rs` — the allowlisted
  environment variables (`PATH`, `HOME`, `TERM`, ...) forwarded into
  sandboxed execution; no other host env leaks in.
- `pub fn resolve_sandbox_policy(mode: SandboxMode, action_dir, runtime_config, is_remote_session) -> SandboxPolicy`
  — `ops.rs` — `SandboxMode::None`/`ReadOnly` resolve to `SandboxBackendKind::None`;
  `Sandboxed` resolves to `Docker` when `runtime_config.kind == "docker"` or
  the session is remote (channel/cron), else `Local` (OS jail via
  `cwd_jail`). `allow_network` is `!is_remote_session` for `Sandboxed` and
  `true` otherwise; `workspace_root` is `action_dir`; `read_only_mounts` is
  always empty; `docker_overrides` is populated from `[runtime.docker]` only
  for the `Docker` backend.
- `pub async fn create_sandbox_backend(policy) -> SandboxBackendHandle` —
  `ops.rs` — instantiates/probes the resolved backend.
- `pub async fn execute_in_sandbox(policy, command, working_dir, extra_env, timeout) -> anyhow::Result<SandboxExecResult>`
  — `ops.rs` — routes to unsandboxed, `cwd_jail`-based local jail, or Docker
  execution based on `policy.backend`.
- `pub fn is_elevated_op(tool_name) -> bool` / `pub fn build_elevated_op(...) -> ElevatedOp`
  — `ops.rs` — the escape hatch a sandboxed tool call uses to run on the
  host, with an audited reason.
- `pub mod docker` — Docker-specific container execution
  (`docker_exec`, `docker_backend_handle`, orphan cleanup).
- `pub mod cwd_jail` — the OS-level path-confinement backend used by
  `Local`; see [`cwd_jail/README.md`](cwd_jail/README.md).
- `sandbox` RPC namespace (`schemas.rs`): `status`, `resolve_policy`,
  `cleanup_orphans`, `validate_policy`, wired through
  `all_sandbox_registered_controllers()` in
  `crates/openhuman-core/src/core/all.rs`.

## Backend behavior

- **None** — `execute_unsandboxed` runs the command directly via
  `agent::platform_shell` after validating `working_dir` with
  `config::ensure_usable_cwd`.
- **Local** — `execute_local_jail` builds a `cwd_jail::Jail` rooted at
  `policy.workspace_root`, applies `deny_net()`/read-only mounts from the
  policy, and spawns through `cwd_jail::default_backend()` (falling back to
  `NoopBackend` if no OS jail is available on the host). Output is captured
  by redirecting stdout/stderr to temp files inside the jail root because
  some backends (macOS Seatbelt) rebuild the command and drop piped stdio.
- **Docker** — `docker::docker_exec` runs `docker run --rm` with the host
  `action_dir` mounted read/write at `/workspace`, network `none` by
  default, `--cap-drop ALL` (plus policy-specified extra drops),
  `--security-opt no-new-privileges`, a read-only rootfs with `/tmp` and
  `/var/tmp` tmpfs mounts, memory/CPU limits (512 MB / 1 CPU defaults),
  and only the explicit env passthrough list injected. Containers carry
  `openhuman.sandbox=true` for orphan cleanup. `validate_docker_policy`
  rejects host networking and `/`, `/etc`, `/proc`, `/sys`, or the Docker
  socket as mount roots.

## Security invariant

Sandbox backend selection is a defense-in-depth layer, not a replacement for
policy. Rust path checks in `security` (`is_workspace_internal_path`,
`is_always_forbidden`, `classify_command`) still apply even when
`resolve_sandbox_policy` falls back to `SandboxBackendKind::None` — either
explicitly (`SandboxMode::None`/`ReadOnly`) or implicitly when the `Local`
backend has no usable OS jail: `cwd_jail::default_backend()` substitutes
`NoopBackend`, `execute_local_jail` in `ops.rs` spawns through it, and
`create_sandbox_backend` reports the handle as `SandboxStatus::Inactive`
rather than `Ready` so callers can tell the difference. Do not treat a
resolved `SandboxBackendKind` as a security boundary on its own.

## Dependencies

- `crate::agent::harness::definition::SandboxMode` — the agent-declared
  mode this domain resolves against.
- `crate::agent::platform_shell` — Windows-aware shell/command building for
  the unsandboxed and local-jail paths.
- `crate::config::RuntimeConfig` — `[runtime] kind` and `[runtime.docker]`
  overrides feed `resolve_sandbox_policy`.

## Called by

- `crates/openhuman-core/src/tools/impl/system/{shell,node_exec,npm_exec,python_exec}.rs`
  — resolve a policy and call `execute_in_sandbox` per invocation.
- `crates/openhuman-core/src/flows/tinyflows/caps/code.rs` — sandboxed code
  execution capability.
- `crates/openhuman-core/src/agent/platform_shell.rs` — doc references
  only; it is the shared Windows-aware command builder that
  `execute_unsandboxed`/`execute_local_jail` call into.
- `crates/openhuman-core/src/agent/profiles/guard.rs` — doc comment noting
  that its profile-path scan is not an OS sandbox and pointing at
  `cwd_jail` as the confinement layer.
- `crates/openhuman-core/src/config/ops/sandbox.rs` — RPC settings surface
  (`get_sandbox_settings`) reads `SANDBOX_ENV_PASSTHROUGH` and
  `[security.sandbox]` config.

## Tests

- `types_tests.rs`, `ops_tests.rs`, `schemas_tests.rs`, `docker_tests.rs` —
  sibling `#[cfg(test)]` suites per file.
- `ops_tests.rs` includes a regression test (#3235) pinning
  `local_status_for_backend` so a host with no OS jail reports `Inactive`
  rather than a false `Ready`.
