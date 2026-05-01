# Resource Profiles Reference

## Table of Contents

- [Overview](#overview)
- [Available Profiles](#available-profiles)
- [Configuration Values](#configuration-values)
- [How to Configure](#how-to-configure)
- [Selection Guide](#selection-guide)

## Overview

Microsoft Fabric supports predefined Spark resource profiles that apply workload-optimized Spark configurations. These profiles eliminate trial-and-error tuning by bundling proven settings for common patterns.

All newly created Fabric workspaces default to `writeHeavy`. V-Order is disabled by default in new workspaces to prioritize write performance.

## Available Profiles

| Profile | Use Case | Property |
|---------|----------|----------|
| `readHeavyForSpark` | Spark workloads with frequent reads | `spark.fabric.resourceProfile = readHeavyForSpark` |
| `readHeavyForPBI` | Power BI queries on Delta tables | `spark.fabric.resourceProfile = readHeavyForPBI` |
| `writeHeavy` | High-frequency ingestion and writes | `spark.fabric.resourceProfile = writeHeavy` |
| `custom` | Fully user-defined configuration | `spark.fabric.resourceProfile = custom` |

## Configuration Values

### writeHeavy (Default for New Workspaces)

```json
{
  "spark.sql.parquet.vorder.default": "false",
  "spark.databricks.delta.optimizeWrite.enabled": "null",
  "spark.databricks.delta.optimizeWrite.binSize": "128",
  "spark.databricks.delta.optimizeWrite.partitioned.enabled": "true"
}
```

Best for: ETL pipelines, batch ingestion, streaming workloads, large-scale data transformations.

### readHeavyForPBI

```json
{
  "spark.sql.parquet.vorder.default": "true",
  "spark.databricks.delta.optimizeWrite.enabled": "true",
  "spark.databricks.delta.optimizeWrite.binSize": "1g"
}
```

Best for: Power BI Direct Lake models, dashboard serving, interactive BI queries.

### readHeavyForSpark

```json
{
  "spark.databricks.delta.optimizeWrite.enabled": "true",
  "spark.databricks.delta.optimizeWrite.partitioned.enabled": "true",
  "spark.databricks.delta.optimizeWrite.binSize": "128"
}
```

Best for: Interactive Spark analytics, exploratory data analysis, ad-hoc queries.

### custom

Fully user-defined. Example:

```json
{
  "spark.sql.shuffle.partitions": "800",
  "spark.sql.adaptive.enabled": "true",
  "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
}
```

Name your custom profile meaningfully, e.g., `fastIngestProfile` or `lowLatencyAnalytics`.

## How to Configure

### Method 1: Environment Level (Persistent)

1. Navigate to Fabric workspace
2. Edit or create an environment
3. Under Spark Configurations, set: `spark.fabric.resourceProfile = readHeavyForSpark`
4. Publish the environment
5. All notebooks/jobs using this environment inherit the profile

### Method 2: Runtime Override (Per Notebook/Job)

```python
# Override at runtime — takes precedence over environment
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
```

Runtime settings take precedence over environment settings.

### Method 3: Customize Existing Profiles

Choose an existing profile and modify specific values:

```python
# Start with readHeavyForSpark but increase bin size
spark.conf.set("spark.fabric.resourceProfile", "readHeavyForSpark")
spark.conf.set("spark.databricks.delta.optimizeWrite.binSize", "256")
```

## Selection Guide

```
What is the primary workload?
│
├── Data Ingestion / ETL
│   └── writeHeavy (default)
│       - V-Order OFF for faster writes
│       - Run OPTIMIZE VORDER post-ingestion for read consumers
│
├── Power BI Dashboards / Direct Lake
│   └── readHeavyForPBI
│       - V-Order ON (enables Verti-Scan acceleration)
│       - Large bin size (1 GB) for fewer, larger files
│       - Run OPTIMIZE VORDER regularly
│
├── Spark Analytics / Data Science
│   └── readHeavyForSpark
│       - Optimize Write enabled
│       - Partitioned optimize write enabled
│       - Enable autotune for query-level tuning
│
└── Mixed (ETL + Analytics in same workspace)
    ├── Option A: Separate environments per workload type
    └── Option B: Use spark.conf.set() per notebook to switch profiles
```

## V-Order Interaction

V-Order is controlled independently from resource profiles but is set by profile defaults:

| Profile | V-Order Default |
|---------|----------------|
| writeHeavy | `false` (disabled) |
| readHeavyForPBI | `true` (enabled) |
| readHeavyForSpark | Not explicitly set (inherits workspace default) |

To override V-Order regardless of profile:

```python
spark.conf.set('spark.sql.parquet.vorder.default', 'true')   # Enable
spark.conf.set('spark.sql.parquet.vorder.default', 'false')  # Disable
```

In Runtime 1.3+, V-Order is applied automatically during OPTIMIZE statements, so manual session-level enabling is less critical for maintenance operations.
