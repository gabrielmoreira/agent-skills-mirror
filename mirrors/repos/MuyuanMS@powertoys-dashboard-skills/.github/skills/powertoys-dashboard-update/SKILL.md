---
name: powertoys-dashboard-update
description: "Reliable resumable PowerToys triage-dashboard updater. Exhaustively inventories freshness, processes bounded normal updates or uncapped drain-mode work, checkpoints completed work, and republishes periodically so finished work survives crashes. Does not post upstream reviews/comments or open upstream PRs without explicit approval."
---

# PowerToys Dashboard Update

Use this skill for the scheduled or manual daily refresh of the public
PowerToys triage board:

- "update my PowerToys dashboard"
- "run the daily dashboard update"
- "refresh the PowerToys triage queue"
- "check old work and find new issues/PRs"

The skill is an **orchestrator**, not a replacement for the three execution
skills:

- `powertoys-pr-review` — review a community PR in the fork until the Copilot
  review loop is clean, then draft proposed upstream review actions.
- `powertoys-issue-to-design` — triage a bug, investigate it, run the
  investigator/adversary loop, and stop at the design gate.
- `powertoys-design-to-pr` — turn an approved fork design into a reviewed,
  build-verified fork PR and stop before opening upstream.

## Safety rules

1. Read upstream freely, but never post an upstream review/comment, open an
   upstream PR, close/label/assign upstream, or create a cross-reference
   without explicit user approval.
2. Fork-side mirrors, branches, Copilot review loops, and local builds are
   allowed. Preserve each sub-skill's approval gates.
3. Never duplicate existing fork work. Resume the existing mirror issue or
   fork PR after checking its current state.
4. Do not publish PATs, tokens, local paths, or private notes to the artifact
   repository.
5. Every run must regenerate and publish `data/index.json`, `data/index.js`, and
   `data/items/<number>.json` before heavy agent work and after each completed
   batch. A non-empty stale queue is valid when deferred items remain explicit.
6. PowerToys Pulse is the user-facing dashboard. After publishing artifacts,
   synchronize and validate Pulse, then deploy only an approved Pulse branch or
   workflow. Do not substitute the artifact repository's Pages site as the
   final preview.
7. The only canonical skill and action-data repository is
   `MuyuanMS/powertoys-pulse-actions`. Before reading or writing checkpoints,
   generating data, or publishing, run
   `scripts/Assert-CanonicalDashboardTarget.ps1`. Never update or push
   `MuyuanMS/powertoys-triage-board`; it is a retired standalone prototype.

## Configuration

```powershell
$Upstream = 'microsoft/PowerToys'
$Dashboard = if ($env:POWERTOYS_DASHBOARD_PATH) {
  (Resolve-Path $env:POWERTOYS_DASHBOARD_PATH).Path
} else {
  (git rev-parse --show-toplevel).Trim()
}
$SkillRoot = Join-Path $Dashboard '.github\skills\powertoys-dashboard-update'
$ForkOwner = if ($env:POWERTOYS_FORK_OWNER) {
  $env:POWERTOYS_FORK_OWNER
} else {
  (gh api user --jq '.login').Trim()
}
$Fork = if ($env:POWERTOYS_FORK_REPO) {
  $env:POWERTOYS_FORK_REPO
} else {
  "$ForkOwner/PowerToys"
}
$Board = 'MuyuanMS/powertoys-pulse-actions'
$Since = (Get-Date).AddDays(-2).ToUniversalTime().ToString('o')
$IssueWindowDays = 30
$DrainReviewQueue = $env:POWERTOYS_DASHBOARD_DRAIN_QUEUE -eq '1'
$DesignBatchSize = if ($env:POWERTOYS_DESIGN_BATCH_SIZE) { [int]$env:POWERTOYS_DESIGN_BATCH_SIZE } elseif ($DrainReviewQueue) { [int]::MaxValue } else { 4 }
$PrReviewBatchSize = if ($env:POWERTOYS_PR_REVIEW_BATCH_SIZE) { [int]$env:POWERTOYS_PR_REVIEW_BATCH_SIZE } elseif ($DrainReviewQueue) { [int]::MaxValue } else { 16 }
$PrReviewConcurrency = if ($env:POWERTOYS_PR_REVIEW_CONCURRENCY) { [int]$env:POWERTOYS_PR_REVIEW_CONCURRENCY } elseif ($DrainReviewQueue) { 6 } else { 3 }
$RunBudgetMinutes = if ($env:POWERTOYS_DASHBOARD_RUN_BUDGET_MINUTES) { [int]$env:POWERTOYS_DASHBOARD_RUN_BUDGET_MINUTES } elseif ($DrainReviewQueue) { 0 } else { 50 }
$RunStartedAt = (Get-Date).ToUniversalTime().ToString('o')
$ProjectOwner = if ($env:POWERTOYS_PROJECT_OWNER) { $env:POWERTOYS_PROJECT_OWNER } else { 'microsoft' }
$ProjectNumber = if ($env:POWERTOYS_PROJECT_NUMBER) { [int]$env:POWERTOYS_PROJECT_NUMBER } else { 2445 }
$BoardOwner, $BoardName = $Board -split '/', 2
$ArtifactBaseUrl = if ($env:POWERTOYS_ARTIFACT_BASE_URL) {
  $env:POWERTOYS_ARTIFACT_BASE_URL.TrimEnd('/')
} else {
  "https://raw.githubusercontent.com/$BoardOwner/$BoardName/main/data"
}
$Pulse = if ($env:POWERTOYS_PULSE_REPO) { $env:POWERTOYS_PULSE_REPO } else { 'gim-home/powertoys-pulse' }
$PulsePreview = if ($env:POWERTOYS_PULSE_PREVIEW_REPO) { $env:POWERTOYS_PULSE_PREVIEW_REPO } else { 'MuyuanMS/powertoys-pulse-action-private' }
$NotifyOutlook = if ($env:POWERTOYS_DASHBOARD_NOTIFY) { $env:POWERTOYS_DASHBOARD_NOTIFY -ne 'none' } else { $true }
```

