---
agent: agent
description: Analyze Chrome bookmarks and reorganize them into a clean folder structure
---

Reorganize my Chrome bookmarks using the `chrome-bookmarks` skill and follow
`.github/skills/chrome-bookmarks/references/organize-workflow.md` exactly.

${input:goal:Any preferences? e.g. "folders for work/dev/learning", "keep bookmarks bar flat", "only touch Other bookmarks"}

Steps: snapshot (info, stats, export) -> propose a folder taxonomy and wait for my OK ->
write `.bmk/plan.json` -> run `apply` as preview and summarize -> wait for my
confirmation -> apply with `--yes` -> show the final tree and backup path.
