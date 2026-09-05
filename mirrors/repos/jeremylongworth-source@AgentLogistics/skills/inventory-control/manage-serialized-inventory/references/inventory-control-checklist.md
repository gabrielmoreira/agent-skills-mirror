# Manage Serialized Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `manage-serialized-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- serial ID list or specific serial IDs under review
- SKU, location, status, and custody record for each serial
- transaction or event window being reviewed
- source system or document evidence for current serial state

## Workflow Checks

- Confirm the serial-control scope and unique identifier format.
- Trace each serial through its transaction chronology.
- Compare serial status, location, and custody across system records and physical evidence.
- Flag missing, duplicate, mismatched, or unsupported serial state changes.
- Return serial-level findings and review actions without approving custody or financial changes.

## Output Checks

- serial scope and source records
- serial status and custody table
- transaction chronology
- exceptions and missing evidence
- review boundaries and next actions
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- unique serial trace
- duplicate serial exception
- aggregate-vs-serial count check
- custody conflict handling

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
