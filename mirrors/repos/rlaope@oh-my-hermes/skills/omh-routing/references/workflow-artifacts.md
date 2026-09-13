# Workflow Artifact Operator Reference

Agent/operator surface only. Normal users remain chat-first: ask Hermes for the outcome. No command below executes work or implies approval.

```sh
omh runtime workflow-artifact <workflow> <operation> --input <json-file-or->
```

The bounded JSON result is `workflow_artifact_operation_result/v1`; the CLI is metadata-only and never invokes providers, subprocesses, schedulers, CRM mutation, or production promotion.

## Closed registry

- `decision-prototype`: `prepare`, `validate`, `observe`, `receipt`, `handoff`, `persist`
- `lifecycle-growth`: `build`, `prepare`, `validate`, `evaluate`, `readout`, `audience`, `promote`, `graduate`, `configuration`, `metrics`
- `product-discovery-validation`: `build`, `prepare`, `validate`, `audience-gate`, `evaluate`, `handoff`, `append`
- `sales-pipeline-review`: `prepare`, `validate`, `evaluate`, `handoff`

Public contract and synthetic command inputs: [`docs/WORKFLOW-ARTIFACTS.md`](https://github.com/rlaope/oh-my-hermes/blob/main/docs/WORKFLOW-ARTIFACTS.md).

`build` derives schemas, statuses, metadata, and discovery hashes; `validate` is structural, not readiness. `prepare`/`evaluate` apply gates, so lifecycle may return `HOLD` for unknown consent and synthetic discovery remains `inconclusive`. Preparation does not persist; only explicit producer-owned `persist` or `append` writes validated metadata. `handoff` is proposed and executor-neutral and never dispatches, executes, or approves implementation.

Lifecycle launch review (`audience`, `promote`, `graduate`) returns separate `prepared_not_observed` records outside the six closed artifact schemas. Reachability is configuration analysis, not targeted membership or exposure; promotion defaults to `disabled` and requires explicit carry approvals; graduation proposes cleanup only from supplied rollout and rollback evidence. `prepare` and `evaluate` require a separate `lifecycle_growth_exposure_evidence/v1` companion under `exposure_evidence`: bound audience/safety policies, eligibility/exclusion checks, assigned population, actual reach, repeated-contact pressure, overlap, and channel-failure accounting. Unknown evidence holds expansion; first-launch preparation requires observed audience/reachability/contact checks without inventing treatment observations. `readout` accepts the same complete evaluation envelope, or reads a legacy artifact conservatively. Old artifacts still validate but cannot alone produce a new `ship` recommendation. Optional `evaluation_context` adds reference/baseline reasons; independently justified rollback remains rollback.
