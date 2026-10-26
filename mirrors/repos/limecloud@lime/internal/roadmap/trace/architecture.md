# Claw Trace 目标架构

> 状态：target architecture draft
> 更新时间：2026-06-27
> 目标：建立可开关、低侵入、可导出、可回放的 Claw Trace 体系，并让它复用现有 App Server / runtime event / diagnostics 主链。

## 1. 架构原则

### 1.1 Trace 不是第二套事实源

Trace 只观察和投影现有事实：

```text
AgentRuntimeEvent / RuntimeEvent / renderer stream lifecycle
```

新增 instrumentation 只允许补时间点、span 边界和关联 id，不允许把 Trace 当业务状态来源。

### 1.2 先 envelope，再 payload

借鉴 Codex `rollout-trace`：所有 raw trace event 使用统一 envelope，payload 再按类型扩展。

```text
RawTraceEvent
  schema_version
  seq
  wall_time_unix_ms
  monotonic_ms
  trace_id
  run_id
  span_id
  parent_span_id
  session_id
  thread_id
  turn_id
  event_type
  payload
  redaction
```

这样做的收益：

1. 先保证排序、关联和回放。
2. payload schema 迭代不会破坏基础读取。
3. 可以在 projector 不理解新事件时仍保留原始证据。

### 1.3 采集和投影分离

```text
TraceCollector
  -> RawTraceWriter
  -> TraceStore
  -> TraceProjector
  -> Developer UI / export / support bundle
```

采集层只负责写 append-only event，不直接生成 UI view model。

### 1.4 默认安全

默认配置：

```text
enabled: false
level: off
sampling_rate: 0
include_content: false
include_provider_payload: false
retention_days: 3
max_event_payload_bytes: 16 KiB
```

开发者开启后才采集 summary / diagnostic / verbose。配置必须可恢复默认。

## 2. 配置模型

目标配置挂在现有 developer 配置下：

```ts
type ClawTraceLevel = "off" | "summary" | "diagnostic" | "verbose";

interface ClawTraceDeveloperConfig {
  enabled: boolean;
  level: ClawTraceLevel;
  samplingRate: number; // 0..1
  retentionDays: number; // default 3
  includeContent: boolean; // default false
  includeProviderPayload: boolean; // default false
  maxPayloadBytes: number;
}
```

建议落点：

```text
Config.developer.claw_trace
```

调试 override 可使用 localStorage 或 env，但必须低优先级可撤销，且 UI 能显示当前 override 来源。

## 3. ID 模型

| ID                    | 生命周期                             | 来源                                          |
| --------------------- | ------------------------------------ | --------------------------------------------- |
| `trace_id`            | 一次用户提交到可见完成 / 失败 / 取消 | renderer submit 创建；App Server 缺失时补建   |
| `run_id`              | 一次 Claw turn runtime run           | 与 eventName / turn run 关联                  |
| `span_id`             | 一个阶段或子操作                     | TraceCollector 创建                           |
| `parent_span_id`      | span tree 父节点                     | 调用方上下文传递                              |
| `session_id`          | Claw session                         | existing runtime                              |
| `thread_id`           | runtime thread                       | existing runtime                              |
| `turn_id`             | runtime turn                         | existing runtime                              |
| `provider_request_id` | provider HTTP request                | response headers / provider trace event，可空 |

## 4. Span 分层

P0/P1 固定 span taxonomy：

```text
claw.turn
  renderer.submit
  app_server.turn
    app_server.routing
    app_server.context_prepare
    agent.reply
      agent.tool_surface
      provider.inference
        provider.request
        provider.stream
    app_server.event_emit
  bridge.delivery
  renderer.stream
    renderer.event_receive
    renderer.text_apply
    renderer.render_flush
    renderer.first_paint
```

所有 span 只记录结构化 stage，不用自然语言正文判断。

## 4.1 W3C / OpenTelemetry 边界

W3C `traceparent / tracestate` 只承担跨进程传播职责，不替代 Lime 内部 `trace_id / run_id / request_id`。

当前 S19 App Server / Agent / provider 边界：

