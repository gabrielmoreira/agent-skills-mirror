# Lime AgentRuntime Profile 架构蓝图

> 状态：implementation-audited
> 更新时间：2026-05-16
> 作用：定义 AgentRuntime Profile 在 Lime current 主链中的分层、owner、事实源和接口边界。

## 1. 架构目标

本架构只追求五个目标：

1. 让 runtime facts 成为唯一执行事实源。
2. 让 GUI、evidence、review、replay、analysis 只消费同一组 facts。
3. 让 task、turn、tool、action、subagent、job 可以通过稳定 ids join。
4. 让模型路由、成本、限额、权限、沙箱成为 runtime facts。
5. 让公开 AgentRuntime 标准通过 Lime Profile 可测试地落地。

## 2. 总体分层

| 层 | 角色 | 输入 | 输出 | Owner |
| --- | --- | --- | --- | --- |
| Product Surface | 收集用户意图与业务状态 | Chat 输入、Claw `@` 命令、Plugin 表单、Automation job | surface request | Chat / Claw / Plugin / Automation |
| Runtime Surface Adapter | 把 surface intent 适配为统一 runtime request | taskKind、capabilityId、app provenance、request metadata | AgentRuntime submit request | frontend gateway / App Server surface |
| Runtime Control Plane | 接收、排队、中断、恢复 | submit/interrupt/resume/respond/export | accepted turn、queued turn、actions | App Server RuntimeCore |
| Execution Loop | 执行 agent turn | input snapshot、model config、tool inventory | model/tool/action events | Query Loop / runtime_turn |
| Orchestration Facts | 记录 task、routing、permission、sandbox、process、subagent | execution loop 内部状态 | RuntimeEvent stream | AgentRuntime Profile |
| Durable Read Models | 支撑恢复和 GUI 投影 | event log、runtime state | ThreadReadModel、TaskSnapshot | runtime store / repository |
| Evidence Exports | 导出可信制品 | runtime facts、artifacts、verification | evidence pack、replay、review | harness engine / evidence exporter |
| UI Projection | 展示，不定义事实 | read model、evidence summary | Workspace/Harness cards | Agent UI |

## 3. 事实源声明

AgentRuntime 相关能力默认收敛到：

```text
RuntimeEvent + ThreadReadModel + TaskSnapshot + EvidencePack
```

事实方向固定为：

```text
runtime control plane
  -> execution loop
  -> runtime events
  -> durable snapshots / read models
  -> evidence / replay / review
  -> GUI projection / dashboard
```

禁止反向或旁路：

1. GUI 状态反向成为 runtime truth。
2. analysis/review 重新拼 observability summary。
3. replay 不复用 evidence pack。
4. dashboard 用本地 heuristics 推断 task completion。
5. Plugin 用模型 API、App 本地 mock 或嵌入通用 Chat 作为完整 Agent 能力边界。
6. Claw `@` 能力被复制成 Plugin 专用 skill launch。

## 3.2 Surface 边界

Chat、Claw、Plugin、Automation 都是 AgentRuntime 的调用面，不是新的运行事实 owner：

```text
Surface input
  -> AgentRuntime Surface Adapter
  -> Runtime Control Plane
  -> RuntimeEvent / ThreadReadModel / TaskSnapshot / EvidencePack
  -> Surface-specific projection
```

Surface adapter 只允许做：

1. 把 UI / App / job 输入转换为 `taskKind`、`capabilityId`、`inputRef`、`expectedOutput`、`eventSink`。
2. 附加 `appId`、`entryKey`、`workflowRunId`、`artifactPolicyRef`、`evidencePolicyRef` 等 provenance。
3. 选择事件投影目标，例如 conversation stream、PluginTaskStreamEvent、automation job event。

Surface adapter 不允许做：

1. 自己执行模型或工具。
2. 自己判断 task completed / failed / evidence pass。
3. 复制 `runtime_turn.rs`、`tool_runtime.rs` 或 `*_skill_launch.rs` 的执行准备逻辑。
4. 让 App 业务组件直接决定 allowed tools / denied tools。

## 3.1 全球本地化边界

AgentRuntime facts 是跨语言机器事实源，AgentUI presentation 是用户可见本地化层。两者必须分离：

