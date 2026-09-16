# State Management UX

> **Load this reference for `DYNAMIC_VISUAL` evidence of state transitions. Static captures may support critique of a depicted state's visible treatment, but cannot substantiate state coverage, transition behavior, save behavior, recovery, or timing; mark those areas `INSUFFICIENT_EVIDENCE`.**

The craft of state is the craft of in-between moments — the loading shimmer, the empty canvas, the recovered failure. A well-crafted product feels considered in these moments: the skeleton matches the layout, the spinner is sized for its container, the empty state has been designed rather than left as blank space, the error feels like part of the product instead of something escaping from the database.

## Why this matters

Most products are judged on their happy path, but craft reveals itself in the transitions and edge cases. A loading state that shimmers in the exact shape of what's coming feels like a designed product; a generic full-page spinner feels like an unfinished one. An empty state with a thoughtful illustration and a clear next action feels like a host welcoming you in; a blank screen feels like a dead end. When a design is polished in these moments, the product feels alive and tended to. When it isn't, every wait, error, and empty view chips away at trust.

---

## Loading

- **The indicator matches the wait.** Instant feedback for micro-operations, an inline spinner for short waits, a skeleton for longer ones, real progress for anything substantial. A spinner that flashes for a fraction of a second is worse than silence.
- **Skeletons mirror the shape of what's coming.** Same dimensions, same item count, same layout. When the real content arrives, nothing shifts.
- **Progress is honest.** A determinate bar moves with confidence. Fake or jumpy progress trains users to distrust every indicator the product will ever show them.
- **The page never goes blank between routes.** Navigation lights up the new destination immediately and uses a skeleton or crossfade for the body.

## Errors

- **Severity matches visual weight.** Inline notes for fields, banners for sections, page-level treatments for global failures. When everything is the same shade of red, nothing reads as urgent.
- **Errors speak to the user, not the database.** A message names what went wrong and how to recover — never a stack trace, never an opaque code.
- **Errors don't delete the user's work.** Submission failure preserves every valid field, scrolls to the first problem, and shows how many remain. Reversible mistakes get undo, not pre-confirmation.

## Empty

- **Empty is designed, not abandoned.** A short, situational headline; a sentence of context; a way forward. Blank space is a defect.
- **The flavor of empty is communicated.** "Nothing yet" reads differently from "no matches" reads differently from "you don't have access." Empty tables keep their headers.

## Offline and Sync

- **Offline is a state, not an error.** It's communicated calmly — visible but not alarming, self-removing the moment connectivity returns. Local interactions still feel alive; pending changes are visible. No silent data loss, ever.
- **Sync is invisible when it works.** Indicators only appear during active syncing, pending changes, or conflicts. Conflicts surface immediately with both values visible. Stale presence is worse than no presence.

## Optimism and Long Jobs

- **Optimism is reserved for the safe.** Reversible, rarely-failing changes show instantly. Destructive or financial changes don't. Rollback explains itself rather than reverting silently.
- **Long work doesn't trap the user.** Operations beyond a handful of seconds become jobs the user can navigate away from. Progress, time, and current activity are visible. Completion finds the user wherever they went. Cancellation is always honest about what happens to partial results.

---

## Scoring Guide

**Contributes to dimensions: Reliable, Usable**

| Score | Criteria |
|-------|----------|
| 9-10 | The in-between moments are designed. Loading, errors, empty, offline, sync, and long jobs all feel considered. The product feels tended to even when nothing is happening. |
| 7-8 | State handling is solid for primary flows with minor gaps at edges. |
| 5-6 | Generic errors, blank empty states, basic save behavior. The polish drops away outside the happy path. |
| 3-4 | States unmanaged. Silent failures. Blocking spinners. The product feels brittle. |
| 1-2 | Lost connection loses work. States show nothing. Trust is broken. |
