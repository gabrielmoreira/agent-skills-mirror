# Workflow Artifact Operator Reference

Agent/operator surface only. Normal users remain chat-first: ask Hermes for the outcome. No command below executes work or implies approval.

```sh
omh runtime workflow-artifact <workflow> <operation> --input <json-file-or->
```

The bounded JSON result is `workflow_artifact_operation_result/v1`; the CLI is metadata-only and never invokes providers, subprocesses, schedulers, CRM mutation, or production promotion.

## Closed registry

- `decision-prototype`: `prepare`, `validate`, `observe`, `receipt`, `handoff`, `persist`
- `lifecycle-growth`: `build`, `prepare`, `validate`, `evaluate`, `readout`
- `product-discovery-validation`: `build`, `prepare`, `validate`, `evaluate`, `handoff`, `append`
- `sales-pipeline-review`: `prepare`, `validate`, `evaluate`, `handoff`

Public contract and synthetic command inputs: [`docs/WORKFLOW-ARTIFACTS.md`](https://github.com/rlaope/oh-my-hermes/blob/main/docs/WORKFLOW-ARTIFACTS.md).

`build` derives schemas, statuses, metadata, and discovery hashes; `validate` is structural, not readiness. `prepare`/`evaluate` apply gates, so lifecycle may return `HOLD` for unknown consent and synthetic discovery remains `inconclusive`. Preparation does not persist; only explicit producer-owned `persist` or `append` writes validated metadata. `handoff` is proposed and executor-neutral and never dispatches, executes, or approves implementation.
