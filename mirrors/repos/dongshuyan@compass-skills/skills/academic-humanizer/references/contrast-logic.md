# Supported and unsupported contrast

This cross-language rule handles false opposition in English and Chinese. It is
semantic, not a phrase ban. A pattern match may open an audit; it never decides
the result by itself.

## Contents

1. Definition
2. Candidate families
3. Grounding test
4. Three decisions
5. Safe transformations
6. Protected academic uses
7. Anti-overfitting checks

## 1. Definition

An **unsupported rhetorical contrast** introduces, denies, or downgrades X mainly
to make Y sound deeper, broader, or more novel, even though X has no identifiable
source or argumentative role.

The defect is not negation itself. The defect is an unsupported X plus a contrast
that adds ceremony or inflation instead of evidence.

## 2. Candidate families

English candidates include:

- `not X but Y`, `not merely/just/simply X; Y`;
- `not only X but also Y`, `more than X`, `beyond X`;
- `less about X and more about Y`, `rather than simply X, Y`;
- `on the surface X, but fundamentally Y`;
- split forms such as `This is not X. It is Y.`

Chinese candidates include:

- `不是/并非 X，而是 Y`；
- `不只是/不仅仅是 X，更是 Y`；
- `问题不在于 X，而在于 Y`；
- `与其说 X，不如说 Y`；
- `表面上是 X，本质上是 Y`；
- `超越 X，成为 Y` and equivalent split-sentence forms.

These lists are recall aids. Quoted language, cited language, and discussed-as-
example spans are protected.

## 3. Grounding test

For every candidate, identify X and Y, then ask in order:

1. **Source**: Is X explicitly asserted, attributed, cited, hypothesized, requested
   by a reviewer, defined as a baseline, or otherwise present in the source bundle?
2. **Need**: Would stating Y alone, or X and Y as a neutral addition, lose a real
   correction, exclusion, or comparison?
3. **Evidence**: Does the available text support rejecting/downgrading X and
   supporting Y? An ablation, controlled comparison, negative result, definition,
   citation, or scope statement can provide support.
4. **Specificity**: Is X a concrete, testable proposition or only a generic
   downgrader such as `a simple tool`, `an implementation detail`, `一次改进`?
5. **Inflation**: Is Y an abstract escalation such as `paradigm`, `mindset`,
   `revolution`, `本质`, `格局`, or `范式变革` without source evidence?

Frequency is not a validity test. One unsupported contrast is still unsupported;
several valid experimental contrasts remain valid.

## 4. Three decisions

### A. Protected contrast: keep

Choose **keep** when X has an identifiable source or technical role and evidence
supports the distinction. Preserve its polarity, baseline, and relation.

### B. Unsupported rhetorical contrast: rewrite

Choose **rewrite** only when X is generic evaluative scaffolding, contributes no
independent content, and Y can be stated without adding or deleting a material
claim. Remove the staged opposition and state the supported content directly.

### C. Concrete but unverified contrast: flag

Choose **flag** when X or the X/Y relation is concrete but the available source
does not establish it. Do not decide that the contrast is true or false. In detect
mode, request evidence. In rewrite/edit mode, preserve the sentence or ask before
changing it.

## 5. Safe transformations

| Original relation | Safe action |
|---|---|
| generic X rejected to inflate Y | remove the empty downgrader; state supported Y directly |
| `not only X but also Y`, with both claims supported | keep, or rewrite as neutral `X and Y`; preserve both claims |
| concrete `not X but Y`, evidence present | keep the contrast; simplify only redundant wording |
| concrete `not X but Y`, evidence absent | flag; do not delete X or assert Y |
| `surface X / essence Y` with no analysis | state supported observation; remove unsupported essence claim |
| reviewer or scope correction | keep the explicit boundary and its target |

Never replace a vague contrast with a new number, mechanism, example, baseline,
or limitation. If the source has no concrete substitute, use plainer wording.

## 6. Protected academic uses

- a cited misconception or prior interpretation followed by a correction;
- competing hypotheses distinguished by an experiment or analysis;
- ablation-based attribution (`gain comes from Y rather than X`);
- a negative result contrasted with a positive result;
- a definition or scope exclusion (`optimizes latency, not throughput`);
- reviewer-response clarification tied to the reviewer's actual concern;
- a mathematical, legal, or technical distinction where polarity is substantive;
- genuine additive findings where both X and Y are supported.

## 7. Anti-overfitting checks

Before changing a candidate:

- Ignore the surface pattern and restate its propositions. If a proposition would
  disappear, do not auto-rewrite.
- Check at least the surrounding paragraph, supplied source, and cited antecedent.
- Do not infer that an uncited X is false; absence of local evidence creates
  uncertainty, not permission to erase content.
- Do not penalize contrast density in ablations, related work, error analysis,
  definitions, or reviewer responses.
- A detector in `metrics.py` reports `candidate_only`. The language model must run
  this grounding test before choosing keep, rewrite, or flag.
