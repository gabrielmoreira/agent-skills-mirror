# Evidence Ladder

Use this reference when deciding whether an experiment package is only minimally acceptable or strong enough to carry a paper claim.

## Core ladder

- `minimum`
  - basic executable result
  - comparable setup
  - enough to show the direction is not obviously broken
- `solid`
  - main comparison is credible
  - baseline is strong and fair
  - results are stable enough to support the main claim
  - significance testing is present when superiority is claimed
- `maximum`
  - the main claim is already credible
  - additional analysis now broadens confidence, interpretation, or scope

## Auxiliary vs main

- `auxiliary/dev`
  - parameter effects
  - diagnostics
  - mechanism checks
  - setup clarification
- `main/test`
  - claim-carrying comparison
  - the evidence likely to appear first in the paper

Do not confuse auxiliary evidence with the main comparison.

## Default policy

Before spending heavily on `maximum` polish, first move the line from `minimum` to `solid`.

If a result is still below `solid`, the next best action is usually:

- strengthen comparability
- repair a confounder
- add significance testing
- run the most claim-critical follow-up comparison
