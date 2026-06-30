# Composer Model Selection — 护栏

聊天输入框（MessageInput）背后的模型选择是 runtime 过滤、隐藏管理、session 历史三股力量的汇合点。本文档锁住 ChatView / MessageInput / useProviderModels 三角的契约。Codex 在 2026-04-26 的几轮 review 里指出过这块的多个 cross-wire（旧 provider 被替换但仍发送、idle 期发送绕过 gate、env 历史被 localStorage 抢），已修但容易回归。

## 1. 词汇表

| 名称 | 定义 | 来源 |
|---|---|---|
| Composer | chat 页底部输入区，含 textarea + 模型/权限 selector + 发送按钮 | `src/components/chat/MessageInput.tsx` |
| Picker | Composer 顶部模型选择下拉 | `MessageInput.tsx` 内部 |
| ChatView | 已有会话页（chat/[id]）渲染器，包含 Composer + 消息列表 + send 路径 | `src/components/chat/ChatView.tsx` |
| New Chat Page | 新会话入口 (chat/) — 没有 ChatView，自己管 currentModel/currentProviderId | `src/app/chat/page.tsx` |
| Resolved pair | hook 返回的 `(resolvedProviderId, resolvedModel)`，runtime-filtered 后实际生效的发送对 | `useProviderModels.ts` |
| Auto-correct | MessageInput 在 modelName 不在当前 group modelOptions 里时，自动 fire `onProviderModelChange(currentProviderIdValue, modelOptions[0].value)` | `MessageInput.tsx:181-187` |

## 2. Hook 契约（`useProviderModels`）

### 2.1 默认 runtime='auto'

```ts
useProviderModels(providerId?, modelName?, runtime: ChatRuntimeParam | null = 'auto')
```

- `'auto'`（默认）→ fetch `/api/providers/models?runtime=auto`，server 端按 active runtime 过滤
- `'claude_code'` / `'codepilot_runtime'`（显式）→ caller 指定具体 runtime
- `null`（显式 opt-out）→ fetch 不带 query，看完整 catalog

不变量：Composer / chat picker 永远不传 `null`；Settings 全局默认 selector 永远传 `null`。详见 `Runtime.md` §2.1。

### 2.2 返回值契约 — 五个关键字段

```ts
{
  providerGroups,           // 原始 group 列表
  currentProviderIdValue,   // alias for resolvedProviderId（兼容历史 caller）
  modelOptions,             // 当前 group 的 models
  currentModelOption,       // modelOptions 内匹配 modelName 的那个，否则 [0]
  globalDefaultModel,       // 仅 Settings selector 用
  globalDefaultProvider,    // 同上
  noCompatibleProvider,     // = fetchState==='loaded' && providerGroups.length===0
  fetchState,               // 'idle' | 'loaded' | 'failed'
  resolvedProviderId,       // 经 runtime gate 后实际的 provider ID
  resolvedModel,            // 经 runtime gate 后实际的 model value
  providerWasFilteredOut,   // 显式 caller providerId 被 gate 替换 → 触发 PATCH
}
```

### 2.3 fetchState 三态行为

| state | providerGroups | noCompatibleProvider | resolvedProviderId | resolvedModel | 用途 |
|---|---|---|---|---|---|
| `idle` | `[]` 或上次结果（refetch 中） | `false` | 可能空 | 可能空 | 加载窗口，**所有 send 路径必须 gate** |
| `loaded` | server 返回的 groups | groups.length===0 | 算出的 fallback | 算出的 fallback | 正常 |
| `failed` | catch 合成的 `[{ env synthetic }]` | `false`（length=1） | `'env'` | `DEFAULT_MODEL_OPTIONS[0]` | API 不可用 best-effort |

**不变量**：fetchAll 头部**必须** `setFetchState('idle')`；refetch 期间不能仍按 'loaded' 让 send 走旧 feed。

### 2.4 providerId / preferredProviderId / requestedProviderId 三层语义

