# `oneAgentOnAHostClient`

Query hosts by OneAgent characteristics and manage persisted potential problems. Import:

```ts
import { oneAgentOnAHostClient } from "@dynatrace-sdk/client-classic-environment-v1";
```

| Method | Purpose |
|---|---|
| `getHostsWithSpecificAgents` | List hosts filtered by agent version, OS, monitoring type, availability, update status, etc. |
| `getAgentPersistedPotentialProblems` | Get persisted potential agent problems. |
| `deleteAgentPersistedPotentialProblems` | Clear persisted potential agent problems. |
