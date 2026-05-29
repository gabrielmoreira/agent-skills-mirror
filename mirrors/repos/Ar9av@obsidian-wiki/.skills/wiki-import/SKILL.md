---
name: wiki-import
description: >
  Import a wiki knowledge graph from a graph.json export file into the current vault.
  Use this skill when the user says "import wiki", "import from export", "load graph.json",
  "import vault", "/wiki-import", or wants to transfer pages from one vault to another
  using the output of wiki-export.
---

# Wiki Import — Reconstruct Pages from graph.json

You are importing a vault's knowledge graph from a `graph.json` export (produced by `wiki-export`) into the current vault. This reconstructs page stubs with correct frontmatter, wikilinks, and typed relationships, then updates all vault metadata.

## Before You Start

1. **Resolve config** — follow the Config Resolution Protocol in `llm-wiki/SKILL.md` (walk up CWD for `.env` → `~/.obsidian-wiki/config` → prompt setup). This gives `OBSIDIAN_VAULT_PATH`.
2. Read `$OBSIDIAN_VAULT_PATH/AGENTS.md` if it exists — apply any owner-specific conventions.

## Step 1: Locate and Validate Source

**Find the import source:**
- If the user provided a path argument, use it directly.
- Otherwise auto-detect `./wiki-export/graph.json` in the current directory.
- If neither exists, ask the user for the path.

**Validate the file:**
- Must be valid JSON
- Must have top-level keys: `nodes` (array), `links` (array), `graph` (object)
- Must have at least 1 node

If validation fails, report what's wrong and stop.

**Show a preview before importing:**
```
Import preview
  Source: <path>  (exported at <graph.exported_at>)
  Nodes:  N total  (concepts: A, entities: B, skills: C, references: D, ...)
  Links:  M edges  (X typed, Y untyped)
  Target: $OBSIDIAN_VAULT_PATH
```

## Step 2: Determine Conflict Resolution Mode

Read the user's phrasing to determine mode. Default is `merge`.

| Mode | Trigger phrases | Behaviour |
|---|---|---|
| `merge` | (default, no special phrasing) | Existing pages: update frontmatter tags/summary/relationships and add missing wikilinks; new pages: create stub. |
| `skip` | "skip existing", "don't overwrite", "only new pages" | Leave existing pages completely untouched; only create pages that don't exist yet. |
| `overwrite` | "overwrite", "replace existing", "force import" | Replace all matched pages with freshly reconstructed stubs regardless of existing content. |

## Step 3: Build Internal Maps

Before writing anything, build two maps from the `links` array:

**Adjacency map** — for each node id, collect all neighbour ids (edges in either direction):
```
adjacency["concepts/transformers"] = ["entities/vaswani", "concepts/lstm", ...]
```

**Typed edge map** — for each node id, collect outgoing typed edges only (`typed: true`):
```
typed_edges["concepts/transformers"] = [
  {target: "concepts/lstm", relation: "contradicts"},
  ...
]
```

## Step 4: Reconstruct Pages

Record counts: `created = 0`, `skipped = 0`, `merged = 0`.

For each node in `nodes`:

1. Compute `page_path = $VAULT/<node.id>.md`
2. Ensure the parent directory exists (e.g. `$VAULT/concepts/`)
3. Check if the file already exists:
   - **merge mode (default) + exists** → read existing file, apply merge logic (see below), increment `merged`
   - **merge mode (default) + doesn't exist** → proceed to create stub, increment `created`
   - **skip mode + exists** → increment `skipped`, continue to next node
   - **skip mode + doesn't exist** → proceed to create stub, increment `created`
   - **overwrite mode + exists** → proceed to write fresh stub (overwrite), increment `merged`
   - **overwrite mode + doesn't exist** → proceed to create stub, increment `created`

### Page template (new or overwrite)

