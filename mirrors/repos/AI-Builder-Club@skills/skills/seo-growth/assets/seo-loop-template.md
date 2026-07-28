# SEO Engine — loop template

A fill-in-the-blanks brief for a scheduled SEO loop. Replace every `<FILL: …>`, delete the
SETUP block, then point your scheduler at it.

**Do not enable this until you have run the playbook by hand a few times.** Automating an
undiagnosed site produces confident output aimed at the wrong work, faster. The reasoning
behind every rule below is in this skill's `references/`.

**Recommended guard:** have the pre-run step count remaining `<FILL: …>` markers and refuse to
invoke the agent while any remain. A half-configured loop then cannot ship anything.

---

## SETUP — delete once every box is ticked

- [ ] Search Console access works. You can pull query-dim and page-dim rows for
      `<FILL: yourdomain.com>`. Run it once by hand first.
- [ ] **Pick the regime** below and delete the branch you are not in.
- [ ] **Name your breadwinner** — the page earning ≥30% of clicks. Don't know it? You aren't
      ready; measure for a week first.
- [ ] **Write your carve-out** — the query families that will never click. Do this BEFORE run 1
      or your KPI will lie to you.
- [ ] **Name sibling loops** and their owned pages, or write "none yet."
- [ ] Start PR-only. Earn autonomy later.

---

## Spec

**Mission:** <FILL: own head term X / grow clicks on surface Y> for <FILL: brand>. The reader's
next step is <FILL: course, signup, newsletter, community>.

**Property:** `<FILL: yourdomain.com>` · **Repo:** `<FILL: path>` · **Content:** `<FILL: glob>`

**Open monitor, no finish line.** Each run reports the score against its target and flags
movement in or out of it. If runs degenerate into measure-and-skip, slow the cadence rather
than forcing thin work.

### Regime — pick ONE

**[ ] LAND-GRAB** — emerging term, thin SERP, demand still forming.
- North star: **exact-head position (hold ≤3) + family footprint.**
- Default unit: ship ONE cluster article.
- Clicks are a **graduation tripwire**, not a score.
- **Flip gate (report all three numbers every run):** move to HARVEST when
  `family_top3_share ≥ 85%` AND `family_queries` grew <10% vs prior run AND `family_weak ≤ 2`.

**[ ] HARVEST** — pages live, demand established.
- North star: **clicks.** Position is a diagnostic and does not decide the work.
- Default unit: one enrichment on the highest click-opportunity page.
- Name the KPI's successor (clicks → <FILL: conversion>) and say honestly whether it is
  instrumented. Never fake it from what Search Console can reach.

### Carve-out — families that score zero BY DESIGN. Do not optimize these away.

<FILL: your verified non-clicking families>

Screen every low-CTR page against: **LLM fan-out** (no human to click) · **competitor-
navigational** (they want the competitor's site) · **brand-navigational** (your homepage should
win it) · **anonymized tail** (visible impressions <10% of total = undiagnosable).

### Scope

Owns: <FILL: pages>. **Never touches:** <FILL: sibling loop's pages, including your crown jewel>.
Before editing ANY page, check whether a sibling loop touched it in the last 7 days. If so, skip.

---

## Each run, in order

**0. Reconcile against the live system.** Key on **URL, not title** — titles get rewritten at
publish. If state drifted, fix it first; everything downstream is meaningless on a false model.

**0b. Verification ledger.** For every applied change whose `verify_after` has passed: compare
that page's clicks 7d-after vs 7d-before. Human traffic down >30% → flag a **revert
recommendation** naming the change, page, numbers, and commit. **Never revert yourself.**
Otherwise stamp it verified.

**1. Read state.** This file's Current understanding + last Timeline entry + recent commits.
Never re-ship something already covered or in flight.

**2. Read the score.** Use pre-staged data; do not re-fetch what a deterministic pre-stage
already pulled — that is the largest cost sink these loops have. Window: 28 days ending 3 days
back.

**2b. Deployment check.** Count unmerged units. **An unmerged page is not live** — while
anything is unmerged, flat position is expected, not failure.

**2c. Canary + cooldowns.** Breadwinner position drop ≥3 or clicks drop >30% → flag it first and
queue no edits against it. Cooldowns: breadwinner 14 days, other pages 7 days. One edit per page
per window, or you cannot attribute the result.

**3. Pick ONE unit** and log why the data chose it. Menu by leverage: internal link equity into
the page you're compounding · query-match title/H1/meta to the human query the page ranks for
but never names · fresh PAA-style FAQ · tighten the answer into the first 30% · extraction
structuring · follow through on a flagged verification.

**4. Screen the candidate for human intent** before touching it. Non-human → next candidate.

**5. Mine the freshness gap.** Your own curated stream FIRST, then repo/release feeds, then
social listening, then diff against your own pages. **Grounding only on your own data is a
closed loop.** Cite the source that motivated the pick.

**6. Gates — all must hold, or ship nothing.** Cannibalization pre-check (no page of yours at
pos <15 for the target) · CTA test answered in writing · every new technical specific verified
against a **primary source** this run · queue depth under <FILL: n> · voice check on final copy.

**7. Ship.** Branch off `origin/main` after a fetch — never local main, never commit to main.
PR body: target, evidence, the numbers, the CTA answer, before→after, the doc URL you checked.
Stamp `applied:` and `verify_after: +14d`.

**8. Report.** Write a dated run report. Append one Timeline entry. Emit metrics. Notify on:
KPI fell, drift found, canary tripped, a revert recommendation, or nothing cleared the gate for
3+ runs.

### Hard rules

Never auto-publish <FILL: what stays human-gated>. Never fabricate a metric or quote — use
`[NEED: …]`. Never date-bump without a real change, but DO bump it when the change is real.
Never target a head term one of your own pages already ranks pos <15 for. Respect cooldowns.
Keep heavy work out of any synced folder.

---

## Current understanding

*Seed before run 1, never let it go stale. This section — not the automation — is where the
compounding lives. A loop that re-derives its conclusions every run is an expensive cron job.*

- Baseline (<FILL: date>): KPI <FILL:>, head position <FILL:>, breadwinner <FILL:> at <FILL:>%.
- **Verified non-problems — do not re-triage:** <FILL:>
- **Ruled out, and why:** <FILL: so a future run doesn't re-pitch them>
- **Ledger of applied changes:** <FILL:>
- **Environment gotchas:** <FILL: each one costs a run to rediscover>

**Two runtime traps true of any scheduled agent loop:** a run dies the instant the agent yields
the turn, so backgrounded work and "notify me later" waits die with it — long steps must be
blocking foreground calls. And a long run can lose its lease if the machine sleeps; keep runs
short and chunk anything lengthy.

## Timeline
<!-- one dated entry per run -->
