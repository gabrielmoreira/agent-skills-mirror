# Red Team & Risk — Taleb's Working File

Tools for finding how the strategy fails before reality does. The stance is
adversarial by design: this file's user is trying to *break* the plan, not
balance it. Someone else defends it — that separation is the point.

## Pre-mortem

**When:** Phase 4, on every chosen direction — non-negotiable. Also anytime a
plan "feels right" and nobody has argued against it lately (that feeling is
the risk).

**How:** assume total failure three years out, then write the history of the
failure backwards. Run it as a boardroom session (protocol in
`references/boardroom.md`) or solo. Force *specific* causes — "execution was
poor" is not a cause; "the two ERP integrations slipped, the ops team we
budgeted at 6 needed 15, and the anchor customer churned in month 9" is.
Converge on the 2–3 most credible failure paths; for each, the earliest
observable warning and the cheapest present-day mitigation.

Sweep four lanes so the paths don't cluster in one comfort zone: **market**
(demand, competitor response), **execution** (capacity, timeline, key
people), **evidence** (a load-bearing fact that turns out wrong), and — the
lane most pre-mortems miss — **dependency seams**: the third-party
capabilities the option quietly assumes work as advertised (vendor APIs and
their latency/documentation, integrations, a partner's roadmap, a platform's
rate limits, an SI's A-team actually showing up). Hybrid and "buy the core,
build the edge" options live or die at these seams.

**Output format:** run against `checklists/pre-mortem.md`; results into the
session minutes and — critically — the surviving accepted risks into
`recommendation.md`, stated in plain sight.

## Assumption audit

**When:** on Wack's WWHTBT list, Graham's assumptions register, or the fact
base itself.

**How:** for each assumption score two things — **load** (how much of the
case rests on it — from sensitivity analysis where available) and
**fragility** (how badly things break if it is off by half, and how weak the
evidence is). Load × fragility ranks the kill-risks. For the top few: is
there a cheap test, a hedge, or a restructuring that removes the dependency?

**Output format:**

```
| Assumption | Load (1–5) | Fragility (1–5) | Evidence quality | De-risk move |
### Kill risks: [the ones that can sink the strategy alone]
```

## Ruin check

**When:** any irreversible or balance-sheet-scale commitment.

**How:** define the true worst case (not P10 — the structural worst:
the acquisition fails *and* the core business dips *and* the debt reprices).
State the maximum tolerable loss in cash and reputation terms — a number the
executive confirms, not the analyst. If any option's worst case exceeds it,
that option needs restructuring or rejection regardless of expected value.
Expected value is for repeatable bets; a company bets its existence once.

**Output format:** worst-case narrative + the two numbers (worst-case loss
vs maximum tolerable loss) + verdict: survivable / survivable-with-conditions
/ ruin-risk.

## Bias sweep

**When:** before Gate 2 and before the recommendation ships — pointed at the
engagement's *own* artifacts.

**How:** hunt four specific biases with evidence, not vibes:
**survivorship** (are the benchmarks all winners? who tried this and died —
and why don't they appear in the fact base?), **incentive** (which sources
profit from the conclusion — vendor studies, sponsor business cases, the
board's own sunk analysis), **confirmation** (what disconfirming evidence
was never searched for — name the search that wasn't run), **anchoring**
(is the "base case" just the first number anyone said out loud?).

**Output format:** finding-per-bias with the artifact and line it applies
to, plus the repair (a source to add, a search to run, a number to reframe).

## Cheapen the bet

**When:** a favoured option is attractive but the commitment is large and
irreversible.

**How:** restructure for optionality — stage the investment behind kill
criteria; pilot in one market/segment; contract for exit (clawbacks,
licence-before-buy, partner-before-build); separate the reversible 80% from
the irreversible 20% and delay the 20%. Price what the optionality costs
(delay, per-unit premium) against the tail risk it removes — sometimes the
insurance is too expensive, and saying so honestly is part of the job.

**Output format:** restructured option beside the original — same table
columns as `options.md` — with the premium and the removed risk named.

**Tips for the whole file:** dissent is recorded even when overruled
(`decision-log.md`) — not to win later arguments, but because the act of
writing it down forces precision now. Vague doom is noise; a named failure
path with a signpost is a gift.
