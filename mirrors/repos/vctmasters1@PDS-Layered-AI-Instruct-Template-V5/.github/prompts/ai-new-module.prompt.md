---
mode: agent
description: Route module creation through /ai-route, then scaffold new module with .ai/instruct.md, .dev-docs/, registration, and index rebuild
---

# /ai-new-module

Route the module creation workflow through `/ai-route` to resolve scope and governance, then scaffold a new module with full AI-INSTRUCT integration.

## Quick Start

In Copilot Chat:
```
/ai-new-module
```

---

## Workflow: Route → Ask → Create → Register → Rebuild Index

### Step 1: Route Through `/ai-route`

**Invoke the Router:**

```
/ai-route

Task: Create new module with AI-INSTRUCT integration
Scope: root (or user-specified parent directory)
Context: This is a module creation workflow.
  Route to pds-pipe-scaffolder for module scaffolding within resolved scope.
  Apply scope-level naming conventions and structure rules.
  Ensure module authority (.ai/instruct.md) is created with proper hierarchy.
```

The Router will:
1. Resolve the target scope (which `.ai/instruct.md` governs module creation?)
2. Check for module governance rules (naming patterns, structure templates, etc.)
3. Route to `pds-pipe-scaffolder` with scope context
4. `pds-pipe-scaffolder` executes module creation within that scope

### Step 2: Module Creation (via pds-pipe-scaffolder)

Once routed, the scaffolder agent will:

1. Ask the user for:
   - Module name (must be `kebab-case`; reject otherwise per [AI Enforcement](../../.ai/conventions.md#ai-enforcement))
   - One-sentence description of module purpose
   - Whether the module needs its own `.env.example` (runtime config)

2. Validate against scope-level naming conventions:
   - Check for naming conflicts with existing modules
   - Ensure kebab-case per scope's governance
   - Verify uniqueness across the scope hierarchy

3. Create the module directory and files:
   ```
   [module-name]/
   ├── .ai/
   │   └── instruct.md           ← scaffold with module authority template
   └── .dev-docs/
       ├── index.md              ← archive tracking template
       └── .old/                 ← directory for archived docs
   ```
   
   If user confirms, also create:
   ```
   [module-name]/.env.example    ← per .ai/credentials.md#env-file-convention
   ```

4. Populate `.ai/instruct.md` with:
   - Module overview and dependencies
   - Scope declaration (deeper than parent)
   - Template placeholders for module-specific rules
   - References to global rules (conventions, maintenance, credentials)
   - `Last Updated` filled with today's date (YYYY-MM-DD, not `[DATE]`)

5. Populate `.dev-docs/index.md` with archive tracking template

6. Register the module in the parent scope's `.ai/instruct.md`:
   - Add row to `## Key Directories` or equivalent registry table
   - Include module name, `.ai/instruct.md` path, one-line description
   - Update parent's `Last Updated` to today

7. Rebuild the index:
   - Invoke `/ai-update-index` for the resolved scope
   - Ensure new module appears in master index

8. Report:
   - Module path created
   - What was auto-filled
   - What still needs user input (module-specific rules, entry points, etc.)

---

## Guardrails

- Never overwrite existing module — stop and ask if module already exists
- Reject non-kebab-case names per AI Enforcement rules
- Never modify files outside the new module + parent `.ai/instruct.md`
- Validate naming against scope-level governance before creating

---

## See Also

- [/ai-route](ai-route.prompt.md) — the routing gateway (invoked from this prompt)
- [pds-pipe-scaffolder](../agents/pds-pipe-scaffolder.agent.md) — scaffolder worker (routed to)
- [Directory Naming](../../.ai/conventions.md#directory-naming) — kebab-case convention
- [AI Instruction File Naming](../../.ai/conventions.md#ai-instruction-file-naming) — `.ai/instruct.md` naming
- [`.dev-docs` Convention](../../.ai/conventions.md#dev-docs-convention) — module documentation
- [/ai-update-index](ai-update-index.prompt.md) — index rebuild (invoked after module creation)
