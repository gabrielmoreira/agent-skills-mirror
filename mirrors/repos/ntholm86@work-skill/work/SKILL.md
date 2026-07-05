---
name: work
description: 'A standalone, target-agnostic improvement-reasoning skill with full auditability: it can examine and improve anything the model can reason about — code, documents, plans, music, letters, anything — while recording every reasoning step in an auditable trail. One consolidated loop: Intent, Improve, a mini-Destination bootstrap, a self-triggered mini-Orient when the arc needs one, and always-on Trail logging. USE WHEN: you want disciplined, auditable improvement reasoning on any target at a single skill-load, especially in long or frequent sessions where token budget is a real constraint.'
argument-hint: 'The target (repo, file, system) and the request itself'
metadata:
  version: "3.1.0"
---

# work

*Auditable autonomy: reason about anything, improve anything, show every step — cheap enough to use every day, without losing the quality.*

**If you're new to this:** "operator" means whoever directs the work — you, if you're the one using this file. "Subagent" means a separate helper agent dispatched with its own fresh context; if your tooling has none, every mention of them is skippable. `.acm/` is short for Agent Context Memory — a small convention: a folder at the root of whatever repo is being worked on, holding plain-text memory in three files — `destination.md` (what this target is for), `orientation.md` (what recent work has concluded, once enough runs exist to conclude anything), and `audit-trail.md` (what happened and why, one entry per run). This file reads and writes those three files and needs nothing else: no tooling, no install step, no sibling files. A few passages below mention a larger "full suite" of separate skills; they exist for people who also have that suite and are safe to skip if you don't.

## Why this exists, and what it trades away

`work` is a standalone skill: an improvement-reasoning architecture that works on any target — a codebase, a letter, a plan, a book, a piece of music — and leaves a full audit trail of how it reasoned. "Target" below always means *whatever is being worked on*, not just software. Its lineage is a consolidation of a larger suite, and that lineage explains its shape:

The full suite (`intent`, `improve`, `destination`, `orient`, `trail`, `probe` — a sixth skill, contamination/pattern-matching detection, deliberately not folded into this fork) was built when token cost wasn't the binding constraint. It costs tokens on two axes: **loading** (five instruction files instead of one) and **ceremony** (a full interpretation + four-lens examination + reflection essay on every run, even a one-line fix).

`work` cuts both axes without cutting the three principles beneath them:

1. **Operator's Intent** — you are given a destination, not a route.
2. **Observable Autonomy** — every reasoning step is recorded as it happens; an observer must be able to reconstruct what you did and why from the trail alone.
3. **Convergence Is Silence** — finding nothing actionable is a valid outcome. Never manufacture ceremony to look thorough.

**The one rule that makes the trade honest: match reasoning depth to the stakes of the moment, not to a fixed template.** A typo fix and a redesign decision are not the same event and must not cost the same number of tokens to record. Spend full ceremony only on moments that are genuinely hard to reverse or genuinely uncertain; log everything else in one honest line. The depth tiers in step 3 are the mechanism for this — not a suggestion.

And if a cost/quality trade-off is ever genuinely unavoidable in a run, say so in the trail entry. A silent trade-off is exactly the invisible reasoning Observable Autonomy exists to prevent.

## The loop

Four steps every run — **bootstrap** (step 0, first contact with a target only), **understand** (step 1), **work** (step 2), **record** (step 3) — plus an **arc-read** (step 4) whenever the work signals it needs one.

**The skill leads this workflow, not the operator.** Assume the operator is new to this file: they should never need to remember to invoke a step. The loop decides when its own moments are due — a destination question, an arc-read, a trail entry — announces in one line what it's doing and why, and names the one decision that belongs to the operator at that moment (confirm a destination, rule on a proposal, answer a question). Hand-holding is part of the job: a workflow the operator has to drive from memory is a workflow that won't happen.

### 0. Bootstrap gate — mini-Destination

Before anything else, check the **target repo's** `.acm/` folder (always at the root of the repo being worked on — never the skills install directory).

