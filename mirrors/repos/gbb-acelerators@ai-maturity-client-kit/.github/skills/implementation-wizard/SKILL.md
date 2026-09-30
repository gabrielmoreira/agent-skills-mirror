---
name: implementation-wizard
description: Collects implementation guide inputs for report personalization. Use for "wizard implementacao", "implementation guide", "personalizar relatorio", "guía de implementación", "personalizar informe".
---

# Skill: Implementation wizard

Use the existing wizard assets to collect client-specific implementation inputs. Do not alter scoring.

## Relationship to v2

Wizard inputs personalize `v2_implementation_guide.pdf`. They do not change dimension scores, gaps, priority bands, flags, or strategy mappings.

## Fields

The v2 wizard has 11 fields: `executive_steering_committee`, `tpo`, `dimension_owners`, `raci_matrix`, `communication_plan`, `training_plan`, `adkar_notes`, `risk_register`, `quick_wins_w1_4`, `quick_wins_w5_8`, and `quick_wins_w9_12`.

Empty fields render as `to fill with the client`. Never say empty fields fall back to sample content.

## Procedure

1. Use [wizard/implementation-guide-wizard.html](../../../wizard/implementation-guide-wizard.html), [wizard/implementation-guide-inputs.template.json](../../../wizard/implementation-guide-inputs.template.json), or conversational collection.
2. Save `implementation-guide-inputs.json` at the workspace root.
3. Re-render reports:

```bash
python3 reports/scripts/build_payload_and_render.py
```

## Mode D

After the Learning Survey plan exists, run:

```bash
python3 wizard/scripts/auto_fill_from_plan.py --lang en
```

Mode D supports `en`, `pt-br`, and `es`, fills 7 of 11 fields, and marks the rest as fill-in items.

## v1 archive

For v1 inputs, the report dispatcher keeps the archived implementation guide behavior and ignores extra fields.
