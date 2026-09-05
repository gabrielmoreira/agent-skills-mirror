# Reorder Point Formula Adapter

Use `shared/formulas/reorder-point.md` as the canonical formula. This local
reference defines how the shared formula applies inside the
`calculate-reorder-point` skill.

## Formula

```text
ROP = (D * L) + SS
```

Where:

- `ROP` is the reorder point in inventory units.
- `D` is average demand in inventory units per time unit.
- `L` is replenishment lead time in the same time unit as `D`.
- `SS` is safety stock in inventory units.

## Unit Normalization

Use `shared/glossaries/common-units.md` for unit-family boundaries. Demand and
lead time must use compatible time bases before calculation.

Examples:

- If demand is per day and lead time is in days, no time conversion is needed.
- If demand is per week and lead time is in days, convert days to weeks by
  dividing lead-time days by 7.
- If demand is per month and lead time is in days, do not assume a month length
  unless the user states the convention. Ask whether to use calendar days,
  working days, or a fixed planning month.

Use `shared/glossaries/inventory-state-terms.md` for inventory-state terms.
Demand quantity and safety stock must use the same inventory unit. If demand is
in eaches and safety stock is in cases, ask for case pack quantity before
calculating a final reorder point.

## Rounding

The raw formula can produce fractional inventory units. For countable inventory,
round the final reorder point up to the next operational unit.

If an order multiple, case pack, or pallet multiple is provided, report:

- raw reorder point;
- whole-unit reorder point;
- optional operating threshold rounded to the stated multiple.

Do not treat order multiple or minimum order quantity as part of the reorder
point formula unless the user explicitly asks for an adjusted trigger.

## Inventory Position

When the user provides current inventory facts, calculate inventory position as:

```text
inventory position = on hand + on order - allocated/backordered
```

Then compare:

```text
reorder signal = inventory position <= ROP
```

If allocation, backorder, or on-order status is unclear, label the comparison as
approximate.

## Limits

This formula assumes that average demand and lead time are representative for
the planning period. It does not calculate demand variability, lead-time
variability, service-level targets, supplier disruption risk, substitution,
expiry risk, or demand seasonality.

When those factors matter, return the reorder point as a baseline and state what
additional policy or analysis is required.
