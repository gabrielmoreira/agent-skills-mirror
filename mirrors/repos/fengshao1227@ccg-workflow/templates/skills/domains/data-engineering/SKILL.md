---
name: data-engineering
description: 数据工程。Airflow、Dagster、Kafka Streams、Flink、dbt、数据管道、流处理、数据质量。当用户提到数据管道、ETL、流处理、数据质量时路由到此。
license: MIT
user-invocable: false
disable-model-invocation: false
---

# 数据工程域 · Data Engineering

## 域概览

数据工程域涵盖数据管道编排、流式处理、数据质量保障三大核心领域。

```
数据管道层                流处理层              质量保障层
├── Airflow (调度编排)    ├── Kafka Streams     ├── Great Expectations
├── Dagster (资产管理)    ├── Flink             ├── dbt
└── Prefect (现代工作流)  └── Spark Streaming   └── Soda Core
```

---

## 数据管道编排

### 框架对比

| 特性 | Airflow | Dagster | Prefect |
|------|---------|---------|---------|
| 核心模型 | DAG + Task | Asset + Op | Flow + Task |
| 学习曲线 | 陡峭 | 中等 | 平缓 |
| 资产管理 | 无 | 原生支持 | 无 |
| 动态任务 | 支持 | 支持 | 支持 |
| 本地开发 | 复杂 | 简单 | 简单 |
| 社区生态 | 最大 | 成长中 | 成长中 |

### Airflow 核心模式

- DAG 定义：`with DAG(dag_id, schedule, default_args) as dag`
- TaskFlow API：`@task` 装饰器，自动 XCom 传递
- 动态任务：`@task` + `.expand()` 实现 dynamic task mapping
- Operators：PythonOperator / BashOperator / SQL / HTTP / S3
- Sensors：FileSensor / HttpSensor / ExternalTaskSensor
- 重试策略：`retries=3, retry_delay=timedelta(minutes=5), retry_exponential_backoff=True`
- 失败回调：`on_failure_callback` 发送告警
- SLA 监控：`sla=timedelta(hours=2)` + `sla_miss_callback`

### Dagster 核心模式

- Asset 定义：`@asset(group_name, deps)` 声明数据资产
- MaterializeResult：返回元数据（行数、预览等）
- Resources：`ConfigurableResource` 管理外部连接
- Jobs：`define_asset_job(selection=AssetSelection.groups(...))`
- Schedules：`ScheduleDefinition(job, cron_schedule)`
- Sensors：`@sensor(job)` 监听外部事件触发
- Partitions：`DailyPartitionsDefinition` 按日分区
- Asset Checks：`@asset_check` 验证数据新鲜度/质量

### Prefect 核心模式

- Flow/Task：`@flow` + `@task(retries=3, cache_key_fn=task_input_hash)`
- 并发：`ConcurrentTaskRunner` + `task.map(items)`
- Deployments：`Deployment.build_from_flow(schedule=CronSchedule(...))`
- Blocks：`Secret` / `JSON` 管理配置和密钥

### 调度策略 Checklist

- [ ] Cron 表达式正确（`0 2 * * *` 日批 / `*/15 * * * *` 实时）
- [ ] 事件驱动：文件到达 / S3 / API 触发
- [ ] 跨 DAG 依赖：ExternalTaskSensor / Asset deps
- [ ] 幂等性：UPSERT / 分区覆盖写入
- [ ] 增量处理：`WHERE updated_at > last_run`
- [ ] 数据血缘：Dagster 原生 / Airflow Lineage / dbt ref()

---

## 流式处理

### 框架对比

| 特性 | Kafka Streams | Flink | Spark Streaming |
|------|---------------|-------|-----------------|
| 部署模式 | 嵌入式(JVM) | 独立集群 | 独立集群 |
| 状态管理 | RocksDB | 内存/RocksDB | 内存 |
| Exactly-Once | 支持 | 支持 | 支持 |
| 窗口类型 | 丰富 | 最丰富 | 基础 |
| 学习曲线 | 平缓 | 陡峭 | 中等 |
| Python API | kafka-python | PyFlink | PySpark |

### Kafka Streams 核心模式

- 拓扑构建：`StreamsBuilder` → `stream()` → `filter/map/flatMap` → `to()`
- 聚合：`groupByKey().count()` / `.aggregate()` / `.reduce()`
- Join：Stream-Stream（时间窗口）/ Stream-Table / Table-Table
- 状态存储：`Stores.persistentKeyValueStore` + Transformer
- Exactly-Once：`PROCESSING_GUARANTEE_CONFIG = EXACTLY_ONCE_V2`
- 性能调优：`NUM_STREAM_THREADS=4` / `CACHE_MAX_BYTES_BUFFERING` / RocksDB 配置

### Flink 核心模式

