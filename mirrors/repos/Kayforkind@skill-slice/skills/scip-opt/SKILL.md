---
name: scip-opt
version: 1.1.1
description: "Models and solves mixed-integer programs with PySCIPOpt/SCIP: binaries, capacities, routing, assignment, scheduling, packing, and linearized soft-penalty slacks. Use when the problem has an objective plus hard/soft constraints and integer decisions. Not for unconstrained calculations, good-enough heuristics, pure continuous LP (prefer HiGHS), or a second solver stack when PySCIPOpt is already installed. Never call abs() on solver expressions."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

PySCIPOpt is a Python interface to SCIP, an *exact* mixed-integer programming (MIP) solver. Reach for it when a request has the shape of a *decision problem under constraints* rather than a calculation or a data transformation. The recognizable signs, and why each one points at a MIP:

- **An objective to optimize** — minimize cost, distance, time, or unmet demand; maximize throughput, coverage, or profit. When the user wants "the best" of something *subject to limits*, that "best" is an objective function.
- **Discrete choices** — yes/no decisions, which route arc to take, which option to assign, which items to select, what order to sequence. These become binary variables, and binary variables are exactly what separates MIP from ordinary linear algebra.
- **Quantities with bounds** — loads, inventory, flow, served units, slack. These become integer or continuous variables.
- **Hard rules** every valid answer must obey (conservation, capacity, mutual exclusion). These become constraints.
- **Soft rules** that *may* be broken at a stated cost. These become penalty terms, so the solver can trade a small violation against a larger gain whenever that is genuinely the better outcome.

Why prefer an exact solver over a hand-rolled heuristic: SCIP searches the whole feasible space and returns a *proven* optimality gap, so you know how far the incumbent sits from the true optimum instead of guessing. For combinatorial problems that is the difference between "an" answer and "the right" answer.

**Check availability before reaching for anything else.** Installing a second optimization stack (OR-Tools, Gurobi, PuLP) when PySCIPOpt is already present wastes time, risks license problems, and fragments the model across libraries. Probe first, and fail with a message that tells the next person how to recover:

```python
try:
    from pyscipopt import Model, Variable, quicksum
except ImportError as exc:  # environment guard, not normal control flow
    raise RuntimeError(
        "PySCIPOpt is required for this optimization approach. "
        "Install it with `pip install pyscipopt==8.*`, which bundles "
        "matching SCIP 9.0+ wheels on supported platforms."
    ) from exc
```

The `raise ... from exc` chaining is deliberate: it preserves the original `ImportError` traceback, so whoever hits this can tell whether the package is missing entirely or merely failing to load its compiled SCIP backend — two problems with different fixes.

> **Runtime note (2026):** PySCIPOpt 8.x links against SCIP 9.0+. The PyPI wheels ship a matching SCIP build, so `pip install pyscipopt==8.*` is self-contained on supported platforms. Only fall back to a source build against your own SCIP when you need a custom SCIP configuration or run on an unsupported platform.

### When NOT to use

Skip PySCIPOpt — or reach for a different tool — when the problem does not actually need an exact MIP solver. The reasoning matters more than the rule, because each case has a clear "unless":

- **No real objective or constraints.** If there is nothing to optimize and nothing that can be violated, you are doing a calculation, not an optimization; plain Python (or NumPy/pandas) is simpler and faster.
- **A good-enough answer is acceptable and latency dominates.** A purpose-built heuristic can return a reasonable solution in milliseconds where a MIP solve takes seconds to minutes. Use SCIP when you need the *proven* best answer or a bounded gap; use a heuristic when "good and fast" wins.
- **Pure continuous linear programs with no integer decisions.** SCIP solves these, but a dedicated LP solver (such as HiGHS) is usually faster. The MIP branch-and-bound machinery only earns its cost once discreteness enters.
- **Problem size beyond practical limits.** Models with millions of variables can exhaust memory or never close the gap. Before scaling up, reformulate (tighter constraints, decomposition, column generation) rather than throwing a bigger model at the solver.

## Prerequisites

