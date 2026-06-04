---
mode: agent
description: Post-task reflection — examine what changed this session, identify instruction gaps, and propose improvements to .ai/ files.
---

# /ai-reflect

Reflect on the current session and propose targeted improvements to the AI-INSTRUCT system. This command is the interactive entry point for the `reflect-and-improve` governed tool.

> **→ [reflect-and-improve tool](../../.ai/agents/tools/reflect-and-improve.json)** — full checklist for this procedure.
> **→ [AI-INSTRUCT Maintenance Rule](../copilot-instructions.md#ai-instruct-maintenance-rule)** — update instruction files as part of every architectural change.

---

## Steps

### 1. Review session changes

Run:
```
git diff HEAD --stat
git status --short
```

Read the changed files to understand what was added, modified, or removed this session.

### 2. Load the active instruction scope

For each path that was changed, load the effective instruction scope using `.ai/engine/get_effective_instructions.py`. Identify which `.ai/instruct.md` file governs each change.

### 3. Identify instruction gaps

Look for any of the following:

| Signal | Means |
|---|---|
| Agent had to guess at a convention | Rule is absent or underspecified |
| Agent interpreted a rule inconsistently across files | Rule is ambiguous |
| Two rules pointed in opposite directions | Rule conflict |
| Same pattern appeared 3+ times with no canonical source | Canonicalization opportunity |
| A module was added/changed with no `.ai/instruct.md` update | Maintenance rule violation |

### 4. Propose improvements

For each gap, identify the **target file** (use the deepest scope that covers the gap) and write an explicit before/after proposal:

```
### Proposal: [short title]
**Target**: .ai/instruct.md (or [module]/.ai/instruct.md)
**Gap**: [what is missing or wrong]
**Proposed addition**:
> [exact text to add]
```

Present **all proposals together** before applying any.

### 5. Apply confirmed proposals

For each proposal the user approves:

1. Apply the change using the `apply-safe-change` checklist
2. Bump `Last Updated` on the modified file to today
3. Call `log-action` with `action: "reflect-and-improve"`, `safety_level: "medium"`, `approval_obtained: true`

After all approved changes are applied:

4. Run `/ai-update-index` to rebuild `.ai/index.md`
5. Summarise what was changed and what was skipped

### 6. No gaps found

If no gaps are identified, report:
> "No instruction improvements identified for this session."

---

## Constraints

- **Never** apply a proposal without explicit user confirmation.
- **Never** modify `.ai/conventions.md`, `.ai/maintenance.md`, `.ai/credentials.md`, or `.ai/environment.md` without strong justification — these are global canonical rules shared across all adopted projects.
- Prefer adding content to existing files over creating new `.ai/instruct.md` files.
