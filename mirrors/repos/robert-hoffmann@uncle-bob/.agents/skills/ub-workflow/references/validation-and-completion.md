# Validation And Completion

Use this reference for readiness, closeout, and completion checks.

## Wave Readiness

A wave is ready when:

1. `wave.md` states outcome, why now, scope boundaries, success evidence,
   outcome signals, Forecast And Appetite, initiative map, and transition or
   reroute rules;
2. any activation discovery is accepted;
3. at least one initiative can be created without relying on chat history;
4. root options were reviewed for activation candidates;
5. source-pack routes are explicit when retained research is needed.

## Initiative Readiness

An initiative is ready for sprint planning when:

1. `initiative.md` has outcome bet, appetite, success evidence, circuit
   breaker, outcome signals, Forecast And Appetite, goals, non-goals, and
   constraints;
2. `roadmap.md` has Forecast Control, an adaptive plan, active or next route,
   and revalidation rules;
3. `index.md` exists as a triggered T3 durable lookup and history surface;
4. `options.md` exists for possible local insertions before closeout;
5. the active or next discovery is accepted or explicitly pending;
6. WIP state is compatible with the constrained dual-track policy.

## Discovery Readiness

A discovery is ready for decision when:

1. repo truth is current enough for the question;
2. user or operator evidence status is `used`, `not triggered`, or `deferred`
   with a reason and decision impact;
3. relevant source packs, standards, donor notes, or outside research are cited
   or explicitly skipped;
4. options and recommendation are clear;
5. risks and stop conditions are explicit;
6. validation expectations are named;
7. roadmap-changing insertions, splits, reroutes, or deferrals have Forecast
   Impact and have been promoted into the owning `roadmap.md`;
8. option promotions, demotions, or removals are reflected in root or
   initiative-local `options.md` when relevant;
9. the decision slot is ready for operator acceptance, rejection, or redirect.

## Sprint Content Readiness

`sprint_content_ready` is `pass` only when:

1. the sprint is pulled from accepted discovery or reviewed preview;
2. `sprint.md`, `decision-log.md`, `closeout.md`, and `evidence/index.md`
   exist;
3. the sprint has one objective and execution-ready slices;
4. bet framing is present;
5. Product Increment Contribution is recorded as `direct`, `enabling`, or
   `audit`;
6. enabling sprints name the visible increment they unblock and why a direct
   slice is not viable;
7. two consecutive enabling or prerequisite sprints trigger a route review
   with options, pros/cons, and an operator decision to ship a vertical proof,
   cut/defer scope, reroute, or buy more enabling work;
8. validation and live gates are concrete, including which gates are required
   objective proof versus optional, not-triggered, or out-of-scope checks;
9. user or operator evidence status is `used`, `not triggered`, or `deferred`;
10. Project Evolution Gate inventory exists when triggered;
11. operational surface preflight exists when the sprint introduces or changes
    a repo-owned operational surface, including owner, lifecycle, visibility,
    safety policy, validation path, and inventory or topology impact;
12. unclear operational-surface ownership, lifecycle, safety policy,
    validation, or inventory impact that may change scope, architecture, risk,
    or acceptance criteria has been promoted to discovery before execution;
13. options-board validation has passed when the sprint is pulled from an
    option or changes the options route;
14. placeholders that block execution are resolved.

## Sprint Start Readiness

`sprint_start_ready` is `pass` only when:

1. current repo truth has been refreshed;
2. stale candidates have been revalidated;
3. WIP policy allows the sprint;
4. blockers are resolved or explicitly carried;
5. reviewed mode approval was given in a later message after preview when
   reviewed mode is active.

## Sprint Closeout

`sprint_closeout` is `pass` only when:

1. every accepted exit criterion has fresh named passing evidence, or the
   sprint remains active or blocked;
2. required validation and live gates pass after the final relevant change;
3. evidence is saved and routed through `evidence/index.md`, with required
   objective proof separated from optional, not-triggered, blocked,
   out-of-scope, or operator-deferred checks;
4. decision log is current;
5. outcome and learning review is recorded;
6. material closeout result, validation, and route-changing claims are backed
   by `evidence/index.md`; required objective proof cannot be deferred while
   the original objective closes as passed;
7. broader writeback decisions are recorded in the owning artifacts;
8. route-changing learning is promoted into `roadmap.md`;
9. durable lookup learning is compactly promoted into the triggered T3 `index.md`;
10. Forecast Delta is recorded, including planned versus actual, hidden
   prerequisite discovered, remaining forecast impact, and owner updates;
11. sequence expansion beyond appetite records the operator decision after
    scoped cut/defer, reroute, and buy-more tradeoffs were presented;
12. triggered Project Evolution Gate items are converted, removed, or explicitly
   operator-deferred;
13. the mini-retro is recorded, including decision latency and retro evidence
    check;
14. local options are promoted, moved, rejected, or removed when the sprint
    changes initiative closeout posture;
15. next action is explicit.

If required objective proof is missing, stale, failing, or only shows that a
non-objective smoke path ran, the sprint does not pass. Continue iterating
while the accepted objective remains reachable; otherwise mark the sprint
blocked or ask the operator to change scope, reroute, or buy more work.

## Final Audit

A final audit checks:

1. roadmap scope was executed, parked, or explicitly deferred;
2. no material work was silently skipped;
3. bought, parked, cut, and deferred scope is explicit;
4. evidence and closeouts support claimed outcomes;
5. broad docs and route maps are current;
6. roadmaps and options boards do not hide required unfinished work;
7. initiative `index.md` supports lookup of meaningful discoveries, closeouts,
   evidence, and supersession notes;
8. retained note is ready;
9. terminal-audit-mode options validation has no required findings;
10. archive readiness is surfaced for human review.

## Archive Readiness

Archive only after explicit request and when:

1. final audit passed;
2. retained note exists;
3. initiative roadmap, index, and status reflect completion;
4. initiative-local options are resolved;
5. `status.md` no longer points at the initiative as active.
