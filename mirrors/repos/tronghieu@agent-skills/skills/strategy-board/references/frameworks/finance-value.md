# Finance & Value — Graham's Working File

Tools for putting honest numbers on options. Rules that outrank everything:
every figure is `[S#]`-sourced or `(assumption)`-labelled; every estimate
shows a range, not a point; and the downside case is built with the same care
as the base case.

## Performance diagnosis (DuPont-style)

**When:** the engagement starts from a symptom — "margins have slid three
years", "ROE is below peers" — and the question is *where the leak is*
before anyone proposes fixes.

**How:** decompose the headline metric into its levers and walk down the
branch that moved. ROE → net margin × asset turnover × leverage; operating
margin → price, mix, volume, unit cost lines; a profitability tree bottoms
out where an owner and an action exist. Compare each node to its own 3-year
trend and to peers `[S#]` — a number without a comparator is a decoration.
Stop at the 2–3 nodes that explain most of the delta.

**Output format:** the decomposition tree (indented list is fine) with each
node showing `value | 3-yr trend | vs peers [S#]`, then: "The decline lives
in [node(s)], because [driver] — which points the engagement at [question]".

## Opportunity sizing

**When:** any "how big is this" question — market entry, new product, new
segment.

**How:** run top-down (market total [S#] × addressable share × realistic
capture) *and* bottom-up (customers reachable × conversion × price × volume)
independently, then reconcile. If they land more than ~2× apart, an
assumption is wrong — find it before using either number.

**Output format:**

```
## Sizing: [opportunity]
Top-down:  [market S#] × [addressable %] × [capture %] = [range]
Bottom-up: [customers] × [conversion %] × [price] × [freq] = [range]
Reconciled: [range] — divergence explained: [what and why]
Assumptions register: A1 …, A2 … (each: value, basis, owner)
### So what
```

**Tips:** the capture-rate assumption is where sizing lies. Benchmark it
against what comparable entrants actually achieved [S#], not against
ambition. TAM/SAM/SOM lingo is fine but the reconciliation is the substance.

## Unit economics

**When:** before any total P&L is worth building; any recurring-revenue or
volume business.

**How:** per unit (customer, order, seat, ton): revenue, direct costs,
contribution margin; acquisition cost and payback where relevant; break-even
volume against realistic capacity.

**Output format:** the per-unit ledger with sources, contribution margin %,
break-even point, and the sentence that matters: *at what scale does this
turn profitable, and is that scale plausible [ref sizing]?*

## TCO / build-buy-partner comparison

**When:** build vs buy vs partner; any platform, system, or make-or-buy call.

**How:** compare over 3–5 years on total cost of ownership, both directions'
forgotten costs included — build: hiring, opportunity cost of the team,
maintenance (typically ≥2× initial build over 5 years), key-person risk;
buy: implementation and migration, customization, integration, licence
escalation, *exit cost* (the price of being wrong). Add the non-financial
column: control, differentiation (Porter's question), speed, lock-in.

**Output format:**

```
| Dimension | Build | Buy | Partner |
|-----------|-------|-----|---------|
| Year 0 cost | | | |
| Years 1–5 run | | | |
| 5-yr TCO (range) | | | |
| Time to value | | | |
| Exit cost if wrong | | | |
| Control / differentiation | | | |
| Key risks | | | |
```

Each cell sourced or flagged. Verdict as a conditional, not a winner: "Buy
dominates unless [condition]".

Three lenses that separate a board-grade TCO from a spreadsheet:

- **Accounting treatment.** Build costs can often be capitalized (CAPEX,
  amortized) while SaaS licences hit the P&L as OPEX immediately — the same
  cash can look very different in EBITDA. Flag the treatment per option; the
  CFO will ask in the first five minutes.
- **No blank "material" factors.** If cost of delay or opportunity cost of
  talent is material, give it a rough heuristic rather than leaving it
  qualitative — "1% margin improvement on $90M revenue means every month of
  delay costs ~$75K (assumption)". A crude number the board can argue with
  beats an eloquent blank.
- **Stress under growth, not just today's footprint.** TCO curves cross when
  volume changes: per-seat/per-site licences scale linearly while built
  assets scale at marginal cost — and vice versa for the team that maintains
  them. Run the comparison at today's scale *and* the plausible growth case
  (e.g. 8 → 15 warehouses by year 3), and say where the crossover sits.

## Sensitivity analysis

**When:** after any model — always before numbers reach `options.md`.

**How:** vary each major assumption ±30% (or its plausible range if known),
one at a time; rank by swing on the outcome metric. The top 2–3 are the
load-bearing assumptions: they get named in the recommendation, handed to
Taleb, and wired to Wack's signposts.

**Output format:** tornado table — `Assumption | Range tested | Outcome swing
| Rank`, then: "The decision holds unless [assumption] falls below [threshold]".

## Valuing the options (Phase 3 support)

**When:** populating the financial rows of `options.md`.

**How:** same yardsticks for every option — investment (range), NPV or 5-yr
cash profile, payback, downside case (P10, not fantasy-worst), reversibility
cost, and cost of delay for the "wait" option (waiting is never free; price
it). State the discount rate and horizon once, use them everywhere.

**Tips:** when the executive's numbers and public numbers conflict, show
both and say so. And distrust any option whose case rests on "synergies" or
"strategic value" carrying more than a third of the total — that is where
optimism hides from arithmetic.