- If `.acm/destination.md` exists (or the legacy name `.acm/vision.md`): read it, plus `.acm/orientation.md` if present. Continue to step 1.
- If neither exists, this is a first run against this target. Run the condensed Destination:
  1. From the request and any visible repo signal (README, recent commits, folder structure), form **1-3 sourced guesses** about what this target is for and who it serves.
  2. Turn the single most load-bearing guess into **one short, answerable question**.
  3. Ask it. If the operator answers, write `.acm/destination.md` from the answer plus the unasked guesses (marked open — not asked, not confirmed). Plain markdown, no special format: what the target is for, who it serves, any confirmed constraints, then an "Open" list holding the unasked guesses.
  4. If no answer is available this run (operator unreachable, or says "proceed"), write `.acm/destination.md` from your best reading, clearly marked unconfirmed — the recommended phrase, verbatim: `**Operator not yet confirmed** — revise on first pushback.` Any wording works as long as the unconfirmed status is impossible to miss. Don't block: a marked assumption is a legitimate, auditable state; a missing destination file is not.
  5. Once `.acm/destination.md` exists, re-run this step only on a real trigger — never merely because time passed or a session is new. Three triggers are legitimate: explicit invocation; the operator's own signal that the destination is stale or thin; or **the loop's own evidence** that the destination is exhausted or wrong — a plateaued scorecard whose coverage diff (step 2) came back empty, or observed reality contradicting what `destination.md` claims. A self-triggered run may ask and propose, never settle: its output enters `destination.md` as an appended, dated proposal marked unconfirmed until the operator rules, and step 1's pre-commit read-back applies in full — the skill owns detecting that the destination needs revisiting; the operator owns what it becomes.
  6. **Do not build other committed files around an unconfirmed guess in the same pass.** A guess labeled `unconfirmed` in `destination.md` does not license writing the rest of the target's files as though it were settled — ask before producing those artifacts too.

**Scoped memory.** Before trusting the target repo's own destination, walk parent directories upward looking for a higher-scope `.acm/destination.md`. Stop at a `.acm-root` marker file (an empty file an operator drops at the top of a workspace to say "don't look higher"), the filesystem root, or after 4 levels. Higher scope wins on coordination matters. When the difference matters to a decision, label which scope you're reading from ("workspace mandate" vs. "repo mandate").

### 1. Understand the ask (Intent, fused)

Before touching the target, run one fast check: *what does the operator actually want, and is there a plausible alternative reading?* Three cases, three narration costs:

