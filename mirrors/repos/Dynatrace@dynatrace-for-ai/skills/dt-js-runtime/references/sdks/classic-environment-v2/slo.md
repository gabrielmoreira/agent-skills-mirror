# `serviceLevelObjectivesClient`

Manage Service-Level Objectives (SLOs). Import:

```ts
import { serviceLevelObjectivesClient } from "@dynatrace-sdk/client-classic-environment-v2";
```

| Method | Purpose |
|---|---|
| `getSlo` | Query SLOs (filterable, paginated; optional evaluation). |
| `getSloById` | Get one SLO by id. |
| `createSlo` | Create an SLO. |
| `updateSloById` | Update an SLO. |
| `deleteSlo` | Delete an SLO. |
| `createAlert` | Create a burn-rate/status alert for an SLO. |
