---
description: "扩展通用规则的 Go 钩子（Hooks）"
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---
# Go 钩子（Hooks）

> 本文件为通用钩子规则（Hooks）增加了 Go 语言特定的内容。

## 工具执行后钩子（PostToolUse Hooks）

在 `~/.claude/settings.json` 中配置：

- **gofmt/goimports**: 在编辑后自动格式化 `.go` 文件
- **go vet**: 在编辑 `.go` 文件后运行静态分析
- **staticcheck**: 在修改的包上运行扩展静态检查
