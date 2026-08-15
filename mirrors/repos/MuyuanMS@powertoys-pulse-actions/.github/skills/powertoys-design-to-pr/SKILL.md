---
name: powertoys-design-to-pr
description: "Fork-first workflow that turns an APPROVED fix design (produced by powertoys-issue-to-design and captured in a fork mirror issue) into a ready-to-publish PR for microsoft/PowerToys. Given an upstream issue number whose design is already mirrored + approved in the fork, it: (0) syncs the user's fork (MuyuanMS/PowerToys) with upstream and resumes any prior work instead of duplicating; (1) confirms a design-bearing mirror issue exists and the design was approved (else defers to powertoys-issue-to-design); (2) assigns the GitHub Copilot cloud agent to implement the approved fix plan as a draft PR; (3) runs an until-clean Copilot review→fix→push→reply+resolve→re-review loop and builds locally to confirm it compiles and is e2e-testable; (4) checks the implementation against the approved design and assesses confidence, improving obvious flaws; (5) rewrites the fork PR description; and (6) presents a brief + PR link for approval, then only on approval opens the real upstream PR against microsoft/PowerToys linked to the original issue. All AI work stays in the fork to keep the upstream repo clean. Triage and root-cause/fix-plan design are handled upstream of this skill by powertoys-issue-to-design."
---

## When to Use

Use this skill as the **second half** of the fix pipeline: when a PowerToys bug already has an **approved fix design** — produced by `powertoys-issue-to-design` and captured in a fork **mirror issue** — and you want it built into a publish-ready pull request, with every intermediate step inside the personal fork so the upstream repo stays clean.

Trigger phrases: "build the PR for PowerToys issue 12345", "design-to-pr for M", "the design for M is approved — implement it", "turn the approved design into a PR".

If there is **no approved design mirror issue** for `M`, run **`powertoys-issue-to-design`** first (it triages, investigates the root cause with an investigator↔adversary loop, writes the design into the fork mirror issue, and stops at a design-approval gate). This skill picks up from that approved mirror issue.

## Core Principles (read first)

1. **Fork-first, always.** Every AI-generated artifact — the drafted PR, the review loop, the fixes — lives in the user's fork (`<FORK_REPO>`, e.g. `MuyuanMS/PowerToys`). Nothing touches `microsoft/PowerToys` until the final Phase 7 approval. (The design mirror issue was already created, publicly and fork-safe, by `powertoys-issue-to-design`.)
2. **Never leak a back-reference to the upstream issue.** In the fork, in commit messages, in PR titles/bodies, and in any comment, **NEVER** write `#<M>` or any GitHub auto-link form (`GH-M`, `microsoft/PowerToys#M`, a full issue URL, or "fixes/closes/resolves #M"). GitHub turns those into cross-references that notify the upstream thread. Refer to the issue as plain text: `Issue M` or `[Issue M]`. The **only** place a real `#<M>` / `Closes #M` reference is allowed is the final upstream PR body in Phase 7.
3. **Build the approved design — don't redesign.** The root cause and fix plan were investigated and approved upstream (`powertoys-issue-to-design`). Implement THAT plan; if implementation reveals the design is wrong, stop and kick back to `powertoys-issue-to-design` rather than silently improvising a different fix.
4. **Stop-and-ask at the upstream gate.** The design gate already happened in `powertoys-issue-to-design`. Here the one remaining stop is (Phase 7) before opening the upstream PR. Otherwise, in autopilot, proceed and state your assumptions.
5. **Two different Copilots.** Keep them straight:
   - **Copilot cloud/coding agent** — login `copilot-swe-agent` (REST assignee string `copilot-swe-agent[bot]`, PR author shows as `Copilot`). Assigned to the **design mirror issue** to *write* the PR, and re-driven to *fix* review feedback.
   - **Copilot code review** — reviewer `copilot-pull-request-reviewer[bot]`. Requested on the **PR** to *generate* review comments.
6. **Build locally before declaring ready.** A green Copilot review is not enough; the fork branch must compile and be e2e-testable locally (reuse the build reference from `powertoys-pr-review`).
7. **Resume, don't duplicate.** Always run Phase 0 first: sync the fork's `main` with upstream and check whether this skill already left unfinished work for Issue M (a draft PR off the design mirror issue), then pick up from the correct phase.
8. **The review loop is until-clean.** Keep re-requesting Copilot review — fixing, pushing, and replying+resolving each comment — until a freshly-requested review returns zero new comments. A single review pass is never the end.

## Configuration & Prerequisites (verify on first run)

Auto-detect, then confirm:

