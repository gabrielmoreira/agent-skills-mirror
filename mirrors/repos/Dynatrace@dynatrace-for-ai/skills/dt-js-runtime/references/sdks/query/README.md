# DQL Query (`@dynatrace-sdk/client-query`)

> Env: ✅ Server runtime
> Status: current

Query records stored in Grail using Dynatrace Query Language (DQL).

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `queryExecutionClient` | `queryExecute`, `queryPoll`, `queryCancel` | Run, poll, and cancel DQL queries |
| `queryAssistanceClient` | `queryAutocomplete`, `queryParse`, `queryVerify` | Dev-time autocomplete, parse tree, validation (no execution) |

Full method/type detail: [queryExecutionClient.md](queryExecutionClient.md), [queryAssistanceClient.md](queryAssistanceClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Result format (records + types + metadata)

`queryExecute`/`queryPoll`/`queryCancel` results have three sections:

- **`records`** — each record is a set of fields and values; its implicit `index` is its position in the array.
- **`types`** — a list of type **buckets**, each with an `indexRange` `[startIndex, endIndex)`. A record at index `i` finds its field types in the bucket where `startIndex <= i < endIndex`, then in that bucket's `mappings`.
- **`metadata`** — query info like `analysisTimeframe`, `timezone`, `locale`.

**Type collisions:** because Grail has no ingestion-time schema, two records can share a field name with different value types. On collision a new type bucket with a different index range is created. **Always consult the `types` section when consuming records** — every field is guaranteed a corresponding type.

## Required scopes

- `storage:*:read` for the buckets/tables the query touches (e.g. `storage:logs:read`, `storage:events:read`). Query permissions are per bucket/table in Grail — see [Bucket and table permissions in Grail](https://docs.dynatrace.com/docs/shortlink/assign-bucket-table-permissions).

## Example — execute + poll

DQL queries are asynchronous: `queryExecute` returns a `requestToken`, then poll until done.

```ts
import { queryExecutionClient } from "@dynatrace-sdk/client-query";

const { requestToken } = await queryExecutionClient.queryExecute({
  body: { query: "fetch logs | limit 100", maxResultRecords: 100 },
});
let r;
do { r = await queryExecutionClient.queryPoll({ requestToken }); }
while (r.state === "NOT_STARTED" || r.state === "RUNNING");
if (r.state !== "SUCCEEDED") throw new Error(r.state);
const records = r.result.records;
```

## Notes

- Don't author DQL blind — load the relevant DQL/domain skill (e.g. `dt-dql-essentials`) for the query itself.
- Optional `dt-client-context` header tags the query for cost/usage monitoring.
- Results include type mappings and handle field type collisions.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-query/
