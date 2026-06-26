---
description: "智能体编排 (Agent orchestration)：可用智能体、并行执行、多维度分析"
alwaysApply: true
---
# 智能体编排 (Agent Orchestration)

## 可用智能体 (Available Agents)

位于 `~/.claude/agents/`：

| 智能体 (Agent) | 用途 | 何时使用 |
|-------|---------|-------------|
| planner | 实现规划 | 复杂功能、重构 |
| architect | 系统设计 | 架构决策 |
| tdd-guide | 测试驱动开发 (TDD) | 新功能、故障修复 (Bug fixes) |
| code-reviewer | 代码审查 | 编写代码后 |
| security-reviewer | 安全分析 | 提交 (Commits) 前 |
| build-error-resolver | 修复构建错误 | 构建失败时 |
| e2e-runner | E2E 测试 | 关键用户流程 |
| refactor-cleaner | 死代码清理 | 代码维护 |
| doc-updater | 文档更新 | 更新文档 |

## 立即使用智能体 (Immediate Agent Usage)

无需用户提示：
1. 复杂功能请求 - 使用 **planner** 智能体
2. 刚编写/修改的代码 - 使用 **code-reviewer** 智能体
3. 故障修复或新功能 - 使用 **tdd-guide** 智能体
4. 架构决策 - 使用 **architect** 智能体

## 任务并行执行 (Parallel Task Execution)

对于独立操作，务必 (ALWAYS) 使用任务并行执行：

```markdown
# 推荐：并行执行
并行启动 3 个智能体：
1. 智能体 1：身份验证 (Auth) 模块的安全分析
2. 智能体 2：缓存系统的性能审查
3. 智能体 3：实用工具类 (Utilities) 的类型检查

# 错误：非必要的串行执行
先运行智能体 1，然后智能体 2，最后智能体 3
```

## 多维度分析 (Multi-Perspective Analysis)

对于复杂问题，使用角色拆分后的子智能体：
- 事实审查者 (Factual reviewer)
- 资深工程师 (Senior engineer)
- 安全专家 (Security expert)
- 一致性审查者 (Consistency reviewer)
- 冗余检查者 (Redundancy checker)
