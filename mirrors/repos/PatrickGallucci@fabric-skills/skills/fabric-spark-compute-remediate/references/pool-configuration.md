# Pool Configuration Guide

## Table of Contents

- [Node Sizing](#node-sizing)
- [Autoscale](#autoscale)
- [Custom Pool Creation](#custom-pool-creation)
- [Billing Model](#billing-model)
- [Starter Pool Configuration](#starter-pool-configuration)

---

## Node Sizing

### Available Node Sizes

| Size | VCores | Memory | Use Case |
|------|--------|--------|----------|
| Small | 4 | 32 GB | Light ETL, small datasets, high concurrency |
| Medium | 8 | 64 GB | General purpose, default for Starter Pools |
| Large | 16 | 128 GB | Medium datasets, moderate memory needs |
| X-Large | 32 | 256 GB | Large datasets, memory-intensive operations |
| XX-Large | 64 | 512 GB | Very large datasets, heavy joins/aggregations |

**Note**: X-Large and XX-Large are only available for non-Trial Fabric SKUs.

### Node Size Impact on Max Nodes (F64 Example)

With 384 max Spark VCores (including 3x burst):

| Node Size | VCores/Node | Max Nodes | Total VCores |
|-----------|-------------|-----------|--------------|
| Small | 4 | 96 | 384 |
| Medium | 8 | 48 | 384 |
| Large | 16 | 24 | 384 |
| X-Large | 32 | 12 | 384 |
| XX-Large | 64 | 6 | 384 |

### Choosing the Right Node Size

**Prefer smaller nodes when**:
- High concurrency (many users, many notebooks)
- Workloads are CPU-bound, not memory-bound
- You want faster autoscale responsiveness (more granular scaling)

**Prefer larger nodes when**:
- Memory-intensive operations (large DataFrames, broadcast joins)
- Single-job throughput is priority
- Workloads have high per-executor memory requirements

---

## Autoscale

### How Autoscale Works

When autoscale is enabled:
1. Job starts with the **minimum** node count
2. During execution, Spark evaluates if more nodes are needed
3. Scale-up requests go through job admission control
4. Approved requests add nodes up to the **maximum** limit
5. After job stages complete, excess nodes are retired

### Autoscale remediate

| Issue | Cause | Resolution |
|-------|-------|------------|
| Job not scaling up | Capacity fully utilized; no free cores | Cancel other jobs or wait; check Monitoring Hub |
| Job not scaling up | Autoscale disabled on the pool | Enable autoscale in pool settings |
| Scale-up denied | Total Spark cores across all jobs at capacity limit | Free up cores or upgrade SKU |
| Scaling seems slow | Autoscale evaluates per job stage, not continuously | Expected behavior; jobs scale at stage boundaries |

### Autoscale vs Fixed Allocation

**Use autoscale when**:
- Job workload varies across stages
- You want to share capacity across concurrent jobs
- Cost efficiency matters (pay only for active nodes)

**Disable autoscale when**:
- You need guaranteed maximum core allocation for a specific job
- Predictable performance is critical
- Set max nodes within SKU capacity limits

**Important**: When autoscale is disabled, since the job has no minimum core requirement barrier, it starts once any free cores are available and scales up to the configured total. If capacity is fully used, interactive notebook jobs may slow down or get queued.

### Autoscale Billing (New Model)

Key benefits of the new Autoscale Billing model:
- Spark jobs use **serverless resources** instead of consuming CU from Fabric capacity
- A **max CU limit** can be set for budget governance
- When the CU limit is reached, batch jobs queue and interactive jobs throttle
- **No idle compute cost** — only active job runtime is billed
- Integrates with Azure Quota Management

---

## Custom Pool Creation

### Prerequisites

1. **Workspace Admin** role required
2. Capacity admin must enable **Customized workspace pools** in Capacity Admin Settings > Spark Compute

### Creation Steps

1. Navigate to Workspace Settings > Data Engineering/Science > Spark Settings
2. Select **New Pool**
3. Configure:
   - Pool name
   - Node family (Memory Optimized)
   - Node size (Small through XX-Large)
   - Min nodes (minimum: 1)
   - Max nodes (within SKU limits)
   - Autoscale on/off
4. Save the pool configuration

### Common Creation Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Cannot create pool | Not a workspace admin | Request admin role |
| Node size options limited | Trial SKU (no X-Large/XX-Large) | Upgrade to paid SKU |
| Cannot see custom pools option | Capacity admin hasn't enabled it | Ask capacity admin to enable Customized workspace pools |
| Max nodes too low | VCore limit for SKU reached | Choose smaller node size or upgrade SKU |

### Pool Configuration Changes

- Node sizes can be altered after creation
- Active sessions must be restarted for changes to take effect
- Pool deletion requires no active sessions

---

## Billing Model

### What You Pay For

You are **only billed** for the duration when a Spark session is actively running (notebooks, Spark job definitions, lakehouse operations).

### What Is NOT Billed

- Idle pools (Starter or Custom) with no active sessions
- Cluster creation/provisioning time
- Cluster deallocation time
- Spark context initialization

### Session Timeout

- Default session expiration: **20 minutes** of inactivity
- After session expires, if unused for 2 more minutes, pool deallocates
- To stop billing immediately: explicitly stop the session after notebook execution

### Billing States for Custom Pools

```
Creating → Starting → Running → Stopping → Stopped
(Not Billed)  (Not Billed)  (Billed)   (Billed)   (Not Billed)
                                    ↓
                              Deallocating → Deallocated
                              (Not Billed)    (Not Billed)
```

---

## Starter Pool Configuration

### Default Settings

| Property | Value |
|----------|-------|
| Node family | Memory Optimized |
| Node size | Medium (8 VCores, 64 GB) |
| Min/Max nodes | 1-10 |
| Autoscale | On |
| Dynamic allocation | On |

### Starter Pool Limitations

- Only supports **Medium** node sizes for fast startup
- Selecting any other node size results in on-demand session start (2-5 minutes)
- Node count is configurable by workspace admins
- Max nodes limited by SKU capacity

### Configuring Starter Pool Max Nodes

Workspace admins can adjust Starter Pool settings through:

1. Workspace Settings > Data Engineering/Science > Pool tab
2. Select the StarterPool
3. Edit Pool Details (pencil icon)
4. Adjust Number of Nodes

Example: On F64, setting Starter Pool max nodes to 48 (Medium nodes, 8 VCores each) allows a single job to use all 384 burst VCores.
