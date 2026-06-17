# `environmentSettingsClient`

Import:

```ts
import { environmentSettingsClient } from "@dynatrace-sdk/client-platform-management-service";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getEnvironmentSettings` | `SettingsResponse` | one of `app-engine:apps:run` / `app-engine:functions:run` | Basic environment settings of the current environment. |

## Example

```ts
import { environmentSettingsClient } from "@dynatrace-sdk/client-platform-management-service";

const settings = await environmentSettingsClient.getEnvironmentSettings();
```
