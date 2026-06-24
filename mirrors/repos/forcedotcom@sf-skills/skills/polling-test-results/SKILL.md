---
name: polling-test-results
description: "Polls a DevOps Center async test execution by runId until it completes, fails, or times out — using read-only SOQL on the execution record at provider-specific intervals (Apex 15s/5m, Code Analyzer 10s/3m, Provar UI 60s/20m, Flow 20s/8m) — then surfaces results. Use this skill when a test suite run is in progress and the user is waiting on results, or immediately after running a suite. TRIGGER when: a test suite run is in progress and the user is waiting on results, or immediately after running a suite and a runId is available. DO NOT TRIGGER when: there is no active runId."
metadata:
  version: "1.0"
  minApiVersion: "67.0"
---

# polling-test-results

**Confirmation required:** No — polling is automatic and read-only. No user confirmation gate is needed.

**What it does:** Polls the DevOps Center org for the status of an async test execution until it completes, times out, or fails.

---

## Prerequisites

You need an active `runId` (returned by the `running-devops-test-suite` skill) and the confirmed `doce-org-alias`. If org context is not yet established, load `checking-devops-prerequisites` first (Prerequisites 1–3).

---

## Inputs required

| Input | Source |
|---|---|
| `runId` | Returned by the `running-devops-test-suite` skill |
| `testType` | Derived from the suite's test provider (Apex, Code Analyzer, UI/Provar, Flow) |
| `doce-org-alias` | Established via `checking-devops-prerequisites` |

## Polling configuration

| Test type | Poll interval | Max wait | Timeout action |
|---|---|---|---|
| Apex unit tests | 15 seconds | 5 minutes | Surface runId, offer retry |
| Code Analyzer | 10 seconds | 3 minutes | Surface runId, offer retry |
| UI tests (Provar) | 60 seconds | 20 minutes | Surface runId, mark as pending |
| Flow tests | 20 seconds | 8 minutes | Surface runId, offer retry |

## Poll query

Query the execution record by `runId` on each interval:

```bash
sf data query \
  --query "SELECT Id, Status, TestsRan, TestsPassed, TestsFailed, CoveragePercentage FROM DevopsTestExecution WHERE Id = '<runId>' LIMIT 1" \
  --target-org <doce-org-alias> \
  --json
```

Check the `Status` field on each poll:
- `Queued` / `Running` → wait and poll again
- `Completed` → proceed to result analysis
- `Failed` → surface error and offer retry or skip

## On timeout

Surface the `runId` to the user:
> "The test run is taking longer than expected. Your run ID is `<runId>`. You can check the status manually in DevOps Center, or I can keep waiting — what would you prefer?"

Do not automatically retry after timeout. Wait for user instruction.

## On completion

Pass the full result payload to the `analyzing-test-failures` skill for reasoning. Surface `Coverage`, `SuccessCount`, `FailureCount`, and `QualityGateStatus` inline. Do not surface raw JSON to the user.

---

## Related skills

- Runs are started by `running-devops-test-suite` (including its retrigger mode)
- Failure analysis is handled by `analyzing-test-failures`
