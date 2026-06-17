# `licenseInformationClient`

Import:

```ts
import { licenseInformationClient } from "@dynatrace-sdk/client-platform-management-service";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `getLicense` | `License` | one of `app-engine:apps:run` / `app-engine:functions:run` | Basic license information for the current environment. |
| `getLicenseSettings` | `LicenseSettingsResponse` | one of `app-engine:apps:run` / `app-engine:functions:run` | Basic license settings information. |

## Example

```ts
import { licenseInformationClient } from "@dynatrace-sdk/client-platform-management-service";

const license = await licenseInformationClient.getLicense();
```
