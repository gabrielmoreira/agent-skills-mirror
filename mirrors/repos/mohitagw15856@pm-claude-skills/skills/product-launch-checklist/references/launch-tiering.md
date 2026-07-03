# Launch Tiering: Matching Ceremony to Stakes

Launch checklists fail in both directions — 90-item ceremony for a toggle (so teams route around the process) and three Slack messages for a pricing change (so support finds out from customers). Tiering is the fix: classify first, then the checklist scales itself.

## The tier classifier

| Tier | Criteria (any one qualifies) | Ceremony |
|---|---|---|
| **T1 — Full launch** | New product/major capability · pricing or packaging changes · anything press-worthy · changes with migration impact | Full checklist: positioning, enablement, comms plan, war room, staged rollout |
| **T2 — Feature launch** | Meaningful new capability for a real segment · visible workflow changes | Docs + in-product announce + support briefing + metrics plan; no press motion |
| **T3 — Quiet ship** | Improvements, fixes, small additions | Changelog + flag hygiene + the support heads-up line |

Two classification traps: *stakes creep* (a T3 that touches billing UI is a T1 in disguise — the classifier keys on blast radius, not effort) and *ego inflation* (the team's year-long project is not automatically T1; the CUSTOMER's experience of change sets the tier).

## The invariants (every tier, no exceptions)

However quiet the ship: support knows before customers do (one paragraph: what changed, what users might ask, the answer) · rollback exists and is tested (flag flip or revert, named owner) · success criteria written before launch (even T3: "no support spike, adoption > x by day 30") · the changelog entry ships WITH the change.

## The T1 skeleton that matters most

Working backwards from launch day: T-4wk positioning locked (everything downstream inherits it) · T-3wk enablement material drafted · T-2wk support trained + docs staged + beta feedback triaged · T-1wk go/no-go against WRITTEN criteria (a meeting where "no" is sayable) · T-0 staged rollout with monitoring thresholds pre-agreed · T+1wk the retro nobody skips, comparing outcomes to the success criteria written a month earlier.

## Go/no-go honesty

The go/no-go list is short and binary: blockers only, each with an owner asserting "green" ON RECORD. A 40-item go/no-go where everything is "mostly done" is a launch prayer. Distinguish launch-blocking from fast-follow explicitly — the pressure to reclassify blockers as fast-follows peaks in that exact meeting; write the criteria a week earlier for that reason.
