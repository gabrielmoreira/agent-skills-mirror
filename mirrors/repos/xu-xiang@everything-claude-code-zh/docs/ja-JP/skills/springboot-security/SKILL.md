---
name: springboot-security
description: Spring Boot 服务的 Spring Security 身份验证/授权、验证、CSRF、密钥、响应头、速率限制和依赖项安全最佳实践。
---

# Spring Boot 安全审查

在添加身份验证、处理输入、创建端点或处理敏感密钥时使用。

## 身份验证（Authentication）

- 优先使用无状态 JWT 或带有吊销列表的不透明令牌（Opaque Token）
- 对于会话，使用 `httpOnly`、`Secure`、`SameSite=Strict` 的 Cookie
- 在 `OncePerRequestFilter` 或资源服务器中验证令牌

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

- 启用方法级安全：`@EnableMethodSecurity`
- 使用 `@PreAuthorize("hasRole('ADMIN')")` 或 `@PreAuthorize("@authz.canEdit(#id)")`
- 默认拒绝访问，仅公开必要的范围（Scope）

## 输入验证（Input Validation）

- 在控制器中使用 `@Valid` 进行 Bean Validation
- 在 DTO 上应用约束：`@NotBlank`、`@Email`、`@Size` 以及自定义校验器
- 在渲染前使用白名单对 HTML 进行清理（Sanitize）

## SQL 注入防护

- 使用 Spring Data Repository 或参数化查询
- 原生查询使用 `:param` 绑定，禁止字符串拼接

## CSRF 防护

- 对于浏览器会话应用，启用 CSRF 并在表单/响应头中包含令牌
- 对于使用 Bearer 令牌的纯 API 应用，禁用 CSRF 并依赖无状态身份验证

```java
http
  .csrf(csrf -> csrf.disable())
  .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS));
```

## 密钥管理（Secrets Management）

- 禁止在源码中包含密钥。从环境变量或 Vault 加载
- 确保 `application.yml` 中不含凭据，使用占位符代替
- 定期轮换令牌和数据库凭证

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

## 速率限制（Rate Limiting）

- 对高成本端点应用 Bucket4j 或网关级限制
- 记录突发流量日志并发送告警，返回带有重试提示的 429 状态码

## 依赖项安全（Dependency Security）

- 在 CI 中运行 OWASP Dependency Check / Snyk
- 保持 Spring Boot 和 Spring Security 处于受支持的版本
- 针对已知的 CVE 漏洞使构建失败

## 日志与 PII（个人识别信息）

- 禁止在日志中记录密钥、令牌、密码或完整的银行卡号（PAN）数据
- 脱敏敏感字段，并使用结构化 JSON 日志

## 文件上传

- 验证文件大小、内容类型（Content-Type）和扩展名
- 存储在 Web 根目录之外，并根据需要进行扫描

## 发布前检查清单

- [ ] 身份验证令牌已正确验证且未过期
- [ ] 所有敏感路径都有授权保护（Authorization Guard）
- [ ] 所有输入已验证并清理
- [ ] 没有通过字符串拼接的 SQL 语句
- [ ] 针对应用类型采用了正确的 CSRF 对策
- [ ] 密钥已外部化，未提交至仓库
- [ ] 已配置安全响应头
- [ ] API 设有速率限制
- [ ] 依赖项已扫描且为最新版本
- [ ] 日志中不含敏感数据

**注意**：默认拒绝（Default Deny）、验证输入、应用最小权限原则，并优先采用“配置即安全”的实践。
