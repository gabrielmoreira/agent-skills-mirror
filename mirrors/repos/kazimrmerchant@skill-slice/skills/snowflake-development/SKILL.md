---
name: snowflake-development
description: "Writes Snowflake SQL and pipelines: Dynamic Tables, Streams/Tasks, Snowpipe, Cortex AI/Agents, Snowpark Python, dbt-snowflake, clustering, and RBAC/masking. Use when the user mentions Snowflake, Cortex, Snowpark, Snowpipe, Dynamic Tables, or AI_COMPLETE on Snowflake. Not for BigQuery, Databricks, Redshift, or generic pandas ETL. Never use ACCOUNTADMIN for app roles or omit the colon prefix on SQL procedure variables."
version: 1.0.1
category: data-engineering
risk: safe
source: community
date_added: "2026-03-24"
---

# Snowflake Development

You are a Snowflake development expert. Apply these rules when writing SQL, building data pipelines, using Cortex AI, or working with Snowpark Python on Snowflake.

## When to Use

- When the user asks for help with **Snowflake SQL**, stored procedures, semi-structured data, MERGE/upserts, or query optimization.
- When building **data pipelines** with Dynamic Tables, Streams + Tasks, or Snowpipe.
- When integrating **Cortex AI** functions (AI_COMPLETE, AI_CLASSIFY, AI_FILTER, AI_EXTRACT, AI_SENTIMENT, AI_PARSE_DOCUMENT, AI_REDACT) or **Cortex Agents**.
- When writing **Snowpark Python** for server-side DataFrame processing or UDFs.
- When configuring **dbt on Snowflake** with dynamic table or incremental materializations.
- When tuning **performance** (cluster keys, search optimization, warehouse sizing) or hardening **security** (RBAC, masking policies, network policies).

Trigger keywords: Snowflake, Cortex, Snowpark, Dynamic Table, Stream, Task, Snowpipe, dbt Snowflake, AI_COMPLETE, AI_CLASSIFY, Cortex Agent.

## Prerequisites

- A Snowflake account with appropriate role grants (not ACCOUNTADMIN for development work).
- SnowSQL CLI or Snowflake VS Code extension for executing SQL.
- For Snowpark Python: `snowflake-snowpark-python` package installed (`pip install snowflake-snowpark-python`).
- For dbt: `dbt-snowflake` adapter installed (`pip install dbt-snowflake`).
- Environment variables for credentials — never hardcode secrets. Use `YOUR_KEY` / `YOUR_PASSWORD` placeholders in examples.
- Windows host is primary (PowerShell). When setting environment variables in PowerShell, use `$env:SNOWFLAKE_ACCOUNT = "your_account"`.

## Procedure

### 1. SQL Best Practices

#### Naming and Style

1. Use `snake_case` for all identifiers. Avoid double-quoted identifiers — they create case-sensitive names requiring constant quoting.
2. Use CTEs (`WITH` clauses) over nested subqueries for readability and maintainability.
3. Use `CREATE OR REPLACE` for idempotent DDL.
4. Use explicit column lists — never `SELECT *` in production. Snowflake's columnar storage scans only referenced columns, so `SELECT *` wastes compute and breaks on schema changes.

#### Stored Procedures — Colon Prefix Rule

In SQL stored procedures (`BEGIN...END` blocks), variables and parameters **must** use the colon `:` prefix inside SQL statements. Without it, Snowflake raises "invalid identifier" errors.

**BAD:**
```sql
CREATE PROCEDURE my_proc(p_id INT) RETURNS STRING LANGUAGE SQL AS
BEGIN
    LET result STRING;
    SELECT name INTO result FROM users WHERE id = p_id;
    RETURN result;
END;
```

**GOOD:**
```sql
CREATE PROCEDURE my_proc(p_id INT) RETURNS STRING LANGUAGE SQL AS
BEGIN
    LET result STRING;
    SELECT name INTO :result FROM users WHERE id = :p_id;
    RETURN result;
END;
```

#### Semi-Structured Data

1. Use `VARIANT`, `OBJECT`, `ARRAY` for JSON/Avro/Parquet/ORC.
2. Access nested fields with dot notation: `src:customer.name::STRING`. Always cast explicitly: `src:price::NUMBER(10,2)`.
3. VARIANT null vs SQL NULL: JSON `null` is stored as the string `"null"`. Use `STRIP_NULL_VALUE = TRUE` on load to avoid this.
4. Flatten arrays with `LATERAL FLATTEN`:

```sql
SELECT f.value:name::STRING AS item_name, f.value:price::NUMBER(10,2) AS item_price
FROM my_table, LATERAL FLATTEN(input => src:items) f;
```

#### MERGE for Upserts

```sql
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.name = s.name, t.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (id, name, updated_at) VALUES (s.id, s.name, CURRENT_TIMESTAMP());
```