- DataStream API：`env.addSource()` → `filter/map` → `addSink()`
- 窗口类型：
  - 滚动窗口 `TumblingProcessingTimeWindows.of(Time.minutes(5))`
  - 滑动窗口 `SlidingProcessingTimeWindows.of(size, slide)`
  - 会话窗口 `ProcessingTimeSessionWindows.withGap(gap)`
  - 全局窗口 `GlobalWindows.create()` + 自定义 Trigger
- 窗口聚合：`aggregate(AggregateFunction, WindowFunction)` 增量+全窗口
- ProcessFunction：低级 API，访问时间戳、注册定时器
- 状态管理：ValueState / ListState / MapState + TTL 清理
- Checkpoint：`env.enableCheckpointing(60000)` + EXACTLY_ONCE
- Savepoint：`flink run -s /path/to/savepoint`
- 时间语义：Event Time + Watermark（`forBoundedOutOfOrderness`）
- 延迟数据：`allowedLateness()` + `sideOutputLateData()`
- 数据倾斜：添加随机前缀打散 key

### 流处理 Checklist

- [ ] 选择时间语义：Event Time vs Processing Time
- [ ] Watermark 策略：乱序容忍度设置
- [ ] 窗口类型匹配业务场景
- [ ] 状态 TTL 防止无限增长
- [ ] Checkpoint 间隔和超时配置
- [ ] Exactly-Once 语义端到端保证
- [ ] 背压监控和处理
- [ ] 并行度调优

---

## 数据质量

### 质量维度

```
完整性(非空) → 准确性(范围) → 一致性(关联) → 及时性(新鲜度) → 有效性(格式)
```

### 工具对比

| 工具 | 优势 | 适用场景 |
|------|------|----------|
| Great Expectations | 丰富 Expectations、Data Docs | Python 生态、复杂验证 |
| dbt | SQL 原生、血缘追踪 | 数据仓库、转换测试 |
| Soda Core | 简洁 YAML 配置 | 快速验证、CI/CD |

### Great Expectations 核心模式

- Data Context：`gx.get_context()` → 添加数据源 → 构建批次
- 常用 Expectations：
  - `expect_table_row_count_to_be_between(min, max)`
  - `expect_column_values_to_not_be_null(column)`
  - `expect_column_values_to_be_unique(column)`
  - `expect_column_values_to_be_between(column, min, max)`
  - `expect_column_values_to_be_in_set(column, value_set)`
  - `expect_column_values_to_match_regex(column, regex)`
- Checkpoints：批量运行验证 + 生成 Data Docs
- 自定义 Expectation：继承 `ColumnMapExpectation`

### dbt 测试核心模式

- Schema 测试：`unique` / `not_null` / `accepted_values` / `relationships`
- Generic 测试：`{% test name(model, column_name, params) %}`
- Singular 测试：`tests/` 目录下自定义 SQL，返回行 = 失败
- dbt_expectations 包：`expect_column_mean_to_be_between` / `expect_row_values_to_have_recent_data`
- 执行：`dbt test` / `dbt test --select model` / `dbt test --store-failures`
- 血缘：`{{ ref('model') }}` + `{{ source('schema', 'table') }}` → `dbt docs generate`

### Soda Core 核心模式

```yaml
checks for table_name:
  - row_count > 100
  - missing_count(column) = 0
  - duplicate_count(column) = 0
  - invalid_count(column) = 0:
      valid format: email
  - freshness(timestamp_col) < 1d
```

### 数据质量 Checklist

- [ ] 分层验证：源数据 → 转换后 → 目标数据
- [ ] 完整性：必需列非空、无空字符串
- [ ] 准确性：数值范围、格式正则、逻辑一致
- [ ] 一致性：跨表主键匹配、值一致
- [ ] 及时性：数据新鲜度 < 阈值
- [ ] 唯一性：主键/业务键无重复
- [ ] 质量指标：完整性/唯一性/有效性加权评分
- [ ] 告警：指标低于阈值自动通知（Slack/Email/PagerDuty）
- [ ] 持续监控：定时执行质量检查

---

## 最佳实践

| 实践 | 说明 |
|------|------|
| 幂等性设计 | UPSERT / 分区覆盖，重跑不产生副作用 |
| 增量处理 | 基于时间戳/CDC 增量提取，减少全量扫描 |
| 数据血缘 | dbt ref() / Dagster Asset deps 追踪上下游 |
| 分层验证 | 源→转换→目标每层都验证 |
| 监控告警 | 管道 SLA + 质量指标 + 延迟告警 |
| 状态管理 | 流处理状态 TTL + Checkpoint + Savepoint |
| 容错设计 | 重试策略 + 死信队列 + 回滚方案 |

## 触发词

数据管道、Airflow、Dagster、Prefect、ETL、流处理、Kafka Streams、Flink、数据质量、Great Expectations、dbt、数据验证、数据血缘
