# Fabric Capacity Optimization for Power BI

## Table of Contents

- [Understanding Fabric Capacity](#understanding-fabric-capacity)
- [Capacity SKU Mapping](#capacity-sku-mapping)
- [Monitoring with Capacity Metrics App](#monitoring-with-capacity-metrics-app)
- [Interactive vs Background Operations](#interactive-vs-background-operations)
- [Power BI Optimization Strategies](#power-bi-optimization-strategies)
- [Spark Resource Profiles for Power BI](#spark-resource-profiles-for-power-bi)
- [Autoscale and Cost Management](#autoscale-and-cost-management)
- [Capacity Sizing Guidelines](#capacity-sizing-guidelines)

---

## Understanding Fabric Capacity

Microsoft Fabric uses a unified capacity model where all workloads (Power BI, Data Engineering, Data Warehouse, Real-Time Intelligence) share compute resources measured in Capacity Units (CUs).

Power BI operations consume CUs through:
- **Interactive operations**: DAX queries from report visuals, Q&A, Explore
- **Background operations**: Semantic model refresh, dataflow refresh, paginated report rendering

Key concepts:
- Interactive operations have priority and are never smoothed
- Background operations are smoothed over 24 hours
- Throttling occurs when interactive utilization exceeds capacity limits
- Overuse leads to request rejection (HTTP 429) for background and delayed response for interactive

---

## Capacity SKU Mapping

| Fabric SKU | Equivalent Power BI SKU | Max Concurrent Spark Jobs |
|------------|------------------------|--------------------------|
| F2 | - | 4 |
| F4 | - | 4 |
| F8 | - | 8 |
| F16 | - | 16 |
| F32 | - | 32 |
| F64 | P1 | 64 |
| F128 | P2 | 128 |
| F256 | P3 | 256 |
| F512 | P4 | 512 |

**XMLA endpoint** (required for DAX Studio, Tabular Editor): Available on F64 / P1 and above.

**Query scale-out**: Available on F64 / P1 and above. Creates read-only replicas to handle concurrent DAX queries.

---

## Monitoring with Capacity Metrics App

### Installation

1. Navigate to Microsoft AppSource
2. Search for "Microsoft Fabric Capacity Metrics"
3. Install and configure with your capacity ID

### Key Reports to Review

**Compute page:**
- CU utilization percentage over time
- Breakdown by workload type (Power BI, Spark, SQL, etc.)
- Throttling events and severity

**Items page:**
- Top items by CU consumption
- Per-item breakdown of interactive vs background
- Duration trends per item

**Overages page:**
- Cumulative overuse over the 24-hour smoothing window
- Projected throttling based on current trajectory

### Alerting

Configure alerts when:
- Interactive utilization > 80% sustained for 30+ minutes
- Any throttling event occurs
- Background queue depth > 10

---

## Interactive vs Background Operations

### Power BI Interactive Operations

These consume CUs immediately and cannot be smoothed:
- Report visual rendering (DAX queries)
- Dashboard tile refresh
- Q&A natural language queries
- Explore data queries
- Export to Excel (live connection)
- Paginated report on-demand rendering

### Power BI Background Operations

These are smoothed over 24 hours:
- Scheduled semantic model refresh
- Dataflow Gen2 refresh
- Paginated report scheduled rendering
- Dataset eviction and reload

### Optimization Priority

Focus optimization efforts in this order:
1. **High-frequency interactive queries** (most visible user impact)
2. **Large scheduled refreshes** (biggest CU consumers)
3. **Concurrent report access** (multiplicative effect)
4. **Background pipeline jobs** (affect available headroom)

---

## Power BI Optimization Strategies

### Reduce Interactive CU Consumption

| Strategy | Impact | Effort |
|----------|--------|--------|
| Optimize DAX measures | High | Medium |
| Reduce visuals per page | High | Low |
| Enable query caching | Medium | Low |
| Use aggregations (Composite model) | High | High |
| Enable query scale-out | Medium | Low |
| Implement RLS efficiently | Medium | Medium |

### Reduce Background CU Consumption

| Strategy | Impact | Effort |
|----------|--------|--------|
| Enable incremental refresh | High | Medium |
| Stagger refresh schedules | Medium | Low |
| Remove unused tables/columns | Medium | Low |
| Optimize Power Query (enable folding) | High | Medium |
| Use Lakehouse/Warehouse instead of dataflows for heavy transforms | High | High |

### Query Caching

Enable automatic page refresh caching:
- Settings > Datasets > Query caching: On
- Reduces duplicate DAX query execution for repeated report views
- Cache duration aligns with refresh schedule

### Query Scale-Out

For high-concurrency scenarios (F64+):
- Settings > Datasets > Scale-out: On
- Creates read-only replica(s) of the semantic model
- Interactive queries are distributed across replicas
- Does not reduce per-query CU cost, but reduces contention

---

## Spark Resource Profiles for Power BI

When lakehouse data serves Power BI reports, the Spark write configuration affects read performance.

### Available Profiles

| Profile | VOrder | Optimized For |
|---------|--------|---------------|
| writeHeavy (default) | Disabled | Data ingestion and ETL |
| readHeavyForSpark | Enabled | Interactive Spark queries |
| readHeavyForPBI | Enabled | Power BI dashboard serving |

### Enabling readHeavyForPBI

At the **environment level** in Fabric:
1. Navigate to your Fabric environment
2. Select Spark settings
3. Set resource profile to `readHeavyForPBI`

Or set individual Spark properties:
```
spark.sql.parquet.vorder.default=true
```

### What VOrder Does

VOrder applies a special sort order to Parquet/Delta files that aligns with Power BI's VertiPaq engine scan patterns. This dramatically improves:
- DirectQuery read performance from Lakehouse SQL endpoint
- Import refresh performance (faster data ingestion into VertiPaq)
- SQL analytics endpoint query performance

**Trade-off**: Write operations are slower because VOrder adds sorting overhead during file creation.

---

## Autoscale and Cost Management

### When to Consider Autoscale Billing for Spark

If your Fabric capacity hosts both Power BI and heavy Spark workloads, Spark jobs can consume capacity that Power BI needs. Autoscale Billing for Spark offloads Spark compute to a separate, pay-as-you-go billing model.

| Feature | Capacity Model | Autoscale Billing |
|---------|---------------|-------------------|
| Billing | Fixed per SKU | Pay-per-use |
| Scaling | Shared with all workloads | Independent |
| Contention | Possible | Eliminated for Spark |
| Best for | Stable PBI-heavy workloads | Bursty Spark workloads |

### Cost Monitoring

1. Azure Portal > Subscription > Cost Analysis
2. Filter by Fabric capacity resource
3. Track meter: `Autoscale for Spark Capacity Usage CU`

---

## Capacity Sizing Guidelines

### Starting Point Estimation

| Workload Profile | Recommended Starting SKU |
|-----------------|------------------------|
| < 50 users, few reports | F8 |
| 50-200 users, moderate reports | F16-F32 |
| 200-500 users, complex dashboards | F64 |
| 500-2000 users, enterprise deployment | F128-F256 |
| 2000+ users, mission-critical | F256+ with Autoscale |

### Iterative Sizing Approach

1. Start with a trial or small F SKU
2. Deploy representative workloads
3. Monitor with Capacity Metrics app for 1-2 weeks
4. Identify peak utilization and throttling patterns
5. Right-size based on measured data
6. Re-evaluate quarterly as usage grows

### Capacity Pause/Resume for Cost Savings

For non-production capacities:
1. Azure Portal > Fabric Capacity > Pause
2. Wait 5 minutes for cleanup
3. Resume when needed
4. Resize to a lower SKU for off-hours if needed

**Note**: Only Azure administrators can resize SKUs. Changes are made in the Azure portal, not within Fabric settings.