- `<FORK_OWNER>` — GitHub username (e.g. `MuyuanMS`).
- `<FORK_REPO>` — `<FORK_OWNER>/PowerToys` (e.g. `MuyuanMS/PowerToys`).
- `<FORK_REMOTE>` — git remote name pointing at the fork (default `myfork`).
- `<CLONE_PATH>` — local PowerToys clone (e.g. `C:\PowerToys`).
- `M` — the upstream issue number; `F` — the fork **design mirror issue** number (from `powertoys-issue-to-design`).

```powershell
# gh must be authenticated with a USER token (PAT / oauth), not an app installation token.
gh auth status
# Fork must exist:
gh repo view <FORK_REPO> --json nameWithOwner 2>$null || gh repo fork microsoft/PowerToys --clone=false
```

**Copilot coding agent must be enabled on the fork.** Verify with the `suggestedActors` query in Phase 3 — if `copilot-swe-agent` is not the first returned node, direct the user to enable Copilot cloud agent for their account/repo before continuing.

For the local build prerequisites (Visual Studio 2022+ with C++ workload, Spectre override, worktree scripts), reuse the **Prerequisites** and **Build Instructions Reference** sections of the `powertoys-pr-review` skill verbatim — do not duplicate them here.

> Token note: assigning the coding agent via GraphQL requires the header
> `GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection`
> and a fine-grained PAT with read/write on issues, pull requests, contents, and actions (or a classic PAT with `repo`). `gh auth token` typically works if the user has agent access.

---


## Phase 0 — Resume check & fork sync (ALWAYS run first)

Before triaging, do two things: (a) make sure the fork is synced with upstream so any new work is based on fresh `main`, and (b) detect whether this skill was **already** used for Issue M and left unfinished work to pick up instead of starting over.

### 0a. Sync the fork's `main` with upstream `microsoft/PowerToys`

The Copilot coding agent branches the draft PR off the fork's `main`, so a stale fork `main` produces a stale base and diff bloat. Sync **before** any new work (Phase 3) and again right before the upstream PR (Phase 7c).

```powershell
# How far behind is the fork's main vs upstream?
gh api repos/microsoft/PowerToys/compare/main...<FORK_OWNER>:main --jq '{behind_by, ahead_by, status}'
```

If `behind_by > 0`, fast-forward the fork's `main`:

```powershell
cd <CLONE_PATH>
git fetch origin main            # 'origin' = microsoft/PowerToys upstream remote
git checkout main
git merge origin/main --ff-only
git submodule update --init --recursive
git push <FORK_REMOTE> main      # <FORK_REMOTE> = the fork remote
```

If a fork branch already exists for this issue (resume case), rebase it onto the freshly-synced `main` using the same discipline as `powertoys-pr-review` Step 2b (rebase → resolve if confident, else stop and ask → update submodules → `--force-with-lease` push → re-sync fork main). Prefer syncing the fork's `main` via the GitHub "Sync fork" API if you have no local upstream remote:

```powershell
'{ "branch": "main" }' | Set-Content "$env:TEMP\syncfork.json" -Encoding utf8
gh api --method POST /repos/<FORK_REPO>/merge-upstream --input "$env:TEMP\syncfork.json"
```

State the result briefly (e.g. "Fork main was 42 commits behind; fast-forwarded and pushed").

### 0b. Detect prior/unfinished work for Issue M

Look for a mirrored issue and any PR this skill previously created, so you resume instead of duplicating.

```powershell
# 1. Is there already a mirrored issue "[Issue M] ..." in the fork?
gh issue list --repo <FORK_REPO> --state all --search '"[Issue M]" in:title' `
  --json number,title,state,url,assignees
```

- **No mirrored issue found** → no design to build here. Go to Phase 1, which defers to `powertoys-issue-to-design`.
- **Mirrored issue found** → record its number `F`, then find any PR the coding agent opened from it:

```powershell
# 2. Find the linked/drafted PR (coding-agent PRs are authored by "Copilot", branch "copilot/...").
gh pr list --repo <FORK_REPO> --state all --author "Copilot" `
  --json number,title,state,headRefName,isDraft,createdAt,url `
  --jq 'sort_by(.createdAt) | reverse'
# Match the PR to Issue M by title ("Issue M" text) or by the mirrored issue's timeline:
gh api repos/<FORK_REPO>/issues/F/timeline --paginate `
  --jq '.[] | select(.event=="cross-referenced") | .source.issue.pull_request.html_url'
```

### 0c. Determine resume point and jump

Classify the prior state and continue from the matching phase (state it to the user first):

