---
type: skill
lifecycle: stable
inheritance: inheritable
name: datasource-connectors
description: "Ingestion patterns for CSV, JSON, REST API, SQL, Excel, and Parquet -- guides an LLM through loading data from any common source"
tier: standard
applyTo: "**/*data*,**/*ingest*,**/*connect*,**/*csv*,**/*json*,**/*sql*,**/*excel*,**/*parquet*,**/*api*"
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Datasource Connectors

Guide the user through loading data from any common source into a working dataset.
This module is a decision framework, not a library. It tells the LLM what to ask,
what to watch for, and how to handle each format's quirks.

## When to Use

- The brief names a data source that is not yet loaded
- The user says "the data is in X" where X is a file, database, or API
- The orchestrator's plan includes an Ingest step

## When to Skip

- Data is already loaded (inline table, prior step output, user pasted it)
- The brief says "data is pre-loaded" or "use this dataframe"

## Connector Selection

Ask the user what format the data is in, or infer from the path/URL:

| Signal | Connector |
| --- | --- |
| `.csv`, `.tsv`, `.txt` (tabular) | CSV |
| `.json`, `.jsonl`, `.ndjson` | JSON |
| `http://`, `https://` + returns JSON/XML | REST API |
| Connection string, `.sql`, database name | SQL |
| `.xlsx`, `.xls` | Excel |
| `.parquet`, `.arrow` | Parquet |

If ambiguous, ask. Do not guess the format.

## CSV / TSV

### What to ask

- Does the file have a header row? (default: yes)
- What is the delimiter? (auto-detect: comma, tab, semicolon, pipe)
- What is the encoding? (default: UTF-8; watch for: Latin-1, Windows-1252)

### Quirks to handle

| Problem | Detection | Fix |
| --- | --- | --- |
| Wrong delimiter | First row has one column | Try tab, semicolon, pipe |
| Encoding garbled | Non-ASCII chars show as `?` or `Ã©` | Re-read as Latin-1 or Windows-1252 |
| Trailing commas | Row has one extra empty column | Strip trailing delimiter |
| Quoted fields with commas | Standard CSV; most parsers handle it | Use RFC 4180 compliant parser |
| Mixed line endings | `\r\n` and `\n` in same file | Normalize to `\n` |
| BOM marker | `\xEF\xBB\xBF` at file start | Strip or let parser handle |

### Output

A table with typed columns. Report: row count, column count, detected delimiter,
detected encoding.

## JSON / JSONL

### What to ask

- Is it a single JSON object, an array, or newline-delimited (JSONL)?
- What path holds the data? (e.g., `data.results[]`, root array)

### Quirks to handle

| Problem | Detection | Fix |
| --- | --- | --- |
| Nested objects | Column values are objects, not scalars | Flatten with dot notation (`address.city`) |
| Mixed types in array | Some items have extra/missing keys | Union all keys; fill missing with null |
| Large file (> 100MB) | Slow to parse | Stream with JSONL or chunk |
| Date strings | ISO 8601 or Unix timestamps | Parse to date; state the format detected |

### Output

A flat table. Nested objects flattened to dot-notation columns. Report: record
count, nesting depth, keys found.

## REST API

### What to ask

1. What is the endpoint URL?
2. What authentication is needed? (none, API key, OAuth, bearer token)
3. Does it paginate? (offset, cursor, link header, or single page)
4. What response path holds the data? (e.g., `results[]`)

### Authentication patterns

| Method | How to use | Security |
| --- | --- | --- |
| **API key in header** | `Authorization: Api-Key <key>` or custom header | Never log the key |
| **Bearer token** | `Authorization: Bearer <token>` | Store in env var or secret |
| **OAuth 2.0** | Client credentials or authorization code flow | Use refresh tokens |
| **No auth** | Public API | Still rate-limit respectfully |

Never hardcode credentials. Use environment variables or secret storage.

### Pagination patterns

