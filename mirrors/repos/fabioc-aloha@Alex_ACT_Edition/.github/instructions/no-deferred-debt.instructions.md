---
type: instruction
lifecycle: provisional
inheritance: inheritable
description: "When you spot tech debt, stale references, or outdated content — fix it in the same turn. Do not defer."
application: "Whenever an action surfaces stale references, dead links, outdated counts, dead-letter code paths, or any inconsistency between the brain's stated facts and reality"
applyTo: "**"
currency: 2026-05-24
lastReviewed: 2026-05-24
---

# No Deferred Debt

If a turn surfaces tech debt — stale references, dead links, outdated content, dead-letter prompts, hardcoded names that no longer exist — fix it in the same turn. Do not log it as "non-blocking" or "follow-up workstream." The cheapest moment to fix the debt is the moment it surfaced.

## Rule

When any of the following appears in a turn's output:

- A `grep`/`Select-String` surfaces references to artifacts I just deleted
- A regen reveals stale counts in a manifest
- A file lookup returns a path that no longer exists
- A doc enumerates skills/instructions/prompts that are gone
- A script hardcodes names I just renamed or removed
- A link in a markdown file points to something that 404s locally
- A `description` or `applyTo` references concepts no longer in the brain

**Fix it before declaring the turn done.** Do not write "non-blocking, deferred to next pass" unless the debt is genuinely architectural and requires its own decision cycle (in which case open an explicit decision artifact — ADR draft, proposal, or HANDOFF entry naming the *specific* decision the deferral is waiting on).

"I'll fix it in the next session" is not an acceptable reason. The context is already loaded. The diff is already small. The reviewer is already in the file.

## When deferral IS legitimate

| Deferral reason | Acceptable? |
|---|---|
| "Not in scope of this turn" | No — if I spotted it, it's in scope now |
| "Needs user decision" | Yes — but write the specific question in HANDOFF.md or a proposal, don't just leave the debt |
| "Requires architectural redesign" | Yes — open ADR draft naming the question, don't leave a silent broken state |
| "Would take more than 10 minutes" | Borderline — if it's mechanical, do it; if genuinely complex, name the deferral concretely with timeline |
| "Documentation update only" | No — docs that lie are debt |
| "Test data" | No — test data with dead refs makes tests untrustworthy |

## Anti-patterns

| Came out | Correction |
|---|---|
| "Known tech debt (non-blocking, deferred)" with no decision-blocker named | Either fix it or name the specific decision waiting |
| "Will clean in next scripts-hygiene pass" | The pass is now |
| "Stale data ref but tests still pass" | Tests passing on stale data is the worst signal — the assertion has lost meaning |
| Logging debt in commit message and shipping the broken state | The commit message names the debt; the next commit pays it. Don't ship debt with attribution. |
| Spotting a broken link mid-task and skipping past it because "different task" | Same task. The link is now your responsibility because you saw it. |

## Trigger origin

Codified 2026-05-24 after prune sessions left "non-blocking deferred" notes in commit messages for stale hardcoded skill names in scripts (`reset-heirs.cjs`, `measure-combo-tokens.cjs`, `test-edition-applyto-coverage.cjs`-class files). User pushback: *"When you spot tech debt or outdated content, links, fix it immediately. Do not defer."* The first commit applying this rule also pays those specific debts. Lifted from Alyva_Master heir-side discipline and adopted as Supervisor + Edition always-on per FOUR-REPOS-COMPARISON.md Tier A §0.1 row 3.

## Relation to `lint-discipline.instructions.md`

`lint-discipline` is narrower: "if I edited a file, I own its lint state on exit." This rule is broader: "if I spotted the debt, I own the fix." The two compose — `lint-discipline` covers files I touched, `no-deferred-debt` covers debt I surfaced regardless of whether I touched its file.

## Falsification

- **Event-based**: at 10 brain-touching turns since adoption where the rule had an opportunity to fire (debt was surfaced mid-turn), audit whether the rule was honored. If the rule was bypassed ≥3 times with "non-blocking deferred" framing and no decision-blocker named, downgrade `lifecycle: provisional → sinking`.
- **Date-based**: 2026-08-23 (90 days from adoption, same horizon as the other Tier A §0.1 ports). If by then the rule has produced no observed change in deferral-language in commits or HANDOFF entries, downgrade `lifecycle: provisional → sinking`.
- **Sink to archived**: at next deadline check (2026-09-22), if still failing, transition `lifecycle: sinking → archived`.

## Would Revise If

Revise if the rule turns single-file fixes into rabbit holes that consistently double the turn's scope (the "fix now" overhead exceeds the "fix later" cost), or if user signals that a specific class of debt is genuinely worth batching (in which case codify the exception explicitly, don't loosen the general rule).

**Falsification deadline**: 2026-08-23 (date-based), 10 opportunity-turns (event-based). Whichever fires first. See § Falsification above for two-step sink rule.