| Prior state | Evidence | Resume at |
| --- | --- | --- |
| **None** | No `[Issue M]` design mirror in fork | Phase 1 (defer to `powertoys-issue-to-design`) |
| **Issue mirrored, agent not assigned** | Issue `F` exists, no `copilot-swe-agent` assignee, no PR | Phase 3 (assign agent) |
| **Agent assigned, no PR yet** | `copilot-swe-agent` assigned to `F`, no Copilot PR | Phase 4a (wait for draft PR) |
| **PR exists, review loop unfinished** | PR `P` open with outstanding/unresolved Copilot comments, or last Copilot review is stale vs latest push, or never built locally | Phase 4b (resume the loop from `last_ts` = time of latest processed review) |
| **PR exists, loop looks done** | PR `P` open, latest Copilot review has zero unresolved comments, builds locally | Phase 5 (confidence pass) |
| **Upstream PR already opened** | A `microsoft/PowerToys` PR exists from `<FORK_OWNER>:<branch>` | Report it; do not re-open. Only continue if the user wants further iteration. |

To judge "review loop unfinished" on an existing PR `P`, check for **unresolved** Copilot review threads and whether the newest review predates the newest commit:

```powershell
# Unresolved review threads authored by the Copilot reviewer:
gh api graphql -f query='
query {
  repository(owner: "<FORK_OWNER>", name: "PowerToys") {
    pullRequest(number: P) {
      reviewThreads(first: 100) { nodes { isResolved comments(first: 1) { nodes { author { login } createdAt } } } }
      commits(last: 1) { nodes { commit { committedDate } } }
      reviews(last: 5) { nodes { author { login } submittedAt state } } } } }'
```

