# OpenClaw Kiro CLI 技能 🦉

[English](./README.md)

> 专用于 [Kiro CLI](https://kiro.dev/)（AWS AI 编程助手）的 [OpenClaw](https://github.com/openclaw/openclaw) 技能。

## 这是什么？

这个仓库提供了一个 **Kiro 专用技能**。它教会 OpenClaw 如何：

- 启动和管理 Kiro CLI 会话（交互式或一次性）
- 使用 Plan 模式处理复杂的多步骤项目
- 保存和恢复开发对话
- 切换自定义 Agent
- 在后台运行编程任务并跟踪进度

### 这个和 [openclaw-kirocli-coding-agent](https://github.com/terrificdm/openclaw-kirocli-coding-agent) 有什么区别？

| | 本仓库 (kiro-cli) | coding-agent |
|---|---|---|
| **专注点** | 仅 Kiro CLI | 多 Agent（Kiro, Codex, Claude Code, OpenCode, Pi） |
| **深度** | Kiro 全功能深度集成 | 通用编程 Agent 调度 |
| **使用场景** | 你只用 Kiro CLI | 你在多个编程 Agent 之间切换 |
| **功能** | Plan 模式、会话恢复、自定义 Agent、上下文管理 | 所有 Agent 的基础启动和监控 |

**选择本技能：** 你专注使用 Kiro CLI，想要完整的功能覆盖。

**选择 coding-agent：** 你使用多个编程 Agent，需要灵活性。

## 什么是 OpenClaw？

[OpenClaw](https://github.com/openclaw/openclaw) 是一个开源 AI 助手框架，可连接各种消息平台（WhatsApp、Discord、Telegram、Signal 等）。它可以通过 **技能（skills）** 扩展——针对特定任务的模块化指令集。

## 什么是 Kiro CLI？

[Kiro CLI](https://kiro.dev/) 是 AWS 的 AI 编程助手，具有强大功能：

- **Plan 模式** — 复杂项目的结构化规划
- **会话持久化** — 保存和恢复对话
- **自定义 Agent** — 预配置的工具权限和行为
- **MCP 集成** — Model Context Protocol 支持
- **Steering 文件** — 项目上下文感知

## 安装

### 1. 安装前置条件

**OpenClaw：** 参考[安装指南](https://docs.openclaw.ai/)

**Kiro CLI：**
```bash
curl -fsSL https://kiro.dev/install.sh | bash
kiro-cli login
```

### 2. 添加技能

**方式 A: 克隆到工作区（推荐）**
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/terrificdm/openclaw-kirocli-skill.git kiro-cli
```

**方式 B: 仅复制文件**
```bash
mkdir -p ~/.openclaw/workspace/skills/kiro-cli
cp -r skills/kiro-cli/* ~/.openclaw/workspace/skills/kiro-cli/
```

## 使用方法

安装后，当你提到 **"kiro"** 或需要处理代码相关任务时，OpenClaw 会自动使用此技能。

### 一次性任务

```
"用 kiro 给我的 API 路由添加错误处理"
"让 kiro 列出 src/ 下所有的 TODO 注释"
```

OpenClaw 运行：
```bash
kiro-cli chat --no-interactive --trust-all-tools "你的任务"
```

### 交互式会话

```
"启动一个 kiro 会话帮我构建 REST API"
"告诉 kiro 我想用 FastAPI 和 SQLAlchemy"
```

OpenClaw 管理后台会话：
```bash
# 启动会话
exec pty:true background:true command:"kiro-cli"

# 发送消息并监控进度
process action:submit sessionId:XXX data:"你的消息"
process action:log sessionId:XXX
```

### Plan 模式（复杂项目）

```
"用 kiro 的 plan 模式设计一个用户认证系统"
```

Plan 模式流程：
1. **需求** — Kiro 询问澄清问题
2. **调研** — 分析你的代码库
3. **规划** — 创建详细实施计划
4. **执行** — 经你批准后实施

### 会话管理

```
"恢复我上次的 kiro 对话"
"把这个 kiro 会话保存为 'auth-refactor'"
```

命令：`/chat save <名称>`、`/chat load <名称>`、`--resume`

## 主要功能

| 功能 | 命令/参数 | 描述 |
|------|-----------|------|
| Plan 模式 | `/plan` | 复杂任务的结构化规划 |
| 会话恢复 | `/chat save/load` | 持久化对话 |
| 自定义 Agent | `/agent swap <名称>` | 切换 Agent 配置 |
| 工具信任 | `--trust-all-tools` | 自动批准工具执行 |
| 上下文 | `@path` 语法 | 在对话中包含文件 |
| 模型切换 | `/model` | 会话中切换 AI 模型 |

## 文件结构

```
skills/kiro-cli/
├── SKILL.md              # 主技能说明
└── references/
    └── advanced.md       # 详细功能文档
```

## 测试场景

此技能已通过 10 个测试场景验证：

- ✅ 非交互模式（一次性任务）
- ✅ 后台交互模式（长时间运行会话）
- ✅ Plan 模式（1,215 行射击游戏项目）
- ✅ 会话保存/恢复
- ✅ 自定义 Agent 切换
- ✅ 模型确认（claude-sonnet-4.6）
- ✅ 工作区保护规则

## 重要提示

1. **始终使用 `pty:true`** — Kiro CLI 需要伪终端
2. **使用目录隔离** — `mkdir -p ~/project && cd ~/project && kiro-cli`
3. **永远不要在 `~/.openclaw/workspace` 运行** — 包含敏感文件

## 链接

- [OpenClaw](https://github.com/openclaw/openclaw) | [文档](https://docs.openclaw.ai/)
- [Kiro CLI](https://kiro.dev/) | [文档](https://kiro.dev/docs)
- [coding-agent 技能](https://github.com/terrificdm/openclaw-kirocli-coding-agent)（多 Agent 版本）
