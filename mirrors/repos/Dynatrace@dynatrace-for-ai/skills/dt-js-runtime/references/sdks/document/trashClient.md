# `trashClient`

Manage deleted documents (trash). Deleted documents are permanently destroyed after **30 days**. Import:

```ts
import { trashClient } from "@dynatrace-sdk/client-document";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `listTrashedDocuments` | `TrashDocumentList` | `document:trash.documents:read` | List your trashed documents; `filter` by `id`/`name`/`type`/`deletionInfo.*`; naive pagination. |
| `inspectTrashedDocument` | `TrashDocument` | `document:trash.documents:read` | Inspect a deleted document's metadata (owner-only). |
| `restoreTrashedDocument` | — | `document:trash.documents:restore` | Restore from trash; all prior-access users regain access (owner-only). |
| `deleteTrashedDocument` | — | `document:trash.documents:delete` | Irreversibly destroy the document (owner-only). |

All methods accept optional `admin-access` (requires `document:documents:admin`).

## Example

```ts
import { trashClient } from "@dynatrace-sdk/client-document";

const data = await trashClient.restoreTrashedDocument({ id: "..." });
```
