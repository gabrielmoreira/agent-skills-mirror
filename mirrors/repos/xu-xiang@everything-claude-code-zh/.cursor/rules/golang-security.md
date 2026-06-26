---
description: "Go 安全性规则，扩展了通用安全性内容"
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---
# Go 安全性 (Go Security)

> 本文件在通用安全性规则的基础上，扩展了针对 Go 语言的特定内容。

## 密钥管理 (Secret Management)

```go
apiKey := os.Getenv("OPENAI_API_KEY")
if apiKey == "" {
    log.Fatal("OPENAI_API_KEY not configured")
}
```

## 安全扫描 (Security Scanning)

- 使用 **gosec** 进行静态安全分析：
  ```bash
  gosec ./...
  ```

## 上下文与超时 (Context & Timeouts)

始终使用 `context.Context` 进行超时控制：

```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```
