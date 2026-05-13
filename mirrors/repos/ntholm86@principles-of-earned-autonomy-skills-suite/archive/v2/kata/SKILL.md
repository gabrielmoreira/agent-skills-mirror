---
name: kata
version: 2.11.0
description: 'Orchestrate an improvement cycle: diagnose, select methodology, execute, record, persist. The meta-pattern that connects all skills into a coherent workflow. USE WHEN: improve, audit, review, full treatment, kata, run the loop, comprehensive improvement, what does this project need.'
argument-hint: 'Specify the target (project, file, system) and optionally a focus area or concern'
---

# Kata

*The routine of improvement itself.*

Kata is the orchestrator. It takes a target, determines what that target needs, selects and executes the right methodology, records everything, and persists the results.

## The Cycle

### 0. Interpret the Request

Before grasping the target, grasp the request. Apply the **Intent** skill ([intent/SKILL.md](../intent/SKILL.md)) to whatever prompt triggered this Kata run — whether a user message, a scheduled review, or a prior-run finding.

Extract what the requester actually wants, narrate the interpretation, and check the gap against the literal text. If the interpretation materially diverges from the literal request, surface the divergence before entering Step 1. If the interpretation changes what the target is, Step 1 operates on the corrected target, not the originally-named one.

This step is observable: the interpretation goes into the kiroku session's Intent section verbatim (or into the conversation if no session log is active). An observer reading only the trail must be able to answer *"what did the agent take the requester to mean, and what did they ignore or change from the literal prompt?"* without reading the original message.

Intent runs on every Kata cycle. A one-line *"the prompt was unambiguous; proceeding as stated"* is a valid outcome when warranted — silence is not.

### 1. Grasp the Situation

Understand the target before acting on it.

- What is this target? What does it do? Who uses it?
- What state is it in? Read its history if one exists (TRAIL/, changelogs, prior runs).
- What has been tried before? What worked? What did not?
- What is the triggering concern? (User request, periodic review, prior-run finding)
- What assumptions are being made — by the human, by the agent, by prior runs? Surface them explicitly. An unstated assumption that turns out wrong is more damaging than a stated one.
- What constraints apply? Hard limits (safety, legal, compatibility) and soft limits (time budget, acceptable complexity, performance targets). Constraints that aren't identified early become surprises later.
- Does a **Target Condition** exist in `TRAIL/SUMMARY.md`? If yes, it guides all decisions this run. If no, ask the human: *"Where do you want this project to end up?"* Record their answer in `SUMMARY.md` under `## Target Condition`.

If this target has a `TRAIL/` directory, read `TRAIL/GENBA.md` for the most recent run entries. If a prior run exists, verify its claims: check that changes it reported are actually present. Do not anchor to a prior run's score.

**Derive measurements.** After understanding the target, determine what to measure — based on what this target is, what the Target Condition is, and what would make improvement (or its absence) visible. The measurements must make sense for *this* target:

- A skill suite that claims to produce autonomous reasoning should be measured on whether it actually does (ARF, principle compliance, convergence integrity).
- A web application should be measured on what makes it good at being a web application (security posture, accessibility, test coverage, API consistency — whatever the agent determines matters after reading the code).
- A library should be measured on what makes it good at being a library (API surface clarity, documentation coverage, backward compatibility).

Do not prescribe the measurements in advance. Derive them from what you find. State each measurement and why it matters for this target.

**Re-derivation and additive consolidation on evaluator change.** If a prior run on this target established a measurement scheme (recorded in GENBA or SCORECARD), do not silently inherit it when your evaluator differs from the family-version that derived it. Re-derive independently, then consolidate.

**Recommended hygiene — cold derivation before comparison.** The engine cannot blindfold an evaluator from prior context, but the protocol can be stated: derive your own list of measurements *before* studying the existing rubric in detail, then compare. An evaluator that reads the existing rubric first will mostly reproduce it, and the consolidation step becomes hollow.

**Family vs. version.** "Family" is the model lineage (e.g., Claude, GPT, Gemini). "Version" is a release within a family (e.g., Sonnet 4.6 vs Sonnet 4.7). Re-derivation is *required* on family change; on same-family different-version it is *recommended* but not required. Provenance records the full family-version regardless.

