---
name: routing-subtour-elimination
version: 1.1.1
description: "Adds subtour-elimination to TSP, VRP, and pickup/dropoff routing MIPs with binary arc variables (MTZ, flow connectivity, DFJ subset cuts, or lazy iterative cuts). Use when degree constraints still allow disconnected station-only cycles. Not for heuristic routing without a MIP, treating capacity tracking as connectivity, or generic MILP with no arc routing."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Routing Subtour Elimination

In routing MIPs, the per-node degree and continuity constraints — leave the
depot once, return once, and keep in-degree equal to out-degree at every
station — are each individually satisfiable by a solution that is *globally*
disconnected. The solver is free to hand you one depot-to-depot path **plus**
one or more closed loops that sit entirely among the stations and never touch
the depot. Every node in such a loop still has in-degree = out-degree = 1, so
the degree constraints are satisfied, yet no real vehicle could ever drive that
loop because nothing connects it to the depot.

Those phantom loops are **subtours**, and removing them is the entire job of this
skill. The reason you need a dedicated mechanism is that subtour-freeness is a
*global* connectivity property: no purely local (per-node) constraint can rule
out a cycle that is locally consistent at every one of its nodes. So whenever
binary arc variables decide a route, add one of the explicit
subtour-elimination mechanisms below.

## When to Use

Use these methods when binary arc variables define the routes and the standard
degree/continuity constraints (in-degree == out-degree) cannot, by themselves,
prevent disconnected station-only cycles. The need is acute for:

- **Traveling Salesperson Problems (TSP)** — the canonical case; a single tour
  must be one connected cycle, not several.
- **Vehicle Routing Problems with time windows (VRPTW)** — each vehicle's arcs
  must form one depot path, and time windows alone do not forbid a separate loop.
- **Pickup and Delivery Problems (PDP)** with capacity — see the load caveat
  below; capacity tracking is not a connectivity guarantee.
- **Electric Vehicle Routing (EVRP)** with charging detours — charging arcs add
  more ways for a disconnected cycle to look locally valid.
- **Any routing MIP** where route-continuity constraints could otherwise permit
  disconnected cycles.

Trigger keywords: subtour elimination, MTZ, Miller-Tucker-Zemlin, DFJ cuts,
Dantzig-Fulkerson-Johnson, lazy constraint separation, routing MIP, TSP, VRP,
cycle elimination, flow connectivity, disconnected cycle, depot path.

## Prerequisites

- **OR-Tools** with a MILP backend (SCIP is the default; CBC also works).
  Install on Windows (PowerShell):

  ```powershell
  pip install ortools
  ```

- **Python 3.9+** with `from __future__ import annotations` support.
- For property-based verification tests: `hypothesis` (`pip install hypothesis`).
- No live API keys or external services are required — all solving is local.

## Procedure

### Step 0 — Setup and base notation

We model **two** depot copies, `START` and `END`, so that "leave the depot" and
"return to the depot" are distinct events — that separation is what lets a flow
or ordering argument distinguish the legal depot path from an illegal
station-only loop. Stations are plain integer indices, so a node is either a
sentinel string or an integer.

Two deliberate omissions in the arc set matter: we never create a direct
`START -> END` arc (that would let a vehicle "serve" no stations and trivially
satisfy the depart/return constraints), and we never create self-loops
(`i -> i`).

A note on data structures: solver variables are Python objects, not numbers, so
storing them in a NumPy or SciPy numeric array buys nothing and silently coerces
them to floats. A `dict` keyed by the arc tuple is the correct structure — it is
sparse (only arcs that actually exist are materialized), type-stable, and gives
O(1) lookup while building constraints.

