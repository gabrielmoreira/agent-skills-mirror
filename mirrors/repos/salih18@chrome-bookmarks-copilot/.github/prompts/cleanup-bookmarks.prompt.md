---
agent: agent
description: Remove duplicate bookmarks and empty folders, and fix bad titles
---

Clean up my Chrome bookmarks using the `chrome-bookmarks` skill:

1. `python bmk.py info` and `python bmk.py stats --json`. Report what you found.
2. Duplicates: run `python bmk.py dedupe` (preview). Show which copy is kept and
   which are removed. Ask me before `--yes`.
3. Empty folders: `python bmk.py prune` (preview) -> ask -> `--yes`.
4. Bad titles (raw URLs, "Untitled", very long SEO titles): propose new names as a
   table (id, old, new), then put the approved ones in `.bmk/plan.json` as `rename`
   ops and `apply` (preview -> ask -> `--yes`).
5. Finish with `stats` and the backup path.
