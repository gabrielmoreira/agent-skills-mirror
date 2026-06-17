# App Settings v2 (`@dynatrace-sdk/client-app-settings-v2`)

> Env: ✅ Server runtime
> Status: current (replaces [app-settings-v1](../app-settings-v1/README.md))

Retrieve, update, and manage app settings objects, including permissions and ownership.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `appSettingsObjectsClient` | `postAppSettingsObject`, `getAppSettingsObjectByObjectId`, `putAppSettingsObjectByObjectId`, `deleteAppSettingsObjectByObjectId`, `getAppSettingsObjects` | Settings object CRUD |
| `appSettingsObjectsClient` | `getEffectiveAppSettingsValues` | Values incl. schema defaults |
| `appSettingsObjectsClient` | `postAppSettingsPermissionByObjectId`, ownership transfer | Access control |

Full method/type detail: [appSettingsObjectsClient.md](appSettingsObjectsClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `app-settings:objects:read` / `app-settings:objects:write`.

## Example

```ts
import { appSettingsObjectsClient } from "@dynatrace-sdk/client-app-settings-v2";

const data = await appSettingsObjectsClient.postAppSettingsObject({
  body: { schemaId: "jira-connection", value: {} },
});
```

## Concepts

- **Effective values:** for `multiObject: false` schemas with no persisted object, the schema default is returned by `getEffectiveAppSettingsValues`.
- **Secrets:** secret properties are returned in plain text only when the call originates from your app's serverless function; otherwise irreversibly masked.
- **Optimistic locking:** mutations use version tokens.
- **Pagination:** when using `page-key` for subsequent pages, omit all other query params (same gotcha as classic settings — see [classic-environment-v2](../classic-environment-v2/README.md)). Max `pageSize` 500 (0 = all), default 100.
- **Permissions model:** per-object accessor permissions + an all-users permission; ownership transfer via `postAppSettingsOwnershipByObjectId` (owner or main admin only).

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-app-settings-v2/
