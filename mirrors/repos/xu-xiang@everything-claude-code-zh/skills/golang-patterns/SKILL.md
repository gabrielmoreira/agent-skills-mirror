---
name: golang-patterns
description: 编写稳健、高效且易于维护的 Go 应用程序的惯用模式、最佳实践和约定。
origin: ECC
---

# Go 开发模式 (Go Development Patterns)

构建稳健、高效且易于维护的应用程序的惯用 Go 模式和最佳实践。

## 激活时机

- 编写新的 Go 代码时
- 评审 Go 代码时
- 重构现有 Go 代码时
- 设计 Go 包/模块时

## 核心原则

### 1. 简单与清晰

Go 倾向于简单而非巧妙。代码应当直观且易于阅读。

```go
// 推荐：清晰且直接
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// 不推荐：过于巧妙
func GetUser(id string) (*User, error) {
    return func() (*User, error) {
        if u, e := db.FindUser(id); e == nil {
            return u, nil
        } else {
            return nil, e
        }
    }()
}
```

### 2. 使“零值”有用

设计类型时，使其零值（Zero Value）在无需显式初始化的情况下即可立即使用。

```go
// 推荐：零值即有用
type Counter struct {
    mu    sync.Mutex
    count int // 零值为 0，可直接使用
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock()
}

// 推荐：bytes.Buffer 的零值即可工作
var buf bytes.Buffer
buf.WriteString("hello")

// 不推荐：需要显式初始化
type BadCounter struct {
    counts map[string]int // nil map 会引发 panic
}
```

### 3. 接受接口，返回结构体

函数应当接受接口（Interface）参数并返回具体类型（Concrete types/Structs）。

```go
// 推荐：接受接口，返回具体类型
func ProcessData(r io.Reader) (*Result, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return nil, err
    }
    return &Result{Data: data}, nil
}

// 不推荐：返回接口（无谓地隐藏了实现细节）
func ProcessData(r io.Reader) (io.Reader, error) {
    // ...
}
```

## 错误处理模式 (Error Handling Patterns)

### 带有上下文的错误包装

```go
// 推荐：使用上下文包装错误
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("load config %s: %w", path, err)
    }

    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config %s: %w", path, err)
    }

    return &cfg, nil
}
```

### 自定义错误类型

```go
// 定义领域特定的错误
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// 常见情况的哨兵错误 (Sentinel errors)
var (
    ErrNotFound     = errors.New("resource not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)
```

### 使用 errors.Is 和 errors.As 进行错误检查

```go
func HandleError(err error) {
    // 检查特定错误
    if errors.Is(err, sql.ErrNoRows) {
        log.Println("No records found")
        return
    }

    // 检查错误类型
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        log.Printf("Validation error on field %s: %s",
            validationErr.Field, validationErr.Message)
        return
    }

    // 未知错误
    log.Printf("Unexpected error: %v", err)
}
```

### 绝不忽略错误

```go
// 不推荐：使用空白标识符忽略错误
result, _ := doSomething()

// 推荐：处理错误，或显式说明为何忽略是安全的
result, err := doSomething()
if err != nil {
    return err
}

// 可接受：当错误确实无关紧要时（少见）
_ = writer.Close() // 尽力而为的清理，错误已在别处记录
```

## 并发模式 (Concurrency Patterns)

### 工作池 (Worker Pool)

```go
func WorkerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }

    wg.Wait()
    close(results)
}
```

### 使用 Context 处理取消和超时

```go
func FetchWithTimeout(ctx context.Context, url string) ([]byte, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("fetch %s: %w", url, err)
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}
```

### 优雅停机 (Graceful Shutdown)

```go
func GracefulShutdown(server *http.Server) {
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    <-quit
    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := server.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited")
}
```

### 使用 errgroup 协调协程

```go
import "golang.org/x/sync/errgroup"

func FetchAll(ctx context.Context, urls []string) ([][]byte, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([][]byte, len(urls))

    for i, url := range urls {
        i, url := i, url // 捕获循环变量
        g.Go(func() error {
            data, err := FetchWithTimeout(ctx, url)
            if err != nil {
                return err
            }
            results[i] = data
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

### 避免协程泄漏 (Goroutine Leaks)

```go
// 不推荐：如果 context 被取消，协程会泄漏
func leakyFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte)
    go func() {
        data, _ := fetch(url)
        ch <- data // 如果没有接收者，将永久阻塞
    }()
    return ch
}

// 推荐：正确处理取消
func safeFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte, 1) // 使用缓冲通道
    go func() {
        data, err := fetch(url)
        if err != nil {
            return
        }
        select {
        case ch <- data:
        case <-ctx.Done():
        }
    }()
    return ch
}
```

## 接口设计 (Interface Design)

### 小而专注的接口

```go
// 推荐：单方法接口
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// 根据需要组合接口
type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

### 在使用处定义接口

```go
// 在消费者包中定义，而不是在提供者包中
package service

// UserStore 定义了此服务所需的功能
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type Service struct {
    store UserStore
}

// 具体实现在另一个包中
// 它不需要显式感知这个接口
```

### 通过类型断言支持可选行为

```go
type Flusher interface {
    Flush() error
}

func WriteAndFlush(w io.Writer, data []byte) error {
    if _, err := w.Write(data); err != nil {
        return err
    }

    // 如果支持则刷新
    if f, ok := w.(Flusher); ok {
        return f.Flush()
    }
    return nil
}
```

## 包组织 (Package Organization)

### 标准项目布局

