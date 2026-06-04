---
mode: agent
description: Scan all .ai/ instruction files in the project and rebuild .ai/index.md with a complete, up-to-date section index.
---

# Update Index

Rebuild the master section index at `.ai/index.md`.

## Steps

1. Find every file matching `**/.ai/instruct.md` and `.ai/*.md` in the project using `file_search` or `grep_search`

2. **Exclude** these directories from the scan:
   - Exclude `.dev-docs/.old/`
   - `.archive/`
   - `node_modules/`

3. For each matching file:
   - Extract all `##` section headings (not `#` title or `###` subsections)
   - Note the file's relative path from the project root
   - Infer a one-line description from the section content if one isn't obvious

4. Rebuild the index table in `.ai/index.md`:
   - Group sections by file (one group per file)
   - Format: `| Section Name (linked to file) | Relative file path (linked) | One-line description |`
   - Preserve the existing "How to Use" and "Rebuilding This Index" sections unchanged
   - Update the "Last Updated" date to today

5. Report what changed: files added, files removed, sections added or removed.

## Format Rules

- Section links use the file path as the link target (not anchor links, since headings vary)
- File paths are relative to the project root and use forward slashes
- Do not alter non-table content in `index.md`
