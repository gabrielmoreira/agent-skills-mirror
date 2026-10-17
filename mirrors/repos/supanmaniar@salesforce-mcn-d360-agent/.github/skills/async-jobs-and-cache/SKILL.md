---
name: async-jobs-and-cache
description: 'Poll long-running Salesforce and Data 360 asynchronous jobs to completion, and manage response caching for repeated reads. Use when waiting on ingestion jobs, segment publishes, ML predictions, SQL query status, data-kit deployments, or when a repeated read looks stale.'
---

# Async Job Polling and Response Caching

Replaces the MCP server's maintenance tools: `mcnext_poll_job` and
`mcnext_cache`.

## When to Use

- Waiting for an ingestion job, segment publish, ML prediction, or data-kit
  deployment to finish
- Polling a Data 360 Query API v2 batch
- A repeated read returns stale data and you need to bypass a cache

## Polling an Async Job

The MCP server's `mcnext_poll_job` repeatedly called a status endpoint until
the response settled. Reproduce that with a bounded shell loop.

### Procedure

1. **Find the status endpoint** in the catalog. It must be a read-only
   (`kind: query` or `kind: read`) endpoint:

   ```bash
   node scripts/catalog-search.mjs list --family data360 --search "job"
   node scripts/catalog-search.mjs describe ingestion-api.get-job-info
   ```

2. **Start the job** and capture its id from the response.

3. **Poll until it settles.** Stop on a terminal status, on no change, or at a
   timeout — never loop forever:

   ```bash
   JOB_ID="<id from the create call>"
   for i in $(seq 1 30); do
     RESP=$(./scripts/sf-api.sh --path "/ssot/ingest/jobs/$JOB_ID" 2>/dev/null || true)
     STATUS=$(printf '%s' "$RESP" | python3 -c "
   import json,sys
   try: print(json.load(sys.stdin).get('status',''))
   except Exception: print('')" 2>/dev/null)

     echo "[$i] status=$STATUS"
     case "$STATUS" in
       SUCCESS|SUCCEEDED|COMPLETED|FAILED|ERROR|CANCELLED) break ;;
     esac
     sleep 5
   done
   printf '%s\n' "$RESP"
   ```

### Known status vocabularies

The catalog does not document a single status vocabulary, and **the status field
is not always at the top level** — responses are often wrapped
(`{"segments":[{...}]}`). Verified field names:

| Domain | Status field | Terminal values |
| --- | --- | --- |
| Segment publish | `publishStatus` | `SUCCESS`, `ERROR` |
| Ingestion jobs | `status` | `SUCCESS`, `FAILED`, `CANCELLED` |
| ML predictions | `status` | `SUCCEEDED`, `FAILED` |
| Query API v2 | — | results present, or `nextBatchId` absent |

A segment also carries `segmentStatus` (`ACTIVE` / `DRAFT`), which describes its
lifecycle rather than the outcome of the last publish. Use `publishStatus` when
waiting on a publish. See the reference file for a `status_of` helper that
searches the payload for any status-like key.

### Query API v2 specifically

`POST /api/v2/query` is asynchronous. It returns a `nextBatchId`; poll
`GET /api/v2/query/:nextBatchId` until the payload contains rows:

```bash
BATCH=$(./scripts/sf-api.sh --tenant --method POST --path /api/v2/query \
  --body '{"sql":"SELECT ssot__Id__c FROM ssot__Individual__dlm LIMIT 10"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('nextBatchId',''))")

for i in $(seq 1 20); do
  OUT=$(./scripts/sf-api.sh --tenant --path "/api/v2/query/$BATCH")
  printf '%s' "$OUT" | grep -q '"data"' && { printf '%s\n' "$OUT"; break; }
  sleep 3
done
```

## Response Caching

The MCP server cached successful `GET` responses for 30 seconds by default.
The CLI has no such cache — every `sf` invocation is a fresh HTTP call — so
**stale reads are not a failure mode here**. If you need to reduce call volume
during a long investigation, cache deliberately:

```bash
# Cache a describe for the duration of a task
mkdir -p .cache
sf sobject describe -s Account -o "$SF_TARGET_ORG" --json > .cache/Account.json
# reuse it
python3 -c "import json; print(len(json.load(open('.cache/Account.json'))['result']['fields']))"
```

Clear it when you are done:

```bash
rm -rf .cache
```

## Gotchas

- **Always bound the loop.** A job that never reaches a terminal status will
  hang an unbounded `while true`. Cap iterations and sleep between polls.
- **Poll intervals of 3–5 seconds** are reasonable; faster polling burns API
  calls against org limits.
- **Check org limits** if polling many jobs concurrently:
  `sf org list limits -o "$SF_TARGET_ORG" --json`.
- **A job that reports no change for several polls** is usually stuck, not slow.
  Report the last payload rather than waiting indefinitely.
- **Do not cache writes.** Only `GET` responses are safe to reuse.

## Reference

- [Async operations reference](./references/async-operations.md)
