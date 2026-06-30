# MCP Guardrail

> **Status: Stub** — 七节模板占位。首次真实改动触发时由实施 Agent 按 [`README.md`](./README.md) 的七节模板填充。
> **为什么先读**：MCP server 加载 / provider resolution / 持久化跨多个 API 路由；`/api/plugins/mcp/status?sessionId=xxx` 自动从 session.provider_id 解析，前端不需要显式传 providerId（memory 已固化的关键模式）。
> **已知关键文件**：`src/app/api/plugins/mcp/*`、MCP server 加载相关 lib、`src/lib/db.ts` MCP 配置表。

## 词汇表

- `MCP` — Model Context Protocol，第三方工具/资源接入协议。
- `mcp/status` — Session-level MCP 状态查询接口。

## 不变量 / 契约表

| # | 不变量 | 由谁守 |
|---|--------|--------|
| 1 | `GET /api/plugins/mcp/status?sessionId=xxx` 自动从 `getSession(sessionId).provider_id` 解析 providerId；前端不需要也不应该显式传 | `src/app/api/plugins/mcp/status/route.ts` |
| 2 | provider_id 为空的 session 回退到 'env' | 同上 |
| 3 | （待填充） | |

## 关键文件 + 责任

| 文件 | 守哪条不变量 |
|------|--------------|
| `src/app/api/plugins/mcp/status/route.ts` | session→providerId 自动解析 |
| `src/app/api/plugins/mcp/*` | MCP 配置 CRUD + server 加载 |
| `src/lib/db.ts` | MCP 配置表 schema |

## 改动检查表

- [ ] 改 MCP status 路由时确认仍自动解析 providerId
- [ ] 加 MCP 配置字段时同步 schema migration
- [ ] 改 server 加载逻辑时考虑 Bridge 模式 / 后台常驻
- [ ] （待填充）

## 常见坑

- tech-debt #2 — `permission-registry` / `conversation-registry` 运行态依赖内存 Map，重启后丢失；MCP 相关运行态如果用同样模式要注意。
- tech-debt #5 — Bridge 的 `/mode plan` 在 `full_access` 时会被 `bypassPermissions` 覆盖；MCP 相关权限 / 模式控制要保持一致。

## 测试覆盖

| 契约 | 测试文件 |
|------|----------|
| | （待填充） |

## 设计决策日志

- 已实现：`/api/plugins/mcp/status` 自动 providerId 解析（memory 已固化）。
