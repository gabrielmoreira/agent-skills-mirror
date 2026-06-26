---
name: jpa-patterns
description: Spring Boot 中用于实体设计、关联关系、查询优化、事务、审计、索引、分页和连接池的 JPA/Hibernate 模式。
---

# JPA/Hibernate 模式

用于 Spring Boot 中的数据建模、存储库（Repository）和性能调优。

## 实体设计 (Entity Design)

```java
@Entity
@Table(name = "markets", indexes = {
  @Index(name = "idx_markets_slug", columnList = "slug", unique = true)
})
@EntityListeners(AuditingEntityListener.class)
public class MarketEntity {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable = false, length = 200)
  private String name;

  @Column(nullable = false, unique = true, length = 120)
  private String slug;

  @Enumerated(EnumType.STRING)
  private MarketStatus status = MarketStatus.ACTIVE;

  @CreatedDate private Instant createdAt;
  @LastModifiedDate private Instant updatedAt;
}
```

启用审计 (Auditing):
```java
@Configuration
@EnableJpaAuditing
class JpaConfig {}
```

## 关联关系与 N+1 问题预防

```java
@OneToMany(mappedBy = "market", cascade = CascadeType.ALL, orphanRemoval = true)
private List<PositionEntity> positions = new ArrayList<>();
```

- 默认使用延迟加载（Lazy Loading）。根据需要，在查询中使用 `JOIN FETCH`。
- 集合属性应避免使用 `EAGER` 加载，在读取路径中优先使用 DTO 投影（Projection）。

```java
@Query("select m from MarketEntity m left join fetch m.positions where m.id = :id")
Optional<MarketEntity> findWithPositions(@Param("id") Long id);
```

## 存储库模式 (Repository Pattern)

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  Optional<MarketEntity> findBySlug(String slug);

  @Query("select m from MarketEntity m where m.status = :status")
  Page<MarketEntity> findByStatus(@Param("status") MarketStatus status, Pageable pageable);
}
```

- 对于轻量级查询，请使用投影（Projection）:
```java
public interface MarketSummary {
  Long getId();
  String getName();
  MarketStatus getStatus();
}
Page<MarketSummary> findAllBy(Pageable pageable);
```

## 事务 (Transactions)

- 在服务层（Service）方法上添加 `@Transactional` 注解。
- 使用 `@Transactional(readOnly = true)` 优化只读路径。
- 谨慎选择事务传播（Propagation）行为。避免长时间运行的事务。

```java
@Transactional
public Market updateStatus(Long id, MarketStatus status) {
  MarketEntity entity = repo.findById(id)
      .orElseThrow(() -> new EntityNotFoundException("Market"));
  entity.setStatus(status);
  return Market.from(entity);
}
```

## 分页 (Pagination)

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<MarketEntity> markets = repo.findByStatus(MarketStatus.ACTIVE, page);
```

对于类似游标（Cursor）的分页，请在 JPQL 排序中包含 `id > :lastId`。

## 索引创建与性能优化

- 为常用过滤器（如 `status`、`slug`、外键）添加索引。
- 使用符合查询模式的复合索引（例如 `status, created_at`）。
- 避免使用 `select *`，仅投影必要的列。
- 利用 `saveAll` 和 `hibernate.jdbc.batch_size` 进行批量写入。

## 连接池 (Connection Pooling - HikariCP)

推荐属性:
```
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.validation-timeout=5000
```

对于 PostgreSQL 的 LOB 处理，请添加以下内容:
```
spring.jpa.properties.hibernate.jdbc.lob.non_contextual_creation=true
```

## 缓存 (Caching)

- 一级缓存（First-level Cache）是基于 EntityManager 的。不要在事务之间持有实体。
- 对于读取密集型实体，请谨慎考虑二级缓存（Second-level Cache）。验证淘汰策略（Eviction Strategy）。

## 数据库迁移 (Migration)

- 使用 Flyway 或 Liquibase。不要在生产环境中依赖 Hibernate 的自动 DDL。
- 保持迁移脚本的幂等性（Idempotent）和增量性。不要在未规划的情况下删除列。

## 数据访问测试

- 优先使用配合 Testcontainers 的 `@DataJpaTest`，以真实反映生产环境。
- 通过日志断言 SQL 效率：将 `logging.level.org.hibernate.SQL` 设置为 `DEBUG`，将 `logging.level.org.hibernate.orm.jdbc.bind` 设置为 `TRACE` 以查看参数值。

**注意**：保持实体轻量化，确保查询意图明确，并缩短事务时长。通过抓取策略（Fetch Strategy）和投影（Projection）防止 N+1 问题，并为读/写路径创建索引。
