---
name: sharepoint-provision-fields
plugin: sharepoint-provisioning
description: Filters an exported field set down to deployable fields, detects live-type drift against a declared schema, and builds raw Field XML for column types a typed field-creation API cannot express (Calculated -- no -Formula parameter exists; Lookup/LookupMulti; User/UserMulti). Pure planning; no write ships in this module.
allowed-tools: Bash, Read
examples:
  - "python -c \"from field_provisioning import filter_deployable_fields; print(filter_deployable_fields(fields))\""
  - "python -c \"from field_provisioning import build_calculated_field_xml; print(build_calculated_field_xml(field_def, field_id=my_guid))\""
---

# Provision Fields

## Trigger and Purpose

Use this skill to decide which fields from an exported field set are worth
deploying, detect when a live field's type has drifted from what a schema
declares, and construct the raw Field XML required for column types a
typed field-creation API cannot express directly.

## The calculated-column workaround

Typed field-creation APIs generally accept a type but no formula parameter
— a Calculated column has to be created via raw Field XML instead.
`build_calculated_field_xml` builds that XML, escaping every caller-
supplied string: attribute values (display name, static name, group) with
the full XML attribute-escaping set (`&` `<` `>` `"` `'`), and the formula
body (element text) with the text-escaping subset (`&` `<` `>`). Any call
with a non-Calculated `FieldDef` or a missing formula raises
`FieldDefinitionError` rather than emitting malformed or misleading XML.
`build_lookup_field_xml` and `build_user_field_xml` cover Lookup/LookupMulti
and User/UserMulti the same way.

## Deployable-field filtering

`filter_deployable_fields` keeps a field only if it belongs to the
`"Custom Columns"` group, is not a skip-listed system/computed type
(Counter, Computed, Calculated, workflow/event/taxonomy internals, etc.),
is not `Title`, is not explicitly excluded, and is either force-included or
both visible and writable. Nothing is deployed silently by default —
hidden and read-only fields are excluded unless the caller opts them in by
name.

## Where the "injected executor" actually lives

This skill's Python planning functions ship no tenant transport of their own
-- by design. The real, tested PnP.PowerShell executor that these field plans
are meant to be submitted to is `sharepoint-migration-planning`'s
`apply-sharepoint-provisioning-plan` skill, which runs
`spo-provision-site-columns.ps1`, `spo-update-site-column.ps1`, and
`spo-remove-site-column.ps1` (all of which consume outputs from this module
verbatim). This skill produces the plan; that skill is the executor you inject.

## Usage

```bash
python -c "
from field_provisioning import FieldDef, plan_field_action

fd = FieldDef(internal_name='Widget_Count', display_name='Widget Count', type='Number')
print(plan_field_action(fd, existing_type=None))       # -> create
print(plan_field_action(fd, existing_type='Number'))    # -> exists
print(plan_field_action(fd, existing_type='Text'))       # -> repair
"
```

## Scripts

- `scripts/field_provisioning.py` -- `FieldDef`, `FieldAction`, `filter_deployable_fields`, `field_needs_type_repair`, `build_calculated_field_xml`, `build_lookup_field_xml`, `build_user_field_xml`, `plan_field_action`

## Provenance

Adapted from `field-helpers.ps1`'s `Get-DeployableFields`,
`Repair-FieldType`, `Add-FieldSafe`, and `Invoke-FieldsForList` (the
declared-schema-driven field-application loop), plus the calculated/lookup/
user raw-XML construction technique from
`reset-and-provision-etl-target-schema.ps1` — see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
The source performed live `Add-PnPField`/`Add-PnPFieldFromXml` writes
inline; this module only plans and renders XML. Real execution requires an
explicitly injected executor via `provision-list`'s `apply_provisioning`.