- **Python 3.9+** with `pip` available.
- **PySCIPOpt 8.x** (bundles SCIP 9.0+ wheels). Install on Windows PowerShell:

  ```powershell
  pip install pyscipopt==8.*
  ```

  On supported platforms the wheel is self-contained. Only build from source against your own SCIP if you need a custom SCIP configuration or run on an unsupported platform.

- **Verify the installation** before modeling:

  ```powershell
  python -c "from pyscipopt import Model; m=Model('test'); print('PySCIPOpt OK', m.getVersion())"
  ```

## Procedure

### Modeling workflow

The order of these steps is deliberate: each depends on decisions made in the previous one, so getting the variables right up front prevents expensive reformulation later.

1. **Identify the sets and indices first.** Everything else is indexed by these (vehicles `K`, stations `N`, jobs `J`, periods `T`, arcs `A`). Build explicit ID-to-index mappings when input IDs are sparse or non-contiguous (database keys, for example) — relying on list position breaks silently the moment the input is filtered or reordered.

2. **Define decision variables to match the *kind* of decision.** Binary (`"B"`) for choices, visits, and assignments; integer (`"I"`) for indivisible counts; continuous (`"C"`, the default) for divisible quantities. The variable type is not cosmetic — declaring a count continuous lets the solver return 3.5 trucks, while declaring a naturally-continuous flow integer needlessly enlarges the search tree.

3. **Add the hard constraints** — conservation, capacity, bounds, linking, continuity, mutual exclusion. These define feasibility, so model them exactly rather than approximately: every reported answer must satisfy all of them.

4. **Model soft constraints with explicit slack variables, not `abs()`.** A deviation you are willing to pay for needs its own non-negative variable plus two linear inequalities (shown below). Calling `abs()` on a *solver expression* is wrong twice over: PySCIPOpt expressions do not implement Python's `abs`, and even an absolute value is nonlinear, which would push the model out of the MILP class SCIP handles most efficiently. Linearizing keeps the model linear and exact.

5. **Set one objective that combines the named components.** Keep cost and penalty as separately computable expressions even though they are summed into a single objective — you will recompute them individually during validation, and naming them documents the trade-off you are making.

6. **Solve with explicit time and gap limits.** Without `limits/time` a hard instance can run unbounded; without `limits/gap` the solver may keep working long past a solution that is already good enough. For very large models where proving optimality is hopeless, `limits/solutions` caps how many improving incumbents to find before stopping. Always confirm at least one incumbent exists (`getNSols() > 0`) before reading values — a time-limited solve can return with no feasible solution at all.

7. **Reconstruct and independently validate.** Recompute the objective and re-check every hard rule from the *reported* variable values, not from the solver's internal numbers. This catches modeling bugs (a missing constraint), numerical rounding on binary thresholds, and silent unit mismatches — none of which the solver itself will flag.

### Parameter recommendations (SCIP 9)

Reproducibility is the reason behind most of these. SCIP makes randomized choices (tie-breaking, permutations, parallel scheduling) that change the search path and therefore *which* equally-optimal solution comes back. Fixing the seeds and serializing the search makes runs byte-for-byte comparable — what you want in tests and audits — at some cost in wall-clock speed. Relax them in production if you only care about *an* optimal solution rather than a *repeatable* one.

Use this direct form when you control the SCIP build and know every parameter name exists:

```python
from pyscipopt import Model


def apply_scip9_defaults(model: Model) -> None:
    """Pin SCIP's randomized decisions so repeated solves take identical paths."""
    # All three seeds feed different randomized routines; pin them together.
    model.setParam("randomization/randomseedshift", 0)
    model.setParam("randomization/permutationseed", 0)
    model.setParam("randomization/lpseed", 0)

    # Parallelism reorders work nondeterministically; one thread => deterministic.
    model.setParam("parallel/maxnthreads", 1)

    # verblevel 4 is SCIP's normal log; drop to 0 for silence, keep 4 to debug.
    model.setParam("display/verblevel", 4)
```

When the parameter set might vary across builds, use the cross-version helper instead (see Examples below).

## Examples

### Minimal end-to-end template

A complete, typed allocation model: choose which items to activate, pick an integer amount for each within capacity, hit per-item targets where possible, and pay a penalty for any deviation. Every input is validated *before* a single variable is created, because the cheapest place to reject a malformed instance is before the solver ever runs.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from pyscipopt import Model, Variable, quicksum


