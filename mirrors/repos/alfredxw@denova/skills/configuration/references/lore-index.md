# Lore Index

Both resources have scope `workspace`, bound to the current project. They support `list`, `get` and `update` only. Use the returned IDs and revisions; never edit `setting/lore/items.json` directly.

## Guide document: `lore_index`

Read `config_read(operation=get, resource=lore_index, ids=["index"])`. The returned item has `id`, `revision` and `guide`. Submit the complete `guide` as `config_apply.value`, not the surrounding inspection object:

```json
{
  "operation": "update",
  "resource": "lore_index",
  "scope": "workspace",
  "id": "index",
  "revision": "REVISION_FROM_GET",
  "value": {
    "intro_markdown": "Read the relevant character and location sections before drafting.",
    "groups": [
      {
        "id": "harbor-cast",
        "name": "Harbor cast",
        "purpose": "People relevant to harbor investigations.",
        "body_markdown": "Consult these entries when a scene involves the port authority.",
        "default_detail": "brief"
      }
    ],
    "automatic_details": { "resident": "full", "auto:character": "brief" }
  }
}
```

- Start from the current guide and preserve everything outside the request, including other groups, automatic overrides, `group_order` and `item_order`. `groups` is required; an explicit `[]` removes all custom groups. Missing optional fields clears their overrides.
- Keep existing group IDs stable when renaming or reordering. For a new group, choose a unique lowercase ASCII ID using letters, digits and hyphens, at most 64 bytes. Names must be unique. With no saved order, `groups` defines custom section order, followed by automatic sections.
- `group_order` is an optional ordered array of keys: `custom:<group ID>` or `automatic:<automatic key>`, for example `["automatic:resident", "custom:harbor-cast", "automatic:auto:character"]`. It can interleave custom and automatic groups. Unlisted groups follow the default order. Preserve temporarily hidden automatic keys.
- `item_order` maps those same group keys to ordered item IDs, for example `{ "custom:harbor-cast": ["captain", "navigator"] }`. Unlisted members follow in name order. This never adds memberships or enables items. Keep absent/disabled members' saved positions unless asked to change them; permanent deletions clear their references on save. Use IDs from membership metadata and preserve unrelated groups' order. Names and content edits do not move explicitly ordered items.
- `default_detail` is `name`, `brief` or `full`. Every section is directly included in initial model context; there is no activation switch.
- Each entry includes its category display name, importance and actual detail after membership overrides. Empty full bodies display briefs and are marked `brief`. Tags stay searchable and available in Lore query results; they are not automatically injected into the index.
- Automatic groups contain enabled items without custom-group associations. Their keys are `resident`, `auto:<category ID>` and `manual:<category ID>`. Use current category IDs from the Lore catalog or membership metadata. With no override, resident groups include full bodies; other groups include names. Removing an override restores that default.
- A custom group overrides the item's legacy load mode while it has an association. Multiple associations use the most complete effective detail, with the complete content included only once.
- Delete a group only when requested: remove it from the guide. The store backs up the collection and atomically removes its associations, preserving all lore entries, bodies and assets. Items with no remaining associations return to automatic grouping.
- Limits: 256 groups, 256 UTF-8 bytes per name, 1024 bytes per purpose, and 64 KiB for the introduction. The rendered index is capped at 1088 KiB; excess content causes an explicit context/preview error, never silent truncation. Prefer names or briefs for large libraries.
- The guide revision covers the collection, so an item edit also invalidates it. Re-read before a guide change after membership writes. On conflict, re-read and reconcile; do not overwrite the current document with an old draft.

## Item associations: `lore_index_membership`

`list` returns lightweight item metadata including disabled entries: `id`, `name`, `enabled`, `type`, `load_mode`, `index_memberships` and `revision`. Optional `query` filters by ID or name; follow `next_cursor` to retrieve all matches. This catalog excludes bodies and assets. Disabled items remain manageable but never enter model context. Use Lore read tools when deciding groups requires item content.

Read exact item IDs with `get`. To associate an entry, add a membership using an existing group's stable ID, retain unrelated memberships, and submit:

```json
{
  "operation": "update",
  "resource": "lore_index_membership",
  "scope": "workspace",
  "id": "captain",
  "revision": "REVISION_FROM_GET",
  "value": {
    "index_memberships": [{ "group_id": "harbor-cast", "detail": "inherit" }]
  }
}
```

`detail` is `inherit`, `name`, `brief` or `full`. `inherit` uses the group's current default. The array replaces only this item's associations, leaving its name, body, category, enabled state, load mode and assets unchanged. Use `[]` to remove all associations; omitted or null arrays are invalid. Do not send inspection metadata in `value`.

For multiple items, read their current memberships and revisions, then apply one independently committed update per item. A failed item does not undo successful updates. Record results and retry only failed items after reconciling their current state. Create new groups before associating items. After any update, re-read to verify the saved guide or associations; a receipt alone is not verification.