```text
RuntimeEvent stable facts
  -> ThreadReadModel / Evidence facts JSON
  -> AgentUI presentation mapper
  -> i18n key + locale resources
  -> localized UI / markdown presentation
```

架构约束：

1. `RuntimeEvent.type`、`payload.status`、`payload.taskKind`、`payload.source`、`payload.failureCategory`、`reasonCodes[]` 只允许稳定协议值，不允许写入中文、英文或任一 locale 展示文案。
2. `payload.message`、diagnostics summary、provider error 可以作为原始诊断事实保留，但 downstream 不能用字符串包含判断当作状态机。
3. GUI / Harness / Dashboard 必须根据 stable facts 选择 i18n key；新增用户可见文案必须进入 `src/i18n/resources/<locale>/...`。
4. Evidence / Replay / Review 可以生成本地化 Markdown，但必须并存 facts JSON，且 facts JSON 不随 locale 改变。
5. 测试 fixture 的 golden 断言应覆盖 stable facts；本地化测试覆盖 key 是否存在、fallback 是否可控，而不是把中文文案当 profile 合同。

## 4. 核心对象

### 4.1 `RuntimeEvent`

规范化执行事件。首期必需字段：

```text
type
eventId
timestamp
schemaVersion
runtimeId
sessionId
sequence
threadId? / turnId? / taskId? / runId? / stepId? / toolCallId? / actionId? / subagentId? / evidenceId?
payload
refs?
```

### 4.2 `ThreadReadModel`

GUI 与恢复入口。必须表达：

- 当前 thread status
- active turn
- pending actions
- queued turns
- incidents
- tool calls
- routing/limit state
- evidence summary

### 4.3 `TaskSnapshot`

目标工作入口。必须表达：

- task objective
- status
- current run
- attempts
- relationships
- progress
- artifacts/evidence refs

### 4.4 `EvidencePack`

可信导出入口。必须包含：

- runtime correlation spine
- timeline
- tool/process/action failures
- artifacts
- verification outcomes
- applicable known gaps

## 5. Profile 与相邻标准边界

| 标准 | 负责什么 | 不负责什么 | 与 AgentRuntime 的关系 |
| --- | --- | --- | --- |
| AgentRuntime | 执行事实、控制面、事件、快照、恢复 | UI 组件、证据 verdict、上下文内容、artifact bytes | 主链 owner |
| AgentContext | context envelope、context items、source refs、selection、budget、assembly、injection、compaction、missing context | turn 状态和 task 状态 | 由 `context.*` events 或 refs 引用，不复制大上下文 |
| AgentPolicy | policy decision、risk、approval request、permission grant、waiver、redaction/retention obligation、trace | 执行工具或更新 GUI | 由 `permission.*` / `action.*` / `sandbox.*` events 引用 |
| AgentEvidence | evidence pack、claim/source/support/provenance、verification、review、replay、completeness | 重新定义 runtime facts | 消费 runtime facts 导出，并用 completeness 标记缺失 |
| AgentArtifact | artifact bytes、version、preview、diff | 执行状态 | 由 `artifact.changed` 引用 |
| AgentTool | tool declaration、invocation schema、result contract | thread lifecycle | 由 `tool.*` events 引用 |
| AgentUI | projection、layout、interaction、fallback state、controlled actions | runtime truth | 读取 read model / profile events / evidence summary，写入必须回到 owner API |

更细的 owner 边界、连接合同和测试口径见 [./adjacent-protocols.md](./adjacent-protocols.md)。

## 6. Lime 模块映射