**Four outcomes** — every re-derivation produces exactly one. Record the outcome label in the GENBA entry.

- **Convergent (no addition).** Your independent derivation produced the same measurements with the same rationale; no new dimensions, no refinements. Record `Re-derivation: convergent (no addition)`. This is the strongest validation of the rubric and counts toward P3 silence (provided the run also produces zero artifact changes).

- **Convergent with refinement.** Same dimensions, but you would phrase or anchor one differently. Record `Re-derivation: convergent with refinement` and apply the refinement as a `[!DECISION]` with rationale. Refinements must not change what is being measured — only how it is described, anchored, or scored. If the change alters what is measured, it is one of the next two outcomes, not this one.

- **Divergent (additive).** Your derivation surfaced a measurement the existing rubric does not capture. Record `Re-derivation: divergent (additive)` and merge the new dimension into the rubric **this run** as a `[!DECISION]` (do not defer to "a future run"). Add a row to the SCORECARD Rubric Provenance table attributing the dimension to your family-version. Bump the rubric version (e.g., v4 → v4.1).

- **Divergent (contradictory).** Your derivation argues an existing dimension should not be there — measures the wrong thing, double-counts, or rests on a rationale that does not survive scrutiny. Record `Re-derivation: divergent (contradictory)` and retire the dimension as a `[!REVERSAL]` with rationale and Provenance update. Bump the rubric version.

**Same-family runs** still compare against the inherited scheme but are exempt from the consolidation requirement. Record `Re-derivation: inherited (same family, version <X.Y>)`.

**Externally anchored rubrics** (published standards: PDCA, DMAIC, NIST AI RMF, etc.) are exempt from re-derivation and consolidation. They are not exempt from the divergence-as-finding rule: if your independent examination suggests the standard is insufficient for this artifact, record that as a finding for the standard's owners, not a silent deviation.

**Rubric Provenance ledger.** Every target with a non-trivial measurement scheme maintains a Rubric Provenance table in its SCORECARD (or equivalent). Each row: dimension name, contributing family-version, run number, one-line rationale. The table makes the rubric's evolution legible to a deployer who asks *"which families have shaped this rubric, and what did each one add?"* Without it, "consolidated rubric" collapses into "whatever the latest model thought was worth keeping."

The loop's own operational metrics (elapsed time, transcript size, artifact growth) are measurements too. If they trend poorly, that is a finding — the loop should diagnose and address its own resource consumption the same way it addresses any other deficiency.

**Record the measurement scheme.** This is Step 1's observable output — without it, an observer cannot verify what the run was measured against. Before moving to Diagnosis, write a brief measurement scheme statement in this run's GENBA entry:
- What is being measured and why each measurement matters for this target.
- Whether this inherits or revises a prior run's scheme. If inheriting unchanged, one sentence suffices: *"Inheriting [target's scheme name] — no revision."* If revising, record it as `[!DECISION]` with rationale. (The scheme name is whatever was derived for this target in its first run — e.g., "Rubric v3" for the TPS Skill Suite, "M1–M7 article metrics" for a preprint, or a bespoke scheme for a new target.)

An observer reading only the GENBA entry should be able to answer *"what was this run measured against and why?"* without consulting the kiroku session or prior runs.

### 2. Diagnose

Examine the target and determine what it needs. Three classical diagnostic lenses are available as vocabulary:

- **Unevenness** - inconsistency in style, patterns, quality distribution, naming, error handling, coverage. Unevenness is often a root cause: inconsistency breeds confusion, confusion breeds overburden, overburden breeds waste.
- **Overburden** - components asked to do too much. Excessive responsibilities, deep coupling, high complexity concentrated in one place.
- **Waste** - what does not earn its existence. Dead code, unused abstractions, redundant validation, documentation that duplicates rather than illuminates.

These are thinking tools, not a procedure. Use whichever reveals what matters. Use none if the situation calls for something else. The diagnosis must be grounded in what you find, not in which categories exist.