On the first run, verify:

```powershell
gh auth status
gh repo view $Fork
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Assert-CanonicalDashboardTarget.ps1" `
  -Dashboard $Dashboard
```

Run this skill from the `MuyuanMS/powertoys-pulse-actions` repository root, or
set `POWERTOYS_DASHBOARD_PATH` to a checkout of that exact repository. The
other three skills must be present beside it under `.github\skills`. The target
repository is intentionally not overrideable.

The configured repository is both the reusable skill suite and canonical
artifact feed. Generated files belong only in its root `data/` directory, not
inside `.github\skills`. Never place secrets or information that must remain
private in the public feed.

### Dashboard action taxonomy

Pulse action proposals are maintainer-facing actions only. Status, freshness,
queue state, validation gaps, and "wait/do nothing" choices remain metadata and
must not appear as clickable action proposals.

Update this table when a new action type is intentionally introduced, then
update `emit.ps1`, `Sanitize-ActionData.ps1`, Pulse's triage action filter, and
the dashboard artifact validators in the same change.

| Item | Allowed action type | Dashboard meaning | Must contain | Not allowed as an action |
| --- | --- | --- | --- | --- |
| PR | `approve` | Submit/choose approval for a review-clean PR. | Current `head_sha`, covered `source_updated_at`, no unresolved agent findings. | Native validation still pending, queued review, owned elsewhere, re-run prompt. |
| PR | `post_review` | Post selected code suggestions or non-blocking review comments. | Proposed comments pinned to the current head; inline comments use current RIGHT-side ranges when possible. Event must be `COMMENT`; inline-only reviews omit the overall review body. | `REQUEST_CHANGES`, a generic overall message for inline-only suggestions, general "keep checking", "complete validation", or product-direction reminders without a publishable review body. |
| PR | `request_changes` | Post selected blocking review comments as a request-changes review. | Same evidence and current-head requirements as `post_review`. | A standalone request to run the review loop again. |
| PR | `trigger_ci` | Post `/azp run` to request an Azure Pipelines run when live checks are failed, cancelled, timed out, stale, or missing. | Exact comment body `/azp run`; current live head/check state displayed to the maintainer; explicit confirmation before posting. | Posting while all checks pass, treating CI as a substitute for review/build evidence, or auto-posting without a maintainer click. |
| Issue | `request_info` | Ask the reporter for specific missing evidence. | An issue-specific upstream comment that summarizes the relevant facts already supplied, explains why they are insufficient, asks for exact missing evidence, and gives the established collection method when one exists (for example, `/bugreport` for a fresh PowerToys diagnostic ZIP). | "Not now", wait, monitor, a generic checklist, or "send logs/more information" without explaining the gap. |
| Issue | `approve_design` | Approve/start a fork-side fix plan after design convergence. | Detailed design artifact and fork issue/trace for the fix workflow. | A speculative or incomplete design. |
| Issue | `post_comment` | Post a close, duplicate, handled, out-of-scope, or maintainer-direction comment. | Specific rationale and linked duplicate/fix/ownership evidence when applicable. | Silent close, vague "won't fix", or no-op status comments. |
| Issue | `open_upstream_pr` | Open the completed fork fix upstream. | Fork PR/head, implementation evidence, and approval gate. | Opening without explicit approval or without a reviewed fork fix. |

Forbidden action types in public artifacts include `hold`, `rerun`,
`continue_review`, `review_summary`, `monitor`, `start_review`, and
`start_triage`. These may be retained as internal workflow/status metadata, but
Pulse must not render them as executable action proposals.

### Reliability contract

Normal runs are bounded and resumable. They must finish within the 50-minute
default run budget instead of trying to drain an arbitrarily large review queue:

- inventory every eligible PR and changed bug, but select at most
  `$PrReviewBatchSize` PRs and `$DesignBatchSize` full designs for execution;
- run at most `$PrReviewConcurrency` PR workers at once;
- select up to sixteen PRs by default so workers that checkpoint an external
  Copilot wait release their slots to additional queued PRs while still capping
  active heavy local work;
- treat cloud-review waiting as a persisted queue stage, not an active worker:
  request the review, checkpoint `waiting_copilot`, return the worker slot, and
  inspect the result on the next scheduler pass;
- never let a PR worker launch another subagent; the worker performs its review
  directly and may use external GitHub Copilot review as required;
- give each worker the exact UTC deadline from the run plan and require it to
  stop cleanly with durable `review_in_progress` state before that deadline;
- publish the refreshed inventory before launching workers, then publish each
  completed artifact without waiting for the full queue;
- checkpoint every durable transition locally and publish after two transitions,
  after eight minutes, or at run completion, whichever comes first;
- leave unselected or unfinished items explicitly queued for the next run;
- ensure every open, non-draft PR that is not waiting on the author is either
  backed by an allowed PR action from the taxonomy above, explicitly marked as
  pending author feedback, or shown as queued/internal status without a
  clickable Pulse action.

`POWERTOYS_DASHBOARD_DRAIN_QUEUE=1` is an exceptional operator-requested mode.
Drain mode intentionally removes the PR selection limit, issue design cap, and
run deadline. It selects every stale PR, runs up to six PR workers at once by
default, processes all actionable issue designs, and continues until the stale
queue is empty or an unrecoverable blocker is published. Drain mode still must
checkpoint every durable fork/mirror/review transition immediately and publish
after two transitions, after five minutes, or after any completed artifact,
whichever comes first, so completed work and resumable fork traces survive a
frozen or crashed session. Do not use drain mode in scheduled or ordinary manual
runs unless the operator explicitly requested it.

### Scheduled-run status notifications

Scheduled runs are hard to observe from the CLI, so send compact status
notifications through Outlook when M365/WorkIQ tools are available.
`POWERTOYS_DASHBOARD_NOTIFY=none` disables these emails; all other values send
Outlook mail to the signed-in user.

Read `/me?$select=mail,userPrincipalName` and send to
`mail ?? userPrincipalName` via `/me/sendMail`. The first message is the run's
status thread. After sending it, look it up in Sent Items by subject and
timestamp so later updates can reply to the original message with
`/me/messages/{message-id}/reply`. If the original message id cannot be found,
send a new message with the same subject prefixed by `Re:`. If M365 tools are
unavailable or delivery fails, record that in the final report and continue the
dashboard run.

Keep messages brief and clear. Send:

1. **Started** — after the live queue and bounded run plan are enumerated.
   Include selected PRs, deferred PR count, changed/new bug issues, selected
   full-design issues, the concurrency cap, and the UTC deadline. In drain
   mode, state that the deadline, PR selection limit, and issue design cap are
   disabled, and include the higher worker count.
2. **30-minute checkpoint** — if the run is still active 30 minutes after the
   started email, reply to the original with completed PRs/issues, currently
   running PRs/issues, remaining queue count, and next expected milestone.
3. **Completed** — reply to the original after validation and deployment
   verification, with commit, PR/issue coverage, stale queue count, artifact
   count, and whether any upstream public action occurred.
4. **Blocked/failed** — reply to the original before stopping on an
   unrecoverable failure, with the failing phase and the next manual action
   needed.

For incremental publishes before the 30-minute checkpoint, do not send noisy
extra mail unless it materially changes the user's action needed; roll those
details into the checkpoint or completed reply.

Keep notification bodies public-safe: no PATs, local checkout paths, fork-only
implementation provenance, private evidence, or internal worktree details.
These notifications are status messages only and do not authorize posting
reviews/comments to `microsoft/PowerToys`.

## Phase 0 — Sync and load prior state

1. Check the fork's divergence and sync `main` with upstream when behind:

```powershell
gh api "repos/$Upstream/compare/main...${ForkOwner}:main" `
  --jq '{behind_by,ahead_by,status}'
gh api --method POST "repos/$Fork/merge-upstream" `
  --input (@{branch='main'} | ConvertTo-Json)
