---
agent: agent
description: Find dead links, renew moved URLs, and optionally remove dead bookmarks
---

Check my Chrome bookmarks' links using the `chrome-bookmarks` skill.

Scope: ${input:scope:Folder to check (empty = everything), e.g. bar/Dev}

1. `python bmk.py check [--scope <scope>] -o .bmk/link-report.json` (this can take a
   few minutes for large libraries). Summarize counts per verdict.
2. Renew: `python bmk.py renew --report .bmk/link-report.json --https` (preview).
   Show old -> new URLs. Ask before `--yes`.
3. Dead links (`dead` verdict only): list them as a table. Ask whether to delete
   them or move them to `other/Archive/Dead links` (via an `apply` plan).
   Never touch `blocked` or `error` items.
