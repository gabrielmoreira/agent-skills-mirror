# Workflow Contract

Use this reference for the detailed product-agile workflow contract.

## Operating Model

The portable hierarchy is:

```text
Product Vision -> Product Options -> Outcome Waves -> Initiatives -> Discoveries -> Sprints
```

The model is not a full Scrum, SAFe, Shape Up, or Kanban implementation. It
keeps the useful controls from each while optimizing for AI-assisted work,
context recovery, evidence, and adaptive delivery.

## Artifact Owners

- Root `AGENTS.md` owns repo-local agent instructions and a small managed
  workflow-routing section.
- Root `SOURCE_ATLAS.md` owns source-code routing, initial source scan output,
  local source boundaries, and source-route maintenance rules.
- `vision.md` owns the adaptable product north star.
- Root `options.md` owns curated product-level, future-wave, and unknown-owner
  options before commitment. It is not a backlog ledger, completion history,
  or execution authorization surface.
- `status.md` owns current product posture, wave sequencing, active pointers,
  WIP state, blockers, candidate tracks, retained-context routes, and next
  allowed action.
- `waves/wNN-*/wave.md` owns wave-level vision: outcome, why now, scope
  boundaries, bet framing, non-goals, success evidence, outcome signals,
  initiative map, retained inputs, and transition or reroute rules.
- Wave `discoveries/wNN-dNN-*.md` owns activation, transition, or reroute
  research.
- `initiatives/iNN-*/initiative.md` owns the initiative bet, outcome signals,
  scope, durable decisions, and compact index pointers.
- `initiatives/iNN-*/options.md` owns possible initiative-local insertions
  before closeout. Product-level or later-wave options move to root
  `options.md`.
- `initiatives/iNN-*/roadmap.md` owns the adaptive strategy map, active or
  next sprint route, candidate sequence, insertion points, and revalidation
  rules.
- `initiatives/iNN-*/index.md` owns triggered compact lookup, durable history,
  meaningful artifacts, evidence routes, and supersession notes.
- Initiative `discoveries/wNN-iNN-dNN-*.md` owns initiative/sprint-shaping
  research.
- Sprint `sprint.md` owns execution-ready scope, slices, validation, and start
  checkpoint.
- Sprint `decision-log.md` owns sprint-time decisions and reversals.
- Sprint `closeout.md` owns result, evidence summary, outcome and learning
  review, mini-retro, and handoff.
- Sprint `evidence/index.md` owns evidence routing, validated claim mapping,
  gate status, redaction posture, promotion targets, and read policy.
- Root or wave `source-packs/YYYY-MM-DD-*/` own retained research and doctrine.

## Options Validation And Transition Rituals

Run options validation whenever work crosses a commitment boundary:

1. wave activation;
2. initiative activation or closeout;
3. option promotion into roadmap or discovery;
4. terminal audit;
5. sprint preview pulled from an option.

Before wave activation, review root `options.md`, relevant source-pack
readmes, and unresolved local options from the closing initiative. Promote,
park, merge, or reject options before creating the activation discovery.

Before initiative closeout, run closeout-mode options validation. Every local
option must be promoted to roadmap, moved to root options, rejected, or
removed as obsolete before closeout can pass.

Before terminal audit, run terminal-audit-mode options validation. The audit
must prove that roadmaps and options boards do not hide required unfinished
work.

Before sprint preview from an option, revalidate the option against current
repo truth. Use discovery when route, scope, contract, validation, runtime
boundary, or appetite may change. Use reviewed preview only when the route is
already decided and the preview is just freshness and approval-boundary work.

Structural workflow changes that affect artifact ownership, lifecycle gates,
scaffold output, transition policy, or recovery context require a compact
workflow-improvement discovery or equivalent accepted decision record.

## WIP Policy

Default WIP is constrained dual-track:

1. one active delivery sprint per active initiative;
2. one active discovery per active initiative;
3. one wave-level discovery only during activation, transition, or reroute;
4. options boards are pre-commitment memory, not delivery commitments or
   execution queues;
5. no sprint execution from a stale option or candidate entry.

If a repository chooses more WIP, the active status artifact must record the
reason, owner, and stop condition.

## Discovery And Delivery

Discovery is upstream of delivery, but not an endless phase gate.

A sprint may start only when one of these is true:

1. it is pulled from an accepted discovery;
2. a reviewed sprint preview proves the current candidate is still valid;
3. the work is a small direct bounded task and does not need workflow artifacts.

Use discovery when the route needs a decision. Discovery is required when
current evidence may change sequence, scope, appetite, product direction,
contract shape, runtime boundary, or the recommended path; when path-shaping
questions are unresolved; when previous closeout learning changes the route;
when standards, best practices, official docs, current primary research,
analogous-system evidence, source-pack, user, or operator evidence is needed
to choose between approaches; or when a preview cannot honestly prove that the
registered candidate is still the right next slice.

