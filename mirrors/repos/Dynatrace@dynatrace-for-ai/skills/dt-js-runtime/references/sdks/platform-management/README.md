# Platform Management (`@dynatrace-sdk/client-platform-management-service`)

> Env: ✅ Server runtime
> Status: current

Basic read-only information about the currently logged-in environment, plus IAM permission resolution.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `effectivePermissionsClient` | `resolveEffectivePermissions` | Check whether the caller has requested permissions |
| `environmentInformationClient` | `getEnvironmentInformation` | Environment state, ID, creation time |
| `environmentSettingsClient` | `getEnvironmentSettings` | Environment config settings |
| `licenseInformationClient` | `getLicense`, `getLicenseSettings` | License & subscription details |

Full method/type detail: [environmentInformationClient.md](environmentInformationClient.md), [environmentSettingsClient.md](environmentSettingsClient.md), [licenseInformationClient.md](licenseInformationClient.md), [effectivePermissionsClient.md](effectivePermissionsClient.md) · [types.md](types.md).

## Required scopes

- One of `app-engine:apps:run` or `app-engine:functions:run`.

## Example

```ts
import { effectivePermissionsClient } from "@dynatrace-sdk/client-platform-management-service";

const data = await effectivePermissionsClient.resolveEffectivePermissions({
  body: { permissions: [{ permission: "state:app-states:write" }] },
});
```

## Notes

- Apps must declare all permissions they check.
- Settings permission requests always return conditional grants.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-platform-management-service/
