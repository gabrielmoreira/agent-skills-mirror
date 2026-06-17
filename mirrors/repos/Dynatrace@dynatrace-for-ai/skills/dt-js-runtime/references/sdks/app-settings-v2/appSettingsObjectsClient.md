# `appSettingsObjectsClient`

Manage app settings objects, effective values, and permissions. Import:

```ts
import { appSettingsObjectsClient } from "@dynatrace-sdk/client-app-settings-v2";
```

## Objects & effective values

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `postAppSettingsObject` | `AppSettingsObjectResponse` | `app-settings:objects:write` | Create a settings object (`schemaId`, `value`). |
| `getAppSettingsObjects` | `AppSettingsObjectsList` | `app-settings:objects:read` | List objects; `schemaId`, `add-fields`, `page-key`/`pageSize` (max 500). |
| `getAppSettingsObjectByObjectId` | `AppSettingsObject` | `app-settings:objects:read` | Get one object by `objectId`. |
| `putAppSettingsObjectByObjectId` | `AppSettingsUpdateResponse` | `app-settings:objects:write` | Update an object by `objectId`. |
| `deleteAppSettingsObjectByObjectId` | — | `app-settings:objects:write` | Delete an object by `objectId`. |
| `getEffectiveAppSettingsValues` | `EffectiveAppSettingsValuesList` | `app-settings:objects:read` | Effective values for schemas (schema default if none persisted). Secrets plaintext only from your serverless function, else masked. |
| `postAppSettingsOwnershipByObjectId` | — | `app-settings:objects:write` | Transfer object ownership (owner or main admin only). |

## Permissions

| Method | Returns | Purpose |
|---|---|---|
| `getAppSettingsPermissionsByObjectId` | `AppSettingsPermissionsList` | List all accessor permissions on an object. |
| `getAppSettingsPermissionByObjectIdAndAccessorId` | `AppSettingsAccessorPermissions` | Get one accessor's permissions on an object. |
| `postAppSettingsPermissionByObjectId` | — | Add accessor permission on an object. |
| `putAppSettingsPermissionByObjectIdAndAccessorId` | — | Replace an accessor's permission. |
| `deleteAppSettingsPermissionByObjectIdAndAccessorId` | — | Remove an accessor's permission. |
| `getAppSettingsAllUsersPermissionByObjectId` | `AppSettingsAccessorPermissions` | Get the all-users permission on an object. |
| `putAppSettingsAllUsersPermissionByObjectId` | — | Set the all-users permission. |
| `deleteAppSettingsAllUsersPermissionByObjectId` | — | Remove the all-users permission. |
| `resolveEffectivePermissions` | `EffectivePermissions` | Resolve effective permissions for an identity. |

## Example

```ts
import { appSettingsObjectsClient } from "@dynatrace-sdk/client-app-settings-v2";

await appSettingsObjectsClient.postAppSettingsObject({
  body: { schemaId: "jira-connection", value: {} },
});
const effective = await appSettingsObjectsClient.getEffectiveAppSettingsValues();
```
