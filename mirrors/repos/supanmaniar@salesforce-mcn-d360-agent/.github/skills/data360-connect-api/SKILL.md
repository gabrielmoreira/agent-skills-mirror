---
name: data360-connect-api
description: 'Call Salesforce Data 360 Connect APIs (data streams, segments, activations, identity resolutions, connections, data spaces, data kits, calculated insights, machine learning, clean rooms, data governance, data model objects, data lake objects) from the Salesforce CLI without an MCP server. Use when managing Data 360 data streams, building or activating segments, configuring identity resolution, enumerating data model objects (DMOs) or data lake objects (DLOs), or working with any /ssot endpoint.'
---

# Data 360 Connect API

Replaces the MCP server's `mcnext_*` catalog tools for the `data360-connect`
family — the largest family, with **383 endpoints across 35 resource groups**.

## When to Use

- Managing data streams, connections, and connectors
- Creating, updating, or activating segments
- Configuring identity resolution rulesets and match rules
- Working with data spaces, data kits, and data governance
- Calculated insights, machine learning, notebook AI, clean rooms
- Any endpoint whose path begins `/ssot/`

## Routing

`data360-connect` endpoints are served from the **org instance** under
`/services/data/vXX/ssot/...`:

```
{instanceUrl}/services/data/v66.0/ssot/segments
```

Use [sf-api.sh](../../../scripts/sf-api.sh) in its default (instance) mode. Do
**not** pass `--tenant` — that is only for the `data360` family.

## Procedure

1. **Discover the endpoint.** With 383 endpoints, always filter:

   ```bash
   node scripts/catalog-search.mjs list --family data360-connect --group Segments
   node scripts/catalog-search.mjs list --family data360-connect --search "activation"
   node scripts/catalog-search.mjs list --family data360-connect --kind create
   ```

2. **Inspect parameters and body shape:**

   ```bash
   node scripts/catalog-search.mjs describe segments.create-segment
   ```

3. **Call it:**

   ```bash
   ./scripts/sf-api.sh --path /ssot/segments --query 'batchSize=20'
   ```

4. **For writes**, pass a JSON body matching the described schema:

   ```bash
   ./scripts/sf-api.sh --method POST --path /ssot/segments \
     --body @payload.json
   ```

## Resource Groups

The 35 groups, by endpoint count, with the write surface each exposes. Generated
from the catalog — run `node scripts/catalog-search.mjs groups` for the live list.

| Group | Endpoints | Write | Group | Endpoints | Write |
| --- | ---: | --- | --- | ---: | --- |
| Data Governance | 59 | ✅ | Activation Platforms | 13 | ✅ |
| Machine Learning | 37 | ✅ | Data Shares | 11 | ✅ |
| Notebook AI | 35 | ✅ | Data Kits | 10 | ✅ |
| Connections | 23 | ✅ | Document AI | 10 | ✅ |
| Activations | 21 | ✅ | Segments | 10 | ✅ |
| Clean Rooms | 19 | ✅ | Data Graphs | 8 | ✅ |
| Activation Targets | 16 | ✅ | Data Spaces | 8 | ✅ |
| Data Model Objects | 14 | ✅ | Metadata | 8 | read-only |
| Data Transforms | 14 | ✅ | Calculated Insights | 6 | ✅ |
| Activation External Platforms | 2 | read-only | Data Streams | 6 | ✅ |
| Agent Configuration | 4 | ✅ | Identity Resolutions | 6 | ✅ |
| Private Network Routes | 4 | ✅ | Profile | 6 | read-only |
| Query (Current) | 4 | ✅ | Search Index | 6 | ✅ |
| Insights | 3 | read-only | Data Action Targets | 5 | ✅ |
| Query V1 & V2 | 3 | create only | Data Lake Objects | 5 | ✅ |
|  |  |  | Connectors | 2 | read-only |
| Data Actions | 2 | create only | Auth | 1 | read-only |
| Universal ID Lookup | 1 | read-only | Limits | 1 | read-only |