@dataclass(frozen=True)
class AllocationResult:
    """Validated, solver-independent view of an allocation solution."""

    status: str
    objective: float
    fixed_cost: float
    penalty_cost: float
    selected_items: tuple[int, ...]
    amounts: dict[int, int]


def solve_allocation(
    item_ids: Sequence[int],
    capacity: Mapping[int, int],
    target: Mapping[int, float],
    fixed_cost: Mapping[int, float],
    penalty_weight: float,
    *,
    time_limit_seconds: float = 300.0,
    relative_gap: float = 0.01,
) -> AllocationResult:
    """Select items and amounts to minimize fixed cost plus deviation penalty.

    Args:
        item_ids: distinct item identifiers; their order is preserved in outputs.
        capacity: per-item integer upper bound on the chosen amount.
        target: per-item desired amount; missing it costs `penalty_weight`/unit.
        fixed_cost: cost charged once if an item is activated at all.
        penalty_weight: cost per unit of absolute deviation from target (>= 0).
        time_limit_seconds: wall-clock cap handed to SCIP (> 0).
        relative_gap: stop once the proven optimality gap is within this (>= 0).

    Returns:
        An AllocationResult whose objective has been independently reconstructed
        and cross-checked against the solver's reported value.

    Raises:
        ValueError: on empty/duplicate input, negative weights/limits, or bad
            capacities and targets.
        KeyError: when an item is missing an entry in any required mapping.
        RuntimeError: when SCIP terminates without a feasible incumbent.
        AssertionError: when the reconstructed objective disagrees with SCIP's.
    """
    # --- strict validation: fail fast and specifically ---------------------
    if len(item_ids) == 0:
        raise ValueError("item_ids must contain at least one item")
    if len(set(item_ids)) != len(item_ids):
        raise ValueError("item_ids must be unique")
    if penalty_weight < 0:
        raise ValueError(f"penalty_weight must be >= 0, got {penalty_weight}")
    if time_limit_seconds <= 0:
        raise ValueError(
            f"time_limit_seconds must be > 0, got {time_limit_seconds}"
        )
    if relative_gap < 0:
        raise ValueError(f"relative_gap must be >= 0, got {relative_gap}")

    for i in item_ids:
        for label, mapping in (
            ("capacity", capacity),
            ("target", target),
            ("fixed_cost", fixed_cost),
        ):
            if i not in mapping:
                raise KeyError(f"item {i!r} missing from {label}")
        if capacity[i] < 0:
            raise ValueError(f"capacity[{i!r}] must be >= 0, got {capacity[i]}")
        if not 0 <= target[i] <= capacity[i]:
            raise ValueError(
                f"target[{i!r}]={target[i]} must lie in "
                f"[0, capacity={capacity[i]}]"
            )

    # --- build the model ---------------------------------------------------
    model = Model("allocation")
    model.setParam("display/verblevel", 0)  # quiet but recoverable; see notes

    activate: dict[int, Variable] = {
        i: model.addVar(vtype="B", name=f"activate_{i}") for i in item_ids
    }
    amount: dict[int, Variable] = {
        i: model.addVar(vtype="I", lb=0, ub=int(capacity[i]), name=f"amount_{i}")
        for i in item_ids
    }
    deviation: dict[int, Variable] = {
        i: model.addVar(lb=0.0, name=f"deviation_{i}") for i in item_ids
    }

    for i in item_ids:
        # An amount may be positive only when the item is activated.
        model.addCons(amount[i] <= capacity[i] * activate[i], name=f"link_{i}")
        # deviation[i] >= |amount[i] - target[i]|, linearized as two inequalities.
        model.addCons(amount[i] - target[i] <= deviation[i], name=f"dev_pos_{i}")
        model.addCons(target[i] - amount[i] <= deviation[i], name=f"dev_neg_{i}")

    fixed_cost_expr = quicksum(fixed_cost[i] * activate[i] for i in item_ids)
    penalty_expr = penalty_weight * quicksum(deviation[i] for i in item_ids)
    model.setObjective(fixed_cost_expr + penalty_expr, "minimize")

    model.setParam("limits/time", time_limit_seconds)
    model.setParam("limits/gap", relative_gap)
    model.optimize()

    status = model.getStatus()
    if model.getNSols() == 0:
        raise RuntimeError(
            f"SCIP found no feasible solution (status={status!r}); "
            "relax constraints or raise the time limit"
        )

    # --- extract, then independently reconstruct to validate ---------------
    selected = tuple(i for i in item_ids if model.getVal(activate[i]) > 0.5)
    amounts = {i: round(model.getVal(amount[i])) for i in item_ids}

    # abs() is correct here: amounts and target are concrete numbers now, not
    # solver expressions, so the linearization of step 4 no longer applies.
    rebuilt_fixed = sum(fixed_cost[i] for i in selected)
    rebuilt_penalty = penalty_weight * sum(
        abs(amounts[i] - target[i]) for i in item_ids
    )
    rebuilt_objective = rebuilt_fixed + rebuilt_penalty

    solver_objective = float(model.getObjVal())
    if abs(rebuilt_objective - solver_objective) > 1e-6:
        raise AssertionError(
            f"reconstructed objective {rebuilt_objective} disagrees with "
            f"solver {solver_objective}; the model and the readout are "
            "inconsistent"
        )

    return AllocationResult(
        status=status,
        objective=solver_objective,
        fixed_cost=rebuilt_fixed,
        penalty_cost=rebuilt_penalty,
        selected_items=selected,
        amounts=amounts,
    )
