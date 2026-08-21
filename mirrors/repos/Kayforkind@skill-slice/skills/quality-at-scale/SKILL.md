---
name: quality-at-scale
description: >-
  Enforces gold-bar volume across any medium: one locked exemplar, a unit bank,
  3-7 diversity axes, wave calibration, SCALE_LEDGER.jsonl, quarantine-not-delete,
  and stratified done-evidence. Trigger on /scale, N>=10 unique items, or
  mass-create dumps. Never script-and-ship, review-once-at-end, or mark done from
  file count. Distinct from one-deliverable /better polish.
---

# Quality at Scale

**Slash command:** `/scale`
**Templates:** [reference.md](reference.md) · **Examples:** [examples.md](examples.md)

> Produce N units at the **same quality bar** as one hand-crafted gold unit.
> Medium-agnostic. Volume without uniqueness and craft parity is FAILURE.

## Core principles (non-negotiable)

1. **Gold first** — freeze one verified exemplar before bulk
2. **Same bar at N** — unit #N gets the same craft as unit #1
3. **Uniqueness > volume** — refuse count-only done
4. **Unit bank before invent-on-the-fly** — specs exist before generation
5. **Waves, not floods** — verify each wave before the next
6. **Calibrate after wave 1** — continue / shrink / STOP
7. **Quarantine, never hard-delete** — failures logged with reason
8. **Stop on collapse** — drift, twins, or craft drop → halt and fix
9. **Done requires evidence** — ledger + stratified sample + reports
10. **Refuse unscalable huge N** — no scalable path → propose feasible N/path
11. **Harness bulk, don't dump** — a generator script without per-wave sensors is FORBIDDEN (see Bulk harness)

## Bulk harness (1→N collapse)

**Failure mode this skill exists to kill:** unit #1 is careful and good; at N the agent writes a script, runs it once, and ships sludge. That is not “tiredness” — the verify loop disappeared.

| Rule | Requirement |
|------|-------------|
| Generation may be dumb/fast | OK to use bulk generator scripts or CLIs for volume |
| Acceptance may never be | Same verify method as gold, every wave |
| Script legality | Bulk script/CLI is legal **only if** it emits verify artifacts (scores, frames, diffs, exit codes) that the parent checks before the next wave |
| Wave gate | After every wave: medium verify on stratified sample → ledger → then continue / shrink / STOP |
| Sensory media | Video / UI / audio / SVG samples → invoke **`/reviewresults`** (wave mode) before marking the wave done |
| End sensor alone ≠ enough | Final `/reviewresults` on one file does **not** excuse skipping wave gates across N units |
| Done | Ledger `done` + wave reports + sample evidence — never “script exited 0” or file count == N |

**Auto-REFUSE / auto-STOP:** “generate 1000 then review once”; “eyeball a couple”; lowering craft mid-batch to hit a number; marking done without `SCALE_LEDGER.jsonl` `done` entry.

## When active

Activate on `/scale`, or when the request implies **N ≥ 10** unique deliverables of any medium.  
Say once: **“Running quality-at-scale protocol.”**

Do **not** assume SVG / Three.js / PECS / any visual stack. Detect medium from the task.

## Protocol checklist

```
SCALE PROGRESS:
- [ ] 0. Preflight (medium, execution path, budget, gold, unit bank, axes, wave plan)
- [ ] 1. Gold locked + verified with medium's verify method
- [ ] 2. Quality contract written
- [ ] 3. Ledger started (SCALE_LEDGER.jsonl)
- [ ] 4. Wave 1 produced
- [ ] 5. Calibration PASS (or shrink/STOP handled)
- [ ] 6. Later waves + verify + quarantine as needed
- [ ] 7. Done-evidence complete + ledger `done` entry
```

## 0. PREFLIGHT

### Collect

1. **Medium** — code | docs | tests | ui | data | prompts | configs | visuals | research | other
2. **N** — target unique units
3. **Global spec** — what the set must satisfy
4. **Unit-spec source** — outline/scenario/schema/topic bank, or “build bank first”
5. **Execution path** — Cursor only, or named project-approved bulk CLI/script/engine
6. **Budget** — if paid/quota path, ask and wait for ack

### Execution routing (medium-agnostic)