### 2. Data Pipelines

#### Choosing Your Approach

| Approach | When to Use |
|----------|-------------|
| Dynamic Tables | Declarative transformations. **Default choice.** Define the query, Snowflake handles refresh. |
| Streams + Tasks | Imperative CDC. Use for procedural logic, stored procedure calls. |
| Snowpipe | Continuous file loading from S3/GCS/Azure. |

#### Dynamic Tables

```sql
CREATE OR REPLACE DYNAMIC TABLE cleaned_events
    TARGET_LAG = '5 minutes'
    WAREHOUSE = transform_wh
    AS
    SELECT event_id, event_type, user_id, event_timestamp
    FROM raw_events
    WHERE event_type IS NOT NULL;
```

**Key rules (HARD):**
- Set `TARGET_LAG` progressively: tighter at top of the DAG, looser at bottom.
- Incremental DTs **cannot** depend on Full refresh DTs.
- `SELECT *` breaks on schema changes — use explicit column lists.
- Change tracking must stay enabled on base tables.
- Views cannot sit between two Dynamic Tables.

#### Streams and Tasks

```sql
CREATE OR REPLACE STREAM raw_stream ON TABLE raw_events;

CREATE OR REPLACE TASK process_events
    WAREHOUSE = transform_wh
    SCHEDULE = 'USING CRON 0 */1 * * * America/Los_Angeles'
    WHEN SYSTEM$STREAM_HAS_DATA('raw_stream')
    AS INSERT INTO cleaned_events SELECT ... FROM raw_stream;

-- Tasks start SUSPENDED — you MUST resume them
ALTER TASK process_events RESUME;
```

### 3. Cortex AI

#### Function Reference

| Function | Purpose |
|----------|---------|
| `AI_COMPLETE` | LLM completion (text, images, documents) |
| `AI_CLASSIFY` | Classify into categories (up to 500 labels) |
| `AI_FILTER` | Boolean filter on text/images |
| `AI_EXTRACT` | Structured extraction from text/images/documents |
| `AI_SENTIMENT` | Sentiment score (-1 to 1) |
| `AI_PARSE_DOCUMENT` | OCR or layout extraction |
| `AI_REDACT` | PII removal |

**Deprecated — do NOT use:** `COMPLETE`, `CLASSIFY_TEXT`, `EXTRACT_ANSWER`, `PARSE_DOCUMENT`, `SUMMARIZE`, `TRANSLATE`, `SENTIMENT`, `EMBED_TEXT_768`.

#### TO_FILE — Common Error Source

Stage path and filename are **SEPARATE** arguments:

```sql
-- BAD: TO_FILE('@stage/file.pdf')
-- GOOD:
TO_FILE('@db.schema.mystage', 'invoice.pdf')
```

#### Use AI_CLASSIFY for Classification (Not AI_COMPLETE)

```sql
SELECT AI_CLASSIFY(ticket_text,
    ['billing', 'technical', 'account']):labels[0]::VARCHAR AS category
FROM tickets;
```

#### Cortex Agents

```sql
CREATE OR REPLACE AGENT my_db.my_schema.sales_agent
FROM SPECIFICATION $spec$
{
    "models": {"orchestration": "auto"},
    "instructions": {
        "orchestration": "You are SalesBot...",
        "response": "Be concise."
    },
    "tools": [{"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Sales", "description": "Queries sales..."}}],
    "tool_resources": {"Sales": {"semantic_model_file": "@stage/model.yaml"}}
}
$spec$;
```

**Agent rules (HARD):**
- Use `$spec$` delimiter (not `$$`).
- `models` must be an object, not an array.
- `tool_resources` is a separate top-level object, not nested inside tools.
- Do NOT include empty/null values in edit specs — this clears existing values.
- Tool descriptions are the #1 quality factor for agent performance.
- Never modify production agents directly — clone first, test on the clone, then promote.

### 4. Snowpark Python

```python
from snowflake.snowpark import Session
import os

session = Session.builder.configs({
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "role": "my_role", "warehouse": "my_wh",
    "database": "my_db", "schema": "my_schema"
}).create()
```

**Rules (HARD):**
- Never hardcode credentials. Always use environment variables or a secrets manager.
- DataFrames are lazy — executed only on `collect()`/`show()`/`to_pandas()`.
- Do NOT use `collect()` on large DataFrames — process server-side with `save_as_table()` or write to a stage.
- Use **vectorized UDFs** (10-100x faster) for batch/ML workloads instead of scalar UDFs.

### 5. dbt on Snowflake

Dynamic table materialization (streaming/near-real-time marts):
```sql
{{ config(materialized='dynamic_table', snowflake_warehouse='transforming', target_lag='1 hour') }}
```

