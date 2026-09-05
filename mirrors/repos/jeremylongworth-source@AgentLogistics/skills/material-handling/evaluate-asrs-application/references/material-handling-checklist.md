# Evaluate ASRS Application Material Handling Checklist

Completion token:

```text
AGENTLOGISTICS_AL_10_MATERIAL_HANDLING_READY
```

## Purpose

This reference keeps `evaluate-asrs-application` aligned with the AL-10 material-handling foundation and the `material-handling-analyst` skillset.

## Input Checks

- Confirm the request is selection analysis or planning support, not equipment certification.
- Address load, dimensions, volume, travel distance, throughput, storage height, aisle requirements, operating environment, automation level, safety, and capital intensity.
- Identify source records for quantities, dimensions, weights, distances, cycle times, uptime, downtime, utilization, layout, equipment, and safety constraints.
- Preserve missing evidence and source conflicts instead of filling gaps with typical equipment assumptions.

## Workflow Checks

- Apply hard constraints before comparing equipment preferences.
- Keep manual, powered, conveyor, AGV/AMR, AS/RS, storage, flow, and labor alternatives separate when their evidence differs.
- Calculate only from supplied facts or explicitly labeled assumptions.
- Hand off vendor design, engineered capacity, structural, fire, electrical, guarding, traffic, operator, and safety approval to qualified reviewers.

## Output Checks

- Include scope, source records, required considerations, calculations, assumptions, missing evidence, and review boundaries.
- Distinguish equipment class fit from vendor selection, equipment certification, procurement approval, or live configuration.
- Mark safety-sensitive, automation, traffic, building, equipment, and capital decisions as review-required.
- Preserve enough context for downstream material-flow, conveyor, AGV/AMR, AS/RS, equipment-sizing, and utilization skills.

## Skillset Handoff

When this skill is used inside `skillsets/material-handling-analyst/`, preserve the load profile, movement window, throughput basis, route and aisle constraints, storage-height facts, operating environment, automation readiness, safety concerns, capital-intensity limits, missing evidence, and qualified-review needs so downstream material-handling skills can continue without losing context.
