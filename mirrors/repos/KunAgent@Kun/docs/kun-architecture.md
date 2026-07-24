# Kun GUI 单运行时方案

本文记录 Kun 桌面应用现在应该如何围绕一个专门服务 GUI 的
Kun 改造。结论先说清楚：GUI 只保留一个 agent，唯一 ID 是
`kun`；Code、Design、Write、连接手机都通过同一条 `kun serve`
HTTP/SSE 边界工作；历史运行时、旧绘画/设计 starter、运行时诊断面板、
agent 切换都不再是产品表面。

## 目标边界

```text
Renderer (React + Zustand)
  Code / Design / Write / Connect phone UI
        |
        | window.kunGui.runtimeRequest(path, method, body)
        | window.kunGui.startSse(threadId, sinceSeq)
        v
Preload IPC bridge
        |
        v
Main process
  RuntimeHost -> kunRuntimeAdapter
  process/config/port/token management only
        |
        v
kun serve (TypeScript package)
  /health
  /v1/threads
  /v1/threads/{id}/turns
  /v1/threads/{id}/events
  /v1/threads/{id}/fork
  /v1/sessions/{id}/resume-thread
  /v1/approvals/{id}
  /v1/user-inputs/{id}
  /v1/usage
  /v1/workspace/status
```

这个边界采用本地 HTTP 服务架构：GUI 不直接嵌 agent loop，不通过
stdio/RPC 混跑多个状态机，只把 `kun serve` 当成稳定协议。Kun 内部使用
cache-first loop：immutable prefix、append-only log、bounded LRU/TTL cache、
inflight cleanup、steering queue、context compaction、usage/cache telemetry。

## 缓存命中优化

Kun 的缓存命中率要按 provider 原生 usage 字段优先计算和优化：

- 模型 client 优先解析 provider 原生
  `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`。只有原生字段缺失
  时，才退回 `prompt_tokens_details.cached_tokens`、`cache_read_input_tokens`
  等兼容字段。
- cache hit rate 使用 `hit / (hit + miss)`，不使用
  `hit / prompt_tokens`。provider 原生 miss 不一定等于 `prompt_tokens - hit`。
- `kun/src/prompt/kun-system-prompt.ts` 是稳定前缀。它只放长期
  不变的 Kun 运行契约，不能放 workspace、时间戳、文件片段、选中文本、
  用户动态信息或一次性工具结果。
- `ImmutablePrefix` 在每次 model step 前调用 `verifyImmutablePrefix()`。
  如果有人绕过 `setSystemPrompt` / `setTools` / `setFewShots` 直接改 prefix，
  开发和测试期会立即暴露 fingerprint drift，而不是悄悄牺牲缓存。
- few-shot fingerprint 只计算真正会发给模型的内容，不计算 item id、turn id、
  thread id、时间戳等 GUI/存储层动态字段。
- 工具 schema 在发送到模型前 canonical sort，避免同一工具集合因为顺序或
  schema key 顺序变化造成 prefix churn。
- 每个 turn 会持久化 canonical tool catalog fingerprint 和 tool count；同一
  scope 下工具定义漂移时会标记 `toolCatalogDrift`，便于排查 cache miss。
- 历史消息发送给上游模型前会做共享的 model-history repair：孤儿
  `tool_result` 不发，缺少对应 result 的 `tool_call` 不发；同一次响应里的
  多个 tool call 会重组为一个合法 assistant `tool_calls` 消息，避免
  400/retry 造成额外延迟和缓存浪费。
- 同一模型回合里连续的 built-in 只读工具 `read` / `grep` / `find` / `ls`
  会小批量并发执行，但 `tool_result` 仍按 call 顺序写入，减少等待时间的同时
  不让动态历史随完成顺序抖动。
- Serve runtime 会从 persisted usage event 恢复累计 cache hit/miss counters，
  重启或 resume 后 runtime usage 面板不重新从 0 计算。
- 动态上下文必须追加在稳定前缀之后。compaction、resume、fork、plan context
  也不得改写稳定系统前缀。

冷启动第一轮可能仍然低或为 0，因为服务端还没有同一前缀可读；热起来后应稳定
超过 90%。2026-06-02 的真实 Kun 临时线程验证：

- 12 轮短消息：去掉冷启动后的热命中 `94.7%`，最新一轮 `93.6%`。
- 同一稳定前缀热身后 24 轮短消息：整体含冷启动 `95.2%`，最新一轮 `98.1%`。