```

2. Read the latest board index and all existing artifacts. Treat these fields
   as the durable freshness contract:

   - `generated_at` — when the artifact file was emitted;
   - `evaluated_at` — when an agent last made a substantive judgment;
   - `source_updated_at` — upstream `updatedAt` covered by that judgment;
   - `head_sha` — exact upstream PR head covered by the latest code review;
   - `judgment.status` — the latest lightweight issue classification.

   Do not use `generated_at` alone as evidence that an item was reviewed. An
   unchanged artifact copied by the emitter keeps its old `evaluated_at`,
   `source_updated_at`, and `head_sha`.
3. Inventory fork traces:

```powershell
gh pr list -R $Fork --state all --json number,title,state,headRefName,updatedAt,url --limit 200
gh issue list -R $Fork --state all --json number,title,state,updatedAt,url --limit 200
```

Map `[PR N]`, `[Issue N]`, `(Issue N)`, `pr-iterate/N`, and
`copilot/issue-N-...` back to upstream numbers.
For PR reviews, also run `Get-ReviewResumeState.ps1` and preserve durable
branches, review PRs, worktrees, round counts, and unresolved-thread state.

4. Synchronize the PowerToys project board with
   `$SkillRoot\scripts\Sync-PowerToysProject.ps1`. The script is safe to run with
   `-DryRun` while project permissions are being configured. It adds open,
   non-draft PRs that are not already in project 2445 and updates
   existing items:

   - agent-produced review artifacts with suggested comments → `To manually review`;
   - a recognized member's upstream review/comment → `In Review` or the named
     option (`In Review: MuyuanMS`, `In Review: LegendaryBlair`, or
     `In Review: moooyu`) when that option exists;
   - closed or merged items → `Done`.

   Items with no recognized decision remain in their current project status,
   normally `To triage`. Project synchronization never posts upstream content.

## Phase 1 — Build the complete freshness queue

Every run must enumerate **all** open upstream items before selecting work.
Do not limit PR discovery to `$Since`; `$Since` is only an optimization for
activity queries. Join the live list to artifacts and fork traces by upstream
number.

### PR freshness

Every open, non-draft PR must end the run in exactly one state:

- **current clean review** — artifact `head_sha` exactly matches the live head,
  the latest freshly requested Copilot pass has zero new comments and zero
  unresolved threads, required builds/context checks passed, and
  `source_updated_at` covers the latest relevant PR activity;
- **queued/running review** — no current clean result exists;
- **waiting on author** — a posted/requested change is still outstanding and
  the author has not pushed or replied;
- **owned elsewhere** — a recognized maintainer is actively reviewing it;
- **excluded** — draft, closed, or otherwise outside this workflow.

A **full re-review is mandatory** when the live head SHA differs from
`head_sha`, `head_sha` is missing, or there is no clean artifact. If the head is
unchanged but comments/reviews changed after `source_updated_at`, perform a
focused context revalidation. Rerun the full review only when that activity
changes requirements, reveals a concern, resolves author-waiting state, or
invalidates the prior decision. Otherwise advance `evaluated_at` and
`source_updated_at` without pretending a new code review occurred.

Do not classify a PR as waiting on author from "who commented last" or from a
generic maintainer comment alone. Preserve `pending_author` only when current
live evidence supports it: a needs-author-feedback label, a current
changes-requested review after the author's latest activity, or posted Pulse
review comments that have not been followed by an author commit/comment/review.
If the author has pushed or replied after the author-wait signal, clear
`pending_author`, mark the artifact `needs_revalidation`, and put the PR back
in the review queue so the update agent makes a fresh decision.

Never skip an eligible PR merely because it is old or absent from the recent
activity query. Never re-review an unchanged, converged head with no newer
relevant activity.

### Mandatory stale-review queue gate

Before publishing, run the stale-review queue check:

```powershell
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Get-StalePrReviewQueue.ps1" `
  -Dashboard $Dashboard -Upstream $Upstream -AsJson