If any Copilot thread has `isResolved == false`, or the newest commit is newer than the newest Copilot review, the loop is **unfinished** → resume Phase 4b. Set `last_ts` to the submitted time of the most recent Copilot review you have already fully processed (so you don't re-fix resolved threads, but do catch anything newer).

---

## Phase 1 — Confirm the approved design mirror issue

This skill starts from an **approved fix design** already captured in the fork mirror issue by `powertoys-issue-to-design`. Do not re-triage or re-investigate here — that work is done. Confirm the handoff:

```powershell
# Find the design-bearing mirror issue "[Issue M] ..." in the fork:
gh issue list --repo <FORK_REPO> --state all --search '"[Issue M]" in:title' `
  --json number,title,state,body,url
```

Check that the mirror body contains a converged, implementation-grade
`## Fix design` section with inferred root cause, evidence, exact affected
files/symbols, ordered implementation steps with key code shapes, verification,
risks/alternatives, and adversary sign-off. A short prose-only fix plan is not
an approved handoff; return it to `powertoys-issue-to-design` for expansion.
Then:

- **Design present and approved** (the user approved it via the dashboard `approve_design` decision or inline in `powertoys-issue-to-design` Phase 6) → record `F` (fork mirror issue number) and continue to Phase 3 (assign the coding agent to implement the plan).
- **Mirror issue exists but design not yet approved** → **STOP**; the design gate belongs to `powertoys-issue-to-design` Phase 6. Route the user there to approve (or hand back).
- **No `[Issue M]` design mirror exists** → **STOP** and run **`powertoys-issue-to-design` for Issue M first**. This skill does not triage, investigate, or mirror; it consumes an approved design.

> Triage red flags (linked PR, duplicate, someone already working, needs-design, out of scope) are handled in `powertoys-issue-to-design` Phase 1. If new red flags appeared upstream since the design was approved, surface them and confirm with the user before proceeding.

---

## Phase 2 — (handled upstream) Mirror issue + design

**The fork mirror issue and its design were created by `powertoys-issue-to-design` (its Phase 5).** There is nothing to mirror here. The mirror issue body already carries the sanitized original report, evidence, exact files/symbols, implementation steps, verification, risks, alternatives, and any re-hosted diagnostic attachments — this is exactly the context the coding agent needs in Phase 3.

If, on resume, you find the mirror issue is missing the design section, do not re-create it here — hand back to `powertoys-issue-to-design` to (re)produce and (re)approve the design.

---

## Phase 3 — Assign the Copilot coding agent so it drafts a PR

Assigning `copilot-swe-agent` to the fork **design mirror issue** makes the Copilot cloud agent start a session and open a draft PR in the fork. The agent implements the **approved fix plan** already in the mirror issue body.

> **Before assigning, confirm the fork's `main` is synced with upstream (Phase 0a).** The agent branches its draft PR off the fork's `main`; a stale base means a stale/bloated PR. If you skipped Phase 0a or time has passed, re-run the sync now.

### 3a. Resolve the bot id (also confirms the agent is enabled)

```powershell
gh api graphql -f query='
query {
  repository(owner: "<FORK_OWNER>", name: "PowerToys") {
    suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
      nodes { login __typename ... on Bot { id } ... on User { id } }
    }
  }
}' --jq '.data.repository.suggestedActors.nodes[] | select(.login=="copilot-swe-agent")'
```

If no `copilot-swe-agent` node comes back, the agent isn't enabled — stop and tell the user to enable Copilot cloud agent, then retry.

### 3b. Get the forked issue node id

```powershell
gh api graphql -f query='
query { repository(owner: "<FORK_OWNER>", name: "PowerToys") { issue(number: F) { id title } } }' `
  --jq '.data.repository.issue.id'
```

### 3c. Assign the agent

GraphQL (preferred — lets you pass `baseRef`/instructions):

```powershell
gh api graphql -H 'GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection' -f query='
mutation {
  replaceActorsForAssignable(input: {
    assignableId: "ISSUE_NODE_ID",
    actorIds: ["BOT_ID"],
    agentAssignment: { baseRef: "main", customInstructions: "Implement the approved ## Fix design in order, using its exact files, symbols, code-shape guidance, edge cases, and tests. Follow PowerToys contributing conventions; keep the change atomic and buildable; do not redesign — if the plan is wrong or a named symbol no longer matches the code, stop and report." }
  }) {
    assignable { ... on Issue { id assignees(first: 10) { nodes { login } } } }
  }
}'
```

REST fallback (PowerShell has no heredoc — write the JSON to a temp file, then `--input`):

```powershell
'{ "assignees": ["copilot-swe-agent[bot]"], "agent_assignment": { "base_branch": "main" } }' |
  Set-Content -Path "$env:TEMP\assign.json" -Encoding utf8
gh api --method POST -H "X-GitHub-Api-Version: 2022-11-28" `
  /repos/<FORK_REPO>/issues/F/assignees --input "$env:TEMP\assign.json"
```

Confirm `copilot-swe-agent` appears in the returned assignees.

---

## Phase 4 — Wait for the draft PR, then run the review loop

### 4a. Detect the PR the agent created

The coding agent opens a PR in the fork (author shows as `Copilot`, head branch like `copilot/...`). Poll until it appears (every ~30–60s, up to ~15 min):

```powershell
gh pr list --repo <FORK_REPO> --state open --json number,title,author,headRefName,createdAt,isDraft `
  --jq 'sort_by(.createdAt) | reverse | .[] | select(.author.login=="Copilot" or (.headRefName | startswith("copilot/")))'
```

Record the fork **PR number `P`** and head branch. Also wait for the agent to *finish its first pass* — it typically posts a summary comment and/or marks the PR ready-for-review. Signals to poll:
- a comment on `P` from `Copilot` summarizing the work, and/or
- `isDraft` flipping to `false`, and/or
- the agent task state reaching `completed` (`gh api /agents/repos/<FORK_REPO>/tasks` if available).

Don't start reviewing mid-session; give the agent its first complete pass.

**Label the fork PR so it is distinguishable from other skills' fork PRs.** Both this skill and `powertoys-pr-review` create PRs in the same fork; a per-skill label keeps them easy to tell apart and filter. Ensure the label exists (idempotent) and add it to `P`:

```powershell
gh label create design-to-pr --repo <FORK_REPO> --color 0E8A16 --description "Fork PR drafted by the powertoys-design-to-pr skill" --force
gh pr edit P --repo <FORK_REPO> --add-label design-to-pr
```

### 4b. The review loop (Copilot review → fix → push → reply+resolve → RE-REQUEST, until zero new comments)

This mirrors `powertoys-pr-review` Steps 4–6, scoped to the fork PR `P`. You already own `P`, so there is no fork-mirroring — just iterate. **The loop is not optional and does not stop after one round.** It ends *only* when a freshly-requested Copilot review comes back with **zero new actionable comments**. You must actively **re-request** a review every round — Copilot never re-reviews on its own.

> **Why the loop "wasn't working" before:** the two failure modes to avoid are (1) treating a single review pass as "done" instead of re-requesting until a clean pass, and (2) pushing fixes but never replying to and **resolving** the prior Copilot comments (so old threads stay open and the next review re-flags them). Both are fixed by the strict procedure below.

```
round = 1
last_ts = <timestamp captured immediately BEFORE the first review request>

LOOP:
  1. REQUEST a Copilot review on the fork PR (every round, after every push):
       gh api repos/<FORK_REPO>/pulls/P/requested_reviewers -X POST \
         -f "reviewers[]=copilot-pull-request-reviewer[bot]"
     - Reviewer name MUST be exactly copilot-pull-request-reviewer[bot] (plain "copilot" silently no-ops).
     - VERIFY the response's requested_reviewers array is non-empty. If empty, the reviewer
       isn't enabled → stop and tell the user to enable Copilot code review, then retry.

  2. POLL for the new review to land (every 60s, up to 10 min):
       gh api repos/<FORK_REPO>/pulls/P/reviews
     → a review from copilot-pull-request-reviewer[bot] with submitted_at > last_ts.
     The fresh review has COMPLETED when ANY of these is true (check all three — the
     reviews list alone can lag):
       (a) a new review row from the bot with submitted_at > last_ts appears; OR
       (b) Copilot was removed from requested_reviewers (it consumed the request):
             gh api repos/<FORK_REPO>/pulls/P --jq '.requested_reviewers[].login'
           no longer lists the bot; OR
       (c) a `reviewed` event fires after last_ts on the timeline:
             gh api repos/<FORK_REPO>/issues/P/timeline --paginate \
               --jq '.[] | select(.event=="reviewed") | .submitted_at'
     (If none arrives after 10 min, re-request once more, then continue polling.)

  3. FETCH this round's new inline comments:
       gh api repos/<FORK_REPO>/pulls/P/comments
     → keep only created_at > last_ts AND user.login == copilot-pull-request-reviewer[bot].
     Capture each comment's id (for replies) AND node_id (for resolving).
     LOGIN-FILTER GOTCHA (critical — miscounts cause false "clean"): the SAME bot has
     DIFFERENT logins across APIs. REST (/pulls/P/comments, /reviews) reports
     `copilot-pull-request-reviewer[bot]`; GraphQL `reviewThreads` reports
     `copilot-pull-request-reviewer` (NO `[bot]`). An exact-match filter on one form
     silently drops the other and undercounts to zero. Always filter case-insensitively
     with a substring test, e.g. jq `select(.user.login|test("copilot";"i"))` for REST and
     `select(.comments.nodes[0].author.login=="copilot-pull-request-reviewer")` for GraphQL.

  4. If ZERO new actionable comments → the review is clean → EXIT LOOP → go to Phase 5.
     "Zero new comments" means zero *published* inline comments with created_at > last_ts.
     A review whose body says "Copilot reviewed N files ... and generated no new comments"
     is CLEAN even when it lists comments under "**Comments suppressed due to low
     confidence**" — those are self-suppressed by Copilot and are NOT published threads, so
     they neither need resolving nor block the exit. Confirm by cross-checking that there
     are also ZERO unresolved bot-authored reviewThreads.

  5. ADDRESS every comment (pick per situation, but ALWAYS produce a pushed change or a reason):
       PRIMARY — hand back to the coding agent (keeps the PR Copilot-authored):
         Post ONE comment on P: "@copilot please address the review feedback above."
         Optionally re-assign copilot-swe-agent to P (replaceActorsForAssignable / addAssigneesToAssignable
         on the PR node id). Wait for the agent to push new commits to the head branch.
       FALLBACK — if the agent stalls, is wrong, or the fix is trivial:
         Fix directly in the local worktree (Phase 4c), commit, and push to the fork branch.

  6. PUSH first (agent push or local push) — the reviewer only sees pushed code.

  7. REPLY TO **AND** RESOLVE every comment from step 3 (do BOTH for each; never leave a thread open):
       # Reply with the concrete outcome:
       gh api repos/<FORK_REPO>/pulls/P/comments/<comment_id>/replies \
         -f body="Fixed in <sha>: <what changed>"          # or:
         -f body="Not applicable: <reason>"                 # out-of-scope / file not touched
         -f body="Already addressed in <sha>"               # Copilot repeated a prior concern
       # Then RESOLVE the thread (mark it done so the next review won't re-flag it):
       gh api graphql -f query='mutation { minimizeComment(input: {subjectId: "<comment_node_id>", classifier: RESOLVED}) { minimizedComment { isMinimized } } }'
       # If minimizeComment fails, resolve the review thread instead:
       gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "<thread_node_id>"}) { thread { isResolved } } }'

  8. BUILD locally (Phase 4c) to confirm the round still compiles. If the module has unit
     tests, BUILD + RUN them too — a build break or a failing/regressed unit test is a
     legitimate review finding that BLOCKS "clean." When tests fail, feed the exact failing
     test names + file/line back to @copilot (step 5) as part of the next round; do NOT
     exit the loop with red tests, and do NOT weaken/delete a test to make it pass.
     BUT distinguish PR-CAUSED failures from PRE-EXISTING / ENVIRONMENTAL ones before
     handing anything to the agent — do not send it chasing failures the PR didn't cause:
       - Reproduce the failure's root cause. Tells that a failure is NOT the PR's fault:
         it also fails on the merge-base; it depends on the host (e.g. timezone/locale — a
         real-file date/time test that fails on a non-UTC dev box but passes in UTC CI);
         a duplicated test passes in one class but fails in another (real-file vs pure-unit);
         the failing assertion involves data the PR never touches (e.g. a numeric-only string
         when the PR only changed casing). Prove production is correct independently when you
         can (e.g. call the Win32 API directly / P/Invoke to show the mapping is right, so the
         bug is in the test literal, not the code).
       - Watch for source-ENCODING failures: raw non-ASCII string literals in a test .cpp
         with no UTF-8 BOM and no `/utf-8` compile switch get mis-decoded by MSVC. Symptom:
         mojibake in the assert output (e.g. `Ã‰`=É, `Ã©`=é are UTF-8 bytes shown as CP1252).
         Fix by using `\uXXXX` escapes (keeps the file pure-ASCII) or adding a BOM — this is a
         test bug, not a production casing bug.
       - State the categorization explicitly to @copilot: list the MUST-FIX (PR-caused)
         failures with precise fixes, AND the pre-existing/environmental ones with the
         evidence, telling it NOT to touch them. Carve the known-environmental failures out
         of your "clean" gate so the loop can actually terminate.

  9. last_ts = now; round += 1
     Termination guards:
       - round > 10 with only low-severity comments remaining → EXIT (note it in the brief)
       - round > 20 → EXIT and flag for manual attention
     GOTO 1   # ← always re-request; do NOT stop just because you handled this round
