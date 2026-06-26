---
name: cpp-coding-standards
description: 基于 C++ 核心指南 (isocpp.github.io) 的 C++ 编码规范。在编写、评审或重构 C++ 代码时使用，以强制执行现代、安全且地道的实践。
origin: ECC
---

# C++ 编码规范 (C++ Core Guidelines)

源自 [C++ 核心指南 (C++ Core Guidelines)](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) 的现代 C++ (C++17/20/23) 综合编码规范。强制执行类型安全 (Type safety)、资源安全 (Resource safety)、不变性 (Immutability) 和清晰度。

## 何时使用

- 编写新的 C++ 代码（类、函数、模板）
- 评审或重构现有的 C++ 代码
- 在 C++ 项目中做出架构决策
- 在 C++ 代码库中强制执行一致的风格
- 在语言特性之间进行选择（例如 `enum` vs `enum class`，原始指针 vs 智能指针）

### 何时不使用

- 非 C++ 项目
- 无法采用现代 C++ 特性的遗留 C 代码库
- 特定指南与硬件约束冲突的嵌入式/裸机上下文（需选择性调整）

## 核心原则 (Cross-Cutting Principles)

以下主题贯穿整个指南并构成基础：

1. **处处 RAII** (P.8, R.1, E.6, CP.20)：将资源生命周期与对象生命周期绑定。资源获取即初始化 (RAII)
2. **默认不变性** (P.10, Con.1-5, ES.25)：优先使用 `const`/`constexpr`；可变性应当是例外。不变性 (Immutability)
3. **类型安全** (P.4, I.4, ES.46-49, Enum.3)：利用类型系统在编译时防止错误。类型安全 (Type safety)
4. **表达意图** (P.3, F.1, NL.1-2, T.10)：名称、类型和概念应能传达目的。表达意图 (Express intent)
5. **最小化复杂性** (F.2-3, ES.5, Per.4-5)：简单的代码才是正确的代码
6. **值语义优于指针语义** (C.10, R.3-5, F.20, CP.31)：优先考虑按值返回和作用域对象。值语义 (Value semantics)

## 哲学与接口 (P.*, I.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **P.1** | 直接在代码中表达思想 |
| **P.3** | 表达意图 |
| **P.4** | 理想情况下，程序应该是静态类型安全的 |
| **P.5** | 优先考虑编译时检查而非运行时检查 |
| **P.8** | 不要泄露任何资源 |
| **P.10** | 优先考虑不可变数据而非可变数据 |
| **I.1** | 使接口显式化 |
| **I.2** | 避免使用非 const 的全局变量 |
| **I.4** | 使接口具有精确且强类型的定义 |
| **I.11** | 绝不通过原始指针或引用转移所有权 |
| **I.23** | 保持较少的函数参数数量 |

### 正确示例 (DO)

```cpp
// P.10 + I.4: 不可变的强类型接口
struct Temperature {
    double kelvin;
};

Temperature boil(const Temperature& water);
```

### 错误示例 (DON'T)

```cpp
// 弱接口：所有权不明确，单位不明确
double boil(double* temp);

// 非 const 全局变量
int g_counter = 0;  // 违反 I.2
```

## 函数 (F.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **F.1** | 将有意义的操作打包成命名谨慎的函数 |
| **F.2** | 函数应执行单一逻辑操作 |
| **F.3** | 保持函数简短且简单 |
| **F.4** | 如果函数可能在编译时求值，请将其声明为 `constexpr` |
| **F.6** | 如果函数绝不抛出异常，请将其声明为 `noexcept` |
| **F.8** | 优先选择纯函数 (Pure functions) |
| **F.16** | 对于“输入”参数，低开销拷贝类型按值传递，其他类型按 `const&` 传递 |
| **F.20** | 对于“输出”值，优先选择返回值而非输出参数 |
| **F.21** | 若要返回多个“输出”值，优先返回结构体 |
| **F.43** | 绝不返回指向局部对象的指针或引用 |

### 参数传递

