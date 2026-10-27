---
name: powertoys-pr-review
description: "Review a microsoft/PowerToys PR with at most three cloud review requests, grounded architectural early exit, focused local fixes and exact-head validation. Returns author-facing review drafts and private resume state. Never posts upstream without explicit approval."
---

# PowerToys PR Review

Own one PR's review, not the drain. Finish the next useful operation and return
a durable result. Do not build another orchestration or permission framework.

## Inputs and setup

Inputs: upstream PR number, configured writable fork, saved state (if any),
suite revision and coordinator-assigned operation/deadline.
Read [setup-and-mirror.md](./references/setup-and-mirror.md) only for
discovery/mirroring, and [prerequisites.md](./references/prerequisites.md) only
for a missing prerequisite. Self-checks use the author's existing branch.

Run `Get-UpstreamPrReviewGate.ps1` on resume, after each round and its
processing, and before a request, expensive validation or finalization.
Closed/merged/draft stops work. A new head requires repinning and reassessment,
not relabeling old evidence. Preserve consumed requests across heads/sessions.
API errors are explicit errors, not assumed unchanged state.

## The worker loop

The authoritative transition rules and command recipes are in
[copilot-review-loop.md](./references/copilot-review-loop.md).

```text
resume existing fork work; pin the live upstream head
prepare focused validation commands; do not compile before the first request
consume any saved request before issuing a new one
for at most three total cloud requests, including preserved history:
    request -> save identity -> wait without holding a worker/build slot
    read the matching review and all its comments
    assess upstream validity and intent/architecture before first-round fixes
    if a grounded design flaw: stop new rounds and prepare overall comments
    otherwise fix valid localized issues, push, reply and resolve fork threads
    if fresh zero-comment convergence or request cap: leave the loop
validate the final supported output -> draft -> return
```

Three is the initial request plus at most two re-requests, not three per
session/lane/head. Timeouts consume allowance. Never request a fourth.
The cap ends requests, not assessment, validation or drafting.
Cloud review remains required; no automatic local-review substitute.

## Validation and drafting

Load only the reference needed for the current operation:

| Operation | Reference |
| --- | --- |
| Check whether intent/design is flawed | [architecture-review.md](./references/architecture-review.md) |
| Prove findings on upstream; check counterevidence and fork-only regressions | [finding-grounding.md](./references/finding-grounding.md) |
| Run smallest affected checks; reuse verified identical inputs | [build-and-test.md](./references/build-and-test.md) |
| Map findings to diff, form minimal/atomic suggestions, draft author-ready prose | [drafting-and-posting.md](./references/drafting-and-posting.md) |
| Community contributor context checks, without process nags for members/bots | [phase0-context-review.md](./references/phase0-context-review.md) |

Validate the literal final suggestion blocks on the pinned upstream tree,
including raw-blob EOL safety. A passing altered fork is not proof of the
upstream tree. Architectural concerns need grounded evidence, not an invented
replacement implementation. Never copy unassessed cloud comments.

## Return exactly one outcome

| Outcome | Required output / next step |
| --- | --- |
| Cloud pending | Private saved request and next check; release slot. |
| Needs validation | Private commands/inputs and findings; coordinator queues the build slot. |
| Review with findings | Current-head drafts plus private grounding/validation; coordinator publishes `post_review` (or deliberate `request_changes`). Allowed at cap/architectural exit without clean convergence. |
| Clean review | Fresh substantive zero-comment cloud result, zero unresolved threads, exact-upstream checks and context complete; `stage: review_ready`, zero proposed comments. |
| Excluded/head changed | Stop obsolete work; return live gate observation for inventory refresh or repinning. |
| Actual failure | Private exact error, evidence and next remediation; preserve supported drafts. Never publish a blocker as a PR defect. |

Keep `number`, upstream `head_sha`, `source_updated_at`, consumed requests
(`round` in legacy ledgers), phase, request identity, evidence/receipt paths,
and concrete next operation in the private handoff. A worker return is not
proof of publication; the coordinator acknowledges delivery separately.

## Permissions and independent use

Fork feature-branch commits/pushes and fork thread replies/resolution are
normal review work. Preserve shared history; no reset/force-push recovery.
Never write dashboard data from a worker or expose fork/local provenance in
author-facing bodies. For multiple direct reviews, use
[batch-parallel.md](./references/batch-parallel.md); no nested workers.

Without a coordinator, execute the same transitions yourself and present the
validated drafts. Upstream posting is a separate explicitly approved action:
use `Test-ReviewData.ps1` and `Publish-ApprovedReview.ps1`, never ad-hoc posting.
Do not approve the original PR; the human makes that decision.
