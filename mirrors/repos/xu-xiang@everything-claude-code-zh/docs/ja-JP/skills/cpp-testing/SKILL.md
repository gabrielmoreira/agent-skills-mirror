---
name: cpp-testing
description: 仅在创建/更新/修复 C++ 测试、配置 GoogleTest/CTest、诊断失败或不稳定的测试、以及添加覆盖率或消毒器时使用。
---

# C++ Testing（智能体技能）

这是一个基于 CMake/CTest 和 GoogleTest/GoogleMock 的、面向智能体（Agent）的现代 C++（C++17/20）测试工作流（Workflow）。

## 使用场景

- 创建新的 C++ 测试或修改现有测试
- 为 C++ 组件设计单元测试/集成测试覆盖率
- 添加测试覆盖率、CI 门禁和回归保护
- 配置 CMake/CTest 工作流以实现一致的执行
- 调查测试失败或不稳定（Flaky）的行为
- 启用消毒器（Sanitizers）进行内存/竞态诊断

### 不建议使用的场景

- 实现不涉及测试更改的新产品功能
- 与测试覆盖率或失败无关的大规模重构
- 没有需要验证的测试回归的性能调优
- 非 C++ 项目或非测试任务

## 核心概念

- **TDD 循环**: 红（Red） → 绿（Green） → 重构（Refactor）（测试先行，最小化修复，然后清理代码）
- **解耦**: 优先使用依赖注入（Dependency Injection）和伪造对象（Fakes），而非全局状态
- **测试布局**: `tests/unit`、`tests/integration`、`tests/testdata`
- **模拟 (Mock) vs 伪造 (Fake)**: 交互验证使用 Mock，有状态的行为使用 Fake
- **CTest 发现**: 使用 `gtest_discover_tests()` 以实现稳定的测试发现
- **CI 信号**: 先运行子集，然后使用 `--output-on-failure` 运行全量测试套件

## TDD 工作流

遵循 RED → GREEN → REFACTOR 循环：

1. **RED**: 编写一个失败的测试来捕获新行为
2. **GREEN**: 实现最小化的更改使测试通过
3. **REFACTOR**: 在保持测试为绿色的前提下清理代码

```cpp
// tests/add_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // 由生产代码提供

TEST(AddTest, AddsTwoNumbers) { // RED
  EXPECT_EQ(Add(2, 3), 5);
}

// src/add.cpp
int Add(int a, int b) { // GREEN
  return a + b;
}

// REFACTOR: 测试通过后进行简化或重命名
```

## 代码示例

### 基础单元测试 (gtest)

```cpp
// tests/calculator_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // 由生产代码提供

TEST(CalculatorTest, AddsTwoNumbers) {
    EXPECT_EQ(Add(2, 3), 5);
}
```

### 测试固件 (Fixture - gtest)

```cpp
// tests/user_store_test.cpp
// 伪代码桩：请根据项目类型替换 UserStore/User
#include <gtest/gtest.h>
#include <memory>
#include <optional>
#include <string>

struct User { std::string name; };
class UserStore {
public:
    explicit UserStore(std::string /*path*/) {}
    void Seed(std::initializer_list<User> /*users*/) {}
    std::optional<User> Find(const std::string &/*name*/) { return User{"alice"}; }
};

class UserStoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        store = std::make_unique<UserStore>(":memory:");
        store->Seed({{"alice"}, {"bob"}});
    }

    std::unique_ptr<UserStore> store;
};

TEST_F(UserStoreTest, FindsExistingUser) {
    auto user = store->Find("alice");
    ASSERT_TRUE(user.has_value());
    EXPECT_EQ(user->name, "alice");
}
```

### 模拟对象 (Mock - gmock)

```cpp
// tests/notifier_test.cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>

class Notifier {
public:
    virtual ~Notifier() = default;
    virtual void Send(const std::string &message) = 0;
};

class MockNotifier : public Notifier {
public:
    MOCK_METHOD(void, Send, (const std::string &message), (override));
};

class Service {
public:
    explicit Service(Notifier &notifier) : notifier_(notifier) {}
    void Publish(const std::string &message) { notifier_.Send(message); }

private:
    Notifier &notifier_;
};

TEST(ServiceTest, SendsNotifications) {
    MockNotifier notifier;
    Service service(notifier);

    EXPECT_CALL(notifier, Send("hello")).Times(1);
    service.Publish("hello");
}
```

### CMake/CTest 快速上手

