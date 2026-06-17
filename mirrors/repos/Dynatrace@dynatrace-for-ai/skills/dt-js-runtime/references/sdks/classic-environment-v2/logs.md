# `logsClient`

Classic log records API (prefer DQL via [client-query](../query/README.md) for new code). Import:

```ts
import { logsClient } from "@dynatrace-sdk/client-classic-environment-v2";
```

| Method | Purpose |
|---|---|
| `getLogRecords` | Query log records. |
| `exportLogRecords` | Export log records. |
| `getLogHistogramData` | Get log histogram (aggregated counts). |
| `storeLog` | Ingest/store custom log lines. |