| Role | Who |
|------|-----|
| Gold + verify | Always Cursor (full craft + medium verify method) |
| Bulk generation | Project-approved engines/CLIs/scripts **when named**; else Cursor waves |
| Huge N, no scalable path | **REFUSE** — propose feasible N or path |

Cursor frontier is for gold, calibration, verify, and modest high-craft waves — not silent dump volume when a bulk path exists.

Wave size defaults (adjust by craft intensity):

| Target N | Default wave |
|----------|--------------|
| ≤ 100 | 5–25 |
| 101–1000 | 25–100 |
| > 1000 | 50–500 **only** with scalable bulk path; else refuse |

### Gold lock

| Source | Action |
|--------|--------|
| User has a winner | Path + 5–10 why-it-wins traits |
| No winner | Craft **1** premium unit; verify; **confirm before scaling** |
| Prior batch was sludge | Do not scale that process — fix craft, re-lock |

### Unit bank (before generate)

One row per planned unit (schema in reference.md):

- `id`, `title`/`spec`, `medium`, `distinguishing_features`
- `diversity_axis_intents` (values for the chosen 3–7 axes)
- `verify_method`

Rules:

- Bank ≥ N (or wave-chunked for huge N, uniqueness vs prior ledger)
- No inventing units on the fly mid-wave without appending bank rows first
- Two units sharing **all** diversity-axis intents = duplicate → reject/merge

### Diversity axes (pick 3–7 for this medium)

Designed variety — not RNG. Starter lists in reference.md. Examples:

| Medium | Example axes |
|--------|----------------|
| Code | API shape, error paths, deps, sync/async, statefulness, side effects |
| Docs | Audience, depth, structure, tone, example density, prerequisites |
| Tests | Scenario class, input class, failure mode, boundary, concurrency |
| UI | Layout, state, density, theme, interaction, viewport, a11y |
| Data | Schema variant, edge case, nullness, scale, locale, distribution |
| Prompts | Persona, task class, constraints, output shape, difficulty |
| Configs | Environment, flags, region, tenant, version, policy |
| Visuals | Camera, composition, silhouette, palette, lighting, motion |
| Research | Domain, source tier, recency, methodology, scope |

**Auto-FAIL:** ≥3 units share the same full axis-intent set; rename/recolor/copy-paste twins; template paste under new titles.

## 1. Quality contract

Write `SCALE_CONTRACT.md`. Mirror gold — never a lowered bulk bar.

Minimum: fidelity-to-spec, craft bar, uniqueness, technical gates, verify method, stop conditions (sample FAIL > 20% → halt; twin/axis-collision rate rising → halt).

## 2. Produce a wave

- Briefs from unit bank, not improvised spam
- Aim at gold craft, not throughput
- Disjoint output paths if swarming
- Route bulk to named approved engines when present

## 3. CALIBRATION (after wave 1, before wave 2)

Sample ≥ 5 (or all if wave < 5). Score each vs gold (0–3 per dim; gold = 3/3/3):

1. **Fidelity-to-spec** — satisfies unit + global spec?
2. **Craft-parity-vs-gold** — structure, polish, conventions match gold?
3. **Uniqueness-vs-siblings** — differs on declared diversity axes?

Verdict:

- ≥90% of sample at 3/3/3 and none <2 on uniqueness → continue
- 1–2 WEAK → shrink next wave **50%**, tighten brief, re-calibrate
- Collapse (≥3 weak, or >10% uniqueness fail) → **STOP**; revise bank/axes; ask before more spend

Re-calibrate every wave until 2 consecutive clean waves, then every 3rd wave (plus on any collapse signal).

## 4. Verify before “wave done”

Structural/file counts alone are **never** enough. **Wave done without verify = harness failure.**

1. Run the medium’s verify method on the wave (see matrix below)
2. Stratified sample across diversity axes (edges + random + suspicious):
   - wave ≤ 25 → ≥ 5 (or all)
   - 26–100 → ≥ 10
   - > 100 → max(15, 10%)
