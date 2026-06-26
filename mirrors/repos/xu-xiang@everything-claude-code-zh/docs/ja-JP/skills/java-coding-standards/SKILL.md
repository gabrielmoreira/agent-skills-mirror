---
name: java-coding-standards
description: 适用于 Spring Boot 服务的 Java 编码规范：命名、不可变性、Optional 使用、流（Stream）、异常、泛型及项目布局。
---

# Java 编码规范

适用于 Spring Boot 服务中易读且可维护的 Java (17+) 代码标准。

## 核心原则

- 清晰度优先于巧妙性
- 默认不可变；最小化共享的可变状态
- 抛出有意义的异常以实现早期失败（Fail fast）
- 一致的命名与包结构

## 命名

```java
// ✅ 类/记录（Record）: PascalCase
public class MarketService {}
public record Money(BigDecimal amount, Currency currency) {}

// ✅ 方法/字段: camelCase
private final MarketRepository marketRepository;
public Market findBySlug(String slug) {}

// ✅ 常量: UPPER_SNAKE_CASE
private static final int MAX_PAGE_SIZE = 100;
```

## 不可变性

```java
// ✅ 优先使用 record 和 final 字段
public record MarketDto(Long id, String name, MarketStatus status) {}

public class Market {
  private final Long id;
  private final String name;
  // 仅有 getter，没有 setter
}
```

## Optional 的使用

```java
// ✅ find* 方法返回 Optional
Optional<Market> market = marketRepository.findBySlug(slug);

// ✅ 使用 map/flatMap 代替 get()
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));
```

## 流（Stream）最佳实践

```java
// ✅ 使用流进行转换，保持流水线（Pipeline）简洁
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// ❌ 避免复杂的嵌套流；为了清晰起见，优先使用循环
```

## 异常

- 对于领域错误（Domain errors）使用非检查异常（Unchecked Exceptions）；使用上下文包装技术异常
- 创建领域特定的异常（例如：`MarketNotFoundException`）
- 避免捕获过于宽泛的 `catch (Exception ex)`（除非在中心位置重新抛出或记录日志）

```java
throw new MarketNotFoundException(slug);
```

## 泛型与类型安全

- 避免使用原始类型（Raw types）；声明泛型参数
- 优先在可重用的工具类中使用受限泛型（Bounded Generics）

```java
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }
```

## 项目结构 (Maven/Gradle)

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
src/test/java/... (镜像 main 目录)
```

## 格式与样式

- 始终一致地使用 2 或 4 个空格（遵循项目标准）
- 每个文件仅包含一个 public 顶级类型
- 保持方法短小且专注；提取助手方法（Helper methods）
- 成员顺序：常量、字段、构造函数、public 方法、protected、private

## 应避免的代码异味 (Code Smells)

- 过长的参数列表 -> 使用 DTO 或建造者模式（Builder）
- 过深的嵌套 -> 使用早期返回（Early Return）
- 魔术数字 -> 使用命名常量
- 静态可变状态 -> 优先使用依赖注入（Dependency Injection）
- 沉默的 catch 块 -> 记录日志并采取行动，或者重新抛出

## 日志记录

```java
private static final Logger log = LoggerFactory.getLogger(MarketService.class);
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);
```

## Null 处理

- 仅在万不得已时接受 `@Nullable`；否则使用 `@NonNull`
- 对输入使用 Bean 校验（Bean Validation，如 `@NotNull`、`@NotBlank`）

## 测试预期

- JUnit 5 + AssertJ 实现流式断言（Fluent Assertions）
- 使用 Mockito 进行打桩；尽可能避免使用部分打桩（Partial mocks）
- 优先选择确定性测试；严禁隐藏的 `sleep`

**记住**：保持代码的意图清晰、类型安全且可观测。除非证明确有必要，否则应优先优化可维护性而非微小的性能优化。
