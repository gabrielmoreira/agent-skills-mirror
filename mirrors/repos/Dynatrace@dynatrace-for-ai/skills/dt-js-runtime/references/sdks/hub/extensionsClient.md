# `extensionsClient`

Browse Hub extensions. All methods require scope `hub:catalog:read`. Import:

```ts
import { extensionsClient } from "@dynatrace-sdk/client-hub";
```

| Method | Returns | Purpose |
|---|---|---|
| `getExtensionOverviewList()` | `OverviewsList` | List overview info of all extensions. |
| `getExtensionDetails({ id })` | `Detail` | Detailed information about one extension. |
| `getExtensionReleases({ id })` | `ReleasesList` | List releases published for an extension (including revoked releases). |

## Example

```ts
import { extensionsClient } from "@dynatrace-sdk/client-hub";

const detail = await extensionsClient.getExtensionDetails({ id: "..." });
```
