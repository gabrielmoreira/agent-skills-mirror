---
name: sharepoint-convert-aspx-pages
plugin: sharepoint-page-modernization
description: Stages 3-4 of classic page modernization -- selects a modern page layout from declarative, data-driven rules, then maps classified components to modern sections and views, emitting an explicit gap notice for components that cannot be migrated. Produces a conversion manifest; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/layout_selection.py --classified classified.json --output layout.json"
  - "python3 scripts/component_mapping.py --layout layout.json --output manifest.json"
---

# Convert ASPX Pages

## Trigger and Purpose

Stages 3-4 of the modernization pipeline: decide the modern layout, then map
each classified component onto it. Produces a conversion **manifest** — a plan
describing the modern page — not a deployed page.

## Layout rules are data, evaluated safely

`layout_selection.py` reads declarative rules from the packaged
`assets/layout-rules.json` (or a caller-supplied override). Rule conditions are
evaluated by a **restricted AST evaluator** that permits only name lookups,
constants, comparisons, boolean operators, and arithmetic.

**Any call expression is rejected.** A rule containing `__import__(...)`,
`open(...)`, or any other call raises `UnsafeConditionError`, and the offending
rule is recorded in `skippedRules` rather than executed. Rule files are data,
so they are treated as untrusted input — verified by test.

## Gaps are named, never hidden

Not every classic component has a modern equivalent. Connected-consumer web
parts, in particular, cannot be reproduced. Rather than dropping them silently
or emitting a plausible substitute, `component_mapping.py` renders an explicit
**gap notice** from the packaged template that **names the specific lists that
were not migrated**, so a reviewer can see exactly what was lost.

Unsupported web-part types are surfaced explicitly, never silently discarded.

## No tenant writes

This skill produces a manifest describing the intended modern page. It does not
create, publish, or modify anything in SharePoint. Deployment is a separate,
explicitly-authorized concern: once you have a reviewed conversion manifest,
hand the source page name/library/target metadata to
`sharepoint-content-publication`'s `convert-page-to-modern` skill
(`spo-convert-page-to-modern.ps1`, real `ConvertTo-PnPPage` executor,
dry-run by default, gated behind `-Execute -ConfirmToken`). That skill does
not read this plugin's manifest format directly -- you supply its
`-PageName`/`-SourceLibrary`/field-mapping parameters yourself from the
manifest's contents.

## Usage

```bash
python3 scripts/layout_selection.py \
  --classified classified.json --output layout.json

python3 scripts/component_mapping.py \
  --layout layout.json --output manifest.json
```

The manifest conforms to the packaged `assets/manifest-schema.json`.

## Scripts

- `scripts/layout_selection.py` -- stage 3 CLI, `safe_eval_condition`, `UnsafeConditionError`
- `scripts/component_mapping.py` -- stage 4 CLI
- `scripts/outcomes.py` -- shared status vocabulary

Packaged assets: `assets/layout-rules.json`, `assets/webpart-mapping.json`,
`assets/manifest-schema.json`, `assets/preview-template.html`,
`assets/gap-notice.template.html`.

## Provenance

Adapted from `sp-converting-aspx-pages` in the originating SharePoint migration
repository -- the richest single artifact in the source audit (32 files). The
source's organisation-specific layout thresholds and web-part mapping entries
were replaced by the packaged, caller-overridable rule files. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