```

### Common patterns

Each pattern below is a self-contained, typed helper. They share these module-level imports, shown once so the snippets stay focused on the modeling:

```python
from __future__ import annotations

import logging
from typing import Mapping, Sequence

from pyscipopt import Model, Variable, quicksum

logger = logging.getLogger(__name__)
```

#### Binary activation (link a quantity to an on/off decision)

```python
def add_binary_activation(
    model: Model,
    item_ids: Sequence[int],
    upper: Mapping[int, float],
) -> tuple[dict[int, Variable], dict[int, Variable]]:
    """Allow quantity q[i] to be positive only when switch use[i] is on.

    The bound `upper[i]` doubles as the big-M in the linking constraint. Using
    each item's *own* tightest bound (instead of a single large global M) keeps
    the LP relaxation tight, and a tight relaxation is what lets SCIP prune the
    branch-and-bound tree quickly.
    """
    missing = [i for i in item_ids if i not in upper]
    if missing:
        raise KeyError(f"upper bound missing for items: {missing}")
    negative = [i for i in item_ids if upper[i] < 0]
    if negative:
        raise ValueError(f"upper bounds must be >= 0; offenders: {negative}")

    use: dict[int, Variable] = {
        i: model.addVar(vtype="B", name=f"use_{i}") for i in item_ids
    }
    q: dict[int, Variable] = {
        i: model.addVar(lb=0.0, ub=float(upper[i]), name=f"q_{i}")
        for i in item_ids
    }
    for i in item_ids:
        model.addCons(q[i] <= upper[i] * use[i], name=f"activate_{i}")
    return use, q
```

#### Assignment (each item to exactly one option, respecting capacity)

```python
def add_assignment(
    model: Model,
    items: Sequence[int],
    options: Sequence[int],
    weight: Mapping[int, float],
    capacity: Mapping[int, float],
) -> dict[tuple[int, int], Variable]:
    """Assign every item to exactly one option without overloading any option.

    The two constraint families encode the two halves of the requirement: the
    `== 1` per item forces a *complete* assignment, while the per-option capacity
    sum prevents any single option from being overloaded. Modeling both
    explicitly (rather than as a soft preference) is what makes the result
    provably feasible against the stated limits.
    """
    if not items:
        raise ValueError("items must be non-empty")
    if not options:
        raise ValueError("options must be non-empty")
    missing_weight = [i for i in items if i not in weight]
    if missing_weight:
        raise KeyError(f"weight missing for items: {missing_weight}")
    missing_capacity = [j for j in options if j not in capacity]
    if missing_capacity:
        raise KeyError(f"capacity missing for options: {missing_capacity}")
    if any(weight[i] < 0 for i in items):
        raise ValueError("weights must be non-negative")
    if any(capacity[j] < 0 for j in options):
        raise ValueError("capacities must be non-negative")

    assign: dict[tuple[int, int], Variable] = {
        (i, j): model.addVar(vtype="B", name=f"assign_{i}_{j}")
        for i in items
        for j in options
    }
    for i in items:
        model.addCons(
            quicksum(assign[i, j] for j in options) == 1,
            name=f"one_option_{i}",
        )
    for j in options:
        model.addCons(
            quicksum(weight[i] * assign[i, j] for i in items) <= capacity[j],
            name=f"capacity_{j}",
        )
    return assign
