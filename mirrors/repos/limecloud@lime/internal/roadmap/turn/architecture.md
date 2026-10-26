# Turn / Tool 生命周期架构设计

> 状态：已实现并作为 current 参考
> 更新时间：2026-06-19
> 作用：定义 Lime turn 执行、工具生命周期、事件流、read model 和 GUI 投影的目标架构。

## 1. 架构目标

本架构只解决一条主线：

```text
让一个 turn 中的所有模型输出、工具调用、工具结果、计划、reasoning、最终答复都能按稳定 item 边界记录、恢复和渲染。
```

目标：

1. 消除 `item.*` 与 `tool.*` 并列事实源。
2. 消除 WebSearch / WebFetch 多工具结果串线。
3. 让首字慢时有真实运行状态可展示。
4. 让历史 hydrate 与 live stream 使用同一投影规则。
5. 让多模型、多 provider、Codex import、OpenAI-compatible Responses API 都能映射到同一 item lifecycle。

## 2. 总体分层

| 层 | 职责 | 输入 | 输出 | Owner |
| --- | --- | --- | --- | --- |
| Product Surface | 收集用户输入和 UI 上下文 | Chat / Claw / Plugin / Automation 输入 | submit request | Frontend |
| Frontend Runtime Gateway | 调用 current App Server API，绑定 request id 和 session id | submit request | accepted / stream subscription | `src/lib/api/agentRuntime/*` |
| Runtime Control Plane | 创建 session/thread/turn，排队、中断、恢复 | submit / interrupt / respond | turn lifecycle | App Server RuntimeCore |
| Execution Loop | 调模型、调工具、处理 retry / synthesis | turn input snapshot | runtime agent events | `lime-rs/crates/agent` / Agent |
| Item Projector | 把 provider message、tool request、tool response 映射为 item lifecycle | provider / tool events | `item.*` events | Agent `TurnItemRuntimeProjector` |
| Event Log | 持久化 canonical event stream | runtime events | session jsonl / replay input | App Server |
| Read Model | 聚合 turn、item、tool、message、action 状态 | event log / live events | ThreadReadModel | App Server |
| AgentUI Projection | 把 read model / live event 投成 UI events | AgentEvent / ThreadReadModel | projection store | Frontend |
| Message Timeline | 展示 turn items，不定义事实 | projection state | visible UI | Workspace |

## 3. 事实源声明

Turn 工具生命周期的唯一事实源是：

```text
Turn + AgentThreadItem + item lifecycle
```

最小关联键：

```text
session_id
thread_id
turn_id
item_id
sequence
item.type
item.status
started_at
updated_at
completed_at?
```

工具类 item 额外必须有：

```text
tool_call_id = item.id
tool_name
arguments?
output?
success?
error?
metadata?
```

### 3.1 事件方向

正确方向：

```text
provider/tool runtime
  -> ItemRuntime
  -> AgentEvent::ItemStarted / ItemUpdated / ItemCompleted
  -> App Server item.started / item.updated / item.completed
  -> ThreadReadModel.items[]
  -> Frontend threadItemProjection
```

兼容方向：

```text
ItemRuntime
  -> legacy tool.started / tool.result
  -> old clients or transient details
```

禁止方向：

```text
legacy tool.started/tool.result
  -> GUI canonical tool card
  -> ThreadReadModel terminal state
```

历史缺失 item 生命周期时允许一次性补偿：

```text
legacy tool events
  -> synthetic item
  -> marked metadata.source = legacy_tool_event
```

## 4. 核心对象

### 4.1 Turn

Turn 表达一次用户输入到最终结果的执行边界：

```text
id
thread_id
prompt_text
status: running | completed | failed | canceled | interrupted
started_at
completed_at?
error_message?
```

约束：

1. 一个 active turn 的 live stream 必须只更新这个 turn。
2. 新 turn 开始时，前一 turn 的 completed items 不得被 active stream 覆盖。
3. 历史恢复时，turn status 只能由 terminal event 或 read model projection 决定。

### 4.2 TurnItem

TurnItem 表达 turn 内有序运行项：

```text
id
thread_id
turn_id
sequence
type
status
payload
started_at
updated_at
completed_at?
```

首期类型：