END LOOP
```

Loop rules (same discipline as `powertoys-pr-review`):
- **Definition of done = one clean *freshly-requested* review AND a green local build/tests.** The loop terminates ONLY after you request a NEW Copilot review (step 1), wait for it to land (step 2), it returns **zero new comments** (step 4), there are zero unresolved bot threads, AND the affected module builds with its unit tests passing (step 8). Fixing, pushing, replying, and resolving every existing thread is **necessary but NOT sufficient** — a PR with all threads resolved is *not* done until a subsequently-requested review comes back empty. Never conclude on a fix/resolve pass; always spend one more request→wait cycle to CONFIRM clean. If that confirming review adds new comments, you are still in the loop — handle them and go again.
- **Re-request every round until a clean pass.** One review round is never "done." Keep looping request→fix→push→reply+resolve→re-request until a freshly-requested review returns zero new comments.
- **Always push before re-requesting review** — the reviewer only sees pushed code.
- **Always re-request review after each push** — it does not auto re-review.
- **Every handled comment must be BOTH replied to AND resolved** (step 7). Unresolved threads cause the next review to re-flag the same issue and make the loop look "stuck."
- **Track `last_ts`** so you only process *new* comments; never re-fix an already-addressed concern (reply "Already addressed in <sha>" and resolve).
- Treat out-of-scope comments (files the PR didn't touch) as "Not applicable" + resolve.
- **Verify `requested_reviewers` is non-empty** after each request — a silent empty response means the review was never actually queued.

#### 4b-troubleshooting. When the loop stalls (hard-won gotchas)

- **The coding agent can get stuck in a phantom "working" state.** Check the PR timeline for `copilot_work_started` / `copilot_work_finished` events:
  `gh api repos/<FORK_REPO>/issues/P/timeline --paginate --jq '.[] | select(.event|test("copilot_work")) | {event, at:(.created_at//.updated_at)}'`
  If you see a `copilot_work_started` with **no matching `copilot_work_finished`**, the agent session hung. GitHub will **not** start a new session while one is "in progress," so `@copilot` mentions and even un-assign/re-assign become no-ops (they will NOT push new commits). Do not wait indefinitely on it. Switch to the **FALLBACK** in step 5 (fix directly in the local worktree and push), or escalate to the user. A `@copilot` handoff only reliably triggers the agent when no prior session is stuck.
- **`@copilot` handoff is best-effort, not guaranteed.** If, after a handoff, no `copilot_work_started` appears within a few minutes and no new commit lands, assume the agent will not act and take the local-fix fallback rather than re-poking it in a loop.
- **Do NOT rely on `manage_schedule` for multi-round convergence.** Scheduled prompts only fire while a CLI session is actively running — an idle/closed session makes **zero** progress, so a "check every 20m" schedule silently stalls for days. Drive the loop inline within an active session, or hand off to the local-worktree fallback, instead of scheduling it and walking away.
- **Watch for review churn that never converges.** Each fresh review may surface new low-severity nitpicks even after the previous batch is resolved. Honor the termination guards (round > 10 low-severity → exit; round > 20 → exit + flag). Never fabricate a resolution: only reply "Verified addressed" + resolve a thread when you can point to the exact current head code that satisfies it; otherwise leave it open and flag it.

### 4c. Local build & e2e readiness

Reuse the **Build Instructions Reference** from `powertoys-pr-review` (Spectre override, `build-essentials.cmd`, module-interface DLL, managed app, changed project; worktree via `New-WorktreeFromBranch.ps1`). Concretely:

1. Fetch the fork PR branch into `<CLONE_PATH>` and make a **dedicated build worktree** (e.g. `C:\ptbuild-<P>`, never pushed) so the checkout is isolated from fix worktrees.
2. `$env:POWERTOYS_DISABLE_SPECTRE = "1"`, run `build-essentials.cmd`, then build the changed module chain (only build-essentials + the affected module(s) — a full-solution build is NOT required for e2e).
3. Verify exit code 0, `x64/Debug/PowerToys.exe` exists, and the changed module DLL loads (no "Failed to load" in the runner log).
4. Note concrete **e2e test steps** (launch command + how to trigger + what to verify) for the final brief.
5. **Leave the build worktree in place** at the end. Each finished PR should ship with its own local worktree + the affected modules already built, so the user can immediately launch and verify the fix without rebuilding.

A build failure caused by the PR's own code is itself a review finding — feed it back into the loop (agent or local fix) and continue.

> **CRITICAL build gotcha — `POWERTOYS_DISABLE_SPECTRE` is a no-op by default.** On a machine WITHOUT the VS "Spectre-mitigated libraries" component, `build-essentials.cmd` fails with `error MSB8040: Spectre-mitigated libraries are required` because `Cpp.Build.props` hardcodes `<SpectreMitigation>Spectre</SpectreMitigation>` and **nothing reads the env var**. Setting `$env:POWERTOYS_DISABLE_SPECTRE=1` alone does nothing. Two ways to actually build:
> - **Preferred (script-friendly):** in the throwaway build worktree, make the prop honor the env var, then build:
>   ```xml
>   <!-- Cpp.Build.props, replacing the hardcoded line -->
>   <SpectreMitigation Condition="'$(POWERTOYS_DISABLE_SPECTRE)' == '1'">false</SpectreMitigation>
>   <SpectreMitigation Condition="'$(POWERTOYS_DISABLE_SPECTRE)' != '1'">Spectre</SpectreMitigation>
>   ```
>   (MSBuild reads env vars as properties, so `$env:POWERTOYS_DISABLE_SPECTRE=1` then works for build-essentials AND every module build. Do NOT commit this edit — it lives only in the local build worktree.)
> - **Alternative (per-command):** call `msbuild <project> /p:SpectreMitigation=false ...` directly (command-line `/p:` overrides the hardcoded prop). This is what individual module builds use, but `build-essentials.cmd` does not forward it, so the prop edit above is needed for the essentials step.

---

## Phase 5 — Confidence assessment & obvious-flaw pass

Once the loop exits and the build is green:

1. Re-read the original (upstream) issue's acceptance criteria and compare against the actual diff (`git diff main...<head>` on the fork).
2. Judge **how confidently this PR resolves Issue M**:
   - **High** — directly implements the asked behavior, covered by the build/e2e steps, no obvious gaps.
   - **Medium** — plausibly fixes it but has untested paths, partial coverage, or a design choice worth a human eye.
   - **Low** — compiles and passes review but you're not convinced it addresses the root cause.
3. If you spot an **obvious flaw or clear improvement** (missed edge case, wrong resource string, regression risk, incomplete fix), fix it — via the coding agent or locally — then re-run one review + build round. Otherwise, record the concern in the final brief rather than silently shipping it.

---

## Phase 6 — Rewrite the fork PR description

Update `P`'s description to reflect the *final* state (still fork-safe: no `#M` back-links). Include:

