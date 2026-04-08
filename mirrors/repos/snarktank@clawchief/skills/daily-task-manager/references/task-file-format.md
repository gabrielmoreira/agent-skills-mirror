# Legacy markdown task file

`~/.openclaw/workspace/clawchief/archive/legacy-tasks-2026-04-07.md` is now archival migration residue, not the canonical live task system.

Use it only for:
- migration review
- one-time import planning
- historical context while retiring the markdown-era workflow

For live task work, use:
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py ...`
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py schema`

Preview the import set:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py import-markdown
```

Apply the import after review:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py import-markdown --apply
```
