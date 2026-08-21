---
name: better
description: >-
  Quality upgrade pass on the current deliverable: scorecard, improve, review,
  verify with fresh evidence. Use when the user runs /better, /better deep,
  /better ship, /better <focus>, or asks to polish, harden, upgrade quality,
  or review-and-verify without adding features. Not for new scope. Not /scale
  (that is quality-at-scale). Not /reviewresults (that is review-results / sensory proof).
---

# /better — Quality upgrade pass

**Slash:** `/better` (optional project command file)  
**Templates:** [reference.md](reference.md)

Improve the **current deliverable**. Review and verify along the way. Do not claim done without fresh evidence.

Say once: **“Running /better.”** Name the deliverable before editing.

## Modes

| Invocation | Behavior |
|------------|----------|
| `/better` | Scorecard → improve → review → verify |
| `/better deep` | Extra review wave, edge cases, second improve pass |
| `/better ship` | Ship bar: tests + typecheck + Bugbot (+ security when relevant) |
| `/better <focus>` | Narrow (`ui`, `api`, `tests`, `perf`, `a11y`, `copy`, …) |

## Hard contract

1. **Scope lock** — name the deliverable before editing.
2. **Baseline** — diff / screenshot / failing checks. Know what “before” was.
3. **Scorecard** — rank gaps; fix highest impact first (see reference).
4. **Resource fan-out** — load only what this pass needs: `deslop`, `verify-this`, `check-compiler-errors`, `control-ui`, Bugbot, Security Review, smoke tests. Swarm when independent slices exist; parent owns verify.
5. **Review mid-flight** — re-read / re-diff after change clusters.
6. **Verify with evidence** — typecheck, tests, screenshots, or a falsifiable `verify-this` verdict.
7. **No fake done** — report `BETTER: improved | partial | blocked`.
8. **Paid gate** — ask before paid models/APIs.
9. **No scope creep** — quality ≠ new features. No commit/push unless asked.

## Procedure

```
BETTER Progress:
- [ ] 0. Deliverable named + baseline captured
- [ ] 1. Scorecard ranked
- [ ] 2. Highest-impact fixes applied
- [ ] 3. Mid-flight re-read / re-diff
- [ ] 4. Verify (project path + extra bar if /better ship)
- [ ] 5. Report BETTER: improved | partial | blocked
```

### 0. Name and baseline

One sentence: what artifact, what “better” means for *this* pass. Capture the before state (diff, failing test, screenshot path). If there is no deliverable yet, stop — this is not `/goal` (no contract) and not greenfield build.

### 1. Scorecard

Rank 3–7 gaps. Fix top impact first. Do not polish P3 while P0 is open. Use the table in [reference.md](reference.md).

### 2. Improve

Smallest diff that moves the top gaps. Match the file. No drive-by refactors. `deslop` when the gap is mush.

### 3. Review

Re-read the changed region. Re-diff. If `/better deep`, do a second wave on edge cases. If `/better ship`, run Bugbot (and security-review when the change is auth, money, secrets, or user data).

### 4. Verify

Run the **project’s** verify path. Report exit codes verbatim. Sensory / UI: `/reviewresults` (`review-results`). A problem-fit pass is not proof.

### 5. Report

```
BETTER: improved | partial | blocked
Deliverable: <name>
Changed: <paths>
Verified: <commands + exit codes>
Remaining: <what still fails the scorecard>
```

## Compose

| Need | Command / skill |
|------|-----------------|
| Outcome contract | `/goal` (`goal` skill) |
| Autonomous until criteria | `/goal-loop` (mode of `goal`) |
| Parallel workers | `/swarm` — parent owns verify |
| Many unique items | `/scale` (`quality-at-scale`) |
| Sensory proof | `/reviewresults` (`review-results`) |

## Must not

- New features dressed as polish
- Fake done (“looks better”) with no baseline or verify
- Growing always-on skills or dumping the catalog
- Commit/push unless the user asked
- Skipping `/reviewresults` on user-facing / sensory because this pass “felt thorough”
- Using `/better` as a substitute for `/goal` when success criteria do not exist
