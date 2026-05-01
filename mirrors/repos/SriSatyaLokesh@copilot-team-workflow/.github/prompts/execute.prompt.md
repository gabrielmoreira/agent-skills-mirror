---
description: 'Use when executing an approved implementation plan — when a developer says "execute the plan", "start implementing", or "begin the tasks". Requires Phase 3 (Plan) to be complete. Offers choice between TDD agent execution or delegating to Copilot agent mode for heavy lifting, then returning to structured verification.'
tools: [execute, read, edit, search]
---
# Execute Implementation Plan

**Work folder**: ${input:work-folder:Path to work folder (e.g., work/ISSUE-042-name)}

## Step 1 — Load and Review Plan

Read `plan.md` from the work folder. Review Phase 3 critically:
- Are there gaps or ambiguities in any task?
- Are task dependencies clear?
- Are verification commands specified?

If concerns exist: raise them before starting. If clear: proceed.

## Step 1.5 — Pre-Flight Checks (Required)

Before any implementation work starts, confirm all of the following:
- Selected execution mode is explicit (A or B)
- If Mode A: agent mode has been reselected in the target chat
- Terminal tool access is available for test and git commands
- File editing tools are available for implementation updates

If any check fails, stop and resolve it before coding.

## Step 2 — Choose Execution Mode

Ask the developer to choose:

### **Mode A: Agent Mode (Recommended for complex features)**
Hand off to GitHub Copilot agent mode for implementation:
- ✅ Full context awareness
- ✅ Multi-file editing
- ✅ Natural TDD workflow
- ✅ Can ask clarifying questions
- ✅ Returns when done

After completion, you return to this flow for `/verify`.

### **Mode B: TDD Agent (For simple, structured tasks)**
Use the TDD Implementer agent:
- ✅ Strict TDD enforcement
- ✅ Batch-based commits
- ✅ Built-in code review checkpoints
- ✅ Automated progress tracking

---

## If Developer Chooses: Mode A (Agent Mode)

### Step 2A — Prepare Context Bundle

Create a comprehensive prompt for agent mode:

```markdown
# Implementation Task

**Work Folder**: ${input:work-folder}
**Branch**: [current branch from git branch --show-current]
**GitHub Issue**: [parse from work folder name if exists]

## Requirements (from plan.md Phase 1)
[paste Phase 1 requirements]

## Research Context (from plan.md Phase 2)
[paste Phase 2 findings - existing patterns, files to modify]

## Implementation Plan (from plan.md Phase 3)
[paste Phase 3 task breakdown]

## Your Task
Implement all tasks from Phase 3 using test-driven development:
- Write failing test first
- Implement minimal code to pass
- Refactor if needed
- Commit after each logical unit

## Quality Standards
- All tests must pass
- No TypeScript/lint errors
- Follow conventions in docs/codebase/conventions.md
- Update result.md Phase 4 as you work

## File Locations
- Plan: ${input:work-folder}/plan.md
- Results: ${input:work-folder}/result.md (update Phase 4 here)
- Code: [from research findings]

## When Complete
1. Update ${input:work-folder}/result.md Phase 4 with:
   - What was implemented
   - Any deviations from plan
   - All commits made
2. Run full test suite: `npm test`
3. Say: "Implementation complete. Ready for /verify"

## Start Here
[First task from Phase 3]
```

### Step 2B — Display and Hand Off

Show the bundled prompt to the developer and say:

> "📋 **Context bundle prepared for agent mode.**
>
> **Next steps:**
> 1. Open a **new chat** (Ctrl+L / Cmd+L)
> 2. Reselect **agent mode** in that chat
> 3. Paste the context bundle above
> 4. Confirm terminal + edit tools are available
> 5. Let agent mode implement everything
> 6. When it says "Ready for /verify", come back here and run `/verify ${input:work-folder}`
>
> **Why a new chat?** Keeps execution context clean. Agent mode works best in fresh sessions.
>
> **Alternative:** Copy the bundle and reply 'implement this' in agent mode directly."

**STOP HERE.** Wait for developer to complete implementation and return.

---

## If Developer Chooses: Mode B (TDD Agent)

### Step 2B — Hand off to TDD Implementer Agent

Invoke the **TDD Implementer agent** with:
```
@tdd ${input:work-folder}
```

The TDD agent will:
- Read the plan
- Verify you're not on main branch
- Execute tasks in TDD cycle (Red → Green → Refactor)
- Update result.md Phase 4
- Commit after each task
- Offer PR creation when done

---

## After Either Mode Completes

Run:
```bash
git status              # Check what changed
npm test               # Verify all tests pass
```

Then proceed to:
```
/verify ${input:work-folder}
```

The Verify agent will check requirements, test coverage, and code quality before offering to create/merge the PR.

---

## Why Two Modes?

| Feature | Agent Mode | TDD Agent |
|---------|-----------|-----------|
| **Best for** | Complex features, exploration | Well-defined tasks, learning TDD |
| **Context** | Full workspace awareness | Focused on plan |
| **Flexibility** | Can adapt mid-implementation | Strict TDD discipline |
| **Commits** | Developer decides | Automatic after each task |
| **Review** | At the end | Every 3 tasks |
| **Learning** | Production speed | TDD training |

**Recommendation**: Try **Agent Mode** for your first few issues. Once you understand the patterns, use **TDD Agent** for routine work where strict discipline is valuable.

---

## Troubleshooting

### "I chose Agent Mode but got stuck"
- Save your work: `git add . && git commit -m "WIP: partial implementation"`
- Come back and run `/verify` to see what's missing
- Or switch to TDD agent: `@tdd ${input:work-folder}` (it will continue from where you stopped)

### "Mode A started in the wrong mode"
- Open a fresh chat window
- Explicitly select agent mode before pasting the bundle
- Re-run pre-flight checks and continue

### "Agent Mode completed but I'm not sure what changed"
```bash
git diff HEAD~5  # See last 5 commits' changes
git log --oneline -10  # See commit history
```

### "TDD Agent is too slow"
- Switch to Agent Mode mid-stream (it's fine!)
- Agent Mode is faster for bulk implementation

---

## Next Steps

After execution completes (whichever mode you chose):
1. Ensure all tests pass: `npm test`
2. Update `result.md` Phase 4 if not already done
3. Run `/verify ${input:work-folder}` for quality gate
4. If verification passes → PR creation offered automatically
