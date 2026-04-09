# Paper Experiment Matrix Template

Use this template when a paper-like line needs a durable experiment-control surface beyond the selected outline.

Create and maintain both:

- `paper/paper_experiment_matrix.md`
- `paper/paper_experiment_matrix.json`

The Markdown file is the human-facing control surface.
The JSON file is the machine-facing mirror.

## 1. Current Judgment

- current judgment:
- why the matrix is needed now:
- what would make the experiments section stable:
- what still blocks stable paper writing:

## 2. Core Claims

- `C1`:
  - one-line claim:
  - current support status:
  - strongest current evidence:
  - still-missing evidence:

- `C2`:
  - one-line claim:
  - current support status:
  - strongest current evidence:
  - still-missing evidence:

- `C3`:
  - one-line claim:
  - current support status:
  - strongest current evidence:
  - still-missing evidence:

## 3. Highlight Hypotheses

Write only serious hypotheses that could matter to the paper's reader-facing value.
Do not assume the highlight is already true just because it sounds attractive.

- `H1`:
  - one-line highlight:
  - why it is plausible:
  - validation rows:
  - fallback if unsupported:

- `H2`:
  - one-line highlight:
  - why it is plausible:
  - validation rows:
  - fallback if unsupported:

## 4. Taxonomy Summary

Check every category deliberately.
Do not collapse the matrix into “analysis only”.

- main comparison:
- component ablation:
- sensitivity:
- robustness:
- efficiency / cost:
- highlight validation:
- failure boundary:
- case study optional:

## 5. Matrix Table

| Exp id | Title | Tier | Experiment type | Status | Feasibility now | Claim ids | Highlight ids | Research question | Metrics | Paper placement | Next action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | main_required / main_optional / appendix / optional / dropped | main_comparison / component_ablation / sensitivity / robustness / efficiency_cost / highlight_validation / failure_boundary / case_study_optional | proposed / planned / ready / running / completed / analyzed / written / excluded / blocked | feasible_now / light_setup / blocked / uncertain | | | | | main_text / appendix / maybe / omit | |

## 6. Detail Cards

Repeat one card per meaningful row.

### EXP-001

- title:
- tier:
- experiment type:
- current status:
- feasibility now:
- why this row exists:
- research question:
- hypothesis:
- comparators:
- fixed conditions:
- changed variables:
- required metric(s):
- minimal success criterion:
- cost / runtime budget:
- promotion rule:
  - main text if:
  - appendix if:
  - omit if:
- expected figure or table:
- result artifact paths:
- dependencies:
- next action:

## 7. Execution Frontier

- rows ready now:
- rows blocked now:
- rows that must finish before the experiments section is stable:
- rows that are appendix-only and can wait:
- rows that are optional and should not block:

## 8. Main-Text Gate

Do not treat the experiments section as stable while any currently feasible row that is not merely `optional` or `dropped` remains unresolved.

Every currently feasible non-optional row should be one of:

- completed
- analyzed
- excluded with reason
- blocked with reason

## 9. Refresh Log

After every completed, excluded, or blocked slice, reopen the matrix first and update it before selecting the next run.

| Time | Exp id | What changed | Claim/highlight impact | Priority change | New next action |
|---|---|---|---|---|---|
| | | | | | |