1. Renderer 在 `agentSession/turn/start.runtimeOptions.metadata.agentUiPerformanceTrace.w3cTraceContext` 中携带合法 carrier。
2. App Server `trace_context.rs` 统一校验和归一化 carrier；非法 `traceparent` 记录 warning / `w3c.traceparent.valid=false`，不阻断 turn。
3. `processor/request_trace.rs` 创建 `app_server.request` server span，并通过 `otel_trace.rs` 把合法 carrier 设置为 OpenTelemetry remote parent。
4. OTLP exporter 默认关闭；只有开发者显式设置 `APP_SERVER_OTEL_EXPORTER=otlp`、`OTEL_TRACES_EXPORTER=otlp`、`OTEL_EXPORTER_OTLP_ENDPOINT` 或 `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` 时，App Server 才安装 OTEL subscriber/exporter。
5. stdio transport 不安装 fmt subscriber，不向 stdout 写 tracing 日志，避免污染 JSON-RPC。
6. span attributes 只保留安全 scalar：`rpc.*`、client、session/turn、`claw.*`、`w3c.trace_id / parent_span_id / trace_flags / traceparent.valid`；不记录 prompt、assistant delta、provider payload、raw JSONL 或 `tracestate`。
7. App Server `runtime_backend/request_context.rs` 把合法 carrier 投影到 Agent `TurnContextOverride.metadata.w3c_trace_context`；Agent `session_context.rs` 复用现有 request correlation 管道，最终由 `providers/api_client.rs` 在所有 provider HTTP request 上注入标准 `traceparent / tracestate` header。非法 `traceparent` 不注入，`tracestate` 不单独传播。

## 4.2 Provider Request ID 边界

Provider request id 只用于把 Lime 本地 trace 与上游 provider 日志 / 工单关联，不用于驱动 UI 状态。

当前 S20 边界：

1. Agent 在统一 provider HTTP builder 捕获 response headers，不修改每个 provider trait 返回类型。
2. 只从 request-id 类 header 读取小型 scalar：`x-request-id`、`x-oai-request-id`、`x-openai-request-id`、`request-id`、`x-amzn-requestid`、`x-amz-request-id`、`x-goog-request-id`、`x-ms-request-id`。
3. request id 必须是非空、长度不超过 256、只包含 header-safe visible ASCII 的字符串；不安全值直接丢弃。
4. `request_started` 阶段还没有 response headers，不写 provider request id；`first_event / first_text_delta / failed / canceled` 可携带已捕获的 request id。
5. App Server raw trace store 只把 `provider_request_id / provider_request_id_header` 放进 summary-only metrics 白名单，不保存 provider response body、prompt、assistant delta text、raw AgentEvent payload 或 `tracestate`。
6. 参考 Codex 的边界是 `rollout-trace` 中 inference 完成 / 失败 / 取消事件的 `upstream_request_id`，以及 `response-debug-context` 中 header-only 的 request id 提取；Lime 不照搬 cf-ray、authorization error 或 HTTP body 解析。

## 5. Raw event 类型

P0 最小事件集：

| event_type                    | 说明                                 |
| ----------------------------- | ------------------------------------ |
| `trace.started`               | trace root 创建                      |
| `trace.ended`                 | trace 完成 / 失败 / 取消             |
| `span.started`                | span 开始                            |
| `span.ended`                  | span 结束                            |
| `checkpoint.recorded`         | 不适合完整 span 的瞬时时间点         |
| `runtime_event.observed`      | 观察到 existing runtime event        |
| `message_delta.emitted`       | App Server 发出 message.delta        |
| `renderer_event.received`     | renderer 收到 processed event        |
| `renderer_text_delta.applied` | text_delta 写入本地 state            |
| `renderer_text.flush`         | 文本刷新到 overlay / message         |
| `renderer_text.first_paint`   | 首字 paint                           |
| `trace.warning`               | 采集缺口 / 时钟异常 / payload 被截断 |

P1 增加：

| event_type                           | 说明                                                |
| ------------------------------------ | --------------------------------------------------- |
| `provider.request.started`           | provider 请求开始                                   |
| `provider.first_event.received`      | App Server / Agent 观察到首个 provider stream event |
| `provider.first_text_delta.received` | App Server / Agent 观察到首个 provider text delta   |
| `provider.failed`                    | provider 请求失败                                   |
| `provider.canceled`                  | provider 请求取消                                   |
| `tool_surface.resolved`              | 工具面构建完成                                      |
| `context_prepare.ended`              | context / skills / memory / plugin 准备完成         |

