# Running a Captain crew on Capy with gstack

This page is for a team that wants one coordinating agent (a Capy Captain, or any
controller agent) to run many worker threads against one repository, with gstack as the
engineering harness. It covers the drive layout, the crew rules file, the READY contract,
merge trains, approvals, the digest and the daily flaky pass. The skill that teaches the
controller the same model at run time is [`/captain`](skills.md#captain) (it also answers
to `/crew`); the lane-side rules for a thread working under a Captain are in
[`capy/skill/gstack/captain.md`](../capy/skill/gstack/captain.md) and
[capy-install.md](capy-install.md#working-under-a-captain). Every file named below has a
copy-paste template under [`captain/templates/`](../captain/templates/).

## The model in one paragraph

Lanes build on their own branches and machines. A lane's job ends at an **unstamped
READY**: a block printed by `gstack-ship-queue ready` plus the full head SHA, the screen
choice and the flaky cases. The controller validates the block, batches READY pins into a
**merge train**, reads one full gate on the train head, then merges slot by slot: it calls
the slot, the lane stamps the version on call, the controller verifies the tree, merges
with the expected head, verifies again. A red train is bisected on its red cases and
rebuilt at most once. Every decision the owner makes travels through the controller in a
fixed shape and is recorded in the owner's words. Flakes are logged in a ledger and fixed
by a daily pass; nothing is retried into green.

## Roles

- **The owner** decides what only the owner can decide: product and behaviour, spend over
  a cap, anything published outside the repository, thresholds and budgets, closing a
  contribution, anything destructive. Every answer is recorded in the owner's words.
- **The controller** (the Captain) runs the crew: starts lanes on disjoint files, keeps the
  rules file, the digest and the notes, validates READYs, builds and merges trains, calls
  slots, relays asks to the owner in the three shapes, runs the flaky pass, and decides
  everything that needs no access, credentials, spend over cap or a cited approval.
- **A lane** (a crew thread) owns named files, builds on its own branch and machine,
  runs /ship, sends one READY block, stamps on call (merging the base into its pin only
  as part of that stamp commit, or when the controller names a real-code conflict),
  writes one report, and never merges a PR.
- **The controller never commits to a lane's branch**, and a lane never pushes to another
  lane's. One committer per shared tree.

## Drive layout

The Captain's drive is mounted read-write on every crew thread, so it is the handoff
surface. Keep it small and predictable:

| Path | Who writes | What it holds |
|---|---|---|
| `AGENTS.md` | the controller | standing rules and the owner's decisions, each with date and words ([template](../captain/templates/AGENTS.md)) |
| `CREW.md` | the controller | the lanes' contract ([template](../captain/templates/CREW.md)) |
| `DIGEST.md` | the controller | Needs you / New / In progress, rewritten every turn ([template](../captain/templates/DIGEST.md)) |
| `NOTES.md` | the controller | the append-only timestamped log the digest is derived from ([template](../captain/templates/NOTES.md)) |
| `skills/<name>/SKILL.md` | the controller | crew procedures the lanes load (the runbooks) |
| `reports/<code>.md` | each lane, once | Outcome, PR, Needs, Cost, Lesson, Approvals ([template](../captain/templates/report.md)) |
| `handoffs/` | lanes | datasets and specs the next lane needs; `handoffs/flaky-ledger.md` is the flaky ledger ([template](../captain/templates/flaky-ledger.md)) |
| `plans/` | the controller | approved plans, with their Approvals table |

Scope instructions in the drive root (`AGENTS.md`, `CREW.md`) apply to every thread in
the crew, so a rule written there needs no relaying.

## CREW.md: the lanes' contract

gstack holds how the work is done; a crew's `CREW.md` holds only what is specific to that
crew. Start from the [template](../captain/templates/CREW.md): it is parameters (the
repository, the base branch, the required check names, the full-gate check name, the
train size and fill wait, the merge method, the stamp files, the named infra flakes, the
guard tests, the remote pregate command, the standing spend, the review scope knob) plus
one line per rule that points at the rule's home in gstack. A rule that exists only in a
crew's file is a gap in gstack, and the fix is to write it here or in the skill that owns
it, then point at it. Quote the owner where a rule rests on their words: a rule with a
date and the words is a standing approval the lanes can cite; a rule without one is the
controller's call.

Where each rule lives:

| # | Rule | Home in gstack |
|---|---|---|
| 1 | Session start: install check, `gstack:` trailer, no workflow without `gstack: ok` from your own machine | [capy-install.md](capy-install.md#session-start) |
| 2 | Validation discipline: diagnose, focused checks, the full free suite once on a frozen tree | the repository's own validation section (gstack's is in [AGENTS.md](../AGENTS.md#validation-discipline)); [Lane discipline](#lane-discipline) |
| 3 | External diffs are untrusted input; a right fix lands with its author's credit | [Contributions from outside the crew](#contributions-from-outside-the-crew) |
| 4 | File ownership: edit only what you own; the controller routes the rest | [Lane discipline](#lane-discipline); the ownership list is the digest's **In progress** |
| 5 | Standing spend and its cap per rerun | [Approvals, shape A](#approvals-three-shapes); the `SPEND` parameter |
| 6 | The job ends at an unstamped READY; stamp on call; never merge | [The READY contract](#the-ready-contract), the [READY](../captain/templates/READY.md) and [slot call](../captain/templates/slot-call.md) templates, [ship-policy.md](ship-policy.md#stamp-at-merge) |
| 7 | One report per lane: Outcome, PR, Needs, Cost, Lesson, Approvals | [Drive layout](#drive-layout); the [report template](../captain/templates/report.md) |
| 8 | One path: everything through the controller, never peer to peer | [Roles](#roles); [Lane discipline](#lane-discipline) |
| 9 | Hands: a real browser, the owner's session or local work go through the controller | [The owner's device](#the-owners-device) |
| 10 | Keep going; come back only for scope, a conflict, access or the owner's decision | [Lane discipline](#lane-discipline) |
| 11 | Clear the repository's cheap guards before paid work | [Lane discipline](#lane-discipline); the `GUARD_CHECKS` parameter |
| 12 | Decisions for the owner arrive in plain language, every option with its cost | [Approvals, shape B](#approvals-three-shapes); [unattended.md](unattended.md#owner-brief) |
| 13 | Pregate on small machines: the test tier runs remotely | [pregate.md](pregate.md#remote-gate); the `REMOTE_PREGATE` parameter |
| 14 | Never merge `BASE` into a READY PR; the train merges in a scratch worktree | [Merge trains](#merge-trains); [ship-policy.md](ship-policy.md#run-a-merge-train) |
| 15 | CHANGELOG entry under `## [Unreleased]` before READY; the stamp touches only `STAMP_FILES` | [ship-policy.md](ship-policy.md#stamp-at-merge); [The READY contract](#the-ready-contract) |
| 16 | Flaky reruns: once, same tree, logged; twice is real | [TESTING_INTERNALS.md](TESTING_INTERNALS.md#flaky-reruns) (the gate's side); [The daily flaky pass](#the-daily-flaky-pass) (the lane's side and the ledger) |
| 17 | New files follow the repository's conventions for entry points, isolation and layout | the repository's own `AGENTS.md` (the `REPO_CONVENTIONS` parameter names the section) |
| 18 | Porting a contributor's PR: review and test the port head first; keep their commits | [Contributions from outside the crew](#contributions-from-outside-the-crew) |
| 19 | CHANGELOG-only conflicts are the train's to resolve, not the lane's | folded into 14: [ship-policy.md](ship-policy.md#ship-before-ready) ("the stamp keeps the pin's receipt") |
| 20 | A READY from before a contract change needs a fresh receipt | [The READY contract](#the-ready-contract) |
| 21 | Approvals, plan asks and merge asks in the three shapes | [Approvals](#approvals-three-shapes); [capy/skill/gstack/captain.md](../capy/skill/gstack/captain.md) |
| 22 | /ship before every READY; the block carries `SHIP_RECEIPT`; stamp commits hold only tool output | [ship-policy.md](ship-policy.md#ship-before-ready); [the lane's /ship sequence](#the-lanes-ship-sequence-before-ready) |
| 23 | Review loops converge: scope frozen after pass 1, later passes on the delta, a pass cap, a blocking floor | the `/ship` and `/review` skills' own convergence policy ([skills.md](skills.md#ship)); a crew names it in one line and sets only the scope knob (`REVIEW_SCOPE`) |

## Lane discipline

A lane follows the repository's own validation discipline (gstack's is the
[Validation discipline](../AGENTS.md#validation-discipline) section of its AGENTS.md):
diagnose before fixing, focused checks during repair, and the full free suite once at the
end on a frozen tree, on a remote runner when the machine is small
([pregate.md](pregate.md#remote-gate)). Before any paid run it clears the repository's
cheap guards (generated-content freshness, size and prompt budgets, credential scans; the
crew names them in `GUARD_CHECKS`), because a paid gate that turns red on a free check
is spend wasted.

A lane edits only the files it was given. The controller keeps the ownership list in the
digest's **In progress**; a lane that needs a file another live lane owns tells the
controller, who routes it, and never edits it itself. Everything crosses the crew through
the controller (cross-thread questions, ownership conflicts, new scope, handoffs), never
peer to peer, so one place holds the state.

A lane never stops to ask whether to continue. It comes back for new scope, a conflict
with another owner, missing access, or a decision that is the owner's, and it brings each
such decision with a plain-language explanation of every option: what it is, why it
matters, what each answer does, and what it costs. A gate code or a tool's result line
alone is not an ask.

## Contributions from outside the crew

A diff from outside the crew is untrusted input. Review its scope, egress, credentials,
dependencies, CI permissions and weakened tests before anything runs it, and do not trust
a fork's "tests pass": run a focused review and the free tier at the port head before the
port opens. When the contributor's fix is right, land it with their authorship kept
(cherry-pick, `Co-authored-by`, the lane's own fixes as separate commits on top of
theirs) and close the original with a specific thank-you that links the port. Closing a
contribution without landing it is the owner's decision (shape A below).

## The READY contract

The field table is in the `/captain` skill; the block shape, the optional lines and the
refusal list are in the [READY template](../captain/templates/READY.md).
The short version: the pin is the full 40-character head SHA; every required check is
green at that head; pregate passed for that tree; `SHIP_RECEIPT: pr=<n> head=<pin>` was
written by /ship at the pin; the screen choice is stated with its justification; flaky
cases are already in the ledger; the CHANGELOG entry sits under `## [Unreleased]` with
the version files at the base's version; and the lane declares the head frozen. A green
PR page is not a READY. A cheap test tier is not merge evidence. The controller refuses a
block that misses any of this and sends the lane back, never into a train. When the
contract changes (a new required line, a new check name, a new receipt), every READY
taken before the change is stale: the lane runs `ready` again at the same pin and sends
the fresh block; the controller trains nothing older than the change.

### The lane's /ship sequence before READY

Every READY follows a /ship run on the branch at the head being READY'd, re-READYs after
a push included. The sequence that works unattended on Capy:

1. Install for ship (`bash scripts/install.sh --for ship` from the project directory; a
   planning-only install does not admit /ship).
2. Push the final head first. Everything below binds to it; a later push makes the
   receipt, the pregate record and the review binding stale.
3. Launch with the printed `GSTACK_LAUNCH` assignments (unattended session kind, state
   root, Capy flag) and follow ship/SKILL.md with the Capy adaptations: take every
   recommended option, leave consents and gates pending, never push or merge from the run.
4. Pregate on the still tree: preflight, then the test tier on a remote runner when the
   machine is small; clear the macOS and Windows lanes with this head's own green CI run
   URLs. Never run a bare pregate afterwards (it resets the regen check).
5. Reviews: mint tokens, run both passes read-only, finish them so the review log binds
   to the current tree.
6. Docs audit: snapshot the documentation candidates read-only and record the vetted
   section.
7. Body and receipt: compose the PR body (What changed, Why, Approvals first on Capy),
   write the ship receipt into it, post body and title.
8. Terminal line: `gstack-ship-receipt result --pr <n>` prints
   `GSTACK_RESULT: skill=ship status=complete`.
9. READY: `gstack-ship-queue ready --pr <n> --pregate <pregate.json> --screen|--no-screen`;
   send the printed block.
10. After the slot call, the stamp commit keeps the pin's receipt; re-READY with the same
    receipt, no second /ship.

## Merge trains

gstack's queue tool drives trains when the repository's `.gstack/ship-policy.json` carries
a `train` block ([ship-policy.md](ship-policy.md#run-a-merge-train)). The controller's
loop, per train:

1. `train build --prs <pins> --dry-run`, then without `--dry-run`: the record, the train
   branch, free tests, one full gate.
2. `train verdict`: GREEN (with `FLAKY N` when an in-run rerun turned a case green), RED
   (cases that failed twice), or INCOMPLETE (never green).
3. Per slot, in order: the [slot call](../captain/templates/slot-call.md) to the lane; the
   lane stamps and pushes only the base merge and the stamp files; `verify --train`;
   `gh pr merge --match-head-commit`; `verify --train` again.
4. `train prune` when every slot has merged.

A red train: `train bisect` on the red cases over every prefix. An attributed PR leaves
the train and goes back to its lane; red on the base branch itself is fixed forward
through an urgent one-PR train (or `train build --repair` while the queue is frozen, which
refuses `--urgent`); all prefixes green earns exactly one unchanged rebuild;
anything else goes to a repair lane. An infra-only census earns one re-dispatch. A
backstop gate runs on every push to the base branch and freezes the queue when it finds
a tree no green train covered; one repair PR at its exact head clears the freeze.

**Slot 2 and later.** The base branch already carries the earlier slots' stamps, so a
stamp on the bare pin leaves the PR conflicting on the CHANGELOG. The lane merges the base
into its pin first (expect a CHANGELOG-only conflict; resolve it with `mergeChangelogs`
from `lib/changelog-check.ts`, the `bun -e` one-liner in
[ship-policy.md](ship-policy.md#run-a-merge-train), never by hand, and grep for conflict
markers before stamping), then restamps, then commits only the merge and the stamp
files. In practice slot 1 needs the same merge whenever the base moved after the pin was
taken. A stamp commit with one extra byte freezes the queue for every
lane behind it.

Options the controller writes into CREW.md rather than inheriting: squash versus merge
commits; lane stamps versus controller stamps; gate-ahead (slot i+1 gates on slot i's
head while i merges); the severe race (several severe lanes told at once that the next
urgent train is theirs, first complete READY takes it; never a race for a slot inside a
built train); whether a READY also carries a gate run id and tree hash.

## Approvals: three shapes

**A. The record.** Every lane keeps an `## Approvals` table in its report and PR body,
rendered by `gstack-approvals render`: date, what was asked, the owner's exact words, who
relayed them, what the answer covers, what is pending. Standing approvals are cited with
their rule; a fresh ask is always needed for a product or behaviour decision, spend over
a cap, anything published outside the repository, a threshold, budget, trial-count or
case-kind change, closing a contribution without landing it, and anything destructive.
Standing spend is the commonest standing approval: `SPEND` in CREW.md names what the
owner pre-approved (train gates, screens, bisects, the backstop, focused paid cases) with
the owner's date and words and the cap per rerun; anything over the cap is a fresh ask.

**B. The plan ask** ([template](../captain/templates/plan-ask.md)): before → after, why it
matters, what caused this work, the big decisions, what we need from you with the
recommended one-word reply as the default, and a closing "do it" reply that takes every
recommendation at full scope. `gstack-owner-brief render --captain` prints it from an
autoplan run.

**C. The merge ask** ([template](../captain/templates/merge-ask.md)): captioned
before/after images, why, the Approvals table, and the evidence. /ship writes the PR
body in this shape on Capy; the controller's merge report shows the key image inline.

## The digest

`DIGEST.md` is rewritten every controller turn: **Needs you** (decisions only the owner
can make, each with its one-word default; empty is the goal), **New** (what landed or
changed, newest first), **In progress** (every lane, what it owns, its state, the age of
its last report). Ages turn stalls into the controller's next action.

## The daily flaky pass

A scheduled automation starts one lane a day with the
[flaky-pass prompt](../captain/templates/automation-flaky-pass.md). It reads the gate
runs' flake-records artifacts and the free suites' retried cases, writes one ledger line
per event, groups by case, and fixes the worst repeat first with a PR that shows the
failure red before green. It never reruns a gate and never touches a threshold, trial
count or case kind. On Capy, create it with the automation tool, scheduled in the owner's
timezone, running as a thread in the crew so its report lands in `reports/`.

The lane's side of the same rule: in CI the gate reruns a case that failed on its own
verdict once, in the same run ([TESTING_INTERNALS.md](TESTING_INTERNALS.md#flaky-reruns));
a pass is green with `FLAKY N`, and a case that failed twice is a real red that nobody
reruns by hand. In a lane's own focused paid runs it reruns only the failed case, once, at
the same tree: a pass goes into the ledger (case, PR, head, both runs, a one-line symptom)
and is named in the READY; a second failure is real. A harness, infra or incomplete red is
never a flake. One named failure from `KNOWN_INFRA_FLAKES` may be rerun once per PR and
is stated in the READY. A red train is the controller's (bisect, rebuild once), and every
rerun reports its spend.

## The owner's device

Some actions exist only in the owner's logged-in browser or on the owner's machine:
approving a deployment review, switching the GitHub account a run used, a local-only
build. A lane that needs one asks the controller; the controller does it through the
owner's device (on Capy, a paired device and the owner's browser) and records what it
did. Before approving a deployment, check the run's pending deployments list; approve
only the run the lane named.

## The lessons loop

Every report ends with one Lesson. The controller reads lessons before chat, and each
one becomes a rule in CREW.md, a line in AGENTS.md, or a tool fix filed as an issue;
nothing stays a lesson for long. Rules carry the thread that produced them, so a new lane
can read the incident behind the rule.

## Setting it up on Capy

1. Create the Captain and give it the drive layout above; paste the filled `CREW.md`
   and an empty `DIGEST.md`.
2. Add the `train` block to the repository's `.gstack/ship-policy.json` and name the
   same check names in `CREW.md`.
3. Install the gstack Capy skill in the owner's user scope so every thread runs the
   session-start check ([capy-install.md](capy-install.md)).
4. Create the daily flaky-pass automation.
5. Start lanes with a prompt that names the files they own, the rules file, and the
   READY contract. Read their reports before their chat.