For each finding: identify the root cause, not just the symptom. "This function is too long" is a symptom. "This function handles three unrelated responsibilities because they were added incrementally without refactoring" is a root cause.

**Scope the diagnosis to the artifact, not to the change.** Each run's natural pull is to evaluate what was *changed* — the edit that triggered this run, the finding surfaced by the prior run. That scope is insufficient. Accumulated defects that no individual change introduced (stale verifier logic, documentation drift, tooling that silently degrades, mojibake aging in place) are invisible to change-scoped diagnosis. A run that only evaluates its own change will report a clean diagnosis while the artifact as a whole decays.

The corrective discipline: before concluding the Diagnose phase, spend at least part of the lens scan on the *whole* artifact with no privileged focus on recent changes. If three or more consecutive runs have each scoped their diagnosis to the current change, the next run must treat the whole artifact as the target. Two signals that this is overdue:

- **Sustained plateau** (3+ zero-delta runs) combined with **active external criticism** — if an outside observer or a Kaizen-lens-alone pass finds real defects, the prior runs were scanning too narrowly.
- **Tooling results the loop hasn't interrogated** — e.g. persistent verifier warnings, deferred findings that have rolled forward through multiple sessions, or metrics the loop has stopped treating as signal.

A holistic scan that finds nothing is still a valid diagnosis. A change-scoped scan that finds nothing is not — it has only verified that the change is clean, not that the artifact is.

### 3. Decide

Based on the diagnosis, select the methodology. If a Target Condition exists, evaluate each option against it — does this move the target closer?

- **Kaizen** - the target needs incremental improvement. The structure is sound; specific things need fixing. This is the most common case.
- **Kaikaku** - the target's structure cannot reach its goals through incremental changes. It needs redesign. This is rare and must be justified.
- **Hansei** - the improvement loop itself needs examination. Use after every ~10 runs on the same target, or when 3+ consecutive runs produce no changes, or when the same kinds of findings keep recurring.
- **Shiken** - the target needs to prove it supports genuine reasoning, not just compliance. Use when you suspect prescriptive drift or when the system needs ARF validation.

### 4. Execute

Before executing, start a kiroku session for the target:

```powershell
& "<skills-dir>/kiroku/kiroku-start.ps1" -Slug "<methodology>-<target>" -Project "<target-path>"
```

First determine `<target-path>` correctly. It is the repository being improved, not the repository that happens to contain the skill scripts.

The `-Project` parameter determines where `TRAIL/` lives — always in the target being worked on. When Kata targets an external repo, the trail goes in that repo. When Kata targets the skills suite itself, the trail goes in the skills directory.

If direct VS Code chat work and Kata both act on the same repository, they append to the same `TARGET_REPO/TRAIL/`. The trigger differs; the trail does not.

**Pre-flight CM check.** Before modifying files, verify the latest GENBA entry's claims: are the changes it reported actually present? This catches inter-run CM drift (insertions, reverts, or formatting changes that occurred between sessions). If drift is found, record it as a finding before proceeding — the drift itself may be the highest-leverage fix.

Invoke the selected skill. It does the work. During execution, mark decisions, realizations, and reversals in the session transcript.

After execution, close the session:

```powershell
& "<skills-dir>/kiroku/kiroku-close.ps1" -Project "<target-path>"
```

### 5. Record

After execution, update the target's audit trail. All trail artifacts live in a single `TRAIL/` directory. Kiroku manages the core evidence layer (sessions, INDEX, SUMMARY). When Kata evaluates a target as a whole (scored, cross-model), it also maintains a run ledger:

- **`TRAIL/GENBA.md`** — Kata's evaluation run ledger. Used when the entire target is evaluated (e.g., suite-level scoring runs recorded in SCORECARD.md). Not used for development work on individual components — that's tracked by kiroku sessions alone. Prepend the new entry (newest-first). Keep entries compact. Every entry includes:
  - Run number, date, model identity
  - What was found (key findings only — root causes, not exhaustive lists)
  - What was done (actions taken — omit file manifests, `git log` has those)
  - Verification result (build/tests pass/fail)
  - Measurements (what was measured, the scores, and the delta from prior run — this is what makes the gap visible and drives the next run)
  - Assessment (one sentence: current state, what remains)

