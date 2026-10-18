---
name: data360-api
description: 'Call Salesforce Data 360 core APIs (Query API v1/v2, Profile API, Ingestion API, Metadata API, Data Graph API, Calculated Insights, Universal ID Lookup) from the Salesforce CLI without an MCP server. Use when querying Data 360 data with SQL, reading unified profiles, ingesting event data, or inspecting Data 360 metadata and data graphs.'
---

# Data 360 Core API

Replaces the MCP server's `mcnext_*` catalog tools for the `data360` family
(35 endpoints across 9 groups).

## When to Use

- Running SQL against Data 360 (Query API v1 or v2)
- Reading unified individual or account profiles
- Ingesting event data via the Ingestion API
- Inspecting Data 360 metadata, DMOs, or calculated insights
- Traversing data graphs or resolving universal IDs

## Routing — read this first

The `data360` family is the **only** family that does not live on the org
instance. Its paths begin `/api/v1` or `/api/v2` and are served from the
Data 360 **tenant host**:

```
{tenantUrl}/api/v1/...
```

`sf api request rest` always prefixes the org instance and ignores absolute
URLs, so it **cannot** reach these endpoints. Use tenant mode:

```bash
export DATA360_TENANT_URL=https://my-tenant.c360a.salesforce.com
./scripts/sf-api.sh --tenant --path /api/v1/metadata
```

If `DATA360_TENANT_URL` is unset the script fails fast with a clear message
rather than guessing a hostname. Some orgs serve the `ssot/*` endpoints from
the core instance host — those belong to the `data360-connect` family, not this
one. See [data360-connect-api](../data360-connect-api/SKILL.md).

### Authentication — this family needs a Connected App

Unlike every other family, `data360` **cannot** run off the `sf org login`
session. The tenant host sits behind a service mesh that only accepts an OAuth
2.0 client-credentials **JWT**. A session token is opaque, so the mesh rejects
it with **HTTP 400 and an empty body** — on every path, regardless of headers.

Mint a client-credentials token and export it:

```bash
eval "$(./scripts/sf-tenant-token.sh --export)"
./scripts/sf-api.sh --tenant --path /api/v1/query --method POST --body @q.json
```

This needs a Connected App with the Data 360 scopes (`cdp_query_api`,
`cdp_profile_api`, `cdp_ingest_api`). If you do not have one yet, see
[CONNECTED-APP-SETUP.md](../../../docs/CONNECTED-APP-SETUP.md).

If you hit a 400, run `./scripts/diagnose.sh` before changing anything else. The
400-vs-401 split identifies the cause: **400 means the credential is not a JWT;
401 means it was parsed and rejected.** [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md)

## Procedure

1. **Discover the endpoint:**

   ```bash
   node scripts/catalog-search.mjs list --family data360
   node scripts/catalog-search.mjs list --family data360 --group "Query API V2"
   ```

2. **Inspect parameters and body shape:**

   ```bash
   node scripts/catalog-search.mjs describe query-api-v2.query
   ```

3. **Call it in tenant mode:**

   ```bash
   ./scripts/sf-api.sh --tenant --method POST --path /api/v2/query \
     --body '{"sql":"SELECT ssot__Id__c FROM ssot__Individual__dlm LIMIT 10"}'
   ```

## Common Operations

| Operation | Method | Path |
| --- | --- | --- |
| Query (v1) | POST | `/api/v1/query` |
| Query (v2) | POST | `/api/v2/query` |
| Fetch next query batch | GET | `/api/v2/query/:nextBatchId` |
| List metadata | GET | `/api/v1/metadata` |
| Profile metadata | GET | `/api/v1/profile/metadata` |
| Get a profile | GET | `/api/v1/profile/:dmoApiName/:dmoRecordId` |
| Profile child records | GET | `/api/v1/profile/:dmoParentApiName/:dmoParentRecordId/:dmoChildApiName` |
| Calculated insight | GET | `/api/v1/insight/calculated-insights/:ci_name` |
| Data graph metadata | GET | `/api/v1/dataGraph/metadata` |
| Data graph record | GET | `/api/v1/dataGraph/:dataGraphName/:dataGraphRecordId` |
| Universal ID lookup | GET | `/api/v1/universalIdLookup/:entityName/:dataSourceId__c/:dataSourceObjectId__c/:sourceRecordId__c` |
| Create ingest job | POST | `/api/v1/ingest/jobs` |
| Get ingest job | GET | `/api/v1/ingest/jobs/:jobId` |
| Upload job batches | PUT | `/api/v1/ingest/jobs/:jobId/batches` |

## Gotchas

- **Query API v2 is asynchronous.** `POST /api/v2/query` returns a
  `nextBatchId`; poll `GET /api/v2/query/:nextBatchId` until results are ready.
  Use the [async-jobs-and-cache](../async-jobs-and-cache/SKILL.md) skill.
- **DMO API names end in `__dlm`** (e.g. `ssot__Individual__dlm`), not `__c`.
- **`/api/v1/metadata` returns a large payload.** Filter with the query
  parameters shown by `describe` rather than fetching everything.
- **Ingestion is multi-step:** create the job, upload batches, then close it.
  A job left open will not process.
- **Tenant host differs per org.** Never hardcode `c360a.salesforce.com`; read
  it from `DATA360_TENANT_URL`.

## Reference

- [Query and Profile API reference](./references/query-and-profile.md)
- [ENDPOINT-INDEX.md](../../../catalog/ENDPOINT-INDEX.md) — all 35 endpoints
