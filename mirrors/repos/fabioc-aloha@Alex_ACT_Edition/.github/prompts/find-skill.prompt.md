---
description: "Search Alex_Skill_Mall by keyword and surface matching skills"
mode: agent
lastReviewed: 2026-05-01
---

# Find Skill

Search the Mall catalog for skills matching a keyword.

## Steps

1. **Get the query** from the user — a topic, technology name, or problem ("PDF", "shell injection", "azure auth").

2. **Fetch the catalog** — try in order:
   - **GitHub API** (always fresh): `gh api repos/fabioc-aloha/Alex_Skill_Mall/contents/CATALOG.json --jq .content | base64 -d`
   - **Local clone** (fallback): `~/Alex_Skill_Mall/CATALOG.json` or `C:\Development\Alex_Skill_Mall\CATALOG.json`
   - If neither works, link to <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.json>

3. **Search** the JSON catalog — case-insensitive match on:
   - `name` field
   - `category` field
   - `description` field
   - `triggers` array
   - `applyTo` patterns

4. **Rank** results by:
   - Name exact match (highest)
   - Category match
   - Description/trigger match

5. **Display** top 5 matches as:

   ```
   <name>  (<category>)
     <one-line description>
     Install: /install-from-mall <name>
   ```

6. **Suggest** running `/install-from-mall` for guided install if the user picks one.

## Notes

- Searching does not modify anything — read-only
- The Mall has 303 skills across 35 categories
- Catalog is JSON — parse `skills` array, each entry has `name`, `category`, `path`, `description`, `triggers`
- For the full catalog: <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.json>
