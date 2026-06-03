# Artifact Contracts

Use these contracts when creating or validating portable `ub-workflow`
artifacts.

## Project Root Companions

Required project-root files:

1. `AGENTS.md`
2. `SOURCE_ATLAS.md`

`AGENTS.md` owns the repo-local agent overlay. `SOURCE_ATLAS.md` owns source
routing and is seeded once during bootstrap from visible project roots. Later
updates are event-based when source boundaries, package lanes, or test
topology change.

## Operations Root

Required root files:

1. `vision.md`
2. `options.md`
3. `status.md`
4. `WORKFLOW_ATLAS.md`
5. `SOURCE_PACK_ATLAS.md`
6. `AGENTS.md`

Operations-root files should be compact. Detailed workflow rules belong in
this skill; repo overlays should point here instead of copying the whole
contract.

Artifact frontmatter, `context_tier`, `summary_budget_lines`, context receipts,
retained-context reads, evidence index shape, and broader writeback receipts are
defined in `references/context-management.md`. Trace IDs, tags, trace routes,
and owner-only trace-token policy are defined in `references/trace-tokens.md`.

## `vision.md`

Minimum sections:

1. product promise;
2. audiences;
3. durable principles;
4. capability pillars;
5. evidence questions;
6. change rule.

## Root `options.md`

Minimum sections:

1. board rules;
2. next-wave candidate lane;
3. probable-later-wave lane;
4. unassigned product option lane;
5. update rules.

Every active option card must include:

1. suggested home;
2. assignment confidence;
3. evidence links;
4. why it matters;
5. promotion trigger;
6. revalidation rule;
7. last reviewed date.

Options boards are not ledgers. Do not add `Done`, `Completed`, `Closed`, or
archive-style lanes. Remove option cards after promotion, rejection, merge, or
completion once the receiving artifact owns the durable trace.

## `status.md`

Minimum sections:

1. current product posture;
2. current operating state;
3. WIP state;
4. active pointers;
5. blockers;
6. wave sequence;
7. conditional candidate tracks;
8. retained-context routes;
9. next allowed action.

Avoid chronological ledgers, broad reading queues, and sprint history. Update
owned facts by replacement.

## `wave.md`

Minimum sections:

1. outcome;
2. status;
3. why now;
4. scope boundaries;
5. bet framing at wave scale;
6. forecast and appetite;
7. non-goals;
8. success evidence;
9. outcome signals;
10. initiative map;
11. retained inputs;
12. transition and reroute rules.

## `initiative.md`

Minimum sections:

1. summary;
2. outcome bet;
3. appetite;
4. success evidence;
5. circuit breaker;
6. forecast and appetite;
7. outcome signals;
8. goals and non-goals;
9. constraints;
10. durable decisions;
11. current status;
12. index pointers.

## Initiative `options.md`

Minimum sections:

1. board rules;
2. possible initiative insertion lane;
3. deferred-to-product-options lane;
4. update rules.

Every active local option card uses the same fields as root option cards.
Before initiative closeout, every local option must be promoted, moved to root
options, rejected, or removed as obsolete.

## `roadmap.md`

Minimum sections:

1. objective;
2. current position;
3. forecast control;
4. active or next sprint route;
5. adaptive plan, candidate route, or options pointer;
6. sequence changes;
7. revalidation rules;
8. pre-audit continuation window;
9. final audit candidate;
10. update rules.

The roadmap is an adaptive strategy map, not a token ledger. Discovery-driven
insertions, splits, reroutes, and deferrals must be promoted here before the
discovery is accepted. Closeout-driven next-route changes must be promoted
here before sprint closeout passes.

Registered candidate briefs belong in the roadmap because they are live route
and forecast intent. Keep evidence routes and trace lookup in `index.md`.

Forecast And Appetite records appetite, forecast range/count, confidence,
throughput basis, known unknowns, operator-choice scope hammers, and expansion
trigger. Forecast Control records completed count, registered remaining,
forecast delta, appetite state, and next scope tradeoff. Expansion beyond
appetite must show the operator decision to cut/defer, reroute, or buy more.

## `index.md`

Minimum sections:

1. current snapshot;
2. forecast snapshot;
3. durable direction;
4. artifact routes;
5. meaningful accepted discoveries;
6. completed sprints and evidence indexes;
7. trace routes;
8. supersession notes;
9. update rules.

The index is the triggered T3 compact lookup and durable-history surface. It
replaces separate initiative rollups and artifact indexes. It should not own
live candidate briefs, active route decisions, or current forecast control.