| Pattern | Detection | Handling |
| --- | --- | --- |
| **Offset** | `?offset=0&limit=100` | Increment offset until empty page |
| **Cursor** | Response has `next_cursor` field | Pass cursor to next request |
| **Link header** | `Link: <url>; rel="next"` | Follow `rel="next"` until absent |
| **Page number** | `?page=1&per_page=50` | Increment page until empty |

Set a maximum page limit (default: 100 pages) to prevent runaway loops.

### Retry and timeout

| Rule | Value |
| --- | --- |
| Timeout per request | 30 seconds |
| Retries on 429/5xx | 3 with exponential backoff (1s, 2s, 4s) |
| Retries on network error | 2 |
| Never retry | 400, 401, 403, 404 (client errors are not transient) |

### Output

A flat table from all pages combined. Report: total records, pages fetched,
any errors skipped.

## SQL

### What to ask

1. What database engine? (PostgreSQL, SQL Server, MySQL, SQLite)
2. Connection string or host/port/database?
3. What table or query?

### Security rules

| Rule | Reason |
| --- | --- |
| **Always use parameterized queries** | Prevents SQL injection |
| **Never interpolate user input into SQL** | Even for table names; use allowlists |
| **Read-only connection** | The pipeline only reads; never write |
| **Credentials in env vars** | Never in code, never in logs |

### Query patterns

```sql
-- Simple table read
SELECT * FROM schema.table_name LIMIT 1000;

-- Filtered read (parameterized)
SELECT * FROM sales WHERE region = @region AND date >= @start_date;

-- Aggregated read (push aggregation to the database when possible)
SELECT region, month, SUM(revenue) AS revenue
FROM sales
GROUP BY region, month;
```

Push aggregation and filtering to the database when possible. Pulling raw data
and aggregating in the LLM wastes tokens and is slower.

### Output

A table. Report: row count, column count, query execution time, database engine.

## Excel

### What to ask

1. Which sheet? (default: first sheet)
2. Does the data start at A1 or is there a header region to skip?
3. Are there named ranges?

### Quirks to handle

| Problem | Detection | Fix |
| --- | --- | --- |
| Multiple sheets | Workbook has > 1 sheet | Ask which sheet; default to first |
| Header not in row 1 | First rows are title/metadata | Ask for header row number |
| Merged cells | Values span multiple rows/columns | Unmerge and fill down |
| Formulas | Cells contain formulas, not values | Read values, not formulas |
| Mixed types in column | Numbers and text in same column | Coerce to string; flag for data-preparation |
| Date serial numbers | Dates stored as integers (e.g., 45678) | Convert using Excel epoch (1899-12-30) |

### Output

A table from the specified sheet and range. Report: sheet name, row count,
column count, any merged cells detected.

## Parquet / Arrow

### What to ask

- Path to the file or directory (partitioned datasets use directories)

### Advantages

Parquet is self-describing: schema, types, and encoding are embedded. No
delimiter guessing, no encoding issues, no header detection.

### Quirks to handle

| Problem | Detection | Fix |
| --- | --- | --- |
| Partitioned directory | Path is a directory with `part-*.parquet` files | Read all partitions |
| Nested columns (struct/list) | Schema shows complex types | Flatten or ask user which fields |
| Large file | > 1M rows | Sample or filter before loading all |

### Output

A typed table. Report: row count, column count, schema summary (types from
the Parquet metadata).

## Error Handling (all connectors)

| Situation | Action |
| --- | --- |
| File not found | Report the exact path tried. Ask user to verify. |
| Permission denied | Report the error. Do not retry. Ask user to fix permissions. |
| Empty dataset (0 rows) | Report it. Push back: "file exists but has no data rows." |
| Partial data (truncated) | Report row count. Ask if this is expected. |
| Unsupported format | State what was detected. Ask user for the correct format. |

Never fail silently. Every error must produce a specific, actionable message.

## Output Contract

Pass to the next module (`data-preparation`):

- The loaded dataset (or a reference to it)
- A one-line summary: format, row count, column count, source path
- Any warnings (encoding fallback, partial data, skipped errors)
