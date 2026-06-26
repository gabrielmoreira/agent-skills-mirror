---
description: "钩子系统（Hooks system）：类型、自动确认权限、TodoWrite 最佳实践"
alwaysApply: true
---
# 钩子系统（Hooks System）

## 钩子类型（Hook Types）

- **PreToolUse**：工具执行前（校验、参数修改）
- **PostToolUse**：工具执行后（自动格式化、检查）
- **Stop**：会话结束时（最终验证）

## 自动确认权限（Auto-Accept Permissions）

谨慎使用：
- 对于受信任且定义良好的计划，建议启用
- 对于探索性工作，建议禁用
- 严禁使用 `dangerously-skip-permissions` 标志（flag）
- 建议改为在 `~/.claude.json` 中配置 `allowedTools`

## TodoWrite 最佳实践（TodoWrite Best Practices）

使用 `TodoWrite` 工具（Tool）：
- 追踪多步骤任务的进度
- 验证对指令的理解
- 实现实时引导（Real-time steering）
- 展示细粒度的实现步骤

待办事项列表（Todo list）可揭示：
- 步骤顺序错误
- 遗漏项
- 多余的不必要项
- 粒度不正确
- 误解需求
