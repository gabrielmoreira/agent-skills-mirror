---
name: agent-orchestration-improve-agent
version: 2.0.1
description: "Diagnoses and tightens an existing Claude subagent markdown file under `.claude/agents/` from concrete failure transcripts: trigger description, tool list, and output contract. Use when a named subagent drifts, calls the wrong tools, or produces off-task output. Not for authoring a brand-new agent or a Cursor SKILL.md. Do not use to edit Claude's own system prompt or when no failure examples exist."
risk: safe
source: local
date_added: 2026-06-16
---

# Improve an Existing Agent

Use when an agent (subagent definition under `.claude/agents/` or `~/.claude/agents/`) is misbehaving, drifting, or could be tighter. The workflow is: gather evidence → diagnose → edit the prompt → verify → ship.

## When to Use

Trigger this skill when any of the following are true:

- An agent is producing wrong, verbose, or off-task output.
- An agent is calling the wrong tools, or too many of them.
- The agent's `description` triggers the wrong tasks (or doesn't trigger at all).
- You want to tighten scope, add examples, or fix a recurring failure.

## Do Not Use

- Creating a brand-new agent — use the agent-creation skill instead.
- Editing the system prompt of Claude itself.
- You have no concrete examples of the failure — gather them first.

## Prerequisites

Before editing the agent file, collect all of the following. If any are missing, stop and gather them before proceeding.

1. **The agent file** — path to the `.md` under `.claude/agents/` or `~/.claude/agents/`.
2. **At least 2–3 concrete failures** — transcripts, prompts, or outputs showing the problem.
3. **Expected behavior** — what *should* have happened in those cases.
4. **Scope check** — is the agent being invoked for tasks it shouldn't handle, or vice versa?

> Editing prompts blind produces churn. Do not skip the evidence-gathering step.

## Procedure

### Step 1: Read the current agent

```powershell
# From the project root (Windows / PowerShell)
Get-Content .claude\agents\<name>.md
```

Or for a user-level agent:

```powershell
Get-Content $HOME\.claude\agents\<name>.md
```

Note the existing structure: frontmatter (`name`, `description`, `tools`), system prompt body, any examples or constraints.

### Step 2: Diagnose

Map each failure to a root cause. Common patterns:

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent triggers on wrong tasks | `description` too broad or vague | Tighten description; add explicit "do not use" cases |
| Agent skips tasks it should handle | `description` too narrow or missing trigger keywords | Add example triggers to description |
| Wrong tool calls | `tools:` list too permissive, or prompt doesn't guide tool choice | Restrict tool list; add tool-selection guidance |
| Verbose / off-format output | No output format specified | Add explicit output contract with example |
| Hallucinated file paths or APIs | Prompt encourages guessing | Add "verify before recommending" instruction |
| Drifts mid-task | No checkpoint / no stop condition | Add explicit completion criteria |

### Step 3: Edit the prompt

Make the **smallest** change that fixes the observed failures. Avoid sweeping rewrites.

Patterns that work:

1. **Tighten `description`** — include 2–3 example user phrases that should trigger it, and 1–2 that should not.
2. **Add a "Do not" section** — explicit anti-patterns are more effective than aspirational instructions.
3. **Add a worked example** — input → expected output, in the exact format you want.
4. **Restrict tools** — remove any tool the agent doesn't need; fewer options = less drift.
5. **Specify output shape** — bullet list / JSON / sectioned report — pick one and show it.

Anti-patterns to avoid in the edit:

- Adding "be careful" or "make sure" without saying *what* to check.
- Long preambles about the agent's role — Claude already knows it's an assistant.
- Vague metrics ("high quality", "accurate") — replace with concrete checks.

### Step 4: Verify

Re-run the agent on the original failure cases. For each case:

- Does it now produce the expected behavior?
- Did the change regress any previously-working case? Run 1–2 known-good cases too.

If you can't reproduce the original failures interactively, write the test inputs into a scratch file and run the agent against them one at a time.

### Step 5: Commit

If the agent file lives in a git repo, commit with a message that names the symptom fixed:

```powershell
git add .claude\agents\<name>.md
git commit -m "tighten reviewer agent description to skip docs-only diffs"
```

No commit if the file is in `~/.claude/agents/` and not tracked.

## Pitfalls

- **Editing without evidence.** Without real failure examples, this skill produces guesses. Always gather 2–3 concrete failures first.
- **Sweeping rewrites.** Large prompt rewrites introduce regressions. Make the smallest change that fixes the observed failure.
- **Vague instructions.** "Be careful" and "make sure" without specifying *what* to check are no-ops. Replace with concrete, checkable instructions.
- **Over-permissive tool lists.** Extra tools cause drift. Remove any tool the agent doesn't need.
- **Model limitations vs. prompt issues.** Prompt edits don't fix model limitations — if the failure is the model misreading clear instructions, a model swap may help more than a prompt tweak.
- **Expectation mismatch.** Some "failures" are actually user expectations the agent was never designed to meet. Widening scope is a design decision, not a bug fix.

## Verification

Confirm the improvement is complete by checking each item:

1. **Failure cases resolved** — re-run the agent on each original failure input and confirm it now produces the expected behavior.
2. **No regressions** — run 1–2 previously-working cases and confirm they still pass.
3. **Diff reviewed** — the change to the agent file is the smallest possible and targets the diagnosed root cause.
4. **Committed (if applicable)** — the agent file is committed with a message naming the symptom fixed.

### Output contract

When invoked, this skill should produce:

1. A summary of failures found and their root cause.
2. A diff (or before/after snippet) of the agent prompt.
3. Verification results on the original failure cases.
4. Any remaining concerns or follow-ups.

## Limitations

- Prompt edits don't fix model limitations — if the failure is the model misreading clear instructions, a smaller/larger model swap may help more than a prompt tweak.
- Without real failure examples, this skill produces guesses.
- Some "failures" are actually user expectations the agent was never designed to meet; widening scope is a design decision, not a bug fix.

## Related Skills

- **Agent creation** — for building a brand-new subagent from scratch rather than improving an existing one.
