# `stateClient`

Key-value app/user state CRUD. Import:

```ts
import { stateClient } from "@dynatrace-sdk/client-state";
```

## App state (cross-user)

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `setAppState` | — | `state:app-states:write` | Create/update cross-user app state for a key. Readable by all app users; supports `validUntilTime` TTL. |
| `getAppState` | `AppState` | `state:app-states:read` | Get one app state by key. |
| `getAppStates` | `AppStates` | `state:app-states:read` | List app states (key only by default; use `add-fields` and `filter`). |
| `deleteAppState` | — | `state:app-states:delete` | Delete one app state by key. |
| `deleteAppStates` | — | `state:app-states:delete` | Delete all app states (reset app to clean state). |

## User app state (per authenticated user)

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `setUserAppState` | — | `state:user-app-states:write` | Create/update app state for the calling user + key; supports `validUntilTime` TTL. |
| `getUserAppState` | `UserAppState` | `state:user-app-states:read` | Get one user app state by key. |
| `getUserAppStates` | `UserAppStates` | `state:user-app-states:read` | List the calling user's app states (filterable). |
| `deleteUserAppState` | — | `state:user-app-states:delete` | Delete one user app state by key. |
| `deleteUserAppStates` | — | `state:user-app-states:delete` | Delete all user app states for the calling user + app. |

## `getAppStates` / `getUserAppStates` filter

- **Filterable fields & operators:** `key` (`=`,`!=`,`contains`,`starts-with`,`ends-with`), `modificationInfo.lastModifiedBy` (same), `modificationInfo.lastModifiedTime` (`=`,`!=`,`<`,`<=`,`>`,`>=`), `validUntilTime` (same comparison ops).
- `contains`/`starts-with`/`ends-with` are case-insensitive; `=`/`!=` case-sensitive. Connect with `and`/`or`, negate with `not`. Strings in single quotes (escape `\'`). Max nesting 2, max length 256 chars.
- Example: `modificationInfo.lastModifiedTime >= '2022-07-01T00:10:05.000Z' and not (key contains 'new')`.

## Example

```ts
import { stateClient } from "@dynatrace-sdk/client-state";

await stateClient.setUserAppState({
  key: "some-key",
  body: { value: "some-state", validUntilTime: "now+2d" },
});
```
