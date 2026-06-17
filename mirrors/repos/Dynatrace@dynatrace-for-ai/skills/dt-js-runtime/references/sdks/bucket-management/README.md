# Grail Bucket Management (`@dynatrace-sdk/client-bucket-management`)

> Env: ✅ Server runtime
> Status: current

Manage Grail storage buckets — creation, retention, truncation.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `bucketDefinitionsClient` | `createBucket`, `getDefinition`, `getDefinitions`, `updateBucket`, `updateBucketPartially`, `deleteBucket`, `truncateBucket` | Bucket lifecycle |

Full method/type detail: [bucketDefinitionsClient.md](bucketDefinitionsClient.md) (per-method returns, scopes, examples) · [types.md](types.md) (types + enums).

## Required scopes

- `storage:bucket-definitions:read` / `storage:bucket-definitions:write` / `storage:bucket-definitions:delete`.

## Example

```ts
import { bucketDefinitionsClient } from "@dynatrace-sdk/client-bucket-management";

const data = await bucketDefinitionsClient.createBucket({
  body: { bucketName: "custom_logs", table: "logs", displayName: "Custom logs", retentionDays: 35 },
});
```

## Notes

- Bucket name: 3–100 chars, starts with a letter, lowercase/numbers/`_`/`-` only; no `default_`/`dt_` prefix; immutable after creation.
- Retention 1–3657 days; shortening it triggers automatic data deletion.
- Mandatory optimistic locking (version) on updates.
- Creation can take up to 1 minute to appear; delete/truncate are irreversible async operations.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-bucket-management/
