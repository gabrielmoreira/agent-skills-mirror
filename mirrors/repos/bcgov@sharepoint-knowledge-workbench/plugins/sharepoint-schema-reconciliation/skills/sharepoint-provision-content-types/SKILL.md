---
name: sharepoint-provision-content-types
plugin: sharepoint-schema-reconciliation
description: Plans create-if-missing SharePoint content-type provisioning from a caller-supplied declarative definition (add, hide, show and unlink field links, with hidden-flag drift against the schema surfaced rather than silently fixed) plus content-type-to-list attach planning. Use when reconciling a content type against current state. Pure planning, read-safe by construction; no write ships in this module.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from content_type_provisioning import plan_add_content_type_to_list; print(plan_add_content_type_to_list('Demo_List', 'Demo_Item', ('Demo_Item',)))\""
---

# Provision Content Types

Plan how a declared content type should be reconciled against its current live state: create if missing, link fields, hide or show them, unlink fields no longer declared, and attach to lists.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-safe by construction: every function only computes a plan from caller-supplied inputs. Execution goes through `sharepoint-provision-list`'s gated `apply_provisioning`, or the `sharepoint-provisioning` plugin's executors.
- Reconcile, do not recreate: leave an existing content type alone except for the drift the schema calls out. Report a hidden-flag mismatch as drift in the action's `detail`; never correct it silently.
- Unlink a field only if it is currently linked. An already-absent link is neither an error nor a fake success.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from content_type_provisioning import ContentTypeDef, ContentTypeFieldSpec, ContentTypeState, plan_content_type
ct = ContentTypeDef(name="Demo_Item", parent="Item", fields=(ContentTypeFieldSpec(field_name="Widget_Count", hidden=False),), unlink_fields=("Deprecated_Field",))
current = ContentTypeState(name="Demo_Item", exists=True, field_links={"Deprecated_Field": False})
for a in plan_content_type(ct, current): print(a.step, a.already_correct, a.detail)
```

## Workflow

1. Describe the declared content type (`ContentTypeDef`) and the observed state (`ContentTypeState`).
2. Call `plan_content_type`; use `plan_add_content_type_to_list` to attach it to a list.
3. Present each action and any drift to the user before any apply.

## Verification

Every action shows `step`, `already_correct` and `detail`; drift is named in `detail`. A plan with every action `already_correct` means current state matches the schema.

## References

- [Content type provisioning details](references/content-type-provisioning-details.md): read for the reconcile rules, full usage and provenance.
- [Pipeline and write safety](references/schema-reconciliation-pipeline.md): read for where the executors live.
