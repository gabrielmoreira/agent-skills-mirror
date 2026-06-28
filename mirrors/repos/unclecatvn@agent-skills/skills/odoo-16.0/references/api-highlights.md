---
name: odoo-16-api-highlights
description: Version-distinguishing API patterns for Odoo 16. Read this when the target version is 16.0 so the reviewer/tracer applies the right rules.
---

# Odoo 16 API Highlights

Use this file as the version-specific ruleset when the resolved Odoo version is `16.0`. It supplements, not replaces, the general review checklist.

## Views

- **List view tag: `<tree>`**. The rename to `<list>` happens in 18.
- **Use `attrs="{...}"` and `states="..."` modifiers** when `invisible`, `readonly`, `required`, or `column_invisible` must react dynamically to record values in the client.
  Direct attributes such as `invisible="1"`, `invisible="context.get('default_state')"`, or `invisible="state != 'draft'"` are accepted by Odoo 16, but they are not client-side dynamic modifiers.
- **Chatter uses the explicit block**, not the `<chatter/>` shortcut from 18+.
- Reference: `references/odoo-16-view-guide.md`.

## Fields

- **Aggregation parameter: `group_operator=`**. The `aggregator=` parameter is for newer versions.
- Reference: `references/odoo-16-field-guide.md`.

## Decorators

- **`@api.model_create_multi`** should be used on `create()` overrides.
- **`@api.ondelete(at_uninstall=False)`** is available and preferred over validation logic in `unlink()`.
- Reference: `references/odoo-16-decorator-guide.md`.

## Frontend

- Odoo 16 still uses the classic `kanban-box` template name in kanban views.

## Quick Review Checks

- Wrong: `<list>` tag. Use `<tree>` in 16.
- Wrong: `aggregator=`. Use `group_operator=` in 16.
- Wrong: `<chatter/>`. Use the explicit chatter block in 16.
- Risky: relying on direct attributes such as `invisible="state != 'draft'"` for client-side dynamic behavior. Use `attrs` in 16 when it must update as field values change.
- Correct: direct `invisible="1"` or context-based `invisible="context.get('...')"` for static/context-time visibility.
- Correct: `attrs="{'invisible': [('state', '!=', 'draft')]}"` and `states="draft,confirmed"`.
- Correct: `<tree>` in views, xpath targets, and `view_mode`.
- Correct: `@api.model_create_multi` and `@api.ondelete` are appropriate in 16.
