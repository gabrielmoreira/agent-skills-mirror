# Everything Claude Code (ECC) — 智能体（Agent）指令

这是一个**生产级 AI 编码插件**，为软件开发提供 13 个专业智能体（Agent）、50+ 个技能（Skill）、33 个命令（Command）以及自动化的钩子（Hook）工作流（Workflow）。

## 核心原则

1. **智能体优先（Agent-First）** — 将领域任务委托给专业智能体处理
2. **测试驱动（Test-Driven）** — 先写测试后实现，要求 80% 以上的覆盖率
3. **安全第一（Security-First）** — 绝不在安全性上妥协；验证所有输入
4. **不可变性（Immutability）** — 始终创建新对象，绝不修改现有对象
5. **先规划后执行（Plan Before Execute）** — 在编写代码前先规划复杂功能的实现

## 可用智能体（Available Agents）

| 智能体（Agent） | 用途 | 何时使用 |
|-------|---------|-------------|
| planner | 实现规划 | 复杂功能、重构 |
| architect | 系统设计与可扩展性 | 架构决策 |
| tdd-guide | 测试驱动开发 | 新功能、错误修复 |
| code-reviewer | 代码质量与可维护性 | 编写/修改代码后 |
| security-reviewer | 漏洞检测 | 提交前、敏感代码 |
| build-error-resolver | 修复构建/类型错误 | 构建失败时 |
| e2e-runner | 端到端 Playwright 测试 | 关键用户流程 |
| refactor-cleaner | 死代码清理 | 代码维护 |
| doc-updater | 文档与代码映射（codemaps） | 更新文档 |
| go-reviewer | Go 代码审查 | Go 项目 |
| go-build-resolver | Go 构建错误 | Go 构建失败 |
| database-reviewer | PostgreSQL/Supabase 专家 | 模式设计、查询优化 |
| python-reviewer | Python 代码审查 | Python 项目 |

## 智能体编排（Agent Orchestration）

无需用户提示，主动使用智能体：
- 复杂功能请求 → **planner**
- 刚刚编写/修改的代码 → **code-reviewer**
- 错误修复或新功能 → **tdd-guide**
- 架构决策 → **architect**
- 安全敏感代码 → **security-reviewer**

对于独立操作使用并行执行 — 同时启动多个智能体。

## 安全指南（Security Guidelines）

**在进行任何提交前：**
- 无硬编码密钥（API 密钥、密码、令牌）
- 所有用户输入均已验证
- 防止 SQL 注入（参数化查询）
- 防止 XSS（清理 HTML）
- 已启用 CSRF 保护
- 身份验证/授权已验证
- 所有端点均设有频率限制（Rate limiting）
- 错误消息不会泄露敏感数据

**密钥管理（Secret management）：** 绝不硬编码密钥。使用环境变量或密钥管理器。在启动时验证所需密钥。立即轮换任何暴露的密钥。

**如果发现安全问题：** 停止（STOP） → 使用 security-reviewer 智能体 → 修复关键（CRITICAL）问题 → 轮换暴露的密钥 → 检查代码库是否存在类似问题。

## 编码风格（Coding Style）

**不可变性 (关键)：** 始终创建新对象，绝不直接修改。返回应用更改后的新副本。

**文件组织：** 倾向于多个小文件而非少数大文件。通常为 200-400 行，最多 800 行。按功能/领域组织，而非按类型。高内聚，低耦合。

**错误处理：** 在每个层级处理错误。在 UI 代码中提供用户友好的消息。在服务端记录详细的上下文（Context）。绝不默默吞掉错误。

**输入验证：** 在系统边界验证所有用户输入。使用基于模式（schema-based）的验证。出现错误时快速失败并提供清晰的消息。绝不信任外部数据。

**代码质量自检清单：**
- 函数简短（<50 行），文件集中（<800 行）
- 无深度嵌套（>4 层）
- 正确的错误处理，无硬编码值
- 易读、命名规范的标识符

## 测试要求（Testing Requirements）

**最低覆盖率：80%**

测试类型（全部必需）：
1. **单元测试（Unit tests）** — 独立函数、实用工具、组件
2. **集成测试（Integration tests）** — API 端点、数据库操作
3. **端到端测试（E2E tests）** — 关键用户流程

**TDD 工作流 (强制)：**
1. 先写测试 (红灯/RED) — 测试应当失败
2. 编写最小化实现 (绿灯/GREEN) — 测试应当通过
3. 重构 (改进/IMPROVE) — 验证覆盖率 80%+

排除故障：检查测试隔离性 → 验证 Mock → 修复实现（除非测试本身错误，否则不要修改测试）。

## 开发工作流（Development Workflow）

1. **规划 (Plan)** — 使用 planner 智能体，识别依赖项和风险，分解为多个阶段
2. **TDD** — 使用 tdd-guide 智能体，先写测试，再实现，后重构
3. **审查 (Review)** — 立即使用 code-reviewer 智能体，解决关键（CRITICAL）/高危（HIGH）问题
4. **提交 (Commit)** — 采用约定式提交（Conventional commits）格式，提供详尽的 PR 摘要

## Git 工作流（Git Workflow）

**提交格式：** `<type>: <description>` — 类型：feat, fix, refactor, docs, test, chore, perf, ci

**PR 工作流：** 分析完整提交历史 → 起草详尽摘要 → 包含测试计划 → 使用 `-u` 标志推送。

## 架构模式（Architecture Patterns）

**API 响应格式：** 一致的信封格式，包含成功指示符、数据负载、错误消息和分页元数据。

**仓库模式 (Repository pattern)：** 将数据访问封装在标准接口（findAll, findById, create, update, delete）之后。业务逻辑依赖于抽象接口，而非存储机制。

**骨架项目 (Skeleton projects)：** 搜索经过实战检验的模板，使用并行智能体（安全性、可扩展性、相关性）进行评估，克隆最匹配的模板，并在经过验证的结构中进行迭代。

## 性能优化（Performance）

**上下文管理（Context management）：** 对于大型重构和多文件功能，避免使用上下文窗口最后 20% 的空间。较低敏感度的任务（单个编辑、文档、简单修复）可以容忍更高的利用率。

**构建故障排除：** 使用 build-error-resolver 智能体 → 分析错误 → 逐步修复 → 每次修复后进行验证。

## 项目结构（Project Structure）

```
agents/          — 13 个专业子智能体
skills/          — 50+ 个工作流技能和领域知识
commands/        — 33 个斜杠命令
hooks/           — 基于触发器的自动化
rules/           — 始终遵守的准则（通用 + 按语言）
scripts/         — 跨平台 Node.js 实用工具
mcp-configs/     — 14 个 MCP 服务器配置
tests/           — 测试套件
```

## 成功指标（Success Metrics）

- 所有测试通过且覆盖率达到 80%+
- 无安全漏洞
- 代码易读且可维护
- 性能可接受
- 满足用户需求