```python
from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Set, Tuple, Union

from ortools.linear_solver import pywraplp

# A node is one of the two depot sentinels or an integer station index.
Node = Union[str, int]
Arc = Tuple[Node, Node]

START: str = "depot_start"
END: str = "depot_end"


def build_arcs(n_stations: int) -> List[Arc]:
    """Build the directed arc set, excluding self-loops and the START->END short
    circuit. Validates the station count up front so a bad call fails loudly
    instead of producing an empty, silently-infeasible model."""
    if n_stations <= 0:
        raise ValueError(f"n_stations must be positive, got {n_stations}")

    stations: List[int] = list(range(n_stations))
    from_nodes: List[Node] = [START, *stations]
    to_nodes: List[Node] = [*stations, END]
    return [
        (i, j)
        for i in from_nodes
        for j in to_nodes
        if i != j and not (i == START and j == END)
    ]


def make_solver(backend: str = "SCIP") -> pywraplp.Solver:
    """Create an OR-Tools MILP solver. CreateSolver returns None when the
    requested backend is not compiled into this OR-Tools build — a classic
    silent footgun — so we convert that into an explicit error."""
    solver = pywraplp.Solver.CreateSolver(backend)
    if solver is None:
        raise RuntimeError(
            f"Could not create an OR-Tools solver for backend {backend!r}; "
            "verify the backend is supported by this OR-Tools build."
        )
    return solver


def build_arc_vars(
    solver: pywraplp.Solver,
    vehicles: range,
    arcs: List[Arc],
) -> Dict[Tuple[int, Node, Node], pywraplp.Variable]:
    """One binary variable per (vehicle, arc). Keyed by the tuple so lookups are
    O(1) and only real arcs occupy memory."""
    if len(vehicles) <= 0:
        raise ValueError("vehicles range must be non-empty")
    if not arcs:
        raise ValueError("arcs must be non-empty")

    return {
        (v, i, j): solver.BoolVar(f"x_{v}_{i}_{j}")
        for v in vehicles
        for (i, j) in arcs
    }


def build_arc_index(
    arcs: List[Arc],
) -> Tuple[Dict[Node, List[Node]], Dict[Node, List[Node]]]:
    """Precompute successor and predecessor adjacency maps.

    Building constraints by indexing `x[v, j, i]` for arbitrary (j, i) risks a
    KeyError whenever that arc does not exist. Iterating the precomputed
    adjacency instead guarantees we only ever touch arcs we created.
    """
    successors: Dict[Node, List[Node]] = {}
    predecessors: Dict[Node, List[Node]] = {}
    for (i, j) in arcs:
        successors.setdefault(i, []).append(j)
        predecessors.setdefault(j, []).append(i)
    return successors, predecessors
```

### Step 1 — Add required base route constraints

Subtour elimination assumes each selected station has matching inbound and
outbound route arcs — that flow balance is the foundation every method below
builds on. We force each vehicle to depart and return exactly once, which means
every vehicle must serve at least one station (there is no `START -> END`
short-circuit arc). If vehicles should be optional in your model, relax the two
`== 1` constraints to `<= 1` and add a direct `START -> END` arc so an unused
vehicle has a legal "empty" route.

```python
def add_base_route_constraints(
    solver: pywraplp.Solver,
    x: Dict[Tuple[int, Node, Node], pywraplp.Variable],
    vehicles: range,
    stations: List[int],
    successors: Dict[Node, List[Node]],
    predecessors: Dict[Node, List[Node]],
) -> None:
    if not stations:
        raise ValueError("stations must be non-empty")

    for v in vehicles:
        # Depart the start depot exactly once per vehicle.
        solver.Add(
            sum(x[v, START, j] for j in successors.get(START, [])) == 1,
            f"depart_depot_v{v}",
        )
        # Return to the end depot exactly once per vehicle.
        solver.Add(
            sum(x[v, i, END] for i in predecessors.get(END, [])) == 1,
            f"return_depot_v{v}",
        )

        for i in stations:
            inflow = sum(x[v, p, i] for p in predecessors.get(i, []))
            outflow = sum(x[v, i, s] for s in successors.get(i, []))
            # If a vehicle enters a station it must also leave it.
            solver.Add(inflow == outflow, f"flow_balance_v{v}_n{i}")
            # A vehicle visits each station at most once.
            solver.Add(outflow <= 1, f"visit_once_v{v}_n{i}")
```

### Step 2 — Choose exactly one subtour-elimination method

Pick **one** of the four methods below. Do not combine them — each is sufficient
on its own and stacking multiple methods only bloats the model.

---

#### Method A: MTZ order constraints

The Miller–Tucker–Zemlin (MTZ) idea is to attach an *order* value to every
station and force the order to strictly increase along any selected arc. A cycle
would require the order to increase all the way around and return below itself,
which is impossible — so cycles among stations are ruled out, while the depot
path is untouched because the depot carries no order variable.

