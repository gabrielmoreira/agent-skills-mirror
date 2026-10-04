---
name: sharepoint-plan-column-changes
plugin: sharepoint-site-build-and-publish
description: Filters an exported field set down to deployable fields, detects live-type drift against a declared schema, and builds raw Field XML for column types a typed field-creation API cannot express (Calculated has no formula parameter; Lookup and LookupMulti; User and UserMulti). Use when planning site-column provisioning. Pure planning; no write ships in this module.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from field_provisioning import filter_deployable_fields; print(filter_deployable_fields(fields))\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from field_provisioning import build_calculated_field_xml; print(build_calculated_field_xml(field_def, field_id=my_guid))\""
---

# Provision Fields

Decide which exported fields are worth deploying, detect type drift against a schema, and build raw Field XML for column types a typed API cannot express.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Planning only, zero tenant I/O. Nothing this skill returns has been executed; execution goes through the `sharepoint-site-build-and-publish` plugin's `sharepoint-apply-provisioning-plan` skill.
- Raw Field XML is the only route for a Calculated column. `build_calculated_field_xml` escapes every caller-supplied string; a non-Calculated `FieldDef` or a missing formula raises `FieldDefinitionError`. Never emit
  hand-built XML around it.
- Deploy nothing silently: hidden and read-only fields are excluded unless the caller opts them in by name.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from field_provisioning import FieldDef, plan_field_action
fd = FieldDef(internal_name="Widget_Count", display_name="Widget Count", type="Number")
print(plan_field_action(fd, existing_type=None))   # create
print(plan_field_action(fd, existing_type="Text")) # repair
```

## Workflow

1. Filter the export with `filter_deployable_fields`.
2. For each field, call `plan_field_action(fd, existing_type=...)`: `create`, `exists` or `repair`.
3. For Calculated, Lookup or User columns build the XML with `build_calculated_field_xml`, `build_lookup_field_xml` or `build_user_field_xml`.
4. Hand the plan to the executor skill after the user reviews it.

## Verification

Each field has an explicit action; XML builders either returned escaped XML or raised `FieldDefinitionError`. Report any `repair` (type drift) to the user rather than fixing it silently.

## References

- [Field provisioning details](references/field-provisioning-details.md): read for the calculated-column workaround, the filtering rules, usage and provenance.
- [Pipeline and write safety](references/schema-reconciliation-pipeline.md): read for where the executors live and the shared outcome vocabulary.