Read-only groups expose no `POST`/`PATCH`/`PUT`/`DELETE` at all. "create only"
means `POST` exists but no update or delete.

### Measured reachability

Not every catalogued endpoint is reachable in every org. Probing one read per
group against a live org returned **27 of 35 reachable**, with these exceptions:

| Group | Read result | Cause |
| --- | --- | --- |
| Data Governance | `NOT_FOUND` on all 8 paramless GETs | Feature not enabled in this org |
| Activation Platforms | `NOT_FOUND` on every path and method | Feature not enabled; use `/ssot/activation-external-platforms` |
| Data Kits | `INTERNAL_SERVER_ERROR` | Server-side null dereference — a Salesforce bug, not an auth issue |

Provisioning state varies by org, so treat a `NOT_FOUND` as "not enabled here"
rather than "wrong path". Verify the feature exists before assuming a typo.

### Query — this is how you read Data 360 records

The two query groups are the data-access path, and both work:

| Group | Endpoint | Style |
| --- | --- | --- |
| Query (Current) | `POST /ssot/query-sql` | Rows as positional arrays |
| Query V1 & V2 | `POST /ssot/query` | Rows as named objects |

```bash
./scripts/sf-api.sh --method POST --path /ssot/query \
  --body '{"sql":"SELECT ssot__Id__c FROM ssot__Individual__dlm LIMIT 2"}'
```

Both execute real SQL and return rows. `query-sql` returns `data` as arrays with
a parallel `metadata` array; `/ssot/query` returns objects keyed by field name.

**CRUD applies here exactly as it does at the sObject layer: read only.** The
`POST` is an RPC-style body for submitting SQL, not a create. SQL is limited to
`SELECT` — there is no DML through these endpoints, matching the record-level
read-only behaviour of DMOs and DLOs. Writes go through the Ingestion API.

## Common Operations

| Operation | Method | Path |
| --- | --- | --- |
| List segments | GET | `/ssot/segments` |
| Create segment | POST | `/ssot/segments` |
| Get segment | GET | `/ssot/segments/:segmentApiNameOrId` |
| Update segment | PATCH | `/ssot/segments/:segmentApiName` |
| Delete segment | DELETE | `/ssot/segments/:segmentApiName` |
| List data streams | GET | `/ssot/data-streams` |
| List data spaces | GET | `/ssot/data-spaces` |
| List identity resolutions | GET | `/ssot/identity-resolutions` |
| List activations | GET | `/ssot/activations` |
| List connections | GET | `/ssot/connections` |
| List data model objects | GET | `/ssot/data-model-objects` |
| Get one data model object | GET | `/ssot/data-model-objects/:dataModelObjectName` |
| List object mappings | GET | `/ssot/data-model-object-mappings` |
| List data lake objects | GET | `/ssot/data-lake-objects` |

### Enumerating data model objects

`GET /ssot/data-model-objects` is **the only way to enumerate the full data
model**. Every sObject-based method misses most of it:

```bash
# The full model, with fields, categories and data spaces
./scripts/sf-api.sh --path /ssot/data-model-objects --query 'limit=500&offset=0'
```

This response is large — each DMO carries all of its fields. Page it and extract
names rather than printing the payload:

```bash
off=0
while : ; do
  ./scripts/sf-api.sh --path /ssot/data-model-objects \
    --query "limit=500&offset=$off" --raw > /tmp/page.json
  n=$(python3 -c "import json;print(len(json.load(open('/tmp/page.json')).get('dataModelObject') or []))")
  [ "$n" -le 0 ] && break
  python3 -c "
import json
for o in json.load(open('/tmp/page.json')).get('dataModelObject') or []:
    print(o['name'])"
  [ "$n" -lt 500 ] && break
  off=$((off+500))
done | sort -u
```

**Defined is not the same as materialised.** A DMO can exist in the data model
without being queryable:

