Use local skills as the primary routing layer for AgentOps evaluation work.

Use `skill-benchmark-design` when defining whether a skill or bundle improves
outputs and what evidence should be captured.

Use `scenario-test-authoring` when adding route scenarios, expected routing, or
scenario coverage for a skillset.

Use `before-after-evaluation` when comparing baseline and skill-enabled agent
outputs and making a keep/revise/split/merge/defer/retire decision.

Use `acceptance-criteria-mapper` when turning skill, bundle, feature, or
workflow goals into observable pass/fail checks.

Use `prompt-regression-testing` when creating reusable prompt tests for known
skill behaviors, failures, or safety boundaries.

Use `skill-output-scoring` when scoring outputs with a rubric and documenting
evidence for each score.

Use `skill-token-overhead-review` when reviewing context, token, tool, or
process overhead added by a skill or bundle.

Use `skill-evaluation-iteration` for broader skill improvement loops and
`concise-technical-writing` for reports, decisions, and release notes.

Keep evaluations vendor-neutral. Do not require a specific tracing,
observability, or LLM-judge platform unless the user explicitly chooses one.
Do not publish private prompts, customer data, secrets, or sensitive outputs in
public evaluation artifacts.
