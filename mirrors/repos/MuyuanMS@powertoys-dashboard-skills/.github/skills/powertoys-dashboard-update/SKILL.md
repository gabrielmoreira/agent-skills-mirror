---
name: powertoys-dashboard-update
description: "Daily PowerToys triage-dashboard updater. Exhaustively checks every eligible PR against its latest head and activity, quickly judges changed bug issues into explicit actions, resumes stale review/design work, requires implementation-grade issue designs with exact files/symbols/code paths, and republishes the v3 dashboard. Does not post upstream reviews/comments or open upstream PRs without explicit approval."
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
4. Do not publish PATs, tokens, local paths, or private notes to the board repo.
5. Every run must regenerate and publish `data/index.json`, `data/index.js`, and
   `data/items/<number>.json` to the configured board repository after the
   agent work completes.
6. PowerToys Pulse is the user-facing dashboard. After publishing artifacts,
   synchronize and validate Pulse, then deploy only an approved Pulse branch or
   workflow. Do not substitute the artifact repository's Pages site as the
   final preview.

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
$Board = if ($env:POWERTOYS_BOARD_REPO) {
  $env:POWERTOYS_BOARD_REPO
} else {
  (gh repo view --json nameWithOwner --jq '.nameWithOwner').Trim()
}
$Since = (Get-Date).AddDays(-2).ToUniversalTime().ToString('o')
$IssueWindowDays = 30
$DesignBatchSize = 10
$RunStartedAt = (Get-Date).ToUniversalTime().ToString('o')
$ProjectOwner = if ($env:POWERTOYS_PROJECT_OWNER) { $env:POWERTOYS_PROJECT_OWNER } else { 'microsoft' }
$ProjectNumber = if ($env:POWERTOYS_PROJECT_NUMBER) { [int]$env:POWERTOYS_PROJECT_NUMBER } else { 2445 }
$BoardOwner, $BoardName = $Board -split '/', 2
$BoardUrl = if ($env:POWERTOYS_BOARD_URL) {
  $env:POWERTOYS_BOARD_URL.TrimEnd('/') + '/'
} else {
  "https://$($BoardOwner.ToLowerInvariant()).github.io/$BoardName/"
}
$Pulse = if ($env:POWERTOYS_PULSE_REPO) { $env:POWERTOYS_PULSE_REPO } else { 'gim-home/powertoys-pulse' }
$PulsePreview = if ($env:POWERTOYS_PULSE_PREVIEW_REPO) { $env:POWERTOYS_PULSE_PREVIEW_REPO } else { 'MuyuanMS/powertoys-pulse-action-private' }
```

On the first run, verify:

```powershell
gh auth status
gh repo view $Fork
gh repo view $Board
```

Run this skill from the board repository root, or set
`POWERTOYS_DASHBOARD_PATH`. The other three skills must be present beside it
under `.github\skills`. Personal overrides are environment variables so no
account-specific configuration or token is committed.

The board repository may be public when its GitHub plan does not support
private Pages. Never place secrets or information that must remain private in
its data.

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
   non-draft, non-CmdPal PRs that are not already in project 2445 and updates
   existing items:

   - agent-produced review artifacts with suggested comments → `To manually review`;
   - a recognized member's upstream review/comment → `In Review` or the named
     option (`In Review: MuyuanMS`, `In Review: LegendaryBlair`, or
     `In Review: moooyu`) when that option exists;
   - closed or merged items → `Done`.

   Items with no recognized decision remain in their current project status,
   normally `To triage`. CmdPal classification uses labels and title signals;
   ambiguous PRs are not added automatically and must be reviewed by the agent
   before inclusion. Project synchronization never posts upstream content.

## Phase 1 — Build the complete freshness queue

Every run must enumerate **all** open upstream items before selecting work.
Do not limit PR discovery to `$Since`; `$Since` is only an optimization for
activity queries. Join the live list to artifacts and fork traces by upstream
number.

### PR freshness

Every open, non-draft, non-CmdPal PR must end the run in exactly one state:

- **current clean review** — artifact `head_sha` exactly matches the live head,
  the latest freshly requested Copilot pass has zero new comments and zero
  unresolved threads, required builds/context checks passed, and
  `source_updated_at` covers the latest relevant PR activity;
- **queued/running review** — no current clean result exists;
- **waiting on author** — a posted/requested change is still outstanding and
  the author has not pushed or replied;
- **owned elsewhere** — a recognized maintainer is actively reviewing it;
- **excluded** — draft, CmdPal, closed, or otherwise outside this workflow.

A **full re-review is mandatory** when the live head SHA differs from
`head_sha`, `head_sha` is missing, or there is no clean artifact. If the head is
unchanged but comments/reviews changed after `source_updated_at`, perform a
focused context revalidation. Rerun the full review only when that activity
changes requirements, reveals a concern, resolves author-waiting state, or
invalidates the prior decision. Otherwise advance `evaluated_at` and
`source_updated_at` without pretending a new code review occurred.

Never skip an eligible PR merely because it is old or absent from the recent
activity query. Never re-review an unchanged, converged head with no newer
relevant activity.

### Fast issue judgment

Every open `Issue-Bug` issue with no `judgment`, or with live `updatedAt` newer
than `source_updated_at`, receives a lightweight judgment during the run. This
pass is deliberately cheaper than `powertoys-issue-to-design`: inspect the
body, latest comments, labels, assignees, linked PRs/issues, and obvious
repository ownership signals, then emit one of:

| `judgment.status` | Dashboard result |
| --- | --- |
| `actionable_design` | `Design fix` action; candidate for the bounded full-design batch |
| `needs_information` | Draft a specific `request_info` action describing exactly what evidence is missing |
| `duplicate_or_handled` | Link the duplicate/fix/owned work; no duplicate agent work |
| `waiting_on_author` | Preserve the requested evidence and waiting-since timestamp |
| `not_actionable` | Explain feature/by-design/external/hardware/insufficient-scope reason |

Each judgment must contain `rationale`, concrete `evidence`, a
`recommended_action`, `evaluated_at`, and `source_updated_at`. Do not claim a
root cause during the fast pass. When evidence is insufficient, prefer
`needs_information` over a speculative design.

Older unchanged bugs do not need to be re-read every run, but they must retain
their prior explicit judgment/action in the board. The 30-day window controls
full-design priority, not whether changed issues receive a judgment.

For every artifact and mapped fork trace, also detect:

- upstream PR/issue closed, merged, superseded, or linked work appeared;
- labels, assignee, author response, or reproduction evidence changed;
- a fork mirror/PR was closed, merged, or replaced.

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

PR coverage is exhaustive by default: every open, non-draft PR that is not
waiting on the author, owned elsewhere, or CmdPal must have a current result or
be resumed/sent through `powertoys-pr-review` in the fork. Process PRs in
parallel batches of 3–5 to overlap Copilot polling and builds, while preserving
each fork's independent convergence state. Prioritize missing/stale heads, then
unchanged heads with newer activity. Do not re-review an unchanged head that
already has a current clean fork result and no relevant newer activity.
Do not call a PR review complete, approval-ready, or "clean" unless the latest
freshly requested Copilot review has zero new comments, zero unresolved threads,
and the required local build has passed. A Copilot-clean result with a pending
build, context review, spelling check, or timed-out fresh request remains
`review_in_progress` and must get a `Re-run review`/`Continue review` action.

Issue **judgment** is exhaustive for new/changed bugs, while full design work is
bounded. Rank `actionable_design` judgments by confidence, reproducibility,
scope, recency, and lack of existing ownership. Run at most
`$DesignBatchSize` (default 10) through `powertoys-issue-to-design`; leave the
rest queued with explicit `Design fix` actions. Prefer issues updated in the
last `$IssueWindowDays`, then consume older actionable issues as capacity
allows.

For each queued item, invoke the corresponding skill with the upstream number
and complete its fork-side loop. Do not bypass its gates:

The retired custom `pr-iterate` agent must not be launched. `pr-iterate/<N>`
remains the durable fork branch naming convention used by
`powertoys-pr-review`; the current execution path is the `powertoys-pr-review`
skill itself, using a general-purpose worker when parallel background execution
is needed.

- PR: `powertoys-pr-review` must reach zero new Copilot comments and zero
  unresolved Copilot threads before a new artifact is emitted.
- Issue: `powertoys-issue-to-design` must reach a converged adversary-reviewed
  implementation-grade design and stop at approval.
- Approved design: `powertoys-design-to-pr` may build/review the fork PR but
  stops before opening the upstream PR unless separately approved.

If a workflow is waiting on an author or user approval, do not rerun it just to
make activity; preserve that status. A queued item must retain an explicit
fork trace or dashboard action even when its execution is deferred.
When drafting review payloads, follow the review skill's schema rules: inline
suggestions must target an exact current RIGHT-side diff range and contain an
apply-ready suggestion block; architectural or out-of-diff findings belong in
body comments. Keep fork/worktree provenance in internal evidence, never in
public upstream comment text.

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
  "evaluated_at": "UTC ISO",
  "source_updated_at": "upstream updatedAt covered by this result",
  "judgment": {
    "status": "actionable_design",
    "rationale": "...",
    "evidence": ["..."],
    "recommended_action": "..."
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
- PRs: community-authored, non-draft, non-CmdPal, and no meaningful
  maintainer/reviewer ownership or existing fork trace. If labels do not
  identify the area, inspect the title, changed files, linked issue, and
  description before deciding whether it is CmdPal-related.

Rank candidates using:

- PRs: close to merge, fewer unresolved concerns, newer activity, and prior
  maintainer involvement;
- issues: easy reproduction/verification, low risk, small scope, and clear
  acceptance criteria.

Run only the bounded top candidates through the relevant sub-skill. Report the
remaining candidates without starting them.

## Phase 4 — Emit artifacts and update PowerToys Pulse

Run the v3 generator after all fork-side work:

```powershell
pwsh -NoProfile -File "$Dashboard\emit.ps1"
```

The generator preserves valid per-number artifacts written by review workers;
it must not delete worker output merely because an item is not in the
hand-authored overlay. Run it only after worker writes are complete when
possible, and verify the resulting `artifact_numbers` includes every completed
review from the run.

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
```

