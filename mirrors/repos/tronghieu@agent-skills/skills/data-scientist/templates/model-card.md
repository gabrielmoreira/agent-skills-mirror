# Model Card — {model name}

_Date: {} · Experiment log: run #{} · Data: {file/version}_

## Purpose

{One paragraph: predicts what, for whom, feeding which decision. From the
project brief.}

## Data & features

- **Training data:** {source, period, rows, grain, filters}
- **Target:** {operational definition}
- **Features:** {count; the groups; where the full list lives}
- **Known exclusions:** {segments/periods not represented}

## Validation

- **Split design:** {and why it mirrors deployment}
- **Results:**

| Model | {primary metric} | {secondary} |
|---|---|---|
| Dummy | | |
| Linear | | |
| **Final: {model}** | **mean ± std** | |

- **Holdout (spent once):** {score, bootstrap CI}
- **Sliced:** {worst segments/periods and their scores}
- **Calibration:** {checked? method?}
- **Leakage gate:** {date run; suspects investigated and disposition}

## Recommended operating point

{Threshold table or equivalent — options with business-unit consequences.
The chosen row is the decision-owner's call.}

## Top drivers (associations, not causes)

1. {driver, direction, shape, size in business units}

## Limitations & assumptions for validity

- {what has to stay true for these numbers to hold: distributions, feature
  availability at decision time, upstream definitions}
- {surviving concerns from the review gate}

## Reproduce

{Command/script + data version that regenerates this result.}