优化前已经持久化的旧 usage 事件不会被事后改写，因为当时没有保存
provider 原生缓存字段；这些历史数据只能作为旧实现的证据，不能证明新实现仍然低命中。

## Subagent 召回与派发

`delegate_task` 把可信的内置、GUI 配置和工作区 `.kun/agents/*.md` 目标统一成
独立 agent profile 检索集合，不再存在 skill worker。仓库可编辑的
`.kun/agents/*.md` 进入自动 BM25/LLM 召回（仅索引 id/name/description，不索引
body），也可按精确 ID 显式选择，并出现在设置页与工作台右侧子代理面板（带
「自定义」标签；定义来自 markdown，面板内只读）。未写 `toolPolicy` 时默认只读；显式
`toolPolicy: inherit` 时可在父能力快照内使用写工具。`omit_base_prompt: true`
时 child 只用 role prompt，不再 prepend Kun base。宿主仍强制禁用 Skills、
屏蔽 model/provider/reasoning 覆盖，并阻止嵌套 `delegate_task` /
`generate_subagent`。

Subagent 目录按产品 surface 分层。`shared` 是 Code、Write、Design 强制继承的
基础池，其余 profile 可以属于一个或多个 `code` / `write` / `design` surface；
空 surface 列表表示不参与派发。Renderer 在每个 turn 持久化 `agentSurface`，旧 turn
缺失时按 Code 兼容。自动 BM25、LLM Top-5 判断、生成器样例选择和显式 profile
解析都只能看到“shared + 当前 surface”，跨模式显式调用会被宿主拒绝。child-run
同时记录 surface，确保历史派发可解释、可复现。

设置页以“基础 / Code / 写作 / 设计”配置同一份 profile 定义，不复制 Agent；搜索和
分类后按 12 条分页。工作台侧栏不分页，只展示当前 surface 的有效集合。内置
`general` 始终属于 shared，作为稳定兜底；旧自定义 profile 没有 surface 字段时按
shared 读取，保持升级前的全局可用语义。

内置目录共 45 个角色，其中 8 个中文本地化核心角色标记为基础代理并默认启用；其余
25 个 agent-skills 角色、6 个 Write 和 6 个 Design 专属角色默认不分配 surface。
工作台可通过“扩展代理”总开关一次性启用这 37 个角色，或通过“仅保留基础代理”
清空全部扩展角色的 surface 分配。

未显式指定 `profile` 或 `custom_agent` 时，派发顺序固定为：

1. 对 ID/名称、description 和单一权威目录中的双语能力 facets 建立字段加权
   BM25 索引，使用 `k1=1.2`、`b=0.75`，并按任务显式只读/修改意图做策略加权后
   只保留 Top 5。真实 33-Agent 中英 query 集持续验证 Recall@5。
2. 使用 `roles.smallModel`（未配置则父会话/运行时模型）做一次无工具、JSON
   约束的判断。模型只能选择 Top 5 中的 profile，且 confidence 至少为 0.60；
   低于阈值或没有完整匹配时返回生成角色所需的 brief。
3. 无合适项时由独立 `SubagentGenerator` 从最多 3 个可信内置 agent prompt 中总结
   设计模式，生成只对本次 child run 生效的完整 profile；它不写入 settings 或
   workspace，并强制屏蔽 `delegate_task`、`generate_subagent`、`load_skill`。
4. 判断模型超时、报错、输出非法 JSON 或虚构候选 ID 时，只有任务明确点名
   Top 1 的 ID/名称才直达该候选；普通词面重叠不足以证明适配，此时与完全无召回
   一样进入独立生成器；失败路径默认 read-only，只有显式权限选择或一次有效的
   LLM 判断可以要求 inherit。父 abort 会直接终止派发，不会生成 fallback child。

显式 `profile` 是稳定直达路径；选中的 profile 会连同来源和权限在执行前快照，
不在 recall 与 run 之间重新读取。`custom_agent` 允许主 agent 直接给出一次性角色，
`generate_subagent` 则显式要求系统自动设计并立即执行临时角色。任何路径都不能扩大
父 turn 的 approval policy、sandbox 根、工具/工具 Provider allowlist、denylist 或 Memory
边界；有效能力始终是父快照与 profile 约束的交集。独立 workflow agent 和生成 agent
都禁用 Skills 自动激活。child record 持久化 route method、Top 5、选择理由、置信度、
生成样例及临时角色快照；router 与 generator 的 usage 分别计入父 thread。

