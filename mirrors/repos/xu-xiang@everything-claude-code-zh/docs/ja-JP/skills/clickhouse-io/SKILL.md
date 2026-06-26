---
name: clickhouse-io
description: ClickHouse 数据库模式、查询优化、分析以及高性能分析工作负载的数据工程最佳实践。
---

# ClickHouse 分析模式

针对高性能分析和数据工程的 ClickHouse 特定模式。

## 概览

ClickHouse 是一个用于联机分析处理（OLAP）的列式数据库管理系统（DBMS）。它针对大规模数据集上的快速分析查询进行了优化。

**主要功能：**
- 列式存储
- 数据压缩
- 并行查询执行
- 分布式查询
- 实时分析

## 表设计模式

### MergeTree 引擎（最常用）

```sql
CREATE TABLE markets_analytics (
    date Date,
    market_id String,
    market_name String,
    volume UInt64,
    trades UInt32,
    unique_traders UInt32,
    avg_trade_size Float64,
    created_at DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, market_id)
SETTINGS index_granularity = 8192;
```

### ReplacingMergeTree (重复数据删除)

```sql
-- 用于可能存在重复的数据（如来自多个源的数据）
CREATE TABLE user_events (
    event_id String,
    user_id String,
    event_type String,
    timestamp DateTime,
    properties String
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, event_id, timestamp)
PRIMARY KEY (user_id, event_id);
```

### AggregatingMergeTree (预聚合)

```sql
-- 用于维护聚合指标
CREATE TABLE market_stats_hourly (
    hour DateTime,
    market_id String,
    total_volume AggregateFunction(sum, UInt64),
    total_trades AggregateFunction(count, UInt32),
    unique_users AggregateFunction(uniq, String)
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, market_id);

-- 查询聚合数据
SELECT
    hour,
    market_id,
    sumMerge(total_volume) AS volume,
    countMerge(total_trades) AS trades,
    uniqMerge(unique_users) AS users
FROM market_stats_hourly
WHERE hour >= toStartOfHour(now() - INTERVAL 24 HOUR)
GROUP BY hour, market_id
ORDER BY hour DESC;
```

## 查询优化模式

### 高效过滤

```sql
-- ✅ 推荐：优先使用索引列
SELECT *
FROM markets_analytics
WHERE date >= '2025-01-01'
  AND market_id = 'market-123'
  AND volume > 1000
ORDER BY date DESC
LIMIT 100;

-- ❌ 不推荐：先过滤非索引列
SELECT *
FROM markets_analytics
WHERE volume > 1000
  AND market_name LIKE '%election%'
  AND date >= '2025-01-01';
```

### 聚合

```sql
-- ✅ 推荐：使用 ClickHouse 特有的聚合函数
SELECT
    toStartOfDay(created_at) AS day,
    market_id,
    sum(volume) AS total_volume,
    count() AS total_trades,
    uniq(trader_id) AS unique_traders,
    avg(trade_size) AS avg_size
FROM trades
WHERE created_at >= today() - INTERVAL 7 DAY
GROUP BY day, market_id
ORDER BY day DESC, total_volume DESC;

-- ✅ 计算分位数请使用 quantile（比 percentile 更高效）
SELECT
    quantile(0.50)(trade_size) AS median,
    quantile(0.95)(trade_size) AS p95,
    quantile(0.99)(trade_size) AS p99
FROM trades
WHERE created_at >= now() - INTERVAL 1 HOUR;
```

### 窗口函数 (Window Functions)

```sql
-- 累计计算
SELECT
    date,
    market_id,
    volume,
    sum(volume) OVER (
        PARTITION BY market_id
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_volume
FROM markets_analytics
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY market_id, date;
```

## 数据插入模式

### 批量插入 (推荐)

```typescript
import { ClickHouse } from 'clickhouse'

const clickhouse = new ClickHouse({
  url: process.env.CLICKHOUSE_URL,
  port: 8123,
  basicAuth: {
    username: process.env.CLICKHOUSE_USER,
    password: process.env.CLICKHOUSE_PASSWORD
  }
})

// ✅ 批量插入（高效）
async function bulkInsertTrades(trades: Trade[]) {
  const values = trades.map(trade => `(
    '${trade.id}',
    '${trade.market_id}',
    '${trade.user_id}',
    ${trade.amount},
    '${trade.timestamp.toISOString()}'
  )`).join(',')

  await clickhouse.query(`
    INSERT INTO trades (id, market_id, user_id, amount, timestamp)
    VALUES ${values}
  `).toPromise()
}

// ❌ 逐条插入（低效）
async function insertTrade(trade: Trade) {
  // 请勿在循环中执行此操作！
  await clickhouse.query(`
    INSERT INTO trades VALUES ('${trade.id}', ...)
  `).toPromise()
}
```

### 流式插入

```typescript
// 用于持续的数据摄取
import { createWriteStream } from 'fs'
import { pipeline } from 'stream/promises'

async function streamInserts() {
  const stream = clickhouse.insert('trades').stream()

  for await (const batch of dataSource) {
    stream.write(batch)
  }

  await stream.end()
}
```

## 物化视图 (Materialized Views)

### 实时聚合

