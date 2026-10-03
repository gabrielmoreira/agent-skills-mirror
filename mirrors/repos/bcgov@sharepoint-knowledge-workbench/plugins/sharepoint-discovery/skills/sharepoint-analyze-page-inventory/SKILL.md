---
name: sharepoint-analyze-page-inventory
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint page inventory, scoring per-page migration complexity, classifying web-part categories and emitting a disposition hint per page (migrate as-is, rebuild, retire), using a caller-supplied rules file. Use when planning a classic-to-modern migration and deciding which pages are cheap to move. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from page_inventory_analysis import run; print(run(inventory_path='inv.json', rules_path='rules.json', output_dir='out/').status)\""
---

# Analyze Page Inventory

Answer: how complex is each page, which web-part categories appear, and what is the suggested
disposition (migrate as-is, rebuild, retire).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. The analysis makes no tenant writes and no network access; it reads the export path
  you name and writes to the output directory you name.
- Rules are data, not code. Complexity weights, category classifications and disposition
  thresholds all come from the caller-supplied rules JSON. No site-specific judgement is built in.
- A missing input file is `UNAVAILABLE` and creates no output directory; never fabricate defaults
  to look successful. An empty inventory is `EMPTY`, never a pass.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from page_inventory_analysis import run
o = run(inventory_path='page-inventory.json', rules_path='rules.json', output_dir='out/')
print(o.status, o.detail)"
```

## Workflow

1. Get a page inventory from `scripts/collect-sharepoint-page-inventory.ps1` or any source in the
   same JSON shape; see [collection](references/page-inventory-collection-and-scripts.md).
2. Choose the rules file and the output directory.
3. Call `run(...)`: `load_rules`, `analyse` (`compute_complexity`, `disposition_hint`), then
   `generate_report`.
4. Report per-page complexity, web-part categories and disposition.

## Verification

Check `outcome.status` is `OBSERVED` and the output directory holds the report. Treat any other
status as the honest outcome it is; see [outcomes](references/discovery-outcomes.md).

## References

- [Collection and scripts](references/page-inventory-collection-and-scripts.md): read when you
  need a fresh export or the script list.
- [Outcomes](references/discovery-outcomes.md): read when interpreting a non-`OBSERVED` status.
