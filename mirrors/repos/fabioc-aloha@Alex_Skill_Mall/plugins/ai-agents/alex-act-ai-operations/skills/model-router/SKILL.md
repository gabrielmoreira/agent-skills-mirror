---
name: model-router
description: "Plan AI model work across Microsoft Foundry, Hugging Face, and ElevenLabs using live provider evidence. Use when choosing a model or provider, comparing cross-provider options, decomposing multimodal work, estimating constraints, or preparing an executable plan before any paid service call."
lastReviewed: 2026-08-11
---

# Model Router

Turn a task into an explainable, executable provider plan. This skill advises;
it does not authorize or invoke paid provider work.

## Procedure

1. State the task goal and concrete deliverables.
2. Decompose compound requests into model-sized steps. Keep steps separate when
   they have different modalities, privacy boundaries, or validation methods.
3. Capture hard constraints: modality, quality, latency, privacy, region,
   license, budget, local-versus-hosted preference, and required output format.
4. Query all relevant live provider tools. Use the exact provider contract in
   [provider-contract.md](references/provider-contract.md).
5. Eliminate candidates that violate a hard constraint. Do not rank an
   infeasible candidate above a feasible one because its quality looks better.
6. Compare the feasible set. Separate observed evidence from provider claims
   and unknowns.
7. Select a primary model and ordered fallbacks. A recommendation may remain a
   Pareto set when quality, cost, privacy, and latency cannot be reduced to one
   honest score.
8. If the selected provider/model requires a credential, add a plain-language
   `Secret setup` section naming the provider-native login or exact host
   environment variable. Do not ask for the value before model selection, and
   do not write or echo it.
9. Emit a JSON plan conforming to
   [model-task-plan.schema.json](references/model-task-plan.schema.json).
10. Set `consent.status` to `pending` whenever any step spends credits,
   transmits data, changes provider state, or creates an externally visible
   artifact.
11. Hand the plan to `model-task-execution`; do not call the provider yourself.

## Credential Boundary

All provider credentials are optional until the user selects a model and
operation that needs one. Public discovery and planning may proceed without
any API key. After selection, route hosted providers through their native login
and local providers through the exact host environment variable or approved
secret storage. Never create a credential value, print it, persist it in a
plan, or request it in chat.

## Ranking Discipline

Use constraints before preferences:

1. Safety, legal, privacy, and region eligibility
2. Required modality and output compatibility
3. Quality evidence relevant to the actual task
4. Latency and availability
5. Cost and budget fit
6. Operational convenience

Never invent a provider-neutral quality score. If evidence is not comparable,
show the tradeoff.

## Output

Return:

- One-sentence recommendation
- Candidate comparison table
- Eliminated candidates with reasons
- Unknown evidence that could change the decision
- Complete JSON plan
- A plain-language consent summary

## Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| Recommend from memory | Query current provider evidence. |
| Treat popularity as task quality | Match evidence to the requested task. |
| Present unknown cost as free | Mark estimate status `unknown`. |
| Hide external data transmission | Name every provider input in `dataBoundary`. |
| Call a model while planning | Planning and execution are separate skills. |
| Collapse every tradeoff to one score | Preserve Pareto choices when evidence is incommensurable. |
| Request every provider key before choosing a model | Defer secret setup until the selected provider/model requires it. |

## Would Revise If

Revise by **2026-11-11** if two accepted plans cannot represent provider-specific
requirements, if live evidence repeatedly leaves the router unable to identify
feasibility, or if users cannot understand why the selected model won.