- **What was fixed** — concise summary of the change and root cause.
- **How to verify** — the exact e2e steps from Phase 4c (launch path, trigger, expected result).
- **Confidence** — the High/Medium/Low rating from Phase 5, with the one-line rationale.
- **Reviewer/loop summary** — number of Copilot review rounds and that the branch builds locally.
- **Known limitations / anything the user should weigh before approving.**

```powershell
gh pr edit P --repo <FORK_REPO> --body-file <final-fork-body-file>
```

Keep the plain-text `Issue M` reference; do **not** add `Closes #M` here.

---

## Phase 7 — Brief the user, get approval, then open the upstream PR

### 7a. Present the brief (MANDATORY STOP)

Give the user a short brief and **stop** for approval (use `ask_user`):

- one-paragraph summary of the fix,
- **confidence level** + rationale (Phase 5),
- e2e verification steps,
- known limitations / open questions,
- the **fork PR link** (`https://github.com/<FORK_REPO>/pull/P`) so they can inspect the code and diff.

Ask: *"Approve opening this as a PR against microsoft/PowerToys, or do you have changes?"*

### 7b. On changes requested

Apply the requested changes (agent or local), push, and run **another** review + build loop (Phase 4b–4c). Re-brief. Repeat until approved.

### 7c. On approval — open the real upstream PR

