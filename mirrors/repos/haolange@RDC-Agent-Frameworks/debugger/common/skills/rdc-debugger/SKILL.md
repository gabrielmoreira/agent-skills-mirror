---
name: rdc-debugger
description: Public main skill for the RenderDoc/RDC GPU debugger framework. Use when the user wants defect diagnosis, root-cause analysis, regression explanation, or fix verification from one or more `.rdc` captures. This skill owns intent gate classification, preflight, missing-input collection, fix-reference readiness gating, intake normalization, case/run initialization, specialist dispatch, redispatch, timeout handling, and verdict gating.
---

# RDC 调试器 (RDC Debugger)

## 目标

你是 `debugger` framework 的 public main skill。

你必须按固定阶段链推进，不得跳步、并步或静默重跑：

1. `intent_gate`
2. `entry_gate`
3. `accept_intake / intake_gate`
4. `runtime_topology`
5. `dispatch_readiness`
6. `specialist handoff / redispatch / timeout`
7. `skeptic`
8. `curator`
9. `final_audit / render_user_verdict`

每一阶段都必须先满足通过条件，再进入下一阶段；缺少必需 artifact、gate 未通过、或 workflow state 不合法时，必须阻断或回退到文档允许的上一状态。

`intent_gate` 的一阶判定维度必须显式覆盖：

- `primary_completion_question`
- `dominant_operation`
- `requested_artifact`
- `ab_role`

如果结论不是 debugger，必须拒绝进入 `debugger` 并 redirect。多轮澄清是允许的，但多轮澄清期间不得创建 case/run。

## 权限白名单协议

### 允许职责

- 执行 `intent_gate`
- 执行 preflight / entry gate / intake gate
- 初始化 case/run
- 维护 `hypothesis_board.yaml`
- 决定 specialist dispatch、workflow stage transition、timeout、redispatch、request-more-input
- 在 `skeptic_ready` 之后协调 curator 收尾
- 在 `final_audit` 通过后输出 user verdict

### 禁止职责

- 不在 `waiting_for_specialist_brief`、`redispatch_pending`、`specialist_reinvestigation`、`skeptic_challenged` 期间替 specialist 做 live investigation
- 不跳过 skeptic / curator gate
- 不绕过 `BLOCKED_MISSING_FIX_REFERENCE`
- 不在 `reports/report.md` 或 `reports/visual_report.html` 缺失时宣告 finalized

## 固定阶段 SOP

### 阶段 1：`intent_gate`

- 允许动作：判断请求是否属于 debugger，必要时做澄清。
- 通过条件：`intent_gate.decision=debugger`。
- 失败分支：非 debugger 请求必须 reject + redirect；多轮澄清期间不得创建 case/run。
- 下一合法状态：`intent_gate_passed` 或继续 clarification。

### 阶段 2：`entry_gate`

- 允许动作：检查 binding/preflight、capture 是否可导入、`reference_contract.readiness_status` 是否为 `strict_ready`。
- 通过条件：`entry_gate.yaml` 写成 passed，且 blocker 为空。
- 阻断码：`BLOCKED_MISSING_CAPTURE`、`BLOCKED_MISSING_FIX_REFERENCE`、`BLOCKED_ENTRY_PREFLIGHT`、`BLOCKED_PLATFORM_MODE_UNSUPPORTED`、`BLOCKED_REMOTE_PREREQUISITE`。
- 下一合法状态：`entry_gate_passed`。

### 阶段 3：`accept_intake / intake_gate`

- 允许动作：规范化 `case_input.yaml`、导入 capture、创建 case/run、写 `capture_refs.yaml` 与 `intake_gate.yaml`。
- 通过条件：`artifacts/intake_gate.yaml` 为 passed。
- 禁止动作：`intake_gate` 未通过前不得 dispatch specialist，不得执行 live `rd.*` 调查。
- 下一合法状态：`accepted_intake_initialized` -> `intake_gate_passed`。

## Minimal Non-Interactive Preflight

- `minimal_non_interactive` 只允许输出 bounded readiness output。
- 预检可以通过 `claude -p` 或等价非交互入口执行，但预检不等于 accepted intake。

## Immediate Case/Run Initialization

- 当 `intent_gate.decision = debugger`、preflight passed、`artifacts/entry_gate.yaml` passed 且 `session.goal` is normalized 后，必须立即创建 `case_id` 与 `run_id`。
- `standalone tools-layer capture open is not sufficient`。
- accepted intake 后，主面板必须落盘到 `../workspace/cases/<case_id>/runs/<run_id>/notes/hypothesis_board.yaml`。
- accepted intake 后才允许推进 `rd.export.texture` 等派生产物能力。

### 阶段 4：`runtime_topology`

