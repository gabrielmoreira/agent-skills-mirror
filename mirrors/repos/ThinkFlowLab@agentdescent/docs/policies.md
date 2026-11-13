---
description: The decision plane of AgentDescent: eight named policy slots covering selection, sampling, proposal, staleness, conflict, fusion, acceptance and promotion.
---

# Choosing policies — the decision plane

*Module:* [`agentdescent.policies`](https://github.com/ThinkFlowLab/agentdescent/blob/main/agentdescent/policies.py)

Every decision `evolve()` makes is an object you can swap, and they all travel
in one argument. This page is the catalogue; [the guide](policy-guide.md)
is the how — where each slot sits, what it is handed, how they compose, and
how to prove one ran.

```python
from agentdescent import Policies, evolve
from agentdescent.selection import Beam
from agentdescent.sampling import DifficultyWeighted
from agentdescent.advantage import AdvantageAcceptance
from agentdescent.fusion import reflective_merge

evolve(tasks, reward, agent=agent, policies=Policies(
    selection=Beam(4),
    task_sampler=DifficultyWeighted(),
    acceptance=AdvantageAcceptance(inner=my_gate),
    **reflective_merge(completion),
))
```

Two guarantees make the bundle trustworthy. **Nothing is silently ignored**:
each engine declares what it honours, and `Policies.require_supported` raises
on anything else — a custom acceptance rule either runs or refuses loudly.
**`None` means today's behaviour**: `Policies()` and passing nothing are the
same run, so adding a policy never changes an existing measurement.

Each field is independent: swap one and the other seven stay at their defaults.
The one deliberate pair is `conflict` + `fusion` for model merging, which is why
`reflective_merge()` returns both. A wrapper that defers to a shipped default —
`AdvantageConflict()`, `AdvantageAcceptance()` — needs nothing from you: the
aggregator hands the engine's verifier and config to any policy exposing the
optional `bind(verifier)` / `configure(config)` hooks
([details](acceptance-policies.md#installing-a-policy-the-two-optional-hooks)).

## Which version of this bundle is a run using?

A commit records its artifact and its diff; it did not record the rules that let
it through, so a three-line change to an acceptance threshold could move a run's
acceptance rate with nothing in the ledger to separate the commits on either
side of it. `policy_digest()` is that missing version — a 64-hex content hash of
the whole procedure:

```python
from agentdescent import Policies, policy_digest
from agentdescent.aggregator import AggregatorConfig

policy_digest(Policies(), config=AggregatorConfig(base_delta=0.05))
# '3f2a…'  -> change base_delta, or swap a policy class, and this changes
```

The engine computes it once per run, from the **resolved** bundle (legacy
keyword arguments folded in), the aggregator config and the verifier that
actually measures, and stamps it on:

- every `MergeContext` (`ctx.policy_digest`) and so every acceptance decision;
- the ledger commit message, as a `policy-digest: <hash>` trailer, alongside a
  `DecisionRecord.policy_digest`;
- `RunManifest.policy_digest` and `EvolutionResult.policy_digest` — recorded
  beside the manifest id, never inside it, so the same inputs judged by a new
  policy are the same run with a different procedure rather than a second id.

Flags, numbers and strings are hashed **by value**, and a replaceable piece is
hashed by class plus its optional `policy_fingerprint()` method — which is how a
rule that keeps its knobs on the instance stays visible: `StableDistanceAcceptance(strength=0.1)`
and `strength=0.9` hash differently, and so do two `AdaptiveTrustRegion`s with a
different `window`. Live state is never hashed: a policy's caches, counters and
spend change while a run spends them, and hashing those would report a policy
change every round. The honest limitation is that a class which keeps an
admission-affecting argument on the instance and does not implement the hook is
identified by its class alone. Nothing here reads the environment, the clock or
the filesystem.

## Which seam is my mechanism?

An algorithm's distinctive mechanism lives in exactly one of three layers:

1. **The artifact's shape** — what a proposal *is* — belongs in the
   [strategy](strategies.md), not a policy. Append-only memory, a keyed
   library, a single replaced slot.
2. **A decision the engine already makes** — which parent, which task, which
   prior, merge or drop — belongs in a `Policies` field. This page's table.
3. **Pure actor text** — prompts and tools — belongs in the definition and
   needs no seam at all.

| Field | The decision | Page | Shipped implementations |
|---|---|---|---|
| `task_sampler` | which task the next rollout spends | [Task sampling](sampling.md) | `RoundRobin`, `DifficultyWeighted` |
| `selection` | which candidate the next batch starts from | [Candidate selection](selection.md) | `SingleHead`, `Beam`, `ParetoFrontier`, `Archive`, `MCTS` (+ examples-level `BinaryTournament`, `SoftMixed`) |
| `proposal` | how rollout evidence becomes proposals | [Proposal policies](proposal-policies.md) | protocol only — write your own |
| `conflict` | what happens to contradicting diffs | [Conflict policies](conflict-policies.md) | `DefaultConflict`, `KeepContradictions`, `AdvantageConflict` |
| `fusion` | whether and how survivors merge | [Fusion policies](fusion-policies.md) | `DefaultFusion`, `ReflectiveFusion` |
| `acceptance` | whether the merged candidate commits | [Acceptance policies](acceptance-policies.md) | `DefaultAcceptance`, `AdvantageAcceptance`, `StableDistanceAcceptance` |
| `promotion` | when dev reaches stable | [Promotion policies](promotion-policies.md) | `DefaultPromotion` |
| `staleness` | what a lagging diff is worth | [Staleness policies](staleness.md) | `Full`, `Guarded`, `Reflective` |

The remaining fields are machinery, not algorithm: `verifier`, `ledger`,
`eval_cache`, `executor`, `evaluator`, `sandbox_*` — see
[the verifier](verifier.md), [the ledger](ledger.md), and
[execution](execution.md).

## When one decision is not enough

Some optimizers change *how the decisions compose* — a population with its own
admission rule, per-instance score rows, an archive driving parent switches.
That is the [`aggregator_factory` exit](aggregator-factory.md): replace (or
subclass) the whole optimizer while every policy above stays available to the
replacement. Rule of thumb: **swap a field first; reach for the factory when
your mechanism needs state the pipeline does not keep.**
