---
name: {{candidate_name}}
description: {{candidate_description_with_trigger_boundary}}
---

# {{candidate_title}}

## Review guard

This tree defaults to `review`. Before executing any candidate rule, the host governance process
must prove its lifecycle and private provenance from an authoritative record that binds the current
complete tree hash. If an accepted or deployed record cannot be proven, uniquely locate the owning
distillation, candidate ID/path and private sources manifest; missing or ambiguous provenance fails
closed. Do not expose those private records to task outputs. Then read the authoritative
`gate-decisions.yml` record for `{{candidate_id}}` and verify that the explicit current
(`is_current: true`) Gate 3 decision, its approval snapshot and materialization record form one
of these states:

1. no current `approved-for-eval`: review or explicitly authorized candidate maintenance only;
2. an exact snapshot-bound approval but no matching completed materialization: quick-validate the
   unchanged review tree and record materialization only;
3. approval plus a completed materialization whose candidate ID/path/hash, full rule set and
   quick-validation pass match: controlled Gate 4 execution is allowed for that exact version.
4. invalid or ambiguous snapshot/governance/tree state: fail closed and repair only.

Never use a `legacy-quarantined` prototype for evaluation. In states 1–2, do not process target
task material or generate downstream task outputs.

Gate 3 approval permits controlled evaluation only. It does not mean the Skill is accepted,
publishable, or deployable.

After any session restart, context compression, checkpoint, stage transition, background return,
or agent handoff, re-read the Gate-1-bound task contract, `task-coverage.yml`, this candidate's
`stable_task_ids`, and the current Gate 3/materialization state. A stage objective or temporary
constraint may narrow the current operation but cannot supersede the product contract.

## Use when

{{should_trigger_summary}}

## Do not use when

{{should_not_trigger_summary}}

## Required input

{{required_inputs}}

## Workflow

{{reviewed_rule_workflow}}

Every operational item must map to the reviewed capability rule and its item-level semantic
support. Apply only the source-neutral reconstruction; do not read private method material during
ordinary task execution. Stop rather than filling missing target content with model knowledge.

## Output

{{output_contract}}

Output only target-grounded observations, source-neutral reasoning, conclusions, hypotheses,
limitations, unknowns and stop reasons. Never emit private provenance identifiers; bibliographic
identity such as a book title, author, publisher or ISBN; series or original file names/paths;
attribution phrases; quotations or close source paraphrases; chapter/page locators; or recognizable
named source cases. Canonical method-source
evidence remains in the private owning distillation and is not a user-facing output layer.

## Stop conditions

{{stop_conditions}}

## Reference routing

{{reference_routing}}

Runtime references contain only the reviewed problem, premises, invariant, derivation, assumptions,
boundaries, falsifiers and stops. Private evidence, source identity, locators, quotations and named
source cases remain outside this tree.

## Evaluation boundary

Read the JSON cases and rubric under `evals/`. Use only defined case IDs. Record root-confined
strict JSON fixture/baseline/with-Skill paths, recomputed full hashes, canonical case-definition
hash, candidate hash, materialized rubric/dimension scores, holdout isolation and leakage controls
in `eval-runs.yml`. Separate a
single-run blocker from a Gate 4 acceptance blocker. A definition, plan, quick validation or
structural validator PASS is not an executed evaluation, and the review package must not decide
acceptance for the user.