3. Always keep gold as a control reference
4. For **video / ui / audio / svg** (and packs of those): run **`/reviewresults --mode wave`** on the stratified sample set (or each sampled deliverable). Append paths of `.reviews\` reports to the wave report + ledger `wave_review` entry
5. Write `SCALE_WAVE_REPORT.md` with PASS / WEAK / FAIL
6. Sample FAIL rate **> 20%** vs gold → **STOP** (same as contract stop conditions)

| Medium | Verify method |
|--------|----------------|
| Code | tests + typecheck + review vs gold |
| Docs | Read + structural/spec diff vs gold |
| Tests | run + coverage/assertion quality |
| UI | `/reviewresults --mode wave` (screenshot matrix + Read) |
| Data | schema validate + uniqueness/edge coverage |
| Prompts | eval on held-out cases + diff vs gold |
| Configs | schema validate + dry-run |
| Visuals | render + inspect + uniqueness; pack samples → `/reviewresults --mode wave` when sensory |
| Video | `/reviewresults --mode wave` on stratified sample units |
| Audio | `/reviewresults --mode wave` (loudness + probe + optional waveform Read) |
| Research | source check + claim–evidence pairing |

On FAIL: quarantine, fix process — do **not** start the next wave.

## 5. Quarantine (not delete)

Near-dupes / verify fails → `quarantine/<run_id>/`, ledger `quarantine` entry.  
Quarantined units **do not** count toward N; regenerate later.

## 6. Subagent / swarm

- **Parent** owns ledger, gold, calibration, final verify
- Workers get: gold path, unit-bank slice, diversity intents, **disjoint** output prefix, quarantine-not-delete contract
- Workers return `{id, path, self_check}` — self-check is **not** final
- Parent runs medium verify + uniqueness before accept

## 7. Ledger

Append-only `SCALE_LEDGER.jsonl` in the work folder.

Types: `meta` · `unit_bank` · `wave` · `calibration` · `quarantine` · `done`  
(Schema in reference.md.)

**Resume:** if no `done`, continue from last wave/calibration. Never re-do gold.

## 8. DONE-DEFINITION

All required:

1. N live units (quarantine excluded)
2. Unit-bank rows consumed for shipped units
3. Every completed wave has calibration; no ignored `stop`
4. Every sensory wave has a ledger `wave_review` (or equivalent logged medium verify) before the next wave
5. Final stratified sample (5% of N, min 5, max 50) verified with medium method — craft parity + uniqueness hold
6. No cluster of ≥3 units sharing full diversity-axis intent set
7. Quarantine logged if any failures
8. Ledger `done` with evidence: `n_shipped`, `n_quarantined`, `sample_ids`, `sample_verdicts`, `waves_run`, `calibrations`, `wave_reviews`, `medium`, `review_paths`
9. Project AGENTS.md / stricter domain rules honored when present

Missing any → **NOT DONE**. “Script exited 0” / file count == N → **NOT DONE**.

## Anti-patterns (forbidden)

- File/row count == N ⇒ done
- Shared template + different titles
- Version-suffix spam / redesign loops to fake uniqueness
- Skipping medium verify because a structural count passed
- Lowering the bar mid-batch to hit a number
- One giant wave
- Hard-deleting rejects
- Assuming the task is visual/SVG by default
- Burning frontier tokens on dump volume when a named bulk path exists
- **Script-and-ship** — generator/CLI with no per-wave sensors or ledger
- **Review-once-at-end** for N≥10 sensory units (skips wave harness)
- Claiming done because “the script finished” / exit code 0

## Relation to other tools

| Need | Use |
|------|-----|
| Outcome contract | `/goal` |
| Autonomous until criteria | `/goal-loop` |
| Parallel workers | `/swarm` (parent owns verify) |
| One deliverable evidence review | `/reviewresults` |
| Wave / bulk sample review | `/reviewresults --mode wave` |
| Many unique items, gold bar held | **`/scale`** |

## Domain appendix — visual flood lessons (examples only)

Not the scope of this skill — cautionary collapse modes that also apply to code/docs/tests:

1. **batch-500** — structural size/path-count passed; vision failed (shared abstract template). **Gates that ignore medium verify never prove done.**
2. **~17k near-copies** — version loops + shared silhouettes under new names. **Uniqueness > volume**; quarantine similars; do not hard-delete. For Three.js projects, honor `THREEJS_MAX_VERSION_LAPS=0` when that project rule exists.
3. Giant same-looking floods without a unit bank or diversity axes.

Visuals remain **one medium** among many (routing/axes/verify in the tables above).