Renderer 侧将 `provider.*` notification 投影为 `provider_trace` 诊断事件，只记录 `agentStream.providerTrace` metrics，不驱动消息 UI。Summary projector 使用 `provider.first_text_delta.received.elapsed_ms` 生成 `providerWaitMs`，使用首个 `message.delta.server_event_emitted_at -> firstTextPaint` 生成 `clientLocalOutputMs`，避免把 provider/API 等待误归因到 Lime 客户端。

Provider trace event 可以携带 provider response header request id。该字段只作为 summary-only 安全 metrics 导出，用于关联上游 provider 日志，不参与 latency 计算。

## 6. 存储

Trace store 必须走平台无关路径 resolver，不硬编码用户目录。

当前 S8 内部实现：

```text
runtime/
  traces/
    sessions/
      session_<safe_session_id>/
        trace_<safe_trace_id>.jsonl
```

当前规则：

1. `TraceEventWriter` 只消费已装饰的 `AgentEvent.payload.trace`，不新增第二套 runtime event。
2. `RawTraceEvent` 固定包含 `schema_version / seq / wall_time_unix_ms / trace_id / run_id / request_id / session_id / thread_id / turn_id / event_id / event_sequence / event_type / checkpoint / metrics / redaction`。
3. `redaction.mode = summary_only`，不保存 raw AgentEvent payload、不保存 prompt、不保存 provider payload、不保存 assistant delta 文本。
4. 每个 session 保留最近 100 个 trace JSONL 文件。
5. Writer 按 Codex `TraceWriter` 思路缓存每个 trace 文件的 `next_seq`；同一 trace 多次 append 不做全文件计数，retention 只在新 trace 文件创建后触发。
6. 当前已开放 raw trace JSON-RPC read/list API：`diagnostics/trace/list`、`diagnostics/trace/read`；返回仍固定为 summary-only envelope，不含 prompt / provider payload / assistant text。
7. Provider request id 属于 metrics 白名单；`tracestate`、provider response body、assistant delta text 和 raw JSONL 原始字节不进入 metrics。
8. raw trace export zip / support bundle 选择性 raw trace 尚未开放；对普通诊断包仍只默认输出 compact Agent UI performance summary。

目标结构：

```text
diagnostics/
  traces/
    manifest.json
    sessions/
      <session_id>/
        <turn_id-or-run_id>.trace.jsonl
        <turn_id-or-run_id>.summary.json
```

规则：

1. Raw trace append-only JSONL。
2. Summary 是 projector 派生物，可删除重建。
3. payload 超过阈值写 payload ref 或截断摘要。
4. 默认保留 3 天或最近 100 个 turns。
5. support bundle 只包含 summary + 选中的 raw trace，避免无界导出。

## 7. 脱敏与内容策略

| 内容                  | summary         | diagnostic      | verbose        |
| --------------------- | --------------- | --------------- | -------------- |
| stage / duration      | 采集            | 采集            | 采集           |
| model / provider id   | 采集            | 采集            | 采集           |
| absolute cwd          | hash + basename | hash + basename | 可选完整路径   |
| user prompt           | 不采集          | 长度 + hash     | 可选截断       |
| assistant delta       | 不采集          | 长度 + hash     | 可选截断       |
| provider request body | 不采集          | 不采集          | 显式开启后截断 |
| API key / env         | 永不采集        | 永不采集        | 永不采集       |

任何 level 都必须先过 secret-like scanner。

## 8. 导出

导出格式：

```text
trace-export/
  manifest.json
  trace.jsonl
  summary.json
  flamegraph.json
  runtime-events.sample.json
  renderer-metrics.json
```

`manifest.json` 必须包含：

1. app version / commit hash 如可得。
2. trace schema version。
3. config level。
4. redaction policy。
5. session_id / turn_id / trace_id。
6. start / end time。
7. known gaps。

## 9. 与现有诊断主链关系

Trace 不新增普通用户侧入口，集成到：

```text
Developer & Labs
  -> Diagnostic Logs
  -> Support Bundle
  -> Claw Trace
```

App Server 侧优先复用：

```text
diagnostics/supportBundle/export
diagnostics/logStorage/read
log/diagnosticHistory/clear
```

如果后续需要新增 App Server method，命名建议为：

```text
trace/config/read
trace/config/write
trace/session/list
trace/session/read
trace/session/export
trace/history/clear
```

新增时必须同步 protocol、client、processor、frontend API 网关、contract tests 和 governance catalog。
