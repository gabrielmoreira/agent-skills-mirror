---
description: "Go 测试 (Testing) 扩展通用规则"
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---
# Go 测试 (Go Testing)

> 本文件是对通用测试规则的 Go 语言特定内容的扩展。

## 框架 (Framework)

使用标准的 `go test` 与 **表格驱动测试 (table-driven tests)**。

## 竞态检测 (Race Detection)

始终使用 `-race` 标志运行：

```bash
go test -race ./...
```

## 覆盖率 (Coverage)

```bash
go test -cover ./...
```

## 参考 (Reference)

请参阅技能 (Skill)：`golang-testing` 以了解详细的 Go 测试模式与助手。
