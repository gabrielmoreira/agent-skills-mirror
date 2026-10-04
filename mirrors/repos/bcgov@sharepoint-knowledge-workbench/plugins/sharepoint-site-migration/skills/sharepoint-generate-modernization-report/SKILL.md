---
name: sharepoint-generate-modernization-report
plugin: sharepoint-site-migration
description: Renders a human-readable Markdown disposition report from a PageConversionManifest (conforming to assets/manifest-schema.json), with a web-part classification table, a gaps section naming every unmigrated item, and a layout and confidence summary. Use to give a reviewer a scannable view of a conversion plan. A pure function on a manifest already on disk; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/conversion_report.py --manifest manifest.json --output conversion-report.md"
---

# Generate Conversion Report

Turn a produced conversion manifest into a readable Markdown report: what was classified, what could not be migrated, and how confident the decisions were.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Render only. It reads one manifest and writes one report; it does not produce a manifest. No network calls and no tenant I/O.
- Gaps are named, never hidden: every `gaps` entry is its own line, and an empty `gaps` array prints an explicit "No gaps recorded".
- The manifest must carry every required top-level field in `assets/manifest-schema.json`; a missing field is `Unavailable` and no report is written. An invalid `outcome` value is `Failed`.
- Run from this skill's root. Standard library only.

## Quick start

```bash
python3 scripts/conversion_report.py --manifest manifest.json --output conversion-report.md
```

## Workflow

1. Get a manifest conforming to the schema (assembled by the caller or the modernization agent from the conversion stage outputs).
2. Run `conversion_report.py --manifest ... --output ...`.
3. Report the outcome and the report path, and read the Gaps section aloud for the user.

## Verification

`Observed` means no gaps; `Partial` means one or more gaps (the count is named); `Unavailable` and `Failed` write nothing. Confirm the Gaps section lists every entry from the manifest.

## References

- [Report details](references/conversion-report-details.md): read for the required fields, the outcome table and provenance.
- [Pipeline and outcomes](references/page-modernization-pipeline.md): read for how the manifest relates to the stage outputs.
- [Manifest schema](assets/manifest-schema.json): read when checking the manifest shape.
