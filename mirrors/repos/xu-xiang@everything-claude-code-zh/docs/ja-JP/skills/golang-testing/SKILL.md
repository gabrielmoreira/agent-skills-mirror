---
name: golang-testing
description: 保证测试驱动开发与 Go 代码高质量的全面测试策略。
---

# Go 测试 (Go Testing)

保证测试驱动开发（TDD）与 Go 代码高质量的全面测试策略。

## 何时激活

- 编写新的 Go 代码时
- 审查（Review）Go 代码时
- 改进现有测试时
- 提高测试覆盖率（Test Coverage）时
- 调试与修复 Bug 时

## 核心原则

### 1. 测试驱动开发（TDD）工作流

遵循编写失败测试、实现代码、重构（Refactor）的循环。

```go
// 1. 编写测试（失败）
func TestCalculateTotal(t *testing.T) {
    total := CalculateTotal([]float64{10.0, 20.0, 30.0})
    want := 60.0
    if total != want {
        t.Errorf("got %f, want %f", total, want)
    }
}

// 2. 实现代码（使测试通过）
func CalculateTotal(prices []float64) float64 {
    var total float64
    for _, price := range prices {
        total += price
    }
    return total
}

// 3. 重构
// 在不破坏测试的前提下改进代码
```

### 2. 表格驱动测试 (Table-Driven Tests)

