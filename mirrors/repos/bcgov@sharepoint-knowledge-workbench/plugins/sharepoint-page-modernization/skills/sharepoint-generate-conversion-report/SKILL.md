---
name: sharepoint-generate-conversion-report
plugin: sharepoint-page-modernization
description: Renders a human-readable Markdown disposition report from a PageConversionManifest (conforming to assets/manifest-schema.json) -- a web-part classification table, a gaps section naming every unmigrated item, and a layout/confidence summary. Pure function on the manifest already on disk; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/conversion_report.py --manifest manifest.json --output conversion-report.md"
---

# Generate Conversion Report

## Trigger and Purpose

A produced conversion manifest (`assets/manifest-schema.json`) is structured
JSON -- accurate, but not something a reviewer can scan quickly. This skill
turns an already-produced manifest into a readable Markdown disposition
report: what web parts were classified, what could not be migrated, and how
confident the layout/mapping decision was.

## Inputs

A single **manifest file** conforming to `assets/manifest-schema.json`'s
required top-level fields (`sourcePage`, `convertedAt`, `manifestHash`,
`mapping`, `environmentProfile`, `source`, `target`, `webParts`, `layout`,
`gaps`, `confidence`, `outcome`). This is the same manifest produced by
`convert-aspx-pages`.

## Gaps are named, never hidden

Every entry in the manifest's `gaps` array is rendered as its own line in
the report's Gaps section -- none dropped, none summarized away. An empty
`gaps` array renders an explicit "No gaps recorded" line rather than an
absent section, so a reviewer never has to guess whether the section was
skipped or genuinely empty.

## Honest outcomes

| Condition | Outcome | Report written? |
|---|---|---|
| Manifest missing a required field | `Unavailable` | No |
| Manifest `outcome` field is not a valid outcome status | `Failed` | No |
| Manifest has one or more `gaps` | `Partial` (gap count named) | Yes |
| Manifest has no gaps | `Observed` | Yes |

## No tenant writes

This skill only reads the manifest file it is given and writes the one
report file it is given (or `conversion-report.md` in the current
directory, by default). It performs no network calls and no
SharePoint/tenant I/O of any kind.

## Usage

```bash
python3 scripts/conversion_report.py \
  --manifest manifest.json --output conversion-report.md
```

## Scripts

- `scripts/conversion_report.py` -- CLI entry point, `render_conversion_report`
- `scripts/outcomes.py` -- shared status vocabulary

## Provenance

Generalized from a disposition-worksheet capability found in another
SharePoint migration repository's `sharepoint-migration` plugin -- only the
shape (classification table, gap/dependency summary, confidence section) was
carried over; its organisation-specific rule categories and hardcoded paths
were not.