This is the **only** step that writes to `microsoft/PowerToys`, and the **only** place a real `#M` link is allowed.

1. Ensure the fork branch is current and rebased on upstream `main` — **re-run the Phase 0a sync** so the fork's `main` matches the latest `microsoft/PowerToys:main`, then rebase the head branch on it (avoids diff bloat — same discipline as `powertoys-pr-review` Step 2b/2c).
2. Build the upstream PR body from the **PowerToys PR template** (`.github/PULL_REQUEST_TEMPLATE.md` in the repo): Summary, the `Closes #M` line (real reference — intended), Validation/Test steps, screenshots/recording if the change is user-visible.

   **The upstream PR title and body must be self-contained and reference ONLY the upstream issue via `Closes #M`.** The fork is an internal staging area and must be fully abstracted away — a maintainer reviewing the upstream PR should see no trace of it. In the title/body/commits, **NEVER** mention or link:
   - the fork PR number or its `[PR N]`/mirror title (no `MuyuanMS/PowerToys#<n>`, no fork PR URL),
   - the mirrored fork issue number or `[Issue M]` mirror,
   - the fork branch name, the Copilot review-loop rounds, or "mirrored from…" notes.

   A bare `#<n>` in the body auto-links to whatever issue/PR shares that number **in `microsoft/PowerToys`**, silently pinging an unrelated upstream thread — so the only `#`-reference allowed anywhere in the upstream PR is `#M` (the issue this fix closes). Scrub the body for any stray `#<n>` before creating.
