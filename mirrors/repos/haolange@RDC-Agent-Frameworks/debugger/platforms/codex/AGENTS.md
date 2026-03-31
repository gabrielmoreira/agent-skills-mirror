# Codex 工作区说明（工作区约束）

<!-- BEGIN GENERATED COMMON-FIRST ADAPTER BLOCK -->
## Common-First Adapter Contract

- `common/` + package-local `tools/` 是共享执行内核，platform folder 只是 adapter 壳层。
- 宿主可见的 native surface：`workspace_instructions`、`skills`、`mcp`、`per_role_config`、`multi_agent`。
- 目标合同来自 `common/config/platform_capabilities.json` 和 `common/config/framework_compliance.json`，不等同于当前 readiness。
- 当前 adapter 必须满足的 surface：`agents`、`skills`、`mcp`。
- 目标合同：`coordination_mode = staged_handoff`、`sub_agent_mode = puppet_sub_agents`、`peer_communication = via_main_agent`。
- 当前 adapter readiness 单独记录在 `common/config/adapter_readiness.json`：`adapter_in_progress`。
- `status_label` / `local_support` / `remote_support` / `enforcement_layer` 只描述仓库姿态，不代表 strict readiness。
- 严格执行必须由 shared harness、runtime lock、freeze state、artifact gate 和 finalization receipt 共同约束。
<!-- END GENERATED COMMON-FIRST ADAPTER BLOCK -->

当前目录是 Codex 的 platform-local 模板。所有角色在进入 role-specific 行为前，都必须先服从本文件与共享 `common/` 约束。

## 前置检查

在执行任何工作前，必须验证：

1. `common/AGENT_CORE.md` 存在。
2. `tools/spec/tool_catalog.json` 与 `tools/rdx.bat` 存在。

任一文件不存在时，立即停止，并向用户输出前置环境未就绪提示。

验证通过后，按顺序阅读：

1. `common/AGENT_CORE.md`
2. `common/config/platform_adapter.json`
3. `common/skills/rdc-debugger/SKILL.md`
4. `common/docs/platform-capability-model.md`
5. `common/docs/model-routing.md`

强制规则：

- 平台启动后默认保持普通对话态；只有用户手动召唤 `rdc-debugger`，才进入 RenderDoc/RDC GPU Debug 调试框架。
- 其他 specialist 默认都是 internal/debug-only，只能由 `rdc-debugger` 分派。
- 未提供可导入的 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止。
- `codex` 的 `local_support` / `remote_support` / `enforcement_layer` 以 `common/config/platform_capabilities.json` 当前行与 `runtime_mode_truth.snapshot.json` 为准。

运行时工作区固定为平台根目录下的 `workspace/`。
- 当前平台按 `pseudo-hooks` 处理；`hooks/hooks.json` 只作为 wrapper 触发面。
- 结案仍必须依赖共享 harness 与 `artifacts/run_compliance.yaml` 作为统一合规裁决。
