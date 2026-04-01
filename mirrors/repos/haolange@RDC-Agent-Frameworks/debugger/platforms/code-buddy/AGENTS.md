# Code Buddy 工作区约束

<!-- BEGIN GENERATED COMMON-FIRST ADAPTER BLOCK -->
## Common-First Adapter Contract

- `common/` + package-local `tools/` are the shared execution kernel; platform folders are adapter shells.
- Host-visible native surfaces: `plugin`, `agents`, `skills`, `hooks`, `mcp`, `per_agent_model`
- Target contract comes from `common/config/platform_capabilities.json` and `common/config/framework_compliance.json`; it is not the same as current readiness.
- Current adapter must satisfy required surfaces: `agents`, `skills`, `hooks`, `mcp`
- Target contract: `coordination_mode = concurrent_team`, `sub_agent_mode = team_agents`, `peer_communication = direct`
- Current adapter readiness is tracked separately in `common/config/adapter_readiness.json`: `adapter_in_progress`
- `status_label` / `local_support` / `remote_support` / `enforcement_layer` describe repo posture only; they do not imply strict readiness.
- Strict execution must be enforced by shared harness, runtime lock, freeze state, artifact gate, and finalization receipt; not by prompt wording or host marketing text.
- Notes: Retains concurrent_team/team_agents/direct target contract; strict adapter must move beyond write-and-stop-only hooks.
<!-- END GENERATED COMMON-FIRST ADAPTER BLOCK -->


当前目录是 Code Buddy 的 platform-local 模板。所有角色在进入 role-specific 行为前，都必须先服从 shared `common/` 约束。

强制规则：

- 未完成 `common/` 与 `tools/` 覆盖、且未通过 `validate_binding.py --strict` 前，不得开始依赖平台真相的工作
- 用户未提供 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止
- 用户未提供 `strict_ready` 的 fix reference 时，必须以 `BLOCKED_MISSING_FIX_REFERENCE` 停止
- clarification、challenge、redispatch、timeout 都必须遵循 shared workflow
