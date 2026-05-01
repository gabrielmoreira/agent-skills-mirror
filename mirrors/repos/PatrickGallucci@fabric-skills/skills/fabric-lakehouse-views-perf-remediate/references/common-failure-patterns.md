# Common Failure Patterns for Materialized Lake Views

## Table of Contents

- [Delta Table Not Found](#delta-table-not-found)
- [Spark Job OOM (Out of Memory)](#spark-job-oom-out-of-memory)
- [Schema Mismatch After Source Change](#schema-mismatch-after-source-change)
- [Concurrent Refresh Conflicts](#concurrent-refresh-conflicts)
- [Permission and Authentication Errors](#permission-and-authentication-errors)
- [Data Quality Constraint Failures](#data-quality-constraint-failures)
- [Lineage Dependency Failures](#lineage-dependency-failures)
- [Environment Configuration Errors](#environment-configuration-errors)

---

## Delta Table Not Found

### Symptoms

- Error message: "delta table not found" during MLV creation or refresh
- Occurs specifically with FAIL action in data quality constraints

### Root Cause

Known issue where MLV creation/refresh with a FAIL constraint action fails to locate the underlying Delta table. The FAIL action halts processing at the first constraint violation, which can leave the MLV in an inconsistent state.

### Resolution

1. Drop the existing MLV:

```sql
DROP MATERIALIZED LAKE VIEW schema_name.mlv_name;
```

2. Recreate with DROP action instead of FAIL:

```sql
CREATE MATERIALIZED LAKE VIEW schema_name.mlv_name (
    CONSTRAINT valid_amount CHECK (amount > 0) ON MISMATCH DROP
) AS
SELECT * FROM source_table;
```

3. If you need FAIL behavior, implement validation in a separate upstream step before the MLV.

### Prevention

- Prefer `ON MISMATCH DROP` for data quality constraints in MLVs
- Use FAIL constraints only when data integrity is critical AND you have verified the constraint will not trigger on the initial dataset
- Test constraint conditions against source data before applying to MLV

---

## Spark Job OOM (Out of Memory)

### Symptoms

- Spark executor logs show `java.lang.OutOfMemoryError`
- MLV refresh takes excessively long then fails
- Large MLVs with complex joins or aggregations fail during refresh

### Root Cause

Default Spark environment does not have sufficient memory for the workload. Common with large source tables, wide joins across multiple tables, or complex aggregation queries.

### Resolution

1. Attach a custom Spark environment with higher memory allocation:
   - Navigate to Manage materialized lake views
   - Select custom environment from the environment dropdown
   - Choose an environment with higher executor memory

2. Optimize the MLV query:
   - Add `PARTITIONED BY` to distribute data across partitions
   - Reduce the number of columns in SELECT (only include needed columns)
   - Pre-filter data in source tables to reduce volume
   - Break complex multi-table joins into chained MLVs

3. Example optimization:

```sql
-- Instead of one large MLV with 5 joins
-- Break into chained MLVs

-- Step 1: Join customers and orders
CREATE MATERIALIZED LAKE VIEW silver.cust_orders
PARTITIONED BY (region)
AS
SELECT c.customerID, c.region, o.orderDate, o.amount
FROM bronze.customers c
INNER JOIN bronze.orders o ON c.customerID = o.customerID;

-- Step 2: Aggregate on top of step 1
CREATE MATERIALIZED LAKE VIEW gold.regional_sales
AS
SELECT region, DATE(orderDate) as sale_date, SUM(amount) as total
FROM silver.cust_orders
GROUP BY region, DATE(orderDate);
```

### Prevention

- Size custom environments based on expected data volume
- Chain MLVs for complex transformations instead of single monolithic views
- Use `PARTITIONED BY` for tables exceeding 10 million rows

---

## Schema Mismatch After Source Change

### Symptoms

- MLV refresh fails after source table schema change (added/removed/renamed columns)
- Error references column not found or type mismatch

### Root Cause

MLV definitions are fixed at creation time. If the source table schema changes (columns added, removed, renamed, or types changed), the MLV definition becomes incompatible.

### Resolution

1. Review the MLV definition:

```sql
SHOW CREATE MATERIALIZED LAKE VIEW schema_name.mlv_name;
```

2. Drop and recreate the MLV with the updated schema:

```sql
DROP MATERIALIZED LAKE VIEW schema_name.mlv_name;

CREATE OR REPLACE MATERIALIZED LAKE VIEW schema_name.mlv_name AS
SELECT ... -- updated column references
FROM source_table;
```

3. Update all downstream dependent MLVs that reference the changed MLV.

### Prevention

- Use explicit column lists in MLV SELECT statements (avoid `SELECT *`)
- Document source table schema contracts
- Test schema changes in a development workspace before applying to production

---

## Concurrent Refresh Conflicts

### Symptoms

- Run state shows "Skipped" for scheduled runs
- Multiple runs queued but only one executes
- Schedule appears to miss refresh windows

### Root Cause

MLV supports only one active refresh per lineage at a time. If a previous run is still in progress when the next scheduled run triggers, the new run is skipped.

### Resolution

1. Check current run status in the lineage view dropdown
2. If a run is stuck, cancel it from Monitor Hub:
   - Navigate to Monitor Hub
   - Filter by Job Type: MaterializedLakeViews
   - Hover over the in-progress run and click Cancel
3. Adjust schedule frequency to allow sufficient time for each run to complete
4. Consider optimizing refresh duration (see Spark Job OOM section)

### Prevention

- Set schedule intervals longer than the typical refresh duration
- Monitor average refresh times and adjust schedules accordingly
- MLV supports only one schedule per lineage; do not attempt to create multiple

---

## Permission and Authentication Errors

### Symptoms

- "Run" or "Schedule" buttons are disabled in lineage view
- API calls return 401 or 403 errors
- Environment details not visible in run history

### Root Cause

- User lacks access to the selected custom environment
- Service principal authentication is not supported for MLV
- Workspace role insufficient for scheduling operations

### Resolution

1. Verify workspace role is Admin or Contributor
2. Ensure the selected custom environment is accessible to the user
3. Use Microsoft Entra user authentication (not service principals) for MLV API calls
4. If environment was deleted, select a new one from the dropdown

---

## Data Quality Constraint Failures

### Symptoms

- MLV refresh fails at constraint validation step
- High number of dropped records reported in lineage view
- Pipeline halts when using FAIL action

### Root Cause

Source data contains values that violate the defined constraints. With FAIL action, the first violation stops the entire refresh. With DROP action, violations are silently removed.

### Resolution

1. Review constraint definitions:

```sql
SHOW CREATE MATERIALIZED LAKE VIEW schema_name.mlv_name;
```

2. Query source data to identify violations:

```sql
-- Example: Find rows that would fail the constraint
SELECT * FROM source_table
WHERE NOT (amount > 0);
```

3. Fix source data quality upstream, OR switch constraint action:
   - Change FAIL to DROP if partial data is acceptable
   - Recreate MLV (constraint updates are not supported in-place)

### Prevention

- Use DROP action for non-critical constraints to avoid pipeline failures
- Implement data quality checks in the bronze-to-silver ETL before MLV processing
- Monitor dropped record counts in the lineage view

---

## Lineage Dependency Failures

### Symptoms

- Child MLV nodes show "Skipped" state
- Only the first MLV in the chain succeeds
- Cascading failures across the lineage graph

### Root Cause

When a parent node in the lineage fails, all dependent (child) nodes are automatically skipped. The dependency chain enforces execution order.

### Resolution

1. Always fix the root (first) failure in the chain
2. Click the failed node in lineage to see the specific error
3. After fixing the root cause, re-run the lineage (all nodes will re-execute)
4. Use the activity panel at the bottom of the lineage view for a high-level overview

### Prevention

- Design lineage chains with independent branches where possible
- Test each MLV independently before building dependencies
- Monitor root nodes more closely as they impact the entire chain

---

## Environment Configuration Errors

### Symptoms

- Error message prompting user to choose an accessible environment
- Environment dropdown shows warning icon
- Lineage refresh fails with environment-related errors

### Root Cause

- The associated custom environment was deleted
- User does not have access to the selected environment
- Environment changes only take effect from the next refresh

### Resolution

1. Open Manage materialized lake views
2. Select a new accessible environment from the dropdown
3. Trigger a new refresh to apply the environment change
4. If using workspace default environment, verify it has sufficient resources

### Prevention

- Document which environments are associated with which lineages
- Avoid deleting environments that are in active use
- Use dedicated environments for MLV workloads to avoid conflicts