```cpp
// F.16: 低开销类型按值传递，其他按 const& 传递
void print(int x);                           // 低开销：按值
void analyze(const std::string& data);       // 高开销：按 const&
void transform(std::string s);               // 接收端：按值（将触发 move）

// F.20 + F.21: 使用返回值，而非输出参数
struct ParseResult {
    std::string token;
    int position;
};

ParseResult parse(std::string_view input);   // 推荐：返回结构体

// 不良实践：使用输出参数
void parse(std::string_view input,
           std::string& token, int& pos);    // 避免这样做
```

### 纯函数与 constexpr

```cpp
// F.4 + F.8: 尽可能使用纯函数和 constexpr
constexpr int factorial(int n) noexcept {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

static_assert(factorial(5) == 120);
```

### 反模式 (Anti-Patterns)

- 从函数返回 `T&&` (F.45)
- 使用 `va_arg` / C 风格变长参数 (F.55)
- 在传递给其他线程的 lambda 中按引用捕获 (F.53)
- 返回 `const T`，这会抑制移动语义 (F.49)

## 类与类层次结构 (C.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **C.2** | 如果存在不变式 (Invariant)，使用 `class`；如果成员数据独立变化，使用 `struct` |
| **C.9** | 最小化成员的公开暴露 |
| **C.20** | 如果可以避免定义默认操作，则不要定义（零法则 Rule of Zero） |
| **C.21** | 如果定义或 `=delete` 了任何拷贝/移动/析构函数，请处理所有五个（五法则 Rule of Five） |
| **C.35** | 基类析构函数：要么是 public virtual，要么是 protected non-virtual |
| **C.41** | 构造函数应创建一个完全初始化的对象 |
| **C.46** | 将单参数构造函数声明为 `explicit` |
| **C.67** | 多态类 (Polymorphic class) 应抑制公开的拷贝/移动 |
| **C.128** | 虚函数：必须精确指定 `virtual`、`override` 或 `final` 中的一个 |

### 零法则 (Rule of Zero)

```cpp
// C.20: 让编译器生成特殊成员
struct Employee {
    std::string name;
    std::string department;
    int id;
    // 无需析构函数、拷贝/移动构造函数或赋值运算符
};
```

### 五法则 (Rule of Five)

```cpp
// C.21: 如果必须管理资源，请定义所有五个
class Buffer {
public:
    explicit Buffer(std::size_t size)
        : data_(std::make_unique<char[]>(size)), size_(size) {}

    ~Buffer() = default;

    Buffer(const Buffer& other)
        : data_(std::make_unique<char[]>(other.size_)), size_(other.size_) {
        std::copy_n(other.data_.get(), size_, data_.get());
    }

    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            auto new_data = std::make_unique<char[]>(other.size_);
            std::copy_n(other.data_.get(), other.size_, new_data.get());
            data_ = std::move(new_data);
            size_ = other.size_;
        }
        return *this;
    }

    Buffer(Buffer&&) noexcept = default;
    Buffer& operator=(Buffer&&) noexcept = default;

private:
    std::unique_ptr<char[]> data_;
    std::size_t size_;
};
```

### 类层次结构

```cpp
// C.35 + C.128: 虚析构函数，使用 override
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;  // C.121: 纯接口
};

class Circle : public Shape {
public:
    explicit Circle(double r) : radius_(r) {}
    double area() const override { return 3.14159 * radius_ * radius_; }

private:
    double radius_;
};
```

### 反模式 (Anti-Patterns)

- 在构造函数/析构函数中调用虚函数 (C.82)
- 对非平凡 (Non-trivial) 类型使用 `memset`/`memcpy` (C.90)
- 为虚函数及其覆盖者提供不同的默认参数 (C.140)
- 使数据成员成为 `const` 或引用，这会抑制移动/拷贝 (C.12)

## 资源管理 (R.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **R.1** | 使用 RAII 自动管理资源 |
| **R.3** | 原始指针 (`T*`) 是非所有权的 |
| **R.5** | 优先选择作用域对象；不要不必要地在堆上分配 |
| **R.10** | 避免使用 `malloc()`/`free()` |
| **R.11** | 避免显式调用 `new` 和 `delete` |
| **R.20** | 使用 `unique_ptr` 或 `shared_ptr` 表示所有权 |
| **R.21** | 除非共享所有权，否则优先选择 `unique_ptr` 而非 `shared_ptr` |
| **R.22** | 使用 `make_shared()` 创建 `shared_ptr` |