```

#### Absolute deviation penalty

```python
def add_absolute_deviation(
    model: Model,
    index: Sequence[int],
    actual: Mapping[int, Variable],
    target: Mapping[int, float],
) -> dict[int, Variable]:
    """Create dev[i] >= |actual[i] - target[i]| via two linear inequalities.

    `actual[i]` are *decision variables*, so their distance from target cannot be
    computed with Python's abs(); it must be bounded by a fresh non-negative
    variable that the objective then minimizes. Because the objective drives
    dev[i] down, at the optimum it settles to exactly the absolute deviation —
    the linear stand-in for a nonlinear absolute value. The caller adds the
    penalty term, for example:

        penalty = penalty_weight * quicksum(dev[i] for i in index)
    """
    missing = [i for i in index if i not in actual or i not in target]
    if missing:
        raise KeyError(f"missing entries for indices: {missing}")

    dev: dict[int, Variable] = {
        i: model.addVar(lb=0.0, name=f"dev_{i}") for i in index
    }
    for i in index:
        model.addCons(actual[i] - target[i] <= dev[i], name=f"dev_pos_{i}")
        model.addCons(target[i] - actual[i] <= dev[i], name=f"dev_neg_{i}")
    return dev
```

#### Multi-vehicle routing structure (flow conservation)

```python
def add_routing_structure(
    model: Model,
    vehicles: Sequence[int],
    locations: Sequence[str],
    start: str,
    end: str,
) -> tuple[dict[tuple[int, str, str], Variable], list[tuple[str, str]]]:
    """Create arc variables and flow-conservation constraints for multi-vehicle routing.

    Each vehicle leaves the start depot exactly once, enters the end depot exactly
    once, and has flow conservation at every intermediate location. The `<= 1`
    visit constraint allows locations to be skipped (unvisited), which is correct
    when not every location must be served. The flow-conservation equalities
    force the chosen arcs to form genuine routes instead of a scatter of
    disconnected edges.
    """
    if not vehicles:
        raise ValueError("vehicles must be non-empty")
    if not locations:
        raise ValueError("locations must be non-empty")
    if start == end:
        raise ValueError("start and end depot labels must differ")
    if start in locations or end in locations:
        raise ValueError("depot labels must not collide with customer locations")

    nodes_from = [start, *locations]
    nodes_to = [*locations, end]
    arcs: list[tuple[str, str]] = [
        (i, j)
        for i in nodes_from
        for j in nodes_to
        if i != j and not (i == start and j == end)
    ]
    arc_set = set(arcs)

    x: dict[tuple[int, str, str], Variable] = {
        (k, i, j): model.addVar(vtype="B", name=f"x_{k}_{i}_{j}")
        for k in vehicles
        for (i, j) in arcs
    }

    for k in vehicles:
        model.addCons(
            quicksum(x[k, start, j] for j in locations) == 1,
            name=f"leave_depot_{k}",
        )
        model.addCons(
            quicksum(x[k, i, end] for i in locations) == 1,
            name=f"enter_depot_{k}",
        )
        for i in locations:
            incoming = quicksum(
                x[k, j, i] for j in nodes_from if (j, i) in arc_set
            )
            outgoing = quicksum(
                x[k, i, j] for j in nodes_to if (i, j) in arc_set
            )
            model.addCons(incoming == outgoing, name=f"balance_{k}_{i}")
            model.addCons(outgoing <= 1, name=f"visit_once_{k}_{i}")
    return x, arcs
