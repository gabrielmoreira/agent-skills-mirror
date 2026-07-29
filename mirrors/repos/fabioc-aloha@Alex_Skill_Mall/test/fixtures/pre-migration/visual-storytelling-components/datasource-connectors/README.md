# datasource-connectors

Ingestion patterns for CSV, JSON, REST API, SQL, Excel, and Parquet. A decision
framework that guides an LLM through loading data from any common source.

**Status**: Published (v1.0.0)

## What It Does

- **CSV/TSV**: Encoding detection, delimiter inference, header handling, BOM stripping
- **JSON/JSONL**: Path extraction, nested object flattening, mixed-type handling
- **REST API**: Pagination (offset, cursor, link-header), auth (API key, OAuth, bearer), retry/timeout
- **SQL**: Parameterized queries, connection string patterns, injection prevention, push-down aggregation
- **Excel**: Sheet selection, named ranges, header detection, merged cell handling, date serial conversion
- **Parquet/Arrow**: Schema inspection, partitioned directory reading, nested column flattening
- **Error handling**: Retries, timeouts, partial data, encoding fallbacks, actionable error messages

## Pipeline Position

Fires after `storytelling-requirements`, before `data-preparation`.

## Install

```bash
cp -r plugins/datasource-connectors/ /your/project/.github/skills/local/datasource-connectors/
```

## Security

- Always use parameterized queries for SQL (no string interpolation)
- Never hardcode credentials (use env vars or secret storage)
- Read-only connections only
- Never log API keys or tokens
