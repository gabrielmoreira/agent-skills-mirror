---
description: "扩展通用规则的 TypeScript 钩子（Hooks）"
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
alwaysApply: false
---
# TypeScript/JavaScript 钩子（Hooks）

> 本文件使用 TypeScript/JavaScript 特定内容扩展了通用钩子（Hooks）规则。

## 工具调用后钩子（PostToolUse Hooks）

在 `~/.claude/settings.json` 中配置：

- **Prettier**：在编辑后自动格式化 JS/TS 文件
- **TypeScript 检查（TypeScript check）**：编辑 `.ts`/`.tsx` 文件后运行 `tsc`
- **console.log 警告**：针对已编辑文件中的 `console.log` 发出警告

## 停止钩子（Stop Hooks）

- **console.log 审计**：在会话结束前检查所有已修改文件中的 `console.log`