- **Unambiguous and mechanical** (a named file, a one-line fix, a direct yes/no): don't narrate at length — one clause inside the trail entry's own description is enough. A paragraph explaining that "fix the typo on line 12" means fixing the typo on line 12 is waste, and waste is what this skill exists to cut.
- **Minor interpretive gap** (clear enough to act, but you're making a judgment call on scope, format, or approach): proceed, and flag the specific choice in one sentence in the trail entry, so a wrong call is cheap to correct.
- **Material divergence** (the literal request and the likely goal point different directions, or the ask is bare — "continue", "keep going", "next"): stop and narrate before acting. State what you believe the destination is, what would count as success, and at least one alternative reading you considered and rejected, with why — if you can't name one, you likely pattern-matched instead of interpreting. For a bare ask, form 1-3 sourced hunches from `.acm/destination.md`, `.acm/orientation.md`, the last few trail entries, and what the conversation itself has emphasized, corrected, or redirected toward, about what matters most now; surface the single most useful question; and if no answer comes back, proceed on your best hunch as an explicit assumption.
- **Internal contradiction** (the request conflicts with itself, or with something the operator stated earlier): name the contradiction explicitly rather than silently resolving it by picking one side. Surface both readings and let the operator adjudicate — a confidently-executed resolution of a contradiction the operator never saw is a distinct failure from misreading a clear-enough ask.

One class of edit always gets its interpretation read back to the operator **before** committing, not after: anything touching `.acm/destination.md` or the target's own statement of what it is. A misreading at that layer is cheap to catch before commit and compounding after — every downstream run inherits it.

This step replaces a standalone Intent invocation. It is never optional — only its narration length varies.

### 2. Work — examine, challenge, decide, act

Do the work, scaling the rigor of examination to the stakes. Four lenses are available as thinking tools, not a checklist: **Purpose** (does the target achieve what it's for, against `.acm/destination.md`?), **Inconsistency** (does it contradict itself or its own stated rules?), **Overburden** (does it ask more of its users or maintainers than it's worth?), **Waste** (does everything here still earn its place?) — plus whatever the target itself invites (security, performance, correctness...). Name the lenses that were actually load-bearing; don't narrate the ones that weren't. When the examination is a fidelity audit — checking a derivative against its source (a consolidation against its suite, a summary against its document, a port against its original) — compare against the source directly; self-review of the derivative alone reliably misses what was dropped.

If a score or rubric helps the examination, treat it as a temporary diagnostic of the current plateau — void when the destination or focus shifts — never a standing target to optimize toward. A metric that outlives its plateau starts prescribing a route.

**Scoring, when the operator asks for a rating.** "Rate this" is a distinct request from a plain examination: produce roughly **10 relevant measurements**, chosen for this target's actual destination and evidence — not a fixed universal checklist reused unchanged across unrelated targets. For each measurement give a score, the evidence it rests on (name the trail entry, file, or test it's read from — a score with no cited evidence is a guess wearing a number), and exactly one concrete improvement suggestion, checked against `.acm/destination.md`'s confirmed constraints before it's offered — a suggestion that would violate a settled constraint (e.g. reintroducing dropped mechanism weight, adding an installer where one was permanently rejected) is not valid here; name the tension instead of proposing it. Record the scorecard, dated, in `.acm/orientation.md` so the *next* rating can show whether a score moved — the delta is the actual signal, not the absolute number. This is still bound by the plateau rule above: a scorecard is void the moment the destination or focus shifts, never a standing target pursued for its own sake. And when scores flatline instead — sustained deltas of ~0 under an unchanged destination — don't invent fresh metrics just to have something to score. First distrust the plateau itself: exhausted territory, or metrics too coarse to see movement? Then diff the destination text against the measurement set, looking for obligations no metric projects. Uncovered obligations become the next work or the next measurements; an **empty** diff is evidence the destination as written is served — the one finding that self-triggers a destination re-run (step 0.5), because a loop that keeps polishing a served destination is manufacturing ceremony, and a loop that silently stops is abandoning its post. It asks instead.

For anything beyond a mechanical fix, pause on this before deciding: *What am I not seeing? Am I anchored on the most obvious finding and missing a subtler, more important one?* Then the redesign question: *is the target's structure itself wrong, so that no incremental fix will help?* If the structure itself is wrong, don't patch — argue for redesign: sketch the alternative, weigh redesign cost against the cost of continuing to patch, and stop for the operator's decision.

Then pick exactly one outcome:

- **A change.** Name the single highest-leverage thing and why. Make a falsifiable prediction before acting ("I will do X; I expect Y; I expect Z *not* to happen"), act, then verify the outcome against the prediction.
- **An argument for redesign.** Surface it. Do not act on it without confirmation.
- **Silence.** Nothing actionable — a valid outcome, but bound it: name the bar this was tested against and what remains untested. Unbounded silence is not a valid form.

If you back out of something mid-run (tried X, reverted when Y proved it wrong), mark it `[!REVERSAL]`. Within-run reversals are as much evidence of honest reasoning as cross-run ones; hiding them inflates the trail's apparent success rate.

### 3. Trail — always, every run, no exceptions

Append one entry to `.acm/audit-trail.md` in the target repo, using the header format `## <date> — <slug>` (create the file with a one-line header if absent: `# Audit Trail — <repo name>`, where the repo name is simply the name of the folder holding this `.acm/`). This is the one step never skipped and never optional, however trivial the run: a run with no entry is a run that didn't happen, as far as anyone auditing later can tell.

**Depth tiers — pick the lowest one that's honest:**