下一阶段仍值得推进的缓存能力：

- 工具集合 mutation gate：新增工具允许 append，编辑、重排、删除工具时要求
  restart 或新会话边界，避免热前缀突然全量 miss。当前 Kun 已排序工具
  schema，但还没有把“工具集合变更策略”做成显式产品规则。
- LLM fold summarizer：`contextCompaction.summaryMode: "model"` 时，自动压缩和
  GUI `/compact` 都会额外请求模型生成结构化摘要，并复用主 agent 的 system /
  few-shot 前缀；超时、空响应或模型错误会降级到启发式摘要。
- 大工具结果 token cap 和长参数 markerize：当前本地工具输出较小；一旦加入
  shell、文件全文、网页抓取类工具，需要在进入历史窗口前按 token 截断或标记化，
  不让超大 tool result 把 append-only log 撑爆。
- volatile scratch 边界：assistant reasoning 现在不会上传给模型，但仍会落 GUI
  历史。未来若加入内部计划、临时草稿或子 agent scratch，应保持“可展示”和
  “可重放给模型”分离。

## GUI 要拆的东西

Renderer 只应展示 Kun。需要删除或保持删除的 UI 面包括：

- Agent 切换器：`AgentSwitcher` 不再出现，`AGENT_CATALOG` 只有
  `kun`。
- 顶部连接状态条和 runtime 诊断按钮：不再把运行时检测作为用户入口。
- Runtime insights/right panel：右侧面板只保留 Changes、Preview、Plan、
  File 等 GUI 工作区视图，不再有 runtime/usage 控制台。
- 斜杠菜单里的 `/usage`、`/runtime`：这些命令会暗示还有可切换运行时。
- 设置页 provider selector：Settings -> Agents 直接展示 Kun 配置，
  包含 binary path、port、autoStart、API key、base URL、runtime token、
  data dir、model、approval policy、sandbox mode、insecure。
- 旧绘画/设计 starter：不恢复与当前 Design 模式并行的旧入口。核心工作区入口是
  Code、Design、Write，连接手机和自动化仍走各自入口。

## Main / Preload 要拆的东西

主进程和 preload 不再暴露旧 agent IPC：

- 删除历史运行时的 spawn/update/diagnostics IPC。
- 删除历史 RPC event bridge。
- 删除历史 adapter、HTTP bridge、updater、binary resolver 和 process manager。
- 删除 Kun 之外的 diagnostics/importer 模块。用户要的是可用的单
  agent，不是运行时检测中心。

主进程现在只需要：

- `kunRuntimeAdapter`：启动/停止 `kun serve`、同步 config、
  计算 base URL、附加 auth header。
- `runtimeRequestViaHost`：确保 Kun running 后转发 `/v1/*`。
- `startSse/stopSse`：按 `threadId + sinceSeq` 转发 Kun SSE。

## Settings / Migration

保存后的 settings 结构只应有：

```json
{
  "agentProvider": "kun",
  "agents": {
    "kun": {
      "binaryPath": "",
      "port": 18899,
      "autoStart": true,
      "apiKey": "",
      "baseUrl": "https://api.deepseek.com/beta",
      "runtimeToken": "<generated-local-token>",
      "dataDir": "~/.kun/data",
      "model": "deepseek-v4-pro",
      "approvalPolicy": "auto",
      "sandboxMode": "workspace-write",
      "insecure": false
    }
  }
}
```

代码里仍允许出现历史 provider 字符串的唯一原因是读取旧 settings 文件时做
一次性迁移：

- 历史 `agentProvider` 值归一为 `kun`。
- 历史 provider 的 port、autoStart、API key、base URL、runtime token、
  approval、sandbox、model 会种到 `agents.kun`。
- 迁移后的落盘文件不再保留历史 provider 配置块。
- 连接手机（内部旧名 Claw）的历史 `agentThreadIds` 只折叠成
  `agentThreadIds.kun`，不保留 per-agent map。

## Code / Design / Write / 连接手机如何走 Kun

- Code：`KunRuntimeProvider` 负责 list/create thread、send turn、
  steer、interrupt、compact、approval、SSE 映射。Chat UI 不知道旧
  provider。
- Design：设计工作区创建/复用 Kun thread，设计稿、原型和设计流程图落在
  `.kun-design/`，通过画布预览和版本记录迭代；确认后的设计可以发布
  `DESIGN_SYSTEM.md`，再打开新的 Code thread 执行实现。
