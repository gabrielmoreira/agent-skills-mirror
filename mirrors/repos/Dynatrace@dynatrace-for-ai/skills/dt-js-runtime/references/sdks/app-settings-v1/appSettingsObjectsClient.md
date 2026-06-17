# `appSettingsObjectsClient`

> **DEPRECATED** — migrate to [app-settings-v2](../app-settings-v2/README.md).

Import:

```ts
import { appSettingsObjectsClient } from "@dynatrace-sdk/client-app-settings";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `postAppSettingsObject` | object response | `app-settings:objects:write` | Create a settings object (`schemaId`, `value`). |
| `getAppSettingsObjects` | objects list | `app-settings:objects:read` | List settings objects. |
| `getAppSettingsObjectByObjectId` | object | `app-settings:objects:read` | Get one object by `objectId`. |
| `putAppSettingsObjectByObjectId` | update response | `app-settings:objects:write` | Update an object by `objectId`. |
| `deleteAppSettingsObjectByObjectId` | — | `app-settings:objects:write` | Delete an object by `objectId`. |
| `getEffectiveAppSettingsValues` | effective values | `app-settings:objects:read` | Effective values for schemas (schema default if none persisted). |
| `resolveEffectivePermissions` | effective permissions | `app-settings:objects:read` | Resolve effective permissions for an identity. |

## Example

```ts
import { appSettingsObjectsClient } from "@dynatrace-sdk/client-app-settings";

const data = await appSettingsObjectsClient.getEffectiveAppSettingsValues();
```
