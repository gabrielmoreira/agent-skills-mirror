---
name: guide
description: >
  Explains what autopilot-preflight does, when to use each command, and how
  to set up Snowflake connectivity. Use when the user asks "what is
  autopilot-preflight", "how do I use preflight", "what commands does
  preflight have", "help me set up a Snowflake connection for preflight",
  "how do I export data for Autopilot", or needs orientation before running
  any preflight command.
---

# Autopilot Preflight Guide

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, and MAY in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Autopilot Preflight is a CLI that extracts data from customer source systems (Snowflake today, Databricks and Azure Fabric planned) into DuckDB files for ingestion by the Maxa Autopilot pipeline. It ships as a single native binary with no runtime dependencies.

## When to use it

Use autopilot-preflight when the goal is to get a portable snapshot of a customer's source data into DuckDB for Autopilot processing. The typical workflow is:

1. **Connect** — verify connectivity to the source system
2. **Discover** — understand what's in the source (schema, tables, columns, foreign keys)
3. **Classify** — decide per-table date-filtering strategy (the `date-filter-spec` skill handles this)
4. **Export** — extract data into a DuckDB file

## Commands

### `test` — verify a connection

```
autopilot-preflight test snowflake --connection CONNECTION
```

Run this first. Confirms the connection profile works and the credentials are valid. No data is read.

### `discover` — explore the source schema

```
autopilot-preflight discover snowflake \
  --connection CONNECTION \
  --database DATABASE \
  [--schema SCHEMA ...] \
  -o DATABASE.discover.json
```

Produces a JSON file with every table's columns (types, comments), foreign key graph, and row counts. No row data is exported — this is structure only. The output is the foundation for the `date-filter-spec` skill and for understanding the source before exporting.

### `inspect column-stats` — targeted column analysis

```
autopilot-preflight inspect column-stats snowflake \
  --connection CONNECTION \
  --database DATABASE \
  --schema SCHEMA \
  --table TABLE \
  --column COLUMN [--column COLUMN ...]
```

Computes aggregate statistics (null rate, distinct count, min/max, detected date format) for specific columns without exporting data. Used by the `date-filter-spec` skill to disambiguate date columns and confirm date encoding formats.

### `validate-date-filter-spec` — validate a spec file

```
autopilot-preflight validate-date-filter-spec \
  --spec DATABASE.spec.json \
  --discover DATABASE.discover.json
```

Validates a date-filter spec against the discover output. Checks structural correctness and cross-references tables, columns, and fingerprints. Runs locally against the two JSON files — no connection needed.

### `run` — export data

```
autopilot-preflight run snowflake \
  --connection CONNECTION \
  --database DATABASE \
  [--schema SCHEMA ...] \
  [--sampling-strategy STRATEGY] \
  [--sample-size N] \
  [-o OUTPUT.duckdb]
```

Exports data into a DuckDB file. This is the main operation. Key flags:

| Flag | Default | Purpose |
|---|---|---|
| `--sampling-strategy` | `row-count` | How to sample: `row-count`, `referential-integrity`, `coverage-maximizing`, `full` |
| `--sample-size` | 10000 | Max rows per table (ignored by `full`) |
| `--schema` | all | Specific schema(s) to include (repeatable) |
| `--schema-pattern` | | SQL LIKE pattern for schema filtering |
| `--exclude-table-pattern` | | SQL LIKE pattern to exclude tables |
| `--compute-stats` | false | Compute column statistics on full source |
| `-o` | `DATABASE.duckdb` | Output file path |

## Snowflake connection setup

Autopilot Preflight reads `~/.snowflake/connections.toml` — the same format used by the Snowflake CLI (`snow`). Each `[section]` is a named connection.

### Minimal connection (password)

```toml
[default]
account = "orgname-accountname"
user = "username"
password = "..."
warehouse = "WAREHOUSE_NAME"
```

### Key-pair authentication (recommended for automation)

```toml
[prod]
account = "orgname-accountname"
user = "svc_maxa"
warehouse = "PROD_WH"
authenticator = "snowflake_jwt"
private_key_file = "~/.snowflake/rsa_key.p8"
```

For encrypted private keys, set the `PRIVATE_KEY_PASSPHRASE` environment variable.

### Browser SSO (for interactive use)

```toml
[dev]
account = "orgname-accountname"
user = "jdoe"
warehouse = "DEV_WH"
authenticator = "externalbrowser"
```

### Supported authenticators

| Value | Method |
|---|---|
| `snowflake` | Username/password (default) |
| `snowflake_jwt` | Key-pair |
| `externalbrowser` | Browser-based SSO |
| `oauth` | OAuth bearer token (requires `token` field) |
| `programmatic_access_token` | PAT (requires `token` field) |

## Important constraints

- Every CLI invocation MUST be a Bash tool call, not an MCP server call.
- MUST NOT pass `--interactive` (`-i`) — there is no TTY in a tool call and it will hang.
- Every `snowflake` subcommand MUST include `--connection NAME`. Omitting it silently uses `default`, which may be the wrong profile.
- The `discover` and `inspect` commands read schema and aggregates only — no row-level data is ever exposed.
- The `run` command exports sampled data by default (10,000 rows per table). Use `--sampling-strategy full` only when a complete export is explicitly requested.

## Typical workflow

1. Check if `autopilot-preflight` is installed (`autopilot-preflight --version`). If not, use the `install` skill.
2. Verify Snowflake connection: `autopilot-preflight test snowflake --connection CONNECTION`
3. Discover the schema: `autopilot-preflight discover snowflake --connection CONNECTION --database DB -o DB.discover.json`
4. Generate a date-filter spec: use the `date-filter-spec` skill.
5. Export data: `autopilot-preflight run snowflake --connection CONNECTION --database DB`