体系化地测试多个用例。

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"mixed signs", -2, 3, 1},
        {"zeros", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d; want %d",
                    tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

### 3. 子测试 (Subtests)

使用子测试组织逻辑测试。

```go
func TestUser(t *testing.T) {
    t.Run("validation", func(t *testing.T) {
        t.Run("empty email", func(t *testing.T) {
            user := User{Email: ""}
            if err := user.Validate(); err == nil {
                t.Error("expected validation error")
            }
        })

        t.Run("valid email", func(t *testing.T) {
            user := User{Email: "test@example.com"}
            if err := user.Validate(); err != nil {
                t.Errorf("unexpected error: %v", err)
            }
        })
    })

    t.Run("serialization", func(t *testing.T) {
        // 另一个测试组
    })
}
```

## 测试组织

### 文件结构 (File Structure)

```text
mypackage/
├── user.go
├── user_test.go          # 单元测试
├── integration_test.go   # 集成测试
├── testdata/             # 测试固件 (Test Fixtures)
│   ├── valid_user.json
│   └── invalid_user.json
└── export_test.go        # 为内部测试提供的私有导出
```

### 测试包 (Test Packages)

```go
// user_test.go - 同一包内（白盒测试）
package user

func TestInternalFunction(t *testing.T) {
    // 可以测试内部逻辑
}

// user_external_test.go - 外部包（黑盒测试）
package user_test

import "myapp/user"

func TestPublicAPI(t *testing.T) {
    // 仅测试公开 API
}
```

## 断言（Assertions）与辅助函数（Helpers）

### 基本断言

```go
func TestBasicAssertions(t *testing.T) {
    // 相等性
    got := Calculate()
    want := 42
    if got != want {
        t.Errorf("got %d, want %d", got, want)
    }

    // 错误检查
    _, err := Process()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }

    // nil 检查
    result := GetResult()
    if result == nil {
        t.Fatal("expected non-nil result")
    }
}
```

### 自定义辅助函数

```go
// 标记为 Helper（不会在堆栈跟踪中显示）
func assertEqual(t *testing.T, got, want interface{}) {
    t.Helper()
    if got != want {
        t.Errorf("got %v, want %v", got, want)
    }
}

func assertNoError(t *testing.T, err error) {
    t.Helper()
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}

// 使用示例
func TestWithHelpers(t *testing.T) {
    result, err := Process()
    assertNoError(t, err)
    assertEqual(t, result.Status, "success")
}
```

### 深度一致性检查（Deep Equality Check）

```go
import "reflect"

func assertDeepEqual(t *testing.T, got, want interface{}) {
    t.Helper()
    if !reflect.DeepEqual(got, want) {
        t.Errorf("got %+v, want %+v", got, want)
    }
}

func TestStructEquality(t *testing.T) {
    got := User{Name: "Alice", Age: 30}
    want := User{Name: "Alice", Age: 30}
    assertDeepEqual(t, got, want)
}
```

## 模拟（Mocking）与桩（Stubs）

### 基于接口的模拟

```go
// 生产代码
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type UserService struct {
    store UserStore
}

// 测试代码
type MockUserStore struct {
    users map[string]*User
    err   error
}

func (m *MockUserStore) GetUser(id string) (*User, error) {
    if m.err != nil {
        return nil, m.err
    }
    return m.users[id], nil
}

func (m *MockUserStore) SaveUser(user *User) error {
    if m.err != nil {
        return m.err
    }
    m.users[user.ID] = user
    return nil
}

// 测试
func TestUserService(t *testing.T) {
    mock := &MockUserStore{
        users: make(map[string]*User),
    }
    service := &UserService{store: mock}

    // 测试服务...
}
```

### 时间模拟

```go
// 生产代码 - 使时间可注入
type TimeProvider interface {
    Now() time.Time
}

type RealTime struct{}

func (RealTime) Now() time.Time {
    return time.Now()
}

type Service struct {
    time TimeProvider
}

// 测试代码
type MockTime struct {
    current time.Time
}

func (m MockTime) Now() time.Time {
    return m.current
}

func TestTimeDependent(t *testing.T) {
    mockTime := MockTime{
        current: time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
    }
    service := &Service{time: mockTime}

    // 在固定时间内测试...
}
```

### HTTP 客户端模拟

```go
type HTTPClient interface {
    Do(req *http.Request) (*http.Response, error)
}

type MockHTTPClient struct {
    response *http.Response
    err      error
}

func (m *MockHTTPClient) Do(req *http.Request) (*http.Response, error) {
    return m.response, m.err
}

func TestAPICall(t *testing.T) {
    mockClient := &MockHTTPClient{
        response: &http.Response{
            StatusCode: 200,
            Body:       io.NopCloser(strings.NewReader(`{"status":"ok"}`)),
        },
    }

    api := &APIClient{client: mockClient}
    // 测试 API 客户端...
}
```

## 测试 HTTP 处理程序（Handlers）

### 使用 httptest

```go
func TestHandler(t *testing.T) {
    handler := http.HandlerFunc(MyHandler)

    req := httptest.NewRequest("GET", "/users/123", nil)
    rec := httptest.NewRecorder()

    handler.ServeHTTP(rec, req)

    // 检查状态码
    if rec.Code != http.StatusOK {
        t.Errorf("got status %d, want %d", rec.Code, http.StatusOK)
    }

    // 检查响应体
    var response map[string]interface{}
    if err := json.NewDecoder(rec.Body).Decode(&response); err != nil {
        t.Fatalf("failed to decode response: %v", err)
    }

    if response["id"] != "123" {
        t.Errorf("got id %v, want 123", response["id"])
    }
}
```

### 测试中间件（Middleware）

```go
func TestAuthMiddleware(t *testing.T) {
    // 虚拟处理程序
    nextHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    // 用中间件包装
    handler := AuthMiddleware(nextHandler)

    tests := []struct {
        name       string
        token      string
        wantStatus int
    }{
        {"valid token", "valid-token", http.StatusOK},
        {"invalid token", "invalid", http.StatusUnauthorized},
        {"no token", "", http.StatusUnauthorized},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req := httptest.NewRequest("GET", "/", nil)
            if tt.token != "" {
                req.Header.Set("Authorization", "Bearer "+tt.token)
            }
            rec := httptest.NewRecorder()

            handler.ServeHTTP(rec, req)

            if rec.Code != tt.wantStatus {
                t.Errorf("got status %d, want %d", rec.Code, tt.wantStatus)
            }
        })
    }
}
```

### 测试服务器

```go
func TestAPIIntegration(t *testing.T) {
    // 创建测试服务器
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(map[string]string{
            "message": "hello",
        })
    }))
    defer server.Close()

    // 执行真实的 HTTP 请求
    resp, err := http.Get(server.URL)
    if err != nil {
        t.Fatalf("request failed: %v", err)
    }
    defer resp.Body.Close()

    // 验证响应
    var result map[string]string
    json.NewDecoder(resp.Body).Decode(&result)

    if result["message"] != "hello" {
        t.Errorf("got %s, want hello", result["message"])
    }
}
```

## 数据库测试

### 使用事务实现测试隔离

```go
func TestUserRepository(t *testing.T) {
    db := setupTestDB(t)
    defer db.Close()

    tests := []struct {
        name string
        fn   func(*testing.T, *sql.DB)
    }{
        {"create user", testCreateUser},
        {"find user", testFindUser},
        {"update user", testUpdateUser},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            tx, err := db.Begin()
            if err != nil {
                t.Fatal(err)
            }
            defer tx.Rollback() // 测试后回滚

            tt.fn(t, tx)
        })
    }
}
```

### 测试固件 (Test Fixtures)

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()

    db, err := sql.Open("postgres", "postgres://localhost/test")
    if err != nil {
        t.Fatalf("failed to connect: %v", err)
    }

    // 迁移架构
    if err := runMigrations(db); err != nil {
        t.Fatalf("migrations failed: %v", err)
    }

    return db
}

