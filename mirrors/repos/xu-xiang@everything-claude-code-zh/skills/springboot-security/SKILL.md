---
name: springboot-security
description: Spring Boot 服务的身份验证/授权、校验、CSRF、机密管理、响应头、速率限制及依赖安全的 Spring Security 最佳实践。
origin: ECC
---

# Spring Boot 安全审查（Security Review）

在添加身份验证（Auth）、处理输入、创建端点或处理机密信息时使用。

## 何时激活（When to Activate）

- 添加身份验证（JWT、OAuth2、基于 Session 的认证）
- 实现授权（`@PreAuthorize`、基于角色的访问控制）
- 校验用户输入（Bean Validation、自定义校验器）
- 配置 CORS、CSRF 或安全响应头
- 管理机密信息（Vault、环境变量）
- 添加速率限制（Rate Limiting）或暴力破解防护
- 扫描依赖项的 CVE 漏洞

## 身份验证（Authentication）

- 优先使用无状态 JWT 或带撤回列表的模糊令牌（Opaque Tokens）
- 为 Session 使用 `httpOnly`、`Secure`、`SameSite=Strict` 属性的 Cookie
- 使用 `OncePerRequestFilter` 或资源服务器校验令牌

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {
  private final JwtService jwtService;

  public JwtAuthFilter(JwtService jwtService) {
    this.jwtService = jwtService;
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String header = request.getHeader(HttpHeaders.AUTHORIZATION);
    if (header != null && header.startsWith("Bearer ")) {
      String token = header.substring(7);
      Authentication auth = jwtService.authenticate(token);
      SecurityContextHolder.getContext().setAuthentication(auth);
    }
    chain.doFilter(request, response);
  }
}
```

## 授权（Authorization）

- 启用方法安全：`@EnableMethodSecurity`
- 使用 `@PreAuthorize("hasRole('ADMIN')")` 或 `@PreAuthorize("@authz.canEdit(#id)")`
- 默认拒绝访问（Deny by default）；仅公开所需的权限范围（Scopes）

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {

  @PreAuthorize("hasRole('ADMIN')")
  @GetMapping("/users")
  public List<UserDto> listUsers() {
    return userService.findAll();
  }

  @PreAuthorize("@authz.isOwner(#id, authentication)")
  @DeleteMapping("/users/{id}")
  public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    userService.delete(id);
    return ResponseEntity.noContent().build();
  }
}
```

## 输入校验（Input Validation）

- 在控制器（Controllers）上对 `@Valid` 使用 Bean Validation
- 在 DTO 上应用约束：`@NotBlank`、`@Email`、`@Size`、自定义校验器
- 在渲染前，使用白名单清理（Sanitize）任何 HTML 内容

```java
// 差（BAD）：没有校验
@PostMapping("/users")
public User createUser(@RequestBody UserDto dto) {
  return userService.create(dto);
}

// 好（GOOD）：校验过的 DTO
public record CreateUserDto(
    @NotBlank @Size(max = 100) String name,
    @NotBlank @Email String email,
    @NotNull @Min(0) @Max(150) Integer age
) {}

@PostMapping("/users")
public ResponseEntity<UserDto> createUser(@Valid @RequestBody CreateUserDto dto) {
  return ResponseEntity.status(HttpStatus.CREATED)
      .body(userService.create(dto));
}
```

## 防止 SQL 注入（SQL Injection Prevention）

- 使用 Spring Data 存储库（Repositories）或参数化查询
- 对于原生查询（Native Queries），使用 `:param` 绑定；切勿拼接字符串

```java
// 差（BAD）：在原生查询中直接拼接字符串
@Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)

// 好（GOOD）：参数化原生查询
@Query(value = "SELECT * FROM users WHERE name = :name", nativeQuery = true)
List<User> findByName(@Param("name") String name);

// 好（GOOD）：Spring Data 衍生查询（自动参数化）
List<User> findByEmailAndActiveTrue(String email);
```

## 密码编码（Password Encoding）

- 始终使用 BCrypt 或 Argon2 对密码进行哈希处理 —— 严禁存储明文
- 使用 `PasswordEncoder` Bean，而不是手动执行哈希

```java
@Bean
public PasswordEncoder passwordEncoder() {
  return new BCryptPasswordEncoder(12); // 成本因子（cost factor）为 12
}

// 在 Service 中
public User register(CreateUserDto dto) {
  String hashedPassword = passwordEncoder.encode(dto.password());
  return userRepository.save(new User(dto.email(), hashedPassword));
}
```

