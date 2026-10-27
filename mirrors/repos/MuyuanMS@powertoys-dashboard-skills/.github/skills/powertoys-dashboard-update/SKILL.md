---
name: powertoys-dashboard-update
description: "Update PowerToys Pulse artifacts. Coordinates bounded scheduled updates or an explicitly requested PR-only drain; dispatches PR workers, resumes cloud waits, and publishes validated user-facing results incrementally. Never posts upstream without approval."
---

# PowerToys Dashboard Update

You are the coordinator, not another PR reviewer. Your job is to keep eligible
work moving until validated artifacts are delivered. A saved checkpoint is
progress, not a completed review.

## Choose one execution path

| Request | Read next | Scope |
| --- | --- | --- |
| Start/resume a PR drain | [drain-dispatch.md](./references/drain-dispatch.md) | All eligible PRs; exclude CmdPal only when explicitly requested. No issue work. |
| Scheduled/normal dashboard update | [scheduled-updates.md](./references/scheduled-updates.md) | Exhaustive discovery; bounded PR and issue execution, including CmdPal. |
| Issue triage/design | [issue-triage.md](./references/issue-triage.md) | Issue-specific judgment; approved design workflow remains separate. |

Read [publication.md](./references/publication.md) when ready to publish.
Do not load issue schemas, notification instructions or deployment recipes into
a PR worker. Detailed review policy belongs only to `powertoys-pr-review`.

## Start once, resume thereafter

1. Recover the active owner, workers, saved requests and exact-tree receipts.
   Do not start a competing drain. Preserve existing fork work and dirty files.
2. Use a clean dedicated `main` checkout of
   `MuyuanMS/powertoys-pulse-actions`. Fetch/fast-forward; never reset a dirty
   or divergent checkout. Use a separate clean checkout when necessary.
3. Run `scripts/Assert-CanonicalDashboardTarget.ps1 -Dashboard <checkout>`.
   From that checkout run `Install-Skills.ps1 -Update`, then
   `Install-Skills.ps1 -VerifyOnly`. Reload the four skill entry points and
   record one source revision for the coordinator and workers.

## Coordinator loop

```text
discover live eligible work
repeat:
    reconcile worker completions and due saved cloud requests
    persist their actual results
    publish every newly validated artifact
    execute dispatch assignments into available slots
    if only cloud/build waits remain: arrange the next real wake
    refresh live scope before deciding that the run is finished
until scope is delivered, the normal-run deadline arrives, or only verified exceptions remain
```

Use `Get-StalePrReviewQueue.ps1` for PR discovery and
`Get-PrReviewDispatchPlan.ps1` for assignments. Execute the plan; do not merely
report it. Refill after completion even when the queue has not changed.
Cloud waits use read-only status checks, not occupied heavy workers.
Compilations share one exclusive build slot.
Both normal delta and drain PRs use the same worker loop: at most three total
cloud requests, localized fixes, then validation and drafting, with grounded
architectural early exit. Selection and deadline differ, not review policy.

## Boundaries

- Workers may push their configured fork feature branches, update fork PRs,
  and reply/resolve fork threads. They never write dashboard data or upstream.
  Only the coordinator publishes artifacts.
- No comments, reviews, labels, closes, upstream PRs or other writes to
  `microsoft/PowerToys` without separate explicit approval.
- Canonical artifacts come only from actions `main`. Public `data/` contains
  dashboard-user results and neutral availability metadata, never operational
  blockers, local paths, request counts, credentials or private evidence.
- Keep cloud review required. Use the PR skill's three-request loop and
  architectural exit; do not invent another review policy here.
- A failed PR does not prevent other PRs from delivering. Notifications and
  project synchronization are side effects, not gates for PR review dispatch.

## Report delivered coverage

Report current-head artifacts with findings, clean reviews, justified author
waits, excluded PRs and private exceptions separately. Verify canonical files
and Pulse synchronization before claiming delivery. Pending metadata and
timestamp rewrites never count as reviews. A drain with exceptions is
**incomplete**, not a successful zero-backlog drain.