```text
myproject/
├── cmd/
│   └── myapp/
│       └── main.go           # 入口点
├── internal/
│   ├── handler/              # HTTP 处理函数
│   ├── service/              # 业务逻辑
│   ├── repository/           # 数据访问
│   └── config/               # 配置
├── pkg/
│   └── client/               # 公共 API 客户端
├── api/
│   └── v1/                   # API 定义 (proto, OpenAPI)
├── testdata/                 # 测试固件
├── go.mod
├── go.sum
└── Makefile
```

### 包命名

```go
// 推荐：简短、小写、无下划线
package http
package json
package user

// 不推荐：冗长、混合大小写或冗余
package httpHandler
package json_parser
package userService // 冗余的 'Service' 后缀
```

### 避免包级状态

```go
// 不推荐：全局可变状态
var db *sql.DB

func init() {
    db, _ = sql.Open("postgres", os.Getenv("DATABASE_URL"))
}

// 推荐：依赖注入 (Dependency injection)
type Server struct {
    db *sql.DB
}

func NewServer(db *sql.DB) *Server {
    return &Server{db: db}
}
```

## 结构体设计 (Struct Design)

### 函数式选项模式 (Functional Options Pattern)

```go
type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

func WithLogger(l *log.Logger) Option {
    return func(s *Server) {
        s.logger = l
    }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // 默认值
        logger:  log.Default(),    // 默认值
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// 使用示例
server := NewServer(":8080",
    WithTimeout(60*time.Second),
    WithLogger(customLogger),
)
```

### 通过嵌套实现组合 (Embedding)

```go
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type Server struct {
    *Logger // 嵌套 - Server 获得了 Log 方法
    addr    string
}

func NewServer(addr string) *Server {
    return &Server{
        Logger: &Logger{prefix: "SERVER"},
        addr:   addr,
    }
}

// 使用示例
s := NewServer(":8080")
s.Log("Starting...") // 调用了嵌入的 Logger.Log
```

## 内存与性能 (Memory and Performance)

### 当大小已知时预分配切片

```go
// 不推荐：切片会多次扩容
func processItems(items []Item) []Result {
    var results []Result
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}

// 推荐：单次分配内存
func processItems(items []Item) []Result {
    results := make([]Result, 0, len(items))
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}
```

### 对频繁分配使用 sync.Pool

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func ProcessRequest(data []byte) []byte {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    buf.Write(data)
    // 处理...
    return buf.Bytes()
}
```

### 避免在循环中进行字符串拼接

```go
// 不推荐：产生大量字符串分配
func join(parts []string) string {
    var result string
    for _, p := range parts {
        result += p + ","
    }
    return result
}

// 推荐：使用 strings.Builder 进行单次分配
func join(parts []string) string {
    var sb strings.Builder
    for i, p := range parts {
        if i > 0 {
            sb.WriteString(",")
        }
        sb.WriteString(p)
    }
    return sb.String()
}

// 最佳：使用标准库
func join(parts []string) string {
    return strings.Join(parts, ",")
}
```

## Go 工具链集成

### 常用命令

```bash
# 构建并运行
go build ./...
go run ./cmd/myapp

# 测试
go test ./...
go test -race ./...
go test -cover ./...

# 静态分析
go vet ./...
staticcheck ./...
golangci-lint run

# 模块管理
go mod tidy
go mod verify

# 格式化
gofmt -w .
goimports -w .
```

### 推荐的 Linter 配置 (.golangci.yml)

```yaml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gofmt
    - goimports
    - misspell
    - unconvert
    - unparam

linters-settings:
  errcheck:
    check-type-assertions: true
  govet:
    check-shadowing: true

issues:
  exclude-use-default: false
```

## 快速参考：Go 惯用语 (Go Idioms)

| 惯用语 | 描述 |
|-------|-------------|
| 接受接口，返回结构体 | 函数接受接口参数，返回具体类型 |
| 错误即值 (Errors are values) | 将错误视为一等公民，而非异常 |
| 不要通过共享内存来通信 | 使用通道 (Channels) 在协程间进行协调 |
| 使零值有用 | 类型在未显式初始化时也应能工作 |
| 少许复制好过少许依赖 | 避免不必要的外部依赖 |
| 清晰优于巧妙 | 优先考虑可读性而非代码的巧妙性 |
| gofmt 并非谁的最爱，却是每个人的朋友 | 始终使用 gofmt/goimports 进行格式化 |
| 尽早返回 | 优先处理错误，保持“快乐路径”不缩进 |

## 应避免的反模式 (Anti-Patterns)

```go
// 不推荐：在长函数中使用裸返回 (Naked returns)
func process() (result int, err error) {
    // ... 50 行代码 ...
    return // 返回了什么？
}

// 不推荐：使用 panic 进行流程控制
func GetUser(id string) *User {
    user, err := db.Find(id)
    if err != nil {
        panic(err) // 不要这样做
    }
    return user
}

// 不推荐：在结构体中传递 context
type Request struct {
    ctx context.Context // Context 应当是第一个参数
    ID  string
}

// 推荐：Context 作为第一个参数
func ProcessRequest(ctx context.Context, id string) error {
    // ...
}

// 不推荐：混合使用值接收者和指针接收者
type Counter struct{ n int }
func (c Counter) Value() int { return c.n }    // 值接收者
func (c *Counter) Increment() { c.n++ }        // 指针接收者
// 选择一种风格并保持一致
```

**记住**：Go 代码应当以最好的方式显得“无聊”——它是可预测的、一致的且易于理解的。如有疑问，请保持简单。
