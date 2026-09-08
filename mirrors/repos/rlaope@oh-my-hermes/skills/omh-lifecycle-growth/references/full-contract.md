# Lifecycle Growth

Load this on-demand contract after the compact `lifecycle-growth` body identifies the
workflow. The main body owns routing signals, shared rules, the runtime
operation, delegation fallback, and completion/recovery pointers; this file
holds the workflow-specific detail without copying those shared rails.

## Why This Exists

`lifecycle-growth` exists so audience eligibility, consent and frequency safety, sticky exposure, causal measurement, and the stop decision travel together in one plan instead of being assembled ad hoc from analysis, copy, scheduling, and connector work.

## Do Not Use When

- The user only wants a one-off message, email, banner, or push copy rewrite with no audience, experiment, or decision; use `content-operator`.
- The user wants generic exploration or calculation over a supplied cohort, retention, conversion, or segment table with no journey or experiment to design; use `data-analysis`.
- The user wants a recurring schedule, cron, or digest cadence for an already-decided operation rather than a lifecycle intervention; use `automation-blueprint`.
- The user asks to send a message, change a feature flag, create a segment, or start an experiment in a provider now; use `connector-operator` with explicit authorization and observed results.
- The user needs a PRD, prioritization frame, or roadmap for a product change rather than a journey or experiment; use `product-brief`.

## Examples

Good example:

- Prompt: Our day-7 retention dropped for new workspace admins; design an in-app onboarding journey and a holdout experiment so we know whether it works.
- Expected behavior: Prepare the brief, audience trigger policy, safety policy, experiment plan with sticky assignment and actual exposure, a readout scaffold, and an approval-gated handoff disposition.
- Why: The request spans lifecycle stage, audience, treatment, and causal measurement, which is the whole lifecycle-growth loop rather than one sibling's slice.

Bad example:

- Prompt: Send the re-engagement push to every inactive user tonight.
- Expected behavior: Route to `connector-operator` with explicit authorization, or return HOLD if consent, suppression, and frequency eligibility are unknown.
- Why: An immediate external send is a connector action, and lifecycle-growth never sends or claims delivery.

## Completion Checklist

- The target behavior, baseline, eligible audience, safety policy, experiment design, readout, and decision owner are named or marked HOLD.
- Prepared plan, human approval, observed delivery or display, observed user action, observed outcome, and causal claim are reported as separate states.
- The readout disposition is exactly `ship`, `rollback`, `review`, or `insufficient_data`, and every proposed handoff names its owning workflow, approver, and stop conditions.

## Recovery Notes

- If consent, suppression, identity, event semantics, denominator, or the decision owner is unknown, return HOLD with the missing fields and ask for the one input that unblocks the smallest next step.
- If provider or data evidence for delivery, display, action, or outcome is unavailable, keep every readout stage not_observed and set the disposition to `insufficient_data` or `review` rather than `ship`.

## Use When

Use when a product or growth owner wants to improve a lifecycle stage and needs the target behavior, eligible audience, safety policy, experiment design, launch/rollback gates, measurement readout, and ship/rollback/review/insufficient_data decision assembled as one evidence-bounded plan.

Routing signals: `lifecycle-growth`, `lifecycle growth`, `lifecycle marketing`, `lifecycle messaging`, `in-app journey`, `in-app message campaign`, `onboarding journey`, `onboarding nudge`, `activation campaign`, `activation experiment`, `retention campaign`, `retention experiment`, `re-engagement campaign`, `win-back campaign`, `referral experiment`, `monetization experiment`, `growth experiment`, `holdout experiment`, `product-led growth loop`, `라이프사이클 마케팅`, `온보딩 여정`, `그로스 실험`

## Workflow Contract

Category: `strategy`
Phase: `lifecycle-growth`
Hermes role: `operator`
Quality tier: `decision-gated`
Reasoning demand: `standard`

Quality bar:

- Define the value-bearing behavior and its baseline before any campaign or treatment is proposed.
- Separate assignment from actual exposure, and eligible, attempted, delivered, displayed, acted, and outcome stages from one another.
- Keep copy, supplied-data calculation, recurring scheduling, external sends, and PRD work with their owning workflows.
- Require a named human approval before any launch handoff and observed evidence before any delivery or outcome claim.

Handoff policy:

Keep lifecycle framing, audience and safety policy, experiment design, and readout interpretation in Hermes. A prepared journey or experiment plan is not a send, a flag change, a delivered message, a displayed treatment, a user action, a business outcome, or a causal result. Hand external sends and flag mutations to `connector-operator`, copy to `content-operator`, supplied-data calculation to `data-analysis`, recurring scheduling to `automation-blueprint`, and validated product changes to `product-brief`, each only after the human approval gate and only reported from observed evidence.

Required inputs:

- lifecycle objective and stage
- target segment
- event schema and baseline
- channels or product surfaces
- consent and policy constraints
- experiment budget
- decision owner

Expected outputs:

- lifecycle_growth_brief/v1
- audience_trigger_policy/v1
- lifecycle_safety_policy/v1
- growth_experiment_plan/v1
- growth_measurement_readout/v1
- growth_handoff_disposition/v1

Artifact expectations:

- prepared lifecycle-growth plan and readout, as metadata-only records with safe references, when a wrapper captures them

Safety rules:

- Fail closed: unknown consent, suppression, frequency eligibility, event semantics, identity, denominator, or decision owner returns HOLD and blocks a launch-ready handoff.
- Consent and suppression come only from supplied records; product usage or the absence of an opt-out never implies either.
- Do not claim a message was sent, a flag was changed, a treatment was displayed, a user acted, an outcome moved, or an experiment succeeded without observed provider, runtime, or data evidence.
- Delivery and click counts are not product or revenue impact; a causal claim needs a valid observed experiment or another named identification method.
- Retain bounded metadata and safe references only; never store user identity, event payloads, message bodies, consent records, or transcripts in durable artifacts.
- Treat small samples, novelty effects, seasonality, concurrent interventions, and inconsistent event semantics as blockers or stated uncertainty, not as results.

Detailed procedure steps: `references/procedure.md`.