| | Meaning | How to enumerate |
| --- | --- | --- |
| **Defined** | Exists in the data model. Every DMO. | `GET /ssot/data-model-objects` |
| **Materialised** | Has storage in a data space, so SOQL works on it. | `sf sobject list` (suffix `__dlm`) |

Materialised objects are always a **small subset** of defined ones — expect the
count from `/ssot/data-model-objects` to be far larger than the `__dlm` count in
`sf sobject list`.

Querying a defined-but-unmaterialised DMO fails outright rather than returning
zero rows:

```text
UNSUPPORTED_QUERY
The object ssot__AgentWork__dlm can't be queried.
Verify that ssot__AgentWork__dlm exists and has been mapped.
```

"Has been mapped" is the operative phrase: the object needs an object mapping
(`/ssot/data-model-object-mappings`) before it can hold or return data.

**The listing response has no total.** `/ssot/data-model-objects` returns
`{"dataModelObject": [...]}` with no `totalSize` and no `nextPageUrl`, so the
count is only obtainable by paging to exhaustion. Its sibling
`/ssot/data-lake-objects` *does* return `totalSize` — do not assume consistency.

Measurements from a real org, to give a sense of the gap: **1,067** DMOs defined
against **45** materialised and queryable.

### Data lake objects

DLOs use the suffix `__dll` and are enumerated by `GET /ssot/data-lake-objects`,
which returns `totalSize` (60 in the org measured). They are **queryable but
invisible to sObject enumeration**: `SELECT Id FROM Account_Home__dll` works and
`sf sobject describe -s Account_Home__dll` returns 119 fields, yet the object
appears in neither `sf sobject list` nor `EntityDefinition`. Never conclude a
DLO does not exist because a listing omits it.

`SELECT COUNT()` is **not supported on DLOs**:

```text
UNSUPPORTED_QUERY: SELECT COUNT() is not supported by Account_Home__dll.
```

Use `SELECT Id ... LIMIT n` and page, or read `totalSize` from the listing
endpoint. `SELECT COUNT()` on a DMO works normally.

## Gotchas

- **Some creates have no matching delete.** The catalog exposes collection-level
  `POST` endpoints with no `DELETE` on the same resource, so a created object may
  not be removable through this API. Confirmed by catalog inspection, **not**
  executed — treat as a caution to check before relying on reversal:

  | Create | Delete route |
  | --- | --- |
  | `POST /ssot/data-actions` | none |
  | `POST /ssot/machine-learning/alerts` | none (`PATCH` only) |
  | `POST /ssot/data-clean-room/collaborations` | none |
  | `POST /ssot/data-clean-room/providers` | none |
  | `POST /ssot/knowledge-space/library` | none (`.../library/remove-library` exists, but it is a distinct action, not a resource delete) |

  Contrast with resources that *are* reversible: `/ssot/data-kits/:name`,
  `/ssot/connections/:id`, `/ssot/knowledge-space/:name` and
  `/ssot/data-share/:nameOrId` all have `DELETE` routes. Note `data-share` is
  reversible even though the collection is `/ssot/data-share` while the list is
  `/ssot/data-shares` — do not infer reversibility from naming alone.

  The `destructive` flag does not cover this: a create is flagged
  `destructive: false` because the verb destroys nothing, which says nothing about
  whether the result can be removed. Check for a matching `DELETE` before creating
  anything you may need to undo.
- **Segment SQL is validated on write.** `POST`/`PATCH /ssot/segments` reject
  invalid SQL with a descriptive error — read it before retrying.
- **Deletes are destructive.** `DELETE /ssot/segments/:segmentApiName` removes
  the segment permanently. Confirm with the user first.
- **Pagination parameter names are not consistent across this family.**
  `/ssot/segments` takes `batchSize` + `offset`; `/ssot/data-model-objects`
  takes `limit` + `offset`. Check the endpoint in the catalog before assuming:

  ```bash
  node scripts/catalog-search.mjs describe segments.get-segments
  ```

