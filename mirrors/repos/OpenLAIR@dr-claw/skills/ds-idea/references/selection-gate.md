# Selection Gate And Handoff

Use this reference when choosing the final idea and preparing the handoff to `experiment`.

## 1. Lightweight quality gate

Score the final serious candidate on a `0/1/2` scale:

- novelty
  - `0` obvious tweak
  - `1` moderate variant
  - `2` clear non-trivial mechanism change
- falsifiability
  - `0` vague claim
  - `1` partially testable
  - `2` explicit metric, direction, and boundary condition
- feasibility
  - `0` unclear implementation path
  - `1` large refactor risk
  - `2` minimal touchpoints clearly identified
- evidence quality
  - `0` no credible citation
  - `1` weak or indirect support
  - `2` directly relevant papers plus baseline evidence
- constraint fit
  - `0` violates constraints
  - `1` uncertain fit
  - `2` fully compliant with dataset, protocol, and compute limits

If total `< 7/10`, do not promote the idea yet.
Also treat these as hard gates before promotion:

- the literature survey must already durably cover at least `5` and usually `5-10` related and usable papers
- the closest-prior-work comparison must explain why the idea is still needed
- the final selected-idea draft must be ready to carry standard-format citations for the papers actually used

## 2. Honest novelty / value labels

Use these labels explicitly:

- `novel`: closest prior work does not already make the same mechanism-plus-claim combination
- `incremental but valuable`: overlap exists, but the new setting, evidence package, or failure-mode resolution is still meaningful
- `not sufficiently differentiated`: closest prior work already dominates the idea

Only the first two are eligible for promotion.

## 3. Handoff fields for experiment

The selected idea record should include:

- stable idea id
- `motivation` in SCQA form
- `reasoning` with main hypothesis plus `2-3` competing hypotheses near the top
- `claim` as one falsifiable sentence tied to:
  - `metric_key`
  - expected direction
  - boundary condition
- `theory_and_method`
- `code_level_plan`
- `relation_to_literature`
- `references` or `bibliography` in a standard citation format
- evidence or source pointers

Inside the implementation handoff, also include:

- `metric_key`
- `expected_direction`
- `minimal_experiment`
- `abandon_condition`
- `strongest_alternative_hypothesis`

## 4. Recommended presentation shape

Use a compact Pyramid structure:

- first line: falsifiable claim plus metric focus plus boundary condition
- then `3-6` bullets of reasoning and evidence pointers
- then the minimal validation plan
- then a short `References` or `Bibliography` section that cites the survey-stage papers actually used

## 5. Promotion gate

Do not promote a candidate if any of these remain unclear:

- what exactly is being claimed
- how the claim differs from closest prior work
- what minimal experiment can refute it
- which code touchpoints are affected
- what evidence package would later defend it in writing
- which `5-10` surveyed papers actually support the motivation, mechanism, and claim boundary
- whether the final idea draft includes proper citation markers plus a standard-format reference list
