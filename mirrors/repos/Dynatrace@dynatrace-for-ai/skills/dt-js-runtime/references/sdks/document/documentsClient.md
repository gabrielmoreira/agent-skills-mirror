# `documentsClient`

Core document lifecycle: create, read, update, delete, content, snapshots, ownership. Import:

```ts
import { documentsClient } from "@dynatrace-sdk/client-document";
```

| Method | Returns | Scope | Purpose |
|---|---|---|---|
| `createDocument` | `DocumentMetaData` | `document:documents:write` | Create a document (you become owner). `name` + `type` required; content max 50 MB. `type` is user-defined semantics, not Content-Type. |
| `getDocument` | `GetDocumentResponse` | `document:documents:read` | Get metadata + content in one multipart response. Optional `snapshot-version` (needs write access). |
| `getDocumentMetadata` | `DocumentMetaData` | `document:documents:read` | Get metadata only. Optional extra fields, `snapshot-version`. |
| `downloadDocumentContent` | — | `document:documents:read` | Download latest (or snapshot) content; response Content-Type matches upload. |
| `updateDocument` | `UpdateDocumentMetadata` | `document:documents:write` | Update metadata and/or content; optionally create a snapshot. Optimistic-locking version required. |
| `updateDocumentContent` | `DocumentMetaData` | `document:documents:write` | Replace content entirely (0 < size ≤ 50 MB). Requires Content-Type + Content-Disposition on the part; optimistic locking. |
| `updateDocumentMetadata` | `DocumentMetaData` | `document:documents:write` | ⚠️ Deprecated — use `updateDocument`. Partial metadata update. |
| `deleteDocument` | — | `document:documents:delete` | Move document to trash (optimistic locking via `optimistic-locking-version`). Must own it. |
| `bulkDeleteDocument` | `BulkDeleteResponse` | `document:documents:delete` | Move up to 100 documents to trash by id. |
| `transferDocumentOwner` | — | `document:documents:write` | Transfer ownership; previous owner loses access. Owner-only. |
| `listDocuments` | `DocumentList` | `document:documents:read` | List accessible documents' metadata; `filter`/`sort` (see notes), naive pagination. |
| `listSnapshots` | `SnapshotList` | `document:documents:read` | List a document's snapshots (newest first); requires write access; paginated. |
| `getSnapshotMetadata` | `SnapshotMetadata` | `document:documents:read` | Metadata about a snapshot itself (requires write access). |
| `restoreSnapshot` | `RestoreDocumentResult` | `document:documents:write` | Reset content to a snapshot's state (creates a snapshot of current state first if none); content-only. |
| `deleteSnapshot` | — | `document:documents:write` | Irrevocably delete a snapshot (owner-only); doesn't affect current content. |

All methods accept optional `admin-access` (requires `document:documents:admin`).

## `listDocuments` filter/sort

- **Filterable fields:** `id`, `name`, `type`, `version`, `owner`, `modificationInfo.{createdTime,createdBy,lastModifiedTime,lastModifiedBy}`, `originAppId`, `originExtensionId`. Operators `contains`/`starts-with`/`ends-with` are case-insensitive (string fields); `==`/`!=` are case-sensitive equality operators. String literals must use single quotes. Max nesting depth 3, max length 1024 chars. Example: `type in ('dashboard', 'notebook') and name contains 'report'`.
- **Sortable fields:** `name`, `type`, `version`, `owner`, `modificationInfo.*`, `originAppId`, `userContext.lastAccessedTime`. Max 5 sort params. Default sort: by id. Example: `name,-type,modificationInfo.lastModifiedTime`.
- Pagination is naive — interim mutations can yield duplicates/missing entries.

## Example

```ts
import { documentsClient } from "@dynatrace-sdk/client-document";

const data = await documentsClient.createDocument({
  body: { name: "...", type: "...", content: "..." },
});
```
