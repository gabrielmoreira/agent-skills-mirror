# State (`@dynatrace-sdk/client-state`)

> Env: ✅ Server runtime
> Status: current

Key-value storage for small chunks of app state. **App states** are readable by all app users; **user app states** are scoped to the authenticated user.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `stateClient` | `setAppState`, `getAppState`, `deleteAppState`, `getAppStates`, `deleteAppStates` | App-wide state |
| `stateClient` | `setUserAppState`, `getUserAppState`, `deleteUserAppState`, `getUserAppStates`, `deleteUserAppStates` | Per-user state |

Full method/type detail: [stateClient.md](stateClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Concepts

- **App state** — cross-user, scoped to the app. Any user of the app can read it. Scopes `state:app-states:*`.
- **User app state** — scoped to the app **and** the calling (authenticated) user. Scopes `state:user-app-states:*`.
- Use user-app-state for per-user values; use app-state only when the value is meant to be shared across all users.
- **Limits** — size/count limits apply; see [State service limits](https://dt-url.net/platform-services-state-service/).

## Required scopes

- `state:app-states:read` / `state:app-states:write` (and the `user-app-states` equivalents).

## Example

```ts
import { stateClient } from "@dynatrace-sdk/client-state";

await stateClient.setAppState({ key: "lastRun", body: { value: new Date().toISOString() } });
const state = await stateClient.getAppState({ key: "lastRun" });
```

## Notes

- Optional TTL via `validUntilTime` (range: now+1m … now+90d).
- Records `lastModifiedBy` / `lastModifiedTime`.
- Size limits apply; exceeding them throws a descriptive error.
- List filters support `=`, `!=`, `contains`, `starts-with`, `ends-with`.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-state/
