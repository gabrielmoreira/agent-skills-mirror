# Attribution Modeling

Purpose: assign conversion credit across the touchpoints a user encountered before
converting. This is **observational credit assignment** over tracked events — it is
distinct from causal incrementality (`experiment`) and from aggregate spend
allocation (MMM). Use this reference to pick an attribution model, understand its
bias, and route correctly to the causal toolkit when the question is actually causal.

## Contents
- Where attribution sits (boundary map)
- Rules-based models
- Algorithmic models (Shapley, Markov, GA4 DDA)
- Selection guide
- Privacy / consent caveats
- Implementation notes

## Where Attribution Sits — Boundary Map

Three different questions, three different tool families. Do not mix them.

| Question | Family | Owner | Method |
|----------|--------|-------|--------|
| "Which touchpoints get credit for *this* conversion?" | Multi-touch attribution (MTA) — observational | `pulse` (this file) | Rules-based / Shapley / Markov / GA4 DDA |
| "How should I split *budget* across channels?" | Marketing-mix modeling (MMM) — aggregate regression | `experiment` (`MMM`) + `pulse` `funnel-cohort-analysis.md` | Robyn / Meridian / PyMC-Marketing |
| "Did this channel *cause* incremental conversions?" | Incrementality — causal | `experiment` | Conversion Lift / GeoLift / Holdout / Synthetic Control |

**Key rule:** MTA answers *credit*, not *causation*. A channel can win attribution credit
while contributing zero incremental conversions (e.g. branded-search capturing
already-decided users). When a stakeholder asks "is this channel worth it?", that is an
incrementality question — hand off to `experiment`, do not answer it with MTA alone.

## Rules-Based Models

Deterministic heuristics. Cheap, transparent, but encode a fixed prior about where value lives.

| Model | Credit rule | Bias | Best for |
|-------|-------------|------|----------|
| `first-touch` | 100% to first interaction | over-credits awareness | demand-gen / top-of-funnel evaluation |
| `last-touch` | 100% to last interaction | over-credits closing / branded search | default in cookieless reality; simple ROAS |
| `last-non-direct` | 100% to last non-direct touch | hides direct-traffic value | GA-style default |
| `linear` | equal split across all touches | ignores intensity / timing | long considered cycles, no strong prior |
| `time-decay` | exponential weight toward recent touches | under-credits early funnel | sales cycles where recency signals intent |
| `position-based` (U-shaped) | 40/20/40 first/middle/last | arbitrary middle weighting | balancing awareness + closing |

Use rules-based only when (a) path data is thin, (b) you need an explainable model for
non-technical stakeholders, or (c) as a baseline to compare an algorithmic model against.

## Algorithmic Models

Data-derived credit from observed path patterns. Require sufficient path volume
(rule of thumb: thousands of converting *and* non-converting paths) and break down on
sparse or heavily consent-truncated data.

### Shapley Value
- Cooperative game theory: each channel is a "player"; credit = its average marginal
  contribution across all channel coalitions.
- Strength: fair, axiomatic (efficiency, symmetry, null-player, additivity); order-independent.
- Weakness: combinatorial cost grows with channel count (`2^n` coalitions — collapse rare
  channels into an "other" bucket); treats presence/absence, ignores sequence and frequency.
- Use when channel *set* matters more than *order*, and channel count is moderate (≤ ~12).

### Markov Chain (removal effect)
- Model paths as a first- (or higher-) order Markov chain between channel states
  (incl. `start`, `conversion`, `null`). A channel's credit = the **removal effect**:
  the drop in conversion probability when that state is removed from the graph.
- Strength: captures *sequence* and *transition* structure; handles loops and repeat touches.
- Weakness: first-order forgets long-range order; needs enough transitions per edge;
  higher-order models explode in state count.
- Use when *order/sequence* carries signal (e.g. nurture sequences, retargeting loops).

### GA4 Data-Driven Attribution (DDA)
- Google Analytics 4's built-in algorithmic model (Shapley-derived, counterfactual-based).
- Became GA4's default after rules-based models (first/linear/time-decay/position) were
  deprecated in GA4 reporting (2023).
- Strength: zero-build, integrated with Google Ads bidding.
- Weakness: black-box, Google-walled, conversion-volume thresholds before it activates,
  cross-platform blind. Treat as a managed Shapley variant, not a separate theory.

## Selection Guide

```
Is the real question "did it CAUSE conversions?"  → experiment (incrementality). STOP.
Is it "how to split budget across channels?"      → MMM (experiment + funnel-cohort-analysis). STOP.
Otherwise (credit assignment over paths):
  Path volume thin / need explainability          → rules-based (last-touch baseline)
  Channel SET matters, order doesn't, ≤~12 chans  → Shapley
  SEQUENCE / loops / nurture order matters         → Markov removal-effect
  On Google stack, want zero-build + Ads bidding   → GA4 DDA
Always: validate the algorithmic model against a rules-based baseline before trusting it.
```

## Privacy / Consent Caveats

MTA degrades under the same cookieless conditions documented in `privacy-consent.md`
and `funnel-cohort-analysis.md`:
- Consent-denied EEA/UK traffic produces **truncated paths** — touchpoints silently drop,
  biasing credit toward observable (often last/direct) touches.
- iOS / cross-device journeys fragment paths; algorithmic models trained on fragments
  inherit the fragmentation bias.
- Always disclose the consent-denial blind spot alongside any attribution report
  (mirror the disclosure rule in `funnel-cohort-analysis.md`).

When path data is too truncated to trust MTA, escalate to aggregate methods (MMM) or
causal methods (incrementality) rather than reporting biased per-path credit.

## Implementation Notes
- Attribution needs clean touchpoint events: every marketing interaction must emit a
  consistent event with `channel`, `campaign`, `timestamp`, and a stitched `user_id` /
  `session_id`. Gaps here corrupt every model downstream (see `event-schema.md`).
- Tooling: GA4 DDA (managed); `ChannelAttribution` (R, Markov); custom Shapley via Python
  (`itertools` coalitions for small `n`); warehouse-native path tables in BigQuery/Snowflake.
- Report attribution as a *range across models*, not a single number — divergence between
  last-touch and Shapley/Markov is itself the insight (it quantifies funnel-stage bias).
