# ECC 针对 Codex CLI 的指南

本文件为根目录下的 `AGENTS.md` 提供针对 Codex 的补充指导。

## 模型推荐（Model Recommendations）

| 任务类型 | 推荐模型 |
|-----------|------------------|
| 常规编码、测试、格式化 | o4-mini |
| 复杂功能、架构设计 | o3 |
| 调试、重构 | o4-mini |
| 安全审查 | o3 |

## 技能发现（Skills Discovery）

技能（Skills）从 `.agents/skills/` 目录自动加载。每个技能包含：
- `SKILL.md` — 详细说明与工作流（Workflow）
- `agents/openai.yaml` — Codex 接口元数据

可用技能：
- tdd-workflow — 测试驱动开发（TDD），包含 80% 以上的覆盖率
- security-review — 全面的安全自查清单
- coding-standards — 通用编码规范
- frontend-patterns — React/Next.js 模式
- frontend-slides — 视口安全（Viewport-safe）的 HTML 演示文稿及 PPTX 转 Web 转换工具
- article-writing — 基于笔记和语音参考的长文写作
- content-engine — 平台原生社交内容及内容再利用
- market-research — 带有来源引用的市场与竞争对手研究
- investor-materials — 幻灯片、备忘录、模型和单页介绍（One-pagers）
- investor-outreach — 个性化投资者触达与跟进
- backend-patterns — API 设计、数据库、缓存
- e2e-testing — Playwright 端到端（E2E）测试
- eval-harness — 评测驱动开发（EDD）
- strategic-compact — 上下文（Context）管理
- api-design — REST API 设计模式
- verification-loop — 构建、测试、Lint、类型检查、安全检查

## MCP 服务器（MCP Servers）

在 `~/.codex/config.toml` 的 `[mcp_servers]` 部分进行配置。参考 `.codex/config.toml` 中的示例配置，包含 GitHub、Context7、Memory 和 Sequential Thinking 服务器。

## 与 Claude Code 的主要区别

| 特性 | Claude Code | Codex CLI |
|---------|------------|-----------|
| 钩子（Hooks） | 8+ 种事件类型 | 暂不支持 |
| 上下文文件 | CLAUDE.md + AGENTS.md | 仅 AGENTS.md |
| 技能（Skills） | 通过插件加载技能 | `.agents/skills/` 目录 |
| 命令（Commands） | `/slash` 命令 | 基于指令（Instruction-based） |
| 智能体（Agents） | Subagent Task 工具 | 单智能体模型 |
| 安全（Security） | 基于钩子的强制执行 | 指令 + 沙箱 |
| MCP | 全面支持 | 仅限基于命令 |

## 无钩子模式下的安全（Security Without Hooks）

由于 Codex 缺少钩子（Hooks），安全强制执行是基于指令的：
1. 始终在系统边界验证输入
2. 严禁硬编码密钥 — 使用环境变量
3. 在提交前运行 `npm audit` / `pip audit`
4. 在每次推送前检查 `git diff`
5. 在配置中使用 `sandbox_mode = "workspace-write"`