Incremental materialization (large fact tables):
```sql
{{ config(materialized='incremental', unique_key='event_id') }}
```

Snowflake-specific configs (combine with any materialization):
```sql
{{ config(transient=true, copy_grants=true, query_tag='team_daily') }}
```

**Rules (HARD):**
- Do NOT use `{{ this }}` without `{% if is_incremental() %}` guard — it will full-refresh and clobber data.
- Use `dynamic_table` materialization for streaming/near-real-time marts.

### 6. Performance Tuning

1. **Cluster keys**: Only for multi-TB tables, on columns used in WHERE/JOIN/GROUP BY. Do not cluster small tables.
2. **Search Optimization**: `ALTER TABLE t ADD SEARCH OPTIMIZATION ON EQUALITY(col);`
3. **Warehouse sizing**: Start X-Small, scale up only when needed. Set `AUTO_SUSPEND = 60`, `AUTO_RESUME = TRUE`.
4. **Separate warehouses** per workload (ETL, BI, ad-hoc) to avoid contention.
5. **Estimate AI costs first** before running large batch Cortex jobs:

```sql
SELECT SUM(AI_COUNT_TOKENS('claude-4-sonnet', text)) FROM table;
```

### 7. Security Hardening

1. Follow least-privilege RBAC. Use database roles for object-level grants.
2. Audit ACCOUNTADMIN regularly:

```sql
SHOW GRANTS OF ROLE ACCOUNTADMIN;
```

3. Use network policies for IP allowlisting.
4. Use masking policies for PII columns and row access policies for multi-tenant isolation.

## Pitfalls

| Error | Cause | Fix |
|-------|-------|-----|
| "Object does not exist" | Wrong context or missing grants | Fully qualify names (`db.schema.table`), check grants |
| "Invalid identifier" in proc | Missing colon prefix on variable | Use `:variable_name` in SQL statements inside BEGIN...END |
| "Numeric value not recognized" | VARIANT not cast to typed value | `src:field::NUMBER(10,2)` |
| Task not running | Forgot to resume after creation | `ALTER TASK ... RESUME` |
| DT refresh failing | Schema change or tracking disabled | Use explicit columns, check change tracking on base tables |
| Cortex TO_FILE error | Combined stage path and filename in one arg | Split: `TO_FILE('@db.schema.stage', 'file.pdf')` |
| Agent spec rejected | Used `$$` instead of `$spec$` | Use `$spec$` delimiter |
| Agent tools broken | `tool_resources` nested inside `tools` | Move `tool_resources` to top-level object |
| Agent values cleared | Empty/null in edit spec | Omit keys you don't want to change |
| dbt full-refresh clobber | `{{ this }}` without incremental guard | Wrap in `{% if is_incremental() %}` |
| Snowpark OOM on collect() | Large DataFrame pulled to client | Process server-side, use `save_as_table()` |
| JSON null vs SQL NULL | `STRIP_NULL_VALUE` not set on load | Add `STRIP_NULL_VALUE = TRUE` to file format |

## Verification

1. **Dynamic Table is refreshing:**
```sql
SELECT name, state, data_timestamp, refresh_mode
FROM INFORMATION_SCHEMA.DYNAMIC_TABLES
WHERE name = 'CLEANED_EVENTS';
```
Expected: `state = 'OK'`, `data_timestamp` recent relative to `TARGET_LAG`.

2. **Task is running (not suspended):**
```sql
SELECT name, state FROM INFORMATION_SCHEMA.TASKS WHERE name = 'PROCESS_EVENTS';
```
Expected: `state = 'STARTED'`.

3. **Stream has data:**
```sql
SELECT SYSTEM$STREAM_HAS_DATA('raw_stream');
```
Expected: `TRUE` when changes are pending.

4. **Stored procedure executes without "invalid identifier":**
```sql
CALL my_proc(42);
```
Expected: returns result without error.

5. **Cortex AI function returns expected type:**
```sql
SELECT AI_SENTIMENT('I love this product!') AS sentiment;
```
Expected: numeric score between -1 and 1.

6. **Cortex Agent is created:**
```sql
SHOW AGENTS;
```
Expected: agent name appears in results.

7. **Snowpark session connects:**
```python
print(session.sql("SELECT CURRENT_VERSION()").collect()[0][0])
```
Expected: Snowflake version string (e.g., `8.x.x`).

8. **dbt models compile and run:**
```powershell
dbt run --select my_dynamic_table_model
```
Expected: `OK` status for each model.

9. **Search optimization is active:**
```sql
SHOW SEARCH OPTIMIZATION ON TABLE my_table;
```
Expected: row with the optimization type and column.

10. **No ACCOUNTADMIN over-grant:**
```sql
SHOW GRANTS OF ROLE ACCOUNTADMIN;
```
Expected: review list — flag any unexpected user or role grants.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
