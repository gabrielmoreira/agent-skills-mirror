# App Environment (`@dynatrace-sdk/app-environment`)

> Env: ✅ Server runtime
> Status: current

Basic information about the app and the environment it runs in.

## Key exports

| Function | Returns |
|---|---|
| `getAppId()` | App identifier |
| `getAppName()` | App name |
| `getAppVersion()` | App version (from manifest) |
| `getCurrentUserDetails()` | `UserDetails` — `{ id, name, email }` |
| `getEnvironmentId()` | Environment identifier |
| `getEnvironmentUrl()` | Environment base URL |

Full detail: [functions.md](functions.md) (per-function signatures + examples) · [types.md](types.md) (`UserDetails`). All exports are synchronous functions — no clients, no scopes.

## Example

```ts
import { getAppId, getCurrentUserDetails } from "@dynatrace-sdk/app-environment";

const appId = getAppId();
const { id, name, email } = getCurrentUserDetails();
```

## Notes

- If the Dynatrace JS runtime is unavailable, functions return placeholder values prefixed `"dt.missing."` and log a console warning.

Canonical reference: https://developer.dynatrace.com/develop/sdks/app-environment/
