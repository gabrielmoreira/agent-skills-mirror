# PermissionBoundary Guardrail

> **Status: Active** — 2026-07-20 因 Claude/Codex auto reviewer 接线与旧版本降级完成首次真实填充。
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
| 4 | Runtime 的 reviewer 能力必须由该 Runtime 自己的事实源判定；Codex 不得受 Claude SDK 版本探测影响 | `src/lib/permission/profile.ts`、capability route |
| 5 | Codex `auto_review` 需同时通过保守版本门和 thread start/resume 回显；旧版、未知版本、缺少/不一致回显一律降级到 user reviewer，并发 canonical `unavailable` | `src/lib/codex/app-server-manager.ts`、`runtime.ts` |
| 6 | 权限 profile 是 CodePilot 会话事实源：Codex default 显式发送 on-request + user + workspace sandbox，不隐式继承用户全局 config；Plan/full access/auto 各自保持独立语义 | `src/lib/codex/permission.ts` |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `src/lib/permission/*` | 工具白名单 + 用户确认流程 |
| `src/lib/agent-sdk-capabilities.ts` | mutationLevel 派生 |
| `src/__tests__/unit/harness-capability-contract.test.ts` | 跨 Runtime exposure 一致性 |
| `src/lib/permission/profile.ts` | 跨 Runtime reviewer capability 分流与 fail-closed |
| `src/lib/codex/app-server-manager.ts` | Codex binary 版本门与最低已验证版本 |
| `src/lib/codex/permission.ts` | Codex profile → thread/turn wire 与回显降级 |
| `src/lib/codex/runtime.ts` | 运行时二次门禁、thread 回显和 canonical unavailable |

## 改动检查表

- [ ] 加新工具时确认默认是 unsafe，明确决定是否加入 PERMISSION_SAFE_TOOLS
- [ ] 改 mutationLevel 分类时跑 harness-capability-contract.test.ts
- [ ] 新 Runtime 接入时填能力矩阵；不支持的能力标 `unsupported` 不能假装支持
- [ ] 改 reviewer capability 时覆盖 UI route 与运行时 shipping boundary；不得只在下拉框禁用
- [ ] 改 Codex thread/turn 权限字段时同时验证 start、resume、resume fallback 与每 turn 刷新
- [ ] 版本能力未知时 fail closed；禁止把当前开发机版本当作所有用户版本

## 常见坑

- `codepilot_*` 工具名前缀曾被当作"内部工具自动放行"——这是 Phase 5e 修的真实安全洞，不要再引入类似的"按 prefix 放行"逻辑。
- live smoke 前必须先过 contract test；不要用 live smoke 驱动逐个补丁（Phase 5b round 6 教训）。
- 不要用 Claude Agent SDK 的版本或 MCP 探测结果判断 Codex reviewer；两者没有依赖关系。
- 仅依赖“请求没有报错”不能证明 Codex 接受 reviewer 字段；旧 app-server 可能忽略未知字段，必须检查响应回显。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| 跨 Runtime exposure | `harness-capability-contract.test.ts` |
| Runtime-specific auto reviewer gate | `permission-runtime-capability.test.ts` |
| Codex profile mapping、版本门、thread 回显与运行时消费 | `codex-permission-wire.test.ts`、`codex-binary-discovery.test.ts` |

## 设计决策日志

- 2026-05-18 — Phase 5e：`codepilot_*` 前缀洞改为 mutationLevel 派生；Native image/media 走 MediaBlock side-channel；live=zero unsupported exposures（详见 `completed/phase-5e-runtime-harness-architecture.md`）。
- 2026-07-20 — Codex auto reviewer 不再依赖 Claude SDK capability；最低已验证版本保守钉为 `0.145.0-alpha.18`，并以 thread start/resume 的 `approvalsReviewer` 回显作为最终事实源。
- 2026-07-20 — 接受 CodePilot profile 覆盖用户 Codex 全局默认的产品语义：会话选择必须可预测，default 显式使用 user reviewer + workspace sandbox；这可能比用户全局配置更保守，但不会静默放宽。