| 类型 | 说明 | 终态来源 |
| --- | --- | --- |
| `user_message` | 用户输入 | submit accepted |
| `agent_message` | assistant 正文 | provider message final / turn completed |
| `reasoning` | thinking / reasoning | provider reasoning item |
| `plan` | `<proposed_plan>` 或 plan update | provider structured item |
| `tool_call` | 普通工具、WebSearch、WebFetch、MCP、browser、shell | tool result / failed |
| `command_execution` | 命令执行 | process terminal |
| `patch` | patch apply | patch terminal |
| `approval_request` | 工具审批 | action resolved |
| `request_user_input` | 用户输入请求 | action resolved |
| `file_artifact` | 文件/制品 | artifact persisted |
| `warning` / `error` | 诊断 | emitted event |
| `turn_summary` | runtime status summary | runtime status item |

### 4.3 ToolCall Item

工具 item 是 `tool_call_id` 的 owner：

```text
item.id == tool_call_id
item.type == "tool_call"
item.status: in_progress | completed | failed
payload.tool_name
payload.arguments
payload.output
payload.success
payload.error
payload.metadata
```

约束：

1. `tool_start` 不得创建第二个 tool item。
2. `tool_end` 不得覆盖已 completed 的 item terminal state，除非它是同一 `tool_call_id` 的补充字段。
3. `tool_input_delta` 只更新 input draft，不改变 item terminal status。
4. `tool_output_delta` 只追加 output stream，不改变 item terminal status。
5. `tool_progress` 只更新 transient progress，不写成 completed。

## 5. 多模型和 provider 映射

不同 provider 只允许影响 adapter，不允许影响 read model / UI 合同：

| Provider 形态 | 映射规则 |
| --- | --- |
| OpenAI Responses function_call | `call_id -> tool_call_id`，function name -> `tool_name` |
| OpenAI hosted web_search | `ResponseItem::WebSearchCall` -> `tool_call` item，metadata 标记 hosted |
| Anthropic-style tool_use | `id -> tool_call_id`，input -> arguments |
| Agent MessageContent::ToolRequest | 创建或更新 `tool_call` item |
| Agent MessageContent::ToolResponse | complete/fail 同一 `tool_call_id` item |
| Codex import rollout item | 直接导入为 turn item，legacy event 只派生 |

## 6. WebSearch / WebFetch 目标行为

WebSearch 是普通工具 item，不是单独状态机：

```text
WebSearch item started
  -> WebSearch item completed
  -> WebFetch item started
  -> WebFetch item completed
  -> assistant final agent_message item
```

搜索策略只负责约束工具可用性和最低证据，不负责 UI 分组：

1. `RequestToolPolicy` 可以验证 required/allowed/disallowed tools。
2. `WebSearchExecutionTracker` 可以临时判断证据是否足够。
3. UI 分组必须只看 item lifecycle。
4. 不能再用中文关键词或 prompt 文本判断是否“新鲜联网”。

## 7. 首字慢和“像卡住”的解决方式

首字慢不能靠前端假进度解决。正确做法：

1. submit accepted 后立即生成 `turn_started`。
2. runtime status 作为 `turn_summary` 或 diagnostics event 展示准备态。
3. 工具开始时立即生成 `item_started(tool_call)`。
4. 工具 input/progress/output delta 绑定到同一 tool item。
5. 最终正文慢时，UI 仍能看到真实 turn 和 item 进展。

## 8. 历史和第二轮输入

历史恢复规则：

1. 已 completed turn 的 items 是 immutable projection input。
2. active turn stream 只能追加或更新 active turn。
3. timeline grouping 必须按 `turn_id` 分组，再按 `sequence` 排序。
4. 第二轮输入开始时，不允许清空或重算上一轮 assistant final text。
5. 如果 live stream 与 history hydrate 同时返回同一 turn，按 `event.sequence` 和 item terminal status 去重。

## 9. 与 AgentRuntime / AgentUI 的关系

本路线图是 AgentRuntime Profile 的 turn/item 子问题，不新建平行 runtime：

```text
AgentRuntime owns execution facts
Turn roadmap owns turn/item lifecycle constraints
AgentUI owns projection and presentation
Workspace owns visual layout only
```

GUI 不允许写回 runtime truth；任何用户动作必须回到 App Server current API。
