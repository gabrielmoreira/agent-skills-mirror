# Optimize Pick Path Fulfillment Optimization Checklist

Completion token:

```text
AGENTLOGISTICS_AL_09_FULFILLMENT_OPTIMIZATION_READY
```

## Purpose

This reference keeps `optimize-pick-path` aligned with the AL-09
fulfillment-optimizer foundation and the `fulfillment-optimizer` skillset.

## Input Checks

- Confirm order pool, pick list, location sequence, and order-profile scope.
- Identify whether the work is low-volume/high-SKU, high-volume/low-SKU,
  ecommerce each-pick, case pick, pallet movement, or mixed orders.
- Confirm location map, aisle sequence, distance matrix, or travel-distance
  basis before calculating path impact.
- Preserve replenishment, batch, zone, staging, packing, equipment, traffic, and
  carrier-cutoff constraints.

## Workflow Checks

- Apply movement, zone, equipment, heavy-item, fragile-item, controlled-item, and
  priority constraints before minimizing travel.
- Compare proposed and baseline routes only when both use the same distance
  basis.
- Hand off stockout, replenishment, packing, staging, and shipping constraints to
  the relevant AL-09 fulfillment skills.

## Output Checks

- Include the route scope, source records, mapped and unmapped locations, travel
  assumptions, and missing evidence.
- Keep path recommendations separate from live system configuration changes.
- Do not claim mathematical optimality without complete distance data and a
  validated optimization method.
- Preserve equipment, pedestrian, traffic, carrier, and safety review
  boundaries.
