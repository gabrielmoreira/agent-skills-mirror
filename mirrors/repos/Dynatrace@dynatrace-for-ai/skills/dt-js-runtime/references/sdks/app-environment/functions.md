# App Environment — Functions

Import individually from `@dynatrace-sdk/app-environment`.

| Function | Returns | Purpose | Fallback if runtime missing |
|---|---|---|---|
| `getAppId()` | `string` | App id from app config | `dt.missing.app.id` |
| `getAppName()` | `string` | App name from app config | `dt.missing.app.name` |
| `getAppVersion()` | `string` | App version from app manifest | `dt.missing.app.version` |
| `getCurrentUserDetails()` | `UserDetails` | `id`, `name`, `email` of the logged-in user | placeholder `UserDetails` (`dt.missing.user.*`) |
| `getEnvironmentId()` | `string` | Environment id the app runs on | `dt.missing.environment.id` |
| `getEnvironmentUrl()` | `string` | Environment URL the app runs on | `https://dynatrace.com/` |

## Example

```ts
import { getAppId, getCurrentUserDetails } from "@dynatrace-sdk/app-environment";

const appId = getAppId();
const { id, name, email } = getCurrentUserDetails();
```
