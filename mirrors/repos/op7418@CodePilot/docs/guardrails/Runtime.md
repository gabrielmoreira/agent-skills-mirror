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

## 3. 关键文件 + 不变量

| 模块 | 文件 | 不变量 |
|---|---|---|
| ChatRuntime 词汇 | `src/lib/chat-runtime.ts` | 必须 import 自 `'./runtime'`（barrel）而非 `'./runtime/registry'`，否则 `registerRuntime()` 副作用不触发 → `resolveRuntime()` 抛 "No agent runtime registered" |
| Provider compat tier | `src/lib/runtime-compat.ts` `getProviderCompat()` | preset.protocol='anthropic' 必须按 `meta.claudeCodeVerified` 拆 verified vs experimental；`codepilot_only` 分支**不能**有 claude alias lift |
| Model compat flags | `src/lib/runtime-compat.ts` `getModelCompat()` | `claude_code_ready` 双向兼容（claude_code + codepilot_runtime）；`verified` / `experimental` 仅 `claude_code_compatible`；`codepilot_only` 仅 `codepilot_runtime_compatible` |
| Server filter | `src/app/api/providers/models/route.ts` | 仅当传 `?runtime=` 才过滤；过滤后空 group **必须** drop（`.filter(g => g.models.length > 0)`），否则 hook 仍会 cross-wire |
| Hook contract | `src/hooks/useProviderModels.ts` | 暴露 `fetchState / resolvedProviderId / resolvedModel / providerWasFilteredOut / noCompatibleProvider` 五字段；区分 `providerId === undefined`（fallback chain）vs `providerId === ''`（env 历史会话）vs 显式值 |
| Composer send | `src/components/chat/ChatView.tsx` `doStartStream` / `sendMessage` | 三道 gate：`fetchState === 'idle'` / `noCompatibleProvider` / `loaded && (!resolvedProviderId \|\| !resolvedModel)`；wire 用 resolved pair 而非 raw |
| Composer disabled | `src/components/chat/ChatView.tsx` `MessageInput.disabled` | `noCompatibleProvider \|\| providerFetchState === 'idle'` —— idle 也禁用，避免 send 按钮看似可用但底层吞 |
| New session init | `src/app/chat/page.tsx` | 两处 init handler 必须用 `?runtime=auto`；空集合 → `setNoCompatibleProvider(true)`，不走 localStorage fallback |
| Auto-trigger | `src/hooks/useAssistantTrigger.ts` | welcome / heartbeat 必须吃 resolved pair + 在 `fetchState !== 'loaded' \|\| noCompatibleProvider` 时 return |
| Chat API resolver | `src/app/api/chat/route.ts` 第 263 行 | `resolveProvider({ runtime: getActiveChatRuntime() })` —— 别忘了传 |
| Bridge engine | `src/lib/bridge/conversation-engine.ts` | 同上 |

## 4. 加 / 改新功能时必须检查

- 新增 provider preset：在 `provider-catalog.ts` 加 `meta.claudeCodeVerified: true` 当且仅当**实测**端到端跑通 tool calling / thinking / 模型别名。否则保持 `experimental`
- 新增 runtime path（如未来加 OpenAI Responses / Codex / Hermes runtime）：
  - 在 `runtime/index.ts` 注册
  - 在 `chat-runtime.ts` `getActiveChatRuntime()` 加 mapping
  - 在 `runtime-compat.ts` 加新 ProviderRuntimeCompat tier + getModelCompat 分支
  - 更新本文 §2.2 命中表
- 新增 `useProviderModels` consumer：
  - 默认走 `runtime: 'auto'`（chat picker 行为）
  - 想看全集才显式传 `null`，并在代码里写注释说明为什么需要全集
- 新增 chat 入口（除现有 chat-route / bridge 外）：
  - 调 `resolveProvider()` 时**必须**传 `runtime: getActiveChatRuntime()`
  - send 路径前必须 gate `noCompatibleProvider` + `fetchState`

## 5. 常见坑

