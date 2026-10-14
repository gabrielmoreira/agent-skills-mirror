---
name: date-filter-spec
description: Produce and validate a per-table date-filtering decision spec for an Autopilot Preflight source, deciding which tables get filtered to a date range vs exported in full. Use this whenever the user wants to prepare, generate, review, or fix a date-range export spec for autopilot-preflight, or mentions "date filter spec", "date-range export", or a table's date column being ambiguous.
---

# Date-Filter Spec

Produces `spec.json`: a reviewable, per-table decision about whether a table is filtered to an exact date range on export, or exported in full. This is a design-time artifact. It is not trusted blindly, and it does not run an export.

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, and MAY in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

Column-name and type heuristics for picking a date column do not generalize across real schemas. Every table's decision MUST be backed by real evidence (a column comment, FK position, aggregate stats) or MUST be marked `unresolved`. Never guess.

A chosen date column also has a value encoding — native `DATE`/`TIMESTAMP`, or a raw numeric encoding such as a packed `YYYYMMDD` integer. This is never guessed either: it comes verbatim from `inspect column-stats`' `detected_date_format`, which runs a deterministic SQL probe against the column's live min/max. If the probe found nothing consistent, the table is marked `unresolved_format` — a column choice with an unconfirmed encoding, distinct from `unresolved` (no confident column at all).

## Constraints

- MUST NOT assert a `date_column` unless the evidence for it is confident. If no column is clearly indicated, mark the table `unresolved` and list its plausible candidates.
- MUST NOT inspect customer row data. Only `autopilot-preflight discover` (schema structure) and `autopilot-preflight inspect column-stats` (aggregate stats) MAY be used as evidence sources. No available tool returns row-level data; treat wanting to run a `SELECT *`-equivalent as a signal to stop.
- The spec and discover JSON MUST remain tool-agnostic: MUST NOT contain Claude-specific fields, and MUST NOT contain prose explanations outside the `rationale` field.
- Every `preflight` invocation MUST be a Bash tool call to the compiled binary, never an MCP server call, and MUST NOT pass `--interactive` — a Bash tool call has no TTY, and an interactive prompt will fail with "could not open a new TTY" instead of proceeding. Supply every value (`--database`, `--schema`, `--connection`, etc.) as an explicit flag.
- Every invocation of a `snowflake` subcommand MUST include `--connection <NAME>` using the connection resolved in Inputs. Omitting it silently targets the `default` profile instead of the intended one.
- MUST NOT initiate or run any export. Producing and validating `spec.json` is the entire scope.

## Inputs

Before asking the operator anything, check for information already available on disk:

1. **Connection.** Check `~/.snowflake/connections.toml` for configured connection names (each `[section-name]` line is one connection) before asking the operator to name one. If exactly one connection exists, propose it directly rather than asking. If multiple exist, present them as concrete choices, not as an open-ended question. MUST NOT read connection credentials from this file — only the section names.
2. **Existing discover output.** Check the working directory for a `<database>.discover.json` matching the target database before asking whether one exists.

