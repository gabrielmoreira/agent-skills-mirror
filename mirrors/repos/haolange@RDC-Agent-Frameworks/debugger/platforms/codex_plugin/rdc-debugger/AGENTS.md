# Codex 插件工作区说明（工作区约束）

当前目录是 Codex 的 installable plugin bundle。所有角色在进入 role-specific 行为前，都必须先服从本文件与共享 `common/` 约束。

## 前置检查

在执行任何工作前，必须验证：

1. `common/AGENT_CORE.md` 存在。
2. `tools/spec/tool_catalog.json` 与 `tools/rdx.bat` 存在。

任一文件不存在时，立即停止，并向用户输出前置环境未就绪提示。

验证通过后，按顺序阅读：

1. `common/AGENT_CORE.md`
2. `common/config/platform_adapter.json`
3. `skills/rdc-debugger/SKILL.md`
4. `common/docs/platform-capability-model.md`
5. `common/docs/model-routing.md`

强制规则：

- 平台启动后默认保持普通对话态；只有用户手动召唤 `rdc-debugger`，才进入 RenderDoc/RDC GPU Debug 调试框架。
- 其他 specialist 默认都是 internal/debug-only，只能由 `rdc-debugger` 分派。
- 未提供可导入的 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止。
- 当前插件不预注册 `.codex/agents` 自定义 agent；如需 specialist 角色，`rdc-debugger` 必须显式要求 Codex 创建通用 sub-agent，并让它先加载对应 `skills/<role>/SKILL.md`。

运行时工作区固定为平台根目录下的 `workspace/`。
- 当前插件路径按 `no-hooks` 处理；执行门禁固定为 `intent_gate -> accept-intake -> dispatch_readiness / dispatch_specialist / specialist_feedback -> staged_handoff -> run_compliance`。
- 在 `artifacts/intake_gate.yaml` 通过前，不得执行 specialist dispatch 或 live `rd.*` 调试。
