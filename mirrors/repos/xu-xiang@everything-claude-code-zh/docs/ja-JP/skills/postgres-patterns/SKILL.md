---
name: postgres-patterns
description: PostgreSQL 数据库模式，涵盖查询优化、架构设计、索引和安全。基于 Supabase 最佳实践。
---

# PostgreSQL 模式 (Patterns)

PostgreSQL 最佳实践快速参考。如需详细指导，请使用 `database-reviewer` 智能体 (Agent)。

## 触发时机

- 创建 SQL 查询或迁移 (Migration) 时
- 设计数据库架构 (Schema) 时
- 排查低速查询时
- 实现行级安全 (Row Level Security) 时
- 配置连接池 (Connection Pooling) 时

## 快速参考

### 索引速查表 (Index Cheat Sheet)

| 查询模式 | 索引类型 | 示例 |
|--------------|------------|---------|
| `WHERE col = value` | B-tree（默认） | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | 复合索引 (Composite) | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| 时序范围 | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

### 数据类型快速参考

| 用途 | 正确类型 | 应当避免 |
|----------|-------------|-------|
| ID | `bigint` | `int`、随机 UUID |
| 字符串 | `text` | `varchar(255)` |
| 时间戳 | `timestamptz` | `timestamp` |
| 金额 | `numeric(10,2)` | `float` |
| 标志位 | `boolean` | `varchar`、`int` |

### 常用模式

**复合索引顺序:**
```sql
-- 等值列在前，范围列在后
CREATE INDEX idx ON orders (status, created_at);
-- 适用于: WHERE status = 'pending' AND created_at > '2024-01-01'
```

**覆盖索引 (Covering Index):**
```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- 避免针对 email, name, created_at 的表查找 (Table scan)
```

**部分索引 (Partial Index):**
```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- 索引更小，仅包含活跃用户
```

**RLS 策略（优化）:**
```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- 使用 SELECT 包装！
```

**UPSERT:**
```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

**游标分页 (Cursor Pagination):**
```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
-- O(1) 对比 OFFSET 的 O(n)
```

**队列处理 (Queue Processing):**
```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

### 反模式 (Anti-patterns) 检测

```sql
-- 查找没有索引的外键
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- 查找低速查询
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- 检查表膨胀 (Table Bloat)
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 配置模板

```sql
-- 连接限制（根据 RAM 调整）
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- 超时设置
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- 监控
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 安全默认值
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

## 相关

- 智能体 (Agent): `database-reviewer` - 完整的数据库评审工作流
- 技能 (Skill): `clickhouse-io` - ClickHouse 分析模式
- 技能 (Skill): `backend-patterns` - API 和后端模式

---

*基于 [Supabase Agent Skills](Supabase Agent Skills (credit: Supabase team))（MIT 许可证）*