- **Tier 1 — Micro** (mechanical, no real decision: typo fix, direct question answered, one obvious command). One or two lines: what was asked, what was done, outcome. No decision/prediction/reflection scaffolding, and no next-move line — work with no real decision rarely implies a meaningful next step.

  ```
  ## 2026-07-03 — fix-typo-readme
  Asked to fix "recieve" typo in README. Fixed. No decisions, nothing notable.
  Cost: light — 2 tool ops, 1 file.
  ```

- **Tier 2 — Standard** (a real choice existed between plausible alternatives, or the work could plausibly be second-guessed later). Compact: interpretation in one line (only if it wasn't obvious), decision plus a one-line prediction, outcome vs. prediction, one line naming the blind spot (or the nothing-found), and one line naming the most obvious next-step candidate if one stands out — skip it if none does; silence is valid here too. Skip the full reflection ceremony unless one of the escalation triggers below fires.

  ```
  ## 2026-07-03 — split-config-loader
  Read "clean up config handling" as splitting the loader, not rewriting it. [!DECISION] — rewrite was plausible but riskier.
  Predicted the split leaves all 12 tests green; it did.
  Blind spot: no test covers the env-override path. Next: cover it.
  Cost: moderate — 9 tool ops, 4 files, no subagent.
  ```

- **Tier 3 — Full** (structural or architectural decisions, redesign arguments, anything the operator would want deeply audited, anything touching an area a past `[!REVERSAL]` or a recurring finding-class — the same kind of defect turning up across separate runs — already flagged). The complete shape: interpretation, examination with lenses named, challenge, decision + prediction, action, reflection (a falsifiable claim about the target, a named blind spot, an imagined expert's pushback), the four across-trail triggers each explicitly evaluated — *did the operator ask for a deeper audit? is a recurring finding-class present? does this run contradict a prior `[!REALIZATION]`? is a silence declaration imminent?* — and candidate next moves.

**Escalate a tier — never de-escalate below what's honest — when:** the operator pushes back, the change is hard to reverse, a past `[!REVERSAL]` touched this area, or something about the run surprised you mid-work. Genuinely unsure which tier? Take the higher one: over-recording a routine entry costs little; under-recording a real decision breaks the audit trail. If a surprise surfaces only after the entry is committed, don't edit it in place — append a short follow-up entry cross-referencing the original by slug, at whatever tier the new information warrants.

**Cost line — every entry, every tier.** End each entry with one line of observed run cost: a bucket (light / moderate / heavy) plus the countable proxies behind it — tool operations, files read or written, subagents dispatched. Count the proxies roughly but consistently from run to run — the trend across entries is what the mini-orient reads, not the unit definition. Use real token counts only if the platform actually exposes them; **never invent a token number** — a plausible-looking count with no source is fabricated telemetry in the one file that must never lie. And the cost line is telemetry to reflect on, never a target to minimize: cutting honest depth to make the line look cheaper is the de-escalation this step already forbids, now with a number attached.

**Markers** make the trail searchable and are never cut for cost, at any tier, when one genuinely applies:

- `[!DECISION]` — a genuine choice between plausible alternatives; the moment a future audit wants to find first.
- `[!REALIZATION]` — something shifted in what this run understood about the target that wasn't known going in.
- `[!REVERSAL]` — an attempted approach was backed out of after it proved wrong.

**Cut from the full Trail skill, on purpose:** derived-artifact regeneration (`history.md`/`learning.md` — rebuilt summary files the full suite maintains alongside its trail), the `record.py` tooling (the full suite's script that runs that regeneration and enforces entry formatting), and writer-splitting (a second, independent agent writing the trail entry, so the agent that decided isn't also the one describing — a stronger anti-rationalization safeguard than this file uses). None of it is required here. The entry header format (`## <date> — <slug>`) and the marker vocabulary are kept compatible with that tooling on purpose, so it can be run against this same `audit-trail.md` later if you have it — optional, never a dependency.

### 4. Mini-Orient — when the work signals it, with a backstop counter

The skill decides when an arc-read is due — never wait for the operator to ask for one. Check at trail-append time, and run the mini-orient **in this same run** when any of these fires:

- **The arc contradicts itself** — this run hit a `[!REVERSAL]` or a missed prediction in territory recent entries treated as settled, or the same finding-class has now turned up across separate runs.
- **The operator pushed back** — a correction means the arc misread something; check what else the misreading touched before building on it.
- **A stretch just closed** — a tracked open item converted, a phase completed, or the next move is genuinely unclear: natural arc boundaries are where an arc-read pays best.
- **`orientation.md` reads stale** — its claims are contradicted by what recent entries actually show, or cost lines look like they're drifting without the stakes drifting with them.
- **Backstop:** none of the above has fired within the last **~5 of this loop's entries** (count `## ` headers after `orientation.md`'s dated header; if the file doesn't exist yet, from the start of the trail). The 5 is deliberately arbitrary — a cheap tripwire, not the logic. It exists because the run that most needs an arc-read is often the one least able to notice it; the signals above are the real trigger, the counter only catches what judgment misses.

**Multi-writer trails.** On targets whose `.acm/` is also written by other agents or the target's own tooling (a pipeline's own record phase, other skills), the backstop count applies to **entries this loop wrote** — other writers' entries are context to read, not a schedule this loop can breach; a "missed" mini-orient charged to sessions that never loaded this skill is a false positive, not a backlog to catch up. And where `orientation.md` is owned by the target's own machinery (rewritten by its own arc-reading phase), don't overwrite its claims: append a dated mini-orient addendum and leave the owner's sections intact.

1. Read only the **last ~5-10 entries** — not the full history. (The trigger check is per-run and exact; this read window is deliberately approximate.) That limit is the deliberate cut versus real Orient, which reads the whole arc.
2. Form **1-3 falsifiable arc-claims** about what this stretch of work shows is true of the target, or what is changing.
3. Check whether a `[!REVERSAL]` or a recurring finding-class shows up across those entries — and check the opposite too: a suspiciously clean run with no reversals, no missed predictions, and no named blind spots is itself a finding (likely rationalization, not a job well done). Where an earlier entry made a prediction, check whether a later entry's actual outcome confirms it or quietly contradicts it without saying so.
4. Read the cost lines across those entries: is cost drifting upward without the stakes drifting with it — ceremony creep, habitual high tiers, runs heavier than their decisions warrant? A cost trend is a plateau diagnostic like any other score: worth one line if it says something, void when the focus shifts.
5. If something material emerged, update `.acm/orientation.md` (create it if absent, dating its header) with a short "Current claims" section and a "Watch for" line. If nothing material emerged, say so in one line in this run's own trail entry and leave `orientation.md` alone — a mini-orient with nothing to say should say nothing.

No freshness guard (the full suite's staleness check, flagging when a derived artifact like `history.md` no longer matches the trail it was built from), no `record.py`, no `learning.md` extraction — exactly the heavy tooling this cut removes. If you separately have the full `orient` skill and the target needs its deeper discipline (quality-bar naming, adversarial arc-audit, loop-effectiveness review), invoke that instead: this mini-orient is a cheap tripwire, not a replacement. If you don't have it, the mini-orient above is the ceiling this file offers — a design choice, not a gap.

## Self-check before calling a run done

- Did step 3 (Trail) actually happen? If not, the run isn't done, whatever else was accomplished.
- At append time, did you check the mini-orient's need-signals and the ~5-entry backstop (on multi-writer trails, counting only this loop's entries)? If either fired, did the mini-orient actually run *in this run*? A due-but-skipped mini-orient is a breach, not a deferral.
- Did you pick the lowest honest tier — or default to Tier 3 out of habit? Habitual Tier 3 defeats the entire point of this skill.
- If you cut a corner for cost anywhere in this run, is the cut visible in the trail entry — or did it happen silently?
- If this run built more than one new committed file around an inference from step 0 or step 1, did you ask before building the rest — or only label the first one unconfirmed and proceed as if that were enough?
