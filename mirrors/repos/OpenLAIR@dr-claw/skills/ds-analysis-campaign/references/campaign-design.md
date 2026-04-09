# Campaign Design

Use this reference when an analysis campaign exists to strengthen writing-facing evidence rather than to accumulate miscellaneous extra runs.

## Goal

A strong campaign should move the evidence boundary from:

- fragile -> interpretable
- minimum -> solid
- solid -> broader confidence

Do not treat every available follow-up as equally valuable.

## Priority order

Prefer this order:

1. claim-critical contradiction checks
2. strongest robustness or sensitivity checks
3. failure-mode explanation
4. efficiency or secondary support

## Slice classes

- `auxiliary`
  - helps understand settings, thresholds, or mechanisms
  - does not itself carry the main paper claim
- `claim-carrying`
  - directly affects whether the main narrative is justified
- `supporting`
  - broadens confidence or interpretability after the main claim is already credible

## Campaign question

Each slice should answer one of these:

- does the main claim still hold when X changes?
- which component actually causes the gain?
- where does the method fail?
- how sensitive is the method to a controllable factor?
- what boundary should be written into the paper?

## Writing-facing policy

If the campaign is tied to a selected outline:

- run the claim-carrying slices first
- only then run supporting slices that deepen interpretation
- route back to `write` once the evidence is strong enough for the selected narrative