### 智能指针用法

```cpp
// R.11 + R.20 + R.21: 使用智能指针进行 RAII
auto widget = std::make_unique<Widget>("config");  // 独占所有权
auto cache  = std::make_shared<Cache>(1024);        // 共享所有权

// R.3: 原始指针 = 非所有权的观察者
void render(const Widget* w) {  // 不拥有 w
    if (w) w->draw();
}

render(widget.get());
```

### RAII 模式

```cpp
// R.1: 资源获取即初始化 (Resource acquisition is initialization)
class FileHandle {
public:
    explicit FileHandle(const std::string& path)
        : handle_(std::fopen(path.c_str(), "r")) {
        if (!handle_) throw std::runtime_error("Failed to open: " + path);
    }

    ~FileHandle() {
        if (handle_) std::fclose(handle_);
    }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept
        : handle_(std::exchange(other.handle_, nullptr)) {}
    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this != &other) {
            if (handle_) std::fclose(handle_);
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

private:
    std::FILE* handle_;
};
```

### 反模式 (Anti-Patterns)

- 裸 `new`/`delete` (R.11)
- C++ 代码中使用 `malloc()`/`free()` (R.10)
- 在单个表达式中进行多次资源分配 (R.13 —— 异常安全风险)
- 在 `unique_ptr` 足以胜任的情况下使用 `shared_ptr` (R.21)

## 表达式与语句 (ES.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **ES.5** | 保持较小的作用域 |
| **ES.20** | 始终初始化对象 |
| **ES.23** | 优先选择 `{}` 初始化语法 |
| **ES.25** | 除非打算修改，否则将对象声明为 `const` 或 `constexpr` |
| **ES.28** | 对 `const` 变量的复杂初始化使用 lambda |
| **ES.45** | 避免幻数 (Magic constants)；使用符号常量 |
| **ES.46** | 避免收窄/有损的算术转换 |
| **ES.47** | 使用 `nullptr` 而非 `0` 或 `NULL` |
| **ES.48** | 避免强制类型转换 (Casts) |
| **ES.50** | 不要转换掉 `const` 属性 |

### 初始化

```cpp
// ES.20 + ES.23 + ES.25: 始终初始化，优先使用 {}，默认设为 const
const int max_retries{3};
const std::string name{"widget"};
const std::vector<int> primes{2, 3, 5, 7, 11};

// ES.28: 用于复杂 const 初始化的 lambda
const auto config = [&] {
    Config c;
    c.timeout = std::chrono::seconds{30};
    c.retries = max_retries;
    c.verbose = debug_mode;
    return c;
}();
```

### 反模式 (Anti-Patterns)

- 未初始化的变量 (ES.20)
- 使用 `0` 或 `NULL` 作为指针 (ES.47 —— 应使用 `nullptr`)
- C 风格强制转换 (ES.48 —— 应使用 `static_cast`、`const_cast` 等)
- 转换掉 `const` 属性 (ES.50)
- 不带命名常量的幻数 (ES.45)
- 混合有符号和无符号算术运算 (ES.100)
- 在嵌套作用域中重复使用名称 (ES.12)

## 错误处理 (E.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **E.1** | 在设计早期制定错误处理策略 |
| **E.2** | 当函数无法执行其分配的任务时抛出异常 |
| **E.6** | 使用 RAII 防止泄露 |
| **E.12** | 当不可能或不接受抛出异常时使用 `noexcept` |
| **E.14** | 使用专门设计的用户定义类型作为异常 |
| **E.15** | 按值抛出，按引用捕获 |
| **E.16** | 析构函数、释放操作和 swap 绝不能失败 |
| **E.17** | 不要试图在每个函数中捕获每个异常 |

### 异常层次结构

