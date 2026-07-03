# Avoidable or Not? The Judgment Calls in Churn Classification

The whole value of churn analysis lives in one column: avoidable vs unavoidable. Get it wrong in either direction and the interventions are wrong — over-classify as unavoidable and you absolve the product; over-classify as avoidable and you chase ghosts. These are the calls.

## The honest taxonomy

| Stated reason | Usually means | Classification |
|---|---|---|
| "Went out of business / acquired" | true exogenous loss | Unavoidable — but verify; "restructuring" often means the champion lost the budget fight, which is avoidable-adjacent |
| "Too expensive" | value story failed, not price | Avoidable until proven — price complaints from customers using <30% of features are adoption failures wearing a price costume |
| "Missing feature X" | sometimes true, often exit politeness | Check usage: were they power users blocked by X, or barely active? The latter churned from low value; X is the excuse |
| "Switched to competitor" | you lost a comparison | Avoidable — get the real comparison via a churned-customer interview; the reason sales heard is rarely the reason |
| "No longer need it" | job disappeared OR was never real | Split: seasonal/project use (semi-avoidable via pause plans) vs bad-fit acquisition (avoidable at MARKETING, not product) |
| Silent non-renewal | drifted — the deadliest kind | Avoidable, and your health score missed it; audit what "green" meant for this account |

## The three-signal verification

Never classify on the exit survey alone. Triangulate: **stated reason** × **usage trajectory** (when did engagement actually die — usually 60-90 days before the cancel) × **support/commercial history**. When the signals disagree, the usage trajectory is the honest one.

## Bad-fit churn is an acquisition finding

A cohort that churns in month 2 having never activated didn't fail at retention — they were sold something they didn't need. Route it to marketing/sales targeting with the segment named, or the analysis punishes the wrong team.

## The intervention mapping rule

Every avoidable cluster must map to an intervention *at the moment the signal appeared*, not at the cancellation: the day usage dipped, the day the champion left, the day the third P1 hit. Interventions at the exit interview are condolence cards.
