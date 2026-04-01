# Codex 工作区说明（工作区约束）

<!-- BEGIN GENERATED COMMON-FIRST ADAPTER BLOCK -->
## Common-First Adapter Contract

- `common/` + package-local `tools/` are the shared execution kernel; platform folders are adapter shells.
- Host-visible native surfaces: `workspace_instructions`, `skills`, `mcp`, `per_role_config`, `multi_agent`
- Target contract comes from `common/config/platform_capabilities.json` and `common/config/framework_compliance.json`; it is not the same as current readiness.
- Current adapter must satisfy required surfaces: `agents`, `skills`, `mcp`
- Target contract: `coordination_mode = staged_handoff`, `sub_agent_mode = puppet_sub_agents`, `peer_communication = via_main_agent`
- Current adapter readiness is tracked separately in `common/config/adapter_readiness.json`: `adapter_in_progress`
- `status_label` / `local_support` / `remote_support` / `enforcement_layer` describe repo posture only; they do not imply strict readiness.
- Strict execution must be enforced by shared harness, runtime lock, freeze state, artifact gate, and finalization receipt; not by prompt wording or host marketing text.
- Notes: Wave 1 strict target using runtime_guard plus common-first control interfaces.
<!-- END GENERATED COMMON-FIRST ADAPTER BLOCK -->


当前目录是 Codex 的 platform-local 模板。所有角色在进入 role-specific 行为前，都必须先服从 shared `common/` 约束。

强制规则：

- 未完成 `common/` 与 `tools/` 覆盖、且未通过 `validate_binding.py --strict` 前，不得开始依赖平台真相的工作
- 用户未提供 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止
- 用户未提供 `strict_ready` 的 fix reference 时，必须以 `BLOCKED_MISSING_FIX_REFERENCE` 停止
- 当前平台通过 `runtime_owner + shared harness guard + audit artifacts` 执行强门禁
- `.codex/runtime_guard.py` 必须先后裁决 `artifacts/entry_gate.yaml`、`artifacts/intake_gate.yaml`、`artifacts/runtime_topology.yaml`
- capture import 与 case/run bootstrap 只能发生在 accepted intake 内
- `waiting_for_specialist_brief`、`redispatch_pending`、`skeptic_challenged` 期间，orchestrator 不得抢做 live investigation
- reopen / reconnect 产生新的 `session_id` / `context_id` 是预期行为