```

#### MTZ subtour elimination (SCIP 9 syntax)

```python
def add_mtz_subtour_elimination(
    model: Model,
    x: Mapping[tuple[int, str, str], Variable],
    vehicles: Sequence[int],
    locations: Sequence[str],
) -> dict[tuple[int, str], Variable]:
    """Forbid disconnected subtours with Miller-Tucker-Zemlin ordering vars.

    Flow conservation alone still permits a valid route plus a separate closed
    loop that never touches the depot. MTZ assigns each visited location a
    position in [1, n] and forces that position to strictly increase along any
    used arc; strictly increasing positions are impossible around a cycle, so
    subtours are ruled out. MTZ is compact (O(n^2) constraints) but weaker than
    exponential cut families — well suited to small and medium instances.
    """
    if not vehicles:
        raise ValueError("vehicles must be non-empty")
    if not locations:
        raise ValueError("locations must be non-empty")

    n = len(locations)
    order: dict[tuple[int, str], Variable] = {
        (k, i): model.addVar(lb=1.0, ub=float(max(1, n)), name=f"order_{k}_{i}")
        for k in vehicles
        for i in locations
    }
    for k in vehicles:
        for i in locations:
            for j in locations:
                if i == j:
                    continue
                key = (k, i, j)
                if key not in x:
                    continue  # arc not modeled; nothing to constrain
                model.addCons(
                    order[k, i] - order[k, j] + n * x[key] <= n - 1,
                    name=f"mtz_{k}_{i}_{j}",
                )
    return order
```

#### Reproducibility across SCIP builds (updated for SCIP 9)

```python
def set_if_available(
    model: Model,
    name: str,
    value: bool | int | float | str,
) -> bool:
    """Set a SCIP parameter, tolerating names that differ across SCIP versions.

    Parameter names drift between SCIP releases — a name valid in SCIP 8 may be
    renamed in SCIP 9. We try to set it and, if SCIP rejects the name, log a
    warning rather than failing the whole solve. We *do* log it, though: a
    silently-skipped seed quietly destroys the reproducibility you believed you
    had configured. Catching KeyError specifically (the error PySCIPOpt raises
    for an unknown parameter) avoids masking unrelated bugs. Returns True iff the
    parameter was applied.
    """
    try:
        model.setParam(name, value)
    except KeyError:
        logger.warning(
            "SCIP parameter %r not available in this build; skipped", name
        )
        return False
    return True


def configure_reproducibility(model: Model) -> None:
    """Best-effort deterministic configuration that survives build differences."""
    # Seed every randomized source so the search path is fixed.
    for seed_param in (
        "randomization/randomseedshift",
        "randomization/permutationseed",
        "randomization/lpseed",
    ):
        set_if_available(model, seed_param, 0)

    # Disable nondeterministic permutations of variables and constraints.
    for permute_param in (
        "randomization/permutevars",
        "randomization/permuteconss",
    ):
        set_if_available(model, permute_param, False)

    # Serialize the solve so parallel scheduling cannot reorder work.
    set_if_available(model, "parallel/maxnthreads", 1)
```

#### Extraction and validation

```python
def is_selected(
    model: Model,
    var: Variable,
    *,
    threshold: float = 0.5,
) -> bool:
    """Interpret a binary variable's possibly-fractional solver value as on/off.

    SCIP returns floating-point values, so a 'true' binary can come back as
    0.9999999998 and a 'false' one as 1e-12. Thresholding at 0.5 turns the
    numeric value into the boolean decision the model intends; never compare a
    binary variable to exactly 1.0.
    """
    return model.getVal(var) > threshold


def validate_route_cost(
    model: Model,
    x: Mapping[tuple[int, str, str], Variable],
    vehicle: int,
    arcs: Sequence[tuple[str, str]],
    distance: Mapping[tuple[str, str], float],
    expected_cost: float,
    *,
    tolerance: float = 1e-6,
) -> float:
    """Recompute one vehicle's route cost from the readout and check it.

    Recomputing from the *reported* arc decisions, instead of trusting the
    solver's objective, is what catches an omitted constraint or a unit slip: if
    this independent reconstruction disagrees with `expected_cost` beyond
    `tolerance`, the model and its interpretation are out of sync and the answer
    is not trustworthy. Returns the reconstructed cost on success.
    """
    missing = [(i, j) for (i, j) in arcs if (i, j) not in distance]
    if missing:
        raise KeyError(f"distance missing for arcs: {missing}")

    selected_arcs = [
        (i, j)
        for (i, j) in arcs
        if (vehicle, i, j) in x and is_selected(model, x[vehicle, i, j])
    ]
    reconstructed = sum(distance[i, j] for (i, j) in selected_arcs)

    if abs(reconstructed - expected_cost) > tolerance:
        raise AssertionError(
            f"route cost mismatch for vehicle {vehicle}: reconstructed "
            f"{reconstructed} vs expected {expected_cost}"
        )
    return reconstructed
