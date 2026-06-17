# Settings clients

Settings objects, schemas, and management zones. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `settingsObjectsClient`

| Method | Purpose |
|---|---|
| `postSettingsObjects` | Create settings object(s). |
| `getSettingsObjects` | List settings objects (filter by `schemaIds`, `fields`, `pageSize`; **paginated — see gotcha**). |
| `getSettingsObjectByObjectId` | Get one object by `objectId`. |
| `putSettingsObjectByObjectId` | Update an object by `objectId`. |
| `deleteSettingsObjectByObjectId` | Delete an object by `objectId`. |
| `getSettingsHistory` | Get change history of settings objects. |
| `getEffectiveSettingsValues` | Effective values for a schema (defaults if none persisted). |
| `getPermissions` / `getPermission` / `getPermissionAllUsers` | Read object permissions. |
| `addPermission` / `updatePermission` / `removePermission` | Manage accessor permissions. |
| `updatePermissionAllUsers` / `removePermissionAllUsers` | Manage all-users permission. |
| `resolveEffectivePermissions` | Resolve effective permissions for an identity. |
| `transferOwnership` | Transfer object ownership. |

Common scopes: `settings:objects:read` / `settings:objects:write`, plus `settings:objects:admin` for some permission ops.

### Pagination gotcha

```ts
const items = [];
let nextPageKey;
do {
  const page = await settingsObjectsClient.getSettingsObjects(
    nextPageKey
      ? { nextPageKey }                                              // sole param!
      : { schemaIds: "builtin:my-schema", fields: "scope,value", pageSize: 500 }
  );
  items.push(...(page.items ?? []));
  nextPageKey = page.nextPageKey;
} while (nextPageKey);
```

Passing `nextPageKey` alongside `schemaIds`/`fields`/`pageSize` on page 2 returns `400: Constraints violated`.

## `settingsSchemasClient`

| Method | Purpose |
|---|---|
| `getAvailableSchemaDefinitions` | List available settings schema definitions. |
| `getSchemaDefinition` | Get a specific schema definition. |

## `settingsManagementZonesClient`

| Method | Purpose |
|---|---|
| `getManagementZoneDetails` | Get details of a management zone. |