```cmake
# CMakeLists.txt (节选)
cmake_minimum_required(VERSION 3.20)
project(example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
# 优先使用项目锁定的版本。如果使用标签，请根据项目策略使用固定版本。
set(GTEST_VERSION v1.17.0) # 根据项目策略进行调整
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/${GTEST_VERSION}.zip
)
FetchContent_MakeAvailable(googletest)

add_executable(example_tests
  tests/calculator_test.cpp
  src/calculator.cpp
)
target_link_libraries(example_tests GTest::gtest GTest::gmock GTest::gtest_main)

enable_testing()
include(GoogleTest)
gtest_discover_tests(example_tests)
```

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```

## 运行测试

```bash
ctest --test-dir build --output-on-failure
ctest --test-dir build -R ClampTest
ctest --test-dir build -R "UserStoreTest.*" --output-on-failure
```

```bash
./build/example_tests --gtest_filter=ClampTest.*
./build/example_tests --gtest_filter=UserStoreTest.FindsExistingUser
```

## 调试失败

1. 使用 gtest 过滤器重新运行单个失败的测试。
2. 在失败的断言周围添加作用域日志（Scoped logging）。
3. 启用消毒器（Sanitizers）后重新运行。
4. 根本原因修复后，扩展到全量测试套件。

## 覆盖率 (Coverage)

优先使用目标级（Target-level）配置，而非全局标志。

```cmake
option(ENABLE_COVERAGE "Enable coverage flags" OFF)

if(ENABLE_COVERAGE)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    target_compile_options(example_tests PRIVATE --coverage)
    target_link_options(example_tests PRIVATE --coverage)
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(example_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
    target_link_options(example_tests PRIVATE -fprofile-instr-generate)
  endif()
endif()
```

GCC + gcov + lcov:

```bash
cmake -S . -B build-cov -DENABLE_COVERAGE=ON
cmake --build build-cov -j
ctest --test-dir build-cov
lcov --capture --directory build-cov --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage
```

Clang + llvm-cov:

```bash
cmake -S . -B build-llvm -DENABLE_COVERAGE=ON -DCMAKE_CXX_COMPILER=clang++
cmake --build build-llvm -j
LLVM_PROFILE_FILE="build-llvm/default.profraw" ctest --test-dir build-llvm
llvm-profdata merge -sparse build-llvm/default.profraw -o build-llvm/default.profdata
llvm-cov report build-llvm/example_tests -instr-profile=build-llvm/default.profdata
```

## 消毒器 (Sanitizers)

```cmake
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)

if(ENABLE_ASAN)
  add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address)
endif()
if(ENABLE_UBSAN)
  add_compile_options(-fsanitize=undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=undefined)
endif()
if(ENABLE_TSAN)
  add_compile_options(-fsanitize=thread)
  add_link_options(-fsanitize=thread)
endif()
```

## 不稳定测试 (Flaky Test) 的防护栏

- 不要使用 `sleep` 进行同步，应使用条件变量（Condition variables）或门闩（Latches）。
- 确保临时目录对每个测试都是唯一的，并且始终在测试后清理。
- 在单元测试中避免依赖真实的时间、网络和文件系统。
- 为随机化输入使用确定的种子（Deterministic seeds）。

## 最佳实践

### 推荐做法

- 保持测试是确定性的且相互隔离的
- 优先使用依赖注入而非全局变量
- 前置条件使用 `ASSERT_*`，多个检查项使用 `EXPECT_*`
- 通过 CTest 标签（Labels）或目录结构分离单元测试和集成测试
- 在 CI 中运行 Sanitizer 以检测内存问题和竞态条件

### 禁忌做法

- 单元测试不要依赖真实的时间或网络
- 如果可以使用条件变量，不要使用 sleep 进行同步
- 不要对简单的值对象（Value objects）过度模拟（Over-mocking）
- 不要对非关键日志使用脆弱的字符串匹配

### 常见陷阱

- **使用固定的临时路径** → 为每个测试生成唯一的临时目录并进行清理。
- **依赖墙上时钟时间** → 注入时钟源或使用伪造的时间源。
- **不稳定的并发测试** → 使用条件变量/门闩和带超时的等待。
- **隐蔽的全局状态** → 在测试固件中重置全局状态，或移除全局变量。
- **过度模拟 (Over-mocking)** → 优先使用 Fake 处理有状态行为，仅对交互进行 Mock。
- **缺失 Sanitizer 运行** → 在 CI 中添加 ASan/UBSan/TSan 构建。
- **仅在 Debug 构建中统计覆盖率** → 确保覆盖率目标使用的是一致的标志。

## 可选附录：模糊测试与属性测试

仅当项目已经支持 LLVM/libFuzzer 或属性测试库时使用。

- **libFuzzer**: 最适合 I/O 极少的纯函数。
- **RapidCheck**: 验证不变性（Invariants）的基于属性的测试。

最小化 libFuzzer 挂钩示例（伪代码：请替换 ParseConfig）：

```cpp
#include <cstddef>
#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string input(reinterpret_cast<const char *>(data), size);
    // ParseConfig(input); // 项目函数
    return 0;
}
```

## GoogleTest 的替代方案

- **Catch2**: 仅头文件（Header-only），具有表现力的匹配器
- **doctest**: 轻量级，编译开销极小
