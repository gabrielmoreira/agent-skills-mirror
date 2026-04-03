# Claude Code 入口说明

<!-- BEGIN GENERATED COMMON-FIRST ADAPTER BLOCK -->
## Common-First Adapter Contract

- `common/` + package-local `tools/` are the shared execution kernel; platform folders are adapter shells.
- Host-visible native surfaces: `agents`, `skills`, `hooks`, `mcp`, `per_agent_model`
- Target contract comes from `common/config/platform_capabilities.json` and `common/config/framework_compliance.json`; it is not the same as current readiness.
- Current adapter must satisfy required surfaces: `agents`, `skills`, `hooks`, `mcp`
- Target contract: `coordination_mode = staged_handoff`, `orchestration_mode = multi_agent`, `live_runtime_policy = single_runtime_single_context`
- Current adapter readiness is tracked separately in `common/config/adapter_readiness.json`: `adapter_in_progress`
- `status_label` / `local_support` / `remote_support` / `enforcement_layer` describe repo posture only; they do not imply strict readiness.
- Strict execution must be enforced by shared harness, runtime broker, ownership lease, freeze state, artifact gate, and finalization receipt; not by prompt wording or host marketing text.
<!-- END GENERATED COMMON-FIRST ADAPTER BLOCK -->

@../AGENTS.md
@../common/AGENT_CORE.md
@../common/docs/platform-capability-model.md
@../common/docs/model-routing.md

当前目录是面向 `RenderDoc/RDC GPU debugger framework` 的 Claude Code platform-local 模板。

入口约束：

- 启动后保持普通对话态，不自动进入 debugger framework
- public main skill 为 `.claude/skills/rdc-debugger/`
- 只有用户显式调用 `rdc-debugger` 时，才进入 debugger framework
- 默认入口模式是 `CLI`
- 只有用户明确要求 `MCP` 时，才切换到 `MCP`
- 已配置的 `MCP` server 只是可选接入面，不是默认 live-access 前提

运行时约束：

- 独立的 tools-layer session bootstrap 不会创建 framework `workspace/case/run`
- 只有被 `rdc-debugger` 接受的 intake，才允许初始化 framework workspace state 与 broker-owned runtime artifacts
- 运行时 workspace 固定在 platform-root `workspace/`
- live runtime 固定为单 session / 单 context；platform hooks 不得私自扩展第二套 context 语义

前置条件：

- 在将顶层 `debugger/common/` 拷贝到 platform-root `common/` 之前，不得使用当前模板
