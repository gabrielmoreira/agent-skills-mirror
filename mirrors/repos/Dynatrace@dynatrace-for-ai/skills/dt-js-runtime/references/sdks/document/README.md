# Document (`@dynatrace-sdk/client-document`)

> Env: ✅ Server runtime
> Status: current

Create, manage, and share documents (dashboards, notebooks, launchpads). Documents are schemaless and hold up to **50 MB** of content.

## Clients & key methods

| Client | Methods | Purpose |
|---|---|---|
| `documentsClient` | `createDocument`, `getDocument`, `downloadDocumentContent`, `updateDocument`, `deleteDocument`, `listDocuments` | Document CRUD + metadata/content |
| `directSharesClient` | `createDirectShare`, recipients mgmt | Share with specific users/groups |
| `environmentSharesClient` | `createEnvironmentShare`, claim | Environment-wide shares |
| `documentLockingClient` | acquire / inspect / release | Active edit locks |
| `trashClient` | list / restore / purge | Deleted-document trash |

Full method/type detail: [documentsClient.md](documentsClient.md), [directSharesClient.md](directSharesClient.md), [environmentSharesClient.md](environmentSharesClient.md), [documentLockingClient.md](documentLockingClient.md), [trashClient.md](trashClient.md) (per-method returns, scopes, examples) · [types.md](types.md).

## Required scopes

- `document:documents:read` / `document:documents:write` (plus share/trash scopes as needed).

## Example

```ts
import { documentsClient } from "@dynatrace-sdk/client-document";

const doc = await documentsClient.createDocument({
  body: { name: "Report", type: "dashboard", content: "..." },
});
```

## Concepts

- **Access management** — two layers: IAM **endpoint permissions** (e.g. `document:documents:read`, not modifiable via API) and per-document **document permissions** (modeled in the service, modifiable via sharing endpoints). A user needs both.
- **Sharing** — three mechanisms, not mutually exclusive:
  - **Public** — via `updateDocument` (`isPrivate: false`); grants read to all environment users immediately.
  - **Environment-shares** — grant read or read-write to same-environment users, but users must actively **claim** the share; owner loses control over who claims.
  - **Direct-shares** — immediately grant read/read-write to specific users/groups; owner keeps full control and can revoke. Max one direct-share per access type per document; up to 1000 recipients.
  - Set `isReshareable: false` (via `updateDocument`) to stop write-access users from re-sharing.
- **Owner transfer** — `transferDocumentOwner`; previous owner loses access.
- **Locking:**
  - **Optimistic locking** (mandatory) — modifying ops require the current document `version`; mismatch ⇒ rejected.
  - **Active locking** (optional) — lock a document to block other users' updates. Max **5 locked docs per user**; lock duration max **15 min** (default 10); re-acquiring extends.
- **Deletion & restoration** — deletes move to trash, permanently removed after **30 days**; restore re-grants prior access.
- **Snapshots** — reset content to an earlier state. Created explicitly on update; max **50 per document** (oldest auto-deleted), rate-limited **5 per 60 s**, auto-deleted after **30 days**. Read with doc read access; create with write access; restore/delete owner-only.
- **Document identity** — unique immutable `id` assigned at creation; may be user-supplied, else system-generated.
- **Admin access** — `document:documents:admin` lets a user act on all environment documents regardless of ownership; enabled per-request via the `admin-access` parameter (not supported for ready-made documents).
- **User data** — no names/emails stored; SSO ids are persisted. Last-access per document is tracked for ordering.
- **System-owned / ready-made / extension-shipped documents** — some documents are system-, app- (`originAppId`), or extension-owned (`originExtensionId`) and auto-available on install/update.
- **Content size** — max **50 MB** per document.

Canonical reference: https://developer.dynatrace.com/develop/sdks/client-document/ · npm `@dynatrace-sdk/client-document` (v1.30.0).
