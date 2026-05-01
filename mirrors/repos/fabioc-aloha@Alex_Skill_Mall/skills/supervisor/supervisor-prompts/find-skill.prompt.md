---
description: "Supervisor: Search Alex_Skill_Mall by keyword and surface matching skills with ready-to-copy install commands"
mode: agent
lastReviewed: 2026-04-30
---

# Find Skill

Query the Mall catalog and return matches without round-tripping to GitHub.

## Steps

1. **Get the query** from the user — a topic, technology name, or problem ("PDF", "shell injection", "azure auth").

2. **Locate Mall locally** — try:
   - `%USERPROFILE%/Alex_Skill_Mall` or `~/Alex_Skill_Mall`
   - Sibling directory: `..\Alex_Skill_Mall` from the current heir's repo
   - If absent, instruct: `git clone https://github.com/fabioc-aloha/Alex_Skill_Mall.git ~/Alex_Skill_Mall`

3. **Search** — case-insensitive grep across:
   - All `skills/<category>/<name>/SKILL.md` files (title and body)
   - `CATALOG.md` if present
   - `patterns/<name>.md` files
   - Folder names themselves (a query like "pdf" should match `md-to-pdf` even if its SKILL.md doesn't say "pdf" prominently)

4. **Rank** results by:
   - Folder name exact match (highest)
   - Title H1 match
   - Body match (snippet relevance)

5. **Display** top ~5 matches as:

   ```
   <name>  <category>
     <one-line description from H1 or first paragraph>
     Install: cp -r ~/Alex_Skill_Mall/skills/<category>/<name> .github/skills/local/<name>
     [+ if companion .cjs exists]
     Then:    mv .github/skills/local/<name>/<name>.cjs .github/muscles/local/<name>.cjs
   ```

6. **Suggest** running `/install-from-mall` for guided install if the user picks one.

## Refuse if

- Query is empty (ask for a topic)
- Mall not found and user declines to clone

## Notes

- The Mall is independent of the heir — searching it doesn't modify anything
- For the official catalog, link to <https://github.com/fabioc-aloha/Alex_Skill_Mall/blob/main/CATALOG.md>
