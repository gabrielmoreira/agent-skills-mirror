---
mode: agent
description: Route index rebuild through /ai-route, then scan .ai/ instruction files and rebuild .ai/index.md
---

# /ai-update-index

Route the index update through `/ai-route` to resolve scope, then scan all `.ai/` instruction files and rebuild the master index.

## Quick Start

In Copilot Chat:
```
/ai-update-index
```

To update a specific module's index:
```
/ai-update-index src/api
```

---

## Workflow: Route → Scan → Rebuild

### Step 1: Route Through `/ai-route`

**Invoke the Router:**

```
/ai-route

Task: Rebuild instruction index
Scope: root (or user-specified scope for module-level index)
Context: This is an index maintenance workflow.
  Route to pds-man-curator for index rebuild within resolved scope.
  Scan all .ai/ instruction files in that scope.
  Update Last Updated date to today.
```

The Router will:
1. Resolve the target scope (which `.ai/index.md` to rebuild?)
2. Check for index governance rules
3. Route to `pds-man-curator` with scope context
4. `pds-man-curator` executes index rebuild within that scope

### Step 2: Index Rebuild Execution (via pds-man-curator)

Once routed, the curator agent will:

1. Find every file matching `**/.ai/instruct.md` and `.ai/*.md` in the resolved scope
   - Use `file_search` or `grep_search`

2. Exclude these directories:
   - `.dev-docs/.old/`
   - `.archive/`
   - `node_modules/`
   - Any vendored or third-party folders

3. For each matching file:
   - Extract all `##` section headings (skip `#` title and `###` subsections)
   - Note the file's relative path from the scope root
   - Infer a one-line description from section content if needed

4. Rebuild the index table in `.ai/index.md`:
   - Group sections by file
   - Format: `| Section Name (linked to file) | Relative file path (linked) | One-line description |`
   - Preserve existing "How to Use" and "Rebuilding This Index" sections
   - Update `Last Updated` to today (`YYYY-MM-DD`)

5. Report what changed: files added, removed, sections added/removed

---

## See Also

- [/ai-route](ai-route.prompt.md) — the routing gateway (invoked from this prompt)
- [pds-man-curator](../agents/pds-man-curator.agent.md) — curator (routed to, maintains `.ai/index.md`)
- [.ai/index.md](../../.ai/index.md) — the index being rebuilt

## Format Rules

- Section links use the file path as the link target (not anchor links, since headings vary)
- File paths are relative to the project root and use forward slashes
- Do not alter non-table content in `index.md`
