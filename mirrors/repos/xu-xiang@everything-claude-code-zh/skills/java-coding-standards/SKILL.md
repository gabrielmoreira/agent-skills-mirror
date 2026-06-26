---
name: java-coding-standards
description: "Spring Boot 服务的 Java 编码规范：命名、不可变性、Optional 使用、流（streams）、异常、泛型以及项目布局。"
origin: ECC
---

# Java 编码规范 (Java Coding Standards)

适用于 Spring Boot 服务中可读、可维护的 Java (17+) 代码规范。

## 何时激活 (When to Activate)

- 在 Spring Boot 项目中编写或评审 Java 代码时
- 强制执行命名、不可变性（immutability）或异常处理约定时
- 使用 records、密封类（sealed classes）或模式匹配（pattern matching）（Java 17+）时
- 评审 Optional、流（streams）或泛型（generics）的使用时
- 规划包结构和项目布局时

## 核心原则 (Core Principles)

- 清晰度优先于技巧性
- 默认不可变；尽量减少共享的可变状态
- 快速失败（Fail fast）并提供有意义的异常信息
- 保持命名和包结构的一致性

## 命名 (Naming)

```java
// ✅ 类/Records：大驼峰（PascalCase）
public class MarketService {}
public record Money(BigDecimal amount, Currency currency) {}

// ✅ 方法/字段：小驼峰（camelCase）
private final MarketRepository marketRepository;
public Market findBySlug(String slug) {}

// ✅ 常量：全大写蛇形（UPPER_SNAKE_CASE）
private static final int MAX_PAGE_SIZE = 100;
```

## 不可变性 (Immutability)

```java
// ✅ 优先使用 records 和 final 字段
public record MarketDto(Long id, String name, MarketStatus status) {}

public class Market {
  private final Long id;
  private final String name;
  // 仅提供 getter，不提供 setter
}
```

## Optional 使用 (Optional Usage)

```java
// ✅ find* 方法应返回 Optional
Optional<Market> market = marketRepository.findBySlug(slug);

// ✅ 使用 Map/flatMap 替代 get()
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));
```

## 流最佳实践 (Streams Best Practices)

```java
// ✅ 使用流进行转换，保持流水线简短
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// ❌ 避免复杂的嵌套流；为了清晰起见，优先使用循环
```

## 异常处理 (Exceptions)

- 对领域错误使用非受检异常（unchecked exceptions）；通过上下文包装技术异常
- 创建领域特定的异常（例如 `MarketNotFoundException`）
- 避免捕获广义的 `catch (Exception ex)`，除非是在中心位置重新抛出或记录日志

```java
throw new MarketNotFoundException(slug);
```

## 泛型与类型安全 (Generics and Type Safety)

- 避免使用原始类型（raw types）；显式声明泛型参数
- 对于可重用的工具类，优先使用有界泛型（bounded generics）

```java
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }
```

## 项目结构 (Project Structure - Maven/Gradle)

```
src/main/java/com/example/app/
  config/
  controller/
  service/
  repository/
  domain/
  dto/
  util/
src/main/resources/
  application.yml
src/test/java/... (与 main 结构镜像)
```

## 格式与风格 (Formatting and Style)

- 一致地使用 2 或 4 个空格（遵循项目标准）
- 每个文件仅包含一个公共顶级类型
- 保持方法简短且聚焦；提取助手方法（helpers）
- 成员排序：常量、字段、构造函数、公共方法、受保护方法、私有方法

## 应避免的代码异味 (Code Smells to Avoid)

- 参数列表过长 → 使用 DTO/构建器（builders）
- 层级嵌套过深 → 提前返回（early returns）
- 魔法数字 → 命名常量
- 静态可变状态 → 优先使用依赖注入（dependency injection）
- 沉默的 catch 块 → 记录日志并处理或重新抛出

## 日志记录 (Logging)

```java
private static final Logger log = LoggerFactory.getLogger(MarketService.class);
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);
```

## 空值处理 (Null Handling)

- 仅在不可避免时接受 `@Nullable`；否则使用 `@NonNull`
- 对输入使用 Bean 校验（Bean Validation，如 `@NotNull`, `@NotBlank`）

## 测试期望 (Testing Expectations)

- 使用 JUnit 5 + AssertJ 进行流式断言
- 使用 Mockito 进行 Mock；尽可能避免部分 Mock（partial mocks）
- 优先使用确定性测试；严禁隐藏的 sleep 等待

**记住**：保持代码有明确意图、强类型且可观测。除非证明确有必要，否则应优先考虑可维护性，而非微优化。
