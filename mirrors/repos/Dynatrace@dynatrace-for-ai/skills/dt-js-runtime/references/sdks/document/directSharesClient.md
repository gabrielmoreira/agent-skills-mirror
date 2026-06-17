# `directSharesClient`

Direct-shares immediately grant read or read-write access to specific SSO users/groups. Import:

```ts
import { directSharesClient } from "@dynatrace-sdk/client-document";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `addDirectShareRecipients` | — | `document:direct-shares:write` | Add SSO users/groups (max 1000) to a share; they immediately gain access. Already-added entries ignored. |
| `createDirectShare` | `DirectShare` | `document:direct-shares:write` | Create a direct-share (read or read-write) for a document you own or can reshare. Max one share per access type per document; optionally seed recipients. |
| `deleteDirectShare` | — | `document:direct-shares:delete` | Delete a share (not the document); revokes access of all its recipients. |
| `getDirectShare` | `DirectShare` | `document:direct-shares:read` | Retrieve a direct-share by id. |
| `getDirectShareRecipients` | `DirectShareRecipientList` | `document:direct-shares:read` | List a share's recipients (groups before users); paginated (`page`/`nextPageKey`/`pageSize`, max 1000). |
| `listDirectShares` | `DirectShareList` | `document:direct-shares:read` | List all direct-shares accessible to you; `filter` by `documentId`; naive pagination. |
| `removeDirectShareRecipients` | — | `document:direct-shares:write` | Remove recipients (max 1000); they immediately lose access. Non-existing entries ignored. |

All methods accept optional `admin-access` (requires `document:documents:admin`).

## Example

```ts
import { directSharesClient } from "@dynatrace-sdk/client-document";

const data = await directSharesClient.createDirectShare({
  body: {
    documentId: "...",
    access: "read-write",
    recipients: [{ id: "441664f0-23c9-40ef-b344-18c02c23d789", type: "group" }],
  },
});
```
