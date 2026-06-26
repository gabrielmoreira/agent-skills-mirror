---
name: springboot-verification
description: "Spring Boot 项目验证循环：包含构建、静态分析、带覆盖率的测试、安全扫描，以及发布或 PR 前的差异审查。"
origin: ECC
---

# Spring Boot 验证循环 (Verification Loop)

在合并请求 (PR) 之前、重大变更之后以及部署前运行。

## 触发时机

- 在为 Spring Boot 服务开启合并请求 (Pull Request) 之前
- 在重大重构 (Refactoring) 或依赖 (Dependency) 升级之后
- 预发布或生产环境部署 (Deployment) 前的验证
- 运行完整的 构建 (Build) → 代码检查 (Lint) → 测试 (Test) → 安全扫描 (Security Scan) 流水线 (Pipeline)
- 验证测试覆盖率 (Test Coverage) 是否达到阈值

## 第一阶段：构建 (Build)

```bash
mvn -T 4 clean verify -DskipTests
# 或者
./gradlew clean assemble -x test
```

如果构建失败，请停止并修复。

## 第二阶段：静态分析 (Static Analysis)

Maven（常用插件）：
```bash
mvn -T 4 spotbugs:check pmd:check checkstyle:check
```

Gradle（如果已配置）：
```bash
./gradlew checkstyleMain pmdMain spotbugsMain
```

## 第三阶段：测试与覆盖率 (Tests + Coverage)

```bash
mvn -T 4 test
mvn jacoco:report   # 验证 80% 以上的覆盖率
# 或者
./gradlew test jacocoTestReport
```

报告内容：
- 测试总数、通过/失败数
- 覆盖率 %（行/分支）

### 单元测试 (Unit Tests)

通过模拟依赖 (Mocked dependencies) 隔离测试服务逻辑：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

  @Mock private UserRepository userRepository;
  @InjectMocks private UserService userService;

  @Test
  void createUser_validInput_returnsUser() {
    var dto = new CreateUserDto("Alice", "alice@example.com");
    var expected = new User(1L, "Alice", "alice@example.com");
    when(userRepository.save(any(User.class))).thenReturn(expected);

    var result = userService.create(dto);

    assertThat(result.name()).isEqualTo("Alice");
    verify(userRepository).save(any(User.class));
  }

  @Test
  void createUser_duplicateEmail_throwsException() {
    var dto = new CreateUserDto("Alice", "existing@example.com");
    when(userRepository.existsByEmail(dto.email())).thenReturn(true);

    assertThatThrownBy(() -> userService.create(dto))
        .isInstanceOf(DuplicateEmailException.class);
  }
}
```

### 使用 Testcontainers 进行集成测试 (Integration Tests)

针对真实数据库而非 H2 进行测试：

```java
@SpringBootTest
@Testcontainers
class UserRepositoryIntegrationTest {

  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
      .withDatabaseName("testdb");

  @DynamicPropertySource
  static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
  }

  @Autowired private UserRepository userRepository;

  @Test
  void findByEmail_existingUser_returnsUser() {
    userRepository.save(new User("Alice", "alice@example.com"));

    var found = userRepository.findByEmail("alice@example.com");

    assertThat(found).isPresent();
    assertThat(found.get().getName()).isEqualTo("Alice");
  }
}
```

### 使用 MockMvc 进行 API 测试 (API Tests)

在完整的 Spring 上下文中测试控制层 (Controller layer)：

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

  @Autowired private MockMvc mockMvc;
  @MockBean private UserService userService;

  @Test
  void createUser_validInput_returns201() throws Exception {
    var user = new UserDto(1L, "Alice", "alice@example.com");
    when(userService.create(any())).thenReturn(user);

    mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"name": "Alice", "email": "alice@example.com"}
                """))
        .andExpect(status().isCreated())
        .andExpect(jsonPath("$.name").value("Alice"));
  }

  @Test
  void createUser_invalidEmail_returns400() throws Exception {
    mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"name": "Alice", "email": "not-an-email"}
                """))
        .andExpect(status().isBadRequest());
  }
}
```

## 第四阶段：安全扫描 (Security Scan)

```bash
# 依赖项 CVE 漏洞扫描
mvn org.owasp:dependency-check-maven:check
# 或者
./gradlew dependencyCheckAnalyze

# 源码中的密钥/敏感信息 (Secrets)
grep -rn "password\s*=\s*\"" src/ --include="*.java" --include="*.yml" --include="*.properties"
grep -rn "sk-\|api_key\|secret" src/ --include="*.java" --include="*.yml"

# 密钥/敏感信息 (Git 历史记录)
git secrets --scan  # 如果已配置
```

### 常见安全问题检查

```
# 检查 System.out.println (应使用 logger 代替)
grep -rn "System\.out\.print" src/main/ --include="*.java"

# 检查响应中是否包含原始异常信息
grep -rn "e\.getMessage()" src/main/ --include="*.java"

# 检查通配符 CORS 配置
grep -rn "allowedOrigins.*\*" src/main/ --include="*.java"
```

## 第五阶段：代码检查/格式化 (Lint/Format)（可选关卡）

```bash
mvn spotless:apply   # 如果使用了 Spotless 插件
./gradlew spotlessApply
```

## 第六阶段：差异审查 (Diff Review)

```bash
git diff --stat
git diff
```

检查清单：
- 未遗留调试日志（`System.out`，无守卫的 `log.debug`）
- 错误信息和 HTTP 状态码具有明确意义
- 在需要的地方包含事务 (Transactions) 和校验 (Validation)
- 配置变更已记录文档

## 输出模板

```
验证报告 (VERIFICATION REPORT)
===================
构建 (Build):     [通过/失败]
静态分析 (Static): [通过/失败] (spotbugs/pmd/checkstyle)
测试 (Tests):     [通过/失败] (X/Y 通过, Z% 覆盖率)
安全 (Security):  [通过/失败] (CVE 漏洞发现: N)
差异 (Diff):      [X 个文件已变更]

总体状态 (Overall): [准备就绪 / 尚未就绪]

待修复问题：
1. ...
2. ...
```

## 持续模式 (Continuous Mode)

- 在发生重大变更时，或在长会话期间每 30–60 分钟重新运行各阶段。
- 保持短循环：运行 `mvn -T 4 test` + spotbugs 以获取快速反馈。

**请记住**：快速反馈优于后期“惊喜”。保持关卡严格——在生产系统中，将警告视为缺陷。