func seedTestData(t *testing.T, db *sql.DB) {
    t.Helper()

    fixtures := []string{
        `INSERT INTO users (id, email) VALUES ('1', 'test@example.com')`,
        `INSERT INTO posts (id, user_id, title) VALUES ('1', '1', 'Test Post')`,
    }

    for _, query := range fixtures {
        if _, err := db.Exec(query); err != nil {
            t.Fatalf("failed to seed data: %v", err)
        }
    }
}
```

## 基准测试（Benchmarks）

### 基本基准测试

```go
func BenchmarkCalculation(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Calculate(100)
    }
}

// 报告内存分配情况
func BenchmarkWithAllocs(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        ProcessData([]byte("test data"))
    }
}
```

### 子基准测试

```go
func BenchmarkEncoding(b *testing.B) {
    data := generateTestData()

    b.Run("json", func(b *testing.B) {
        b.ReportAllocs()
        for i := 0; i < b.N; i++ {
            json.Marshal(data)
        }
    })

    b.Run("gob", func(b *testing.B) {
        b.ReportAllocs()
        var buf bytes.Buffer
        enc := gob.NewEncoder(&buf)
        b.ResetTimer()
        for i := 0; i < b.N; i++ {
            enc.Encode(data)
            buf.Reset()
        }
    })
}
```

### 基准测试对比

```go
// 运行: go test -bench=. -benchmem
func BenchmarkStringConcat(b *testing.B) {
    b.Run("operator", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            _ = "hello" + " " + "world"
        }
    })

    b.Run("fmt.Sprintf", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            _ = fmt.Sprintf("%s %s", "hello", "world")
        }
    })

    b.Run("strings.Builder", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            var sb strings.Builder
            sb.WriteString("hello")
            sb.WriteString(" ")
            sb.WriteString("world")
            _ = sb.String()
        }
    })
}
```

## 模糊测试（Fuzzing Tests）

### 基本模糊测试（Go 1.18+）

```go
func FuzzParseInput(f *testing.F) {
    // 种子语料库
    f.Add("hello")
    f.Add("world")
    f.Add("123")

    f.Fuzz(func(t *testing.T, input string) {
        // 确保解析不会引发 panic
        result, err := ParseInput(input)

        // 确保即使有错误，结果不为 nil 或具有一致性
        if err == nil && result == nil {
            t.Error("got nil result with no error")
        }
    })
}
```

### 更复杂的模糊测试

```go
func FuzzJSONParsing(f *testing.F) {
    f.Add([]byte(`{"name":"test","age":30}`))
    f.Add([]byte(`{"name":"","age":0}`))

    f.Fuzz(func(t *testing.T, data []byte) {
        var user User
        err := json.Unmarshal(data, &user)

        // 如果 JSON 解码成功，理应可以再次编码
        if err == nil {
            _, err := json.Marshal(user)
            if err != nil {
                t.Errorf("marshal failed after successful unmarshal: %v", err)
            }
        }
    })
}
```

## 测试覆盖率（Test Coverage）

### 运行并查看覆盖率

```bash
# 运行测试并生成 HTML 报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# 显示每个包的覆盖率
go test -cover ./...

