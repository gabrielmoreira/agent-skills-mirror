# LLM Behavior Guidelines

Behavioral guardrails to prevent systematic agent anti-patterns in multi-agent workflows. Derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, adapted for ControlFlow's delegation-chain context.

**Tradeoff:** These guidelines bias toward caution over speed. For TRIVIAL-tier tasks, use judgment — not every task needs full clarification rituals.

## Applicable Agents

| Agent | Principles to Apply |
| ----- | ------------------- |
| CoreImplementer-subagent | All 4 |
| UIImplementer-subagent | All 4 |
| CodeReviewer-subagent | Simplicity First, Surgical Changes (audit focus) |
| Planner | Think Before Coding, Goal-Driven Execution |
| PlatformEngineer-subagent | Think Before Coding, Surgical Changes |
| TechnicalWriter-subagent | Surgical Changes |

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.** Before any non-trivial task:

- State assumptions explicitly; if uncertain, ask via `NEEDS_INPUT`.
- If multiple valid interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so and push back when warranted.
- If genuinely unclear, stop, name what's confusing, return `NEEDS_INPUT` with a `clarification_request`.

**ControlFlow context:** Silent subagent assumptions propagate invisibly up the delegation chain — an incorrect one in CoreImplementer becomes a CodeReviewer blocker and forces an expensive replan. Surface it early. Example: "Add an endpoint to export reports" → ❌ silently assume JSON/all-records/no-pagination/authed-only and write 200 lines; ✅ clarify format, scope (performance risk), and auth, state simplest interpretation (paginated JSON with auth guard), return `NEEDS_INPUT` if intent differs.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was explicitly asked; no abstractions for single-use paths.
- No "flexibility"/"configurability" that was not requested.
- No error handling for scenarios that cannot happen given system constraints.
- If an implementation is 200 lines and could be 50, rewrite it.

**The test:** Would a senior engineer call this overcomplicated? If yes, simplify.

**ControlFlow context:** Over-engineering raises CodeReviewer's `validated_blocking_issues` and triggers rewrites; bloated scope is flagged by PreFlect. Complexity "for future use" is unprovable and untestable — a liability. Example: "save the user's theme preference" → ❌ a 120-line `PreferenceManager(db, cache, validator, event_bus)`; ✅ `db.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))`, adding cache/validation/events only when explicit and tested.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.** When editing existing files:

- Don't "improve" adjacent code/comments/formatting; don't refactor things that aren't broken.
- Match existing style even if you'd do it differently.
- Unrelated dead code → **mention it in the execution report**, do not delete.
- Remove only orphans (unused imports/vars/functions) that YOUR changes made dead; never pre-existing dead code unless explicitly asked.

**The test:** Every changed line traces directly to the delegated task scope.

**ControlFlow context:** CodeReviewer's `validated_blocking_issues` flags out-of-scope modifications; orthogonal changes contaminate the diff and can break sibling phases in parallel waves. Example: "Fix null check in `processOrder()`" → ❌ also reformat 3 functions, rename a parameter, delete an "obviously dead" helper; ✅ fix the null check, then report "Observed potentially unused helper `formatOrderLegacy()` — recommend a cleanup task if confirmed dead."

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.** Transform imperative descriptions into verifiable goals:

| Instead of... | Transform to... |
| ------------ | --------------- |
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure all existing tests pass before and after" |
| "Add the feature" | "Define acceptance criteria, write tests, implement" |

For multi-step phases, state a brief plan as `[Step] → verify: [check]` lines. Strong criteria let the agent loop independently; weak criteria ("make it work") guarantee back-and-forth.

**ControlFlow context:** Planner phase `tasks` follow the `[Step] → verify: [check]` pattern. Orchestrator's Phase Verification Checklist (tests, build, lint, review APPROVED) is the final gate — goal-driven execution ensures phases arrive passing rather than via multiple revision loops. Example: ❌ "Improve the authentication flow" (no measurable criterion); ✅ "Add JWT expiry validation to `AuthMiddleware` → verify: `npm test auth` passes with a new test case for expired tokens."

## 5. Prompt Compression Anti-Pattern Lexicon

Bounded list of anti-patterns that waste context tokens in agent files; avoid when writing/updating prompts:

- **Filler opt-in closers:** conversational endings ("Let me know if you want me to proceed"). *Instead: end with a structural command like "Emits: [schema name]".*
- **Duplicated routing tables:** re-stating tier-to-pipeline mappings or retry values in markdown. *Instead: reference `governance/runtime-policy.json` as source of truth.*
- **Long inline restatements of shared policy:** copying whole spec sections (e.g., semantic risk taxonomy) into a subagent. *Instead: reference `plans/project-context.md` or `.github/copilot-instructions.md` by name and section.*

## Anti-Rationalization Table (Canonical)

Shared contract for recurring rationalizations in ControlFlow skills. Skill-local sections keep only role-specific deltas and point here for the generic rule.

| Pattern | Required Action |
| ------- | --------------- |
| Assume the missing requirement because the likely answer is obvious | Surface the assumption or return `NEEDS_INPUT` when it changes scope, behavior, or file set. |
| Add an abstraction because future tasks might need it | Build only the requested behavior; record future options outside the implementation. |
| Clean up adjacent code while editing nearby lines | Limit changes to delegated scope and report unrelated observations. |
| Skip verification because the edit seems low-risk | Run the smallest relevant gate plus any suite required for the phase. |

## Summary Decision Table

| Situation | Action |
| --------- | ------ |
| Multiple valid task interpretations | Present options, return `NEEDS_INPUT` |
| Tempted to add untasked feature | Don't. Note it in execution report instead |
| Noticed adjacent code smell | Note in execution report; don't touch it |
| Task description has no verify criterion | Derive one; state it explicitly before implementation |
| Implementation exceeds ~3x expected size | Stop, surface as `NEEDS_INPUT` with simpler alternative |
