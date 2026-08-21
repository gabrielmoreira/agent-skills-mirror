# quality-at-scale — reference

Medium-agnostic templates. Load when writing contracts, banks, calibration, ledger, or worker briefs.

## Unit bank (JSONL)

One object per unit. Chunk by wave when N > 500.

```json
{"type":"unit_bank","id":"U001","title":"POST /orders — idempotent create","medium":"code","distinguishing_features":["Idempotency-Key","409 on conflict"],"diversity_axis_intents":{"api_shape":"POST create","error_paths":"409+422","sync_async":"sync"},"verify_method":"tests+typecheck"}
```

Required: `id`, `title` (or `spec`), `medium`, `distinguishing_features` (≥1), `diversity_axis_intents` (≥3 axes), `verify_method`.

Duplicate rule: same full `diversity_axis_intents` map as another live unit → reject/merge.

## Diversity axis starters (pick 3–7)

| Medium | Axes |
|--------|------|
| Code | api_shape, error_paths, deps, sync_async, statefulness, side_effects, purity |
| Docs | audience, depth, structure, tone, example_density, prerequisites |
| Tests | scenario_class, input_class, failure_mode, boundary, concurrency, negative_path |
| UI | layout, state, density, theme, interaction, viewport, a11y |
| Data | schema_variant, edge_case, nullness, scale, locale, distribution |
| Prompts | persona, task_class, constraints, output_shape, difficulty, modality |
| Configs | environment, feature_flags, region, tenant, version, policy |
| Visuals | camera, composition, silhouette, palette, lighting, motion, scale |
| Research | domain, source_tier, recency, methodology, scope, stakeholder |

Rotate values deliberately within a wave — no two consecutive units share the same value on every chosen axis.

## SCALE_CONTRACT.md template

```markdown
# Scale contract

- **Run id:**
- **Medium:**
- **Target N:**
- **Global spec:**
- **Execution path:** cursor-waves | <named CLI/engine>
- **Gold path:**
- **Why gold wins (5–10 traits):**
  1.
- **Diversity axes (3–7):**
- **Pass criteria:**
  - Fidelity-to-spec:
  - Craft-parity-vs-gold:
  - Uniqueness-vs-siblings:
  - Technical gates:
- **Verify method:**
- **Wave size:**
- **Bulk harness:**
  - Generator/CLI may produce volume; must emit verify artifacts
  - After each wave: medium verify + (sensory) `/reviewresults --mode wave`
  - Script-and-ship / review-once-at-end = FORBIDDEN
- **Stop conditions:**
  - sample FAIL > 20% → halt
  - axis-collision / twin rate rising → halt
  - calibration stop → halt
  - wave review FAIL without fix → halt
- **Quarantine path:**
- **Out of scope:**
- **Budget ack:** pending | approved | n/a
```

## Calibration rubric

| Dimension | 3 (pass) | ≤2 (weak/fail) |
|-----------|----------|----------------|
| Fidelity-to-spec | Meets unit + global spec | Missing requirements / wrong behavior |
| Craft-parity-vs-gold | Matches gold polish, structure, conventions | Noticeably thinner/sloppier than gold |
| Uniqueness-vs-siblings | Differs on declared axes | Twin / shared full axis-intent set |

Wave pass: ≥90% of sample at 3/3/3; none <2 on uniqueness.  
1–2 weak → shrink next wave 50%. Collapse → STOP and revise bank/axes.

## Verify methods

| Medium | Method |
|--------|--------|
| Code | tests + typecheck + review vs gold |
| Docs | Read + structural/spec diff vs gold |
| Tests | run + coverage / assertion quality |
| UI | render/screenshot + inspect (+ a11y) |
| Data | schema validate + uniqueness + edge coverage |
| Prompts | eval on held-out cases + diff vs gold |
| Configs | schema validate + dry-run |
| Visuals | render + inspect + uniqueness vs siblings |
| Research | source check + claim–evidence pairing |

Stratified sample always; include gold as control.

## SCALE_WAVE_REPORT.md template

