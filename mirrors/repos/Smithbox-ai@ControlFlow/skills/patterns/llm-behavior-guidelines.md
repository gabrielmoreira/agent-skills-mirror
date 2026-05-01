# LLM Behavior Guidelines

Behavioral guardrails to prevent systematic agent anti-patterns in multi-agent workflows. Derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, adapted for ControlFlow's delegation-chain context.

**Tradeoff:** These guidelines bias toward caution over speed. For TRIVIAL-tier tasks, use judgment — not every task needs full clarification rituals.

## Applicable Agents

| Agent | Principles to Apply |
|-------|-------------------|
| CoreImplementer-subagent | All 4 |
| UIImplementer-subagent | All 4 |
| CodeReviewer-subagent | Simplicity First, Surgical Changes (audit focus) |
| Planner | Think Before Coding, Goal-Driven Execution |
| PlatformEngineer-subagent | Think Before Coding, Surgical Changes |
| TechnicalWriter-subagent | Surgical Changes |

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing any non-trivial task:
- State your assumptions explicitly. If uncertain, ask via `NEEDS_INPUT`.
- If multiple valid interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so and push back when warranted.
- If something is genuinely unclear, stop. Name what's confusing. Return `NEEDS_INPUT` with a `clarification_request`.

**In ControlFlow context:** Assumptions made silently by a subagent propagate invisibly up the delegation chain. An incorrect assumption in CoreImplementer becomes a blocker in CodeReviewer and forces an expensive replan. Surface it early.

### ❌ Anti-pattern: Silent assumption

> Task: "Add an endpoint to export reports"

Agent silently assumes: JSON format, all records, no pagination, authenticated users only — and implements 200 lines without surfacing any of these decisions.

### ✅ Correct behavior

```
Before implementing, I need to clarify:
1. Format: JSON, CSV, or caller's choice? (affects schema)
2. Scope: All records or filtered? (affects performance risk — see data_volume)
3. Auth: Public endpoint or requires token?

Simplest interpretation: paginated JSON with auth guard.
Returning NEEDS_INPUT if the above differs from intent.
```

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was explicitly asked.
- No abstractions for single-use code paths.
- No "flexibility" or "configurability" that was not requested.
- No error handling for scenarios that cannot happen given the system's constraints.
- If an implementation is 200 lines and could be 50, rewrite it.

**The test:** Would a senior engineer say this is overcomplicated? If yes, simplify.

**In ControlFlow context:** Over-engineered implementations increase CodeReviewer's `validated_blocking_issues` count and trigger rewrites. Bloated scope causes scope drift flagged by PreFlect. Complexity added "for future use" is unprovable and untestable — it's a liability, not an asset.

### ❌ Anti-pattern: Speculative abstraction

```python
# Requested: "save the user's theme preference"
class PreferenceManager:
    def __init__(self, db, cache=None, validator=None, event_bus=None):
        # 120 lines of pluggable infrastructure for a single column update
```

### ✅ Correct behavior

```python
# Minimum code that solves the problem
def save_theme(user_id: int, theme: str) -> None:
    db.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
```

Add cache, validation, and events only when those requirements are explicit and tested.

---

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing files:
- Do not "improve" adjacent code, comments, or formatting.
- Do not refactor things that aren't broken.
- Match existing style — even if you'd do it differently.
- If you notice unrelated dead code, **mention it in the execution report** — do not delete it.

When your changes create orphans (unused imports, variables, functions YOUR changes made dead):
- Remove only the orphans your changes created.
- Do not remove pre-existing dead code unless explicitly asked.

**The test:** Every changed line should trace directly to the delegated task scope.

**In ControlFlow context:** CodeReviewer's `validated_blocking_issues` explicitly flags out-of-scope modifications. Orthogonal changes contaminate the diff, make code review harder, and can break sibling phases in parallel wave execution.

### ❌ Anti-pattern: Scope drift

> Task: "Fix null check in `processOrder()`"

Agent fixes the null check **and** reformats 3 functions, renames a parameter, and removes an "obviously dead" helper — none of which were in scope.

### ✅ Correct behavior

Fix the null check. In the execution report note: "Observed potentially unused helper `formatOrderLegacy()` in the same file — recommend a cleanup task if confirmed dead."

---

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform imperative task descriptions into verifiable goals before starting work:

| Instead of... | Transform to... |
|--------------|-----------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure all existing tests pass before and after" |
| "Add the feature" | "Define the acceptance criteria, write tests, implement" |

For multi-step phases, state a brief plan with explicit verification:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria allow the agent to loop independently without constant clarification. Weak criteria ("make it work") guarantee back-and-forth.

**In ControlFlow context:** Planner's phase `tasks` should follow this `[Step] → verify: [check]` pattern. Orchestrator's Phase Verification Checklist (tests pass, build passes, lint clean, review APPROVED) is the final gate — goal-driven execution ensures phases arrive at that gate in a passing state rather than requiring multiple revision loops.

### ❌ Anti-pattern: Unverifiable task definition

> Phase task: "Improve the authentication flow"

No measurable criterion. The agent cannot determine when it is done, and CodeReviewer cannot evaluate completion.

### ✅ Correct behavior

> Phase task: "Add JWT expiry validation to `AuthMiddleware` → verify: `npm test auth` passes with a new test case for expired tokens"

## 5. Prompt Compression Anti-Pattern Lexicon

A bounded list of specific anti-patterns that waste context tokens in agent files. When writing or updating prompts, avoid these:

- **Filler opt-in closers:** Ending prompts with conversational filler (e.g., "Let me know if you want me to proceed" or "Are you ready?"). *Instead: End with a clear structural command like "Emits: [schema name]" or stop after output rules.*
- **Duplicated routing tables:** Re-stating tier-to-pipeline mappings or retry values directly in an agent's markdown. *Instead: Reference `governance/runtime-policy.json` as the source of truth for routing and budgets.*
- **Long inline restatements of shared policy:** Copying entire sections of shared specs (like the semantic risk taxonomy) into a subagent's rules. *Instead: Reference `plans/project-context.md` or `.github/copilot-instructions.md` by explicit name and section.*

---

## Summary Decision Table

| Situation | Action |
|-----------|--------|
| Multiple valid task interpretations | Present options, return `NEEDS_INPUT` |
| Tempted to add untasked feature | Don't. Note it in execution report instead |
| Noticed adjacent code smell | Note in execution report; don't touch it |
| Task description has no verify criterion | Derive one; state it explicitly before implementation |
| Implementation exceeds ~3x expected size | Stop, surface as `NEEDS_INPUT` with simpler alternative |
