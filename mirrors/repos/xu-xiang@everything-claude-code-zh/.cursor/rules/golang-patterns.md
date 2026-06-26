---
description: "Go 模式（Go patterns），扩展了通用规则（common rules）"
globs: ["**/*.go", "**/go.mod", "**/go.sum"]
alwaysApply: false
---
# Go 模式（Go Patterns）

> 本文件扩展了通用模式规则，包含了 Go 特有的内容。

## 函数式选项（Functional Options）

```go
type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

## 小接口（Small Interfaces）

在接口被使用的地方定义它们，而不是在实现它们的地方定义。

## 依赖注入（Dependency Injection）

使用构造函数（Constructor functions）来注入依赖：

```go
func NewUserService(repo UserRepository, logger Logger) *UserService {
    return &UserService{repo: repo, logger: logger}
}
```

## 参考（Reference）

请参阅技能（Skill）：`golang-patterns` 以获取全面的 Go 模式，包括并发、错误处理和包组织。