```cpp
// E.14 + E.15: 自定义异常类型，按值抛出，按引用捕获
class AppError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class NetworkError : public AppError {
public:
    NetworkError(const std::string& msg, int code)
        : AppError(msg), status_code(code) {}
    int status_code;
};

void fetch_data(const std::string& url) {
    // E.2: 抛出异常以表示失败
    throw NetworkError("connection refused", 503);
}

void run() {
    try {
        fetch_data("https://api.example.com");
    } catch (const NetworkError& e) {
        log_error(e.what(), e.status_code);
    } catch (const AppError& e) {
        log_error(e.what());
    }
    // E.17: 不要在此处捕获所有异常 —— 让非预期错误继续传播
}
```

### 反模式 (Anti-Patterns)

- 抛出内置类型如 `int` 或字符串字面量 (E.14)
- 按值捕获（存在对象切割风险） (E.15)
- 静默吞掉错误的空 catch 块
- 使用异常进行流程控制 (E.3)
- 基于全局状态（如 `errno`）的错误处理 (E.28)

## 常量与不变性 (Con.*)

### 全部规则

| 规则 | 摘要 |
|------|---------|
| **Con.1** | 默认情况下，使对象不可变 |
| **Con.2** | 默认情况下，使成员函数为 `const` |
| **Con.3** | 默认情况下，传递指向 `const` 的指针和引用 |
| **Con.4** | 对于构造后不改变的值使用 `const` |
| **Con.5** | 对于编译时可计算的值使用 `constexpr` |

```cpp
// Con.1 到 Con.5: 默认不变性
class Sensor {
public:
    explicit Sensor(std::string id) : id_(std::move(id)) {}

    // Con.2: 默认 const 成员函数
    const std::string& id() const { return id_; }
    double last_reading() const { return reading_; }

    // 仅在需要修改时才使用非 const
    void record(double value) { reading_ = value; }

private:
    const std::string id_;  // Con.4: 构造后绝不改变
    double reading_{0.0};
};

// Con.3: 按 const 引用传递
void display(const Sensor& s) {
    std::cout << s.id() << ": " << s.last_reading() << '\n';
}

// Con.5: 编译时常量
constexpr double PI = 3.14159265358979;
constexpr int MAX_SENSORS = 256;
```

## 并发与并行 (CP.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **CP.2** | 避免数据竞态 (Data races) |
| **CP.3** | 最小化显式共享可写数据 |
| **CP.4** | 以任务 (Tasks) 而非线程 (Threads) 的方式思考 |
| **CP.8** | 不要使用 `volatile` 进行同步 |
| **CP.20** | 使用 RAII，绝不直接调用 `lock()`/`unlock()` |
| **CP.21** | 使用 `std::scoped_lock` 获取多个互斥锁 |
| **CP.22** | 持有锁时绝不调用未知代码 |
| **CP.42** | 不要无条件等待 |
| **CP.44** | 记得为你的 `lock_guard` 和 `unique_lock` 命名 |
| **CP.100** | 除非绝对必要，否则不要使用无锁编程 (Lock-free programming) |

### 安全加锁

```cpp
// CP.20 + CP.44: RAII 锁，始终命名
class ThreadSafeQueue {
public:
    void push(int value) {
        std::lock_guard<std::mutex> lock(mutex_);  // CP.44: 已命名！
        queue_.push(value);
        cv_.notify_one();
    }

    int pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        // CP.42: 始终带条件等待
        cv_.wait(lock, [this] { return !queue_.empty(); });
        const int value = queue_.front();
        queue_.pop();
        return value;
    }

private:
    std::mutex mutex_;             // CP.50: 互斥锁及其保护的数据
    std::condition_variable cv_;
    std::queue<int> queue_;
};
```

### 多个互斥锁

```cpp
// CP.21: std::scoped_lock 用于多个互斥锁（避免死锁）
void transfer(Account& from, Account& to, double amount) {
    std::scoped_lock lock(from.mutex_, to.mutex_);
    from.balance_ -= amount;
    to.balance_ += amount;
}
```

### 反模式 (Anti-Patterns)

