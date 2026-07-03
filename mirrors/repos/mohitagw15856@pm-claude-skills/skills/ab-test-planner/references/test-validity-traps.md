# The Validity Traps That Quietly Invalidate A/B Tests

Most invalid tests die before the first user is bucketed — in design decisions that seemed innocent. This is the pre-registration checklist of traps.

## Design-time traps

- **Peeking disguised as diligence.** Checking results daily and stopping "when it's significant" guarantees false positives — significance at SOME interim point is near-certain. Fix: fixed horizon (or a proper sequential method), decided and WRITTEN before launch.
- **Underpowered by optimism.** Detecting a 2% lift on a 5%-baseline metric needs far more traffic than intuition says. Run the power calc backwards from realistic traffic: what's the minimum effect we CAN detect in [weeks]? If that minimum exceeds any plausible effect, the test cannot succeed — redesign for a bigger swing or a more sensitive metric.
- **Randomisation unit mismatch.** Users see both variants (session-level bucketing on a UX change) or teams share an experience (user-level bucketing on a collaborative feature — one workspace, mixed variants, contaminated). Bucket at the level where the experience is coherent, then power-calc at THAT unit (workspaces, not users — your n just shrank).
- **The metric can move for bad reasons.** "Clicks on Buy" can rise while purchases fall (confusion clicks). Primary metric = the value event, decided before launch, with 2-3 guardrails (retention, refunds, latency) that veto shipping regardless of the win.

## Run-time traps

- **Novelty and its evil twin.** Week-1 lifts from newness, week-1 dips from change-aversion — both fade. Run at least two weekly cycles; compare early vs late cohorts before believing either.
- **Sample ratio mismatch.** 50/50 split arriving as 52/48 with big n = bucketing bug; the test is invalid regardless of results. Check SRM FIRST, automatically.
- **Mid-test changes.** Fixing a variant bug, shifting traffic, adding a segment — each restarts the clock. If it changed, the pre-change data is a different experiment.

## Read-time traps

- **Segment fishing.** The overall result was flat, but "it worked for Android users in DACH"! With 20 segments, one is significant by luck. Segments are hypotheses for the NEXT test, never conclusions from this one — unless pre-registered.
- **Significant ≠ worth it.** p<0.05 on +0.3% may be real and still lose to the maintenance cost. Pre-write the ship threshold in effect-size terms, not just significance.
