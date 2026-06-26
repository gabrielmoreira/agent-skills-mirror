---
description: "扩展通用规则的 Go 编码风格"
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---
# Go 编码风格 (Go Coding Style)

> 本文件是对通用编码风格规则的扩展，涵盖了 Go 语言特有的内容。

## 格式化 (Formatting)

- 强制使用 **gofmt** 和 **goimports** —— 不进行代码风格争论

## 设计原则 (Design Principles)

- 接收接口（Accept interfaces），返回结构体（return structs）
- 保持接口（interfaces）精简（建议 1-3 个方法）

## 错误处理 (Error Handling)

始终使用上下文包装错误：

```go
if err != nil {
    return fmt.Errorf("failed to create user: %w", err)
}
```

## 参考 (Reference)

有关完整的 Go 惯用法和模式（Patterns），请参阅技能（Skill）：`golang-patterns`。