- 使用 `volatile` 进行同步 (CP.8 —— 它仅用于硬件 I/O)
- 分离线程 (Detaching threads) (CP.26 —— 生命周期管理将变得几乎不可能)
- 未命名的锁保护：`std::lock_guard<std::mutex>(m);` 会立即销毁 (CP.44)
- 调用回调时持有锁 (CP.22 —— 死锁风险)
- 缺乏深厚专业知识却进行无锁编程 (CP.100)

## 模板与泛型编程 (T.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **T.1** | 使用模板提升抽象层级 |
| **T.2** | 使用模板为多种参数类型表达算法 |
| **T.10** | 为所有模板参数指定概念 (Concepts) |
| **T.11** | 尽可能使用标准概念 |
| **T.13** | 简单概念优先使用简写表示法 |
| **T.43** | 优先选择 `using` 而非 `typedef` |
| **T.120** | 仅在确实需要时使用模板元编程 (Template metaprogramming) |
| **T.144** | 不要特化函数模板（应使用重载） |

### 概念 Concepts (C++20)

```cpp
#include <concepts>

// T.10 + T.11: 使用标准概念约束模板
template<std::integral T>
T gcd(T a, T b) {
    while (b != 0) {
        a = std::exchange(b, a % b);
    }
    return a;
}

// T.13: 简写概念语法
void sort(std::ranges::random_access_range auto& range) {
    std::ranges::sort(range);
}

// 针对领域特定约束的自定义概念
template<typename T>
concept Serializable = requires(const T& t) {
    { t.serialize() } -> std::convertible_to<std::string>;
};

template<Serializable T>
void save(const T& obj, const std::string& path);
```

### 反模式 (Anti-Patterns)

- 可见命名空间中使用无约束模板 (T.47)
- 特化函数模板而非重载 (T.144)
- 在 `constexpr` 足以胜任时使用模板元编程 (T.120)
- 使用 `typedef` 而非 `using` (T.43)

## 标准库 (SL.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **SL.1** | 尽可能使用库 |
| **SL.2** | 优先选择标准库而非其他库 |
| **SL.con.1** | 优先选择 `std::array` 或 `std::vector` 而非 C 数组 |
| **SL.con.2** | 默认优先选择 `std::vector` |
| **SL.str.1** | 使用 `std::string` 拥有字符序列 |
| **SL.str.2** | 使用 `std::string_view` 引用字符序列 |
| **SL.io.50** | 避免使用 `endl`（使用 `'\n'` —— `endl` 会强制刷新缓冲区） |

```cpp
// SL.con.1 + SL.con.2: 优先选择 vector/array 而非 C 数组
const std::array<int, 4> fixed_data{1, 2, 3, 4};
std::vector<std::string> dynamic_data;

// SL.str.1 + SL.str.2: string 拥有所有权，string_view 负责观察
std::string build_greeting(std::string_view name) {
    return "Hello, " + std::string(name) + "!";
}

// SL.io.50: 使用 '\n' 而非 endl
std::cout << "result: " << value << '\n';
```

## 枚举 (Enum.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **Enum.1** | 优先选择枚举而非宏 |
| **Enum.3** | 优先选择 `enum class` 而非普通 `enum` |
| **Enum.5** | 不要对枚举成员使用 全大写 (ALL_CAPS) 命名 |
| **Enum.6** | 避免使用匿名枚举 |

```cpp
// Enum.3 + Enum.5: 有作用域枚举，非全大写
enum class Color { red, green, blue };
enum class LogLevel { debug, info, warning, error };

// 不良实践：普通枚举会泄露名称，全大写会与宏冲突
enum { RED, GREEN, BLUE };           // 违反 Enum.3 + Enum.5 + Enum.6
#define MAX_SIZE 100                  // 违反 Enum.1 —— 应使用 constexpr
```

## 源文件与命名 (SF.*, NL.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **SF.1** | 代码文件使用 `.cpp`，接口文件使用 `.h` |
| **SF.7** | 不要在头文件的全局作用域编写 `using namespace` |
| **SF.8** | 为所有 `.h` 文件使用 `#include` 保护 |
| **SF.11** | 头文件应当是自包含的 (Self-contained) |
| **NL.5** | 避免在名称中编码类型信息（不使用匈牙利命名法） |
| **NL.8** | 使用一致的命名风格 |
| **NL.9** | 仅对宏名称使用 全大写 (ALL_CAPS) |
| **NL.10** | 优先选择 `下划线风格 (underscore_style)` 命名 |

