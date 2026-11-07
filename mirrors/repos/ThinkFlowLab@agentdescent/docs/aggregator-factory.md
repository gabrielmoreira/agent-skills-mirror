# The `aggregator_factory` exit — replacing the optimizer

*Contract:* `factory(ledger, verifier, audit, config, staleness_policy) -> aggregator`
with `ingest(card)` and `step() -> list[MergeReport]` (and optionally
`finalize()`), per `AggregatorProtocol`.

Every [policy field](policies.md) swaps **one decision** inside the shipped
seven-stage pipeline. Some optimizers need more: their own candidate pool,
their own admission rule, per-instance score rows, parent switches. For those,
`aggregator_factory=` replaces the optimizer wholesale — the sanctioned exit,
and the one the mechanism-heavy ports have always used.

## The single-head fact that makes this necessary

The engine's `selection` seam is honest about its limit: the ledger holds one
live `dev` branch, so a selection policy that names any starting point other
than the head is refused (`_check_selection` — "multi-head support is a
separate change"). Population search on a single-head ledger therefore lives
in the aggregator: **keep the pool in the optimizer, and make "selection" a
ledger commit that rewrites the head.**

## Implemented

| Aggregator | What it adds | Where |
|---|---|---|
| `Aggregator` | the shipped pipeline: dedupe, staleness, conflict, fusion, statistical acceptance, transactional commit, promotion | `agentdescent.aggregator` |
| `PopulationAggregator(Aggregator)` | an archive of every distinct committed head (held-out mean **and** per-task score vector) + any standard `SelectionPolicy` picking the next parent, committed back to dev; `finalize()` lands the archive's best. Per-task rows let `ParetoFrontier` ride the Policies path without a factory (#806) | `agentdescent.population` — **not** something you install yourself: `Policies(selection=…)` installs it, on both drivers ([selection](selection.md)) |
| `ParetoAggregator` | GEPA's pool with per-instance score rows and Algorithm-2 frontier sampling | `examples/gepa/` |
| `DGMArchiveAggregator` | DGM's keep-all archive with `sigmoid(perf) × 1/(1+children)` parent selection | `examples/dgm/` |
| `MetaSearchAggregator` | ADAS's keep-all archive over agent designs (head rule: shipped `Beam(1)`) | `examples/adas/` |
| `TopKFrontierAggregator` | EvoSkill's bounded top-K frontier (parent rule: `FrontierBest`), on every arm | `examples/evoskill/` |
| `StrictGateAggregator` | SkillOpt's strict gate (acceptance rule: `StrictImprovement`) + rejected-edit buffer + LR schedule | `examples/skillopt/` |
| `PromptBreederPopulation` | PromptBreeder's binary tournament: two units re-scored on a train batch, the loser's slot reused | `examples/promptbreeder/` |

## Composing with merge Policies (#807)

`evolve` forwards merge-side `Policies` (`conflict`, `fusion`, `acceptance`,
`promotion`, `screen`) into the factory when its signature accepts them, and
then applies any remaining slots onto attributes the returned aggregator
exposes (`fusion` also maps to `merge_round` on GEPA/SkillOpt). A factory that
still leaves requested slots unused **raises** unless
`Policies(accept_orphaned_merge_policies=True)` — warn-and-drop was how callers
lost governance gates.

`agentdescent.population.population_factory` remains the template for a custom
`Aggregator` subclass. Shipped mechanism factories (`gepa`, `skillopt`) accept
the same kwargs.

A declared `selection` policy and an `aggregator_factory=` are refused together
rather than resolved: both fill the aggregator seat, and a caller who passed
both has nothing to read that says which one ran.

Prefer a policy field when one decision is enough; reach for the factory when
your mechanism needs state the pipeline does not keep. The contributor map is
the [algorithm decision tree](algorithm-decision-tree.md). Composing factory
with merge Policies without a silent drop is **done**
([#807](https://github.com/ThinkFlowLab/agentdescent/issues/807), see above);
`plan` still warns when merge-side Policies would be unused on an older path
(#805).