We store the order variables in a plain `dict` keyed by `(vehicle, station)`.
Wrapping solver variables in a NumPy array (as older versions of this skill did)
gives no speedup — the heavy work happens inside the solver, not in Python
indexing — and an object-dtype array only adds confusion.

```python
def add_mtz_constraints(
    solver: pywraplp.Solver,
    x: Dict[Tuple[int, Node, Node], pywraplp.Variable],
    vehicles: range,
    stations: List[int],
) -> Dict[Tuple[int, int], pywraplp.Variable]:
    n = len(stations)
    if n == 0:
        raise ValueError("stations must be non-empty for MTZ constraints")

    order: Dict[Tuple[int, int], pywraplp.Variable] = {
        (v, i): solver.NumVar(1.0, float(n), f"order_v{v}_n{i}")
        for v in vehicles
        for i in stations
    }

    for v in vehicles:
        for i in stations:
            for j in stations:
                if i == j:
                    continue
                # If arc i->j is used, order[j] must exceed order[i]; the big-M
                # term (n) deactivates the bound when the arc is unused.
                solver.Add(
                    order[v, i] - order[v, j] + n * x[v, i, j] <= n - 1,
                    f"mtz_v{v}_{i}_{j}",
                )
    return order
```

**Pros:**
- Compact: `O(K * n**2)` constraints and `O(K * n)` extra variables, with no
  exponential blow-up — you add it once, up front.
- Solver-agnostic: needs only linear inequalities and bounded continuous
  variables, so it works in any MILP solver without callbacks.
- Deterministic model size: the whole model is specified before solving, which
  makes debugging and reproducibility straightforward.

**Cons:**
- Weak LP relaxation: the big-M coupling gives loose lower bounds, so
  branch-and-bound can crawl on larger instances (hundreds of nodes).
- Big-M sensitivity: an unnecessarily large M weakens the relaxation further and
  can introduce numerical trouble; keep M as tight as the data allows (here `n`).
- Maps poorly onto QUBO/annealing encodings (see Pitfalls).

---

#### Method B: Single-commodity flow connectivity

Flow formulations give a stronger LP relaxation than MTZ by enforcing
connectivity directly: the depot injects one unit of "commodity" per visited
station, every visited station consumes exactly one unit, and flow may only ride
an arc that the route actually selects. A disconnected station loop is then
impossible because no flow can reach it from the depot, yet it would still need
to consume a unit at each of its nodes.

We keep the flow variables in a `dict` keyed by `(vehicle, tail, head)`. (A
SciPy sparse float matrix cannot hold solver-variable objects — that was a bug in
the earlier version of this skill, not an optimization.) No flow is ever shipped
into `END`; the commodity is consumed at stations, so arcs into `END` carry none.

```python
def add_single_commodity_flow(
    solver: pywraplp.Solver,
    x: Dict[Tuple[int, Node, Node], pywraplp.Variable],
    vehicles: range,
    stations: List[int],
    successors: Dict[Node, List[Node]],
    predecessors: Dict[Node, List[Node]],
) -> Dict[Tuple[int, Node, Node], pywraplp.Variable]:
    n = len(stations)
    if n == 0:
        raise ValueError("stations must be non-empty for flow constraints")

    flow: Dict[Tuple[int, Node, Node], pywraplp.Variable] = {}

    for v in vehicles:
        # One flow variable per arc (except arcs into END), capacity 0..n.
        for tail, heads in successors.items():
            for head in heads:
                if head == END:
                    continue
                f = solver.NumVar(0.0, float(n), f"flow_v{v}_{tail}_{head}")
                flow[v, tail, head] = f
                # Flow only on a selected arc; the cap n links it to x.
                solver.Add(f <= n * x[v, tail, head], f"flow_cap_v{v}_{tail}_{head}")

        # The depot injects exactly one unit per visited station.
        visited = sum(
            x[v, i, s] for i in stations for s in successors.get(i, [])
        )
        solver.Add(
            sum(
                flow[v, START, j]
                for j in successors.get(START, [])
                if (v, START, j) in flow
            )
            == visited,
            f"flow_source_v{v}",
        )

        # Each visited station consumes exactly one unit of flow.
        for i in stations:
            inflow = sum(
                flow[v, p, i] for p in predecessors.get(i, []) if (v, p, i) in flow
            )
            outflow = sum(
                flow[v, i, s] for s in successors.get(i, []) if (v, i, s) in flow
            )
            visit_i = sum(x[v, i, s] for s in successors.get(i, []))
            solver.Add(inflow - outflow == visit_i, f"flow_balance_v{v}_n{i}")

    return flow
```

