---
name: sharepoint-provision-content-types
plugin: sharepoint-provisioning
description: Plans create-if-missing SharePoint content-type provisioning from a caller-supplied declarative definition -- add/hide/show/unlink field links, with hidden-flag drift against the schema surfaced (not silently fixed) and content-type-to-list attach planning. Pure planning, read-safe by construction; no write ships in this module.
allowed-tools: Bash, Read
examples:
  - "python -c \"from content_type_provisioning import ContentTypeDef, plan_content_type; print(plan_content_type(ct_def, current))\""
  - "python -c \"from content_type_provisioning import plan_add_content_type_to_list; print(plan_add_content_type_to_list('Demo_List', 'Demo_Item', ('Demo_Item',)))\""
---

# Provision Content Types

## Trigger and Purpose

Use this skill to plan how a declared SharePoint content type should be
reconciled against its current live state: create it if missing, link any
declared fields, hide/show them per the schema, unlink fields no longer
declared, and attach the content type to target lists.

This skill is read-safe by construction — every function here only computes
a plan from caller-supplied inputs. Nothing it returns has been executed
against a tenant; execution happens only via `provision-list`'s gated
`apply_provisioning`.

## Reconcile, not recreate

- An existing content type is left alone except for the drift the schema
  calls out.
- A field-link's hidden flag is compared against the schema; a mismatch is
  reported as drift in the action's `detail` (`"... (drift: was ...)"`), not
  silently corrected without being named.
- Fields listed in `ContentTypeDef.unlink_fields` are unlinked only if
  currently linked — never a no-op mistaken for success, never an error on
  an already-absent link either.

## Where the "injected executor" actually lives

This skill's Python planning functions ship no tenant transport of their own
-- by design. The real, tested PnP.PowerShell executor that these content-type
plans are meant to be submitted to is `sharepoint-migration-planning`'s
`apply-sharepoint-provisioning-plan` skill, which runs
`spo-provision-content-types.ps1`, `spo-update-content-type.ps1`,
`spo-remove-content-type.ps1`, and `spo-detach-content-type-from-list.ps1`
(all of which consume outputs from this module verbatim). This skill produces
the plan; that skill is the executor you inject.

## Usage

```bash
python -c "
from content_type_provisioning import ContentTypeDef, ContentTypeFieldSpec, ContentTypeState, plan_content_type

ct = ContentTypeDef(
    name='Demo_Item',
    parent='Item',
    fields=(ContentTypeFieldSpec(field_name='Widget_Count', hidden=False),),
    unlink_fields=('Deprecated_Field',),
)
current = ContentTypeState(name='Demo_Item', exists=True, field_links={'Deprecated_Field': False})
for action in plan_content_type(ct, current):
    print(action.step, action.already_correct, action.detail)
"
```

## Scripts

- `scripts/content_type_provisioning.py` -- `ContentTypeDef`, `ContentTypeFieldSpec`, `ContentTypeState`, `ContentTypeAction`, `plan_content_type`, `plan_add_content_type_to_list`

## Provenance

Adapted from `content-type-lib.ps1`'s six functions (`New-SiteContentTypeSafe`,
`Add-FieldToContentTypeSafe`, `Hide-FieldOnContentTypeSafe`,
`Show-FieldOnContentTypeSafe`, `Unlink-FieldFromContentTypeSafe`,
`Add-ContentTypeToListSafe`) in the originating SharePoint migration
repository — see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
The source performed live PnP writes inline; this module only plans. Real
execution requires an explicitly injected executor via
`provision-list`'s `apply_provisioning`.

