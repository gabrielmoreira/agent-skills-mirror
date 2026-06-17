# `environmentSharesClient`

Environment-shares grant claimable read/read-write access to same-environment users. Import:

```ts
import { environmentSharesClient } from "@dynatrace-sdk/client-document";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createEnvironmentShare` | `EnvironmentShare` | `document:environment-shares:write` | Create a share (read or read-write) for a document you own/can reshare. Max one per access type; creating it doesn't grant access until users claim it. |
| `claimEnvironmentShare` | `EnvironmentShareClaimResult` | `document:environment-shares:claim` | Claim another user's share to gain its access. Can't claim your own; can't self-revoke once claimed; claiming twice is a no-op. |
| `getEnvironmentShare` | `EnvironmentShare` | `document:environment-shares:read` | Retrieve a share by id. |
| `getEnvironmentShareClaimers` | `EnvironmentShareClaimerList` | `document:environment-shares:read` | List users who claimed a share; paginated. |
| `listEnvironmentShares` | `EnvironmentShareList` | `document:environment-shares:read` | List accessible env-shares; `filter` by `documentId`; paginated. |
| `deleteEnvironmentShare` | — | `document:environment-shares:delete` | Delete a share (not the document); revokes access of all claimers (only way to revoke; can't revoke individuals). |

All methods accept optional `admin-access` (requires `document:documents:admin`).

## Example

```ts
import { environmentSharesClient } from "@dynatrace-sdk/client-document";

const data = await environmentSharesClient.createEnvironmentShare({
  body: { documentId: "...", access: "read" },
});
```