```

## Pitfalls

Two habits to avoid, again with the reasoning so you can judge exceptions:

- **Do not silence the solver with `model.hideOutput()` in code you intend to operate or debug.** It suppresses *all* output, including the warnings that explain why a solve stalled or returned nothing. Prefer fine-grained control via `model.setParam("display/verblevel", 0)`, which you can raise back to `4` when something goes wrong without touching the rest of the code.

- **Never interpolate untrusted input into variable or constraint names.** Names flow into SCIP's C layer and into `.lp`/`.mps` exports; unsanitized names can collide, break round-tripping, or smuggle delimiters into exported files. Generate names programmatically from indices (as every example above does) rather than from user-supplied strings.

Additional pitfalls from lived experience:

- **Do not call `abs()` on solver expressions.** PySCIPOpt expressions do not implement Python's `abs`, and absolute value is nonlinear. Use explicit slack variables with two linear inequalities instead (see the `add_absolute_deviation` pattern).

- **Never compare a binary variable's solver value to exactly `1.0`.** SCIP returns floating-point values; a "true" binary can come back as `0.9999999998`. Always threshold at `0.5`.

- **Do not read variable values before confirming `model.getNSols() > 0`.** A time-limited solve can return with no feasible solution at all. Reading values when no solution exists returns garbage or raises.

- **Do not use a single large global big-M.** Using each item's own tightest upper bound as the linking big-M keeps the LP relaxation tight, which lets SCIP prune the branch-and-bound tree quickly. A loose global M inflates the search space.

- **Do not skip independent reconstruction.** The solver's reported objective can agree with its internal model while the model itself is wrong (missing constraint, unit mismatch). Recompute from the *reported* variable values to catch these.

- **Do not leave randomized SCIP parameters unpinned in test or audit code.** SCIP makes randomized choices (tie-breaking, permutations, parallel scheduling) that change which equally-optimal solution comes back. Pin all three seeds and serialize to one thread for reproducibility.

## Verification

Each check below exists to catch a specific failure mode, not as box-ticking:

- [ ] **Run the test suite** — confirms the model still builds and solves on known inputs after a change.
- [ ] **Validate against benchmark problems with known optima** — confirms the *formulation* is correct, not merely that it runs; a model can solve cleanly and still optimize the wrong thing.
- [ ] **Exercise the solution reconstruction path** — confirm the independent recomputation actually runs and would catch a mismatch, by testing it against a deliberately corrupted readout.
- [ ] **Verify reproducibility settings** — solve the same instance twice and assert identical objective and variable values; any drift means a randomized source was left unpinned.
- [ ] **Test empty and infeasible instances** — confirm the code raises a clear, specific error (not an `IndexError` or a silently wrong answer) when there is nothing to optimize or no feasible solution exists.

### Quick verification commands (Windows PowerShell)

```powershell
# Confirm PySCIPOpt imports and SCIP version
python -c "from pyscipopt import Model; m=Model('v'); print('SCIP', m.getVersion())"

# Run a minimal solve to confirm the solver works end-to-end
python -c "from pyscipopt import Model; m=Model('t'); x=m.addVar('x', lb=0, ub=10); m.addCons(x >= 3); m.setObjective(x, 'minimize'); m.optimize(); print('status:', m.getStatus(), 'obj:', m.getObjVal(), 'x:', m.getVal(x))"
```

Expected output for the second command: `status: optimal obj: 3.0 x: 3.0`

## Related skills

- Linear programming
- Mixed-integer programming
- Constraint programming
- Heuristic optimization
- Mathematical modeling