- Write：写作助手和 inline completion 读取同一份 Kun API key /
  base URL 配置。Write thread registry 只把写作线程识别为 Kun
  thread，不再区分旧运行时会话。
- 连接手机：定时任务、飞书/Lark/微信、IM webhook 创建或复用 Kun thread。
  代码内部仍沿用 `claw` route / settings key / runtime 文件名，作为旧命名兼容。
  `threadId` / `localThreadId` 字段只作为旧 settings 兼容字段存在，真正
  当前映射写入 `agentThreadIds.kun`。

## GUI HTTP 功能等价面

运行时归一不是只保留聊天。Kun 的 GUI HTTP 面必须覆盖 store/UI
已经依赖的能力：

- `GET /v1/threads` 支持 `limit`、`search`、`include_archived`、
  `archived_only`。默认隐藏 archived/deleted，会话搜索和归档视图不依赖
  GUI 本地猜测。
- `POST /v1/threads/{id}/fork` 复制 thread 历史、写入 fork lineage，
  并把历史 item 写回新 thread 的 session store。复制时会把 pending
  approval/user-input 规整为不可继续操作的历史状态，避免新会话悬挂旧 gate。
- `POST /v1/sessions/{id}/resume-thread` 沿用历史 resume 路径。
  Kun 优先从同名 thread 恢复；没有 thread 时从 session snapshot
  或 JSONL items 重建 turns；找不到时返回 404，而不是在 GUI 抛
  unsupported。
- `POST /v1/user-inputs/{id}` 和旧兼容路径 `/v1/user-input/{id}` 都可接收
  `{ answers }` 或 `{ cancelled: true }`。AgentLoop 通过 `request_user_input`
  / `user_input` tool 暂停，GUI 回答后继续模型回合。
- `POST /v1/approvals/{id}` 继续支持工具审批；approval 和 user-input 都是
  gate/route/service 分层，不在 renderer 内实现 agent 逻辑。
- `GET /v1/usage?group_by=thread|day` 返回累计 token、turn、cache hit 数据。
  Workbench 首页和 composer 底部只消费 Kun usage，不再打开 runtime
  insights 面板。

## 已删除/应保持删除的旧入口

旧 agent 运行路径不应再回来：

- 历史 runtime adapters / bridges
- 历史 runtime process managers / binary resolvers
- 历史 runtime update modules
- Kun 之外的 diagnostics/importers

旧 UI 入口不应再回来：

- `AgentSwitcher`
- `ConnectionStatusBar`
- `RuntimeDiagnosticsDialog`
- `RuntimeInsightsPanel`
- 旧设计/绘画 starter card（独立于 Design 模式的入口）

## 架构设计约束

Kun 包按 ports & adapters 组织：

- `contracts/`：HTTP/SSE DTO 和 zod schema。
- `ports/`：ModelClient、ToolHost、ThreadStore、SessionStore、
  ApprovalGate、EventBus、WorkspaceInspector、Clock。
- `adapters/`：DeepSeek-compatible model client、local tool host、
  file/in-memory stores、workspace inspector。
- `loop/`：AgentLoop、InflightTracker、SteeringQueue、ContextCompactor。
- `cache/`：ImmutablePrefix、LRU、TTL-LRU。
- `server/`：Router、auth、SSE、routes。

GUI 侧不实现 agent 逻辑，只做 HTTP client、SSE subscription 和状态映射。
新增能力时优先加 Kun tool 或 HTTP endpoint，不新增 GUI 内第二个
agent。

## 验证清单

每次改这条线至少跑：

```bash
npm run typecheck
npm test
npm run build
```

手动冒烟：

1. 打开 Kun 桌面应用。
2. Code 新建会话，能创建 thread、发送消息、流式返回、审批/中断可用。
3. Design 打开画布，能创建或迭代设计稿、预览/导出原型，并把设计交给新的
   Code thread 实现。
4. Write 打开写作空间，inline completion 和选中文本助手能用同一个 API key。
5. 连接手机能保存设置、运行手动 task、把 thread id 写回 Kun mapping。
6. Settings -> Agents 只看得到 Kun，没有 provider switch、runtime
   diagnostics、历史 provider 配置块。
7. `GET /v1/usage?group_by=thread` 有历史 usage 时，GUI 首页/底部不显示
   “暂无用量”，而显示 token、回合、缓存命中等指标。
8. 线程搜索、归档视图、fork、resume session、request_user_input 回答/取消
   都能通过 Kun HTTP 路径完成。
