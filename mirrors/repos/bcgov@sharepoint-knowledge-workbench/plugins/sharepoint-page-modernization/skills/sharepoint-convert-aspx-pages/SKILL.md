---
name: sharepoint-convert-aspx-pages
plugin: sharepoint-page-modernization
description: Stages 3-4 of classic page modernization. Selects a modern page layout from declarative, data-driven rules, then maps classified components to modern sections and views, emitting an explicit gap notice for components that cannot be migrated. Use after classification, to plan the modern page. Produces mapping and view plans; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/layout_selection.py --input classified.json --output layout.json"
  - "python3 scripts/component_mapping.py --components classified.json --layout layout.json --output-mapping mapping.json --output-views views.json"
---

# Convert ASPX Pages

Decide the modern layout (stage 3), then map each classified component onto it (stage 4). The result is a plan describing the modern page, not a deployed page.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- No tenant writes. Never create, publish or modify anything in SharePoint; deployment is a separate, authorized step (`sharepoint-convert-page-to-modern`).
- Layout rules are untrusted data. Conditions run in a restricted evaluator (names, constants, comparisons, boolean and arithmetic operators only); any call expression raises `UnsafeConditionError` and
  the rule goes to `skippedRules`.
- Gaps are named, never hidden. A component with no modern equivalent (connected consumers especially) gets an explicit gap notice naming the lists not migrated; unsupported web-part types
  are surfaced, never discarded.
- Run from this skill's root. Standard library only.

## Quick start

```bash
python3 scripts/layout_selection.py --input classified.json --output layout.json
python3 scripts/component_mapping.py --components classified.json --layout layout.json --output-mapping mapping.json --output-views views.json
```

## Workflow

1. Take `classified.json` from `sharepoint-analyze-aspx-pages`.
2. Select the layout (`layout_selection.py`; add `--rules` for a caller-supplied ruleset).
3. Map the components (`component_mapping.py`; optional `--mapping-rules`, `--view-name-prefix`). Review the gap notice.
4. Report the mapping, the views to provision, and every gap. Assembling a full conversion manifest from these outputs is done by the caller or the modernization agent, not by a script here.

## Verification

Confirm each stage's outcome, that `skippedRules` is empty or explained, and that every connected consumer appears as `NOT_MIGRATED` in the gap notice.

## References

- [Conversion details](references/aspx-conversion-details.md): read for the safe rule evaluator, gap handling, optional flags, packaged assets and the deployment handoff.
- [Pipeline and outcomes](references/page-modernization-pipeline.md): read for the stage table and why no script emits the full manifest.
- Assets: [layout rules](assets/layout-rules.json), [web-part mapping](assets/webpart-mapping.json), [manifest schema](assets/manifest-schema.json),
  [gap notice template](assets/gap-notice.template.html), [preview template](assets/preview-template.html).
