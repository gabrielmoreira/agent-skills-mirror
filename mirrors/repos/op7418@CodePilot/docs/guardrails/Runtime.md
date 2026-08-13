# Runtime Compatibility Filtering — 护栏

CodePilot 有两条 chat 运行路径：**Claude Code Runtime**（SDK 子进程）和 **CodePilot Runtime**（@ai-sdk/* 直连）。Provider / Model / Composer 三层过滤契约必须严格对齐，否则 picker 看到的、resolver 选中的、wire 上发出去的会出现三方不一致，长期看就是用户报"模型选了 A，实际请求 B"或者"切了 runtime 但 picker 还是老模型"。

## 1. 词汇表

| 名称 | 取值 | 来源 |
|---|---|---|
| `agent_runtime` setting | `'auto' \| 'native' \| 'claude-code-sdk'` | DB `settings` 表，用户在 Settings → CLI 设置 |
| Concrete runtime | `'native' \| 'claude-code-sdk'` | `resolveRuntime()` 输出（`runtime/registry.ts`） |
| `ChatRuntime` | `'claude_code' \| 'codepilot_runtime'` | `chat-runtime.ts` 把 concrete 映射到 chat-side 词汇 |
| `ChatRuntimeParam` | `ChatRuntime \| 'auto'` | API query / hook 参数；`'auto'` = server 端用 `getActiveChatRuntime()` 自己解析 |
| `ProviderRuntimeCompat` | `claude_code_ready` / `claude_code_verified` / `claude_code_experimental` / `codepilot_only` / `media_only` / `unknown` | `getProviderCompat()` (`runtime-compat.ts`) |
| `ModelRuntimeCompat` | `{ chat?, tool_capable?, thinking_capable?, claude_code_compatible?, codepilot_runtime_compatible?, media? }` | `getModelCompat()` (`runtime-compat.ts`) |

## 2. 三层过滤契约

### 2.1 Settings 全量 vs Composer runtime-filtered

| 入口 | 调用 | 看到什么 |
|---|---|---|
| Settings → Providers 全局默认模型选择器 | `fetch('/api/providers/models')`（**不传** `?runtime=`） | 完整 catalog，所有 provider 所有 enabled 模型 |
| Settings → Models 页 | 直接 fetch + 自己 filter，不通过 hook | 完整 catalog，按用户操作（runtime filter dropdown / 搜索 / enabled tab）筛 |
| Composer / chat picker | `useProviderModels(providerId, modelName)` 默认 `runtime: 'auto'` → `?runtime=auto` | 服务端按 active runtime 过滤后的 enabled 模型 |
| chat 主入口 send 路径 | `resolveProvider({ ..., runtime: getActiveChatRuntime() })`（`/api/chat/route.ts` + `bridge/conversation-engine.ts`） | server 端按 runtime gate 选 default model + availableModels |

**不变量**：Composer / chat send 路径**永远**带 active runtime；Settings 全局默认选择器**永远**不带（避免 user 看不到他想设为默认的 codepilot_only 模型）。这两条对调过任何一次都会出 bug。

### 2.2 Compat tier × runtime 必须命中表

| `ProviderRuntimeCompat` | runtime=`claude_code` 时该出现？ | runtime=`codepilot_runtime` 时该出现？ |
|---|---|---|
| `claude_code_ready` (Anthropic / Bedrock / Vertex) | ✅ 必须 | ✅ 必须（`@ai-sdk/anthropic` 也能直调） |
| `claude_code_verified` (GLM / Kimi / Volcengine 等已实测 Code Plan) | ✅ 必须 | ❌ 整组 drop（多数 sdkProxyOnly） |
| `claude_code_experimental` (anthropic-thirdparty wildcard) | ✅ 必须 | ❌ 整组 drop |
| `codepilot_only` (OpenRouter / OpenAI-compat / Google chat) | ❌ 整组 drop | ✅ 必须 |
| `media_only` | ❌ 整组 drop | ❌ 整组 drop（不进 chat picker） |
| `unknown` (custom URL 没匹配预设) | ✅ 必须（双向兼容，UI 标"需验证"） | ✅ 必须 |

**已知陷阱（已修，别走回头路）**：
- 之前 `getModelCompat` 的 `codepilot_only` 分支有 alias lift 让 `anthropic/claude-*` 标 `claude_code_compatible`，导致 OpenRouter 的 claude 模型在 `claude_code` runtime 下能被选中——但 OpenRouter 整组在 group-layer 已被 drop，user 选了又跑不通。Codex 2026-04-26 review 指出后已删（`runtime-compat.ts:128` 注释）。**不要再加回去**。要让 OpenRouter 的 claude 走 Claude Code，方案是单独配 `anthropic-thirdparty` preset 指向 OpenRouter 的 anthropic-compat endpoint。

### 2.3 API 失败 ≠ 空集合（不能静默伪造 env fallback）

`/api/providers/models?runtime=...` 三种返回，hook + chat-page init 必须分清：

| 来源 | hook 行为 (`useProviderModels`) | chat-page init 行为 |
|---|---|---|
| HTTP 200 + `groups: [...]` 非空 | `setProviderGroups(data.groups)`、`fetchState='loaded'` | 走 validation chain，应用 global default / saved provider |
| HTTP 200 + `groups: []` (runtime filter 后真空) | `setProviderGroups([])`、`fetchState='loaded'` → `noCompatibleProvider=true` | 清 `currentProviderId/Model` + `noCompatibleProvider=true` + 引导 UI |
| HTTP error / parse fail / network down | catch 分支合成 `[{ provider_id: 'env', models: DEFAULT_MODEL_OPTIONS }]`、`fetchState='failed'` | 走 localStorage best-effort fallback |

**不变量**：成功返回的空集合**绝对不能**触发"合成 env + sonnet/opus/haiku"逻辑——那等于把刚被 server 端 runtime gate 过滤掉的模型偷渡回来。仅 `catch` 分支可以走 env synthetic fallback。

### 2.4 同 Runtime 子 Agent 路由

| 层 | 契约 |
|---|---|
| 父主控 | 当前会话已选 Runtime / Provider / Model 不变；delegate 不允许偷换父会话路由 |
| CodePilot Runtime | managed `Agent` 使用全 CodePilot-compatible catalog 的精确 `provider_id + model`；child 工具装配与模型调用必须同时切到目标 Provider。省略两者才继承父路由 |
| Claude Code Runtime | 精确模型委派必须走 `codepilot_spawn_subagent`：route 来自全部 Claude Code picker 未置灰模型，handler exact 校验 Provider+Model 后启动独立 SDK subprocess；child 继承父 query 的 built-ins、MCP、permission profile 与 approval callback，并移除 Agent/Task。route 只证明 catalog-compatible，不证明账号 entitlement；SDK terminal 必须检查 `is_error` / `api_error_status` |
| Codex Runtime | CodePilot Provider 会话通过 builtin proxy bridge 新建显式目标 Provider+Model 的 child thread，继承父 sandbox / approval、Codex 原生工具与全部 MCP，并按 thread ID 隔离父子事件；CodePilot 不再按联网/写入/Shell 等类别建立第二套 capability gate。app-server 的 `web_search` 只在目标 SDK 有真实 hosted tool 时翻译。Codex Account 只归一化原生 `collabAgentToolCall` |
| 展示 | requested 与 effective 分离；Native 以执行结果 breadcrumb 证明 effective，其他 Runtime 拿不到就只显示 requested |

**不变量**：同 Runtime 不等于任意 model string，也不等于同 Provider。managed route 必须来自该 Runtime picker 未置灰/兼容集合并同时命中 `provider_id + model`，执行层的工具装配、凭据解析和模型调用必须全部使用目标 Provider；只传 `sonnet / haiku` 等重复 alias 不足以证明模型身份。不能按品牌误杀 Kimi / GLM / DeepSeek，也不能把不可达模型静默改成 Sonnet/inherit。Claude 原生 AgentDefinition 与 Codex 原生 spawn 即使接受 model，也不能被当作 CodePilot 跨 Provider 路由；Runtime 未返回 effective 事实时 UI 留空；一旦 Runtime 明确报告了不同模型，必须以 `ROUTE_MISMATCH` 终止当前 attempt，不能接受 fallback。catalog 命中不等于 entitlement 成功；任何结构化 provider error 都不能归为 completed。

DB Provider 与已认证的 managed virtual Provider 必须共用同一套 picker / Sub-agent catalog 事实源。`openai-oauth`、`xai-oauth` 这类不写入 `providers` 表的凭据入口，不能只在 `/api/providers/models` 手工追加：认证成功时它们必须进入三条 managed Sub-agent 候选集合，再统一由 Runtime 兼容矩阵决定是否保留；因此 CodePilot/Codex 能看到 Grok，而 Claude Code 是经 compat gate 排除 xAI，不是靠漏枚举碰巧排除。未认证或集成关闭时各入口同时消失。Codex proxy 的 compat/protocol 也必须从同一静态定义派生，不能维护第二份 metadata。`codex_account` 的模型来自 app-server 异步发现，继续走其原生边界，不混入这个 managed virtual catalog。

Claude managed subprocess 的调用方仍必须完整声明 `required_capabilities`，该字段只核对 Claude SDK 父 query 的真实工具 surface，不是固定只读开关。Codex managed child 不暴露这个字段：Codex app-server 是 native tools、MCP、sandbox 与 approval 的唯一能力事实源，CodePilot 只负责目标 Provider+Model 路由与 transport，不预判或裁剪工具类别。两条路径在真实工具缺失时都必须诚实失败，不能用训练知识或本地旧内容冒充实时检索。每个调用仍是 one-shot foreground attempt，不能 placeholder / stand-by / resume；同一用户任务的显式 retry 必须复用前次返回的 `logicalRunId`，不同任务不得复用。Runtime Adapter 不能只信调用方：复用 active/settling logical run 必须返回 `LOGICAL_RUN_STILL_RUNNING`，复用 completed logical run 必须返回 `LOGICAL_RUN_ALREADY_COMPLETED`，且两者都不得调用 Provider 或把拒绝记录成新的 attempt。

三 Runtime 的依赖编排不能由各自 SDK 猜测。一个 dependency graph 使用共同的 `workflow_id`，每个 child 使用唯一 `task_key`，边由 `depends_on` 声明；Adapter 先创建 durable queued run，再统一调用 `resolveSubagentDependencies()`。只有上游同 workflow task 已 durable completed 且存在结果时，CodePilot 才把结果作为带 provenance 的 data 注入实际 child prompt 并切换到 executing。SDK tool call 串行不等于结果自动传递；调用方必须先发 upstream，缺失上游只给并行 handler 5 秒创建宽限，不能让 dependent-first 在串行 Runtime 上长期阻塞。未声明依赖的 wait/stand-by prompt、失败依赖、重复 task key 与 self/indirect cycle 必须在 Provider 启动前 fail closed。

### 2.5 Codex 本机 Provider Proxy 边界

CodePilot Provider 会话把 Codex app-server 的 Responses endpoint 指向
`http://127.0.0.1:<port>/api/codex/proxy/v1`。这是**本机 transport**，不是上游 Provider：

- Electron → packaged Next 与 Next → Codex app-server 两道进程边界都必须幂等追加
  `NO_PROXY/no_proxy=127.0.0.1,localhost,::1`，并保留用户已有 bypass 条目。
- 外网 `HTTP_PROXY/HTTPS_PROXY/ALL_PROXY` 继续保留；禁止为修 loopback 而全局关闭代理。
- Windows child env 中 proxy key 必须规范化为单一 casing，避免 Node 只传某个重复键。
- 已解析的 `stream:true` managed proxy 请求发生 Provider / application error 时，必须用 HTTP 200
  SSE `response.failed` 承载 structured error；显式 non-stream 请求才保留 HTTP status + JSON。
  禁止把上游 Provider 502重新暴露成 loopback transport HTTP 502。
- 只有 transport 502 同时指向 loopback + `/api/codex/proxy/`，且不含 CodePilot structured
  error envelope 时，才能诊断为 `CODEX_LOOPBACK_PROXY_INTERCEPTED`；诊断必须保留原始
  Codex error，外部 Provider 错误不得冒充本机拦截。
- 用户自建 `~/.codex/proxy.mjs` 不属于 CodePilot 生命周期，禁止自动执行；本地自定义 endpoint
  未监听时只可给出连接诊断。
- bundled Codex 含 `respect_system_proxy` feature 不代表环境变量 bypass 一定覆盖 Windows
  system proxy resolver；相关改动必须补“仅 system proxy、无 env proxy”的 packaged smoke，
  不能用 source test 或 macOS build 代替。

### 2.6 Codex 会话存储隔离

- CodePilot 的 `codex app-server` 必须同时把 `CODEX_HOME` 与
  `CODEX_SQLITE_HOME` 指向 `<CLAUDE_GUI_DATA_DIR>/codex-home`，不能再使用官方
  Codex 客户端默认的 `~/.codex` 状态根。否则 CodePilot 创建的 thread 会进入
  Codex Desktop 的任务列表，两个客户端也会竞争同一份 rollout / SQLite 索引。
- 隔离目录可以镜像用户所有的 Harness 输入（账号引导、`config.toml` 与 profile、
  Skills、Plugins、rules、themes、memories），但禁止镜像 runtime 所有的
  `sessions`、`archived_sessions`、SQLite、日志与缓存。`config.toml` 等 Harness
  输入优先使用 live symlink / junction（Windows 文件可降级 hardlink）；CodePilot
  对这些 live entry 的写入有意回到用户的官方 Codex Harness，因此 project trust
  等配置可能同时出现在官方客户端。若上游以 atomic rename 替换文件而断开链接，
  下次启动必须识别为 snapshot 并告警；禁止自动覆盖或伪装仍在实时同步。
- 镜像配置文件时必须保留 Codex 的相对路径解析语义：`model_catalog_json`、指令文件
  以及 `agents.*.config_file` 等声明的被动文件依赖，必须在隔离目录的相同相对位置
  继续镜像，并在每次启动补齐先前缺失的 entry。只处理同时位于源 Codex home 与
  隔离 home 内的相对文件；绝对路径继续由 Codex 直接读取，`..` 越界路径不得复制。
  该规则不能扩大成复制整个 `~/.codex`，runtime 状态仍受上一条禁止项约束。
- 首次初始化只复制 `session_meta.originator === 'codex_codepilot'` 的旧 rollout；
  禁止把用户的全部 Codex 历史导入 CodePilot。rollout 必须复制而非链接，保证后续
  CodePilot turn 不会继续改写官方客户端的历史文件。
- 凭据 entry 只在首次初始化建立一次；初始化模式必须写进 marker，每次启动还要按
  当前 inode / realpath 重新分类并在日志披露：
  `symlink`（macOS/Linux 首选，实时共享）、`hardlink`（Windows 同卷降级，共享
  inode）或 `copy`（跨卷/受限环境降级，从建立时起为 CodePilot 独立凭据）。
  `copy` / `target_only` 必须明确告警“可能需要分别登录”；不得把它们描述为共享。
  symlink/hardlink 遇到 atomic rename 后也可能转为独立文件，不能继续沿用 marker 中
  的旧分类。用户在 CodePilot 内退出登录只删除隔离目录 entry，不能
  删除官方凭据；marker 存在后重启不得再次从官方客户端静默恢复。
- live mirror 不可用时，文件/目录 copy 只是 snapshot。启动日志必须列出降级 entry；
  因 CodePilot 与官方客户端都可能写入，首版不做破坏性的自动覆盖/伪合并，由用户
  重新登录或手动同步 Harness 内容。
- 旧 rollout 采用 copy-not-move；因此升级前已经显示在 Codex Desktop 的历史条目
  仍会保留，但 CodePilot 后续只续写隔离副本。清理官方历史必须是独立的用户确认
  操作，不能藏在迁移里。
- 后续新增的 app-server spawn 路径或后台 worker 必须复用
  `prepareCodePilotCodexHome()`；只设置两个 home 变量中的一个属于契约违规。

## 3. 关键文件 + 不变量

| 模块 | 文件 | 不变量 |
|---|---|---|
| ChatRuntime 词汇 | `src/lib/chat-runtime.ts` | 必须 import 自 `'./runtime'`（barrel）而非 `'./runtime/registry'`，否则 `registerRuntime()` 副作用不触发 → `resolveRuntime()` 抛 "No agent runtime registered" |
| Provider compat tier | `src/lib/runtime-compat.ts` `getProviderCompat()` | preset.protocol='anthropic' 必须按 `meta.claudeCodeVerified` 拆 verified vs experimental；`codepilot_only` 分支**不能**有 claude alias lift |
| Model compat flags | `src/lib/runtime-compat.ts` `getModelCompat()` | `claude_code_ready` 双向兼容（claude_code + codepilot_runtime）；`verified` / `experimental` 仅 `claude_code_compatible`；`codepilot_only` 仅 `codepilot_runtime_compatible` |
| Managed virtual catalog | `src/lib/managed-virtual-provider-models.ts` | 已认证的非 DB Provider 是 picker、resolver 与 managed Sub-agent route 的共同事实源；未认证/disabled fail closed；不纳入异步发现的 `codex_account` |
| Server filter | `src/app/api/providers/models/route.ts` | 仅当传 `?runtime=` 才过滤；过滤后空 group **必须** drop（`.filter(g => g.models.length > 0)`），否则 hook 仍会 cross-wire |
| Claude SDK model cache | `src/app/api/providers/models/route.ts` `mergeEnvCatalogWithSdkModels()` | `supportedModels()` 只补充 runtime convenience entries，不能整表替换 `ENV_CLAUDE_CODE_MODELS`、删除显式 canonical route，或用移动 alias 描述覆盖固定版本标签/upstream |
| Hook contract | `src/hooks/useProviderModels.ts` | 暴露 `fetchState / resolvedProviderId / resolvedModel / providerWasFilteredOut / noCompatibleProvider` 五字段；区分 `providerId === undefined`（fallback chain）vs `providerId === ''`（env 历史会话）vs 显式值 |
| Codex model warm-up | `src/lib/codex/model-catalog-warmup.ts` + `src/hooks/useProviderModels.ts` | 全量目录继续只读 Codex cache；chat mount 以独立 bounded endpoint 非阻塞预热，成功后只通知模型 hook refetch，并在 renderer 内 memo 成功避免会话切换 churn；Codex login start/complete/logout 必须在 Settings 侧显式失效 memo（此时 chat hook 通常未挂载）。禁止恢复全量目录内同步 spawn，也禁止依赖进入 Settings 才预热 |
| Codex model discovery containment | `bounded-ndjson-reader.ts` + `app-server-client.ts` + `models.ts` | stdout frame 按 UTF-8 bytes 在 copy/concat 前执行 32 MiB hard cap；`model/list` 调用方 deadline 同步 abort client pending；同 generation 单航班、失败 cooldown，显式 retry 才 bypass |
| Codex wedged instance recovery | `app-server-manager.ts` | spawn promise 去重保持不变；连续内部 refresh timeout/`model/list` failure 只标记当前 generation unhealthy，确认无 active turn 时才 dispose/rebuild，无法证明 idle 时不热杀 |
| Main-owned recovery safe mode | Main env + model routes + warmup/hook/ChatView | server 端强制 cache-only 且 `getCodexAppServer()` fail closed；scheduler 不启动；Renderer 显示暂停并 gate Codex Runtime，不能把空 catalog 伪装成“账号无模型”或只清客户端状态假装恢复 |
| Composer send | `src/components/chat/ChatView.tsx` `doStartStream` / `sendMessage` | 三道 gate：`fetchState === 'idle'` / `noCompatibleProvider` / `loaded && (!resolvedProviderId \|\| !resolvedModel)`；wire 用 resolved pair 而非 raw |
| Composer disabled | `src/components/chat/ChatView.tsx` `MessageInput.disabled` | `noCompatibleProvider \|\| providerFetchState === 'idle'` —— idle 也禁用，避免 send 按钮看似可用但底层吞 |
| New session init | `src/app/chat/page.tsx` | 两处 init handler 必须用 `?runtime=auto`；空集合 → `setNoCompatibleProvider(true)`，不走 localStorage fallback |
| Auto-trigger | `src/hooks/useAssistantTrigger.ts` | welcome / heartbeat 必须吃 resolved pair + 在 `fetchState !== 'loaded' \|\| noCompatibleProvider` 时 return |
| Chat API resolver | `src/app/api/chat/route.ts` 第 263 行 | `resolveProvider({ runtime: getActiveChatRuntime() })` —— 别忘了传 |
| Bridge engine | `src/lib/bridge/conversation-engine.ts` | 同上 |
| Codex child process env | `src/lib/process-proxy-env.ts`, `src/lib/codex/app-server-manager.ts` | 保留外网 proxy、loopback 直连、Windows key 单一化 |
| Codex proxy HTTP/SSE contract | `src/lib/codex/proxy/http-response.ts`, `src/app/api/codex/proxy/v1/responses/route.ts` | streaming structured error 走 HTTP 200 `response.failed`；non-stream 保留 status + JSON |
| Codex network diagnosis | `src/lib/codex/error-diagnostics.ts`, `src/lib/codex/event-mapper.ts` | 只识别 CodePilot loopback transport 502，保留原文，不误判 managed upstream envelope |
| Runtime-specific provider transport | `src/lib/provider-catalog.ts` wire capabilities → `provider-resolver.ts:toAiSdkConfig()` → `ai-provider.ts` | 只在 preset identity + exact model + runtime 都命中时换协议；不得用 hostname 特判；unsupported 回原协议 |
| Anthropic-compatible effort | `agent-loop-anthropic-wire.ts` + `claude-code-compat/request-builder.ts` | 未验证第三方继续省略 effort；verified model×tier 才生成 `output_config.effort` |
| Codex provider Responses effort | `codex/proxy/unified-adapter.ts:buildProviderOptions()` | preset-verified third-party Responses 才可 `forceReasoning`；档位按 transport allowlist，未知档位省略 |

## 4. 加 / 改新功能时必须检查

- 新增 provider preset：在 `provider-catalog.ts` 加 `meta.claudeCodeVerified: true` 当且仅当**实测**端到端跑通 tool calling / thinking / 模型别名。否则保持 `experimental`
- 新增 runtime path（如未来加 OpenAI Responses / Codex / Hermes runtime）：
  - 在 `runtime/index.ts` 注册
  - 在 `chat-runtime.ts` `getActiveChatRuntime()` 加 mapping
  - 在 `runtime-compat.ts` 加新 ProviderRuntimeCompat tier + getModelCompat 分支
  - 更新本文 §2.2 命中表
- 给既有 provider 增加 runtime 专用 transport：
  - 在 preset `wireCapabilities` 声明 endpoint + exact model，不在 resolver 写品牌/hostname if
  - 同时验证模型 UI capability、transport effort allowlist、默认值、unsupported fallback
  - 补同名聚合渠道负例，防止第一方能力外溢
  - 用真实凭据至少跑一条 production factory 请求；只测 SDK mock 不得标 Smoke passed
- 新增 `useProviderModels` consumer：
  - 默认走 `runtime: 'auto'`（chat picker 行为）
  - 想看全集才显式传 `null`，并在代码里写注释说明为什么需要全集
  - chat 首次进入必须能独立发现 Codex Account 模型；不能把 Settings 页面 mount 当成隐式初始化步骤
- 新增 chat 入口（除现有 chat-route / bridge 外）：
  - 调 `resolveProvider()` 时**必须**传 `runtime: getActiveChatRuntime()`
  - send 路径前必须 gate `noCompatibleProvider` + `fetchState`
- 改 Codex model discovery / transport：覆盖 frame chunk/CRLF/multibyte/exact-cap/oversize/no-newline、RPC deadline、10 caller single-flight、cooldown/force 与 unhealthy-idle recycle；日志 fixture 中不得出现 frame/prompt/path/token 内容。
- 新增任何 Codex app-server 直达入口时必须复用 `getCodexAppServer()` 的 recovery-safe-mode gate，不得自行 spawn 绕过 Main owner。
- 新增 sub-agent adapter：必须定义 model allowlist / alias canonicalization / effective provenance，并消费共同 workflow/task/dependency compiler；未证明的能力 fail closed，不得实现第四套 queued/依赖等待语义

## 5. 常见坑

1. **直接 import `./runtime/registry` 而非 `./runtime` barrel** → `resolveRuntime()` 抛 "No agent runtime registered"。但 `claude-client.ts` 是个例外（与 sdk-runtime 循环依赖），它故意只 import registry，靠 caller 触发 barrel
2. **把 `providerId === ''` 当 falsy** → 历史 env-mode session（`provider_id=''`）被 localStorage / global default 抢走。区分 `=== undefined`（caller 没给）vs `=== ''`（env 显式选）
3. **Hook fetchState 初始 `'loaded'`** → 挂载第一帧 picker 误判 `noCompatibleProvider=true`，让 send 被吞。必须 `'idle'` 起步
4. **`fetchAll` 重新拉时不重置 `fetchState`** → `provider-changed` 事件 refetch 期间旧 groups 仍生效，runtime gate 短暂打开。每次 fetchAll 头部 `setFetchState('idle')`
5. **没 abort 旧 fetch** → 慢的旧请求晚到覆盖新请求结果。`useRef<AbortController>` + 每次 fetchAll 头部 `controller.abort()`，`.then` / `.catch` 检查 `signal.aborted`
6. **catch 合成 env synthetic 后下游 derivation 仍按"groups 空 = noCompatibleProvider"判** → 矛盾。`noCompatibleProvider = fetchState === 'loaded' && providerGroups.length === 0`，failed 状态里 groups.length=1 不算 noCompatibleProvider
7. **MessageInput auto-correct fire `onProviderModelChange(currentProviderIdValue, fallback)` 时，`currentProviderIdValue` 是 hook 内部 fallback group 的 id 而非 prop providerId** → 写回 session 的是 fallback provider，正确。但 Composer 顶层那次 `useProviderModels` 必须返回**同步过的** resolved pair，不能让 ChatView 的 `currentProviderId` state 落后于 hook 的 resolved 信号 → ChatView 用 useEffect 监听 `providerWasFilteredOut` + PATCH session 同步
8. **父模型在一个 turn 内同时生成 A/B tool input，SDK 随后按 A→B 串行执行** → B 的 prompt 仍在 A 结果产生前冻结，不能据此宣称 B 获得 A 输出。依赖必须走 `workflow_id/task_key/depends_on` 与 app-side durable handoff。
9. **AI SDK 不认识第三方 Responses 模型就静默丢 reasoning** → 对 preset-verified transport 显式 `forceReasoning`，并用真实 outbound body 测试；不能只断言 providerOptions 内存对象。
10. **把 OpenAI Responses 附加字段原样发给兼容端点** → 供应商只承诺的子集才保留。DeepSeek 当前不声明 reasoning summary，fetch 边界必须剥离 SDK 自动生成的 `reasoning.summary`。
11. **只给 HTTP warmup 加 2.5s timeout** → client pending 仍会活到内部 30s timer。调用方 deadline 必须向下 abort 对应 JSON-RPC id，late response 只能被丢弃。
12. **把一次 refresh warning 当成僵死进程热杀** → 可能中断 active turn/approval。必须按 generation+窗口累计并仅在 idle recycle。

## 6. 测试覆盖

| 测试文件 | 覆盖 |
|---|---|
| `src/__tests__/unit/chat-runtime.test.ts` | `getActiveChatRuntime()` 不抛 + 各 setting 下返回值 + param helpers |
| `src/__tests__/unit/provider-resolver.test.ts` | `getProviderCompat` 5 态 + `getModelCompat` alias-lift 删除回归 + runtime gate skip + hidden+runtime stack + env session env normalize |
| `src/__tests__/unit/env-models-single-source.test.ts` | canonical env 目录三方单一出口；SDK 五行 convenience cache 注入后 `opus-5` 仍保留、动态入口只追加、固定 alias 不被改名 |
| `src/__tests__/unit/runtime-selection.test.ts` | inlined `predictNativeRuntime` (registry side effects 隔离) |
| `src/__tests__/unit/sdk-availability.test.ts` | sdk-runtime 直接 import（被 barrel registerRuntime 调用前先 init），测 isAvailable 各路径 |
| `src/__tests__/unit/subagent-orchestration.test.ts` | Provider+Model route、三 Runtime 工具/权限继承、hosted search、requested/effective view |
| `src/__tests__/unit/subagent-virtual-provider-routes.test.ts` | OAuth virtual Provider 的 picker/Sub-agent route 同源；xAI/OpenAI 正例、未认证/disabled/Claude Code 负例 |
| `src/__tests__/unit/process-proxy-env.test.ts` | Electron/Codex 两道 child env、显式/system proxy 优先级、Windows casing、loopback bypass |
| `src/__tests__/unit/codex-home-isolation.test.ts` | Codex runtime state 隔离、凭据/Harness 镜像模式、相对 model catalog/指令/agent 配置依赖递归补齐与越界拒绝 |
| `src/__tests__/unit/codex-proxy-foundation.test.ts` | streaming Provider error 的 HTTP 200 `response.failed` 与 non-stream HTTP status 合同 |
| `src/__tests__/unit/codex-event-mapper.test.ts` | loopback transport 502 专用诊断、原文保留与 managed upstream envelope 反例 |
| `src/__tests__/unit/opus-5-model.test.ts` | Opus 5 显式目录与旧 alias pin、1M context、adaptive/sampling/effort、disabled-thinking 上限、Auto compatibility-default provenance、本地化调整提示和 Claude managed Sub-agent route |
| `src/__tests__/unit/agent-loop-anthropic-wire.test.ts` | Anthropic 官方 model×effort-tier wire allowlist；Auto 不冒充显式 High；第三方代理保留原始 requested tier；Sonnet 4.6 max/xhigh 正反例 |
| `src/__tests__/unit/codex-proxy-translators.test.ts` | Codex proxy 对 Anthropic resolved upstream model 使用共享 sanitizer；adaptive 家族禁止 manual budget thinking，支持档位 xhigh 保真、Sonnet 4.6 非法 xhigh 省略 |
| `src/__tests__/unit/deepseek-v4-flash-adaptation.test.ts` | Codex Runtime exact-model Responses dispatch、production factory outbound body、DeepSeek max/xhigh 映射、Anthropic output_config 与 aggregator fail-closed |
| `codex-bounded-ndjson-reader.test.ts` + `codex-app-server-client.test.ts` + `codex-models-decoupling.test.ts` | frame byte cap、deadline pending cleanup、model/list single-flight/cooldown/safe-mode cache-only |
| `codex-binary-discovery.test.ts` | internal refresh-timeout signature、health window threshold 与 app-server spawn compatibility |

加新 runtime gate 行为的功能时，至少加一组 unit test 覆盖三场景：(1) loaded + 兼容 → 通过；(2) loaded + 不兼容 → gate 拦；(3) idle → gate 拦。

## 7. 设计决策日志

- **2026-04-26** 拆 verified vs experimental，理由：所有 anthropic-thirdparty 被一刀切橙色 warning，主流 Code Plan provider 视觉看像 error。verified 用 info 蓝 + "Claude Code 兼容"，experimental 仍橙 + "Claude Code 实验"
- **2026-04-26** 删 `getModelCompat` codepilot_only 的 claude alias lift。理由：与 provider-layer "不进入 Claude Code 流程" 语义打架，且 group-layer 已 drop 整组，alias 留着是死代码 + 可能误导
- **2026-04-26** `claude_code_ready` 双向兼容（既 `claude_code_compatible` 又 `codepilot_runtime_compatible`）。理由：`@ai-sdk/anthropic` 能直调 Anthropic / Bedrock / Vertex，native runtime 用户配 Anthropic 不该看到 0 模型
- **2026-04-26** API 空集合 server-side drop（不返回 `models: []`）。理由：hook 兜底逻辑会把空 group fallback 到 `DEFAULT_MODEL_OPTIONS`，相当于偷渡 sonnet/opus/haiku 进 picker
- **2026-04-26** Hook 加 `fetchState`、`AbortController`、`requestedProviderId vs preferredProviderId` 拆分，全部因 Codex review 指出竞态 / 语义错位
- **2026-08-03** chat 非阻塞预热 Codex model catalog。全量目录保留 cache-only 防卡顿；显式 discovery 从 Settings 副作用迁到 chat mount，成功后用窄事件刷新模型 hook
- **2026-08-11** Codex model discovery 增加 transport byte cap、RPC 同 deadline abort、server-side single-flight/cooldown 与 unhealthy-idle recycle；utility crash 后由 Main safe mode 禁止 Codex/scheduler 自动重触发，Renderer 只读展示并 gate 发送。
- **2026-04-26** `chat-runtime.ts` 必须 import barrel（`./runtime`）。理由：runtime/index.ts 的 `registerRuntime` 副作用是注册唯一入口，跳过 → empty registry → 500
- **2026-07-22—23** 子 Agent 首版保持 same-runtime，但用户复测纠正了“same-runtime = same-provider”的错误假设。CodePilot Native、Claude managed subprocess、Codex CodePilot-Provider proxy child 都必须使用 Runtime-compatible exact Provider+Model route；合法集合与 picker 未置灰状态同源。AgentDefinition full model string 与 Codex 原生 spawn 都不能承担 CodePilot 跨 Provider 路由，因为它们不能可靠切换父 endpoint/provider config。Codex Account 只展示原生 collab，不冒充跨 CodePilot Provider 成功。
- **2026-07-23** 用户真实 smoke 发现 SDK `success` envelope 可携带 `is_error=true` 的 403，且父 Agent 把 one-shot subprocess 当作待命/续跑 worker，造成 3 个逻辑 Agent 产生 6 次调用。终态收口到结构化 SDK 字段；managed tool 加 one-shot 与 capability 声明，unsupported 能力 fail closed。
- **2026-07-23** Codex 真实会话 `1d154cca69c53c23091b43d8f55100a6` 暴露两层错误：proxy 内已执行的 `codepilot_spawn_subagent` 被再次回传给 app-server，得到 `unsupported call`；dynamic MCP bridge 又只允许 Memory namespace。修复后所有 bridge-executed tool 都在 Codex-bound stream 中抑制，所有 namespaced MCP 调用都交回 Codex MCP manager；Codex child 不再要求 `required_capabilities` 或维护第二套工具 allowlist，只禁止递归 spawn。
- **2026-07-24** 会话 `3f0085c5fc664deca85005d70b1abfca` 证明 one-shot prompt 指导不能完成结果 handoff：DeepSeek tool input 在 Qwen 输出前已冻结，串行执行后仍只能自行重搜。三 Runtime 现统一使用 workflow/task/dependency durable compiler；Adapter 不再各自解释“等待上游”的自然语言。
- **2026-07-27** Windows + Clash 实机证明 Codex 的 CodePilot loopback Responses 请求会继承 proxy env 并在缺少 `NO_PROXY` 时被截获为 502。两道 child-process 边界统一使用共享 proxy-safe builder；保留外网代理，不用 Chromium direct mode 掩盖 Rust 子进程问题。
- **2026-07-27** Claude 独立审查证明“loopback URL + HTTP 502”不足以识别代理截获，因为 CodePilot managed proxy 的上游失败也曾返回同一 HTTP 签名。parsed streaming 请求现统一用 HTTP 200 SSE `response.failed` 表达 Provider 错误；专用 loopback 诊断只处理 transport 502、排除 structured envelope 并保留原文。bundled Codex 的 `respect_system_proxy` 语义仍以 Windows system-proxy-only smoke 为准。
- **2026-07-27** v0.60.0 用户在另一台电脑确认 Grok 4.5 主会话可用，但 managed Sub-agent 声称没有该 route。根因不是 entitlement，而是 picker 手工加入 `xai-oauth`，Sub-agent route 却只枚举 env + `providers` 表。现以 `managed-virtual-provider-models.ts` 统一 OAuth provider/model/auth 事实，CodePilot/Codex 同时获得已认证 Grok/OpenAI OAuth route；Claude Code 的协议 gate 不放宽。
- **2026-07-27** Claude review 通过变异测试证明首版 Claude negative 是空断言，且 Codex proxy 仍复制 compat。现让 Claude 候选也消费共享 catalog 后再按 compat 过滤；测试直接锁定 xAI=`codepilot_only/xai`、OpenAI OAuth=`codepilot_only/openai-compatible`。Proxy registry 从共享定义生成，metadata parity 同时断言 id/compat/protocol，不再只比 id。
- **2026-07-28** Opus 5 以显式 `opus-5 → claude-opus-5` 加入 first-party/env 单一目录，并自然进入 Claude managed Sub-agent route；既有 `opus → claude-opus-4-7` pin 不变，避免旧会话静默迁移。模型合同为 1M context + adaptive thinking + low/medium/high/xhigh/max effort；thinking disabled × xhigh/max 必须受控降到 high 并通过本地化结构化状态告知，Auto 也必须显式发 high，不能依赖 CLI 可变默认值。Codex proxy 的 Anthropic 请求必须用 resolved upstream model 经过同一 sanitizer/wire builder；禁止再把 adaptive 家族的 effort 翻译成 manual `budgetTokens`。CodePilot 生产路径使用系统 Claude binary，Opus 5 要求 Claude Code `2.1.219+`；Agent SDK 大版本升级和未经验证的 OpenRouter/Bedrock/Vertex slug 不与本次目录修复捆绑。
- **2026-08-02** DeepSeek V4 Flash 在 Codex Runtime 使用第一方原生 Responses；同 credential 在 CodePilot Runtime 保持 Anthropic-compatible，Claude Code 保持官方 `/anthropic` env 路径。transport 由 preset 声明而非 hostname 分支；V4 Pro 暂不切 Responses。AI SDK 对未知模型的 reasoning heuristic 由 verified transport 的 `forceReasoning` 覆盖，DeepSeek 未支持的 summary 被移除。真实 API 已分别跑通 Responses High 与 Anthropic thinking+High；聚合渠道 effort 继续 fail closed。
