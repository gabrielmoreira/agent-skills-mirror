# BASES

Obsidian Bases are optional helper artifacts. They are explicit-only and should not be created by default.

## Default policy

- Do not generate `.base` files unless the user explicitly asks for Bases or database-like views.
- Keep `.base` files under a project-local helper area only when they improve navigation.
- Do not make Bases the canonical registry or source of truth.

## Basic structure

A `.base` file is YAML and typically contains:

```yaml
filters:
  and:
    - 'status == "active"'

views:
  - type: table
    name: "Active Results"
    order:
      - file.name
      - status
      - updated
```

## Good use cases

- table view for active experiments or results
- card view for paper notes
- filtered task-like view over canonical notes

## Avoid by default

- auto-generating many `.base` files during bootstrap
- using Bases to replace `_system/registry.md`
- coupling critical project logic to plugin-specific Base behavior