- **SCORECARD Dimension Trajectory** — if the target has a SCORECARD with a Dimension Trajectory table, append a row with **start→end scores for every measurement** (format: `start→end`, e.g., `8→9`). This applies to both rubric dimensions and any derived measurements recorded in Step 1. Use the `Derived` column for any measurements beyond the standard rubric — list each as `Name: start→end`. The run table shows only the mean; the Dimension Trajectory shows which specific dimensions moved, where each started, and what was measured at all. An observer reading the Dimension Trajectory row alone should be able to verify the run's claimed delta without consulting GENBA.

  **Silence run convention:** For runs where the P3 silence chain advances (zero score delta AND zero artifact changes), include the marker `(silence)` in the main run table's Result column immediately after the methodology name (e.g., `Kaizen (silence). ...`). `metrics.ps1` Metric 7 uses this `(silence)` marker — in parentheses — to distinguish genuine P3 silence from zero-delta action runs such as CM fixes that leave scores unchanged but still modify files. Bare occurrences of the word without parentheses (e.g., "not a silence run") do not qualify. Zero-delta rows without `(silence)` in the Result break the computed silence chain.

- **`TRAIL/sessions/`** — the session transcript. Mark decisions with `[!DECISION]` (include rationale and alternatives considered), realizations with `[!REALIZATION]`, reversals with `[!REVERSAL]`.

- **`TRAIL/INDEX.md`** — auto-generated decision index. Run `kiroku-index.ps1` after closing the session.

- **`TRAIL/SUMMARY.md`** — executive digest. Updated after each run. Must not duplicate GENBA or INDEX content. Contains:
  - One-line status
  - Target Condition (human-stated desired end-state, if provided)
  - Direction (current methodology and why)
  - Key decisions (max 3 strategic ones — link to INDEX for full list)
  - Open concerns
  - Integrity warning

The observer looks at one directory. CHANGELOG.md stays outside TRAIL/ — it serves project users, not process observers.

### 6. Persist

Commit the changes to version control. The disaster recovery floor is one run deep.

## Convergence

Kata honors Principle 3. Convergence requires three simultaneous conditions:

1. Three or more consecutive evaluations by distinct evaluator families produce the same score (within a defined tolerance)
2. Zero artifact changes in each of those evaluations
3. Each evaluator scored independently without consulting prior scores, **and at least one of the three re-derived the measurement scheme from the target and found it convergent** (see Step 1)

When these conditions are met, record the convergence and stop. Do not manufacture findings to justify continued execution. The P3 silence counter is computed by `metrics.ps1` from SCORECARD data — it is not asserted by the agent. If the asserted counter drifts from the computed value, the metrics output flags it.

**Operational note:** In chat-based tools, changing the selected model inside the same conversation does **not** satisfy independent assessment. Prior scores and reasoning remain in context. For a run to count toward convergence, start a fresh conversation/session with that evaluator and do not expose prior scores.

## Periodic Hansei

Hansei is triggered by signals, not by fixed cadence. Invoke Hansei when any of these conditions hold:

1. **Recurring findings:** 3+ consecutive Kaizen runs produce findings in the same defect class (same root cause wearing different symptoms).
2. **Sustained plateau:** 3+ consecutive zero-delta runs without convergence being declared (the loop is running but not moving).
3. **Methodology doubt:** The evaluator suspects the rubric, measurements, or diagnostic approach is measuring the wrong things.
4. **Explicit human request:** The human asks for reflection.

The verifier (`verify-suite.ps1` Check 9) monitors signal 2 (sustained plateau via SCORECARD deltas). Signals 1, 3, and 4 are judgment-based — the evaluator or human must recognize them.

**What this replaces:** Prior versions used a fixed cadence (every N runs). Cadence-driven Hansei risks compliance-shaped reflection — producing bullets to satisfy a periodic rule rather than reflecting because there is something to reflect on. Signal-driven Hansei fires when reflection has a purpose.
