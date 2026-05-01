---
name: torch_geometric
description: Compatibility alias for the underscore PyG skill name. Delegate to the canonical local `torch-geometric` payload while preserving route compatibility.
---

# torch_geometric (Compatibility Alias)

## Purpose

Provide a stable underscore-form alias for PyTorch Geometric workflows that are
canonically maintained under the sibling `torch-geometric` skill directory.

This preserves:

- route compatibility for callers using `torch_geometric`
- existing `skills-lock` and pack-manifest entries
- a thin alias surface instead of a second full payload copy

## Resolution Order

1. Use the canonical local `torch-geometric` skill payload first.
2. Reuse the canonical supporting files:
   - `../torch-geometric/SKILL.md`
   - `../torch-geometric/references/**`
   - `../torch-geometric/scripts/**`
3. Keep this alias directory thin and free of duplicated heavy assets.

## Minimal Workflow

1. Read `../torch-geometric/SKILL.md` for the full PyG guidance.
2. Use the canonical reference and helper scripts from `../torch-geometric/`.
3. Report under `torch_geometric` only when a caller or route explicitly requested that alias.
