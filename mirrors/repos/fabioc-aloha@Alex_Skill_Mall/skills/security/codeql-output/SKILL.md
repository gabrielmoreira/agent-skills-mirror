---
type: skill
lifecycle: stable
inheritance: inheritable
name: output
description: Produce the final CodeQL fix result table and choose the correct exit code and retry behavior
tier: standard
applyTo: '**/*codeql*,**/*output*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Output Reporting — Instructions

> Scope: Final reporting and failure classification for every `codeql-fix` run

---

## Objective

Use this skill when a `codeql-fix` run finishes, stops early, or fails.

This skill has two jobs:

1. Produce one stable, machine-readable and human-readable final result.
2. Choose the correct exit code and determine whether the failure is retryable.

Do not return free-form final status text when this skill applies. Always use the required table format below.

---

## Required Final Format

Return the final outcome as a Markdown table with exactly these fields and in this order.

| Field | Required content |
|---|---|
| Exit Code | Numeric exit code from the error classification table in this skill. |
| Cloned Repo Path | Local checkout path used for the run. For interactive mode, use the current repository path. If cloning never succeeded, use `NOT_AVAILABLE`. |
| Alert Details | Alert ID or identifiers, query ID when available, and concise per-alert status. If the alert was not found, include the reason. |
| Fix Status | One of `ALL_ALERTS_FIXED`, `PARTIAL_FIX`, `FALSE_POSITIVE`, `NOT_FIXED`, or `NOT_RUN`, plus a numeric summary such as `2/3 alerts fixed`. |
| Code Review Output | `PASSED`, `FAILED`, `NOT_RUN`, or `SKIPPED`, followed by the blocking finding summary or a concise reason. |
| Build Check Output | `PASSED`, `FAILED`, `NOT_RUN`, or `SKIPPED`, followed by the build summary or failure reason. If retries were used, include the retry count. |
| PR Link | Draft or published PR link. In interactive mode use `NOT_APPLICABLE`. If PR creation fails, use `NOT_CREATED: <reason>`. |

---

## Output Rules

1. Always return the full table, even when the run stops early.
2. Do not omit later fields when an earlier phase fails. Use `NOT_RUN`, `SKIPPED`, `NOT_AVAILABLE`, or `NOT_CREATED` as appropriate.
3. Use `PR Link = NOT_APPLICABLE` in interactive mode.
4. If at least one alert was fixed but the full alert set was not completed, use `Fix Status = PARTIAL_FIX` and include the exact count.
5. If SymFix classifies every requested alert as a false positive, use exit code `0` and `Fix Status = FALSE_POSITIVE (0/N alerts fixed)`.
6. If a failure happens after some alerts were fixed, keep the failure exit code and report the exact completed count in `Fix Status`.
7. Keep status values stable and uppercase so they are easy to parse.

---

## Error Classification

Use this table to decide the exit code and whether the current failure may be retried.

| Exit Code | Error name | Retryable | Max additional retries | Retry guidance |
|---|---|---|---|---|
| `0` | `SUCCESS` | `NO` | `0` | No retry needed. |
| `10` | `REPO_CLONE_FAILED` | `CONDITIONAL` | `2` | Retry only for transient clone, fetch, checkout, or network failures. Do not retry when the repository URL is wrong, access is denied, the branch source commit is invalid, or branch creation is blocked by policy. |
| `11` | `ALERT_NOT_FOUND` | `YES` | `1` | Re-run input resolution once to re-resolve `JobId`, alert metadata, repository, file path, and line details. If the alert is still not found, stop. |
| `12` | `SYMFIX_FAILED` | `NO` | `0` | Stop when a SymFix step fails or generated changes cannot be applied. The current SymFix workflow does not allow an in-place retry loop for terminal failures. |
| `13` | `CODE_REVIEW_FAILED` | `NO` | `0` | Stop when code review finds blocking issues or the review step itself fails in a deterministic way. Report the finding and do not continue in the same run. |
| `14` | `BUILD_CHECK_FAILED` | `YES` | `5` | Follow the build-fix workflow exactly. Retry only after applying a different minimal fix strategy for self-caused errors. Stop after 5 failed fix-build cycles. |
| `15` | `PR_CREATION_FAILED` | `CONDITIONAL` | `1` | Retry once only for transient remote failures such as temporary push rejection, service timeout, or PR API failure. Do not retry for permission errors, policy blocks, invalid remote configuration, or unsupported target branch settings. |
| `16` | `INPUT_RESOLUTION_FAILED` | `YES` | `1` | Re-run input resolution once when required metadata is incomplete, inconsistent, or clearly derived from the wrong repository or CodeQL job. If still unresolved, stop. |
| `17` | `SYMFIX_MCP_UNAVAILABLE` | `CONDITIONAL` | `1` | Retry once if the SymFix MCP service is unavailable due to a transient issue. Do not retry if the service is deprecated, the endpoint is wrong, or credentials are invalid. |
| `18` | `NO_CODE_REVIEW_TOOL_AVAILABLE` | `NO` | `0` | Stop when no code review tool is available in the current environment. |

---

## Decision Rules

1. Select the exit code that matches the terminal outcome of the run.
2. If a failure occurs after one or more alerts were fixed, keep the failure exit code and report the completed count in `Fix Status`.
3. Retry only when the classification table explicitly permits it.
4. When a retry is allowed, do not exceed `Max additional retries`.
5. When a retry is not allowed, stop immediately and emit the final output table.
6. When the run succeeds completely, use exit code `0`.
7. When all requested alerts are classified as false positives, also use exit code `0`.

---

## Success Example

| Field | Value |
|---|---|
| Exit Code | `0` |
| Cloned Repo Path | `e:\work\.repo\sample-repo` |
| Alert Details | `AlertId=123,124; QueryId=cs/sql-injection; Statuses=123:FIXED,124:FIXED` |
| Fix Status | `ALL_ALERTS_FIXED (2/2 alerts fixed)` |
| Code Review Output | `PASSED: No blocking findings` |
| Build Check Output | `PASSED: Build succeeded on retry 1/5` |
| PR Link | `https://dev.azure.com/org/project/_git/repo/pullrequest/12345` |

## Failure Examples

### Alert Not Found

| Field | Value |
|---|---|
| Exit Code | `11` |
| Cloned Repo Path | `e:\work\.repo\sample-repo` |
| Alert Details | `AlertId=NOT_FOUND; QueryId=cs/sql-injection; Reason=No alert matched JobId=abcd... after re-checking repository, file path, and line metadata` |
| Fix Status | `NOT_RUN (0/1 alerts fixed)` |
| Code Review Output | `NOT_RUN: Alert resolution failed` |
| Build Check Output | `NOT_RUN: Alert resolution failed` |
| PR Link | `NOT_CREATED: Alert resolution failed before remediation` |

### Build Failed After Retry Budget

| Field | Value |
|---|---|
| Exit Code | `14` |
| Cloned Repo Path | `e:\work\.repo\sample-repo` |
| Alert Details | `AlertId=123; QueryId=cs/sql-injection; Status=FIXED` |
| Fix Status | `PARTIAL_FIX (1/1 alerts fixed)` |
| Code Review Output | `PASSED: No blocking findings` |
| Build Check Output | `FAILED: Build still failing after 5/5 retries due to self-caused type mismatch in SecurityConfig.cs` |
| PR Link | `NOT_CREATED: Build validation did not pass` |