### 头文件保护 (Header Guard)

```cpp
// SF.8: 包含保护 (或 #pragma once)
#ifndef PROJECT_MODULE_WIDGET_H
#define PROJECT_MODULE_WIDGET_H

// SF.11: 自包含 —— 包含此头文件所需的所有内容
#include <string>
#include <vector>

namespace project::module {

class Widget {
public:
    explicit Widget(std::string name);
    const std::string& name() const;

private:
    std::string name_;
};

}  // namespace project::module

#endif  // PROJECT_MODULE_WIDGET_H
```

### 命名规范

```cpp
// NL.8 + NL.10: 一致的下划线风格
namespace my_project {

constexpr int max_buffer_size = 4096;  // NL.9: 非全大写（它不是宏）

class tcp_connection {                 // 下划线风格的类名
public:
    void send_message(std::string_view msg);
    bool is_connected() const;

private:
    std::string host_;                 // 成员变量带后缀下划线
    int port_;
};

}  // namespace my_project
```

### 反模式 (Anti-Patterns)

- 头文件全局作用域中使用 `using namespace std;` (SF.7)
- 依赖包含顺序的头文件 (SF.10, SF.11)
- 匈牙利命名法，如 `strName`、`iCount` (NL.5)
- 除宏以外的任何内容使用全大写 (NL.9)

## 性能 (Per.*)

### 核心规则

| 规则 | 摘要 |
|------|---------|
| **Per.1** | 不要无理由地进行优化 |
| **Per.2** | 不要进行过早优化 |
| **Per.6** | 没有测量，不要对性能下结论 |
| **Per.7** | 旨在支持优化的设计 |
| **Per.10** | 依赖静态类型系统 |
| **Per.11** | 将计算从运行时移至编译时 |
| **Per.19** | 以可预测的方式访问内存 |

### 指南

```cpp
// Per.11: 尽可能在编译时计算
constexpr auto lookup_table = [] {
    std::array<int, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = i * i;
    }
    return table;
}();

// Per.19: 优先选择连续数据以实现缓存友好
std::vector<Point> points;           // 推荐：连续存储
std::vector<std::unique_ptr<Point>> indirect_points; // 不良实践：指针追踪
```

### 反模式 (Anti-Patterns)

- 在没有性能分析数据的情况下进行优化 (Per.1, Per.6)
- 选择“聪明”的低级代码而非清晰的抽象 (Per.4, Per.5)
- 忽视数据布局和缓存行为 (Per.19)

## 快速参考自检清单

在标记 C++ 工作完成之前：

- [ ] 无原始 `new`/`delete` —— 使用智能指针或 RAII (R.11)
- [ ] 对象在声明时初始化 (ES.20)
- [ ] 变量默认设为 `const`/`constexpr` (Con.1, ES.25)
- [ ] 成员函数尽可能设为 `const` (Con.2)
- [ ] 使用 `enum class` 而非普通 `enum` (Enum.3)
- [ ] 使用 `nullptr` 而非 `0`/`NULL` (ES.47)
- [ ] 无收窄转换 (ES.46)
- [ ] 无 C 风格强制转换 (ES.48)
- [ ] 单参数构造函数设为 `explicit` (C.46)
- [ ] 应用了零法则或五法则 (C.20, C.21)
- [ ] 基类析构函数为 public virtual 或 protected non-virtual (C.35)
- [ ] 模板通过概念 (Concepts) 进行约束 (T.10)
- [ ] 头文件全局作用域中无 `using namespace` (SF.7)
- [ ] 头文件具有包含保护且是自包含的 (SF.8, SF.11)
- [ ] 锁使用 RAII (`scoped_lock`/`lock_guard`) (CP.20)
- [ ] 异常为自定义类型，按值抛出，按引用捕获 (E.14, E.15)
- [ ] 使用 `'\n'` 而非 `std::endl` (SL.io.50)
- [ ] 无幻数 (ES.45)
