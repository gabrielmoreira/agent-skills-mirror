---
name: jpa-patterns
description: JPA/Hibernate 模式，涵盖 Spring Boot 中的实体设计、关系、查询优化、事务、审计、索引、分页和连接池。
origin: ECC
---

# JPA/Hibernate 模式

用于 Spring Boot 中的数据建模、仓库层（Repositories）实现和性能调优。

## 何时激活

- 设计 JPA 实体（Entities）和表映射
- 定义关联关系（@OneToMany、@ManyToOne、@ManyToMany）
- 优化查询（防止 N+1 问题、抓取策略、投影）
- 配置事务、审计（Auditing）或逻辑删除
- 设置分页、排序或自定义 Repository 方法
- 调优连接池（HikariCP）或二级缓存（Second-level Caching）

## 实体设计

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

启用审计（Auditing）：
```java
@Configuration
@EnableJpaAuditing
class JpaConfig {}
```

## 关联关系与防止 N+1 问题

```java
@OneToMany(mappedBy = "market", cascade = CascadeType.ALL, orphanRemoval = true)
private List<PositionEntity> positions = new ArrayList<>();
```

- 默认使用延迟加载（Lazy Loading）；必要时在查询中使用 `JOIN FETCH`
- 避免在集合上使用 `EAGER`；在读取路径中使用 DTO 投影（Projections）

```java
@Query("select m from MarketEntity m left join fetch m.positions where m.id = :id")
Optional<MarketEntity> findWithPositions(@Param("id") Long id);
```

## Repository 模式

```java
public interface MarketRepository extends JpaRepository<MarketEntity, Long> {
  Optional<MarketEntity> findBySlug(String slug);

  @Query("select m from MarketEntity m where m.status = :status")
  Page<MarketEntity> findByStatus(@Param("status") MarketStatus status, Pageable pageable);
}
```

- 对轻量级查询使用投影（Projections）：
```java
public interface MarketSummary {
  Long getId();
  String getName();
  MarketStatus getStatus();
}
Page<MarketSummary> findAllBy(Pageable pageable);
```

## 事务

- 在 Service 方法上添加 `@Transactional` 注解
- 在读取路径上使用 `@Transactional(readOnly = true)` 以进行优化
- 谨慎选择传播行为（Propagation）；避免长事务

```java
@Transactional
public Market updateStatus(Long id, MarketStatus status) {
  MarketEntity entity = repo.findById(id)
      .orElseThrow(() -> new EntityNotFoundException("Market"));
  entity.setStatus(status);
  return Market.from(entity);
}
```

## 分页

```java
PageRequest page = PageRequest.of(pageNumber, pageSize, Sort.by("createdAt").descending());
Page<MarketEntity> markets = repo.findByStatus(MarketStatus.ACTIVE, page);
```

对于类游标分页（Cursor-like pagination），在 JPQL 中包含 `id > :lastId` 并配合排序。

## 索引与性能

- 为常用过滤器（`status`、`slug`、外键）添加索引
- 使用匹配查询模式的复合索引（`status, created_at`）
- 避免使用 `select *`；仅投影所需的列
- 使用 `saveAll` 和 `hibernate.jdbc.batch_size` 进行批量写入

## 连接池 (HikariCP)

推荐属性配置：
```
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=30000
spring.datasource.hikari.validation-timeout=5000
```

对于 PostgreSQL 的 LOB 处理，添加：
```
spring.jpa.properties.hibernate.jdbc.lob.non_contextual_creation=true
```

## 缓存

- 一级缓存（1st-level cache）是基于 EntityManager 的；避免跨事务保留实体
- 对于读多写少的实体，谨慎考虑二级缓存（Second-level cache）；验证逐出策略（Eviction Strategy）

## 数据库迁移 (Migrations)

- 使用 Flyway 或 Liquibase；生产环境绝不依赖 Hibernate 的自动 DDL（auto DDL）
- 保持迁移脚本的幂等性和增量性；避免在没有计划的情况下删除列

## 测试数据访问

- 优先使用 `@DataJpaTest` 配合 Testcontainers 以镜像生产环境
- 通过日志断言 SQL 效率：设置 `logging.level.org.hibernate.SQL=DEBUG` 以及针对参数值的 `logging.level.org.hibernate.orm.jdbc.bind=TRACE`

**记住**：保持实体精简、查询意图明确、事务简短。通过抓取策略和投影防止 N+1 问题，并为读/写路径建立索引。
