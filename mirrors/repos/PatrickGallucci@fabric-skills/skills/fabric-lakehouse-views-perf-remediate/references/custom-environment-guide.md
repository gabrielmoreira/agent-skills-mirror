# Custom Spark Environment Guide for MLV Workloads

## Table of Contents

- [Overview](#overview)
- [When to Use a Custom Environment](#when-to-use-a-custom-environment)
- [Attaching an Environment to MLV Lineage](#attaching-an-environment-to-mlv-lineage)
- [Recommended Configurations by Workload Size](#recommended-configurations-by-workload-size)
- [Spark Properties for MLV Optimization](#spark-properties-for-mlv-optimization)
- [Important Constraints](#important-constraints)

---

## Overview

By default, MLV lineage refreshes use the workspace's default Spark environment. For workloads that require more compute, memory, or specific library versions, you can attach a custom Spark environment to the lineage. Only environments that the user has access to can be selected.

## When to Use a Custom Environment

- Source tables exceed 50 million rows
- MLV definitions include multi-table joins (3+ tables)
- Refresh runs are timing out or running OOM
- You need specific Spark configuration properties not set at workspace level
- Different lineages in the same workspace have different resource requirements

## Attaching an Environment to MLV Lineage

1. Navigate to the lakehouse and select **Manage materialized lake views**
2. In the lineage view, locate the environment dropdown (typically in the ribbon or settings panel)
3. Select the desired custom environment from the dropdown
4. Changes take effect from the **next** refresh (not the current in-progress run)

**Access Requirements:**

- You must have access to the environment to select it
- If you lack access, the environment name and workspace details may not be visible
- Schedule and Run buttons are disabled if the user cannot access the selected environment

## Recommended Configurations by Workload Size

| Workload | Source Rows | Recommended Node Size | Executor Count | Notes |
|----------|-------------|----------------------|-----------------|-------|
| Small | < 10M | Small (4 vCores, 28 GB) | 2-4 | Default environment usually sufficient |
| Medium | 10M - 100M | Medium (8 vCores, 56 GB) | 4-8 | Add partitioning to MLV definition |
| Large | 100M - 1B | Large (16 vCores, 112 GB) | 8-16 | Chain MLVs, use partitioning |
| Extra Large | > 1B | XL (32+ vCores, 224+ GB) | 16-32 | Dedicated environment, aggressive partitioning |

## Spark Properties for MLV Optimization

These properties can be configured in the custom environment. Note that **session-level Spark properties are NOT applied during scheduled lineage refresh** -- you must set them in the environment.

### Memory and Shuffle

```
spark.executor.memory         = 28g    (increase for large joins)
spark.executor.memoryOverhead = 4g     (increase for complex aggregations)
spark.sql.shuffle.partitions  = 200    (increase for wide joins, decrease for small datasets)
spark.sql.adaptive.enabled    = true   (let Spark optimize at runtime)
```

### Delta Lake Optimization

```
spark.databricks.delta.optimizeWrite.enabled  = true
spark.databricks.delta.autoCompact.enabled    = true
spark.databricks.delta.properties.defaults.enableChangeDataFeed = true
```

### Parallelism

```
spark.default.parallelism        = 200
spark.sql.files.maxPartitionBytes = 134217728  (128 MB per partition)
```

## Important Constraints

| Constraint | Detail |
|-----------|--------|
| Session properties ignored | Spark properties set via `SET` in notebooks do not apply to scheduled MLV refreshes |
| Environment change timing | Changes take effect only from the next refresh |
| Deleted environment | If the associated environment is deleted, an error prompts you to choose a new one |
| Access required | Users without access to the environment cannot see its details or trigger runs |
| One environment per lineage | Each lineage can have one associated environment at a time |