| 层 | 计算 | 用途 |
|---|---|---|
| Caller `providerId` prop | undefined / '' / 显式字符串 | 三种语义不能混 |
| `requestedProviderId` | `undefined` → `undefined`；`''` → `'env'`；显式 → 原值 | 跟 `resolvedProviderId` 对比算 `providerWasFilteredOut` |
| `preferredProviderId` | `undefined` → fallback chain；`''` → 'env' / fallback；显式 → 原值 | 用于 `providerGroups.find` 找当前 group |
| `resolvedProviderId` | currentGroup?.provider_id | 实际生效的 ID，发送和 PATCH 用这个 |

**不变量**：
- `providerId === undefined` ≠ `providerId === ''`。前者是 caller 没指定（用 fallback），后者是历史 env-mode session 的 explicit value
- `requestedProviderId vs resolvedProviderId` 比较算 filteredOut，不能用 raw providerId vs resolvedProviderId（empty string 永远不等于任何 group ID，会 false-positive）

### 2.5 AbortController 治竞态

`fetchAll` 头部：
```ts
fetchControllerRef.current?.abort();
const controller = new AbortController();
fetchControllerRef.current = controller;
fetch(url, { signal: controller.signal });
```

`.then` 头部 `if (signal.aborted) return`；`.catch` 头部 `if (err?.name === 'AbortError' || signal.aborted) return`。

**不变量**：`provider-changed` 事件触发 refetch 时，旧请求晚到不能覆盖新请求结果。

## 3. ChatView 三道 send gate

`doStartStream` 入口顺序：

```ts
// Gate 1: idle = picker 未加载，发送会绕过 runtime 过滤
if (providerFetchState === 'idle') return;

// Gate 2: noCompatibleProvider = 真空集合，没有 provider 兼容当前 runtime
if (noCompatibleProvider) return;

// Gate 3: loaded 态下 resolved pair 不能为空
if (providerFetchState === 'loaded' && (!resolvedProviderId || !resolvedModel)) return;
```

不变量：三道 gate**全部**必须存在。删掉任何一道都会让 cross-wire 重新出现。

`sendMessage` 头部**也**必须有 gate 1 + gate 2（在 append user message 之前），否则 user 看到自己消息悬停无回复。`dequeue useEffect` 同样。

## 4. ChatView resolved pair 同步

```ts
useEffect(() => {
  if (providerFetchState !== 'loaded') return;
  if (!providerWasFilteredOut) return;
  if (!resolvedProviderId || !resolvedModel) return;
  if (resolvedProviderId === currentProviderId && resolvedModel === currentModel) return;
  setCurrentProviderId(resolvedProviderId);
  setCurrentModel(resolvedModel);
  fetch(`/api/chat/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: resolvedModel, provider_id: resolvedProviderId }),
  }).catch(() => {});
}, [providerFetchState, providerWasFilteredOut, resolvedProviderId, resolvedModel, currentProviderId, currentModel, sessionId]);
```

不变量：
- `providerFetchState !== 'loaded'` 跳过 — idle 时 hook 信号不可靠；failed 时 catch 已合成 env，不强制 PATCH
- `providerWasFilteredOut` 必须为 true 才同步 — 防止稳态下反复 PATCH
- 等值检查防止 React 18 双 effect / 重复 fetch
- DB PATCH 失败 silent — UI 已切了，DB 同步是 best-effort（下次打开会再次 trigger 同步）

## 5. ChatView 初始化保留 '' 语义

```ts
const [currentProviderId, setCurrentProviderId] = useState(() =>
  providerId !== undefined
    ? providerId
    : (typeof window !== 'undefined' ? localStorage.getItem('codepilot:last-provider-id') : null) || ''
);

