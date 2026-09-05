# Manage Expiration Controlled Inventory Inventory Control Checklist

Completion token:

```text
AGENTLOGISTICS_AL_07_INVENTORY_CONTROL_READY
```

## Purpose

This reference keeps `manage-expiration-controlled-inventory` aligned with the AL-07 inventory-control
foundation and the `inventory-control-specialist` skillset.

## Input Checks

- item, SKU, item group, location, facility, or inventory scope
- inventory unit and source system or record owner
- SKU, lot, quantity, inventory unit, and location
- expiration date, best-by date, or usable-life date basis
- as-of date and minimum remaining shelf-life rule
- status such as available, hold, quarantine, damaged, expired, or blocked

## Workflow Checks

- Confirm the date basis, as-of date, and minimum remaining shelf-life rule.
- Calculate days until expiry and classify inventory by expiry risk.
- Separate usable, near-expiry, expired, held, and unavailable inventory by lot and location.
- Check rotation and allocation risks against the selected policy.
- Return actions for review, hold, allocation check, or disposition packet without approving release.

## Output Checks

- date basis, as-of date, and shelf-life rule
- expiry risk table by SKU, lot, location, and status
- usable, near-expiry, expired, and held quantities
- rotation or allocation risks
- review requirements and missing evidence
- Include source conflicts, missing evidence, assumptions, and review boundaries.
- Keep operational recommendations separate from approval decisions.

## Evidence Checks

- Identify whether each value came from WMS, ERP, count sheet, source document, SOP, or user statement.
- Preserve transaction chronology when receipts, picks, moves, counts, or adjustments affect the result.
- Do not net conflicting units, statuses, lots, serials, or dates without a supplied conversion or policy.
- For discrepancy work, trace receiving quantity, WMS balance, physical count, picking transactions, and adjustment history before naming a cause.

## Acceptance Checks

- days-until-expiry calculation
- minimum shelf-life threshold
- held inventory exclusion
- quality release boundary

## Handoff

When this skill is used inside `skillsets/inventory-control-specialist/`,
preserve the item scope, unit basis, source records, unresolved conflicts,
and next required review so downstream inventory-control skills can continue
without losing evidence context.
