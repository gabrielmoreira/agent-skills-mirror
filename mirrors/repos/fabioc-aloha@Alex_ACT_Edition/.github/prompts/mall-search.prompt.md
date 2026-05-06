---
description: "Search the Alex ACT Plugin Mall by keyword, category, shape, or tier"
mode: agent
lastReviewed: 2026-05-02
---

# /mall search

Search the Plugin Mall catalog for plugins matching a query.

## Steps

1. **Get the query** from the user: a topic, technology, problem, category name, or shape.

2. **Fetch the catalog** (try in order):
   - **GitHub API**: `gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/CATALOG.json --jq .content | base64 -d`
   - **Local clone**: `~/Alex_ACT_Plugin_Mall/CATALOG.json` or `C:\Development\Alex_ACT_Plugin_Mall\CATALOG.json`
   - If neither works, link to <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.json>

3. **Parse** the `plugins` array in CATALOG.json. Each entry has: `name`, `title`, `category`, `shape`, `tier`, `description`, `token_cost`, `path`, `artifacts`.

4. **Search** (case-insensitive) across: `name`, `title`, `category`, `description`.

5. **Display** top results as:

   ```text
   <name>  <shape>  (<category>, <tier>)  ~<token_cost> tokens
     <one-line description>
     Install: /mall install <name>
   ```

6. **If the user filters by shape or tier**, apply before display:
   - `/mall search ISP.` shows only trifectas
   - `/mall search security standard` shows standard-tier security plugins

## Notes

- Read-only: searching does not modify anything
- Shape notation: `.S..` (skill), `.S.M` (skill+muscle), `ISP.` (trifecta), etc.
- Plugin count and categories are derived from CATALOG.json at runtime