# 详细覆盖率
go test -coverprofile=coverage.out -covermode=atomic ./...
```

### 覆盖率最佳实践

```go
// Good: 易于测试的代码
func ProcessData(data []byte) (Result, error) {
    if len(data) == 0 {
        return Result{}, ErrEmptyData
    }

    // 每个分支均可测试
    if isValid(data) {
        return parseValid(data)
    }
    return parseInvalid(data)
}

// 对应的测试涵盖所有分支
func TestProcessData(t *testing.T) {
    tests := []struct {
        name    string
        data    []byte
        wantErr bool
    }{
        {"empty data", []byte{}, true},
        {"valid data", []byte("valid"), false},
        {"invalid data", []byte("invalid"), false},
    }
    // ...
}
```

## 集成测试（Integration Tests）

### 使用构建标签（Build Tags）

```go
//go:build integration
// +build integration

package myapp_test

import "testing"

func TestDatabaseIntegration(t *testing.T) {
    // 需要真实数据库的测试
}
```

```bash
# 运行集成测试
go test -tags=integration ./...

# 排除集成测试
go test ./...
```

### 使用测试容器（Testcontainers）

```go
import "github.com/testcontainers/testcontainers-go"

func setupPostgres(t *testing.T) *sql.DB {
    ctx := context.Background()

    req := testcontainers.ContainerRequest{
        Image:        "postgres:15",
        ExposedPorts: []string{"5432/tcp"},
        Env: map[string]string{
            "POSTGRES_PASSWORD": "test",
            "POSTGRES_DB":       "testdb",
        },
    }

    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    if err != nil {
        t.Fatal(err)
    }

    t.Cleanup(func() {
        container.Terminate(ctx)
    })

    // 连接到容器
    // ...
    return db
}
```

## 测试并行化（Parallelizing Tests）

### 并行测试

```go
func TestParallel(t *testing.T) {
    tests := []struct {
        name string
        fn   func(*testing.T)
    }{
        {"test1", testCase1},
        {"test2", testCase2},
        {"test3", testCase3},
    }

    for _, tt := range tests {
        tt := tt // 捕获循环变量
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // 并行执行此测试
            tt.fn(t)
        })
    }
}
```

### 控制并行执行

```go
func TestWithResourceLimit(t *testing.T) {
    // 同时仅运行 5 个测试
    sem := make(chan struct{}, 5)

    tests := generateManyTests()

    for _, tt := range tests {
        tt := tt
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            sem <- struct{}{}        // 获取
            defer func() { <-sem }() // 释放

            tt.fn(t)
        })
    }
}
```

## Go 工具集成

### 测试命令

```bash
# 基本测试
go test ./...
go test -v ./...                    # 详细输出
go test -run TestSpecific ./...     # 运行特定测试

# 覆盖率
go test -cover ./...
go test -coverprofile=coverage.out ./...

# 竞态检测 (Race Condition)
go test -race ./...

# 基准测试
go test -bench=. ./...
go test -bench=. -benchmem ./...
go test -bench=. -cpuprofile=cpu.prof ./...

# 模糊测试
go test -fuzz=FuzzTest