3. Create the PR from the fork head branch into `microsoft/PowerToys:main`:

   ```powershell
   gh pr create --repo microsoft/PowerToys `
     --head <FORK_OWNER>:<head-branch> --base main `
     --title "<final title>" --body-file <upstream-body-file>
   ```

4. **Verify the published PR is clean:** re-fetch the body and confirm it contains no fork reference and no `#<n>` other than `#M`:

   ```powershell
   gh pr view <UP_PR> --repo microsoft/PowerToys --json body --jq '.body' |
     Select-String -Pattern "fork|<FORK_OWNER>|mirror|#(?!M\b)\d+"
   ```

   If anything matches, edit the body (`gh pr edit <UP_PR> --repo microsoft/PowerToys --body-file <clean-file>`) before continuing.
5. **Clean up the fork mirror** so it can't cause future confusion: close the mirrored fork issue `F` and the fork PR `P`, each with a short comment pointing to the upstream PR (`microsoft/PowerToys#<UP_PR>`). Deleting the fork mirror branch is optional and may be blocked by a fork ruleset — that's harmless once its PR is closed. Do this pointing **from** the fork **to** upstream only; never post the fork PR/issue numbers back onto the upstream PR.
6. Return the upstream PR URL to the user.

> Everything before 7c stays in the fork. If the user never approves, nothing is ever posted upstream. The upstream PR must read as a standalone contribution — the fork PR and mirrored issue are internal scaffolding and are never referenced from it.

---

## Critical Rules (summary)

1. **Always run Phase 0 first:** sync the fork's `main` with upstream (0a) and check for prior/unfinished work on Issue M (0b–0c) so you resume instead of duplicating.
2. All AI work happens in `<FORK_REPO>` until explicit Phase 7 approval.
3. **Never** emit `#M` / `microsoft/PowerToys#M` / issue URL / "closes #M" anywhere except the final upstream PR body (Phase 7c). Use `Issue M` plain text everywhere else.
3b. **The upstream PR must not reference the fork.** In the upstream PR title/body/commits, the only `#`-reference allowed is `Closes #M` (the upstream issue). Never include the fork PR number, the mirrored fork issue number, the fork branch name, "mirrored from…" notes, or any bare `#<n>` (it auto-links to an unrelated upstream thread). After creating the PR, verify the body is clean and close the fork mirror (issue `F` + PR `P`) pointing to the upstream PR — never the reverse (Phase 7c steps 4–5).
4. Stop for user approval at exactly **one** gate here: before the upstream PR (7a). (The design-approval gate happens earlier, in `powertoys-issue-to-design` Phase 6.)
5. Distinguish the coding agent (`copilot-swe-agent`, drafts & fixes) from the review bot (`copilot-pull-request-reviewer[bot]`, comments).
6. The fork branch must build locally before you call the PR ready.
7. **The review loop runs until a freshly-requested Copilot review returns zero new comments.** Push before every re-review; re-request review after every push (verify `requested_reviewers` non-empty); reply to AND resolve every handled comment; only process comments newer than `last_ts`.
8. Reuse `powertoys-pr-review`'s Build Reference and resolve/reply commands rather than duplicating them.
