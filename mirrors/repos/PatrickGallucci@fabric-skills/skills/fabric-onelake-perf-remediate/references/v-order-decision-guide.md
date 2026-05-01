# V-Order Decision Guide

## Table of Contents

- [What is V-Order](#what-is-v-order)
- [Resource Profiles](#resource-profiles)
- [Decision Matrix](#decision-matrix)
- [Configuration Methods](#configuration-methods)
- [Common Patterns](#common-patterns)

## What is V-Order

V-Order is a write-time optimization to the Parquet file format that enables fast reads across all Microsoft Fabric engines. It applies optimized sorting, row group distribution, encoding, and compression.

Key characteristics:

- 100% open-source Parquet format compliant — any Parquet engine can read V-Ordered files
- Power BI and SQL engines leverage Verti-Scan technology for in-memory-like access times
- Spark and non-Verti-Scan engines see approximately 10% faster reads (up to 50% in some cases)
- Write time overhead is approximately 15%
- Compression improvement is up to 50%
- Compatible with Z-ORDER — they can be applied together (bin-compact → Z-ORDER → V-ORDER)

## Resource Profiles

Fabric supports predefined Spark resource profiles that bundle optimized settings for different workload patterns.

| Profile | V-Order Default | Best For |
|---------|----------------|----------|
| `writeHeavy` | **Disabled** | Large-scale ETL, streaming ingestion, batch data engineering |
| `readHeavyForSpark` | Enabled | Interactive Spark queries, analytics workloads |
| `readHeavyForPBI` | Enabled | Power BI dashboards, Direct Lake semantic models |

**Important:** All new Fabric workspaces default to `writeHeavy` profile where `spark.sql.parquet.vorder.default=false`.

## Decision Matrix

Use this matrix to determine V-Order configuration:

| Workload Pattern | V-Order | Profile | Rationale |
|-----------------|---------|---------|-----------|
| ETL ingestion → Power BI reporting | Enable on reporting tables | Mixed | Disable during ingestion, enable via OPTIMIZE VORDER after load |
| Streaming ingestion (high volume) | Disable during ingest | writeHeavy | V-Order overhead slows ingestion; apply post-hoc |
| Interactive Spark analytics | Enable | readHeavyForSpark | Read speed more important than write overhead |
| Power BI Direct Lake | Enable | readHeavyForPBI | Critical for avoiding DirectQuery fallback |
| Staging / temporary tables | Disable | writeHeavy | Tables are transient; V-Order overhead provides no benefit |
| Data warehouse (Fabric Warehouse) | Enabled by default | N/A | V-Order is on by default for warehouses |

**Staging + serving pattern:** Use a staging lakehouse with V-Order disabled for high-throughput ingestion and transformation. Apply V-Order when writing final output to a serving lakehouse or warehouse.

## Configuration Methods

### Session level

```python
# Enable V-Order for all writes in the session
spark.conf.set("spark.sql.parquet.vorder.default", "true")

# Disable V-Order for the session
spark.conf.set("spark.sql.parquet.vorder.default", "false")
```

### Table level (persistent)

```sql
%%sql
-- Enable V-Order on a specific table
ALTER TABLE my_schema.my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true");

-- Disable V-Order on a specific table
ALTER TABLE my_schema.my_table SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "false");

-- Remove V-Order setting (inherits session/workspace default)
ALTER TABLE my_schema.my_table UNSET TBLPROPERTIES("delta.parquet.vorder.enabled");
```

### OPTIMIZE command level (one-time apply)

```sql
%%sql
-- Apply V-Order to existing files without changing table properties
OPTIMIZE my_schema.my_table VORDER;

-- Combined with Z-ORDER
OPTIMIZE my_schema.my_table ZORDER BY (customer_id) VORDER;

-- With predicate filter
OPTIMIZE my_schema.my_table WHERE region = 'US' VORDER;
```

### Environment level (workspace default)

Configure in Workspace Settings → Data Engineering/Science → Spark Settings → choose the resource profile that matches your workload.

## Common Patterns

### Pattern 1: ETL Pipeline with Post-Load Optimization

```python
# Step 1: Disable V-Order for fast ingestion
spark.conf.set("spark.sql.parquet.vorder.default", "false")

# Step 2: Write data
df.write.format("delta").mode("overwrite").saveAsTable("staging.raw_events")

# Step 3: Apply V-Order after load completes
spark.sql("OPTIMIZE staging.raw_events VORDER")
```

### Pattern 2: Mixed Workload with Table-Level Control

```sql
%%sql
-- Staging tables: V-Order off (write-optimized)
ALTER TABLE staging.raw_orders SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "false");

-- Serving tables: V-Order on (read-optimized)
ALTER TABLE analytics.fact_orders SET TBLPROPERTIES("delta.parquet.vorder.enabled" = "true");
```

### Pattern 3: Verify V-Order Status

```sql
%%sql
-- Check V-Order property for a table
SHOW TBLPROPERTIES my_schema.my_table;
```

Look for `delta.parquet.vorder.enabled` in the output. If absent, the table inherits the session/workspace default.
