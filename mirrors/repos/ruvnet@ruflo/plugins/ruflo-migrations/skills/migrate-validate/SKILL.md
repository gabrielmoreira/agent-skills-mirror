---
name: migrate-validate
description: Validate pending migrations for foreign key consistency, rollback safety, and best practices
argument-hint: ""
allowed-tools: Read Glob Grep Bash mcp__claude-flow__agentdb_hierarchical-recall mcp__claude-flow__agentdb_pattern-store mcp__claude-flow__agentdb_semantic-route
---

# Migrate Validate

Validate all pending database migrations for correctness, safety, and adherence to best practices.

## When to use

Before applying migrations to catch issues early -- foreign key references to non-existent tables, missing rollback SQL, destructive operations without safeguards, and naming convention violations.

## Steps

1. **Find pending migrations** -- use `Glob` to list all migration files, cross-reference with applied history via `mcp__claude-flow__agentdb_hierarchical-recall` to identify pending ones
2. **Parse SQL** -- use `Read` to load each pending `.up.sql` and `.down.sql` file and parse the SQL statements
3. **Check foreign keys** -- verify that all REFERENCES targets exist in the current schema or in prior migrations (both applied and pending)
4. **Check NOT NULL defaults** -- verify that any ADD COLUMN with NOT NULL has a DEFAULT value
5. **Check rollback completeness** -- verify every CREATE/ALTER in the UP file has a corresponding DROP/ALTER in the DOWN file
6. **Flag destructive ops** -- warn on DROP TABLE, DROP COLUMN, TRUNCATE without explicit confirmation
7. **Check idempotency** -- verify IF EXISTS / IF NOT EXISTS is used for safety
8. **Check naming** -- verify table names are plural, column names are snake_case, index names follow `idx_table_column` convention
9. **Store results** -- call `mcp__claude-flow__agentdb_pattern-store` to record validation patterns for future reference
10. **Report** -- display: errors (must fix), warnings (should fix), info (suggestions), with file path and line number for each issue

## CLI alternative

```bash
npx @claude-flow/cli@latest memory search --query "migration validation results" --namespace migrations
```
