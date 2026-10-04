---
name: sharepoint-scaffold-schema-definition
plugin: sharepoint-site-build-and-publish
description: Scaffolds a declarative SiteSchemaDefinition JSON structure from scratch or from input parameters, without a live tenant connection. Use to author or bootstrap a new SharePoint site schema definition locally before diffing it with sharepoint-site-build-and-publish or provisioning it with sharepoint-site-build-and-publish.
allowed-tools: Bash, Read, Write
examples:
  - "python3 scripts/schema_scaffold.py --label pilot-site --output schema.json"
---

# Scaffold Schema Definition

Author a new `SiteSchemaDefinition` locally. The command line writes an empty definition; the Python
function builds one from dictionaries.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Constraints

- Local only. No tenant connection and no tenant writes; the output is a JSON file you name.
- The CLI (`--label`, `--output` required) writes an empty definition with status `OBSERVED` and no
  columns, content types or lists. Populate it with `scaffold_schema(...)`, not by hand-editing.
- Diffing and provisioning are other skills' jobs: hand the result to
  `sharepoint-site-build-and-publish` or `sharepoint-site-build-and-publish`.
- Run from this skill's root. Standard library only.

## Quick start

```bash
python3 scripts/schema_scaffold.py --label pilot-site --output schema.json
```

## Workflow

1. For an empty template, run the command above.
2. For a populated definition, call `scaffold_schema(label, output_path, site_columns, content_types,
   lists)` with dicts for each section. A list without a `key` gets one derived from its title.
3. Report the written path and the section counts.

## Verification

Confirm the file exists, loads with `SiteSchemaDefinition.load`, and its section counts match the input.