---

#### Method C: DFJ subset cuts (static enumeration)

Dantzig–Fulkerson–Johnson (DFJ) cuts attack subtours directly: for any station
subset `S`, the arcs that stay inside `S` can use at most `|S| - 1` of them,
because using `|S|` internal arcs would close a cycle on `S`. Enumerating all
subsets is the strongest but least scalable approach — there are `2**n` of them,
which is exactly why we cap the subset size and reserve full enumeration for tiny
instances or for debugging a formulation.

**HARD RULE:** Do not wrap the cut generator in `@lru_cache`. That is actively
harmful — the function has side effects (it adds constraints), and caching a
side-effecting call means the second invocation silently does nothing, leaving
cuts out of your model. Memoization is only ever valid for pure functions.

```python
def add_static_dfj_cuts(
    solver: pywraplp.Solver,
    x: Dict[Tuple[int, Node, Node], pywraplp.Variable],
    vehicles: range,
    stations: List[int],
    max_subset_size: int = 5,
) -> int:
    """Add DFJ subset-elimination cuts for every station subset up to
    `max_subset_size`. Returns the number of cuts added so callers can see the
    (potentially explosive) constraint count."""
    n = len(stations)
    if n < 2:
        raise ValueError("need at least two stations for DFJ cuts")
    if max_subset_size < 2:
        raise ValueError(f"max_subset_size must be >= 2, got {max_subset_size}")

    upper = min(max_subset_size, n - 1)
    cuts_added = 0
    for v in vehicles:
        for size in range(2, upper + 1):
            for subset in combinations(stations, size):
                solver.Add(
                    sum(x[v, i, j] for i in subset for j in subset if i != j)
                    <= len(subset) - 1,
                    f"dfj_v{v}_size{size}_{'_'.join(map(str, subset))}",
                )
                cuts_added += 1
    return cuts_added
```

---

#### Method D: Lazy (iterative) cut separation

The scalable way to use DFJ cuts is to add them only when they are violated:
solve, look at the integer solution, find any station-only cycle, add exactly the
cut that forbids it, and re-solve. Almost all of the `2**n` possible cuts are
never needed, so this converges quickly in practice while keeping the model
small.

**HARD RULE:** `pywraplp` has no in-solve "lazy constraint callback" API, so
"lazy" here means an *iterative cutting-plane re-solve* loop; a true callback
requires a solver/binding that exposes one (Gurobi, CPLEX, or OR-Tools CP-SAT
with its own interface).

**HARD RULE:** Do not parallelize separation with `ThreadPoolExecutor`. The
earlier version of this skill did so and then referenced
`concurrent.futures.as_completed` without importing it — a bug. It also would
not have helped: cycle detection is cheap and CPU-bound (blocked by the GIL),
and the real cost is the *sequential* re-solve. A straight loop is both correct
and faster to reason about.