```

The queue contains every open, non-draft PR that is not explicitly
waiting on the author, owned elsewhere, dropped, awaiting a maintainer
direction/close/takeover decision, or excluded, and that either:

- has no dashboard artifact with a current review action for the live upstream
  head (`post_review` for drafted findings, or `review_ready`/no-comment action
  for a clean looped review); or
- has a prior proposed review, but the live head SHA differs from the artifact
  or review action head SHA.

The queue is exhaustive. Build the run plan:

```powershell
$runPlanArgs = @(
  '-NoProfile', '-File', "$SkillRoot\scripts\Get-PrReviewRunPlan.ps1",
  '-Dashboard', $Dashboard, '-Upstream', $Upstream,
  '-BatchSize', $PrReviewBatchSize,
  '-MaxConcurrency', $PrReviewConcurrency,
  '-RunBudgetMinutes', $RunBudgetMinutes,
  '-AsJson'
)
if ($DrainReviewQueue) { $runPlanArgs += '-DrainQueue' }
pwsh @runPlanArgs
```

In normal mode, send only `selected_prs` through or resume them in
`powertoys-pr-review`; publish `deferred_prs` as queued work for later runs. In
drain mode, `selected_prs` is the full stale queue and `deferred_prs` must be
empty unless an unrecoverable blocker is published. A metadata-only refresh is
still insufficient: every run must either advance its selected work or honestly
retain durable in-progress state. Use `-FailOnStale` only in explicit drain
mode after all selected work has either completed or reached a durable blocked
state.

### Fast issue judgment

Every open `Issue-Bug` issue with no `judgment`, or with live `updatedAt` newer
than `source_updated_at`, receives a lightweight judgment during the run. This
pass is deliberately cheaper than `powertoys-issue-to-design`: inspect the
body, latest comments, labels, assignees, linked PRs/issues, and obvious
repository ownership signals, then emit one of:

| `judgment.status` | Dashboard result |
| --- | --- |
| `actionable_design` | Confidence-scored proposed fix plan and `Design fix` action; candidate for the bounded full-design batch |
| `reproducible` | `Reproduce` action with maintainer-ready local verification steps |
| `needs_information` | Draft a specific `request_info` action describing exactly what evidence is missing |
| `duplicate_or_handled` | Link the duplicate/fix/owned work; no duplicate agent work |
| `waiting_on_author` | Preserve the requested evidence and waiting-since timestamp |
| `not_actionable` | Explain feature/by-design/external/hardware/insufficient-scope reason |

Each judgment must contain `rationale`, concrete `evidence`, a
`recommended_action`, `evaluated_at`, and `source_updated_at`. The fast pass
may describe a root-cause hypothesis, but must distinguish it from confirmed
evidence and score it honestly.

Every new or substantively refreshed open bug must use `schemaVersion: 5` and
include `fix_assessment`:

- `status: proposed` when no existing fix attempt is present and a repository
  change is applicable. Include at least one `proposed_fixes[]` entry with a
  concrete root-cause hypothesis, ordered implementation plan, verification
  steps, and numeric confidence.
- `status: existing_fix` when an open/merged PR, active fork implementation, or
  other concrete fix attempt already covers the issue. Include the public URLs
  and explain the coverage; do not invent a competing plan.
- `status: not_applicable` only when a PowerToys code fix is genuinely not
  applicable, such as duplicate/handled work, expected behavior, unsupported
  hardware/external ownership, or insufficiently scoped non-bug reports.

Confidence is `0..100` and the level must match the score:

- `green` (`85..100`) — the evidence almost certainly identifies the root
  cause and fix.
- `yellow` (`51..84`) — the plan is more likely than not, but targeted
  reproduction or specific additional evidence would materially improve it.
- `red` (`0..50`) — the best current hypothesis, with no more than even odds
  that it is the correct root cause/fix.

For a red plan, the updater may run a short investigator/adversary loop of one
or two iterations before publication. Use it when focused code/history review
can cheaply test the hypothesis. Stop after two iterations, keep the red score
if uncertainty remains, and pair the plan with a targeted `request_info` or
`reproduce` action when that evidence would distinguish competing causes. Do
not force a full implementation-grade design or fabricate confidence merely to
turn the plan yellow.

Before defaulting to a request for logs or `/bugreport`, perform a focused
initial investigation using the issue body, discussion, labels, linked issues,
linked PRs, likely owning code area, and recent history/duplicates that can be
checked without a full implementation pass. If that investigation can identify
a plausible root cause or fix plan with useful confidence, emit that as a
design/fix path instead of only pushing the reporter for more information.

Every new or substantively refreshed issue artifact that exposes an action must
use `schemaVersion: 5` and include display-only `issue_context`:

- `summary` — a concise synthesis of the report and discussion, not a copy of
  the title or issue body;
- `known_information` — concrete facts already supplied by the reporter,
  commenters, labels, attachments, linked work, or live repository state;
- `inferences` — only conclusions supportable from those facts, phrased with
  uncertainty and never presented as confirmed root cause;
- `analysis` — the Copilot triage reasoning that connects the evidence to the
  proposed maintainer action;
- `initial_investigation` — focused code, history, duplicate, ownership, or
  diagnostic findings gathered during the lightweight pass;
- `information_gaps` — for each missing item, record `information`,
  `why_needed`, and, when known, `how_to_collect`.

This context is public, read-only decision support for the Pulse action window.
It is not part of `actions[].comment.body`, is not editable, and must never be
appended to the upstream comment automatically. Keep facts and inferences
separate. Do not publish private notes, unsupported speculation, local paths,
credentials, or sensitive diagnostic contents.

For `needs_information`, read the entire issue body and discussion before
drafting. The comment must acknowledge the useful issue-specific information
already present, identify the exact ambiguity or decision it cannot resolve,
then request only evidence that would change triage or implementation. Reuse
established PowerToys collection conventions instead of inventing generic
instructions:

- when a fresh PowerToys diagnostic archive is needed, ask the reporter to
  submit a comment containing `/bugreport`; explain that the generated ZIP
  should be captured immediately after reproducing the problem;
- ask for recordings, screenshots, Event Viewer entries, installer logs,
  configuration exports, versions, or numbered reproduction steps only when
  they address a specific recorded gap;
- if an attachment or prior answer already supplies an item, do not ask for it
  again;
- do not paste a standard multi-item checklist into unrelated issues.

The editable `request_info` comment and display-only context must agree:
`actions[].comment.body` asks for the same gaps recorded under
`issue_context.information_gaps`, and any gap whose `how_to_collect` names
`/bugreport` must use `/bugreport` in the proposed comment.

When the evidence supports it, emit multiple issue actions rather than a single
default request-info path: an `approve_design` action for the best currently
supportable fix plan, plus a `request_info` action that asks only for evidence
that would materially improve or disprove that plan. The display-only
`proposed_fixes[].confidence` is the canonical score shown by Pulse. Prefer
this split for vague or long issues where the discussion already narrows the
component but still lacks a decisive diagnostic.

When an issue is already clearly reproducible from the public report or
attachments but does not yet justify a fix design, emit a `reproduce` action
instead of asking the reporter for more logs. The action must include the
PowerToys module, version/build requirement when relevant, prerequisites,
numbered reproduction steps, expected result, and any setup requirements. If
the repro needs external assets (for example, a file over a threshold size or a
specific file shape), include `reproduce.setup_prompt` so Pulse can copy a
prompt the maintainer can paste into a local agent to prepare those files, or
link public issue attachments in `reproduce.attachments`.

Older unchanged bugs do not need to be re-read every run, but they must retain
their prior explicit judgment/action in the board. The 30-day window controls
full-design priority, not whether changed issues receive a judgment.

Issue action freshness is anchored to the latest upstream issue activity, with
latest comments being the decisive signal. A proposed issue action is current
only when `source_updated_at` covers the live issue `updatedAt`/latest comment
time. If a newer comment exists, do not expose the old request-info, close, or
fix action as actionable; mark the item for triage revalidation and publish
that queued state instead.

Do not emit placeholder issue controls. Issue artifacts should only include
concrete maintainer actions that can be executed from Pulse: request a specific
piece of information, post a close/dedupe/out-of-scope comment, approve/start a
fix design, guide a maintainer through a local reproduction, or open an
upstream PR from a completed fork fix. Do not include `hold`/`Not now` actions,
and do not publish issue artifacts whose only action is to wait.

For every artifact and mapped fork trace, also detect:

- upstream PR/issue closed, merged, superseded, or linked work appeared;
- labels, assignee, author response, or reproduction evidence changed;
- a fork mirror/PR was closed, merged, or replaced.

For open PRs, query the current head's check runs when permissions allow.
Classify the aggregate as passed, pending, failed, or unavailable/missing.
Pulse may synthesize a `trigger_ci` action from this live state when the checks
failed, were cancelled/timed out/stale, or no check run exists. Do not offer a
rerun while checks are already pending, and never post `/azp run`
automatically.

Use focused API calls rather than downloading the whole repository:

```powershell
gh pr view $Number -R $Upstream --json state,isDraft,headRefName,commits,reviews,comments,updatedAt
gh issue view $Number -R $Upstream --json state,labels,assignees,comments,body,updatedAt
```

Classify unfinished workflow state:

- **still current** — artifact can remain actionable;
- **needs re-review** — rerun `powertoys-pr-review` against the new PR head;
- **needs re-triage/design** — rerun `powertoys-issue-to-design`;
- **author action** — do not rerun; show waiting-on-author;
- **closed/superseded** — retain history but remove from the open backlog;
- **duplicate/handled** — record the linked upstream work and do not duplicate it.

## Phase 2 — Resume or rerun workflows

PR inventory is exhaustive. Normal execution is bounded to the run plan:
process only the selected batch, with at most three active workers by default.
The default batch contains sixteen PRs so cloud waits can release slots and let
other PRs advance without increasing local build concurrency. Drain mode is the
only mode that may select every stale PR in one conversation; it runs up to six
active workers by default and relies on checkpointed fork branches plus
incremental publication instead of a time cap. Prioritize resumable in-progress
reviews, stale proposed reviews, stale artifact heads, then missing artifacts.
Do not re-review an unchanged head that already has a current clean fork result
and no relevant newer activity.
Do not call a PR review complete, approval-ready, or "clean" unless the latest
freshly requested Copilot review has zero new comments, zero unresolved threads,
and the required local build has passed. A Copilot-clean result with a pending
build, context review, spelling check, or timed-out fresh request remains
`review_in_progress` and must get a `Re-run review`/`Continue review` action.

In normal mode, each worker receives the run-plan deadline and must stop
initiating new review rounds or builds 10 minutes before it. If it cannot
converge, it writes durable `review_in_progress` state and returns. In drain
mode, workers do not receive a stop deadline; they still must checkpoint every
fork, mirror, review-request, finding, and build transition so a later run can
resume from the fork branch or dashboard artifact after a crash. Do not keep
polling simply to make the current run look complete. Do not launch nested
agents from a PR worker.

Use `Set-PrReviewCheckpoint.ps1` after each durable transition:

```powershell
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Set-PrReviewCheckpoint.ps1" `
  -Dashboard $Dashboard -Number $Number -HeadSha $LiveHead `
  -SourceUpdatedAt $LiveUpdatedAt -Phase waiting_copilot `
  -Detail "Fresh fork review requested; the next run will inspect the result." `
  -ForkPr $ForkPr -ForkBranch $ForkBranch -Fork $Fork
```

