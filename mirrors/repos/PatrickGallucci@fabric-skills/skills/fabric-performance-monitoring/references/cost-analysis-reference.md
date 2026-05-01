# Cost Analysis Reference: Autoscale vs Capacity Billing

## Table of Contents

- [Billing Models Comparison](#billing-models-comparison)
- [When to Use Each Model](#when-to-use-each-model)
- [Monitoring Autoscale Billing](#monitoring-autoscale-billing)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Capacity Rightsizing Guide](#capacity-rightsizing-guide)

---

## Billing Models Comparison

| Feature | Capacity Model | Autoscale Billing for Spark |
|---------|---------------|---------------------------|
| Billing | Fixed cost per capacity tier | Pay-as-you-go for Spark jobs |
| Scaling | Capacity shared across workloads | Spark scales independently |
| Resource Contention | Possible between workloads | Dedicated compute limits for Spark |
| Cost Predictability | High (fixed monthly cost) | Variable (usage-based) |
| Best Use Case | Predictable, steady workloads | Dynamic or bursty Spark jobs |
| Idle Cost | Full SKU cost even when idle | No idle compute costs |
| CU Rate | Included in SKU | 0.5 CU Hour per Spark job |

### Hybrid Strategy

Organizations can use both models simultaneously. Run stable, recurring jobs on the capacity model while offloading ad-hoc or compute-heavy Spark workloads to Autoscale Billing. This balances cost predictability with burst performance.

---

## When to Use Each Model

### Choose Capacity Model When

- Workloads are predictable and steady throughout the day
- Multiple workload types (Spark, Data Warehouse, Power BI) share the same capacity
- Budget predictability is a priority
- The capacity is consistently utilized at 60%+ of CU allocation

### Choose Autoscale Billing When

- Spark workloads are bursty or unpredictable
- Jobs run primarily during specific windows (nightly ETL, weekly reports)
- You want to isolate Spark cost from other Fabric workloads
- You need to avoid resource contention between Spark and other services
- Dev/test Spark workloads don't justify a dedicated capacity tier

### Decision Framework

```
Is your Spark usage > 60% of capacity consistently?
  YES --> Capacity Model (better cost/CU ratio)
  NO  --> Is your usage bursty or unpredictable?
           YES --> Autoscale Billing
           NO  --> Consider downsizing capacity SKU
```

---

## Monitoring Autoscale Billing

### Azure Cost Analysis Steps

1. Navigate to the Azure portal
2. Select the Subscription linked to your Fabric capacity
3. Go to **Cost Analysis**
4. Filter by the resource (Fabric capacity)
5. Use the meter: **Autoscale for Spark Capacity Usage CU**
6. View real-time compute spend for Spark workloads using Autoscale Billing

### Key Meters

| Meter Name | Description |
|-----------|-------------|
| Autoscale for Spark Capacity Usage CU | Compute consumed by Spark jobs under autoscale |
| Fabric Capacity CU | Standard capacity consumption |
| OneLake Storage | Storage consumed across all workspaces |

### Setting CU Limits

When enabling Autoscale Billing, set a maximum CU limit to control budget:

```
Autoscale CU Limit = Expected peak Spark VCores / 2
```

This prevents runaway costs from unexpected job surges.

---

## Cost Optimization Strategies

### Strategy 1: Pause/Resume Scheduling

For dev/test capacities, schedule pause during non-business hours:

```powershell
# Pause capacity at 7 PM
Suspend-AzFabricCapacity -ResourceGroupName "rg" -CapacityName "dev-cap"

# Resume capacity at 7 AM
Resume-AzFabricCapacity -ResourceGroupName "rg" -CapacityName "dev-cap"
```

Savings: Up to 60% for capacities used only during business hours.

### Strategy 2: Right-Size After Autoscale Migration

1. Enable Autoscale Billing for Spark
2. Pause the capacity for 5 minutes to clear active Spark usage
3. Resume the capacity
4. Resize the capacity to a smaller SKU sized for remaining workloads (Power BI, Data Warehouse)

This separates Spark billing from capacity billing, potentially allowing a significant SKU downgrade.

### Strategy 3: Job Scheduling Optimization

Spread batch jobs across off-peak hours to reduce peak concurrency:

- Schedule ETL jobs in rotating 30-minute windows
- Use pipeline orchestration to serialize dependent jobs
- Avoid scheduling all refreshes at the same time (midnight syndrome)

### Strategy 4: Spark Resource Profile Tuning

Choose the right resource profile to avoid over-provisioning:

| Profile | Best For | VOrder Default |
|---------|----------|---------------|
| writeHeavy | Large ETL, streaming ingestion | Disabled |
| readHeavy | Analytics queries, reporting notebooks | Enabled |
| balanced | Mixed read/write workloads | Enabled |

If your workload is primarily reads (analytics), switching from `writeHeavy` to `readHeavy` can improve query performance without additional CU cost.

### Strategy 5: Starter Pools vs Custom Pools

- **Starter pools**: Fast session init (5-10 seconds), pre-configured, ideal for interactive work
- **Custom pools**: Configurable node sizes, autoscaling, better for production batch jobs

Use starter pools for development and ad-hoc analysis. Reserve custom pools for production pipelines where you need specific memory or node configurations.

---

## Capacity Rightsizing Guide

### Step 1: Measure Current Utilization

Use the Capacity Metrics App to identify:
- Average CU utilization over 7 days
- Peak CU utilization periods
- Top CU-consuming items and operations
- Background vs interactive operation split

### Step 2: Calculate Required SKU

```
Required CU = Average CU * 1.3 (30% headroom)
Required SKU = Next SKU >= Required CU
```

### Step 3: Validate with Trial

Before committing to a reserved instance:
1. Provision a pay-as-you-go F SKU at the target size
2. Run representative workloads for 1-2 weeks
3. Monitor utilization and throttling in the Capacity Metrics App
4. Adjust SKU if throttling occurs or if utilization is consistently below 40%

### SKU Cost Tiers (Reference)

| SKU | CUs | Relative Cost | Typical Use Case |
|-----|-----|--------------|------------------|
| F2-F8 | 2-8 | Low | Dev/test, small workloads |
| F16-F32 | 16-32 | Medium | Department-level analytics |
| F64-F128 | 64-128 | High | Enterprise workloads |
| F256-F1024 | 256-1024 | Very High | Large-scale data platforms |
| F2048 | 2048 | Maximum | Extreme-scale scenarios |

Note: Exact pricing varies by region and commitment term. Check Azure pricing calculator for current rates.
