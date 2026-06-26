# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中处理代码提供指导。

## 项目概览 (Project Overview)

这是一个 **Claude Code 插件 (Plugin)** —— 一个包含生产级智能体 (Agents)、技能 (Skills)、钩子 (Hooks)、命令 (Commands)、规则 (Rules) 及 MCP 配置 (MCP Configurations) 的集合。本项目为使用 Claude Code 进行软件开发提供了经受过实战检验的工作流 (Workflows)。

## 运行测试 (Running Tests)

```bash
# 运行所有测试
node tests/run-all.js

# 运行单个测试文件
node tests/lib/utils.test.js
node tests/lib/package-manager.test.js
node tests/hooks/hooks.test.js
```

## 架构设计 (Architecture)

项目由以下核心组件组成：

- **agents/** - 用于委派 (Delegation) 的专业子智能体 (Subagents)（如 planner、code-reviewer、tdd-guide 等）
- **skills/** - 工作流 (Workflow) 定义与领域知识（如编码标准、模式、测试）
- **commands/** - 用户调用的斜杠命令 (Slash Commands)（如 `/tdd`、`/plan`、`/e2e` 等）
- **hooks/** - 基于触发器的自动化（如会话持久化、工具使用前/后钩子）
- **rules/** - 必须始终遵守的准则（如安全性、编码风格、测试要求）
- **mcp-configs/** - 用于外部集成的 MCP 服务配置
- **scripts/** - 用于钩子与设置的跨平台 Node.js 工具
- **tests/** - 针对脚本与工具的测试套件

## 核心命令 (Key Commands)

- `/tdd` - 测试驱动开发 (TDD) 工作流
- `/plan` - 实现方案规划 (Implementation Planning)
- `/e2e` - 生成并运行端到端 (E2E) 测试
- `/code-review` - 质量审查 (Quality Review)
- `/build-fix` - 修复构建错误
- `/learn` - 从会话 (Sessions) 中提取模式
- `/skill-create` - 从 Git 历史记录生成技能

## 开发注意事项 (Development Notes)

- 包管理器 (Package manager) 检测：支持 npm, pnpm, yarn, bun（可通过 `CLAUDE_PACKAGE_MANAGER` 环境变量或项目配置进行设置）
- 跨平台：通过 Node.js 脚本支持 Windows, macOS, Linux
- 智能体 (Agent) 格式：带有 YAML Frontmatter (元数据前置块) 的 Markdown 文件（包含名称、描述、工具、模型）
- 技能 (Skill) 格式：包含明确章节（何时使用、工作原理、示例）的 Markdown 文件
- 钩子 (Hook) 格式：包含匹配 (Matcher) 条件以及命令/通知钩子的 JSON 文件

## 贡献指南 (Contributing)

请遵循 CONTRIBUTING.md 中的格式要求：
- 智能体 (Agents)：带有 Frontmatter (name, description, tools, model) 的 Markdown 文件
- 技能 (Skills)：明确的章节划分（何时使用、工作原理、示例）
- 命令 (Commands)：带有描述性 Frontmatter 的 Markdown 文件
- 钩子 (Hooks)：带有匹配器 (Matcher) 和钩子数组的 JSON 文件

文件命名：小写字母加连字符（例如：`python-reviewer.md`, `tdd-workflow.md`）
