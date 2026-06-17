# `appEngineRegistrySchemaManifestClient`

App manifest schema and default CSP. Import:

```ts
import { appEngineRegistrySchemaManifestClient } from "@dynatrace-sdk/client-app-engine-registry";
```

| Method | Returns | Purpose |
|---|---|---|
| `getAppManifestSchema()` | `any` (JSON schema) | Get the JSON schema for app manifests. |
| `getDefaultCspProperties()` | `AppDefaultCsp` | Get the default Content-Security-Policy rules for apps. |

## Example

```ts
import { appEngineRegistrySchemaManifestClient } from "@dynatrace-sdk/client-app-engine-registry";

const schema = await appEngineRegistrySchemaManifestClient.getAppManifestSchema();
```
