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
- **`pageSize` maxes at 250.** Page with the `page` query parameter.
- **`scope`** is `All` (all fields) or `TitleOnly`.
- **Publishing is a separate call** from creating content. Creating a content
  item does not make it live.
- **Variants are addressed by `variantId`**, not by content key.

## Reference

- [Content API reference](./references/content-api.md) — request/response shapes
- [ENDPOINT-INDEX.md](../../../catalog/ENDPOINT-INDEX.md) — all 27 endpoints