Required checkpoint phases are: selected/`queued`, fork setup/`mirroring`,
review request/`review_requested`, external wait/`waiting_copilot`, finding
work/`reviewing_findings`, and local validation/`building`. A worker waiting on
GitHub Copilot performs one immediate status check only; if the result is not
ready, it checkpoints and returns instead of polling.

### Incremental publication during long PR loops

Long-running PR reviews must not block fresh dashboard data. Before launching
workers, regenerate and publish the inventory with `-AllowStaleReviewQueue`.
Checkpoint every stage transition locally immediately. In normal mode, after
two checkpoint transitions, eight elapsed minutes, or any completed artifact,
regenerate, sanitize, validate, commit, and push without waiting for remaining
selected PRs. In drain mode, use the same transition/completion triggers and a
five-minute maximum publish interval.
Regenerate and sanitize the feed, validate the completed PR numbers, run the
stale-review queue check without `-FailOnStale`, and commit/push the completed
artifacts plus index updates. The dashboard must show still-running PRs as
queued/running review, not as current.

At the normal-mode run deadline, publish completed/in-progress state and stop
cleanly. In drain mode, continue through additional work until the stale queue
is empty or a published blocker remains. Report selected, completed,
in-progress, and deferred counts. Run the `-FailOnStale` gate only in explicit
drain mode after the drain attempt finishes.

