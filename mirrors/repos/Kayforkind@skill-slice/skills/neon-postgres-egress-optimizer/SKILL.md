---
name: neon-postgres-egress-optimizer
description: "Finds and fixes application query patterns that inflate Postgres/Neon egress (SELECT *, missing LIMIT, JOIN duplication, in-app aggregation) plus cheap non-prod compute via neon.ts. Use when Neon bills spike, data-transfer costs jump, or list endpoints lack pagination. Not a psql meta-command chair (postgresql-cli) and not a full Neon IaC reference (neon)."
version: 1.0.1
risk: unknown
source: https://github.com/neondatabase/agent-skills/tree/main/skills/neon-postgres-egress-optimizer
source_repo: neondatabase/agent-skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/neondatabase/agent-skills/blob/main/LICENSE
---

# Postgres Egress Optimizer

## Overview

Most high Postgres egress bills come from the application fetching more data than it uses. This skill guides you through diagnosing application-side query patterns that cause excessive data transfer from a Postgres database (especially Neon), then applying targeted fixes. It also covers codifying non-production compute cost controls in `neon.ts` so dev, preview, and CI branches stay cheap by default.

## When to Use

Use this skill when any of the following apply:

- A user mentions high database bills, unexpected data transfer costs, network transfer charges, or egress spikes.
- A user asks "why is my Neon bill so high?" or says "database costs jumped."
- You see `SELECT *` in queries that only use a few columns.
- A list endpoint has no `LIMIT` or pagination.
- A high-frequency query targets static or rarely-changing data.
- Application code fetches full tables and aggregates in-memory.
- A JOIN duplicates wide parent columns across many child rows.

Trigger keywords: egress, data transfer, network transfer, Neon bill, database cost, SELECT *, missing pagination, query bloat, pg_stat_statements.

## Prerequisites

- Read access to the target Postgres / Neon database (for diagnostic queries).
- The `pg_stat_statements` extension must be enabled (on Neon it ships by default but may need `CREATE EXTENSION`).
- If you plan to apply the `neon.ts` infrastructure-as-code changes, the `@neon/config` npm package and the `neon` CLI are required.

## Procedure

### Step 1 — Diagnose with pg_stat_statements

Identify which queries transfer the most data. The primary tool is `pg_stat_statements`.

**1.1  Check extension availability**

```sql
SELECT 1 FROM pg_stat_statements LIMIT 1;
```

If this errors, create the extension:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

On Neon, the extension is available by default but may still need this `CREATE EXTENSION` step.

**1.2  Handle empty or stale stats**

Stats are cleared when a Neon compute scales to zero and restarts. If stats are empty or the compute recently woke up:

1. Reset stats to start a clean measurement window:
   ```sql
   SELECT pg_stat_statements_reset();
   ```
2. Let the application run under representative traffic for **at least one hour**.
3. Return and run the diagnostic queries below.

If the user has stats from a production database, use those. If they have no access to production stats, skip to Step 2 and analyze the codebase directly — code-level patterns are often sufficient to identify the worst offenders.

**1.3  Run diagnostic queries**

Focus on queries that return many rows, return wide rows (JSONB, TEXT, BYTEA columns), or are called very frequently.

Queries returning the most **total rows**:

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY rows DESC
LIMIT 10;
```

Queries returning the most **rows per execution** (poorly scoped SELECTs, missing pagination):

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY avg_rows_per_call DESC
LIMIT 10;
```

**Most frequently called** queries (candidates for caching):

```sql
SELECT query, calls, rows AS total_rows, rows / calls AS avg_rows_per_call
FROM pg_stat_statements
WHERE calls > 0
ORDER BY calls DESC
LIMIT 10;
```

**Longest running** queries (not a direct egress measure, but helps identify problem queries during a spike):

```sql
SELECT query, calls, rows AS total_rows,
  round(total_exec_time::numeric, 2) AS total_exec_time_ms
FROM pg_stat_statements
WHERE calls > 0
ORDER BY total_exec_time DESC
LIMIT 10;
```

**1.4  Interpret results**

Rank findings by estimated egress impact:

- **High row count + wide rows** = biggest egress. A query returning 1,000 rows where each row includes a 50 KB JSONB column transfers ~50 MB per call.
- **Extreme call frequency** on even small queries adds up. A query called 50,000 times/day returning 10 rows each = 500,000 rows/day.
- **Cross-reference with the schema** to identify which columns are wide. Look for JSONB, TEXT, BYTEA, and large VARCHAR columns.

### Step 2 — Analyze the codebase

For each query identified in Step 1 — or for each database query in the codebase if no stats are available — check:

1. Does it select **only** the columns the response needs?
2. Does it return a **bounded** number of rows (`LIMIT` / pagination)?
3. Is it called frequently enough to benefit from **caching**?
4. Does it fetch raw data that gets **aggregated in application code**?
5. Does it use a `JOIN` that **duplicates parent data** across child rows?

### Step 3 — Apply fixes

Apply the appropriate fix for each problem found. Below are the most common egress anti-patterns and their fixes.

#### 3.1  Unused columns (SELECT \*)

**Problem:** The query fetches all columns but the application only uses a few. Large columns (JSONB blobs, TEXT fields) get transferred over the wire and discarded.

Before:

```sql
SELECT * FROM products;
```

After:

```sql
SELECT id, name, price, image_urls FROM products;
```

#### 3.2  Missing pagination

**Problem:** A list endpoint returns all rows with no `LIMIT`. This is an **unbounded egress risk** — every new row in the table increases data transfer on every request. Flag this regardless of current table size.