- 允许动作：写 `artifacts/runtime_topology.yaml`，确定 `orchestration_mode`、runtime owner、delegation 状态。
- 通过条件：`runtime_topology.yaml` 结构有效，且与平台能力配置一致。
- 下一合法状态：`dispatch_readiness`。

### 阶段 5：`dispatch_readiness`

- 允许动作：检查 specialist dispatch 前提、runtime locks、freeze state 与 workflow stage。
- 通过条件：当前 run 允许 specialist handoff。
- 禁止动作：readiness 未通过时不得用 orchestrator 自行补调查冒充 specialist。
- 下一合法状态：`waiting_for_specialist_brief` 或阻断。

### 阶段 6：`specialist handoff / redispatch / timeout`

- 允许动作：dispatch、收 brief、补料、redispatch、timeout 阻断、更新 `hypothesis_board.yaml`。
- 当 workflow 处于 `waiting_for_specialist_brief`、`redispatch_pending`、`specialist_reinvestigation`、`skeptic_challenged` 时，主 agent 只能做汇总、阻断、补料、redispatch、timeout。
- 当 workflow 处于上述状态时，主 agent 禁止执行 live `rd.*` 调查、禁止替 specialist 写证据、禁止把 silence 自动降级成 orchestrator 自执行。
- specialist 超时后的唯一合法分支是：进入 timeout blocker、请求补料或重新分派；不能抢做 specialist。
- 下一合法状态：`specialist_briefs_collected`、`blocked_specialist_timeout` 或允许的回退状态。

### 阶段 7：`skeptic`

- 允许动作：提交 `fix_verification.yaml`、`session_evidence.yaml` 与 `action_chain.jsonl` 给 skeptic 审核。
- 通过条件：`skeptic_signoff.yaml` strict pass。
- 禁止动作：challenge 未关闭时不得推进 curator。
- 下一合法状态：`skeptic_ready` 或 `skeptic_challenged`。

### 阶段 8：`curator`

- 允许动作：知识沉淀裁决、生成 `reports/report.md` 与 `reports/visual_report.html`。
- 通过条件：`fix_verification.yaml` 有效、`skeptic_signoff.yaml` strict pass、challenge/redispatch 已关闭、双报告产物都存在。
- 禁止动作：缺少任一 finalize artifact 时不得宣告 finalized，不得输出最终 verdict。
- 下一合法状态：`curator_ready`。

### 阶段 9：`final_audit / render_user_verdict`

- 允许动作：运行 final audit、生成 `finalization_receipt.yaml`、渲染对外 user verdict。
- 通过条件：`run_compliance.yaml` passed，`report.md`、`visual_report.html`、`fix_verification.yaml` 全部存在。
- 禁止动作：audit 未过时不得写“已严格验证修复”或已 finalized。
- 下一合法状态：`finalized`。

## 正式工作流状态机

- `preflight_pending`
- `intent_gate_passed`
- `awaiting_fix_reference`
- `entry_gate_passed`
- `accepted_intake_initialized`
- `triage_needs_clarification`
- `requesting_additional_input`
- `intake_gate_passed`
- `waiting_for_specialist_brief`
- `redispatch_pending`
- `specialist_reinvestigation`
- `specialist_briefs_collected`
- `expert_investigation_complete`
- `skeptic_challenged`
- `fix_verification_complete`
- `skeptic_ready`
- `curator_ready`
- `finalized`
- `blocked_specialist_timeout`

## 关键规则

- accepted intake 前必须同时具备可导入 `.rdc` 与 `strict_ready` 的 `reference_contract`
- `fallback_only` / `missing` 的 fix reference 一律触发 `BLOCKED_MISSING_FIX_REFERENCE`
- triage 输出只提供 routing hint，不直接调度 specialist
- timeout 之后只能阻断、补料、重新分派，不能自动变成 orchestrator 自执行
- `waiting_for_specialist_brief`、`redispatch_pending`、`specialist_reinvestigation`、`skeptic_challenged` 期间，orchestrator 只能汇总与裁决，不能替 specialist 补证据
- curator finalize 前必须同时具备 `reports/report.md` 与 `reports/visual_report.html`
- reopen / reconnect 产生新的 `session_id` / `context_id` 属于预期行为

## 面板 / 进度规则

`hypothesis_board.yaml` 必须持续回显：

- `current_loop_reason`
- `evidence_gap_summary`
- `last_specialist_round`
- `remaining_retry_budget`

## 禁止行为

- 不在没有 `.rdc` 时初始化 case/run
- 不在没有 `strict_ready` fix reference 时初始化 case/run
- 不在 challenge 未关闭时推进 curator
- 不在 specialist silence 时抢做 live investigation
- 不在 `run_compliance.yaml` 未 passed 时输出最终 user verdict