# 集成测试
go test -tags=integration ./...

# JSON 格式（用于 CI 集成）
go test -json ./...
```

### 测试配置

```bash
# 测试超时
go test -timeout 30s ./...

# 短时间测试（跳过耗时测试）
go test -short ./...

# 清除构建缓存
go clean -testcache
go test ./...
```

## 最佳实践

### DRY（Don't Repeat Yourself）原则

```go
// Good: 通过表格驱动测试减少重复
func TestValidation(t *testing.T) {
    tests := []struct {
        input string
        valid bool
    }{
        {"valid@email.com", true},
        {"invalid-email", false},
        {"", false},
    }

    for _, tt := range tests {
        t.Run(tt.input, func(t *testing.T) {
            err := Validate(tt.input)
            if (err == nil) != tt.valid {
                t.Errorf("Validate(%q) error = %v, want valid = %v",
                    tt.input, err, tt.valid)
            }
        })
    }
}
```

### 测试数据分离

```go
// Good: 将测试数据存放在 testdata/ 目录中
func TestLoadConfig(t *testing.T) {
    data, err := os.ReadFile("testdata/config.json")
    if err != nil {
        t.Fatal(err)
    }

    config, err := ParseConfig(data)
    // ...
}
```

### 使用清理函数（Cleanup）

```go
func TestWithCleanup(t *testing.T) {
    // 设置资源
    file, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }

    // 注册清理操作（类似于 defer，但在子测试中也有效）
    t.Cleanup(func() {
        os.Remove(file.Name())
    })

    // 继续测试...
}
```

### 明确错误信息

```go
// Bad: 错误信息不明确
if result != expected {
    t.Error("wrong result")
}

// Good: 带有上下文的错误信息
if result != expected {
    t.Errorf("Calculate(%d) = %d; want %d", input, result, expected)
}

// Better: 使用辅助函数
assertEqual(t, result, expected, "Calculate(%d)", input)
```

## 应避免的反模式（Anti-patterns）

```go
// Bad: 依赖外部状态
func TestBadDependency(t *testing.T) {
    result := GetUserFromDatabase("123") // 使用真实数据库
    // 测试脆弱且缓慢
}

// Good: 注入依赖
func TestGoodDependency(t *testing.T) {
    mockDB := &MockDatabase{
        users: map[string]User{"123": {ID: "123"}},
    }
    result := GetUser(mockDB, "123")
}

// Bad: 在测试间共享状态
var sharedCounter int

func TestShared1(t *testing.T) {
    sharedCounter++
    // 依赖测试顺序
}

// Good: 每个测试保持独立
func TestIndependent(t *testing.T) {
    counter := 0
    counter++
    // 不影响其他测试
}

// Bad: 忽略错误
func TestIgnoreError(t *testing.T) {
    result, _ := Process()
    if result != expected {
        t.Error("wrong result")
    }
}

// Good: 检查错误
func TestCheckError(t *testing.T) {
    result, err := Process()
    if err != nil {
        t.Fatalf("Process() error = %v", err)
    }
    if result != expected {
        t.Errorf("got %v, want %v", result, expected)
    }
}
```

## 快速参考

| 命令/模式 | 目的 |
|--------------|---------|
| `go test ./...` | 运行所有测试 |
| `go test -v` | 详细输出 |
| `go test -cover` | 覆盖率报告 |
| `go test -race` | 检测竞态条件 |
| `go test -bench=.` | 运行基准测试 |
| `t.Run()` | 子测试 |
| `t.Helper()` | 测试辅助函数标识 |
| `t.Parallel()` | 并行执行测试 |
| `t.Cleanup()` | 注册清理操作 |
| `testdata/` | 测试固件目录 |
| `-short` | 跳过耗时测试 |
| `-tags=integration` | 通过构建标签运行测试 |

**请记住**：优秀的测试应该是快速、可靠、可维护且清晰的。追求清晰度而非复杂性。