Issue **judgment** is exhaustive for new/changed bugs. Normal-mode full design
work is bounded: rank `actionable_design` judgments by confidence,
reproducibility, scope, recency, and lack of existing ownership, then run at
most `$DesignBatchSize` (default 4) through `powertoys-issue-to-design`; leave
the rest queued with explicit `Design fix` actions. Drain mode removes this
design cap and processes every actionable issue design, still checkpointing and
publishing after each durable transition or completed artifact. Prefer issues
updated in the last `$IssueWindowDays`, then consume older actionable issues as
capacity allows.

For each queued item, invoke the corresponding skill with the upstream number
and complete its fork-side loop. Do not bypass its gates:

The retired custom `pr-iterate` agent must not be launched. `pr-iterate/<N>`
remains the durable fork branch naming convention used by
`powertoys-pr-review`; the current execution path is the `powertoys-pr-review`
skill itself, using a general-purpose worker when parallel background execution
is needed. That worker must not delegate to another agent.

- PR: `powertoys-pr-review` must reach zero new Copilot comments and zero
  unresolved Copilot threads before a new artifact is emitted. For stale-review
  queue items, the emitted artifact must include `head_sha` and any
  `post_review` action `review.head_sha` pinned to the live upstream head.
- Issue: `powertoys-issue-to-design` must reach a converged adversary-reviewed
  implementation-grade design and stop at approval.
- Approved design: `powertoys-design-to-pr` may build/review the fork PR but
  stops before opening the upstream PR unless separately approved.

If a workflow is waiting on an author or user approval, do not rerun it just to
make activity; preserve that status. A queued item must retain an explicit
fork trace or dashboard action even when its execution is deferred.
Draft every supported, current-head review finding as a proposed upstream
review comment. Prefer an inline suggestion when the finding is localized to a
current RIGHT-side diff range and can contain one apply-ready `suggestion`
block. Do not require an inline anchor to draft the review: architectural,
cross-file, out-of-diff, validation, or coordination findings belong in normal
body comments and must still produce a pinned `post_review` action.

Emit `post_review` with review event `COMMENT`. When every proposed comment is
inline, omit `review.body_prefix` so GitHub receives only the selected inline
comments and no overall review message. Use `request_changes` only for a
deliberate blocking review; never encode a request-changes event inside a
`post_review` action. Pulse may let the maintainer explicitly change the final
submission from Comment to Request changes, but the generated artifact remains
non-blocking by default.

