# App Settings v1 (`@dynatrace-sdk/client-app-settings`)

> Env: ✅ Server runtime
> Status: ⚠ **DEPRECATED** — use [app-settings-v2](../app-settings-v2/README.md) instead

Retrieve, update, and manage app settings objects. This API version is deprecated; new code should use v2.

## Clients & key methods

`appSettingsObjectsClient` — `postAppSettingsObject`, `getAppSettingsObjectByObjectId`, `putAppSettingsObjectByObjectId`, `deleteAppSettingsObjectByObjectId`, `getAppSettingsObjects`, `getEffectiveAppSettingsValues`, `resolveEffectivePermissions`.

Full method/type detail: [appSettingsObjectsClient.md](appSettingsObjectsClient.md) · [types.md](types.md). V2 adds richer per-object permission and ownership management — migrate to it.

## Required scopes

- `app-settings:objects:read` / `app-settings:objects:write`.

## Notes

- Migrate to v2; the surface is largely the same.
- Secret properties appear unmasked in serverless functions, masked elsewhere.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-app-settings/
