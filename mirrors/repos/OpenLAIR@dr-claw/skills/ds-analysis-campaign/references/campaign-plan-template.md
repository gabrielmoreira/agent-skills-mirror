# Analysis Campaign Plan Template

Use this for the campaign-level plan.
Treat it as the durable version of the charter, not a separate optional memo.

## 1. Objective

- campaign id:
- parent run or idea:
- main claim under test:
- user's core requirements:
- campaign outcome needed:
- selected outline ref:
- paper experiment matrix path:
- current matrix execution frontier:

## 2. Boundary And Comparability

- baseline comparison contract:
- fixed conditions:
- variables that may change:
- non-comparable slices to watch for:

## 3. Slice Plan

| Exp id | Slice id | Tier | Slice class | Experiment type | Research question | Expected value | Priority | Paper placement | Needs code change? | Needs extra baseline? |
|---|---|---|---|---|---|---|---|---|---|---|
| | | main_required / main_optional / appendix / optional | auxiliary / claim-carrying / supporting | ablation / sensitivity / robustness / efficiency / highlight / boundary / case-study | | | | main_text / appendix / maybe / omit | yes / no | yes / no |

## 4. Highlight Hypotheses

- highlight id:
- one-line claim:
- why it is plausible:
- which slices validate or falsify it:
- what happens if it fails:

## 5. Assets And Dependencies

- quest-local assets already available:
- checkpoints / baselines already available:
- downloads or services still needed:
- fallback options if external assets are blocked:

## 6. Execution Strategy

- first slices to run:
- smoke-test policy:
- main run policy:
- expected outputs:

Monitoring and sleep plan:

- wait cadence:
  - `60s`
  - `120s`
  - `300s`
  - `600s`
  - `1800s`
- health signals that justify continued monitoring:
- conditions that trigger slice redesign, kill, or campaign revision:

## 7. Reporting Plan

- what will count as stable support:
- what will count as contradiction:
- what will count as unresolved ambiguity:
- campaign summary should say in `1-2` sentences:
- matrix refresh rule after every slice:
- main-text gating rule:

## 8. Checklist Link

- checklist path:
- next unchecked item:

## 9. Revision Log

| Time | What changed | Why it changed | Impact on slices or interpretation |
|---|---|---|---|
| | | | |
