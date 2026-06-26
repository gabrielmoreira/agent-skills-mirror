---
description: "扩展通用规则的 Swift 钩子（Hooks）"
globs: ["**/*.swift", "**/Package.swift"]
alwaysApply: false
---
# Swift 钩子（Hooks）

> 本文件使用 Swift 特有内容扩展了通用钩子（Hooks）规则。

## PostToolUse 钩子（Hooks）

在 `~/.claude/settings.json` 中配置：

- **SwiftFormat**: 编辑后自动格式化 `.swift` 文件
- **SwiftLint**: 编辑 `.swift` 文件后运行 lint 检查
- **swift build**: 编辑后对已修改的包（Packages）进行类型检查

## 警告

标记 `print()` 语句 —— 在生产代码中请改用 `os.Logger` 或结构化日志。