Before a reviewed sprint preview claims discovery is unnecessary, run
Discovery Triage as a fail-closed Routing Preflight. Record the trigger
categories considered before choosing preview. Trigger categories include
autonomy, authority, runtime-boundary, policy, evidence, interoperability,
agent-behavior changes, agent loops, harnesses, loop continuation, goal
judgment, budgets, and checkpoints. Record one of these outcomes:

1. `preview_ok`: the route is already decided and the preview can revalidate
   freshness, scope, risks, validation, and the approval boundary because any
   triggered evidence cannot change route, contract, scope, validation,
   runtime boundary, or implementation path;
2. `discovery_required`: external evidence or path selection may change the
   route, contract, scope, validation, runtime boundary, or implementation
   path;
3. `operator_decision_needed`: the blocking choice is product appetite,
   scope, or priority rather than research alone;
4. `not_triggered`: outside evidence was considered and is not relevant, with
   a concrete reason.

For autonomy, authority, runtime-boundary, policy, evidence,
interoperability, or agent-behavior changes, outside evidence is presumed
relevant unless triage records a concrete reason why it is not. Agent loops,
harnesses, loop continuation, goal judgment, budgets, and checkpoints are
portable trigger examples, not a requirement that all sprints run discovery.
Portable outside evidence includes industry standards, best practices,
official docs, current primary research, analogous systems, and relevant source
packs. Repository overlays may add project-specific evidence sources and
triggers.

Use a reviewed sprint preview when the route is already registered and the
task is to revalidate freshness, scope, risks, validation, and the approval
boundary before start. If preview work uncovers route-changing uncertainty,
stop the preview and promote the question to discovery before implementation.

Discovery must record current repo truth, user or operator evidence status,
relevant standards or research, relevant source-pack or analogous-system
comparison when useful, options, recommendation, risks, validation
expectations, and a user decision slot.

Discovery acceptance is incomplete when the discovery changes future sequence
but the owning `roadmap.md` still lacks that insertion, split, reroute, or
deferral, including Forecast Impact and the operator decision that accepted
the tradeoff or bought more scope. Sprint closeout is incomplete when it
changes the next route but the owning `roadmap.md` is not updated. Durable
lookup facts are promoted into `index.md` through a triggered lookup writeback.

When the previous sprint's learning affects a new route decision, the next
discovery reads the latest closeout and promotes only the routing-relevant
facts. It does not duplicate the whole closeout review.

## Outcome Signals

Waves and initiatives record qualitative Outcome Signals:

1. product or user signal: what user, operator, customer, or product-value
   evidence should move;
2. delivery or flow signal: what should improve about batch size, cycle time,
   WIP, blocked time, or route clarity;
3. quality or stability signal: what should improve about correctness,
   reliability, validation, live behavior, or failure handling;
4. context or evidence cost signal: what should stay cheap enough for agents
   and operators to recover, verify, and continue the work.

Outcome Signals are lightweight routing signals. They do not create a separate
metrics ledger, recurring report, or hard numeric KPI unless a repository
explicitly adopts one.

Discoveries and sprint previews record User Or Operator Evidence with one of
three statuses: `used`, `not triggered`, or `deferred`. Purely internal
technical work may use `not triggered`, but the artifact must say why that
evidence did not affect the current decision.

## Appetite-Boxed Forecast Calibration

Appetite-Boxed is the default forecast-control rule. Candidate counts are
forecasts, not commitments, and sequence expansion is not automatic
adaptation. When discovery or closeout finds pressure to add work, the agent
must state the pressure, propose options with tradeoffs, and ask for an
explicit operator decision to cut/defer scope, reframe, reroute, or buy more.
Appetite pressure does not justify silent under-delivery: if the accepted
objective remains reachable by continued iteration, continue; if the objective
must change, ask the operator to cut scope, reroute, block, or buy more work.

Wave and initiative owner docs record Forecast And Appetite:

1. appetite;
2. forecast range or count;
3. confidence;
4. throughput basis;
5. known unknowns;
6. scope hammers: operator-choice options that could cut, defer, or reframe
   scope;
7. expansion trigger: what requires operator decision.

`roadmap.md` records Forecast Control: completed count, registered remaining,
forecast delta, appetite state, and next scope tradeoff. Appetite states are
`within_appetite`, `at_risk`, `exceeded_pending_decision`, or
`operator_bought_expansion`.

Discoveries and reviewed previews record Forecast Impact when they change
sequence. The allowed results are `fits appetite`, `cuts/defers scope`,
`requires operator buy-more`, or `reroutes/stops`.

