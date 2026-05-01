---
name: shared-operational-rules
description: |
  全局运维规则集 - 按需加载的对话管理、MCP工具、代码规范、质量检查等规则。
  触发关键词: 运维规则, MCP工具, 代码规范, 质量自检, 对话管理, 版本检查, 阶段过渡
triggers:
  - 运维规则
  - MCP工具
  - 代码规范
  - 质量自检
  - 对话管理
  - 版本检查
version: "1.0"
last_updated: "2026-03-26"
---

# 📋 全局运维规则集

> 本 Skill 不直接执行，而是作为**按需加载的规则仓库**供其他 Skill 和 copilot-instructions.md 引用。
> 各规则文件位于 references 子目录，AI 在对应场景触发时按需读取。

---

## 📂 规则索引

| 规则文件 | 何时加载 | 适用场景 |
|----------|----------|----------|
| references/conversation-lifecycle.md | 执行重型 Skill 前 | 对话健康度检测、跨对话续接、多轮修正处理 |
| references/mcp-tools-status.md | 调用 MCP 工具前 | Azure DevOps / 飞书 MCP 工具表、错误处理 |
| references/platform-identification.md | 搜索代码前 | 判断用户问题涉及平台层 vs 应用层 |
| references/pbi-parsing.md | 检测到 PBI 输入时 | PBI ID/链接/标题的自动解析规则 |
| references/quality-selfcheck.md | 工作流 Skill 执行完毕后 | 输出质量异常信号检测 |
| references/workflow-transitions.md | 阶段切换时 | 需求→设计→编码的过渡检查和拦截规则 |
| references/coding-standards.md | 编码或代码审查时 | 命名约定、PowerShell 编码安全 |
| references/mcp-and-devops.md | 会话首次调用 Skill 时 | 知识库版本检查 + Azure DevOps MCP 仓库规则 |
| references/proactive-clarification.md | 对用户意图/需求范围不确定时 | 三级不确定性分级、颗粒度守则、先搜后问 |

---

## 🔴 加载规则（AI 必遵）

1. **不要一次性读取所有 reference 文件** — 仅在对应场景触发时读取需要的文件
2. **重型 Skill 执行前** — 必须读取 `conversation-lifecycle.md`
3. **涉及 MCP 工具调用** — 必须读取 `mcp-tools-status.md`
4. **涉及 Azure DevOps 仓库** — 必须读取 `mcp-and-devops.md`
5. **首次调用任意 Skill** — 静默读取 `mcp-and-devops.md` 执行版本检查