Ask the operator only for what the checks above could not determine:
1. Which connector and connection to use (skip if exactly one connection was found and the operator hasn't indicated otherwise).
2. The database (and optionally a schema filter) to generate a spec for — this cannot be inferred from disk alone and MUST always be confirmed with the operator.
3. Whether to reuse a discovered existing `discover.json` or regenerate it (skip this question if none exists — generation is then implied).

## Procedure

### 1. Get schema context

If a `<database>.discover.json` does not already exist for this database, generate one:

```
autopilot-preflight discover snowflake --connection CONNECTION --database DBNAME [--schema SCHEMA ...] -o discover.json
```

This step produces structure only — tables, columns with types and comments, FK graph, row counts, and a `schema_fingerprint`. No data exposure, no judgment calls.

### 2. Decide each table's mode (Tier 0: structural evidence)

For every table in the discover output, look for a column representing the table's core business date/timestamp, weighing evidence in this order:

1. **Column comment.** A comment such as "Order posting date" SHOULD be treated as strong, explicit evidence.
2. **FK position.** A table with many *inbound* foreign keys and few or no non-audit date columns SHOULD be treated as a dimension/reference table (customers, products, calendars) and assigned `mode: "full"`. A table with mostly *outbound* FKs and a clear business date SHOULD be treated as a fact/transaction table and is a good `filter` candidate.
3. **Naming.** This is the weakest signal and MUST NOT be used alone when stronger evidence is available. `CreatedAt`/`ModifiedAt`/`UpdatedAt`-style names SHOULD NOT be selected as the filter column unless no other candidate exists, and this reasoning MUST be stated in the rationale if it is. Multiple similarly-named date columns (`OrderDate`, `ShipDate`, `DueDate`) MUST be treated as a disambiguation signal, not resolved by arbitrary choice.

If the evidence converges on one column with no serious competing candidate, tentatively select it for `mode: "filter"` and proceed to step 4 to confirm its date_format. If the table has no plausible business date column, assign `mode: "full"`. If the evidence does not converge — multiple equally plausible candidates, or contradictory signals — proceed to Tier 1 before deciding.

### 3. Disambiguate remaining tables (Tier 1: aggregate stats)

For any table still ambiguous after Tier 0, call the coverage tool on each remaining candidate column:

```
autopilot-preflight inspect column-stats snowflake --connection CONNECTION --database DBNAME --schema SCHEMA --table TABLE --column CANDIDATE1 --column CANDIDATE2
```

Read `null_pct`, `distinct_count`, and `min`/`max` per candidate. A column with a high null rate or a suspiciously narrow date range SHOULD be treated as a poor filter boundary regardless of its name.

If this still does not produce a single confident answer, assign `mode: "unresolved"`. List every column seriously considered under `candidates`, and explain in the rationale why none of them won outright. This is an expected, valid outcome, not a failure. Otherwise, the winning column proceeds to step 4.

### 4. Confirm the date format (Tier 2: deterministic probe)

A column choice is never final until its value encoding is confirmed. If step 2 or 3 already called `inspect column-stats` on the chosen column, reuse that output; otherwise call it now for that column alone.

Read `detected_date_format` from the output:
- If it is one of `"native"`, `"yyyymmdd_integer"`, or `"yyyymmddhhmmss_numeric"`, the table is confirmed: assign `mode: "filter"` and copy that value verbatim into `date_format`.
- If it is `null`, the column choice stands but its encoding does not: assign `mode: "unresolved_format"` instead. This is an expected, valid outcome, not a failure — the column is right, but no supported encoding could be confirmed from its live min/max.

MUST NOT infer or guess a `date_format` from the column's declared type or name — `detected_date_format` is the only source of truth, since it comes from a deterministic SQL probe against live data.

### 5. Write the spec

Every table discovered in step 1 MUST appear in the spec exactly once — none skipped, none invented. Write it to `<database>.spec.json` (mirroring the `<database>.discover.json` naming convention) unless the operator specifies a different path. Shape:

```json
{
  "version": "1.1",
  "schema_fingerprint": "<copied verbatim from discover output>",
  "tables": [
    {"schema": "SALES", "table": "SalesOrderHeader", "mode": "filter",
     "date_column": "OrderDate", "date_format": "native", "confidence": 0.95,
     "rationale": "column comment: 'Order posting date'; DueDate/ShipDate are logistics, ModifiedDate is audit"},
    {"schema": "SALES", "table": "Customer", "mode": "full",
     "confidence": 1.0, "rationale": "high inbound FK count, no non-audit date column"},
    {"schema": "LOGISTICS", "table": "ShipmentTracking", "mode": "unresolved",
     "candidates": ["ShipDate", "ReceivedDate", "CreatedAt"],
     "rationale": "no comment or FK signal distinguishes the three; needs operator input"},
    {"schema": "SAP", "table": "BSEG", "mode": "unresolved_format",
     "date_column": "BUDAT",
     "rationale": "BUDAT is the confirmed posting-date column (FK and naming evidence), but detected_date_format was null — live min/max didn't parse cleanly under any supported encoding"}
  ],
  "default_mode": "full"
}
```

Requirements:
- `schema_fingerprint` MUST be copied verbatim from the discover output. MUST NOT be recomputed.
- `rationale` is REQUIRED on every table and MUST name the actual evidence, not merely restate the mode.
- `mode: "filter"` REQUIRES `date_column`, `date_format`, and `confidence`. `candidates` MUST NOT be present.
- `mode: "full"` REQUIRES `confidence`. `date_column`, `date_format`, and `candidates` MUST NOT be present.
- `mode: "unresolved"` REQUIRES `candidates` (at least 2 entries — a single candidate MUST NOT be treated as ambiguous). `date_column`, `date_format`, and `confidence` MUST NOT be present.
- `mode: "unresolved_format"` REQUIRES `date_column`. `date_format`, `confidence`, and `candidates` MUST NOT be present.

### 6. Validate

```
autopilot-preflight validate-date-filter-spec --spec DBNAME.spec.json --discover discover.json
```

This command checks structural correctness (required fields, valid enums, no stray fields) and cross-references the spec against the discover output (fingerprint match, no missing or hallucinated tables, `date_column`/`candidates` exist as real columns, `date_format` looks consistent with the column's declared type). It takes no `--connection` — it only reads the two local files. It returns `{"valid": ..., "errors": [...], "warnings": [...]}`.

- If `valid` is `false`, fix every listed error and re-run this command. MUST NOT present a spec to the operator that has not passed this check.
- Warnings (e.g. a `date_format` that looks inconsistent with the column's declared type) do not block validity, but reconsider the underlying decision before disregarding one.

### 7. Present for review

Summarize the result for the operator, stating how many tables are `filter` and how many are `full`, and call out every `unresolved` and `unresolved_format` table by name — `unresolved` alongside its candidates, `unresolved_format` alongside its confirmed column — since both require a human decision before the spec can be used.