1. **直接 import `./runtime/registry` 而非 `./runtime` barrel** → `resolveRuntime()` 抛 "No agent runtime registered"。但 `claude-client.ts` 是个例外（与 sdk-runtime 循环依赖），它故意只 import registry，靠 caller 触发 barrel
2. **把 `providerId === ''` 当 falsy** → 历史 env-mode session（`provider_id=''`）被 localStorage / global default 抢走。区分 `=== undefined`（caller 没给）vs `=== ''`（env 显式选）
3. **Hook fetchState 初始 `'loaded'`** → 挂载第一帧 picker 误判 `noCompatibleProvider=true`，让 send 被吞。必须 `'idle'` 起步
4. **`fetchAll` 重新拉时不重置 `fetchState`** → `provider-changed` 事件 refetch 期间旧 groups 仍生效，runtime gate 短暂打开。每次 fetchAll 头部 `setFetchState('idle')`
5. **没 abort 旧 fetch** → 慢的旧请求晚到覆盖新请求结果。`useRef<AbortController>` + 每次 fetchAll 头部 `controller.abort()`，`.then` / `.catch` 检查 `signal.aborted`
6. **catch 合成 env synthetic 后下游 derivation 仍按"groups 空 = noCompatibleProvider"判** → 矛盾。`noCompatibleProvider = fetchState === 'loaded' && providerGroups.length === 0`，failed 状态里 groups.length=1 不算 noCompatibleProvider
7. **MessageInput auto-correct fire `onProviderModelChange(currentProviderIdValue, fallback)` 时，`currentProviderIdValue` 是 hook 内部 fallback group 的 id 而非 prop providerId** → 写回 session 的是 fallback provider，正确。但 Composer 顶层那次 `useProviderModels` 必须返回**同步过的** resolved pair，不能让 ChatView 的 `currentProviderId` state 落后于 hook 的 resolved 信号 → ChatView 用 useEffect 监听 `providerWasFilteredOut` + PATCH session 同步

## 6. 测试覆盖

| 测试文件 | 覆盖 |
|---|---|
| `src/__tests__/unit/chat-runtime.test.ts` | `getActiveChatRuntime()` 不抛 + 各 setting 下返回值 + param helpers |
| `src/__tests__/unit/provider-resolver.test.ts` | `getProviderCompat` 5 态 + `getModelCompat` alias-lift 删除回归 + runtime gate skip + hidden+runtime stack + env session env normalize |
| `src/__tests__/unit/runtime-selection.test.ts` | inlined `predictNativeRuntime` (registry side effects 隔离) |
| `src/__tests__/unit/sdk-availability.test.ts` | sdk-runtime 直接 import（被 barrel registerRuntime 调用前先 init），测 isAvailable 各路径 |

加新 runtime gate 行为的功能时，至少加一组 unit test 覆盖三场景：(1) loaded + 兼容 → 通过；(2) loaded + 不兼容 → gate 拦；(3) idle → gate 拦。

## 7. 设计决策日志

- **2026-04-26** 拆 verified vs experimental，理由：所有 anthropic-thirdparty 被一刀切橙色 warning，主流 Code Plan provider 视觉看像 error。verified 用 info 蓝 + "Claude Code 兼容"，experimental 仍橙 + "Claude Code 实验"
- **2026-04-26** 删 `getModelCompat` codepilot_only 的 claude alias lift。理由：与 provider-layer "不进入 Claude Code 流程" 语义打架，且 group-layer 已 drop 整组，alias 留着是死代码 + 可能误导
- **2026-04-26** `claude_code_ready` 双向兼容（既 `claude_code_compatible` 又 `codepilot_runtime_compatible`）。理由：`@ai-sdk/anthropic` 能直调 Anthropic / Bedrock / Vertex，native runtime 用户配 Anthropic 不该看到 0 模型
- **2026-04-26** API 空集合 server-side drop（不返回 `models: []`）。理由：hook 兜底逻辑会把空 group fallback 到 `DEFAULT_MODEL_OPTIONS`，相当于偷渡 sonnet/opus/haiku 进 picker
- **2026-04-26** Hook 加 `fetchState`、`AbortController`、`requestedProviderId vs preferredProviderId` 拆分，全部因 Codex review 指出竞态 / 语义错位
- **2026-04-26** `chat-runtime.ts` 必须 import barrel（`./runtime`）。理由：runtime/index.ts 的 `registerRuntime` 副作用是注册唯一入口，跳过 → empty registry → 500