Do not collapse every concrete code fix into broad companion notes. When the
converged fork contains a localized fix on a current upstream diff line, emit
an `inline`/`in_diff: true` item with the exact range and apply-ready
`suggestion` block. For every other supported finding, emit a non-inline
proposed comment that explains the concern, its impact, and the required
follow-up; never replace it with a generic local `review_summary` action
merely because an inline suggestion is unavailable. Label companion-only
reviews `Post general review notes` and disclose `general review notes — no
inline suggestions`.

Use a local manual-review or validation action only when no defensible
author-facing comment can be drafted from the current head—for example, the
review lacks sufficient evidence, the finding was superseded, or maintainers
must first choose product direction. The iteration cap ends automated loops;
it does not end drafting supported inline or normal review comments.

### Required issue-design artifact

A completed design is not acceptable when it only says “change component X.”
The artifact and fork mirror must contain:

1. **Root cause and evidence** — the failing mechanism, call/data flow, and
   issue/log/code evidence that supports it; distinguish facts from inference.
2. **Affected files** — exact repository-relative paths, each file's role, and
   the relevant classes/functions/symbols.
3. **Implementation steps** — ordered, one logical change per step, each with:
   - exact file path and symbol(s);
   - current behavior/control flow;
   - the new behavior/control flow;
   - a focused pseudo-diff or code-block sketch of the key logic to change;
   - error handling, lifetime/threading/state concerns, and edge cases;
   - tests that prove that step.
4. **Verification** — exact targeted build/test commands where known, plus
   launch and E2E reproduction steps with expected outcomes.
5. **Risk and alternatives** — blast radius, compatibility/migration concerns,
   rejected alternatives, and confidence rationale.

The code-block sketch is design guidance, not an apply-ready patch. It must be
specific enough that another engineer can locate and implement the key change
without repeating the investigation. If exact symbols cannot be identified,
the design is not ready: return to investigation or mark it
`needs_information`.

Write these machine-readable fields into `data/items/<number>.json`:

```jsonc
{
  "schemaVersion": 5,
  "evaluated_at": "UTC ISO",
  "source_updated_at": "upstream updatedAt covered by this result",
  "judgment": {
    "status": "actionable_design",
    "rationale": "...",
    "evidence": ["..."],
    "recommended_action": "..."
  },
  "fix_assessment": {
    "status": "proposed",
    "rationale": "No existing fix attempt covers the likely failing path."
  },
  "proposed_fixes": [
    {
      "title": "Rebuild the stale activation target before launch",
      "root_cause": "The cached target can outlive the source result and is reused during activation.",
      "plan": [
        "Locate the activation target cache and its invalidation boundary.",
        "Re-resolve the target when the source result version changes.",
        "Add focused coverage for stale-result activation."
      ],
      "verification": [
        "Reproduce the original activation sequence and confirm the latest target launches."
      ],
      "confidence": {
        "score": 72,
        "level": "yellow",
        "rationale": "The code path matches the symptom, but a reporter trace would confirm the stale-cache branch."
      }
    }
  ],
  "issue_context": {
    "summary": "Concise synthesis of the report and discussion.",
    "known_information": ["Confirmed fact already present in the issue."],
    "inferences": ["Evidence-supported possibility, explicitly qualified."],
    "analysis": "Why the evidence supports the proposed action.",
    "initial_investigation": ["Focused code/history/duplicate finding."],
    "information_gaps": [
      {
        "information": "Exact missing evidence",
        "why_needed": "Decision this evidence will resolve",
        "how_to_collect": "Comment /bugreport immediately after reproducing"
      }
    ]
  },
  "design": {
    "root_cause": "...",
    "evidence": ["..."],
    "affected_files": [
      { "path": "src/...", "purpose": "...", "symbols": ["Class::Method"] }
    ],
    "implementation_steps": [
      {
        "order": 1,
        "file": "src/...",
        "symbols": ["Class::Method"],
        "current_behavior": "...",
        "change": "...",
        "code_block": "focused pseudo-diff or key code sketch",
        "edge_cases": ["..."],
        "tests": ["..."]
      }
    ],
    "verify": ["..."],
    "risks": ["..."],
    "alternatives": ["..."]
  }
}
```

## Phase 3 — Discover new work

Query current open non-draft upstream work since `$Since` and include older
items with new activity:

```powershell
gh pr list -R $Upstream --state open --json number,title,author,labels,createdAt,updatedAt,isDraft,url --limit 200
gh issue list -R $Upstream --state open --json number,title,author,labels,createdAt,updatedAt,url --limit 200
```

Candidate rules:

- Issues: consume the Phase 1 fast judgments. Only `actionable_design` enters
  the full-design queue; the other statuses already have explicit actions.
- PRs: community-authored, non-draft, and no meaningful maintainer/reviewer
  ownership or existing fork trace. If labels do not identify the area, inspect
  the title, changed files, linked issue, and description before routing it.

Rank candidates using:

- PRs: close to merge, fewer unresolved concerns, newer activity, and prior
  maintainer involvement;
- issues: easy reproduction/verification, low risk, small scope, and clear
  acceptance criteria.

In normal mode, run only the bounded top candidates through the relevant
sub-skill and report the remaining candidates without starting them. In drain
mode, keep consuming candidates until no selected PRs or actionable issue
designs remain, while preserving the higher worker cap and incremental publish
requirements.

## Phase 4 — Emit artifacts and update PowerToys Pulse

Run the v3 generator once before heavy fork-side work and again after each
completed batch:

```powershell
pwsh -NoProfile -File "$Dashboard\emit.ps1" -AllowStaleReviewQueue
pwsh -NoProfile -File "$Dashboard\Sanitize-ActionData.ps1"
```

