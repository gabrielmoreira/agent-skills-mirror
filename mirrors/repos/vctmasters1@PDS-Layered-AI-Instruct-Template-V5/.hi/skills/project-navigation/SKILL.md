---
description: >
  Navigate this project's Depth-Priority Hierarchical-Instruct system. Use when the user
  asks about rules, conventions, or instructions that govern this codebase — or when you need
  to find the authoritative source for a topic before acting.
---

# Skill: Project Navigation

This project uses the **Depth-Priority Hierarchical-Instruct** system. When asked about project rules, conventions, or where to find guidance, follow this protocol.

## Navigation Protocol

1. **Start at the index**: Read `.hi/index.md`
2. **Find the topic**: Look for the keyword in the index tables. Entries link at *file* granularity (not section anchors) because file paths are more stable than headings.
3. **Jump to the section**: Open the linked file and use its own `## Contents` table to navigate to the relevant section.
4. **Apply the rule**: That section is the single source of truth — do not infer, restate, or guess.

## Depth Hierarchy

Deeper `.hi/instruct.md` files override shallower ones. When rules conflict, the deeper file wins.

```
.github/copilot-instructions.md       ← META only (least authoritative for rules)
.hi/instruct.md                       ← Root (project-wide baseline)
[module]/.hi/instruct.md              ← Module (overrides root for that module)
[module]/[sub]/.hi/instruct.md        ← Submodule (overrides module)
```

## Quick Reference

| Need | File |
|------|------|
| Full topic index | `.hi/index.md` |
| Naming conventions | `.hi/conventions.md` |
| Archive / never-delete / never-reset-db | `.hi/maintenance.md` |
| Credential & .gitignore rules | `.hi/credentials.md` |
| Project overview & architecture | `.hi/instruct.md` (root) |

## When Rules Are Silent

If the applicable `.hi/instruct.md` doesn't address something:
1. Check parent `.hi/instruct.md` files going up the tree
2. Check the global `.hi/` files
3. If still silent → apply the most conservative/safe interpretation
4. Flag the gap so the `.hi/instruct.md` can be updated