```markdown
---
title: <node.label>
category: <node.category>
tags: <node.tags as YAML list>
sources:
  - "imported from <graph.json path>"
<if node.summary exists>
summary: "<node.summary>"
</if>
<if typed_edges[node.id] is non-empty>
relationships:
<for each {target, relation} in typed_edges[node.id]>
  - target: "[[<target>]]"
    type: <relation>
</for>
</if>
lifecycle: draft
lifecycle_changed: <today YYYY-MM-DD>
base_confidence: 0.5
tier: supporting
created: <ISO timestamp>
updated: <ISO timestamp>
---

# <node.label>

<node.summary paragraph if available, else omit>

## Related

<for each neighbour in adjacency[node.id], sorted alphabetically>
<if edge is typed>
- [[<neighbour>]] — <relation>
<else>
- [[<neighbour>]]
</if>
</for>
```

If `adjacency[node.id]` is empty, omit the `## Related` section entirely.

### Merge logic (merge mode, existing page)

1. Read the existing page's frontmatter.
2. **Tags**: union of existing tags and `node.tags` (deduplicated, keep existing order, append new ones).
3. **Summary**: if the existing page has no `summary` field and `node.summary` exists, add it.
4. **Relationships**: union of existing `relationships:` entries and `typed_edges[node.id]` — skip entries where the same `(target, type)` pair already exists.
5. **Updated**: set `updated` to the current ISO timestamp.
6. **Body**: scan for a `## Related` section. If it exists, append any missing wikilinks from `adjacency[node.id]` that aren't already linked anywhere in the body. If no `## Related` section exists, append one with the missing links.
7. Leave the rest of the body untouched.

## Step 5: Update Vault Metadata

### `.manifest.json`

Add a new entry keyed by the canonical path of the graph.json file:

```json
"<absolute path to graph.json>": {
  "ingested_at": "<ISO timestamp>",
  "source_type": "wiki-export",
  "pages_created": ["list/of/created/pages.md"],
  "pages_updated": ["list/of/merged/pages.md"]
}
```

Also increment:
- `stats.total_sources_ingested` by 1
- `stats.total_pages` by the count of pages actually created (not skipped/merged)

If `.manifest.json` doesn't exist, create it with the standard structure:
```json
{
  "stats": {
    "total_sources_ingested": 1,
    "total_pages": <created count>
  },
  "<graph.json path>": { ... }
}
```

### `index.md`

For each **created** or **merged** page:
- Add or update the entry under its category section using the format:
  `- [[<id>]] — <summary or title> ( #tag1 #tag2)`
  (Note: space before `(` — `description ( #tag)` not `description(#tag)`)

Keep categories sorted alphabetically. Create the category section if it doesn't exist.

### `log.md`

Append one line:
```
- [<ISO timestamp>] IMPORT source="<graph.json path>" pages_created=<N> pages_skipped=<K> pages_merged=<M>
```

### `hot.md`

Rewrite the **Recent Activity** section to include this import as the latest entry:
```
- [<timestamp>] IMPORT from <graph.json path> — created X, merged Z pages
```
Update the `updated:` frontmatter timestamp. Leave other hot.md sections (Active Threads, Key Takeaways) intact unless they reference pages that were just created — in which case add brief mentions.

## Step 6: Print Summary

```
Wiki import complete → $OBSIDIAN_VAULT_PATH
  Source:  <graph.json path>
           exported at <graph.exported_at>, <N> nodes, <M> links
  Created: <X> pages
  Merged:  <Z> pages  (existing pages updated)
  Skipped: <Y> pages  (only when --skip mode was used)
```

Only show the `Skipped` line if `skip` mode was explicitly requested. If `overwrite` mode was used, label merged pages as `Replaced` instead.

## Notes

- **Stub quality**: Imported pages are stubs — they have structure and wikilinks but no full body content. They're starting points for future ingestion, not finished pages.
- **Re-running is safe**: The default `merge` mode is idempotent — re-running on an unchanged export will update timestamps but won't destroy content. Use `overwrite` only when you want to fully reset pages to stubs.
- **Directory creation**: Always create missing category directories before writing pages.
- **Broken wikilinks**: Since pages are being created together from the same export, most links will resolve. Any node referenced in `links` but absent from `nodes` (broken in the original export) will still appear as a wikilink — it just won't have a corresponding page file, which is valid.
- **Filtered exports**: If the source `graph.json` was produced with visibility filtering (noted in `graph.metadata`), imported pages will only reflect the filtered set. Note this in the summary if `graph.graph` contains a `filtered` key.
