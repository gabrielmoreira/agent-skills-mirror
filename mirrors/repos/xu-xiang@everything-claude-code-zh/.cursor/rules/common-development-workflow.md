---
description: "开发工作流：计划、TDD、评审、提交流水线"
alwaysApply: true
---
# 开发工作流 (Development Workflow)

> 本规则是对 Git 工作流 (Git workflow) 规则的扩展，涵盖了在进行 Git 操作之前发生的完整功能开发流程。

功能实现工作流 (Feature Implementation Workflow) 描述了从计划、TDD、代码评审到 Git 提交的完整开发流水线。

## 功能实现工作流 (Feature Implementation Workflow)

1. **计划先行 (Plan First)**
   - 使用 **planner** 智能体 (Agent) 创建实现计划
   - 识别依赖项和风险
   - 将任务分解为多个阶段

2. **测试驱动开发 (TDD Approach)**
   - 使用 **tdd-guide** 智能体 (Agent)
   - 先编写测试 (红 RED)
   - 实现代码以通过测试 (绿 GREEN)
   - 重构 (优化 IMPROVE)
   - 验证 80% 以上的覆盖率

3. **代码评审 (Code Review)**
   - 编写代码后立即使用 **code-reviewer** 智能体 (Agent)
   - 解决 严重 (CRITICAL) 和 高 (HIGH) 级别的问题
   - 尽可能修复 中 (MEDIUM) 级别的问题

4. **提交与推送 (Commit & Push)**
   - 编写详细的提交信息 (Commit message)
   - 遵循约定式提交 (Conventional Commits) 格式
   - 请参阅 Git 工作流 (Git workflow) 规则，了解提交信息格式和 PR 流程
