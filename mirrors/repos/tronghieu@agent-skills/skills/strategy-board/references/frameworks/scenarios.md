# Scenarios & Uncertainty — Wack's Working File

Tools for decisions whose payoff depends on how the world turns out. The goal
is never prediction — it is options that survive being wrong.

## Macro scan (PESTEL)

**When:** the environment itself is in play — market entry, regulated
industries, long-horizon commitments — or as the feedstock for the
uncertainty scan below.

**How:** sweep six lanes — **Political** (policy direction, trade,
government stability), **Economic** (growth, rates, FX, labour cost,
consumer spending), **Social** (demographics, urbanization, habits, talent
expectations), **Technological** (enablers, disruptors, adoption curves),
**Environmental** (ESG mandates, carbon cost, climate exposure in the
supply chain), **Legal/regulatory** (licensing, data residency, labour and
antitrust law, pending legislation). In regulated industries and cross-border
entries, Legal is routinely the *deciding* lane — sweep it first, not last.
For each factor that matters: the trend `[S#]`, its direction, and its
concrete implication for *this* decision. Skip factors with no implication —
a scan that lists everything weighs nothing.

**Output format:** table — `Factor | Lane | Trend [S#] | Direction ↑/→/↓ |
Implication for the decision`, then one line: which factors are
predetermined vs uncertain (the uncertain ones feed the scan below).

## Uncertainty scan

**When:** first move in any scenario work; also standalone when a decision
"depends on the market".

**How:** list the external factors that swing this decision. Split them:
**predetermined elements** (already in motion; will hold in every future —
demographics, signed regulation, installed-base physics) vs **critical
uncertainties** (genuinely unknowable and high-impact). Rank uncertainties by
impact × unpredictability; the top two become scenario axes.

**Output format:** two lists with one-line rationale each `[S#]` where
factual, then: "The decision hinges on: [uncertainty 1] and [uncertainty 2]".

## Scenario set

**When:** horizon ≥ 2 years, or an irreversible commitment under uncertainty.

**How:** cross the top two uncertainties into a 2×2 (or hand-build 3
futures if the axes don't cross cleanly). For each scenario: a *name that
sticks* (one is a plot summary, "Slow Thaw" is a scenario), the internal
logic — how the world gets there step by step, told as a short narrative,
because a scenario nobody can retell influences nobody — what wins and loses
in it, and its **signposts**: observable events that say this world is
arriving.

**Output format:**

```
## Scenarios: [decision context] — horizon [year]
Axes: [U1] × [U2]

### [Name] ([quadrant])
Logic: [3–5 sentences, causal chain]
Winners/losers: …
Signposts: [event] by [date]; [metric] crossing [threshold]
```

3–4 scenarios, none of them "the base case plus noise". Do not assign
probabilities — the moment one scenario gets 70%, the others stop being
thought about, which defeats the exercise.

## Wind tunnel

**When:** Phase 3–4 — testing the options (or the chosen direction) for
robustness.

**How:** score each option in each scenario: thrives / survives / impaired /
fatal, with one line of reasoning per cell. Then read the rows: an option
that is fatal anywhere needs a mitigation or a rejection; an option that
merely survives everywhere may beat one that thrives in a single future —
that judgment belongs to the executive, stated plainly.

**Output format:** matrix `Option × Scenario → verdict + one line`, followed
by the robustness read and regret cases.

## What would have to be true (WWHTBT)

**When:** a favoured option exists; before Gate 2 — the fastest way to turn
advocacy into analysis.

**How:** for the option, list every belief that must hold for it to be the
right choice — about the market, customers, competitors, our capabilities,
and the economics. For each: current evidence (`[S#]` / assumption /
unknown), and how to test it cheaply. Then hand the list to Taleb.

**Output format:**

```
| # | Must be true | Evidence today | Confidence | Cheap test |
|---|--------------|----------------|------------|-----------|
### The load-bearing beliefs: [the 2–3 the case really rests on]
```

**Tips:** the WWHTBT list doubles as the signpost source — the load-bearing
beliefs are exactly what the roadmap should keep measuring after the
decision ships (revisit triggers in `templates/roadmap.md`).
