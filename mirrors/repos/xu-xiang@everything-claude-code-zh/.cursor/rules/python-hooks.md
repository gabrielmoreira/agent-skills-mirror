---
description: "扩展通用规则的 Python 钩子（Hooks）"
globs: ["**/*.py", "**/*.pyi"]
alwaysApply: false
---
# Python 钩子（Hooks）

> 本文件使用 Python 特定内容扩展了通用钩子（Hooks）规则。

## PostToolUse 钩子（Hooks）

在 `~/.claude/settings.json` 中配置：

- **black/ruff**: 编辑后自动格式化 `.py` 文件
- **mypy/pyright**: 编辑 `.py` 文件后运行类型检查

## 警告（Warnings）

- 针对已编辑文件中的 `print()` 语句发出警告（应使用 `logging` 模块代替）