```python
def find_station_subtours(selected_arcs: List[Arc]) -> List[List[int]]:
    """Find pure-station cycles (subtours) among one vehicle's selected arcs.

    The depot path that runs from START through stations to END is not a
    subtour. With the base degree constraints each station has at most one
    outgoing selected arc, so the station-only subgraph is a functional graph
    and cycles can be traced by following successors.
    """
    successor: Dict[int, int] = {}
    for (i, j) in selected_arcs:
        if isinstance(i, int) and isinstance(j, int):
            if i in successor:
                raise ValueError(
                    f"station {i} has multiple outgoing arcs; the degree "
                    "constraints were violated before subtour separation."
                )
            successor[i] = j

    subtours: List[List[int]] = []
    visited: Set[int] = set()
    for start_node in successor:
        if start_node in visited:
            continue
        path: List[int] = []
        seen_in_path: Set[int] = set()
        node: int = start_node
        while node in successor and node not in seen_in_path:
            seen_in_path.add(node)
            path.append(node)
            node = successor[node]
        if node in seen_in_path:
            # Re-entering the path means we closed a cycle; keep its cyclic part.
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            subtours.append(cycle)
            visited.update(cycle)
        visited.update(seen_in_path)
    return subtours


def solve_with_lazy_subtour_cuts(
    solver: pywraplp.Solver,
    x: Dict[Tuple[int, Node, Node], pywraplp.Variable],
    vehicles: range,
    arcs: List[Arc],
    max_iterations: int = 50,
) -> int:
    """Iteratively solve, detect station-only subtours, add DFJ cuts for each,
    and re-solve until no subtour remains. Returns the final solver status."""
    for iteration in range(max_iterations):
        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            raise RuntimeError(f"no feasible routing found (status={status})")

        cuts_added = 0
        for v in vehicles:
            selected = [
                (i, j) for (i, j) in arcs if x[v, i, j].solution_value() > 0.5
            ]
            subtours = find_station_subtours(selected)
            for subtour in subtours:
                solver.Add(
                    sum(
                        x[v, i, j]
                        for i in subtour
                        for j in subtour
                        if i != j
                    )
                    <= len(subtour) - 1,
                    f"lazy_v{v}_it{iteration}_{'_'.join(map(str, subtour))}",
                )
                cuts_added += 1

        if cuts_added == 0:
            # No subtour remains anywhere; the current solution is valid.
            return status

    raise RuntimeError(
        f"lazy subtour separation did not converge within {max_iterations} "
        "iterations; inspect the model for a cut that fails to bind."
    )
```

### Step 3 — Set the objective and solve

```python
def extract_route(selected_arcs: List[Arc]) -> List[Node]:
    """Reconstruct the ordered route, from START through the visited stations to
    END, from a vehicle's selected arcs.

    Raises ValueError if the arcs do not form exactly one depot-to-depot path
    (subtour present, depot missing, or path disconnected) so that model bugs
    surface loudly rather than as a quietly wrong answer.
    """
    if not selected_arcs:
        raise ValueError("selected_arcs is empty; nothing to extract")

    successor: Dict[Node, Node] = {}
    for (i, j) in selected_arcs:
        if i in successor:
            raise ValueError(f"node {i!r} has more than one outgoing arc")
        successor[i] = j

    if START not in successor:
        raise ValueError("no arc leaves the start depot")

    route: List[Node] = [START]
    node: Node = START
    while node != END:
        if node not in successor:
            raise ValueError(f"route breaks at node {node!r}: no outgoing arc")
        node = successor[node]
        if node in route and node != END:
            raise ValueError(f"cycle detected at node {node!r}; subtour present")
        route.append(node)

    expected = len(successor) + 1  # a simple path has one more node than arcs
    if len(route) != expected:
        raise ValueError(
            f"route covers {len(route)} nodes but {expected} arcs were selected; "
            "a disconnected subtour is likely present."
        )
    return route


def build_and_solve_vrp(
    n_stations: int,
    n_vehicles: int,
    arc_cost: Dict[Arc, float],
    method: str = "mtz",
    backend: str = "SCIP",
) -> Dict[int, List[Node]]:
    if n_stations <= 0:
        raise ValueError(f"n_stations must be positive, got {n_stations}")
    if n_vehicles <= 0:
        raise ValueError(f"n_vehicles must be positive, got {n_vehicles}")

    valid_methods = {"mtz", "flow", "dfj", "lazy"}
    if method not in valid_methods:
        raise ValueError(
            f"unknown method {method!r}; expected one of {sorted(valid_methods)}"
        )

    solver = make_solver(backend)
    stations: List[int] = list(range(n_stations))
    vehicles: range = range(n_vehicles)
    arcs: List[Arc] = build_arcs(n_stations)

    missing = [a for a in arcs if a not in arc_cost]
    if missing:
        raise ValueError(
            f"arc_cost is missing {len(missing)} arc(s), e.g. {missing[:3]}"
        )

    successors, predecessors = build_arc_index(arcs)
    x = build_arc_vars(solver, vehicles, arcs)
    add_base_route_constraints(
        solver, x, vehicles, stations, successors, predecessors
    )

    if method == "mtz":
        add_mtz_constraints(solver, x, vehicles, stations)
    elif method == "flow":
        add_single_commodity_flow(
            solver, x, vehicles, stations, successors, predecessors
        )
    elif method == "dfj":
        add_static_dfj_cuts(solver, x, vehicles, stations)
    # "lazy" adds nothing up front; cuts are separated during the solve loop.

    solver.Minimize(
        sum(arc_cost[i, j] * x[v, i, j] for v in vehicles for (i, j) in arcs)
    )

    if method == "lazy":
        status = solve_with_lazy_subtour_cuts(solver, x, vehicles, arcs)
    else:
        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            raise RuntimeError(f"no feasible routing found (status={status})")

    routes: Dict[int, List[Node]] = {}
    for v in vehicles:
        selected = [(i, j) for (i, j) in arcs if x[v, i, j].solution_value() > 0.5]
        routes[v] = extract_route(selected)  # raises if a subtour slipped through
    return routes
```

