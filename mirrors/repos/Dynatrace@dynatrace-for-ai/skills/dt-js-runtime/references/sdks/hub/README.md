# Hub (`@dynatrace-sdk/client-hub`)

> Env: ✅ Server runtime
> Status: current

Read the Dynatrace Hub catalog — apps, extensions, and technologies for the environment.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `appsClient` | `getAppDetails`, `getAppOverviewList`, `getAppReleases` | Apps |
| `extensionsClient` | `getExtensionDetails`, `getExtensionOverviewList`, `getExtensionReleases` | Extensions |
| `technologiesClient` | `getTechnologyDetails`, `getTechnologyOverviewList` | Technologies |
| `categoriesClient` | category access | Hub categories |

Full method/type detail: [appsClient.md](appsClient.md), [extensionsClient.md](extensionsClient.md), [technologiesClient.md](technologiesClient.md), [categoriesClient.md](categoriesClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `hub:catalog:read`.

## Example

```ts
import { appsClient } from "@dynatrace-sdk/client-hub";

const data = await appsClient.getAppDetails({ id: "..." });
```

## Notes

- Supports filtering to exclude incompatible instances.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-hub/
