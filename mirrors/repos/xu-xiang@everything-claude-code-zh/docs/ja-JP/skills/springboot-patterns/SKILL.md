---
name: springboot-patterns
description: Spring Boot 架构模式、REST API 设计、分层服务、数据访问、缓存、异步处理与日志。适用于 Java Spring Boot 后端开发。
---

# Spring Boot 开发模式

为构建可扩展的生产级服务提供的 Spring Boot 架构与 API 模式。

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
    return ResponseEntity.status(HttpStatus.CREATED).body(MarketResponse::from(market));
  }
}
```

## 仓库模式（Repository Pattern, Spring Data JPA）

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

## DTO 与校验（Validation）

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

## 异常处理（Exception Handling）

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
    // 记录带堆栈轨迹的非预期错误日志
    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(ApiError.of("Internal server error"));
  }
}
```

## 缓存（Caching）

需要在配置类中使用 `@EnableCaching`。

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

需要在配置类中使用 `@EnableAsync`。

```java
@Service
public class NotificationService {
  @Async
  public CompletableFuture<Void> sendAsync(Notification notification) {
    // 发送邮件/短信
    return CompletableFuture.completedFuture(null);
  }
}
```

## 日志（Logging, SLF4J）

```java
@Service
public class ReportService {
  private static final Logger log = LoggerFactory.getLogger(ReportService.class);

  public Report generate(Long marketId) {
    log.info("generate_report marketId={}", marketId);
    try {
      // 业务逻辑
    } catch (Exception ex) {
      log.error("generate_report_failed marketId={}", marketId, ex);
      throw ex;
    }
    return new Report();
  }
}
```

## 中间件 / 过滤器（Middleware / Filter）

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

## 分页与排序

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<Market> results = marketService.list(page);
```

## 具备容错能力的外部调用（Resilient External Calls）

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

## 限流（Rate Limiting, Filter + Bucket4j）

**安全提示**: `X-Forwarded-For` 请求头默认不可信，因为客户端可以伪造它。
仅在以下情况下使用转发请求头：
1. 应用程序部署在受信任的反向代理（如 nginx, AWS ALB 等）后
2. 已将 `ForwardedHeaderFilter` 注册为 Bean
3. 在 application properties 中设置了 `server.forward-headers-strategy=NATIVE` 或 `FRAMEWORK`
4. 代理服务器已配置为重写（而不是追加） `X-Forwarded-For` 请求头

如果正确配置了 `ForwardedHeaderFilter`，`request.getRemoteAddr()` 将自动从转发请求头中返回正确的客户端 IP。如果没有此配置，请直接使用 `request.getRemoteAddr()`，它将返回直连 IP，这是唯一可信的值。

```java
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  /*
   * 安全提示: 此过滤器使用 request.getRemoteAddr() 识别客户端以进行限流。
   *
   * 如果应用程序部署在反向代理（如 nginx, AWS ALB 等）后，需要正确配置 Spring 
   * 处理转发请求头，以确保能够准确检测客户端 IP：
   *
   * 1. 在 application.properties/yaml 中设置 server.forward-headers-strategy=NATIVE
   *    （适用于云平台）或 FRAMEWORK
   * 2. 如果使用 FRAMEWORK 策略，请注册 ForwardedHeaderFilter:
   *
   *    @Bean
   *    ForwardedHeaderFilter forwardedHeaderFilter() {
   *        return new ForwardedHeaderFilter();
   *    }
   *
   * 3. 确保代理服务器会重写（覆盖） X-Forwarded-For 请求头以防止伪造
   * 4. 根据容器类型设置 server.tomcat.remoteip.trusted-proxies 或同等配置
   *
   * 如果没有这些配置，request.getRemoteAddr() 将返回代理服务器的 IP 而不是客户端 IP。
   * 切勿直接读取 X-Forwarded-For，在没有受信任的代理处理机制下，该头很容易被伪造。
   */
  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain filterChain) throws ServletException, IOException {
    // 如果配置了 ForwardedHeaderFilter，getRemoteAddr() 将返回正确的客户端 IP。
    // 否则返回直连 IP。在没有适当代理配置的情况下，不要直接信任 X-Forwarded-For 请求头。
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

## 后台任务

使用 Spring 的 `@Scheduled` 或集成消息队列（Kafka, SQS, RabbitMQ 等）。保持处理器（Handler）幂等且可观测。

## 可观测性（Observability）

- 结构化日志（JSON）：通过 Logback encoder 实现
- 指标（Metrics）：Micrometer + Prometheus/OTel
- 链路追踪（Tracing）：Micrometer Tracing 配合 OpenTelemetry 或 Brave 后端

## 生产环境默认实践

- 优先使用构造函数注入，避免字段注入（Field Injection）
- 启用 `spring.mvc.problemdetails.enabled=true` 以支持 RFC 7807 错误详情（Spring Boot 3+）
- 根据工作负载配置 HikariCP 连接池大小并设置超时
- 为查询操作使用 `@Transactional(readOnly = true)`
- 使用 `@NonNull` 和 `Optional` 强制执行 null 安全性

**请记住**：保持 Controller 层轻量，Service 层专注，Repository 层简单，并集中处理异常。为可维护性和可测试性进行优化。
