# `documentLockingClient`

Optional active locking to prevent concurrent-update conflicts. Import:

```ts
import { documentLockingClient } from "@dynatrace-sdk/client-document";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `acquireLock` | `AcquireLockResult` | `document:documents:write` | Lock a document so other users can't update it. Max **5 locked docs per user**; duration max **15 min** (default 10); re-acquiring by the lock owner extends it. |
| `inspectLock` | `DocumentLockDetails` | `document:documents:read` | Check whether a document is locked and who owns the lock. |
| `releaseLock` | — | `document:documents:write` | Release the lock; only the lock owner may do this. |

## Example

```ts
import { documentLockingClient } from "@dynatrace-sdk/client-document";

const data = await documentLockingClient.acquireLock({
  id: "...",
  body: { documentVersion: 10 },
});
```
