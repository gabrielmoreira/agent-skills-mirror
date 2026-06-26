---
name: golang-patterns
description: 构建健壮、高效且可维护 Go 应用程序的惯用法（Idiomatic Go）、最佳实践与规范。
---

# Go 开发模式（Go Development Patterns）

用于构建健壮、高效且可维护应用程序的惯用法与最佳实践。

## 何时启用

- 编写新的 Go 代码时
- 评审 Go 代码时
- 重构现有 Go 代码时
- 设计 Go 软件包（Package）/ 模块（Module）时

## 核心原则

### 1. 简单与清晰

Go 倾向于简单而非巧妙。代码应当直观且易读。

```go
// Good: 清晰且直接
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// Bad: 过于巧妙
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

### 2. 让零值（Zero Value）变得有用

在设计类型时，应确保其零值无需显式初始化即可直接使用。

```go
// Good: 零值很有用
type Counter struct {
    mu    sync.Mutex
    count int // 零值为 0，可直接使用
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock()
}

// Good: bytes.Buffer 可以直接使用零值
var buf bytes.Buffer
buf.WriteString("hello")

// Bad: 需要初始化
type BadCounter struct {
    counts map[string]int // nil map 会引发 panic
}
```

### 3. 接受接口（Interface），返回结构体（Struct）

函数应当接收接口参数并返回具体类型。

```go
// Good: 接收接口，返回具体类型
func ProcessData(r io.Reader) (*Result, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return nil, err
    }
    return &Result{Data: data}, nil
}

// Bad: 返回接口（无谓地隐藏了实现细节）
func ProcessData(r io.Reader) (io.Reader, error) {
    // ...
}
```

## 错误处理模式（Error Handling Patterns）

### 带有上下文的错误包装（Error Wrapping）

```go
// Good: 使用上下文包装错误
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
// 定义领域特定错误
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// 常见情况的哨兵错误（Sentinel errors）
var (
    ErrNotFound     = errors.New("resource not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)
```

### 使用 errors.Is 与 errors.As 进行错误检查

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

### 永不忽略错误

```go
// Bad: 使用空白标识符忽略错误
result, _ := doSomething()

// Good: 处理错误或显式记录为何可以安全忽略
result, err := doSomething()
if err != nil {
    return err
}

// Acceptable: 当错误确实无关紧要时（罕见）
_ = writer.Close() // 尽力清理，错误已在别处记录
```

## 并发处理模式（Concurrency Patterns）

### 工作池（Worker Pool）

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

### 用于取消（Cancellation）与超时（Timeout）的上下文（Context）

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

### 优雅停机（Graceful Shutdown）

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

### 用于协同协程的 errgroup

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

### 避免协程（Goroutine）泄漏

```go
// Bad: 如果 context 被取消，会发生协程泄漏
func leakyFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte)
    go func() {
        data, _ := fetch(url)
        ch <- data // 如果没有接收者，将永远阻塞
    }()
    return ch
}

// Good: 正确处理取消操作
func safeFetch(ctx context.Context, url string) <-chan []byte {
    ch := make(chan []byte, 1) // 有缓冲通道
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

## 接口设计（Interface Design）

### 小而精简的接口

```go
// Good: 单方法接口
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

### 在使用者处定义接口

```go
// 在消费者包中定义，而不是在提供者包中
package service

// UserStore 定义了该服务所需的功能
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type Service struct {
    store UserStore
}

// 具体实现可以在另一个包中
// 它不需要知道这个接口的存在
```

### 使用类型断言（Type Assertion）实现可选行为

```go
type Flusher interface {
    Flush() error
}

func WriteAndFlush(w io.Writer, data []byte) error {
    if _, err := w.Write(data); err != nil {
        return err
    }

    // 如果支持，则调用 Flush
    if f, ok := w.(Flusher); ok {
        return f.Flush()
    }
    return nil
}
```

## 包（Package）结构

### 标准项目布局

```text
myproject/
├── cmd/
│   └── myapp/
│       └── main.go           # 入口点
├── internal/
│   ├── handler/              # HTTP 处理器
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
// Good: 短小、全小写、无下划线
package http
package json
package user

// Bad: 冗长、大小写混合或冗余
package httpHandler
package json_parser
package userService // 冗余的 'Service' 后缀
```

### 避免包级状态

```go
// Bad: 全局可变状态
var db *sql.DB

func init() {
    db, _ = sql.Open("postgres", os.Getenv("DATABASE_URL"))
}

// Good: 依赖注入
type Server struct {
    db *sql.DB
}

func NewServer(db *sql.DB) *Server {
    return &Server{db: db}
}
```

## 结构体设计

### 函数式选项模式（Functional Options Pattern）

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

### 用于组合（Composition）的嵌入（Embedding）

```go
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type Server struct {
    *Logger // 嵌入 - Server 获得了 Log 方法
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
s.Log("Starting...") // 调用嵌入的 Logger.Log
```

## 内存与性能

### 已知大小时预分配切片（Slice）

```go
// Bad: 切片多次扩容
func processItems(items []Item) []Result {
    var results []Result
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}

// Good: 单次分配内存
func processItems(items []Item) []Result {
    results := make([]Result, 0, len(items))
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}
```

### 使用 sync.Pool 处理频繁分配

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
    // 处理过程...
    return buf.Bytes()
}
```

### 避免在循环中连接字符串

```go
// Bad: 产生大量字符串内存分配
func join(parts []string) string {
    var result string
    for _, p := range parts {
        result += p + ","
    }
    return result
}

// Good: 使用 strings.Builder 进行单次分配
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

// Best: 使用标准库
func join(parts []string) string {
    return strings.Join(parts, ",")
}
```

## Go 工具链集成

### 基本命令

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

### 推荐的 Linter 配置（.golangci.yml）

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

## 快速参考：Go 惯用法

| 惯用法 | 说明 |
|-------|-------------|
| 接受接口，返回结构体 | 函数应当接收接口参数并返回具体类型 |
| 错误即值 | 将错误视为一等公民（First-class Value），而非异常 |
| 不要通过共享内存来通信 | 使用通道（Channel）进行协程间的协调 |
| 让零值变得有用 | 类型应在无显式初始化的情况下即可正常工作 |
| 少量的拷贝好过少量的依赖 | 避免不必要的外部依赖 |
| 清晰好过巧妙 | 可读性优先于奇技淫巧 |
| gofmt 虽然不是任何人的最爱，但它是每个人的朋友 | 始终使用 gofmt/goimports 进行格式化 |
| 尽早返回 | 优先处理错误，使快乐路径（Happy Path）保持较浅的缩进 |

## 应避免的反模式（Anti-patterns）

```go
// Bad: 长函数中的裸返回（Naked returns）
func process() (result int, err error) {
    // ... 50 行代码 ...
    return // 返回了什么？
}

// Bad: 使用 panic 进行控制流管理
func GetUser(id string) *User {
    user, err := db.Find(id)
    if err != nil {
        panic(err) // 不要这样做
    }
    return user
}

// Bad: 在结构体中传递 context
type Request struct {
    ctx context.Context // context 应该是第一个参数
    ID  string
}

// Good: context 作为第一个参数
func ProcessRequest(ctx context.Context, id string) error {
    // ...
}

// Bad: 混合使用值接收者和指针接收者
type Counter struct{ n int }
func (c Counter) Value() int { return c.n }    // 值接收者
func (c *Counter) Increment() { c.n++ }        // 指针接收者
// 请选择一种风格并保持一致
```

**请记住**：Go 代码在最好的意义上应当是“枯燥”的 —— 可预测、一致且易于理解。如有疑疑虑，请保持简单。