Validate every artifact written or substantively updated during this run. Pass
the processed upstream numbers so legacy artifacts are not grandfathered into
new output:

```powershell
pwsh -NoProfile -File `
  "$SkillRoot\scripts\Test-DashboardArtifacts.ps1" `
  -Dashboard $Dashboard -Numbers $ProcessedNumbers -RequireDetailedDesign
```

Do not publish when validation reports an error. Fix the artifact or honestly
leave the workflow queued/in-progress; never shorten a design merely to pass.

For any approved upstream review decision consumed during the run, validate
schema-version-2 data with `Test-ReviewData.ps1` and publish only through
`Publish-ApprovedReview.ps1`; never substitute an ad-hoc `gh pr review`.

Publish only the board data and UI:

```powershell
Set-Location $Dashboard
git add index.html README.md SCHEMA.md data
git diff --cached --check
if (-not (git diff --cached --quiet)) {
  git commit -m "Update PowerToys triage dashboard"
  git push origin HEAD
}
```

Verify the deployment:

```powershell
Invoke-WebRequest $BoardUrl -UseBasicParsing
Invoke-WebRequest "${BoardUrl}data/index.json" -UseBasicParsing
```

The board repository is the static action-artifact transport. Synchronize the
same data into a PowerToys Pulse checkout before claiming the dashboard is
updated:

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
6. explicit confirmation that no upstream public action was taken.

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