```sql
-- 创建按小时统计的物化视图
CREATE MATERIALIZED VIEW market_stats_hourly_mv
TO market_stats_hourly
AS SELECT
    toStartOfHour(timestamp) AS hour,
    market_id,
    sumState(amount) AS total_volume,
    countState() AS total_trades,
    uniqState(user_id) AS unique_users
FROM trades
GROUP BY hour, market_id;

-- 查询物化视图
SELECT
    hour,
    market_id,
    sumMerge(total_volume) AS volume,
    countMerge(total_trades) AS trades,
    uniqMerge(unique_users) AS users
FROM market_stats_hourly
WHERE hour >= now() - INTERVAL 24 HOUR
GROUP BY hour, market_id;
```

## 性能监控

### 查询性能

```sql
-- 检查慢查询
SELECT
    query_id,
    user,
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage
FROM system.query_log
WHERE type = 'QueryFinish'
  AND query_duration_ms > 1000
  AND event_time >= now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### 表统计信息

```sql
-- 检查表大小
SELECT
    database,
    table,
    formatReadableSize(sum(bytes)) AS size,
    sum(rows) AS rows,
    max(modification_time) AS latest_modification
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes) DESC;
```

## 常见分析查询

### 时序分析

```sql
-- 日活跃用户 (DAU)
SELECT
    toDate(timestamp) AS date,
    uniq(user_id) AS daily_active_users
FROM events
WHERE timestamp >= today() - INTERVAL 30 DAY
GROUP BY date
ORDER BY date;

-- 留存分析
SELECT
    signup_date,
    countIf(days_since_signup = 0) AS day_0,
    countIf(days_since_signup = 1) AS day_1,
    countIf(days_since_signup = 7) AS day_7,
    countIf(days_since_signup = 30) AS day_30
FROM (
    SELECT
        user_id,
        min(toDate(timestamp)) AS signup_date,
        toDate(timestamp) AS activity_date,
        dateDiff('day', signup_date, activity_date) AS days_since_signup
    FROM events
    GROUP BY user_id, activity_date
)
GROUP BY signup_date
ORDER BY signup_date DESC;
```

### 漏斗分析 (Funnel Analysis)

```sql
-- 转化漏斗
SELECT
    countIf(step = 'viewed_market') AS viewed,
    countIf(step = 'clicked_trade') AS clicked,
    countIf(step = 'completed_trade') AS completed,
    round(clicked / viewed * 100, 2) AS view_to_click_rate,
    round(completed / clicked * 100, 2) AS click_to_completion_rate
FROM (
    SELECT
        user_id,
        session_id,
        event_type AS step
    FROM events
    WHERE event_date = today()
)
GROUP BY session_id;
```

### 同期群分析 (Cohort Analysis)

```sql
-- 按注册月份划分的用户同期群
SELECT
    toStartOfMonth(signup_date) AS cohort,
    toStartOfMonth(activity_date) AS month,
    dateDiff('month', cohort, month) AS months_since_signup,
    count(DISTINCT user_id) AS active_users
FROM (
    SELECT
        user_id,
        min(toDate(timestamp)) OVER (PARTITION BY user_id) AS signup_date,
        toDate(timestamp) AS activity_date
    FROM events
)
GROUP BY cohort, month, months_since_signup
ORDER BY cohort, months_since_signup;
```

## 数据流水线模式 (Data Pipeline Patterns)

### ETL 模式

```typescript
// 提取、转换、加载 (Extract, Transform, Load)
async function etlPipeline() {
  // 1. 从源提取
  const rawData = await extractFromPostgres()

  // 2. 转换
  const transformed = rawData.map(row => ({
    date: new Date(row.created_at).toISOString().split('T')[0],
    market_id: row.market_slug,
    volume: parseFloat(row.total_volume),
    trades: parseInt(row.trade_count)
  }))

  // 3. 加载到 ClickHouse
  await bulkInsertToClickHouse(transformed)
}

// 定期执行
setInterval(etlPipeline, 60 * 60 * 1000)  // 每 1 小时一次
```

### 变更数据捕获 (CDC)

```typescript
// 监听 PostgreSQL 变更并同步到 ClickHouse
import { Client } from 'pg'

const pgClient = new Client({ connectionString: process.env.DATABASE_URL })

pgClient.query('LISTEN market_updates')

pgClient.on('notification', async (msg) => {
  const update = JSON.parse(msg.payload)

  await clickhouse.insert('market_updates', [
    {
      market_id: update.id,
      event_type: update.operation,  // INSERT, UPDATE, DELETE
      timestamp: new Date(),
      data: JSON.stringify(update.new_data)
    }
  ])
})
```

## 最佳实践

### 1. 分区策略
- 按时间分区（通常是月或日）
- 避免分区过多（会影响性能）
- 分区键应使用 DATE 类型

### 2. 排序键 (Sorting Key)
- 将最常过滤的列放在前面
- 考虑基数（优先放置高基数列）
- 顺序会影响压缩率

### 3. 数据类型
- 使用最小且合适的类型（如 UInt32 vs UInt64）
- 对于重复出现的字符串使用 LowCardinality
- 对于分类数据使用 Enum

### 4. 应当避免的操作
- 使用 SELECT *（应指定具体列）
- 使用 FINAL（建议在查询前合并数据）
- 使用过多的 JOIN（应针对分析进行反规范化）
- 频繁的小批量插入（应改用大批量处理）

### 5. 监控
- 跟踪查询性能
- 监控磁盘使用情况
- 检查合并（Merge）操作
- 查看慢查询日志

**注意**：ClickHouse 在分析工作负载方面表现出色。请根据查询模式设计表结构，采用批量插入，并利用物化视图进行实时聚合。