useEffect(() => { if (providerId !== undefined) setCurrentProviderId(providerId); }, [providerId]);
```

不变量：判断**必须** `=== undefined`，不能用 truthy `||` 短路。`providerId === ''` 是 env-mode session 的合法 prop 值，被当 falsy → localStorage 抢走 → 历史 env session 切到别的 provider。

`modelName` 可以继续按 truthy 处理 — empty model 不是合法 session 状态，env session 的 model 也是 'sonnet' / 'opus' / 'haiku'。

## 6. MessageInput auto-correct

`MessageInput.tsx:181-187`：
```ts
useEffect(() => {
  if (modelName && modelOptions.length > 0 && !modelOptions.some(m => m.value === modelName)) {
    const fallback = modelOptions[0].value;
    onModelChange?.(fallback);
    onProviderModelChange?.(currentProviderIdValue, fallback);
  }
}, [modelName, modelOptions, currentProviderIdValue, onModelChange, onProviderModelChange]);
```

不变量：
- 只在 `modelName` 不在 `modelOptions` 时触发（别频繁 fire）
- fallback 用 `modelOptions[0]`，不要用 `globalDefaultModel`（globalDefault 只对新会话有意义；存量 session 强行覆盖会把用户原选择丢掉）
- `onProviderModelChange` 传 `currentProviderIdValue`（hook 算的 fallback group ID），不要传 raw `providerId` prop（那是已被替换的旧 ID）

## 7. New Chat Page (chat/page.tsx) 自治

`chat/page.tsx` **不**用 `useProviderModels` hook —— 它有自己的 init useEffect，直接 fetch + 自己管 `currentModel/currentProviderId/noCompatibleProvider` state。

为什么不复用 hook：新会话初始化要把 saved provider/model 跟 global default 对比，决定用哪个；逻辑跟 hook 的"展示 picker"职责不同。两套代码各自完整。

不变量：两条路径**都**必须遵守同一契约：
- `?runtime=auto` 拉 runtime-filtered feed
- `groups: []` → `noCompatibleProvider=true` + 清 currentProviderId/Model
- 不要把 saved provider/model 塞回到刚被 runtime 滤掉的位置
- `sendFirstMessage` 加 `noCompatibleProvider` + `!currentModel || !currentProviderId` 防御

## 8. Auto-trigger 同样吃 resolved pair

`useAssistantTrigger` 通过 props 接收 `resolvedModel / resolvedProviderId / noCompatibleProvider / fetchState`。`checkAssistantTrigger` 头部三道 gate：

```ts
if (fetchState !== 'loaded') return;
if (noCompatibleProvider) return;
if (!resolvedProviderId || !resolvedModel) return;
```

不变量：welcome / heartbeat 这种 auto-trigger 也走 resolved pair，不能用 raw `currentModel/currentProviderId`。Auto-trigger 是 backend route 的入口之一，必须跟 user-typed send 同样的 gate。

## 9. 关键文件 + 责任

| 模块 | 文件 | 不变量 |
|---|---|---|
| Hook 主体 | `src/hooks/useProviderModels.ts` | 五字段契约 + AbortController + 三态 fetchState + undefined/'' 区分 |
| Composer 顶层 | `src/components/chat/MessageInput.tsx` line 172 | 调 hook 默认 runtime='auto'；auto-correct fallback 用 modelOptions[0] 不用 globalDefault |
| ChatView 顶层 | `src/components/chat/ChatView.tsx` line 142+ | 调 hook + 同步 useEffect + 三道 gate + sendMessage 头部 gate |
| New Chat Page init | `src/app/chat/page.tsx` line 110+ + line 295+ | `?runtime=auto`；空集合不走 localStorage；sendFirstMessage 防御 |
| Auto-trigger | `src/hooks/useAssistantTrigger.ts` | 接收 resolved pair；三道 gate；startStream 用 resolved pair |
| ChatView state init | `ChatView.tsx` line 130-138 | `providerId !== undefined ? providerId : localStorage` 不能用 truthy |

## 10. 改 / 加新功能必须检查

- 新增 chat 入口（除 chat-route / bridge / new chat / chat[id] 外）：
  - 必须吃 resolved pair，不要用 raw saved provider/model
  - 必须有 idle / noCompatibleProvider gate
- 新增 hook consumer：
  - 默认走 `runtime: 'auto'`
  - 看 fetchState 而不是 providerGroups.length
  - empty providerGroups + loaded ≠ 完全没 provider，可能用户没兼容的 → noCompatibleProvider 信号
- 改 MessageInput 模型选择 UI：
  - **不能**让 picker 显示 hook 不返回的 model（picker 永远 = modelOptions = hook 算后）
  - 改 onProviderModelChange callback 时确保把 hook 的 `currentProviderIdValue` 传上去而非 prop
- 改 ChatView state 初始化：
  - 任何 `providerId || ...` 短路写法都是 bug，必须 `providerId !== undefined`
  - `modelName || ...` OK（empty model 不合法）
- 加 send 路径前置逻辑（如新的 retry / queue）：
  - 在 append user message 之前 gate
  - 或者让 doStartStream 返回 boolean，caller 据此决定是否 append

## 11. 常见坑

1. **`providerId || localStorage.getItem(...)`** — env session 被 localStorage 抢
2. **`if (providerId)` 同步 effect** — env session 的 prop '' 不被同步
3. **fetchState 初始 'loaded'** — 挂载第一帧就误判 noCompatibleProvider
4. **fetchAll 不重置 fetchState** — provider-changed refetch 期间用旧 feed
5. **没 abort** — 慢的旧请求覆盖新请求
6. **idle 状态不 gate** — 加载窗口 send 绕过 runtime 过滤
7. **append user message 在 gate 之前** — gate 退出后用户消息悬挂无回复
8. **auto-trigger 用 raw currentModel/currentProviderId** — backend 端绕过 runtime gate
9. **同步 effect 缺 `providerFetchState` deps** — eslint-disable React Hook 后忘记加
10. **MessageInput auto-correct fallback 用 globalDefaultModel** — 存量 session 被强行改

## 12. 测试覆盖

| 测试文件 | 覆盖 |
|---|---|
| `src/__tests__/unit/chat-runtime.test.ts` | 5 个 chat-runtime helper test，含 registry 注册副作用回归 |
| `src/__tests__/unit/provider-resolver.test.ts` | resolveProvider 在 runtime opt 下的 hidden + runtime stack |
| 待补 `useProviderModels.test.ts` | hook 单测：fetchState 转移 / providerWasFilteredOut / requestedProviderId 三层语义 / AbortController 竞态 |
| 待补 `ChatView-send-gate.test.ts` | 三道 gate / append-before-gate 防御 |
| `src/__tests__/unit/sdk-subprocess-env.test.ts` | toClaudeCodeEnv 不 leak hidden role default |

加 / 改本文涉及任何契约时，至少跑 chat-runtime.test.ts + provider-resolver.test.ts；理想是把 useProviderModels 的 hook test 补上。

## 13. 设计决策日志

- **2026-04-26** Resolved pair 抽成 hook 契约 — Codex review 指出"旧 provider 被过滤但仍发送"；统一让所有 chat 入口吃同一对
- **2026-04-26** undefined vs '' 严格区分 — Codex review 指出 env 旧会话被 localStorage 抢
- **2026-04-26** AbortController 治 fetchAll 竞态 — Codex review 指出 provider-changed 期间旧响应覆盖新
- **2026-04-26** fetchState idle 阻塞 send — Codex review 指出加载窗口 raw 发送绕过 runtime gate
- **2026-04-26** 拆 requestedProviderId vs preferredProviderId — env session + env 不在 feed 时 providerWasFilteredOut 误判 false
- **2026-04-26** ChatView 顶层调 hook 而非通过 props — 让 MessageInput 内部 hook 跟 ChatView 共享同一 fetch 结果不可行（state 各自），但两个 instance 的 fetch 是廉价的
- **2026-04-26** auto-trigger 也吃 resolved pair — welcome/heartbeat 之前用 raw currentModel/currentProviderId 绕过 runtime gate
