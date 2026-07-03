# Acceptance Criteria That Actually Gate

ACs exist to make "done" a fact instead of a negotiation. The craft is writing them so a tester, a developer, and a PM read the same words and expect the same behaviour.

## The form that works

**Given / When / Then** for behaviour; checklists for constraints. One observable behaviour per criterion:

- ✅ "Given an expired card, when the user submits payment, then the form shows 'card expired' inline and preserves the cart"
- ❌ "Handle payment errors gracefully" (which errors? shown where? what's preserved?)

## The four criteria your criteria must meet

1. **Observable** — a human or test can watch it happen. "The system validates input" is invisible; "submitting >500 chars shows a count error" is watchable.
2. **Bounded** — numbers where numbers exist: how many, how fast, which locales, what limit.
3. **Includes the unhappy path** — every story has at least one failure/edge criterion (empty state, timeout, permission-denied, duplicate submit). Happy-path-only ACs are where production bugs are scheduled.
4. **Independent of implementation** — "clicking Save calls POST /v2/items" breaks when engineering refactors; "a saved item survives page reload" doesn't.

## Calibrating the count

3-7 ACs per story. One or two → probably a task, or under-specified. Ten+ → the story is an epic wearing a trench coat; split along the AC clusters (they usually reveal the seams).

## Traps

- **The compound criterion** — "user can filter AND sort AND export" is three; failures hide in the AND
- **The adjective criterion** — "fast", "intuitive", "clean" gate nothing; replace with a number or a named reference ("matches the pattern on /settings")
- **The tautology** — "feature works as designed" (against what design? then link it)
- **ACs written after the code** — those describe what was built, not what was needed; the gate faces backwards
