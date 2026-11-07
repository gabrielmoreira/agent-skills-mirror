# Agent 与 MCP 文档

本目录说明外部 AI Agent 如何通过受控接口使用 QuantDinger。建议人工接入者从中文指南开始；自动化工具应以 OpenAPI 和英文标识符为准。

## 推荐阅读顺序

1. [Agent Gateway 快速开始](AGENT_QUICKSTART_CN.md)：创建令牌、验证身份、提交策略与回测。
2. [MCP 接入指南](MCP_SETUP_CN.md)：连接 Cursor、Claude Code、Codex 或远程 Agent。
3. [Cursor MCP 配置示例](cursor-mcp.example.json)：使用可替换地址与 Token 占位符的最小配置。
4. [Agent OpenAPI](agent-openapi.json)：查看 `/api/agent/v1` 的机器可读契约。
5. [API 约定](../architecture/API_CONVENTIONS.md)（英文）：理解响应、认证和接口分层。

## 权限模型

| Scope | 用途 | 典型操作 |
|---|---|---|
| `R` | 只读 | 行情、研究、账户与运行状态 |
| `W` | 写入配置 | 保存策略源码、创建停止状态的部署 |
| `B` | 回测 | 提交、查询或取消回测任务 |
| `N` | 通知 | 管理和触发信号提醒 |
| `T` | 交易与运行时 | 停止策略、下单、紧急停止 |
| `C` | 管理 | 仅管理员使用 |

令牌权限不会绕过服务端实盘开关、标的白名单、名义金额上限、有效期、速率限制或审计。所有会产生副作用的 `W/B/N/T` 请求都应提供唯一的 `Idempotency-Key`。

## 语言与契约约定

- 中文页面解释操作流程和风险；英文页面与代码中的路由、字段、Scope、环境变量保持原样。
- `agent-openapi.json` 是 Agent HTTP 接口的权威契约。
- Human Web API 另见 [Web API 文档](../api/README_CN.md)，不要混用人类 JWT 与 Agent Token。

仓库级编码 Agent 指令统一维护在根目录的 [`AGENTS.md`](../../AGENTS.md)。各工具的入口文件只负责加载这份规则，不在本目录重复维护。
