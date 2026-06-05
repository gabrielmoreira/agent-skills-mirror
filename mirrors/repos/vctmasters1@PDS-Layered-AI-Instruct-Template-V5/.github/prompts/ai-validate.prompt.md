---
mode: agent
description: Route validation request through /ai-route, then run scope-aware instruction and port validation
---

# /ai-validate

Route the validation request through `/ai-route` to resolve scope and governance, then run instruction-drift and port validation within that scope.

## Quick Start

In Copilot Chat:
```
/ai-validate
```

Optional scope hint (if validating a specific module):
```
/ai-validate src/api
```

---

## Workflow: Route → Validate

### Step 1: Route Through `/ai-route`

**Invoke the Router:**

```
/ai-route

Task: Validate project instructions and configuration
Scope: root (or user's specified scope if provided)
Context: This is a validation workflow.
  Route to pds-pipe-validator for scope-aware instruction/port validation.
  Apply any scope-level validation rules.
  Report findings with severity (error/warning/info).
```

The Router will:
1. Resolve the target scope (deepest `.ai/instruct.md` for the specified path)
2. Check for validation governance rules
3. Route to `pds-pipe-validator` with scope context
4. `pds-pipe-validator` executes validation within that scope

### Step 2: Validation Execution (via pds-pipe-validator)

Once routed, the validator agent will:

1. Read [.github/dev-specs.md](../dev-specs.md) to confirm developer shell and OS

2. Run instruction-drift validation:
   - **Windows / pwsh**: `pwsh -NoProfile -File .github/scripts/validate-instructions.ps1`
   - **macOS / Linux** (pwsh installed): same command
   - Capture stdout and exit code
   - Scan scope-specific `.ai/instruct.md` files

3. Run port registry validation:
   - `python .ai/engine/port_validator.py . --scope <resolved_scope>`
   - Report ERROR/WARN findings (collisions, range violations, unregistered services, drift, orphaned)

4. Report findings grouped by category:
   - **Instruction drift**: Unfilled placeholders, retired syntax, missing TOCs, frontmatter problems, broken links
   - **Index drift**: `.ai/index.md` older than indexed `instruct.md` files
   - **Port issues**: Collision, range_violation, unregistered, drift, orphaned

5. For each issue, propose a one-line fix (no auto-edit unless user asks)

6. Exit with summary and recommended next step

---

## See Also

- [/ai-route](ai-route.prompt.md) — the routing gateway (invoked from this prompt)
- [pds-pipe-validator](../agents/pds-pipe-validator.agent.md) — validator worker (routed to)
- [.github/scripts/validate-instructions.ps1](../scripts/validate-instructions.ps1) — instruction validator script
- [.ai/engine/port_validator.py](../../.ai/engine/port_validator.py) — port registry validator
