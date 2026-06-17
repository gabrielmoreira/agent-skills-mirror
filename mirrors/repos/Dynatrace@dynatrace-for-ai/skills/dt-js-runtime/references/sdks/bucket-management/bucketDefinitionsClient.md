# `bucketDefinitionsClient`

Manage Grail bucket definitions. Import:

```ts
import { bucketDefinitionsClient } from "@dynatrace-sdk/client-bucket-management";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createBucket` | `Bucket` | `storage:bucket-definitions:write` | Create a bucket definition (`bucketName`, `table`, `displayName`, `retentionDays`, …). |
| `getDefinition` | `Bucket` | `storage:bucket-definitions:read` | Get one bucket by `bucketName`. Optional `add-fields`: `records`, `estimatedUncompressedBytes`, `…QueryIncluded`, `…OnDemand` (slower). |
| `getDefinitions` | `Buckets` | `storage:bucket-definitions:read` | Get all bucket definitions (same `add-fields` options). |
| `updateBucket` | — | `storage:bucket-definitions:write` | Full update of `displayName` (≤ 200 chars) / `retentionDays`; requires `optimistic-locking-version` matching body `version`. |
| `updateBucketPartially` | — | `storage:bucket-definitions:write` | Partial update of `displayName` / `retentionDays`; requires `optimistic-locking-version`. |
| `truncateBucket` | — | `storage:bucket-definitions:write` | ⚠️ Irreversibly remove the bucket's records. |
| `deleteBucket` | — | `storage:bucket-definitions:delete` | ⚠️ Irreversibly delete the bucket definition. |

## Example

```ts
import { bucketDefinitionsClient } from "@dynatrace-sdk/client-bucket-management";

await bucketDefinitionsClient.updateBucketPartially({
  bucketName: "custom_logs",
  optimisticLockingVersion: 10,
  body: { displayName: "Custom logs (updated)", retentionDays: 10 },
});
```
