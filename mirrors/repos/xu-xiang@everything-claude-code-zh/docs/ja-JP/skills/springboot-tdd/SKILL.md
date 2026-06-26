---
name: springboot-tdd
description: 使用 JUnit 5, Mockito, MockMvc, Testcontainers 和 JaCoCo 进行 Spring Boot 的测试驱动开发（TDD）。适用于添加新功能、修复 bug 或重构场景。
---

# Spring Boot TDD 工作流 (Spring Boot TDD Workflow)

为 Spring Boot 服务提供测试驱动开发（TDD）指南，要求覆盖率达到 80% 以上（单元测试 + 集成测试）。

## 何时使用

- 新功能或新端点（Endpoint）
- Bug 修复或重构
- 添加数据访问逻辑或安全规则

## 工作流 (Workflow)

1) 先写测试（且测试应当失败）
2) 实现能让测试通过的最小化代码
3) 在保持测试通过（Green）的状态下进行重构
4) 强制执行覆盖率检查（JaCoCo）

## 单元测试 (Unit Testing - JUnit 5 + Mockito)

```java
@ExtendWith(MockitoExtension.class)
class MarketServiceTest {
  @Mock MarketRepository repo;
  @InjectMocks MarketService service;

  @Test
  void createsMarket() {
    CreateMarketRequest req = new CreateMarketRequest("name", "desc", Instant.now(), List.of("cat"));
    when(repo.save(any())).thenAnswer(inv -> inv.getArgument(0));

    Market result = service.create(req);

    assertThat(result.name()).isEqualTo("name");
    verify(repo).save(any());
  }
}
```

模式：
- Arrange-Act-Assert (准备-执行-断言)
- 避免使用部分 Mock（Partial Mock），优先使用显式打桩（Stubbing）
- 针对多种变体情况使用 `@ParameterizedTest`

## Web 层测试 (Web Layer Testing - MockMvc)

```java
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;

  @Test
  void returnsMarkets() throws Exception {
    when(marketService.list(any())).thenReturn(Page.empty());

    mockMvc.perform(get("/api/markets"))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.content").isArray());
  }
}
```

## 集成测试 (Integration Testing - SpringBootTest)

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class MarketIntegrationTest {
  @Autowired MockMvc mockMvc;

  @Test
  void createsMarket() throws Exception {
    mockMvc.perform(post("/api/markets")
        .contentType(MediaType.APPLICATION_JSON)
        .content("""
          {"name":"Test","description":"Desc","endDate":"2030-01-01T00:00:00Z","categories":["general"]}
        """))
      .andExpect(status().isCreated());
  }
}
```

## 持久化测试 (Persistence Testing - DataJpaTest)

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(TestContainersConfig.class)
class MarketRepositoryTest {
  @Autowired MarketRepository repo;

  @Test
  void savesAndFinds() {
    MarketEntity entity = new MarketEntity();
    entity.setName("Test");
    repo.save(entity);

    Optional<MarketEntity> found = repo.findByName("Test");
    assertThat(found).isPresent();
  }
}
```

## Testcontainers

- 使用可复用的 Postgres/Redis 容器以反映生产环境
- 通过 `@DynamicPropertySource` 将 JDBC URL 注入 Spring 上下文 (Context)

## 覆盖率 (Coverage - JaCoCo)

Maven 代码片段：
```xml
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <version>0.8.14</version>
  <executions>
    <execution>
      <goals><goal>prepare-agent</goal></goals>
    </execution>
    <execution>
      <id>report</id>
      <phase>verify</phase>
      <goals><goal>report</goal></goals>
    </execution>
  </executions>
</plugin>
```

## 断言 (Assertions)

- 为了可读性，优先使用 AssertJ (`assertThat`)
- 对于 JSON 响应使用 `jsonPath`
- 对于异常：`assertThatThrownBy(...)`

## 测试数据生成器 (Test Data Builder)

```java
class MarketBuilder {
  private String name = "Test";
  MarketBuilder withName(String name) { this.name = name; return this; }
  Market build() { return new Market(null, name, MarketStatus.ACTIVE); }
}
```

## CI 命令 (CI Commands)

- Maven: `mvn -T 4 test` 或 `mvn verify`
- Gradle: `./gradlew test jacocoTestReport`

**请记住**：保持测试的高速、隔离和确定性。测试行为而非实现细节。
