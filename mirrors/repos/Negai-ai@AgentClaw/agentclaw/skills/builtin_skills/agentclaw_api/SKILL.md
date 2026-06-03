---
name: agentclaw_api
description: Run existing workflows via local /_internal/* relay; relay handles internal authentication. Use AgentClaw platform APIs for workflow/agent execution, scheduler automation, traces/logs, knowledge bases, channels, conversations, files, prompts, models, and hot registration.
metadata: {"always_inject": true}
---

# AgentClaw 平台 API 使用指南

Read this file first. Read `references/*` only when需要操作具体模块时。

## 何时使用 agentclaw_api

- 用户请求可以由已注册的 AgentClaw workflow/agent 能力完成，例如运行、触发、查询或续传已有工作流。
- 用户要创建、查询、更新、删除、暂停、恢复或立即触发定时任务。
- 用户说“每天/每小时/定期/周期性/cron/自动运行某个工作流或智能体”。
- 用户要把已经创建的工作流接入平台运行能力，例如热注册工作流文件、调用工作流、配置调度、查看执行历史。
- 用户要通过平台 API 管理知识库、渠道、对话、文件、提示词、模型、追踪日志。

定时任务相关操作请读取 `references/scheduler.md`，创建任务使用 `POST /api/scheduler/jobs`。

## 调用方式

- **入口**: `{BASE_URL}` 是服务启动时写入 `<project_dir>/.agentclaw/relay.json` 的 `internal_url`。它是独立本机 internal relay 地址，通常不同于主服务端口。
- **备用入口**: 环境变量 `AGENTCLAW_INTERNAL_URL` 也可提供同一个本机 relay 地址。
- **认证**: 所有内部 agent/shell 请求通过 `/_internal/` 前缀访问，relay 会在服务端完成认证。请求只需要业务 payload 和 `Content-Type: application/json`。
- **拼接规则**: `{BASE_URL}/_internal` + 文档路径。文档里的 `/api/...`、`/admin/...` 是目标路径，不是最终 URL。
- **工具选择**: 调用 API 时使用 `python` 或 `shell` 工具发送 HTTP 请求（例如 `requests.post()`、`curl`）。

| 文档路径 | 实际调用路径 |
|---------|------------|
| `/api/workflow/run` | `{BASE_URL}/_internal/api/workflow/run` |
| `/admin/knowledgebases` | `{BASE_URL}/_internal/admin/knowledgebases` |
| `/api/scheduler/jobs` | `{BASE_URL}/_internal/api/scheduler/jobs` |

### 入口读取示例

```python
import json
import os
from pathlib import Path

project_dir = Path(os.getenv("AGENTCLAW_PROJECT_DIR", ".")).resolve()
relay_config = project_dir / ".agentclaw" / "relay.json"
base_url = os.getenv("AGENTCLAW_INTERNAL_URL", "").rstrip("/")
if not base_url and relay_config.exists():
    base_url = json.loads(relay_config.read_text(encoding="utf-8"))["internal_url"].rstrip("/")

url = f"{base_url}/_internal/api/workflow/run"
```

### 错误响应

```json
{"error": "错误描述", "code": "ERROR_CODE"}
```

HTTP 状态码: `400` 参数错误, `401` 未认证, `404` 未找到, `500` 内部错误

---

## 按需读取参考文档

### `references/workflow.md` — 工作流执行与对话

- 列出所有可用工作流
- 执行工作流（blocking 同步 / streaming SSE 流）
- HumanNode 交互续传（等待人工输入后继续）
- 确认危险操作
- SSE 流模式事件序列
- 上下文压缩 / 截断（编辑重试）
- 对话 CRUD（创建、列出、获取详情含消息、更新标题、删除）
- 消息反馈（like / dislike）
- 文件上传 / 下载（multipart 上传、按 ID 下载、Token 临时链接）

### `references/knowledgebase.md` — 知识库管理

- 知识库 CRUD（创建、列出、获取、更新检索配置、删除）
- 文档管理（上传、导入本地文件、列出、下载、重建索引、替换、删除）
- 分块管理（列出、创建、更新内容、删除）
- 知识库检索（hybrid/dense/keyword 模式、相似度阈值、Top K、Rerank 重排序）
- 检索日志（列出、创建、清空）

### `references/scheduler.md` — 定时任务

- 创建定时任务（绑定工作流 + 触发器 + 输入参数）
- 触发器配置（Cron 表达式 / 固定间隔 / 一次性定时）
- 任务 CRUD（创建、列出、获取、更新、删除）
- 任务控制（暂停、恢复、立即触发）
- Webhook 外部触发（Secret 验证、输入覆盖）
- 执行历史（列出执行记录、获取执行详情）
- 执行配置（超时、重试、并发策略）

### `references/channels.md` — 渠道管理

- 渠道 CRUD（创建飞书/钉钉/企微/QQ 渠道，配置 app_id/app_secret、会话模式、绑定工作流）
- 重启渠道 Bot 连接
- 验证渠道凭据（创建前检测配置是否有效）
- 渠道消息日志（全局/单渠道日志列表、按状态筛选、日志统计）

### `references/traces.md` — 追踪与监控

- 追踪摘要（总数、成功/失败/运行中/超时统计、平均耗时）
- 追踪列表（按工作流/状态/时间范围筛选，分页）
- 追踪详情（节点执行日志 NodeLog、LLM 调用日志 LLMLog、输入输出数据）
- 追踪时间线（按时间排序的事件序列，用于可视化）
- 仪表盘统计与趋势（24h/7d/30d）

### `references/prompts_models.md` — 提示词与模型管理

- 提示词列表/获取/更新（热加载，立即生效）/重置为默认值
- 提示词版本历史与回滚到指定版本
- 模型列表（含降级状态 FallbackState）
- 模型配置更新（temperature、max_tokens、timeout）
- 切换工作流节点模型
- 手动降级到备用模型 / 恢复主模型

### `references/workflow_admin.md` — 工作流管理与任务管理

- 工作流列表（含 24h 统计）、详情（节点拓扑、边、输入 Schema、统计）
- 工作流统计与趋势（24h/7d/30d）
- 热加载工作流文件（从文件系统注册/替换工作流）
- 工具配置（启禁用 skills 和 tools）
- 任务管理（列出运行中任务、取消任务、清理已完成任务）