Sprint previews record Product Increment Contribution as `direct`,
`enabling`, or `audit`. Enabling sprints must name the visible product
increment they unblock and why a direct slice is not viable.

Two consecutive enabling or prerequisite sprints trigger a route review asking
whether to ship a vertical proof, cut/defer scope, reroute, or explicitly buy
more enabling work. The agent recommends; the operator decides. Major
capability candidates must decompose prerequisite risks and the first usable
product increment before acceptance.

## Bet Framing

Every initiative and non-trivial sprint records:

1. `appetite`: how much effort/risk is worth spending before re-evaluation;
2. `success evidence`: what proof makes the bet worth keeping;
3. `circuit breaker`: what stops or reroutes the work;
4. `non-goals`: what must not sneak into the bet;
5. `deferral path`: where useful not-now work will live.

Bet framing is not a second governance system. It prevents roadmap candidates
and options boards from becoming invisible backlog commitments.

## Reviewed-Mode Preview

In reviewed mode, a move-on request opens a preview only. The preview states:

1. the sprint has not started;
2. what would happen if it started now;
3. the recommended path;
4. questions that change path, if any;
5. the exact approval boundary.

Non-trivial previews use this order:

1. `What Repo Truth Says`
2. `Inference`
3. `Discovery Triage`
4. `Why Preview Instead Of Discovery`
5. `User Or Operator Evidence`
6. `Forecast Impact` when sequence changes
7. `Product Increment Contribution`
8. `Implementation Paths`
9. `Recommendation`
10. `Questions That Change The Sprint Path`
11. `Approval Boundary`

A later explicit approval starts the sprint directly and does not trigger a
second start prompt.

## Candidate Queues

Candidate queues are not backlogs.

Rules:

1. candidates are hypotheses, not execution authorization;
2. candidate counts are forecasts, not commitments;
3. stale candidates revalidate on touch;
4. candidate states are `required`, `probable`, `conditional`,
   `adaptive insertion`, `parked`, or `terminal audit`;
5. a final audit candidate stays visible until initiative completion;
6. a pre-audit continuation window must exist before final audit;
7. expansion beyond appetite requires operator choice after the agent presents
   cut/defer, reroute, and buy-more tradeoffs.

The roadmap owns candidate order and sequence-change rationale. The index owns
lookup and durable history. Do not duplicate sprint token ledgers in the
roadmap.

## Sprint Outcome And Learning Review

Sprint closeout records:

1. what the sprint achieved;
2. how the project is better after the sprint;
3. what could have been done better;
4. whether the learning changes the next route, stays local, or suggests a
   workflow improvement.

Route-changing learning must be promoted into `roadmap.md` before closeout
passes. Durable lookup learning must be compactly promoted into the triggered
T3 `index.md`.
Every material achievement, project-improvement, validation, or route-changing
claim in the closeout must be backed by `evidence/index.md`. Required
objective proof cannot be recorded as deferred while the original sprint
objective closes as passed; missing or failing required proof keeps the sprint
active or blocked until it passes or the operator explicitly changes scope.

Sprint closeout also records Forecast Delta: planned versus actual, hidden
prerequisite discovered, remaining forecast impact, and whether `roadmap.md`,
`index.md`, or `status.md` were updated.

## Objective-Complete Sprint Completion

Choose an objective-complete action: implement and validate all work required
for the accepted sprint objective and exit criteria. Avoid unrelated expansion,
but do not cut, defer, or split required proof just to preserve scope or
budget.

Scope-control words like `smallest`, `narrow`, and `only as needed` mean the
smallest objective-complete vertical slice. They do not authorize stopping at
the first green focused test, skipping a named repo-owned surface, or omitting
required evidence. If the smallest objective-complete slice no longer fits the
accepted sprint, ask the operator to cut scope, reroute, block, or buy more.

A sprint closes as passed only when every required objective gate has fresh
named passing evidence after the final relevant change. Smoke tests,
orientation scans, or partial deterministic proof cannot stand in for a
required live or end-to-end gate named by the sprint.

## Closeout Mini-Retro

Sprint closeout records:

1. process friction;
2. evidence cost;
3. context cost;
4. decision latency;
5. workflow adjustment, or `none`;
6. retro evidence check: objective signal, controllability, and whether the
   friction repeated from prior work;
7. whether the adjustment is local or should be promoted to this skill after
   repeated evidence.

## Recovery Rules

Prefer objective-complete correction:

1. missing operations root: bootstrap it;
2. missing wave: create the wave before initiative work;
3. missing initiative: create it under the owning wave;
4. missing discovery: create or accept discovery before delivery pulls work;
5. stale candidate: run fresh discovery or reviewed preview;
6. placeholder sprint: prepare the active or next sprint before start;
7. missing evidence index: backfill it before closeout;
8. oversized status or wave files: move detail to owner artifacts.