- **An unknown query parameter is silently ignored.** The API applies its own
  default instead of erroring, so a mistyped parameter yields a plausible but
  wrong result. `/ssot/data-model-objects` defaults to `limit=50`, which makes a
  large model look small. `sf-api.sh` warns when a parameter is not declared:

  ```bash
  ./scripts/sf-api.sh --path /ssot/data-model-objects --query 'batchSize=200'
  # sf-api: warning: unrecognised query parameter(s) for GET /ssot/data-model-objects:
  # sf-api:          batchSize
  # sf-api:          declared parameters: limit, offset, orderBy
  ```

  Never report a count that could have been truncated by an unnoticed default.

- **DMOs and DLOs are absent from `EntityDefinition` and from most sObject
  tooling.** Use `/ssot/data-model-objects` for definitions, `sf sobject list`
  for one subset of materialised objects, and `/ssot/data-lake-objects` for
  DLOs. No single surface is a superset of the others.
- **Data 360 records are read-only over REST and SOQL.** All 45 materialised DMOs
  report `createable=false, updateable=false, deletable=false, queryable=true` —
  unanimously, with no exceptions. Attempts are rejected server-side:

  ```text
  POST   /sobjects/ssot__Individual__dlm       -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  PATCH  /sobjects/ssot__Individual__dlm/{Id}  -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  DELETE /sobjects/ssot__Individual__dlm/{Id}  -> CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY
  ```

  **This is a property of the object, not of your permissions.** An admin sees the
  same flags, so do not retry with elevated access.

  Do not over-generalise this into "Data 360 objects reject DML". It applies to
  the **data** objects — DMOs (`__dlm`) and DLOs (`__dll`). Data 360 *configuration*
  objects are ordinary sObjects and accept DML normally; `DataStream` is
  `createable/updateable/deletable = true`.

  **Write capability exists at the definition layer, not the record layer.** You
  can create/update/delete DMO and DLO *definitions* and mappings via the `/ssot`
  endpoints above, but you cannot write the *records* they hold. Data enters via
  the Ingestion API on the tenant host (`data360` family,
  [data360-api](../data360-api/SKILL.md)) — not via sObject DML.

  If a user asks to insert or update Data 360 records, the answer is "not this
  way"; route them to the Ingestion API rather than attempting DML.
- **`SELECT COUNT()` is unsupported on DLOs** (`__dll`), though it works on DMOs.
  Page with `SELECT Id ... LIMIT n` or read `totalSize` from the listing
  endpoint.
- **`/ssot/data-model-objects` returns no `totalSize`.** Page until a short page
  comes back; do not assume a single call gives you everything, and do not
  assume the default page size matches other endpoints.
- **A catalog `required=false` does not mean the API accepts the call without it.**
  `/ssot/connections` declares `connectorType` as optional, but omitting it fails:

  ```text
  GET /ssot/connections
  -> ILLEGAL_QUERY_PARAMETER_VALUE: ConnectorType must be provided
  ```

  `connectorType` is case-sensitive, and the value must be one the org supports —
  an unknown connector type is rejected rather than returning an empty list:

  ```text
  GET /ssot/connections?connectorType=Gcs
  -> ILLEGAL_QUERY_PARAMETER_VALUE: ConnectorType [Gcs] is not supported
  ```

  The catalog is generated from Salesforce's Postman collections, which do not
  always encode endpoint-level requirements. Treat its `required` flags as a
  starting point, and read the error when a call fails — these messages name the
  missing parameter, so they are worth more than the metadata.
- **`orderByExpression` uses bracket syntax**, e.g. `[Name asc]`.
- **Some operations are asynchronous** (segment publish, data transforms,
  ML predictions). See [async-jobs-and-cache](../async-jobs-and-cache/SKILL.md).

## Reference

- [Segments and activations reference](./references/segments-and-activations.md)
- [ENDPOINT-INDEX.md](../../../catalog/ENDPOINT-INDEX.md) — all 383 endpoints
