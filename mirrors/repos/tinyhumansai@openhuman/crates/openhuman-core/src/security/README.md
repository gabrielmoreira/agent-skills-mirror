# Security

Trust boundary for the autonomous core. `security/mod.rs` calls this the
kernel security family: `SecurityPolicy`, the approval gate, redaction,
credentials, and the keychain. None of these submodules is feature-gated.

## Layout

| Path | Purpose |
| --- | --- |
| `policy/` | `SecurityPolicy`, autonomy tiers, path/command gating — see [policy/README.md](policy/README.md) |
| `approval/` | Human-in-the-loop approval gate for prompted tool calls — see [approval/README.md](approval/README.md) |
| `credentials/` | Per-channel credential storage and profile-scoped secrets — see [credentials/README.md](credentials/README.md) |
| `devices/` | Device pairing and cross-device tunnel security — see [devices/README.md](devices/README.md) |
| `egress/` | Data-egress descriptors and `LocalOnly` enforcement chokepoint — see [egress/README.md](egress/README.md) |
| `encryption/` | Cross-domain `EncryptionEngine` — see [encryption/README.md](encryption/README.md) |
| `keyring/` | OS keyring backend and encrypted-file fallback secret store — see [keyring/README.md](keyring/README.md) |
| `keyring_consent/` | Consent gate for falling back from OS keyring to local encrypted storage — see [keyring_consent/README.md](keyring_consent/README.md) |
| `pii/` | Fully local PII scanner — see [pii/README.md](pii/README.md) |
| `prompt_injection/` | Prompt-injection heuristics — see [prompt_injection/README.md](prompt_injection/README.md) |
| `live_policy.rs` | Process-global, hot-swappable current `SecurityPolicy` (see its own `//!`) |
| `secrets.rs` | One-line re-export of `keyring::encrypted_store` for legacy import paths |
| `tools.rs` | `SecurityPolicyInfoTool`, the only LLM-callable surface of this domain (read-only, default-ON); command/path gating itself is enforced in-engine, never as an agent-callable tool |
| `schemas.rs` | `security.policy_info` RPC controller, registered through `core/all.rs` |
| `ops.rs` | `security_policy_info_for_config` / `load_and_get_security_policy_info` behind that controller |
| `detect.rs` | `create_sandbox` — picks a `Sandbox` backend for the host |
| `traits.rs` | `Sandbox` trait and `NoopSandbox` |
| `docker.rs`, `bubblewrap.rs`, `firejail.rs`, `landlock.rs` | Legacy `Command`-wrapping sandbox backends implementing `Sandbox` (see below) |
| `audit.rs` | Append-only audit log of agent actions |
| `pairing.rs` | Pairing token / non-loopback bind guard |
| `core.rs` | `redact()`, 4-char-prefix log redaction (glob re-exported) |

Sandbox note: `docker.rs` / `bubblewrap.rs` / `firejail.rs` / `landlock.rs`
here wrap a `std::process::Command` per the `Sandbox` trait and are chosen by
`detect::create_sandbox`. `crates/openhuman-core/src/sandbox/` is a separate,
newer domain — see `sandbox/cwd_jail/mod.rs`'s rustdoc for why `cwd_jail`
superseded these backends on macOS (no `bwrap`) and added a Windows
AppContainer backend; the two domains are not interchangeable.

## Public surface

- `pub struct SecurityPolicy`, `pub enum AutonomyLevel`, `pub enum CommandClass`,
  `pub enum GateDecision`, `pub struct TrustedRoot` /
  `pub enum TrustedAccess`, `POLICY_BLOCKED_MARKER` / `POLICY_DENIED_MARKER` —
  `policy/types.rs`, re-exported here — see [policy/README.md](policy/README.md).
- `pub fn validate_path_within_root`, `pub fn openhuman_scratch_dir`,
  `pub fn ensure_openhuman_scratch_dir` — `policy/enforcement.rs`.
- `pub trait Sandbox` / `pub struct NoopSandbox` — `traits.rs` — pluggable
  sandbox abstraction.
- `pub fn create_sandbox(config: &SecurityConfig) -> Arc<dyn Sandbox>` —
  `detect.rs` — honors `config.sandbox.backend` or auto-detects Landlock /
  Firejail / Bubblewrap / Docker, falling back to `NoopSandbox`. Landlock and
  Bubblewrap are behind the `sandbox-landlock` / `sandbox-bubblewrap` cargo
  features.
- `pub use self::keyring::SecretStore` — encrypted-on-disk secret codec whose
  master key lives in keychain-backed storage.
- `pub use egress::{emit_external_transfer, enforce_egress, local_only_blocks, local_only_tool_block, DataKind, EgressDescriptor, EgressReason, IdentificationRisk}` —
  see [egress/README.md](egress/README.md).
- `pub use pii::{scan as scan_pii, CategoryHit, PiiCategory, PiiScanResult, RiskLevel}` —
  see [pii/README.md](pii/README.md).