```markdown
# Wave report — wave __ / N=__ / medium=__

- **Date / run id:**
- **Produced / shipped / quarantined / remaining:**
- **Verify commands + exit codes:**
- **Sample paths + axis coverage:**
- **Fidelity / craft / uniqueness scores:**
- **PASS / WEAK / FAIL counts:**
- **Collapse signals?**
- **Calibration verdict:** continue | shrink | stop
- **Next action:**
```

## Ledger schema (`SCALE_LEDGER.jsonl`)

```json
{"type":"meta","run_id":"...","medium":"code","gold_path":"...","execution_path":"cursor-waves","budget_ask":null,"user_ack":true,"N":200,"wave_size":20,"diversity_axes":["api_shape","error_paths","deps"],"bulk_harness":true}
{"type":"unit_bank","id":"U001","title":"...","medium":"code","distinguishing_features":[],"diversity_axis_intents":{},"verify_method":"tests+typecheck"}
{"type":"wave","wave":1,"ids":["U001"],"paths":["out/.../U001.ts"]}
{"type":"calibration","wave":1,"sampled":["U003"],"fidelity":[3],"craft_parity":[3],"uniqueness":[3],"verdict":"continue"}
{"type":"wave_review","wave":1,"mode":"wave","sample_ids":["U003","U007"],"review_paths":[".reviews/.../reports/review.md"],"verdict":"PASS","fail_rate":0.0}
{"type":"quarantine","ids":["U041"],"reason":"axis-collision with U003","paths":["..."],"quarantine_path":"quarantine/..."}
{"type":"done","evidence":{"n_shipped":200,"n_quarantined":3,"sample_ids":[],"sample_verdicts":[],"waves_run":10,"calibrations":10,"wave_reviews":10,"medium":"code","review_paths":[]}}
```

Types: `meta` · `unit_bank` · `wave` · `calibration` · `wave_review` · `quarantine` · `done`

Resume: no `done` → continue from last wave/calibration. Never re-lock gold unless asked. Sensory waves without a `wave_review` entry are **incomplete** — do not start the next wave.

## Subagent contract

```
You are a worker in a quality-at-scale run (medium-agnostic).
MEDIUM: <medium>
GOLD: <gold_path>
YOUR UNITS: <unit bank slice>
OUTPUT PREFIX: <disjoint path>
DIVERSITY INTENTS: <per-unit axis map>
RULES:
- Match gold craft and conventions.
- Satisfy each unit's spec and global spec.
- Differ from siblings on declared diversity axes.
- No shared templates renamed. No invent-off-bank units.
- Failures → quarantine/, not live out/. Never hard-delete.
- Return: [{id, path, self_check: {fidelity, craft, uniqueness}}]
Parent verify is final. Your self-check is not.
```

## Quarantine workflow

1. Detect fail (verify fail, axis collision, craft drop)
2. Move to `quarantine/<run_id>/` — do not delete
3. Ledger `quarantine` entry
4. Does not count toward N; regenerate later

## Done-evidence checklist

- [ ] N live units; quarantine excluded
- [ ] Unit bank consumed for shipped units
- [ ] Every wave calibrated; no ignored `stop`
- [ ] Every sensory wave has `wave_review` (or equivalent medium verify logged)
- [ ] Stratified sample verified with medium method
- [ ] No ≥3 cluster sharing full axis-intent set
- [ ] Quarantine logged if any failures
- [ ] Ledger `done` with full evidence + `medium` + review paths
- [ ] Final N vs requested documented (incl. refusals/reductions)
- [ ] No script-and-ship / review-once-at-end path used

## Budget ask template

```
Run: <run_id>
Medium: <medium>
Execution path: <cursor-waves | named engine>
N / waves: <n> / <count>×<size>
Est. tokens / minutes / $: <n>
Ack to proceed (yes / budget cap).
```

## Collapse signals

- >10% sample uniqueness < 2
- Craft parity clearly below gold
- Spec drift across the wave
- Duplicate full axis-intent sets
- Verify method skipped in favor of counts alone
- Wave fail_rate > 20%
- Generator finished all N with no intermediate wave_review entries

## Domain appendix — visual floods (optional)

Lessons only: structural counts ≠ done; silhouette/template twins under new names; version-suffix spam. For Three.js repos that define it, honor `THREEJS_MAX_VERSION_LAPS=0`. Same collapse *modes* apply to code/docs/tests/data.
