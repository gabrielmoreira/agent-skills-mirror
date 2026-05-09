---
name: odoo-19-api-highlights
description: Version-distinguishing API patterns for Odoo 19. Read this when the target version is 19.0 so the reviewer/tracer applies the right rules.
---

# Odoo 19 API Highlights

Use this file as the version-specific ruleset when the resolved Odoo version is `19.0`. It supplements — not replaces — the general review checklist. Everything from 18 applies unless noted below.

## Models

- **`_name` is optional** — Odoo 19 derives it automatically from the CamelCase class name (each capital letter → `.` separator):
  - `ResPartner` → `res.partner`
  - `SaleOrder` → `sale.order`
  - `MyModel` → `my.model`
- **`_sql_constraints`** — the constraint name can be omitted; Odoo auto-generates a unique name based on model + attribute.
- Reference: `references/odoo-19-model-guide.md`.

## Views

- Same as 18: `<list>` tag, direct-expression attrs. Reference: `references/odoo-19-view-guide.md`.

## Fields

- Same as 18: `aggregator=` for aggregation. Reference: `references/odoo-19-field-guide.md`.

## Decorators

- Same as 18: `@api.ondelete`, `@api.model_create_multi`. `@api.returns` usage patterns are expanded in the v19 guide. Reference: `references/odoo-19-decorator-guide.md`.

## Quick review checks (v19-specific)

- ✅ `_name` may be omitted when the CamelCase class name maps correctly — don't flag as missing.
- ✅ Unnamed `_sql_constraints` are valid — don't flag as missing name.
- All 18 rules still apply (`<list>`, direct-expression attrs, `aggregator=`, `@api.ondelete`, `@api.model_create_multi`).
