---
name: springboot-patterns
description: Spring Boot 架构模式、REST API 设计、分层服务、数据访问、缓存、异步处理和日志记录。适用于 Java Spring Boot 后端开发。
origin: ECC
---

# Spring Boot 开发模式

适用于可扩展、生产级服务的 Spring Boot 架构和 API 模式。

## 何时启用

- 使用 Spring MVC 或 WebFlux 构建 REST API
- 组织 控制器 (Controller) → 服务 (Service) → 存储库 (Repository) 层
- 配置 Spring Data JPA、缓存或异步处理
- 添加验证、异常处理或分页
- 为开发/测试/生产环境设置配置文件（Profiles）
- 使用 Spring 事件（Spring Events）或 Kafka 实现事件驱动模式

## REST API 结构

```java
@RestController
@RequestMapping("/api/markets")
@Validated
class MarketController {
  private final MarketService marketService;

  MarketController(MarketService marketService) {
    this.marketService = marketService;
  }

  @GetMapping
  ResponseEntity<Page<MarketResponse>> list(
      @RequestParam(defaultValue = "0") int page,
      @RequestParam(defaultValue = "20") int size) {
    Page<Market> markets = marketService.list(PageRequest.of(page, size));
    return ResponseEntity.ok(markets.map(MarketResponse::from));
  }

  @PostMapping
  ResponseEntity<MarketResponse> create(@Valid @RequestBody CreateMarketRequest request) {
    Market market = marketService.create(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(MarketResponse.from(market));
  }
}
```

## 存储库模式（Spring Data JPA）

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  @Query("select m from MarketEntity m where m.status = :status order by m.volume desc")
  List<MarketEntity> findActive(@Param("status") MarketStatus status, Pageable pageable);
}
```

## 带事务的服务层

```java
@Service
public class MarketService {
  private final MarketRepository repo;

  public MarketService(MarketRepository repo) {
    this.repo = repo;
  }

  @Transactional
  public Market create(CreateMarketRequest request) {
    MarketEntity entity = MarketEntity.from(request);
    MarketEntity saved = repo.save(entity);
    return Market.from(saved);
  }
}
```

## DTO 与验证

```java
public record CreateMarketRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Size(max = 2000) String description,
    @NotNull @FutureOrPresent Instant endDate,
    @NotEmpty List<@NotBlank String> categories) {}

public record MarketResponse(Long id, String name, MarketStatus status) {
  static MarketResponse from(Market market) {
    return new MarketResponse(market.id(), market.name(), market.status());
  }
}
```

## 异常处理

```java
@ControllerAdvice
class GlobalExceptionHandler {
  @ExceptionHandler(MethodArgumentNotValidException.class)
  ResponseEntity<ApiError> handleValidation(MethodArgumentNotValidException ex) {
    String message = ex.getBindingResult().getFieldErrors().stream()
        .map(e -> e.getField() + ": " + e.getDefaultMessage())
        .collect(Collectors.joining(", "));
    return ResponseEntity.badRequest().body(ApiError.validation(message));
  }

  @ExceptionHandler(AccessDeniedException.class)
  ResponseEntity<ApiError> handleAccessDenied() {
    return ResponseEntity.status(HttpStatus.FORBIDDEN).body(ApiError.of("Forbidden"));
  }

  @ExceptionHandler(Exception.class)
  ResponseEntity<ApiError> handleGeneric(Exception ex) {
    // 记录带有堆栈跟踪的非预期错误
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(ApiError.of("Internal server error"));
  }
}
```

## 缓存

需要在配置类上添加 `@EnableCaching`。

```java
@Service
public class MarketCacheService {
  private final MarketRepository repo;

  public MarketCacheService(MarketRepository repo) {
    this.repo = repo;
  }

  @Cacheable(value = "market", key = "#id")
  public Market getById(Long id) {
    return repo.findById(id)
        .map(Market::from)
        .orElseThrow(() -> new EntityNotFoundException("Market not found"));
  }

  @CacheEvict(value = "market", key = "#id")
  public void evict(Long id) {}
}
```

## 异步处理

需要在配置类上添加 `@EnableAsync`。

```java
@Service
public class NotificationService {
  @Async
  public CompletableFuture<Void> sendAsync(Notification notification) {
    // 发送电子邮件/短信
    return CompletableFuture.completedFuture(null);
  }
}
```

## 日志记录 (SLF4J)

```java
@Service
public class ReportService {
  private static final Logger log = LoggerFactory.getLogger(ReportService.class);