The generator preserves valid per-number artifacts written by review workers;
it must not delete worker output merely because an item is not in the
hand-authored overlay. The sanitizer removes internal-only fields and
normalizes local checkout paths before publication. Run both only after worker
writes are complete when possible, and verify the resulting `artifact_numbers`
includes every completed review from the run. `emit.ps1` runs the stale-review
queue gate itself and fails by default when any applicable PR lacks a current
looped review for its live head. Normal bounded runs therefore use
`-AllowStaleReviewQueue` for both initial and final publication. In drain mode,
use `-AllowStaleReviewQueue` for intermediate publishes while work remains, and
omit it only for the final gate after all selected work has reached a durable
completed, author-waiting, owned-elsewhere, excluded, or blocked state.

In drain mode only, enforce the stale-review queue gate:

```powershell
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Get-StalePrReviewQueue.ps1" `
  -Dashboard $Dashboard -Upstream $Upstream -FailOnStale
```

In normal mode, rerun the queue command without `-FailOnStale`, publish the
remaining queue, and finish successfully. Do not repair stale items by copying
timestamps or head SHAs into artifacts; only a completed looped review,
author-waiting classification, owned-elsewhere classification, or explicit
exclusion clears a PR.

For incremental publication while review workers are still running, run the
same queue command without `-FailOnStale`, include the remaining stale/running
PR list in the report, and publish only artifacts that have already passed
validation and sanitization.

Then synchronize project state after artifacts are written:

```powershell
pwsh -NoProfile -File "$SkillRoot\scripts\Sync-PowerToysProject.ps1" `
  -Dashboard $Dashboard -Upstream $Upstream -Owner $ProjectOwner `
  -ProjectNumber $ProjectNumber
```

Use `-DryRun` first when project access or status option names have changed.
The updater must not claim project synchronization succeeded if GitHub returns
an authorization error; request the `read:project`/project-write capability and
rerun instead.

Review that `data/index.json` contains all open upstream PRs/issues, including
items with no artifact (`agent_status: none`) and fork-only traces
(`agent_status: mirror`). Verify artifacts are per-number and no secrets are
present:

```powershell
Get-ChildItem "$Dashboard\data\items\*.json"
Select-String -Path "$Dashboard\data\*.json" -Pattern 'ghp_|github_pat_|token' `
  -SimpleMatch
Select-String -Path "$Dashboard\data\items\*.json" `
  -Pattern '[A-Za-z]:\\|internal_evidence|internalEvidence|worktree|evidenceDirectory'
```

Validate every artifact written or substantively updated during this run. Pass
the processed upstream numbers so legacy artifacts are not grandfathered into
new output:

```powershell
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Test-DashboardArtifacts.ps1" `
  -Dashboard $Dashboard -Numbers $ProcessedNumbers `
  -RequireDetailedDesign -RequireIssueContext
```

Do not publish when validation reports an error. Fix the artifact or honestly
leave the workflow queued/in-progress; never shorten a design merely to pass.

For any approved upstream review decision consumed during the run, validate
schema-version-2 data with `Test-ReviewData.ps1` and publish only through
`Publish-ApprovedReview.ps1`; never substitute an ad-hoc `gh pr review`.

Publish only the board data and UI:

```powershell
Set-Location $Dashboard
git add README.md SCHEMA.md UPDATE_DASHBOARD_PROMPT.md emit.ps1 data
git diff --cached --check
if (-not (git diff --cached --quiet)) {
  git commit -m "Update PowerToys triage dashboard"
  git push origin HEAD
}
```

Verify the deployment:

```powershell
Invoke-WebRequest "$ArtifactBaseUrl/index.json" -UseBasicParsing
```

This repository's root `data/` directory is the static action-artifact
transport. Synchronize the same data into a PowerToys Pulse checkout before
claiming the dashboard is updated:

```powershell
Set-Location $PulseCheckout
$env:TRIAGE_DATA_SOURCE_DIR = Join-Path $Dashboard 'data'
node .\scripts\sync-triage-artifacts.mjs
npm run lint
npm run build
```

If local dependency installation is blocked, push the Pulse feature branch to
the authorized private validation repository and require its validation
workflow to pass. For an approved official data refresh, dispatch Pulse after
the artifact push:

```powershell
gh workflow run "Sync + Build + Deploy to Pages" -R $Pulse
```

Never push the official Pulse `main` branch without explicit approval. A
preview is complete only when the Pulse UI or its private build artifact shows
the newly processed item actions.

## Phase 5 — Report

Return one concise report containing:

1. PR coverage: total eligible, current, fully reviewed, context-revalidated,
   waiting/owned/excluded, and still queued;
2. issue judgments by status and full designs completed/deferred;
3. stale workflows resumed/rerun and their resulting stages;
4. closed/superseded/author-waiting items;
5. counts in the regenerated board and the published Pages URL;
6. status notification delivery result, or why delivery was skipped;
7. explicit confirmation that no upstream public action was taken.

## Important limitation: shared action updates

GitHub Pages is static. A member's browser can post an approved action to
PowerToys as that member, and this page updates the current browser session
immediately. It cannot commit refreshed `data/` or redeploy Pages by itself.
Other viewers see the shared update only after the dashboard data is regenerated
and pushed by this skill (or another backend/automation job).

Therefore, after a member acts, the board should show a local immediate state
(`waiting on author`, posted comments, or opened PR), while the next scheduled
run revalidates GitHub and publishes the authoritative shared state for all
viewers. A future backend can trigger this skill/workflow immediately, but a
pure static Pages site cannot do that securely on its own.
