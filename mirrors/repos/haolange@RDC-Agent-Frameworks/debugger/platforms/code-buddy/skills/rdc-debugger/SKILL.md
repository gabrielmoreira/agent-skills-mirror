---
name: rdc-debugger
description: Public main skill for the RenderDoc/RDC GPU debugger framework. Use when the user wants defect diagnosis, root-cause analysis, regression explanation, or fix verification for a GPU rendering issue from one or more `.rdc` captures.
metadata:
  short-description: RenderDoc/RDC GPU debugging workflow for .rdc captures
---

# `RDC Debugger` 主技能包装说明

当前文件是 Code Buddy 的 public main skill 入口。

平台启动后默认保持普通对话态。只有用户手动召唤 `rdc-debugger`，才进入 RenderDoc/RDC GPU Debug 调试框架。

进入 `rdc-debugger` 后，本 skill 负责：

- `intent_gate`
- `entry_gate`
- preflight
- 缺失输入补料
- intake 规范化
- capture 导入 + case/run 初始化
- broker startup
- specialist 分派、阶段推进与质量门裁决

固定顺序：

1. `intent_gate`
2. `entry_gate`
3. `accept_intake`，内部完成 capture import、case/run bootstrap、`intake_gate` 与 broker startup
4. `triage`
5. `dispatch/specialist loop`
6. `skeptic`
7. `curator`
8. `final_audit`

在 `artifacts/intake_gate.yaml` 通过，且 `artifacts/runtime_session.yaml`、`artifacts/runtime_snapshot.yaml`、`artifacts/ownership_lease.yaml`、`artifacts/runtime_failure.yaml` 产出前，不得进入 specialist dispatch 或 live `rd.*` 分析。

本 skill 只引用当前平台根目录的 `common/`：

- `common/skills/rdc-debugger/SKILL.md`
- 进入任何平台真相相关工作前，必须先校验 `common/config/platform_adapter.json`
- local_support / remote_support / enforcement_layer / coordination_mode 统一以 `common/config/platform_capabilities.json` 的当前平台定义为准

当前平台固定 contract：

- `coordination_mode = staged_handoff`
- `orchestration_mode = multi_agent`
- `live_runtime_policy = single_runtime_single_context`
- `hook_ssot = shared_harness`

执行约束：

- live tools process 始终由 broker / coordinator 直接持有。
- specialist 只能在有效 `ownership_lease` 下通过 broker action 请求访问 live runtime。
- 不得直接持有 live CLI / process，不得缓存并跨 handoff 复用 runtime handle。
- 不得临时写 Python、PowerShell 或 shell wrapper 批处理 live CLI。
- specialist dispatch 后，主 agent 必须进入 `waiting_for_specialist_brief` 并持续汇总阶段回报；短时 silence 不得触发 orchestrator 抢活。
- 超过框架预算仍未收到阶段回报时，必须进入 `BLOCKED_SPECIALIST_FEEDBACK_TIMEOUT` 或等价阻断状态，而不是让 orchestrator 抢做 specialist live investigation。

未先将顶层 `debugger/common/` 拷入当前平台根目录的 `common/` 之前，不允许在宿主中使用当前平台模板。

运行时 case/run 现场与第二层报告统一写入平台根目录下的 `workspace/`。
