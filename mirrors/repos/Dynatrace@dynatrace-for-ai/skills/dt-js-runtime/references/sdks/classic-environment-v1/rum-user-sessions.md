# `rumUserSessionsClient`

Query user-session data with USQL (User Session Query Language). Import:

```ts
import { rumUserSessionsClient } from "@dynatrace-sdk/client-classic-environment-v1";
```

| Method | Purpose |
|---|---|
| `getUsqlResultAsTable` | Run a USQL query and return results as a table. |
| `getUsqlResultAsTree` | Run a USQL query and return results as a tree. |

For new code, prefer DQL via [client-query](../query/README.md) over USQL.
