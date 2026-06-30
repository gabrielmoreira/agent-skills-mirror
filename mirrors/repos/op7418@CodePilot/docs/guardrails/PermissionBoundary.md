# PermissionBoundary Guardrail

> **Status: Stub** — 七节模板占位。首次真实改动触发时由实施 Agent 按 [`README.md`](./README.md) 的七节模板填充。
> **为什么先读**：`mutationLevel` + `PERMISSION_SAFE_TOOLS` 是 Phase 5e 修掉的安全洞（`codepilot_*` 权限前缀曾被默认放行）。改一处必须考虑**全部 Runtime**（claude_code / native / codex_proxy）的暴露一致性，否则会绕过权限框。
> **已知关键文件**：`src/lib/permission/*`、`src/lib/agent-sdk-capabilities.ts`（mutationLevel 派生）、`harness-capability-contract.test.ts`（契约测试）。

## 词汇表

- `mutationLevel` — 工具调用的"破坏性等级"分类，决定是否需要用户确认。
- `PERMISSION_SAFE_TOOLS` — 默认免确认的工具白名单。
- `unsupported` — 某 Runtime 不支持某能力的诚实降级标识。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | 任何新工具默认是受保护的（需要确认），明确加入 PERMISSION_SAFE_TOOLS 才放行 | `src/lib/permission/*` |
| 2 | mutationLevel 派生必须基于工具的实际行为（写文件 / 删数据 / 发网络请求），不能用 tool name 前缀猜测 | `src/lib/agent-sdk-capabilities.ts` |
| 3 | 跨 Runtime 暴露必须用 capability contract 表（live=zero unsupported exposures）；不能用 notes-based exceptions（`feedback_no_live_smoke_driven_patching.md`） | `harness-capability-contract.test.ts` |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `src/lib/permission/*` | 工具白名单 + 用户确认流程 |
| `src/lib/agent-sdk-capabilities.ts` | mutationLevel 派生 |
| `src/__tests__/unit/harness-capability-contract.test.ts` | 跨 Runtime exposure 一致性 |

## 改动检查表

- [ ] 加新工具时确认默认是 unsafe，明确决定是否加入 PERMISSION_SAFE_TOOLS
- [ ] 改 mutationLevel 分类时跑 harness-capability-contract.test.ts
- [ ] 新 Runtime 接入时填能力矩阵；不支持的能力标 `unsupported` 不能假装支持

## 常见坑

- `codepilot_*` 工具名前缀曾被当作"内部工具自动放行"——这是 Phase 5e 修的真实安全洞，不要再引入类似的"按 prefix 放行"逻辑。
- live smoke 前必须先过 contract test；不要用 live smoke 驱动逐个补丁（Phase 5b round 6 教训）。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| 跨 Runtime exposure | `harness-capability-contract.test.ts` |

## 设计决策日志

- 2026-05-18 — Phase 5e：`codepilot_*` 前缀洞改为 mutationLevel 派生；Native image/media 走 MediaBlock side-channel；live=zero unsupported exposures（详见 `completed/phase-5e-runtime-harness-architecture.md`）。