- `pub struct AuditLogger` / `pub enum AuditEventType` / `pub struct AuditEvent`
  / `pub struct Actor` / `pub struct Action` / `pub struct ExecutionResult` /
  `pub struct SecurityContext` / `pub struct CommandExecutionLog` — `audit.rs`
  — append-only audit trail.
- `pub fn is_public_bind` / `pub fn ensure_core_rpc_token_for_bind` /
  `CORE_TOKEN_ENV_VAR` / `CoreBindTokenError` — `pairing.rs` — refuse a
  non-loopback RPC bind without a core token. `PairingGuard`,
  `constant_time_eq`, and the token helpers are re-exported from
  `tinychannels_bus::security`.
- `pub fn redact(value: &str) -> String` — `core.rs` — uniform 4-char-prefix
  redaction for logs.
- `pub use ops as rpc` — `ops.rs`'s `security_policy_info_for_config(&Config)`
  and `load_and_get_security_policy_info()` return
  `RpcOutcome<serde_json::Value>` and back the `security.policy_info` RPC
  function; `tools.rs` exposes the same read to the agent.

## Security invariants

These are the invariants AGENTS.md requires of the autonomy policy. Do not
weaken any of the enforcing functions below, or the default-on approval
behavior, to make a feature work:

- **`action_dir` is the agent's permitted read and write root.** Tools resolve
  relative paths and default their cwd here (`SecurityPolicy::action_dir`,
  `policy/types.rs`).
- **`workspace_dir` stores internal state and is never an acting-tool target.**
  Enforced by `SecurityPolicy::is_workspace_internal_path`
  (`policy/path_checks.rs`) — memory DBs, sessions, tokens, and other core
  persistence under `workspace_dir` (`WORKSPACE_INTERNAL_DIRS` /
  `WORKSPACE_INTERNAL_FILES` and the `memory-`/`memory_tree-`/`session_raw-`
  prefixes) are unwritable by agent tools even under a `trusted_root` grant.
- **Unknown commands classify as writes.** `SecurityPolicy::classify_command`
  (`policy/command_checks.rs`) is fail-closed: a command that is not
  provably read-only is at least `CommandClass::Write`, the highest class
  across `;`/`|`/`&&`/`||` segments wins, and a redirect (`>`, `>>`) or `tee`
  lifts the class to at least `Write` no matter how benign the base command
  looks.
- **System and credential paths are always forbidden.**
  `SecurityPolicy::is_always_forbidden` (`policy/path_checks.rs`) matches
  case-insensitively by path segment (`.ssh`, `.gnupg`, `.aws`, `.azure`,
  `.kube`, `keychains`, Windows `Microsoft\{Protect,Credentials,Crypto,Vault}`)
  and by absolute prefix (`/etc`, `/root`, `/boot`, `/proc`, `/sys`, `/system`,
  `C:\Windows`, `C:\Program Files`, `C:\ProgramData`). This check is
  unconditional and is **not** overridable by a `trusted_root` grant.
- **The approval gate is on by default and interactive requests expire as
  denied after ten minutes.** `security/approval/gate.rs`'s
  `DEFAULT_APPROVAL_TTL` is 10 minutes and a timed-out park returns `Deny`;
  `approval_gate_boot_decision` (`core/types.rs`, applied in
  `core/jsonrpc.rs`) always installs the gate for `HostKind::TauriShell` and
  ignores `OPENHUMAN_APPROVAL_GATE=0` there — only CLI, Docker, and library
  hosts may opt out.

## Called by

- `crates/openhuman-core/src/agent/tinyagents/host/security_gate.rs` — bridges
  `SecurityPolicy` into the tinyagents tool-call gate.
- `crates/openhuman-core/src/agent/profiles/guard.rs`,
  `agent/turn_workspace.rs` — profile and per-turn workspace grants.
- `crates/openhuman-core/src/tools/ops.rs` and nearly every
  `tools/impl/{filesystem,network,system,browser,document,presentation}/*.rs`
  — every executable tool consults `SecurityPolicy` before acting.
- `crates/openhuman-core/src/tools/impl/network/{curl,http_request,web_fetch}.rs`
  — risk-classify outbound calls and call into `egress`.
- `crates/openhuman-core/src/agent/tools/delegate.rs` — sub-agent dispatch
  goes through the autonomy gate.
- `crates/openhuman-core/src/cron/scheduler.rs` — wraps scheduled shell jobs in
  `SecurityPolicy`.
- `crates/openhuman-core/src/security/credentials/` — stores profile secrets
  through `keyring::SecretStore`.
- `crates/openhuman-core/src/memory/guard/policy.rs` — `enforce_write_tier`
  under `MemoryCore::store`, `live_policy`, and `egress` for outbound memory.

## Tests

- `policy/policy_tests*.rs`, `policy/proptest_tests.rs`,
  `policy/enforcement_scratch_dir_tests_tests.rs` — see
  [policy/README.md](policy/README.md).
- Every other file has an adjacent `*_tests.rs` (`audit_tests.rs`,
  `core_tests.rs`, `detect_tests.rs`, `live_policy_tests.rs`, `ops_tests.rs`,
  `pairing_tests.rs`, `tools_tests.rs`, `traits_tests.rs`, and one per sandbox
  backend).
