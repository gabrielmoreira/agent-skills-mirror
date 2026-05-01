# Capacity SKU Reference

## Table of Contents

- [Spark VCore Allocation](#spark-vcore-allocation)
- [Queue Limits by SKU](#queue-limits-by-sku)
- [Starter Pool Node Limits](#starter-pool-node-limits)
- [Sizing Recommendations](#sizing-recommendations)

## Spark VCore Allocation

Every Fabric capacity unit (CU) provides **2 Spark VCores**. These VCores are shared across all Spark-based items in workspaces assigned to that capacity, including notebooks, Spark job definitions, and lakehouse operations.

Formula: `Total Spark VCores = Capacity Units × 2`

## Queue Limits by SKU

When all Spark VCores are in use, additional jobs enter a FIFO queue. Once the queue limit is reached, new jobs receive HTTP 430 (TooManyRequestsForCapacity).

| Fabric SKU | Equivalent PBI SKU | Spark VCores | Queue Limit |
|------------|-------------------|--------------|-------------|
| F2         | —                 | 4            | 4           |
| F4         | —                 | 8            | 4           |
| F8         | —                 | 16           | 8           |
| F16        | —                 | 32           | 16          |
| F32        | —                 | 64           | 32          |
| F64        | P1                | 128          | 64          |
| F128       | P2                | 256          | 128         |
| F256       | P3                | 512          | 256         |
| F512       | P4                | 1024         | 512         |
| F1024      | —                 | 2048         | 1024        |
| F2048      | —                 | 4096         | 2048        |
| Trial      | P1                | 128          | N/A (no queuing) |

**Key notes:**

- Queueing is NOT supported for Fabric trial capacities — jobs are throttled immediately
- Queued jobs from pipelines, job scheduler, and Spark job definitions are automatically retried
- Interactive notebook submissions are NOT queued and fail immediately when capacity is full

## Starter Pool Node Limits

Each SKU has specific default and maximum node configurations for starter pools. Higher SKUs support more nodes for larger workloads.

To configure starter pools:

1. Navigate to Workspace Settings
2. Select Data Engineering/Science → Spark Settings
3. Choose the StarterPool option
4. Set maximum node configuration within SKU-allowed limits

## Sizing Recommendations

**Small team / development:** F4–F8 for exploration and development workloads with limited concurrency.

**Medium workloads:** F32–F64 for production ETL pipelines with moderate concurrency. Provides a reasonable queue buffer.

**Large-scale production:** F128+ for high-concurrency environments with multiple teams and streaming ingestion.

**Burst pattern:** If workloads are spiky, consider the queue limit as your burst buffer. If jobs regularly hit the queue limit, scale up the SKU.

**Cost optimization:** Use the Monitoring Hub to track actual VCore utilization over time. If sustained utilization is below 50%, consider downsizing. If queue depth regularly exceeds 75% of the limit, consider upsizing.
