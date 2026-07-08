# Runtime Validation (Workflow B2)

B2 = fetch live log records → run B1 static validation on them.

No DQL query pack is embedded here. All validation logic lives in `mapping-workflow.md § Workflow B1` and `validation-rules.md`.

## Procedure

### Step 0 — Confirm Inputs

1. `log.source` value to query (e.g. `"CyberArk"`, `"Okta"`, `"SignInLogs"`).
2. Time window (default: `now()-24h`).
3. Execution method: live DQL execution against the connected tenant.

### Step 1 — Fetch Sample Records

Execute a DQL query against the live tenant to fetch 3–5 recent log records for the given `log.source`.

Query pattern:

```dql-snippet
fetch logs, from:now()-24h
| filter log.source == "<LOG_SOURCE>"
| sort timestamp desc
| limit 5
```

If 0 records returned: report `🔴 fail — no logs found`. Ask the user to verify `log.source` and time window before continuing.

### Step 2 — Run B1 on Each Fetched Record

Apply the full Workflow B1 procedure from `mapping-workflow.md` to each fetched record.

Treat the fetched records as **final ingested events** — `content` is expected to be a string, top-level semantic fields are expected to be promoted.

### Step 3 — Aggregate and Report

Consolidate B1 findings across all fetched records:

- If the same issue appears on all records: report as a systemic gap.
- If an issue appears on only some records: note variability and which conditions trigger it.

Produce the Validation Summary table and the full B1 report sections from `report-format.md § Workflow B2`.

## Notes

- The B2 query is always a simple `fetch logs | filter log.source == "..."` — do not add complex DQL unless the user requests it.
- If the user asks to narrow the query (e.g. by time, by audit class, by specific `audit.action`), adjust the filter accordingly and note it in the Runtime Context section.
- Do not interpret fetched records beyond what B1 covers. B2 scope = fetch + B1.