## CSRF 防护（CSRF Protection）

- 对于基于浏览器会话（Session）的应用，保持 CSRF 启用；在表单/请求头中包含令牌
- 对于使用 Bearer 令牌的纯 API，禁用 CSRF 并依赖无状态身份验证

```java
http
  .csrf(csrf -> csrf.disable())
  .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```

## 机密管理（Secrets Management）

- 源代码中不保留机密；从环境变量或 Vault 加载
- 保持 `application.yml` 不含凭据信息；使用占位符
- 定期轮换令牌和数据库凭据

```yaml
# 差（BAD）：在 application.yml 中硬编码
spring:
  datasource:
    password: mySecretPassword123

# 好（GOOD）：使用环境变量占位符
spring:
  datasource:
    password: ${DB_PASSWORD}

# 好（GOOD）：Spring Cloud Vault 集成
spring:
  cloud:
    vault:
      uri: https://vault.example.com
      token: ${VAULT_TOKEN}
```

## 安全响应头（Security Headers）

```java
http
  .headers(headers -> headers
    .contentSecurityPolicy(csp -> csp
      .policyDirectives("default-src 'self'"))
    .frameOptions(HeadersConfigurer.FrameOptionsConfig::sameOrigin)
    .xssProtection(Customizer.withDefaults())
    .referrerPolicy(rp -> rp.policy(ReferrerPolicyHeaderWriter.ReferrerPolicy.NO_REFERRER)));
```

## CORS 配置

- 在安全过滤器（Security Filter）级别配置 CORS，而不是按控制器配置
- 限制允许的源（Origins） —— 在生产环境中严禁使用 `*`

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
  CorsConfiguration config = new CorsConfiguration();
  config.setAllowedOrigins(List.of("https://app.example.com"));
  config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
  config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
  config.setAllowCredentials(true);
  config.setMaxAge(3600L);

  UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
  source.registerCorsConfiguration("/api/**", config);
  return source;
}

// 在 SecurityFilterChain 中：
http.cors(cors -> cors.configurationSource(corsConfigurationSource()));
```

## 速率限制（Rate Limiting）

- 在高开销端点上应用 Bucket4j 或网关级限制
- 对爆发性请求进行日志记录和告警；返回 429 错误并提供重试提示

```java
// 使用 Bucket4j 进行单端点速率限制
@Component
public class RateLimitFilter extends OncePerRequestFilter {
  private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();

  private Bucket createBucket() {
    return Bucket.builder()
        .addLimit(Bandwidth.classic(100, Refill.intervally(100, Duration.ofMinutes(1))))
        .build();
  }

  @Override
  protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
      FilterChain chain) throws ServletException, IOException {
    String clientIp = request.getRemoteAddr();
    Bucket bucket = buckets.computeIfAbsent(clientIp, k -> createBucket());

    if (bucket.tryConsume(1)) {
      chain.doFilter(request, response);
    } else {
      response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
      response.getWriter().write("{\"error\": \"Rate limit exceeded\"}");
    }
  }
}
```

## 依赖安全（Dependency Security）

- 在 CI 中运行 OWASP Dependency Check / Snyk
- 保持 Spring Boot 和 Spring Security 处于受支持的版本
- 在发现已知 CVE 时终止构建（Fail build）

## 日志与 PII（个人身份信息）

- 严禁记录机密信息、令牌、密码或完整的银行卡号（PAN）数据
- 对敏感字段进行脱敏（Redact）；使用结构化 JSON 日志

## 文件上传（File Uploads）

- 校验文件大小、内容类型（Content Type）和扩展名
- 存储在 Web 根目录之外；根据需要进行病毒扫描

## 发布前清单（Checklist Before Release）

- [ ] 身份验证令牌已校验且正确过期
- [ ] 每个敏感路径都有授权防护
- [ ] 所有输入均已校验和清理
- [ ] 无字符串拼接的 SQL
- [ ] CSRF 策略符合应用类型
- [ ] 机密信息已外置；未提交到仓库
- [ ] 已配置安全响应头
- [ ] API 已设置速率限制
- [ ] 依赖项已扫描且处于最新状态
- [ ] 日志中不含敏感数据

**记住**：遵循默认拒绝、校验输入、最小权限原则，并优先通过配置实现安全。