| Profile 能力 | 当前或建议 Lime 落点 |
| --- | --- |
| submit turn | `agent_runtime_submit_turn` |
| surface facade | 后续 `agent_runtime_surface_service`，供 Chat / Claw / Plugin / Automation 共用 |
| Plugin task | 后续 `plugin_runtime_cmd` + `plugin_runtime_service`，只作为 App runtime facade |
| Plugin lifecycle | `plugin_cmd.rs`，仅负责 package、installed state、UI runtime、scoped env 注入 |
| Claw capability catalog | 后续 `agent_runtime_capability_catalog_service`，复用现有 `*_skill_launch.rs` 主链 |
| runtime turn | `runtime_turn.rs` / Query Loop 主链 |
| model routing | `request_model_resolution.rs`、`internal/roadmap/task/` |
| thread read | `AgentRuntimeThreadReadModel` |
| evidence export | `agent_runtime_export_evidence_pack` |
| replay export | `agent_runtime_export_replay_case` |
| analysis/review | `agent_runtime_export_analysis_handoff`、review template |
| context owner refs | `turn_context`、`context_trace`、memory / compaction runtime metadata，后续收敛为 `context.*` facts |
| policy owner refs | runtime permission/action/sandbox metadata，后续收敛为 `permission.*` / `action.*` facts |
| GUI projection | Workspace / Harness current read model |
| command contract | frontend gateway、App Server / Electron Host / legacy facade boundary、catalog、mock |

`plugin_cmd.rs` 当前属于 Plugin 生命周期 owner，不是完整 AgentRuntime owner。`LIME_GATEWAY_*` / `OPENAI_BASE_URL` 注入只能视为低阶模型 executor 或开发期 fallback；完整 `lime.agent` / `lime.workflow` 必须进入 AgentRuntime Surface。

## 7. 接口设计原则

### 7.1 写入边界

只有 runtime control plane 或相邻 owner 系统能写事实：

- runtime 写 session/thread/turn/task/action/event/snapshot。
- context 写 context envelope、selection、budget、assembly、injection、missing context，runtime 只引用 refs。
- policy 写 policy decision，然后 runtime 引用。
- artifact 写 artifact bytes/version，然后 runtime 引用。
- evidence 写 evidence pack，然后 runtime 引用。
- UI 写 UI-only projection state；任何会改变事实的动作必须走 runtime / artifact / evidence / policy owner API。

### 7.2 读取边界

消费者只读：

- GUI 读 `ThreadReadModel / TaskSnapshot / EvidenceSummary`。
- review 读 evidence pack 和 runtime timeline。
- replay 读 evidence pack 和 event/snapshot refs。
- dashboard 读 summary，不重新计算事实。

### 7.3 兼容边界

兼容层只能做字段映射：

```text
legacy state -> AgentRuntime profile field
```

不能做：

```text
legacy state -> new parallel truth -> UI/evidence
```

## 8. 最小数据合同

### 8.1 Event payload 最小约束

| Event | payload 必须包含 |
| --- | --- |
| `turn.submitted` | `inputRef`、`source`、`status` |
| `action.required` | `actionType`、`decisionKind`、`scope` |
| `task.attempt.failed` | `status`、`retryable`、`failureCategory` |
| `routing.single_candidate` | `taskKind`、`candidateCount`、`selectedModel`、`decisionSource` |
| `evidence.changed` | `packRef`，可选 `replayRef`、`verificationOutcomes` |

### 8.2 Snapshot 最小约束

`SessionSnapshot` 至少包含：

- `schemaVersion`
- `runtimeId`
- `sessionId`
- `updatedAt`
- `threads[]`
- `tasks[]`
- `taskSummary`
- `routingLimitSummary`
- `telemetrySummary`
- `evidenceRefs[]`

## 9. 验证策略

1. Schema fixture 校验：验证 Lime Profile fixtures。
2. Command mapping 测试：验证 Electron Desktop Host / App Server / legacy facade、frontend gateway、mock / catalog 与 profile control plane 一致。
3. Event replay 测试：用 event stream 重建 ThreadReadModel。
4. Evidence consistency 测试：确认 evidence/replay/review 读同一事实源。
5. GUI smoke：确认 Workspace/Harness 展示 read model，而不是 UI-only truth。

## 10. 不允许的架构形态

1. 新增 `runtime_dashboard_state` 作为 GUI 事实源。
2. 新增 `analysis_observability_builder` 拼第二套 observability。
3. 新增 `task_center_status` 与 `TaskSnapshot.status` 不一致。
4. tool/process/action 只写入文本消息，不写 runtime event。
5. rate limit / quota / cost 只进日志，不进 runtime facts。
6. Plugin 新增平行 runtime facts、工具权限系统或垂直专用 Agent command。
