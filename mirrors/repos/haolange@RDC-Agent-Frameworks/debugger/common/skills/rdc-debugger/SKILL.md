---
name: rdc-debugger
description: Public main skill for the RenderDoc/RDC GPU debugger framework. Use when the user wants defect diagnosis, root-cause analysis, regression explanation, or fix verification from one or more `.rdc` captures. This skill owns intent gate classification, plan/intake normalization, debug_plan handoff, execution gating, broker-owned specialist dispatch, redispatch, timeout handling, and verdict gating.
---

# RDC 调试器

`rdc-debugger` 是唯一 public main skill 与唯一 classifier，但内部固定分成两段：

1. `Plan / Intake Phase`
2. `Audited Execution Phase`

## Plan / Intake Phase

Plan 阶段负责：

- `intent_gate`
- 缺失输入补料
- 生成 `reference_contract`
- 判定 `strict_ready / fallback_only / missing`
- 汇总为 `debug_plan`

Plan 阶段默认通过轻量 sub-agent 收敛输入：

- `clarification_agent`
- `reference_contract_agent`
- `plan_compiler_agent`

Plan 阶段硬规则：

- 不创建 case/run
- 不写 `action_chain.jsonl`、`session_evidence.yaml`、`skeptic_signoff.yaml`
- 不接触 live runtime
- orchestrator 只保留核心简化摘要，不回灌冗长问答全文和大段中间推理

## Audited Execution Phase

只有当 `debug_plan.execution_readiness = ready` 时，才允许进入 execution。

你必须按固定阶段链推进：

1. `entry_gate`
2. `accept_intake / intake_gate`
3. `triage`
4. `dispatch_readiness`
5. `specialist handoff / redispatch / timeout`
6. `skeptic`
7. `curator`
8. `final_audit / render_user_verdict`

Execution 规则：

- `case_input.yaml`、`case_id`、`run_id`、`hypothesis_board.yaml` 只在 execution 内物化或更新
- `triage` 明确属于 execution，不前移到 plan 阶段
- `triage + specialist + skeptic + curator` 明确必须通过 sub-agent 执行
- `entry_gate`、`accept_intake`、`intake_gate`、`dispatch_readiness`、`final_audit` 属于控制面，不 agent 化

关键规则：

- `triage_agent` 只提供 routing hint，不直接 dispatch specialist
- triage 产生的 `candidate_bug_refs`、`recommended_sop`、`recommended_investigation_paths` 只是方向建议，最终是否进入哪个 specialist 仍由 `rdc-debugger` 决定
- live runtime 由 broker 直接持有；specialist 只通过 `ownership_lease` + broker action 消费 live runtime
- `session_id`、`context_id`、`active_event_id` 不得作为跨阶段稳定主键传播
- 临时 Python / PowerShell / shell wrapper 封装 live CLI 一律视为流程偏差
- `waiting_for_specialist_brief`、`redispatch_pending`、`specialist_reinvestigation`、`skeptic_challenged` 期间，orchestrator 只能汇总与裁决，不能替 specialist 补证据
- `primary_completion_question`、`requested_artifact` 等意图字段属于 plan 输入归一化，不属于 run 级 runtime 真相

## Sub-Agent 委派强制规则 (MANDATORY DELEGATION)

### 核心原则

**强制委托（Mandatory Delegation）** 是本框架的核心安全机制：
- **主 Agent 禁止直接执行** 调查、分析、验证等核心任务
- **所有核心任务必须通过 Sub-Agent 执行**
- **主 Agent 仅负责协调、决策和流程推进**

### 必须委托的节点

以下节点 **必须** 通过 sub-agent 执行，禁止主 Agent 直接执行：

