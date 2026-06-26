---
description: "Git 工作流：规范化提交（Conventional Commits），PR 流程"
alwaysApply: true
---
# Git 工作流（Git Workflow）

## 提交信息格式（Commit Message Format）
```
<type>: <description>

<optional body>
```

类型（Types）：feat, fix, refactor, docs, test, chore, perf, ci

注：归属信息已通过 ~/.claude/settings.json 全局禁用。

## 合并请求工作流（Pull Request Workflow）

创建 PR 时：
1. 分析完整提交历史（不仅是最新的一次提交）
2. 使用 `git diff [base-branch]...HEAD` 查看所有变更
3. 撰写全面的 PR 摘要
4. 包含带有待办事项（TODOs）的测试计划
5. 如果是新分支，推送时使用 `-u` 参数

> 在进行 Git 操作之前的完整开发流程（规划、TDD、代码审查），
> 请参阅开发工作流规则。
