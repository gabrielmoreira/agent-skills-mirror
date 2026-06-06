---
mode: agent
description: Route reflection through /hip-route, then examine changes, identify instruction gaps, and propose improvements to .hi/ files
---

# /hip-reflect

Route the reflection workflow through `/hip-route` to resolve scope and governance, then examine session changes, identify instruction gaps, and propose targeted improvements to `.hi/` files.

## Quick Start

In Copilot Chat:
```
/hip-reflect
```

---

## Workflow: Route → Reflect → Propose

### Step 1: Route Through `/hip-route`

**Invoke the Router:**

```
/hip-route

Task: Post-task reflection and instruction gap analysis
Scope: root (or narrower if working within a specific module)
Context: This is a reflection workflow.
  Route to hia-learner for gap identification and proposal.
  Apply scope-level instruction authority.
  Ensure proposed improvements stay within the deepest .hi/instruct.md scope.
```

The Router will:
1. Resolve the target scope(s) affected by this session's changes
2. Check for reflection governance rules
3. Route to `hia-learner` with scope context
4. `hia-learner` executes reflection within resolved scope(s)

### Step 2: Reflection Execution (via hia-learner)

Once routed, the learner agent will:

1. Review session changes:
   - `git diff HEAD --stat` and `git status --short`
   - Read all changed files to understand adds/modifications/removals

2. Load the effective instruction scope:
   - For each changed path, resolve the governing `.hi/instruct.md` (deepest wins)
   - Ensure proposed improvements target the right authority file

3. Identify instruction gaps:
   - Agent guessed at conventions (rule absent or underspecified)
   - Rules interpreted inconsistently across files (rule ambiguous)
   - Conflicting rules (two rules point opposite directions)
   - Repeated patterns 3+ times with no canonical source (canonicalization needed)
   - Module added/changed with no `.hi/instruct.md` update (maintenance rule violation)

4. Propose improvements:
   - For each gap, identify target file (use deepest scope)
   - Write explicit before/after proposals
   - Suggest which scope (root `.hi/instruct.md`, module `.hi/instruct.md`, or new file) owns the rule

5. Ask user approval:
   - Show proposed changes
   - Ask if they want to apply (yes/no)
   - If yes, apply edits and commit with message "docs: Update .hi/ instruction files per reflection"
   - If no, archive the proposals for later consideration

---

## See Also

- [/hip-route](hip-route.prompt.md) — the routing gateway (invoked from this prompt)
- [hia-learner](../../agents/tier-2/observers/hia-learner.agent.md) — learner worker (routed to)
- [Hierarchical-Instruct Maintenance Rule](../../../.github/copilot-instructions.md#hierarchical-instruct-maintenance-rule) — update instruction files as part of every architectural change
- [reflect-and-improve tool](../../agents/tools/reflect-and-improve.json) — full checklist for this procedure
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

4. Run `/hip-update-index` to rebuild `.hi/index.md`
5. Summarise what was changed and what was skipped

### 6. No gaps found

If no gaps are identified, report:
> "No instruction improvements identified for this session."

---

## Constraints

- **Never** apply a proposal without explicit user confirmation.
- **Never** modify `.hi/conventions.md`, `.hi/maintenance.md`, `.hi/credentials.md`, or `.hi/environment.md` without strong justification — these are global canonical rules shared across all adopted projects.
- Prefer adding content to existing files over creating new `.hi/instruct.md` files.