  public Report generate(Long marketId) {
    log.info("generate_report marketId={}", marketId);
    try {
      // 逻辑
    } catch (Exception ex) {
      log.error("generate_report_failed marketId={}", marketId, ex);
      throw ex;
    }
    return new Report();
  }
}
```

## 中间件 / 过滤器

```java
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {
  private static final Logger log = LoggerFactory.getLogger(RequestLoggingFilter.class);

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain filterChain) throws ServletException, IOException {
    long start = System.currentTimeMillis();
    try {
      filterChain.doFilter(request, response);
    } finally {
      long duration = System.currentTimeMillis() - start;
      log.info("req method={} uri={} status={} durationMs={}",
          request.getMethod(), request.getRequestURI(), response.getStatus(), duration);
    }
  }
}
```

## 分页和排序

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<Market> results = marketService.list(page);
```

## 具有容错能力的外部调用

```java
public <T> T withRetry(Supplier<T> supplier, int maxRetries) {
  int attempts = 0;
  while (true) {
    try {
      return supplier.get();
    } catch (Exception ex) {
      attempts++;
      if (attempts >= maxRetries) {
        throw ex;
      }
      try {
        Thread.sleep((long) Math.pow(2, attempts) * 100L);
      } catch (InterruptedException ie) {
        Thread.currentThread().interrupt();
        throw ex;
      }
    }
  }
}
```

## 速率限制（过滤器 + Bucket4j）

**安全提示**：默认情况下 `X-Forwarded-For` 请求头是不可信的，因为客户端可以伪造它。
仅在以下情况使用转发头：
1. 应用位于受信任的反向代理（nginx、AWS ALB 等）之后
2. 已将 `ForwardedHeaderFilter` 注册为 Bean
3. 已在应用属性中配置了 `server.forward-headers-strategy=NATIVE` 或 `FRAMEWORK`
4. 代理已配置为覆盖（而不是追加）`X-Forwarded-For` 请求头

当 `ForwardedHeaderFilter` 配置正确时，`request.getRemoteAddr()` 将自动从转发头中返回正确的客户端 IP。如果没有此配置，请直接使用 `request.getRemoteAddr()`——它返回直接连接的 IP，这是唯一可信的值。

```java
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  /*
   * 安全：此过滤器使用 request.getRemoteAddr() 来识别客户端以进行速率限制。
   *
   * 如果应用位于反向代理（nginx、AWS ALB 等）之后，必须配置 Spring 正确处理转发头，
   * 以进行准确的客户端 IP 检测：
   *
   * 1. 在 application.properties/yaml 中设置 server.forward-headers-strategy=NATIVE（用于云平台）
   *    或 FRAMEWORK
   * 2. 如果使用 FRAMEWORK 策略，请注册 ForwardedHeaderFilter：
   *
   *    @Bean
   *    ForwardedHeaderFilter forwardedHeaderFilter() {
   *        return new ForwardedHeaderFilter();
   *    }
   *
   * 3. 确保代理覆盖（而不是追加）X-Forwarded-For 请求头，以防止伪造
   * 4. 为容器配置 server.tomcat.remoteip.trusted-proxies 或等效配置
   *
   * 如果没有此配置，request.getRemoteAddr() 将返回代理 IP，而不是客户端 IP。
   * 不要直接读取 X-Forwarded-For——在没有受信任代理处理的情况下，它是极易伪造的。
   */
  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain filterChain) throws ServletException, IOException {
    // 使用 getRemoteAddr()，在配置了 ForwardedHeaderFilter 时它返回正确的客户端 IP，
    // 否则返回直接连接 IP。在没有正确代理配置的情况下，切勿直接信任 X-Forwarded-For 请求头。
    String clientIp = request.getRemoteAddr();

    Bucket bucket = buckets.computeIfAbsent(clientIp,
        k -> Bucket.builder()
            .addLimit(Bandwidth.classic(100, Refill.greedy(100, Duration.ofMinutes(1))))
            .build());

    if (bucket.tryConsume(1)) {
      filterChain.doFilter(request, response);
    } else {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
    }
  }
}
```

## 后台作业

使用 Spring 的 `@Scheduled` 或集成队列（如 Kafka、SQS、RabbitMQ）。保持处理程序的幂等性和可观察性。

## 可观察性

- 通过 Logback encoder 实现结构化日志（JSON）
- 指标（Metrics）：Micrometer + Prometheus/OTel
- 链路追踪（Tracing）：使用 OpenTelemetry 或 Brave 后端的 Micrometer Tracing

## 生产环境默认值

- 优先使用构造函数注入，避免字段注入
- 为 RFC 7807 错误启用 `spring.mvc.problemdetails.enabled=true`（Spring Boot 3+）
- 根据工作负载配置 HikariCP 连接池大小，设置超时
- 为查询使用 `@Transactional(readOnly = true)`
- 在适当的地方通过 `@NonNull` 和 `Optional` 强制执行空安全

**牢记**：保持控制器（Controllers）精简，服务（Services）聚焦，存储库（Repositories）简单，并集中处理错误。针对可维护性和可测试性进行优化。
