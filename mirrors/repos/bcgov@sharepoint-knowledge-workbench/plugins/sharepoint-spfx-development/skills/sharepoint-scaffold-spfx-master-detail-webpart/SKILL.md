---
name: sharepoint-scaffold-spfx-master-detail-webpart
plugin: sharepoint-spfx-development
description: Scaffolds a complete SPFx Master-Detail Web Part boilerplate (TypeScript, SCSS module, manifest) from a JSON list layout specification. Use when modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier pages that rely on URL parameter query filtering (?SelectedID=...).
allowed-tools: Bash, Read, Write
examples:
  - "python3 scripts/scaffold_spfx_master_detail.py --spec dossier_spec.json --output-dir path/to/spfx-project/src/webparts/personBriefing"
---

# Scaffold SPFx Master-Detail Web Part

Generate one consolidated Master-Detail web part to replace a classic multi-web-part layout that depended on `?SelectedID=...` filtering.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Out-of-the-box List Web Parts cannot filter on a URL query string; this is the reason for a custom web part. Use it only for that kind of URL-driven master-detail page.
- The generator is local (Python 3.8+) and writes only to `--output-dir`. It needs Node.js LTS (v18 or v22) and SPFx 1.20+ for the surrounding project.
- `scripts/provision-sample-master-detail-schema.ps1`, the optional test-data script, is a live tenant write with no dry-run gate: use a non-production site and let the user run it.
- Run from this skill's root.

## Quick start

```bash
python3 scripts/scaffold_spfx_master_detail.py --spec path/to/dossier_spec.json --output-dir path/to/spfx-project/src/webparts/personBriefing
```

## Workflow

1. Set up the workspace: copy the reference project from `assets/templates/spfx-project-reference/`, or run the Yeoman generator (`WebPart`, `Minimal`).
2. Write the JSON layout spec: `webPartName`, `title`, `primaryList`, `lookupList`, `childLists` (each with `title`, `listName`, `filterField`) and `imageLibrary`.
3. Run the generator, then confirm the three output files exist (web part `.ts`, `.module.scss`, `.manifest.json`).
4. Package with `sharepoint-package-spfx-solution`.

## Verification

All three files exist in the output directory, and the manifest carries a unique GUID. Build and package to confirm the web part compiles.

## References

- [Master-detail details](references/master-detail-scaffold-details.md): read for the spec example, the generated files and the sample-data script.
