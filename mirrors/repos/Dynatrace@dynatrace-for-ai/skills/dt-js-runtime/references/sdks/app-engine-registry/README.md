# AppEngine Registry (`@dynatrace-sdk/client-app-engine-registry`)

> Env: ✅ Server runtime
> Status: current

Manage Dynatrace AppEngine apps — install, update, uninstall, and discover apps and their actions.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `appEngineRegistryAppsClient` | `getApp`, `getApps`, `installApp`, `uninstallApp`, `searchActions` | App lifecycle & discovery |
| `appEngineRegistrySchemaManifestClient` | `getAppManifestSchema`, `getDefaultCspProperties` | Manifest schema & default CSP rules |

Full method/type detail: [appEngineRegistryAppsClient.md](appEngineRegistryAppsClient.md), [appEngineRegistrySchemaManifestClient.md](appEngineRegistrySchemaManifestClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `app-engine:apps:run`, `app-engine:apps:install`, `app-engine:apps:delete` (per operation).

## Example

```ts
import { appEngineRegistryAppsClient } from "@dynatrace-sdk/client-app-engine-registry";

const app = await appEngineRegistryAppsClient.getApp({ id: "my.app" });
const apps = await appEngineRegistryAppsClient.getApps();
```

## Notes

- App IDs follow namespace convention (`dynatrace.*`, `my.*`).
- Install/uninstall are asynchronous; resources carry a `status` / `PendingOperation` / `DeploymentStatus` reflecting in-progress operations.
- Filtering supports up to 3 nesting levels / 256-char limits.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-app-engine-registry/
