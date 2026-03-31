---
name: rdc-debugger
description: Public main skill for the RenderDoc/RDC GPU debugger framework. Use when the user wants defect diagnosis, root-cause analysis, regression explanation, or fix verification for a GPU rendering issue from one or more `.rdc` captures.
metadata:
  short-description: RenderDoc/RDC GPU debugging workflow for .rdc captures
---

# `RDC Debugger` 主技能包装说明

当前文件是 Codex 的 public main skill 入口。

平台启动后默认保持普通对话态。只有用户手动召唤 `rdc-debugger`，才进入 RenderDoc/RDC GPU Debug 调试框架。

进入 `rdc-debugger` 后，本 skill 负责：

- `intent_gate`
- `entry_gate`
- preflight
- 缺失输入补料
- intake 规范化
- capture 导入 + case/run 初始化
- `artifacts/intake_gate.yaml`
- `artifacts/runtime_topology.yaml`
- specialist 分派、阶段推进与质量门裁决

固定顺序：

1. `intent_gate`
2. `entry_gate`
3. binding/preflight + capture import + case/run bootstrap
4. `artifacts/intake_gate.yaml` pass
5. `artifacts/runtime_topology.yaml`
6. `staged_handoff`
7. `artifacts/run_compliance.yaml` pass

在 `artifacts/intake_gate.yaml` 通过前，不得进入 specialist dispatch 或 live `rd.*` 分析。

本 skill 只引用当前平台根目录的 `common/`：

- common/skills/rdc-debugger/SKILL.md
- 进入任何平台真相相关工作前，必须先校验 common/config/platform_adapter.json
- local_support / remote_support / enforcement_layer / coordination_mode 统一以 common/config/platform_capabilities.json 的当前平台定义为准。
- 当前平台的 `sub_agent_mode = puppet_sub_agents`，`peer_communication = via_main_agent`，`agent_description_mode = independent_files`。
- 当前平台的 `specialist_dispatch_requirement = required`，`host_delegation_policy = platform_managed`，`host_delegation_fallback = none`。
- local live policy = `multi_context_orchestrated`；remote live policy = `single_runtime_owner`。
- 当前平台的执行约束补充：
- 当前平台的 local `staged_handoff` 允许 specialist 各持独立 context，但所有协调、brief 重组与裁决都必须经 `rdc-debugger`。
- 跨 context live transfer / resume 只能通过 `runtime_baton`，不得直接跨 specialist 借用 live runtime。
- remote 一律服从 `single_runtime_owner`，不能把 local 的多 context 语义抬到 remote。
- 默认 `orchestration_mode = multi_agent`；当前平台要求先走 specialist dispatch。
- 只有用户显式要求不要 multi-agent context 时，才允许 `single_agent_by_user`，并且必须把 `single_agent_reason = user_requested` 落盘到 `entry_gate.yaml` 与 `runtime_topology.yaml`。
- specialist dispatch 后，主 agent 必须进入 `waiting_for_specialist_brief` 并持续汇总阶段回报；短时 silence 不得触发 orchestrator 抢活。
- 超过框架预算仍未收到阶段回报时，必须进入 `BLOCKED_SPECIALIST_FEEDBACK_TIMEOUT` 或等价阻断状态，而不是让 orchestrator 抢做 specialist live investigation。

- OpenAI Codex 当前原生支持 `AGENTS.md` 分层与 `.codex/agents/*.toml` custom agents；当前模板继续使用这两类原生 surface。
- OpenAI Codex Hooks 当前只对 Bash 提供 guardrail，不足以为本框架的 native `rd.*` / specialist dispatch 提供可靠 host-side enforcement；因此当前模板不引入 `.codex/hooks.json`。
- 当前模板的强制执行链固定为：`.codex/runtime_guard.py preflight` → `entry-gate` → `intake-gate` → `runtime-topology` → `dispatch-readiness` / `specialist-feedback` → `final-audit`。
- 任一 guard 子命令非零退出都必须立即阻断，不得继续 specialist dispatch、live `rd.*` 分析或 finalization。
- direct RenderDoc Python fallback 只允许 local backend；若走直连路径，必须记录 `fallback_execution_mode=local_renderdoc_python` 与 `WRAPPER_DEGRADED_LOCAL_DIRECT`。
- `runtime_guard.py` 只编排 shared validator / gate / audit；平台层不复制 shared schema 或第二套规则正文。


未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。

运行时 case/run 现场与第二层报告统一写入平台根目录下的 `workspace/`
