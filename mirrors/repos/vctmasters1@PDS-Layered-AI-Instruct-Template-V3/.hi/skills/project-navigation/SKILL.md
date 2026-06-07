---
description: >
  Navigate this project's Depth-Priority Hierarchical AI-INSTRUCT system. Use when the user
  asks about rules, conventions, or instructions that govern this codebase — or when you need
  to find the authoritative source for a topic before acting.
---

# Skill: Project Navigation

This project uses the **Depth-Priority Hierarchical AI-INSTRUCT** system. When asked about project rules, conventions, or where to find guidance, follow this protocol.

## Navigation Protocol

1. **Start at the index**: Read `.ai/index.md`
2. **Find the topic**: Look for the keyword in the index tables. Entries link at *file* granularity (not section anchors) because file paths are more stable than headings.
3. **Jump to the section**: Open the linked file and use its own `## Contents` table to navigate to the relevant section.
4. **Apply the rule**: That section is the single source of truth — do not infer, restate, or guess.

## Depth Hierarchy

Deeper `.ai/instruct.md` files override shallower ones. When rules conflict, the deeper file wins.

```
.github/copilot-instructions.md       ← META only (least authoritative for rules)
.ai/instruct.md                       ← Root (project-wide baseline)
[module]/.ai/instruct.md              ← Module (overrides root for that module)
[module]/[sub]/.ai/instruct.md        ← Submodule (overrides module)
```

## Quick Reference

| Need | File |
|------|------|
| Full topic index | `.ai/index.md` |
| Naming conventions | `.ai/conventions.md` |
| Archive / never-delete / never-reset-db | `.ai/maintenance.md` |
| Credential & .gitignore rules | `.ai/credentials.md` |
| Project overview & architecture | `.ai/instruct.md` (root) |

## When Rules Are Silent

If the applicable `.ai/instruct.md` doesn't address something:
1. Check parent `.ai/instruct.md` files going up the tree
2. Check the global `.ai/` files
3. If still silent → apply the most conservative/safe interpretation
4. Flag the gap so the `.ai/instruct.md` can be updated