## Examples

### Method choice matrix

| Method | Best for | Avoid when | Scaling / notes |
| --- | --- | --- | --- |
| MTZ | Small/medium MIPs, prototyping, any MILP solver | Very large instances where the LP bound matters; QUBO/annealing encodings | `O(K * n**2)` constraints; weak LP relaxation |
| Single-commodity flow | VRPs with optional/selective visits, moderate size | When you need the tightest possible bound | `O(K * n**2)` flow vars; stronger than MTZ, still polynomial |
| Multi-commodity flow | Small exact TSP/VRP needing a tight bound | Larger practical instances (memory heavy) | `O(n**3)` variables; strong bound, poor scaling |
| Static DFJ | Tiny instances, teaching, debugging a formulation | `n` beyond ~15–18 | `O(2**n)` cuts; enumerate only small subsets |
| Lazy DFJ (iterative) | Large routing where most subset cuts never bind | Single-shot environments that cannot re-solve | Adds cuts only as violated; needs a termination bound |

### Minimal usage example

```python
# 5 stations, 2 vehicles, random costs, MTZ subtour elimination
import random

n_stations = 5
n_vehicles = 2
arcs = build_arcs(n_stations)
arc_cost = {}
for (i, j) in arcs:
    arc_cost[(i, j)] = random.uniform(1.0, 10.0)

routes = build_and_solve_vrp(
    n_stations=n_stations,
    n_vehicles=n_vehicles,
    arc_cost=arc_cost,
    method="mtz",
    backend="SCIP",
)

for v, route in routes.items():
    print(f"Vehicle {v}: {route}")
```

## Pitfalls

These are not arbitrary prohibitions — each one points at a specific way the
model can silently go wrong, with the reason so you can judge your own edge
cases.

1. **Don't let physical load be your only anti-subtour mechanism in
   pickup/delivery models.** Vehicle load rises at pickups and falls at
   deliveries, so a closed loop of stations can be perfectly load-feasible: the
   net load change around the loop is zero. Load tracking constrains *capacity*,
   not *connectivity*, so a disconnected cycle can satisfy every load bound while
   never touching the depot. Always pair load variables with a true connectivity
   constraint (MTZ, flow, or DFJ cuts).

2. **Don't enumerate DFJ subset cuts statically once you pass roughly 15–18
   stations.** There are `2**n` station subsets, so the constraint count grows
   exponentially and you spend all your time building — and the solver loading —
   cuts that will never bind. Beyond a couple dozen stations, switch to lazy
   separation, which adds a subset cut only when the current solution actually
   contains that subtour.

3. **Don't read MTZ order variables as service or arrival times.** The
   `order`/`u` variables only encode a *relative visiting sequence* whose sole
   purpose is to make any pure-station cycle infeasible. They carry no time units
   and are not linked to travel or service durations, so treating them as a clock
   is wrong. If you need arrival times, add explicit time variables with
   travel-time constraints.