This is easy to miss because the application may work fine with small datasets. But at scale, an unpaginated endpoint returning 10,000 rows with even moderate column widths can transfer hundreds of megabytes per day.

Before:

```sql
SELECT id, name, price FROM products;
```

After:

```sql
SELECT id, name, price FROM products
ORDER BY id
LIMIT 50 OFFSET 0;
```

When adding pagination, check whether the consuming client already supports paginated responses. If not, pick sensible defaults and document the pagination parameters in the API.

#### 3.3  High-frequency queries on static data

**Problem:** A query is called thousands of times per day but returns data that rarely changes. Every call transfers the same rows from the database. This pattern is only visible from `pg_stat_statements` — the code itself looks normal.

Look for queries with extremely high call counts relative to other queries. Common examples: configuration tables, category lists, feature flags, user role definitions.

**Fix:** Add a caching layer between the application and the database so it avoids hitting the database on every request.

#### 3.4  Application-side aggregation

**Problem:** The application fetches all rows from a table and then computes aggregates (averages, counts, sums, groupings) in application code. The full dataset transfers over the wire even though the result is a small summary.

**Fix:** Push the aggregation into SQL.

Before: the application fetches entire tables and aggregates in code with loops or `.reduce()`.

After:

```sql
SELECT p.category_id,
       AVG(r.rating) AS avg_rating,
       COUNT(r.id) AS review_count
FROM reviews r
INNER JOIN products p ON r.product_id = p.id
GROUP BY p.category_id;
```

#### 3.5  JOIN duplication

**Problem:** A `JOIN` between a wide parent table and a child table duplicates all parent columns across every child row. If a product has 200 reviews and the product row includes a 50 KB JSONB column, the join sends that 50 KB × 200 = ~10 MB for a single request.

This is distinct from the `SELECT *` problem. Even if you select only needed columns, a `JOIN` still repeats the parent data for every child row. The fix is structural: **avoid the join entirely**.

Before:

```sql
SELECT * FROM products
LEFT JOIN reviews ON reviews.product_id = products.id
WHERE products.id = 1;
```

After (two separate queries):

```sql
SELECT id, name, price, description, image_urls FROM products WHERE id = 1;
SELECT id, user_name, rating, body FROM reviews WHERE product_id = 1;
```

Two queries instead of one JOIN. The product data is fetched once. The reviews are fetched once. No duplication.

### Step 4 — Codify non-production compute cost controls (neon.ts)

The fixes above cut **egress** (data transferred out of Postgres). The other big non-prod cost lever is **compute**, and you can codify it durably in `neon.ts` — Neon's infrastructure-as-code file (see the `neon` skill for the full reference) — so dev, preview, and CI branches stay cheap by default instead of relying on per-branch flags.

Install the config package:

```bash
npm i @neon/config
```

Create `neon.ts`:

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  branch: (branch) => {
    if (branch.exists || branch.isDefault) return {}; // don't touch prod
    return {
      ttl: "7d", // ephemeral branches auto-expire instead of accruing storage
      postgres: {
        computeSettings: {
          autoscalingLimitMinCu: 0.25, // scale to zero when idle
          autoscalingLimitMaxCu: 1, // cap autoscaling on throwaway branches
          suspendTimeout: "5m",
        },
      },
    };
  },
});
```

Apply the configuration:

```bash
neon config apply   # apply to the current branch (neon deploy is an alias)
```

This is complementary, not a substitute: query-pattern fixes are what actually reduce egress charges, while these settings keep non-production compute and storage from quietly inflating the same bill. Because `neon checkout` applies the policy when it creates a branch, new dev/preview branches inherit the cheap profile automatically.

## Pitfalls

- **Neon compute scale-to-zero wipes stats.** `pg_stat_statements` data is cleared when a Neon compute suspends and restarts. If stats look empty, reset and re-measure for at least an hour under representative traffic before drawing conclusions.
- **Unbounded queries look fine on small datasets.** An unpaginated endpoint may pass all tests with 100 rows but transfer hundreds of MB/day once the table grows. Always flag missing `LIMIT` regardless of current table size.
- **JOIN duplication is invisible in the code.** The query looks reasonable — it selects only needed columns — but the parent row is repeated for every child row. This is a structural problem, not a column-selection problem. The fix is two separate queries, not a better column list.
- **Column-selection and pagination changes can break clients.** Clients may depend on specific fields or full result sets. After applying fixes, verify the API response shape is still compatible.
- **Caching is not a substitute for query fixes.** A cached query that returns `SELECT *` still transfers full-width rows on cache misses. Fix the query first, then cache.
- **Do not touch production branch settings in `neon.ts`.** The guard `if (branch.exists || branch.isDefault) return {};` exists to protect prod. Removing it can alter production compute settings.

## Verification

After applying fixes:

1. **Run existing tests** to confirm nothing broke.
2. **Check API responses** — make sure the API still returns the same data shape. Column selection and pagination changes can break clients that depend on specific fields or full result sets.
3. **Measure the improvement** — if `pg_stat_statements` data is available:
   ```sql
   SELECT pg_stat_statements_reset();
   ```
   Let traffic run under representative load, then re-run the diagnostic queries from Step 1.3 and compare before/after row counts and call counts.
4. **Confirm `neon.ts` applied correctly** — run `neon config apply` and verify the branch shows the expected compute settings (autoscaling min 0.25 CU, max 1 CU, suspend timeout 5m, TTL 7d for non-production branches).

## Related skills

- `neon` — full reference for Neon infrastructure-as-code (`neon.ts`), branch lifecycle, and compute settings.

## Further reading

- https://neon.com/docs/introduction/network-transfer.md
- https://neon.com/docs/introduction/cost-optimization.md

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
