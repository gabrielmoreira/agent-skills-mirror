# `environmentInformationClient`

Import:

```ts
import { environmentInformationClient } from "@dynatrace-sdk/client-platform-management-service";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getEnvironmentInformation` | `EnvironmentInfo` | one of `app-engine:apps:run` / `app-engine:functions:run` | Basic info about the current environment (id, type, state, …). |

## Example

```ts
import { environmentInformationClient } from "@dynatrace-sdk/client-platform-management-service";

const info = await environmentInformationClient.getEnvironmentInformation();
```
