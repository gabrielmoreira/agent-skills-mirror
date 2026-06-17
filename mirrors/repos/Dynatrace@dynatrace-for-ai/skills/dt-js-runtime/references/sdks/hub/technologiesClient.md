# `technologiesClient`

Browse Hub technologies. All methods require scope `hub:catalog:read`. Import:

```ts
import { technologiesClient } from "@dynatrace-sdk/client-hub";
```

| Method | Returns | Purpose |
|---|---|---|
| `getTechnologyOverviewList()` | `OverviewsList` | List overview info of all technologies. |
| `getTechnologyDetails({ id })` | `Detail` | Detailed information about one technology. |

## Example

```ts
import { technologiesClient } from "@dynatrace-sdk/client-hub";

const tech = await technologiesClient.getTechnologyDetails({ id: "..." });
```
