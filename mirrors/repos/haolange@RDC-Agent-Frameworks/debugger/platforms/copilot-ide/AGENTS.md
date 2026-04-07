# Copilot IDE 工作区约束

<!-- BEGIN GENERATED COMMON-FIRST ADAPTER BLOCK -->
## Common-First Adapter Contract

- `common/` + package-local `tools/` 是 shared execution kernel；当前目录只保留宿主壳层。
- 当前平台的 `local_support`、`remote_support`、`enforcement_layer` 与 `coordination_mode` 统一以 `common/config/platform_capabilities.json` 为准。
- `adapter_readiness.json` 是当前适配就绪度记录，不是第二套运行规则。
<!-- END GENERATED COMMON-FIRST ADAPTER BLOCK -->

当前目录是 Copilot IDE 的 platform-local 模板。所有角色在进入 role-specific 行为前，都必须先服从 shared `common/` 约束。

强制规则：

- 未完成 `common/` 与 `tools/` 覆盖、且未通过 `validate_binding.py --strict` 前，不得开始依赖平台真相的工作
- 用户未提供 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止
- 用户未提供 `strict_ready` 的 fix reference 时，必须以 `BLOCKED_MISSING_FIX_REFERENCE` 停止
- specialist silence 或 timeout 不能自动退化成 orchestrator 自执行
