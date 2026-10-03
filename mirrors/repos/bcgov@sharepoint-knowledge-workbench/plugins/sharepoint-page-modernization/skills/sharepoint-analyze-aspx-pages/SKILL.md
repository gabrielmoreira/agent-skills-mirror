---
name: sharepoint-analyze-aspx-pages
plugin: sharepoint-page-modernization
description: Stages 1-2 of classic page modernization. Parses exported classic .aspx content, view exports and connected-consumer overrides into a neutral component inventory, then classifies each component by role, type and variant. Use to understand what a legacy page is made of before deciding how to rebuild it. Read-only; operates on exported files and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/aspx_inventory.py --source-html page.html --views-json views.json --output inventory.json"
  - "python3 scripts/component_classification.py --input inventory.json --output classified.json"
---

# Analyze ASPX Pages

Understand what a legacy classic SharePoint page is made of: stage 1 builds an inventory, stage 2 classifies each component.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. Operate only on exported files you are given; no network access, no SharePoint connection, no writes outside the output path you name.
- `Unknown` is a real answer. Report a component the classifier cannot place as `Unknown`; never force it into a plausible category.
- Never treat a missing or empty result as a pass: missing input is `Unavailable`, no detectable components is `Empty`, a partly readable input is `Partial` with the gaps recorded.
- Run from this skill's root. Standard library only.

## Quick start

```bash
python3 scripts/aspx_inventory.py --source-html classic-page.raw.html --output inventory.json
python3 scripts/component_classification.py --input inventory.json --output classified.json
```

## Workflow

1. Get the exported rendered HTML, optionally a views export (`--views-json`) and a connected-consumer override file (`--override`).
2. Run stage 1 (`aspx_inventory.py`), then stage 2 (`component_classification.py`) on its output.
3. Report the components with their Role, Type and Variant (`Primary`, `Secondary`, `Child`, `Banner`, `Unknown`), and the outcome of each stage.
4. Hand `classified.json` to `sharepoint-convert-aspx-pages`.

## Verification

Check each stage's outcome is `Observed`. Treat `Empty`, `Partial` and `Unavailable` as findings with their detail, and list every `Unknown` component.

## References

- [Analysis details](references/aspx-analysis-details.md): read for stage inputs, the `Unknown` variant, full usage and provenance.
- [Pipeline and outcomes](references/page-modernization-pipeline.md): read for the stage table, the outcome vocabulary and the boundary with `content-rendering`.
