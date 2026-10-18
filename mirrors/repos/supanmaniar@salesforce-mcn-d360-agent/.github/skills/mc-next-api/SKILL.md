---
name: mc-next-api
description: 'Call Salesforce Marketing Cloud Next content and CMS APIs (spaces, content items, variants, publish/unpublish, clone, search) from the Salesforce CLI without an MCP server. Use when working with Marketing Cloud Next content, CMS workspaces, email or template content items, content variants, or the /connect/cms endpoints.'
---

# Marketing Cloud Next Content API

Replaces the MCP server's `mcnext_*` catalog tools for the `mc-next` family
(27 endpoints, all under the `Content` group).

## When to Use

- Listing or searching content in a CMS workspace or folder
- Creating, reading, updating, or deleting content items (emails, templates)
- Managing content spaces and folders
- Publishing, unpublishing, or cloning content
- Working with content variants

## Routing

`mc-next` endpoints are served from the **org instance**, not a tenant host:

```
{instanceUrl}/services/data/v66.0/connect/cms/...
```

Use [sf-api.sh](../../../scripts/sf-api.sh) in its default (instance) mode. Do
**not** pass `--tenant`.

## Procedure

1. **Discover the endpoint.** Search the catalog for the operation you need:

   ```bash
   node scripts/catalog-search.mjs list --family mc-next
   node scripts/catalog-search.mjs list --family mc-next --search "publish"
   ```

2. **Inspect its parameters** before calling it:

   ```bash
   node scripts/catalog-search.mjs describe content.search-content-in-workspace
   ```

3. **Call it** with the helper script:

   ```bash
   ./scripts/sf-api.sh --path /connect/cms/items/search \
     --query 'queryTerm=*&scope=All&pageSize=25&contentSpaceOrFolderIds=<spaceId>'
   ```

4. **For writes**, pass a JSON body. Use `@file` for anything large:

   ```bash
   ./scripts/sf-api.sh --method POST --path /connect/cms/contents \
     --body '{"title":"Welcome Email","contentSpaceOrFolderId":"<spaceId>"}'
   ```

## Common Operations

| Operation | Method | Path |
| --- | --- | --- |
| Search content in workspace | GET | `/connect/cms/items/search` |
| List content spaces | GET | `/connect/cms/spaces` |
| Create a content space | POST | `/connect/cms/spaces` |
| Update a content space | PATCH | `/connect/cms/spaces/:contentSpaceOrFolderId` |
| Create content | POST | `/connect/cms/contents` |
| Get content by key | GET | `/connect/cms/contents/:contentKey` |
| Update a variant | PUT | `/connect/cms/contents/variants/:variantId` |
| Delete a variant | DELETE | `/connect/cms/contents/variants/:variantId` |
| Publish content | POST | `/connect/cms/contents/publish` |
| Unpublish content | POST | `/connect/cms/contents/unpublish` |
| Clone content | POST | `/connect/cms/contents/:contentKey/clone` |

For the full list with parameters, see [ENDPOINT-INDEX.md](../../../catalog/ENDPOINT-INDEX.md)
or run `node scripts/catalog-search.mjs list --family mc-next`.

## Gotchas

- **`contentSpaceOrFolderIds` is required** for search. Omitting it returns
  `MISSING_ARGUMENT: Specify a Library and, optionally, a folder.`

  It takes a **workspace Id, not an apiName**. `CLI_Connectivity_Test` returns
  `INVALID_INPUT`; `0ZuHp000000igNNKAY` works. Get the Id from
  `GET /connect/cms/spaces` (the `id` field).
- **Search needs a `queryTerm` too**, and a one-character term is rejected with
  `INVALID_SEARCH: search term must be longer than one character`. So the minimum
  usable call is space Id **plus** a two-character term. The catalog marks every
  search parameter optional; the API requires both.
- **`pageSize` maxes at 250.** Page with the `page` query parameter.
- **`scope`** accepts `All` or `TitleOnly` (case-insensitive). There is no
  wildcard value.
- **Publishing is a separate call** from creating content. Creating a content
  item does not make it live.
- **Variants are addressed by `variantId`**, and that value is the top-level
  `managedContentVariantId` on the content response. There is **no `variants`
  array** — reading one returns nothing. `PUT` and `DELETE` both need it.
- **Content creation takes `contentType`** (e.g. `sfdc_cms__email`), not
  `contentTypeFQN`. The latter fails with `JSON_PARSER_ERROR: Unrecognized
  field`.
- **`GET /connect/cms/spaces/:contentSpaceOrFolderId` needs the Id.** Passing an
  apiName returns `NOT_FOUND`, which looks like a wrong path rather than a wrong
  identifier.

### Write capability, and one irreversible operation

Unlike the Data 360 record layer (read-only), mc-next writes are **real and
work**. Verified end-to-end by creating, updating and deleting content:

| Operation | Method | Endpoint | Status |
| --- | --- | --- | --- |
| Create content | POST | `/connect/cms/contents` | ✅ verified |
| Update content | PUT | `/connect/cms/contents/variants/:variantId` | ✅ verified |
| Delete content | DELETE | `/connect/cms/contents/variants/:variantId` | ✅ verified |
| Create workspace | POST | `/connect/cms/spaces` | ✅ verified |
| Update workspace | PATCH | `/connect/cms/spaces/:id` | ✅ verified |
| Delete workspace | DELETE | *(none)* | ❌ **not supported** |

**Creating a workspace cannot be undone through this API.** There is no DELETE
for spaces — the request returns `METHOD_NOT_ALLOWED`, and the only two DELETE
endpoints in this family are the content-variant routes. SOQL cannot help either:
`ManagedContentSpace` reports `deletable = False` and a DML delete returns
`INSUFFICIENT_ACCESS_OR_READONLY`.

Removal requires Setup → Content Workspaces. So:

> Confirm before creating a content space. It is one-way from the CLI.

**The catalog's `destructive: no` flag on `POST /connect/cms/spaces` is
misleading.** It is accurate about the verb — a POST destroys nothing — but it
says nothing about whether the created resource can be removed. The flag covers
destructive verbs only, not irreversible creation, so it must not be used as the
sole gate for confirming a write.

Content is safe to create — it has a working DELETE. Workspaces are not.

The sObject layer is read-only for CMS *content* as well: `ManagedContent` and
`ManagedContentVariant` are both `(createable=False, updateable=False,
deletable=False, queryable=True)`. All writes go through `/connect/cms/...`.
This is a property of the object, not of your permissions — an admin sees the
same flags.

## Reference

- [Content API reference](./references/content-api.md) — request/response shapes
- [ENDPOINT-INDEX.md](../../../catalog/ENDPOINT-INDEX.md) — all 27 endpoints
