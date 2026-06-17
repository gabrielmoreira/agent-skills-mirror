# `appsClient`

Browse Hub apps. All methods require scope `hub:catalog:read`. Import:

```ts
import { appsClient } from "@dynatrace-sdk/client-hub";
```

| Method | Returns | Purpose |
|---|---|---|
| `getAppOverviewList()` | `OverviewsList` | List overview info of all apps (optional flag to include extra fields). |
| `getAppDetails({ id })` | `Detail` | Detailed information about one app. |
| `getAppReleases({ id })` | `ReleasesList` | List releases published for an app (including revoked releases). |

## Example

```ts
import { appsClient } from "@dynatrace-sdk/client-hub";

const apps = await appsClient.getAppOverviewList();
const detail = await appsClient.getAppDetails({ id: "..." });
```
