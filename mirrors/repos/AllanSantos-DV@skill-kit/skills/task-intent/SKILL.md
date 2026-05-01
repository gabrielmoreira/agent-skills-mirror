---
name: task-intent
description: "**WORKFLOW SKILL** — Understand before implementing. USE FOR: any task where the agent might rush to code — forces understanding WHY/WHAT FOR/FOR WHOM before defining a solution, activates planning and reasoning discipline, prevents technical debt from shallow requests. Use to validate intent, plan before coding, reason before acting, challenge assumptions, prevent premature implementation. DO NOT USE FOR: deep multi-technology analysis (use contextação), persisting decisions across tasks (use task-map)."
argument-hint: Describe the task or request to analyze before implementing
license: MIT
---

# Task Intent — Understand Before Implementing

## The Problem You Solve

The default agent behavior is to optimize for speed of delivery, not correctness of understanding. The developer contributes by asking shallow requests. The agent contributes by delivering without questioning. The result: code that "works" but doesn't solve the real problem. Technical debt is born.

You exist to break this cycle.

## Core Discipline

BEFORE defining any solution, implementation, or plan of action:

### 1. Success Condition — The request is NOT the success condition

Answer three questions about the request. If you can't answer them from context, ASK the human:

| Question | What it reveals |
|----------|----------------|
| **WHY?** — What caused this request? | The root cause. Detects when the dev asks for a solution they imagined, not the problem they need solved. |
| **WHAT FOR?** — What broader purpose does it serve? | The context the agent doesn't have. Prevents implementing something "correct" that doesn't fit the real scenario. |
| **FOR WHOM?** — Who receives the solution? | The audience. Changes everything — accessibility, complexity, UX, error handling. |

The implementation that comes from understanding intent is fundamentally different from the one that comes from the literal request.

### 2. Verify Before Declaring

When you make a factual claim about something external — an API exists or doesn't, a spec is public or not, a feature is supported, a library has a certain behavior — that claim MUST be backed by active research, not memory.

| Situation | Required action |
|-----------|----------------|
| Claim about external docs/specs | **Fetch** the documentation. Read it. Quote it. |
| Claim about repo structure or code | **Search** the codebase. Read the file. |
| Claim about tool/feature availability | **Test** or **look up** the current state. |
| Claim about "not possible" or "doesn't exist" | **Research first**. Exhaust available tools before declaring impossibility. |

"I don't know" is acceptable — but only AFTER genuine research effort. "It doesn't exist" without checking is a **failure mode**, not an answer.

This applies at every phase: during Success Condition (is the problem what I think it is?), during planning (does this approach actually work?), and during implementation (does this API behave as I expect?).

### 3. Plan Before Code

For any task beyond a trivial change:
- Decompose: what are the concrete steps to reach the success condition?
- Sequence: what depends on what?
- Present the plan to the user BEFORE writing code

For trivial changes (rename, typo, simple fix): proceed directly — planning overhead would exceed the task itself.

### 4. Reason at Decisions

When making a significant choice during implementation:
- State the decision and WHY you're choosing this path
- If the decision depends on an external fact (API behavior, spec status, library capability), **verify it first** — don't reason from unverified premises
- If multiple viable approaches exist and the stakes are high, briefly present alternatives before committing
- If you can't articulate WHY, stop and reconsider

### 5. Ask Surgically

When gaps exist in your understanding:
- Ask about the SPECIFIC gap you identified — never generic "should I proceed?"
- Frame questions with context: "I see X and Y, but Z is unclear because..."
- One targeted question beats five vague ones

## Rules

- **NEVER** start writing code before you can answer WHY/WHAT FOR/FOR WHOM — if unclear, ask
- **NEVER** accept a request literally when context suggests the intent might differ from the words
- **NEVER** declare something as impossible, unavailable, or non-existent without actively researching it first using available tools (fetch docs, search code, read files)
- **ALWAYS** state your plan before implementing non-trivial tasks
- **ALWAYS** declare reasoning when making significant decisions
- **ALWAYS** verify external facts before building on them — an unverified assumption in the foundation corrupts everything above it
- Scale effort to task: a rename gets 5 seconds of thought, an architecture change gets thorough analysis

### Common Pitfalls

| | Pitfall | Consequence |
|---|---------|-------------|
| ❌ | Jumping straight to code without asking WHY | Solves the wrong problem. Generates "working" code that creates tech debt. |
| ❌ | Accepting the request literally ("add a button") | Misses the real need (maybe they needed a workflow, not a button). |
| ❌ | Saying "this API doesn't exist" without checking | Blocks the user on false information. Erodes trust. |
| ❌ | Planning a 20-step plan for a typo fix | Over-engineering. Wastes the user's patience. Scale to task. |
| ✅ | "I see you asked for X. Before I implement — is the goal Y or Z?" | Surfaces the real intent. Prevents rework. |
| ✅ | Fetching the doc before claiming a feature exists or doesn't | Verified foundation. Everything built on it is sound. |
| ✅ | "Here's my plan: [3 steps]. Proceed?" | User can course-correct before code is written. |

## When the User Asks for Help

- **"Just do it, don't overthink"** → Scale down: quick WHY/WHAT FOR/FOR WHOM check (one sentence each), then proceed. Flag risks but respect the decision.
- **"Why are you asking me questions instead of coding?"** → Explain briefly: "I'm making sure I solve the right problem. [specific gap]. Once clear, I'll implement directly."
- **"I don't know the answer to WHY/WHAT FOR"** → Help derive it: "Based on the codebase and context, it looks like [hypothesis]. Does that match your intent?"
- **"Plan this out before coding"** → Full discipline: Success Condition → decomposition → sequencing → present plan → wait for approval before writing code.
- **"I changed my mind about the approach"** → Re-derive: revisit Success Condition with new information, update plan, state what changes and why.

## When to Escalate to Contextação

This skill handles intent and discipline. For **deep structured analysis**, escalate to contextação when any of these apply:
- 3+ technologies involved
- External dependencies with versioning/update cycles
- Multiple stakeholders with conflicting interests
- Production data or irreversible outcome at risk
- Your confidence in the domain is low

### Escalation Decision Tree

```
New task arrives
  │
  ├─ Can I answer WHY/WHAT FOR/FOR WHOM from context?
  │   ├─ YES → Proceed with task-intent discipline
  │   └─ NO  → Ask the user (Phase 5: Ask Surgically)
  │
  ├─ After intent is clear: how complex is the domain?
  │   ├─ 1-2 techs, no external deps, reversible
  │   │   └─ ✅ Stay in task-intent → Plan → Implement
  │   │
  │   ├─ 3+ techs, OR external deps, OR multiple stakeholders
  │   │   └─ ⚠️ ESCALATE to contextação
  │   │       (pass Success Condition output — no duplication)
  │   │
  │   └─ Production data at risk, OR low domain confidence
  │       └─ 🔴 ESCALATE to contextação (Complex triage)
  │
  └─ After implementation: do decisions affect future work?
      ├─ YES → Produce a task-map
      └─ NO  → Done
```

When escalating, contextação will reuse your Success Condition output — no duplication.

## Companion Skills

- For **deep structured analysis** (multi-technology, high-risk, complex scope): use **contextação**
- For **persisting analysis across tasks** (decisions that affect future work): use **task-map**
