# `queryExecutionClient`

Execute, poll, and cancel DQL queries against Grail. Import:

```ts
import { queryExecutionClient } from "@dynatrace-sdk/client-query";
```

| Method | Returns | Purpose |
|---|---|---|
| `queryExecute` | `QueryStartResponse` | Start a Grail query. If it finishes immediately the result is included; otherwise the response carries a `requestToken` for polling. Body is an `ExecuteRequest` (`query`, optional `maxResultRecords`, `requestTimeoutMilliseconds`, `timezone`, `locale`, `defaultScanLimitGbytes`, …). |
| `queryPoll` | `QueryPollResponse` | Poll a started query by `requestToken`; returns query `state` and, when finished, the result. |
| `queryCancel` | `QueryPollResponse` | Cancel a running query. Returns the result if it had already finished, otherwise discards it (no body). |

Permissions are per Grail bucket/table — see [README](README.md#required-scopes).

## Execute + poll loop

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

`QueryState` enum: `NOT_STARTED`, `RUNNING`, `SUCCEEDED`, `CANCELLED`, `FAILED` (see [types.md](types.md)).
