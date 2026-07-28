# Operationalize — making it run without you

Both playbooks are cycles, and a cycle a human runs by hand gets skipped the first busy week.
This is how to hand it to scheduled agent loops.

**Prerequisite: do not automate a stage you have never run by hand.** Automating an
undiagnosed site produces confident output pointed at the wrong work, faster. Run at least a
few cycles manually, learn your own carve-outs and archetypes, *then* encode them.

---

## Four roles, never one loop

The biggest structural lesson from running these: **one "SEO loop" always collapses.**
Measuring, shipping, improving, and answer-engine tracking run on different clocks and score
on different metrics. Split them.

| Role | Cadence | Scores on | Ships | Playbook |
|---|---|---|---|---|
| **Scout** | weekly | candidates found | one article, or a draft for approval | cold-start, and new fronts |
| **Engine** | daily | position + family footprint | cluster articles (as PRs) | land-grab |
| **Enrichment** | daily or every 3 days | clicks | one page edit (as a PR) | with-data |
| **Scorecard** | weekly | nothing — it reports | a dated report | both |

**The scorecard never ships anything.** Mixing measurement with action means one bad week
rewrites the strategy.

## Coordination rules

Each of these exists because it failed first.

1. **Hard carve-outs, written down.** Every page belongs to exactly one loop. Two loops editing
   one page destroys attribution — you can no longer tell which change did what. Include your
   crown-jewel page explicitly in whichever loop owns it.
2. **Standing check before any edit:** has a sibling loop touched this page in the last 7 days?
   If yes, skip it.
3. **Stagger the schedules.** Same-minute fires collide on API quota and on the repo working
   tree.
4. **Human merges.** Loops open PRs; a person merges. Earn autonomy per-lane later, and only
   for small additive changes on non-critical pages, capped at one per run, gated on a passing
   build.

## What each loop must do every run, regardless of role

1. **Reconcile against the live system** before trusting any internal state.
2. **Read the score** from pre-staged data — do not re-fetch what a deterministic pre-stage
   already pulled. Re-fetching is the single largest cost sink these loops have.
3. **Check the canary and respect cooldowns.**
4. **Screen candidates for human intent** before treating anything as a problem.
5. **Run the gates:** cannibalization, CTA test, primary-source fact-check, queue depth.
6. **Ship at most one unit**, stamped with a verify-after date.
7. **Report, and update its own durable state file.**

## The durable state file is where the compounding lives

Not the automation. Each loop keeps a brief with three sections:

- **Spec** — what it does and when it speaks.
- **Current understanding** — baselines, verified non-problems it must stop re-triaging,
  candidates already ruled out and why, the ledger of applied changes, environment gotchas.
- **Timeline** — one dated entry per run, distilled periodically to a milestone spine.

**A loop that re-derives its conclusions every run is just an expensive cron job.** Most of the
value is in "Current understanding" — specifically the list of things it must *stop*
rediscovering.

## Two runtime traps

- **A scheduled run dies the instant the agent yields the turn.** Backgrounded work and
  "notify me when done" waits die with it — there is no later. Long steps must be blocking
  foreground calls. This killed real runs on two properties before it was understood.
- **A long run can still lose its lease** if the machine sleeps. Keep runs short and chunk
  anything lengthy.

## A ready-made starting point

`assets/seo-loop-template.md` in this skill is a fill-in-the-blanks loop spec that encodes the
rules above as an actual run pipeline. Copy it, replace every `<FILL: …>` placeholder, and
point your scheduler at it.

To build the surrounding loop scaffolding, see the **`new-loop`** skill in this same plugin.