4. **Be cautious with MTZ in QUBO / annealing-style solvers.** MTZ relies on
   bounded continuous order variables and big-M inequalities. Annealing/Ising
   solvers optimize an unconstrained quadratic binary objective and have no native
   notion of inequalities or continuous bounds, so MTZ has to be folded in via
   large penalty terms that distort the energy landscape — and its already-weak
   LP relaxation gives the solver little to lean on. A position-indexed binary
   encoding (`x[i, p]` = "city `i` is visited at step `p`") usually maps far
   better onto those solvers.

5. **Don't expose unvalidated separation callbacks or model inputs in a hosted
   solver.** If a service lets callers supply model data — or, worse, callback
   code that runs inside the solve loop — unvalidated input is a code-injection
   and denial-of-service vector: an adversary can force unbounded cut generation
   or pin CPU. Validate and bound every external input, cap iterations and
   wall-clock time, and never `eval` caller-provided expressions.

6. **Don't store solver variables in NumPy/SciPy arrays.** Solver variables are
   Python objects, not numbers. NumPy silently coerces them to floats, destroying
   the variable references. Use a plain `dict` keyed by the arc tuple.

7. **Don't wrap side-effecting constraint generators in `@lru_cache`.** Caching a
   function that adds constraints to a solver means the second call silently does
   nothing. Memoization is only valid for pure functions.

8. **Don't parallelize subtour detection with `ThreadPoolExecutor`.** Cycle
   detection is CPU-bound and GIL-locked, so threads buy nothing. The real cost
   is the sequential re-solve. A straight loop is correct and simpler.

9. **Don't forget to validate that `arc_cost` covers every arc.** A missing cost
   is a common, hard-to-spot modeling slip that produces silently wrong
   objectives.

10. **Always bound the lazy loop with `max_iterations`** (and ideally a solver
    time limit) so termination is guaranteed even if a cut fails to bind.

## Verification

The most valuable checks confirm the *property* that defines correctness: every
vehicle's arcs reconstruct into exactly one connected `START -> END` path. The
round-trip test below builds known-good routes from random station orderings and
asserts `extract_route` recovers them; the second test confirms a planted
subtour is rejected rather than silently accepted.

```python
import hypothesis.strategies as st
from hypothesis import given


@given(st.lists(st.integers(0, 50), min_size=1, max_size=12, unique=True))
def test_extract_route_roundtrip(station_order: List[int]) -> None:
    nodes: List[Node] = [START, *station_order, END]
    arcs: List[Arc] = list(zip(nodes[:-1], nodes[1:]))

    route = extract_route(arcs)

    assert route[0] == START
    assert route[-1] == END
    assert route[1:-1] == station_order
    assert len(set(route)) == len(route)  # every node appears exactly once


def test_extract_route_rejects_subtour() -> None:
    # START -> 0 -> END  plus a detached cycle 1 -> 2 -> 1.
    arcs: List[Arc] = [(START, 0), (0, END), (1, 2), (2, 1)]
    try:
        extract_route(arcs)
    except ValueError:
        pass  # expected: the disconnected cycle is detected
    else:
        raise AssertionError("extract_route accepted arcs containing a subtour")
```

Run the tests on Windows (PowerShell):

```powershell
python -m pytest test_subtour_elimination.py -v
```

Validation checklist:

- [ ] Run the property-based round-trip test and the subtour-rejection test.
- [ ] After solving, assert each vehicle's selected arcs reconstruct via
      `extract_route` (it raises on any subtour or break).
- [ ] Confirm `find_station_subtours` returns an empty list for every vehicle on
      the final solution.
- [ ] Watch the constraint count: prefer static DFJ only for small `n`, and use
      lazy separation otherwise.
- [ ] Bound the lazy loop with `max_iterations` (and ideally a solver time
      limit) so termination is guaranteed.
- [ ] Validate against a known instance (for example a small TSPLIB problem) and
      compare the objective to the published optimum.
- [ ] Confirm compatibility with a recent OR-Tools release and its bundled SCIP
      backend.

## Related skills

- Vehicle Routing with Time Windows (VRPTW)
- Electric Vehicle Routing with Charging (EVRP)
- Mixed-Integer Programming (MIP) with Benders decomposition
- Lazy constraint callbacks in solvers that expose them (Gurobi/CPLEX/CP-SAT)
- Quantum-inspired (QUBO/annealing) formulations for routing
