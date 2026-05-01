# Idea-to-Prompt Patterns

## Purpose
Transform a vague or abstract user idea into a concrete, structured planning prompt that Planner (or Orchestrator) can decompose into an execution-ready plan.

## Trigger Detection

Apply this protocol when the user request shows **all three** of:
1. No specific file names or paths mentioned.
2. No concrete acceptance criteria ("done when X is verified").
3. No explicit technology or constraint named.

Examples of triggering signals: "make it smarter", "improve the pipeline", "add better support for X", "can we do something about Y".

Do NOT trigger if the request contains any concrete signal — a file path, an agent name, a schema reference, or a measurable goal.

## Step-by-Step Interview Protocol

### Step 1 — Idea Decomposition
Use `vscode/askQuestions` to identify the core intent:
- "What is the main problem you want to solve?"
- Options: A) Performance/speed, B) Quality/reliability, C) Developer experience, D) New capability.
- Record: core intent, primary stakeholder (user/developer/system), and what success looks like in one sentence.

### Step 2 — Constraint Discovery
Ask about the execution environment:
- "Which part of the system does this touch?" — options drawn from the known agent/file structure.
- "Are there hard constraints?" — e.g., no file renames, VS Code platform only, additive-only changes.
- Record: affected subsystem, non-negotiable constraints.

### Step 3 — Scope Boundary Mapping
Ask what is explicitly out of scope:
- "What should NOT change as a result of this work?"
- Record: explicit exclusions. These become Scope OUT items.

### Step 4 — Risk Surface Identification
Ask one targeted risk question:
- "What could go wrong or surprise us?" — options: A) Breaking existing behavior, B) Token overhead increase, C) Validation failures, D) Other.
- Record: known unknowns and dependencies.

### Step 5 — Structured Prompt Assembly
Combine interview answers into a planning prompt with these sections:

```
**Objective:** <core intent from Step 1>

**Constraints:**
- <constraint 1 from Step 2>
- <constraint 2>

**Scope IN:** <subsystem / files / behaviors to change>
**Scope OUT:** <explicit exclusions from Step 3>

**Success Criteria:**
- <measurable criterion 1>
- <measurable criterion 2>

**Known Risks:** <findings from Step 4>

**Preferred Approach (if any):** <user preference if stated>
```

Replace the original vague request with this structured prompt for all subsequent Planner workflow steps.

## Output Contract
After Step 5, the assembled prompt feeds directly into Step 0 (Clarification Gate) as the new working request. The idea interview does not produce a plan file itself.