| 节点 | 委派目标 | 产出物 | 违规后果 |
|------|----------|--------|----------|
| `triage` | `triage_taxonomy_agent` | `triage_result.yaml` | 产出物无效，必须重新委派；记录 `PROCESS_DEVIATION_SKIPPED_TRIAGE` |
| `specialist_investigation` | 各类 specialist agent (如 `shader_specialist`, `pipeline_specialist`, `resource_specialist`) | `brief.yaml`, `session_evidence.yaml` | 主 Agent 产出视为无效证据；记录 `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| `skeptic_review` | `skeptic_agent` | `challenge.yaml` 或 `signoff.yaml` | 缺少 skeptic 审计的 brief 不得进入 curator；记录 `PROCESS_DEVIATION_MISSING_SKEPTIC` |
| `curator_finalize` | `curator_agent` | `curator_report.yaml`, `final_hypothesis.yaml` | 未经验证的结论不得输出给用户；记录 `PROCESS_DEVIATION_PREMATURE_VERDICT` |

### 主 Agent 禁止行为清单 (PROHIBITED ACTIONS)

主 Agent 在任何时候都 **禁止** 执行以下操作：

| 禁止行为 | 说明 | 违规后果 |
|---------|------|---------|
| 直接分析 RDC capture 文件 | 必须通过 `specialist` sub-agent | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 直接编写 `session_evidence.yaml` | 必须由 `specialist` 产出 | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 直接编写 `brief.yaml` | 必须由 `specialist` 产出 | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 直接执行 shader 分析 | 必须通过 `shader_specialist` | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 直接执行 pixel forensics | 必须通过 `pixel_forensics_agent` | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 直接验证 fix | 必须通过 `fix_verification_agent` | `PROCESS_DEVIATION_MAIN_AGENT_OVERREACH` |
| 跳过 triage 直接 dispatch | 必须先通过 `triage` | `PROCESS_DEVIATION_SKIPPED_TRIAGE` |
| 跳过 skeptic 直接结案 | 必须通过 `skeptic` 审计 | `PROCESS_DEVIATION_MISSING_SKEPTIC` |

### 主 Agent 允许行为清单 (ALLOWED ACTIONS)

主 Agent **仅允许** 执行以下操作：

| 允许行为 | 说明 |
|---------|------|
| 读取和解析用户输入 | 理解用户意图和需求 |
| 生成 `debug_plan` | 在 Plan 阶段生成执行计划 |
| 调用 `entry_gate`, `intake_gate` | 执行控制面 gate 检查 |
| 委派任务给 Sub-Agent | 通过 `dispatch_specialist` 等机制 |
| 读取 Sub-Agent 产出物 | 读取 `brief.yaml`, `challenge.yaml` 等 |
| 更新 `hypothesis_board.yaml` | 更新 blocker 和决策状态 |
| 决定 redispatch 或 escalation | 基于 Sub-Agent 反馈做决策 |
| 调用 `final_audit` | 执行最终审计 |
| 输出最终 verdict 给用户 | 基于 curator 报告输出结论 |

### 委派验证机制 (Delegation Verification)

**委派前检查**：

1. **Agent 可用性检查**
   - 确认目标 sub-agent 在 `agent_registry.yaml` 中状态为 `available`
   - 检查目标 agent 的 `capability_match` 与当前任务匹配度

2. **输入完整性检查**
   - 确认 `brief_input.yaml` 包含所有必需字段
   - 确认 `ownership_lease.yaml` 已正确配置

3. **上下文隔离检查**
   - 确认主 Agent 上下文已正确序列化到 `delegation_context.yaml`
   - 确认不包含任何 live runtime handle

**委派后验证**：

1. **产出物完整性验证**
   - 检查产出物是否符合 `output_schema`
   - 检查必填字段是否全部存在

2. **来源真实性验证**
   - 验证产出物中的 `from` 字段与委派目标一致
   - 验证 `timestamp` 和 `agent_version` 有效性

3. **内容合规性验证**
   - 验证产出物不包含主 Agent 直接写入的痕迹
   - 验证证据链完整性

**验证失败处理**：

| 失败类型 | 处理动作 | 记录位置 |
|---------|---------|---------|
| 产出物缺失 | 标记为 `DELEGATION_TIMEOUT` 或 `DELEGATION_FAILURE`，触发 redispatch | `action_chain.jsonl`, `hypothesis_board.yaml` |
| 来源不一致 | 标记为 `PROCESS_DEVIATION_SPOOFED_OUTPUT`，强制进入 curator | `audit/security/` |
| 内容不合规 | 退回 sub-agent 要求重新产出，记录 `OUTPUT_VALIDATION_FAILED` | `action_chain.jsonl` |

### Phase Gate 定义

**Phase 1: Plan / Intake Phase**

| Gate | 检查项 | 通过条件 |
|------|--------|---------|
| `intent_gate` | 用户意图分类 | 产出 `intent_classification.yaml` |
| `input_completeness` | 必需输入完整性 | 所有 `required_inputs` 已提供或标记为 `will_provide_later` |
| `reference_contract` | 参考合约生成 | 产出 `reference_contract.yaml` |
| `execution_readiness` | 执行准备度评估 | `strict_ready` 或 `fallback_only` |

**Phase 2: Audited Execution Phase**

| Gate | 检查项 | 通过条件 | 产出物 |
|------|--------|---------|--------|
| `entry_gate` | case/run 创建 | `case_id` 和 `run_id` 已分配 | `entry_gate.yaml` |
| `intake_gate` | 输入最终确认 | 所有必需输入已固化 | `intake_gate.yaml` |
| `triage_gate` | 分类完成 | `triage_result.yaml` 已验证 | `dispatch_recommendation.yaml` |
| `dispatch_readiness` | specialist 委派准备 | `ownership_lease.yaml` 已配置 | `dispatch_approval.yaml` |
| `specialist_feedback` | specialist 调查完成 | `brief.yaml` 已接收并通过 skeptic | `validated_brief.yaml` |
| `skeptic_gate` | 怀疑者审计 | `challenge.yaml` 已解决或 `signoff.yaml` 已接收 | `skeptic_resolution.yaml` |
| `curator_gate` | 策展人结案 | `curator_report.yaml` 已产出 | `final_hypothesis.yaml` |
| `final_audit` | 最终审计 | 所有 artifact 完整性验证通过 | `run_compliance.yaml` |

**Phase Gate 强制执行规则**：

1. **顺序执行**：必须按 Gate 顺序依次通过，禁止跳过
2. **产出物依赖**：前一 Gate 的产出物是后一 Gate 的必需输入
3. **失败阻断**：任一 Gate 失败必须进入 `blocker` 状态，明确记录 `blocker_type` 和 `next_action`
4. **重入检查**：从 blocker 恢复时必须重新通过当前 Gate，禁止直接跳到下一 Gate
5. **Sub-Agent 强制**：所有调查、分析、验证任务必须通过 Sub-Agent 执行，主 Agent 直接执行视为违规