## Discovery Briefs

Wave discovery path: `waves/wNN-*/discoveries/wNN-dNN-slug.md`.
Initiative discovery path:
`waves/wNN-*/initiatives/iNN-*/discoveries/wNN-iNN-dNN-slug.md`.

Minimum sections:

1. question;
2. context receipt;
3. repo truth;
4. user or operator evidence status;
5. outside research, standards, official docs, current primary research, or
   best-practice comparison when relevant;
6. source-pack or analogous-system comparison when relevant;
7. options;
8. recommendation;
9. forecast impact when sequence changes;
10. risk and stop conditions;
11. validation expectations;
12. decision slot.

Forecast Impact is required when a discovery or reviewed preview changes
sequence. It must state one of `fits appetite`, `cuts/defers scope`,
`requires operator buy-more`, or `reroutes/stops`.

## `sprint.md`

Minimum sections:

1. objective;
2. accepted discovery or reviewed preview source;
3. fail-closed Routing Preflight before choosing preview;
4. discovery triage before claiming discovery is unnecessary;
5. why preview instead of discovery when the source is a reviewed preview;
6. product increment contribution;
7. bet framing;
8. exact scope;
9. execution slices;
10. affected areas;
11. operational surface preflight when triggered;
12. Project Evolution Gate when triggered;
13. validation plan;
14. Live Validation Matrix;
15. user or operator evidence status;
16. reviewed-mode start checkpoint when active;
17. context receipt;
18. exit criteria.

Operational surface preflight is triggered when a sprint introduces or changes
a repo-owned surface that future operators, users, code, tools, agents, or
integrations may rely on. Operational surfaces include, when present:
persisted files, caches, logs, queues, databases, generated artifacts,
configuration, secrets-adjacent state, network endpoints, background jobs,
scheduled tasks, public API facets, CLI commands, UI routes, plugin extension
points, telemetry streams, and external integrations. The sprint preview must
identify the surface owner, lifecycle, visibility, safety policy, validation
path, and whether an existing inventory, topology, registry, route map, or
analogous owner document must be updated. If ownership, lifecycle, safety
policy, validation, or inventory impact is unclear enough to change scope,
architecture, risk, or acceptance criteria, promote discovery before
execution.

When `sprint.md` uses words like `smallest`, `narrow`, or `only as needed`,
the artifact must make clear that they mean the smallest objective-complete
vertical slice. Every named owned surface, required evidence gate, and exit
criterion remains in scope unless the operator explicitly changes the
objective.

## `decision-log.md`

Minimum sections:

1. purpose;
2. decisions;
3. reversals and deferrals;
4. evidence pointers;
5. carry forward.

## `closeout.md`

Minimum sections:

1. outcome summary;
2. outcome and learning review;
3. forecast delta;
4. evidence pointer;
5. validation result;
6. broader writeback decisions;
7. Project Evolution Gate result when triggered;
8. mini-retro;
9. handoff;
10. next recommendation.

## `evidence/index.md`

Minimum sections:

1. state;
2. validated claims;
3. evidence files;
4. required objective gates and optional or deferred evidence;
5. redaction and retention;
6. promotion;
7. read policy.

The evidence index is a claim-to-proof router. It should let a future reader
verify every material closeout result, validation claim, and route-changing
learning without loading raw evidence by default. It does not own the sprint
narrative, outcome review, mini-retro, or trace tokens.

Required objective gates must be labeled separately from optional,
not-triggered, blocked, out-of-scope, or operator-deferred checks. A required
objective gate cannot be operator-deferred while the original sprint objective
closes as passed.

Outcome Signals, Forecast And Appetite, Forecast Control, Forecast Impact,
Product Increment Contribution, Forecast Delta, user/operator evidence status,
decision latency, and retro evidence checks belong in the owning wave,
initiative, roadmap, discovery, sprint, or closeout surfaces.
They must not create a separate metrics, forecast, trace, or retro atlas.

Sprint evidence folders include a `.gitignore` for generated runtime scratch
state. Treat any project-specific scratch directories listed there as local
scratch unless a reviewed export policy explicitly promotes a redacted
subset to committed evidence.

## Source Packs

Source-pack roots use `YYYY-MM-DD-slug/` and include `00-readme.md`.

The readme states:

1. status;
2. creation or migration date basis;
3. read triggers;
4. do-not-read triggers;
5. default section limit;
6. promotion rule.
