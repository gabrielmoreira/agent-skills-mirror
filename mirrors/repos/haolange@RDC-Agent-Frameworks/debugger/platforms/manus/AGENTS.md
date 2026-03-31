# Manus 工作区约束

当前目录是 Manus 的 platform-local 模板。所有角色在进入 role-specific 行为前，都必须先服从本文件与共享 `common/` 约束。

## 前置检查（必须先于任何其他步骤执行）

在执行任何工作前，必须验证以下两项均已就绪：

1. `common/` 已正确覆盖：检查 `common/AGENT_CORE.md` 是否存在。
2. `tools/` 已正确覆盖：检查 `tools/spec/tool_catalog.json` 与 `tools/rdx.bat` 是否存在。

任一文件不存在时：

- 立即停止，不得继续任何工作。
- 不得降级处理、搜索替代工具路径、使用模型记忆或以其他方式绕过本检查。
- 向用户输出：

```text
前置环境未就绪：请确认 (1) 已将 debugger/common/ 整包覆盖到平台根 common/；(2) 已将 RDC-Agent-Tools 整包覆盖到平台根 tools/；(3) 在平台根目录运行 python common/config/validate_binding.py --strict 通过后，再重新发起任务。
```

验证通过后，按顺序阅读：

1. `common/AGENT_CORE.md`
2. `common/config/platform_adapter.json`
3. `common/skills/rdc-debugger/SKILL.md`
4. `common/docs/platform-capability-model.md`
5. `common/docs/model-routing.md`

强制规则：

- 平台启动后默认保持普通对话态；只有用户手动召唤 `rdc-debugger`，才进入 RenderDoc/RDC GPU Debug 调试框架。
- 除 `rdc-debugger` 之外，其他 specialist 默认都是 internal/debug-only，只能由 `rdc-debugger` 在框架内分派。
- 用户尚未提供可导入的 `.rdc` 时，必须以 `BLOCKED_MISSING_CAPTURE` 停止，不得初始化 case/run 或继续做 debug、investigation、tool planning。
- `manus` 的 `local_support` / `remote_support` / `enforcement_layer` 以 `common/config/platform_capabilities.json` 当前行与 `runtime_mode_truth.snapshot.json` 为准。
- 当前平台的 `sub_agent_mode = instruction_only_sub_agents`；支持 sub agent runtime，但只能在 spawn 时注入 instruction，不支持独立 agent 描述文件。

未先将 `debugger/common/` 整包覆盖到平台根 `common/`、且将 RDC-Agent-Tools 整包覆盖到平台根 `tools/` 之前，不允许在宿主中使用当前平台模板。

运行时工作区固定为平台根目录下的 `workspace/`
- 当前平台属于 `no-hooks` tier；宿主按 `workflow_stage` 串行运行，不得伪装 host-side strict hooks。
- 最终仍必须生成 `artifacts/run_compliance.yaml`，才算合规结案。
- 可以进行串行 specialist dispatch，但不得在该宿主上模拟实时 multi-agent handoff。
- 不得把独立 specialist 描述文件误写成 Manus 宿主能力；该宿主只支持 spawn-time instruction。
- 若任务需要更高阶 remote 多轮会话、多个 live owners 或 per-agent model routing，必须切回更高能力平台。