---
name: sharepoint-analyze-aspx-pages
plugin: sharepoint-page-modernization
description: Stages 1-2 of classic page modernization -- parses exported classic .aspx content, view exports, and connected-consumer overrides into a neutral component inventory, then classifies each component by role, type, and variant. Read-only, operates on exported files, never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/aspx_inventory.py --raw-html page.html --views views.json --output inventory.json"
  - "python3 scripts/component_classification.py --inventory inventory.json --output classified.json"
---

# Analyze ASPX Pages

## Trigger and Purpose

Use this skill to understand what a legacy classic SharePoint page is actually
made of, before deciding how to rebuild it. It is stages 1-2 of the
modernization pipeline:

```
analyze-aspx-pages  ->  convert-aspx-pages
  1. inventory          3. layout selection
  2. classification     4. component mapping
```

**Stage 1 (`aspx_inventory.py`)** parses three input sources into one neutral
inventory: rendered classic HTML (content-editor zones), a views export
(list-view zones), and an override file (connected-consumer zones that cannot
be detected from markup alone).

**Stage 2 (`component_classification.py`)** assigns each component a Role,
Type, and Variant (`Primary`, `Secondary`, `Child`, `Banner`, `Unknown`).

## Unknown is a real answer

`Unknown` is a first-class variant. A component the classifier cannot place is
reported as `Unknown` rather than being forced into a plausible-looking
category — a wrong classification is more expensive downstream than an honest
gap.

## Honest outcomes

Shared vocabulary in `outcomes.py`. A missing input is `UNAVAILABLE`, never a
clean pass. A page with no detectable components is `EMPTY`, never a success.
A partially-parseable input is `PARTIAL` with the unreadable parts recorded.
Malformed markup does not crash the stage — see the `malformed-page` fixture.

## Read-only, no tenant contact

Operates entirely on exported files you provide. No network access, no
SharePoint connection, no writes outside the output path you name.

## Usage

```bash
python3 scripts/aspx_inventory.py \
  --raw-html classic-page.raw.html \
  --views classic-page.views.json \
  --overrides classic-page.override.json \
  --output inventory.json

python3 scripts/component_classification.py \
  --inventory inventory.json --output classified.json
```

## Scripts

- `scripts/aspx_inventory.py` -- stage 1 CLI
- `scripts/component_classification.py` -- stage 2 CLI
- `scripts/outcomes.py` -- shared status vocabulary

## Boundary vs `structured-content-rendering`

That plugin *renders new* pages from structured content this workbench owns.
This plugin *analyses existing* legacy pages it did not create. Different
inputs, different responsibility -- do not conflate them (spec section 4a).

## Provenance

Adapted from `sp-analysing-aspx-pages` and `sp-converting-aspx-pages` in the
originating SharePoint migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

