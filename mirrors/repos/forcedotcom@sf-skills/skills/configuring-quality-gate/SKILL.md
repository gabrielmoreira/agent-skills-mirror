---
name: configuring-quality-gate
description: "Creates a DevOps Center quality gate with associated rules (PASS_PERCENTAGE, SEVERITY, ESSENTIAL) and links it to a pipeline-stage suite assignment, after showing a mandatory impact preview and obtaining explicit confirmation. Use this skill when a user wants to set or configure a quality gate, change a coverage threshold, or establish testing benchmarks on a pipeline stage. TRIGGER when: the user wants to set/configure a quality gate, change a coverage threshold, or set testing benchmarks on a stage. DO NOT TRIGGER when: only re-running an existing gate (use running-devops-test-suite in retrigger mode)."
metadata:
  version: "1.0"
  minApiVersion: "67.0"
---

## Prerequisites

Load `checking-devops-prerequisites` first — Prerequisites 1–4 AND Prerequisite 5 (stage). You need `doce-org-alias`, `pipelineId`, `stageId`, and the target `DevopsTestSuiteStage` record Id.

## Inputs required

| Input | Source |
|---|---|
| `name` | User-provided name for the quality gate |
| `rules` | List of `{type, threshold?}` — see rule types below |
| `doce-org-alias` | Established in Prereq 1 |
| `testSuiteStageId` | Target `DevopsTestSuiteStage` record Id (Prereq 5) |

## Rule types

| Type | Description | Threshold |
|---|---|---|
| `PASS_PERCENTAGE` | Minimum % of tests that must pass | Required (0–100) |
| `SEVERITY` | Maximum allowed severity level of failures | Required (numeric, e.g. 1–5) |
| `ESSENTIAL` | All essential tests must pass | Not required |

---

## MANDATORY IMPACT PREVIEW

**Before executing any commands**, show the user this preview and wait for explicit confirmation:

> "Here's what this quality gate will enforce on `<stageName>`:
> - Rule: `<type>` — `<description>`
> - Threshold: `<value>`
> - Affected pipelines: `<list>`
>
> Confirm to apply?"

**Never proceed past this point without showing the impact preview first and receiving explicit confirmation.**

---

## Confirmation gate

Only proceed with the steps below after the user has explicitly confirmed (e.g., "yes", "confirm", "go ahead"). If the user declines or does not confirm, stop and do not execute any commands.

---

## Step 1 — Create the gate record

```bash
sf api request rest \
  "/services/data/v67.0/connect/devopstesting/qualityGate" \
  --method POST \
  --body '{"name": "<gateName>"}' \
  --target-org <doce-org-alias>
```

Extract `qualityGateId` from the response.

## Step 2 — Create each rule as a sObject record

Rules are not accepted in the Connect API payload — create them as `DevopsQualityGateRule` records directly. Only create rules the user has requested. `ESSENTIAL` has no threshold.

```bash
sf data create record \
  --sobject DevopsQualityGateRule \
  --values "DevopsQualityGateId='<qualityGateId>' Rule='PASS_PERCENTAGE' Threshold=<value>" \
  --target-org <doce-org-alias> --json

sf data create record \
  --sobject DevopsQualityGateRule \
  --values "DevopsQualityGateId='<qualityGateId>' Rule='ESSENTIAL'" \
  --target-org <doce-org-alias> --json

sf data create record \
  --sobject DevopsQualityGateRule \
  --values "DevopsQualityGateId='<qualityGateId>' Rule='SEVERITY' Threshold=<value>" \
  --target-org <doce-org-alias> --json
```

## Step 3 — Link the gate to the suite stage

Update the `DevopsTestSuiteStage` record to link the new gate:

```bash
sf data update record \
  --sobject DevopsTestSuiteStage \
  --record-id <testSuiteStageId> \
  --values "IsQualityGateEnabled=true DevopsQualityGateId='<qualityGateId>'" \
  --target-org <doce-org-alias> --json
```

---

## On success

Confirm to the user:
> "Quality gate `<gateName>` created with `<N>` rule(s) and assigned to `<suiteName>` on `<stageName>`."

## Error handling

Never expose raw API errors. Use the following responses:

| Status | Response |
|---|---|
| 400 | "The quality gate configuration is invalid. Check that all rule types and thresholds are correct." |
| 403 | "You don't have permission to configure quality gates on this org." |
| 500 | "A server error occurred. Try again in a few minutes." |

---

## Related skills

- To re-run a gate after meeting threshold, use `running-devops-test-suite` (retrigger mode).
- To assign or map suites to stages, use `managing-suite-assignments`.
