# CLAUDE.md

This repository is a **task skill router** for authorized research and analysis workflows.

## On Any Task

`RULES.md` is the single source of truth. Read it immediately before doing anything — it contains the complete behavior chain, routing matrix, authorization pre-declaration, and tool registry.

## First-Run Setup

`skills/tool-index.md` is not included in fresh clones. Generate it before starting:

```bash
# macOS / Linux
bash skills/scripts/refresh-tool-index.sh

# Kali Linux
bash kali/scripts/refresh-tool-index.sh
```

Read `README_AI.md` for the full bootstrap sequence.
