# Onboarding Guardrail

> **Status: Stub** — 七节模板占位。首次真实改动触发时由实施 Agent 按 [`README.md`](./README.md) 的七节模板填充。
> **为什么先读**：凭据形态多样（API key / OAuth / cc-switch shadow），错一处会让发送链路全炸。Phase 5b round 7 的 OAuth refresh bug 就是 sync 捕获了 stale 凭据导致——必须每次 fetch 闭包内 `await ensureTokenFresh()`。
> **已知关键文件**：`src/lib/ai-provider.ts`（OpenAI useResponsesApi fetch 闭包）、`src/lib/onboarding/*`、cc-switch 凭据桥接相关 lib。

## 词汇表

- `ensureTokenFresh()` — OAuth token 刷新闸门；fetch 前必跑。
- `cc-switch shadow` — per-request shadow `~/.claude/` 凭据桥。
- `useResponsesApi` — OpenAI Responses API 路径（区别于 Chat Completions）。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | OAuth 凭据必须每次 fetch 闭包内 `await ensureTokenFresh()`，不能在构造时 sync 捕获 | `src/lib/ai-provider.ts` |
| 2 | OpenRouter `/api`（Anthropic skin）→ `sdkType: 'claude-code-compat'`；`/api/v1`（OpenAI skin）→ `'openai'`。protocol 不能混 | `src/lib/provider-resolver.ts` |
| 3 | OpenRouter Anthropic-skin 历史 DB 行 alias 自指必须 canonicalize 到 preset 真实 slug；用户自定义 full slug 永不覆盖 | `provider-resolver.ts` + `/api/providers/models/route.ts` |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `src/lib/ai-provider.ts` | OAuth ensureTokenFresh 在 fetch 闭包 |
| `src/lib/provider-resolver.ts` | OpenRouter sdkType 双 SDK 分流 + alias canonicalization |
| `src/lib/runtime-compat.ts` | `isOpenRouterAnthropicSkinUrl` |
| `src/app/api/providers/models/route.ts` | picker 和 chat send 一致的 normalize |

## 改动检查表

- [ ] OAuth 相关改动确认 `ensureTokenFresh()` 在 fetch 闭包内 await，不是构造时 sync
- [ ] 加新 provider 时确认 sdkType 路由对（Anthropic-skin vs OpenAI-skin）
- [ ] 改 preset 时考虑历史 DB 行兼容性（用户已有的 provider_models 表会覆盖 preset 默认）
- [ ] 跑 capability matrix smoke 前先确认 contract test 通过（`feedback_no_live_smoke_driven_patching.md`）

## 常见坑

- Phase 5b round 7 — `getOAuthCredentialsSync()` 在构造时捕获 stale token，导致 refresh 后仍发旧 token，请求 401。修法：移到 fetch 闭包 + `await ensureTokenFresh()`。
- Phase 5b round 8 — 改了 preset 的 upstream slug，但用户历史 DB 行 `upstream_model_id='haiku'` 把 preset slug 盖掉。修法：alias→真实 upstream slug canonicalization（DB-wins merge 后做）。
- Phase 5b round 9 — 用户自定义 full slug 必须保留；只在 alias 自指或缺失时填 preset slug。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| OAuth fetch refresh | `openai-oauth-fetch-refresh.test.ts` |
| Provider resolver routing | `provider-resolver.test.ts` |
| OpenRouter normalization | DB-integration tests pin in resolver |

## 设计决策日志

- 2026-05-18 — Phase 5b round 6: macOS Codex.app bundle binary fallback。
- 2026-05-18 — Phase 5b round 7: OAuth `ensureTokenFresh` 移到 fetch 闭包；OpenRouter `/api` 路由到 `claude-code-compat`。
- 2026-05-18 — Phase 5b round 8: `OPENROUTER_ANTHROPIC_MODELS` preset 加 upstream slug。
- 2026-05-18 — Phase 5b round 9: 历史 DB 行 alias canonicalization。
