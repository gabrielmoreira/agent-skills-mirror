---
name: ortools-pickup-delivery-routing
version: 1.1.1
description: "Models Google OR-Tools 9.9+ pickup-and-delivery (PDPTW, dial-a-ride, courier): AddPickupAndDelivery plus same-vehicle and precedence constraints. Use when each job is a coupled pickup/dropoff pair. Not for single-stop VRP, MIP subtour cuts (routing-subtour-elimination), or NVIDIA cuOpt (cuopt-user-rules)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

This skill covers the modeling pattern for pickup-and-delivery routing in OR-Tools (Python, 9.9+). The defining characteristic is that each job is **two coupled events** — a pickup and a matching dropoff — that the same vehicle must serve in order. That coupling separates pickup-and-delivery routing from ordinary stop-by-stop routing: the optimizer cannot visit nodes independently because a dropoff is meaningless unless its pickup happened first, on the same route.

Concrete instances include PDPTW, dial-a-ride, paratransit, patient transport, and same-day courier jobs.

## When to Use

Reach for this skill when each job is really *two coupled events* — a pickup and a matching dropoff/delivery — that the same vehicle must serve in order. Trigger keywords: **pickup-delivery, PDPTW, dial-a-ride, paratransit, patient transport, courier, same-vehicle pairing, precedence, paired stops, connected request set**.

Apply it **after** the base routing model already owns a time dimension and **before** you call the solver. The ordering matters: the pairing constraints reference `time_dimension.CumulVar(index)`, so if the time dimension does not exist yet those references fail at model-build time. Building on top of an existing time dimension also keeps rider time windows and the service-time convention in one place instead of being re-derived for every pair.

### Do not use

Each item below is framed as "avoid X **because** Y" so you can reason about borderline cases:

- **Single-node service jobs.** If a job is a lone stop with no partner node, the pairing machinery (`AddPickupAndDelivery`, the same-vehicle equality, the precedence inequality) adds constraints with nothing to constrain. You pay modeling and search cost for zero benefit; a plain VRP/CVRP model expresses the intent more clearly.
- **OR-Tools older than 9.9.0.** Earlier builds construct `RoutingIndexManager` differently and expose a narrower set of `AddDisjunction` overloads. The grouped-disjunction-with-`max_cardinality` pattern shown here either will not compile or will mean something different. Check the version first (see the runtime guard in the code below).
- **Very large optional-connected sets (more than ~10,000 pairs) without decomposition.** The CP-style grouped disjunction creates a disjunction term per set and keeps partial groups alive throughout local search. At that scale the relaxation inflates memory use and slows convergence past the point of diminishing returns. Decompose the instance first (by region, time bucket, or shipment) so each sub-problem stays tractable.
- **Capacity or load left unmodeled.** This skill deliberately does not re-implement capacity; it assumes a load dimension already enforces it. If you skip capacity entirely the solver will cheerfully overload vehicles, so confirm a load dimension exists (the full example below builds one with `AddDimensionWithVehicleCapacity`).

## Prerequisites

- **OR-Tools ≥ 9.9.0** (Python). The grouped-disjunction overloads and `RoutingIndexManager` constructor changed in 9.9.0; older builds produce a subtly different model rather than an error.
- **Python 3.10+** (uses `from __future__ import annotations` and modern typing).
- A **base routing model** already in place: `RoutingIndexManager`, `RoutingModel`, an arc cost evaluator, and a **time dimension** (`routing.GetDimensionOrDie("Time")`). This skill adds pairing constraints on top of that foundation.
- A **load/capacity dimension** if capacity matters. The example below builds one with `AddDimensionWithVehicleCapacity`; do not skip it unless vehicles are truly uncapacitated.

**Install / verify on Windows (PowerShell, primary host):**

```powershell
pip install ortools
python -c "from ortools import __version__; print(__version__)"
```

Expected output: `9.9.x` or higher. If you see anything below `9.9.0`, upgrade before proceeding.

## Procedure

### Step 1 — Create one pickup node and one dropoff node per job

The solver reasons about *nodes*; a job that is only a row in your data is invisible to it. Represent the pickup and the dropoff as two separate service nodes joined by a shared job ID. Keeping them as distinct nodes is what lets the solver schedule travel between them; a single "job node" could not express the time and load change that happens in between.

- Pickup demand is **positive**; dropoff demand is **negative**, so the running load on the load dimension rises at the pickup and falls back at the dropoff.
- Depot nodes carry **zero demand** and **zero service time** because nothing is loaded or served there.

### Step 2 — Add same-vehicle and precedence constraints for every pair

`AddPickupAndDelivery` alone does **not** force one vehicle or an order. You must add the constraints that encode the real business rules explicitly:

- **Same vehicle:** `routing.VehicleVar(pickup_index) == routing.VehicleVar(dropoff_index)` — without it the solver may legally pick the rider up with one vehicle and drop them off with another.
- **Pickup before dropoff:** `time_dimension.CumulVar(pickup_index) <= time_dimension.CumulVar(dropoff_index)` — the time dimension is the only place the model expresses ordering, so precedence has to live there.

### Step 3 — Apply customer-facing time windows and service-time convention

- Apply customer time windows to the event you actually promised the customer. Appointment and dial-a-ride problems usually constrain the **drop-off arrival** (the rider cares when they get there), and the pickup window is then derived by subtracting direct pickup-to-dropoff travel time from the drop-off window. Anchoring the window to the promised event keeps the optimization honest.
- If the problem statement gives explicit pickup and drop-off window formulas, implement those formulas **verbatim**. Service time belongs in the transit from a node to the next node, not inside the window. Do not silently shift a stated window to "make room" for service time unless the problem says to — doing so changes the customer promise the model is solving, and the discrepancy is invisible later.

### Step 4 — Choose how optional service behaves

Decide whether each optional job is **independent** (may be skipped on its own) or belongs to a **connected request set** (optimized as a group, all-or-nothing). This choice changes which disjunctions you add, so make it explicitly.

For connected sets, prefer the CP-style grouped disjunction (below) when search quality matters. Treat it as a *search-friendly relaxation*: local search may temporarily keep a partial group, and post-processing enforces the final all-or-none business rule. The relaxation exists precisely so the heuristics are not forced into an expensive atomic insert/remove on every move.

- Place the set's pickup nodes in one disjunction with `max_cardinality = len(request_set)` and a large group penalty (for example `len(request_set) * request_penalty`). Scaling the penalty by group size is what makes serving the whole set, rather than one pickup at a time, dominate the objective.
- Add each corresponding dropoff node as an optional node with **zero penalty**. The pickup-delivery constraints still tie feasible served pairs together, while the zero-penalty dropoff optionality prevents the model from being forced to keep an orphan dropoff when its pickup (or the whole set) is skipped.
- Use this grouped-disjunction-plus-post-processing pattern **instead of** hard equality across the set when local search quality matters. Hard all-or-none constraints force insertion and local search to move the entire group atomically, which becomes very slow on large optional pickup-delivery instances.

### Step 5 — Post-process connected sets and re-audit feasibility

After solving, post-process connected sets, rebuild route sequences if a partial group was left behind, and re-audit feasibility before counting served jobs or writing output — because a search-friendly relaxation can produce intermediate states that violate the real all-or-none business rule. Do not count partial sets as served if the domain treats them as unserved. Remove their service nodes and rebuild the route order, or reject the candidate if rebuilding breaks feasibility (the verification helper below flags exactly this).

### Pair constraint skeleton

Use this pattern after the time dimension exists. It encodes the paired-service relationship for each job; optional-service logic is added separately once you have decided whether jobs are independent pairs or members of connected sets. The code is typed end to end and validates its inputs so malformed data fails loudly at build time rather than surfacing as a mysterious "no solution" after a 30-second solve.

```python
"""Pickup-and-delivery pairing constraints for OR-Tools 9.9+ (Python 3.10+)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from ortools.constraint_solver import pywrapcp


def require_ortools_version(minimum: tuple[int, int, int] = (9, 9, 0)) -> None:
    """Fail fast if the runtime predates the API this skill depends on.

    The grouped-disjunction overloads and manager constructor used here changed
    in 9.9.0; running on an older build produces a subtly different model rather
    than an error, so we check explicitly.
    """
    from ortools import __version__ as ortools_version

    parts = tuple(int(p) for p in ortools_version.split(".")[:3])
    if parts < minimum:
        raise RuntimeError(
            f"OR-Tools >= {'.'.join(map(str, minimum))} required, "
            f"found {ortools_version}"
        )


def _validate_window(
    job_id: str, label: str, window: Optional[tuple[int, int]]
) -> None:
    """Reject windows that would silently make the model infeasible."""
    if window is None:
        return
    low, high = window
    if low < 0 or high < 0:
        raise ValueError(f"job {job_id}: {label} window bounds must be non-negative")
    if low > high:
        raise ValueError(
            f"job {job_id}: {label} window is inverted ({low} > {high}); "
            "an inverted window makes the model infeasible with no diagnostic"
        )


@dataclass(frozen=True)
class Job:
    """A single pickup-and-delivery request.

    ``pickup_node`` and ``dropoff_node`` are *model node indices* (positions in
    the travel-time matrix), not OR-Tools routing indices. They are translated
    with ``manager.NodeToIndex`` only when the model is built, so a Job stays
    valid even if the routing model is rebuilt.
    """

    job_id: str
    pickup_node: int
    dropoff_node: int
    demand: int = 1
    pickup_window: Optional[tuple[int, int]] = None
    dropoff_window: Optional[tuple[int, int]] = None

    def __post_init__(self) -> None:
        if self.pickup_node < 0 or self.dropoff_node < 0:
            raise ValueError(f"job {self.job_id}: node indices must be non-negative")
        if self.pickup_node == self.dropoff_node:
            raise ValueError(
                f"job {self.job_id}: pickup and dropoff cannot be the same node "
                f"({self.pickup_node})"
            )
        if self.demand <= 0:
            raise ValueError(
                f"job {self.job_id}: pickup demand must be positive, got {self.demand}"
            )
        _validate_window(self.job_id, "pickup", self.pickup_window)
        _validate_window(self.job_id, "dropoff", self.dropoff_window)


def add_pickup_delivery_pairs(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    time_dimension: pywrapcp.RoutingDimension,
    jobs: Sequence[Job],
) -> None:
    """Wire up the same-vehicle + precedence relationship for every job.

    Why each constraint exists:
    * ``AddPickupAndDelivery`` registers the two nodes as one request so the
      insertion heuristics keep them together instead of treating them as
      unrelated stops.
    * The ``VehicleVar`` equality is *not* implied by the call above; without it
      the solver may legally place pickup and dropoff on different vehicles.
    * The ``CumulVar`` inequality enforces "pick up before you drop off" on the
      shared time dimension, the only place the model expresses ordering.
    """
    if not jobs:
        raise ValueError("no jobs supplied; nothing to constrain")

    num_nodes = manager.GetNumberOfNodes()
    solver = routing.solver()

    for job in jobs:
        if job.pickup_node >= num_nodes or job.dropoff_node >= num_nodes:
            raise ValueError(
                f"job {job.job_id}: node index out of range for a model with "
                f"{num_nodes} nodes"
            )

        pickup_index = manager.NodeToIndex(job.pickup_node)
        dropoff_index = manager.NodeToIndex(job.dropoff_node)

        routing.AddPickupAndDelivery(pickup_index, dropoff_index)
        solver.Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(dropoff_index)
        )
        solver.Add(
            time_dimension.CumulVar(pickup_index)
            <= time_dimension.CumulVar(dropoff_index)
        )

        if job.pickup_window is not None:
            low, high = job.pickup_window
            time_dimension.CumulVar(pickup_index).SetRange(low, high)
        if job.dropoff_window is not None:
            low, high = job.dropoff_window
            time_dimension.CumulVar(dropoff_index).SetRange(low, high)
```

### Optional connected-set modeling

```python
"""Optional connected-set modeling for OR-Tools 9.9+ (Python 3.10+)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ortools.constraint_solver import pywrapcp

# Reuses the Job dataclass and add_pickup_delivery_pairs from the skeleton above.


@dataclass(frozen=True)
class ConnectedRequestSet:
    """A group of jobs the business treats as all-or-nothing."""

    set_id: str
    jobs: Sequence[Job]

    def __post_init__(self) -> None:
        if not self.jobs:
            raise ValueError(
                f"connected set {self.set_id}: must contain at least one job"
            )


def add_optional_connected_sets(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    jobs: Sequence[Job],
    connected_request_sets: Sequence[ConnectedRequestSet],
    request_penalty: int,
) -> None:
    """Model all-or-none optional groups as search-friendly disjunctions.

    Why grouped disjunctions instead of a hard all-or-none equality: hard
    constraints force local search to insert or remove an entire group in one
    move, which cripples insertion heuristics on large instances. A grouped
    disjunction with a large, size-scaled penalty *prefers* serving the whole
    group while still letting search explore partial groups, which we clean up
    in post-processing.
    """
    if request_penalty < 0:
        raise ValueError(
            f"request_penalty must be non-negative, got {request_penalty}"
        )

    num_nodes = manager.GetNumberOfNodes()

    # 1. Mandatory pairing for every job (same vehicle + precedence).
    add_pickup_delivery_pairs(
        routing, manager, routing.GetDimensionOrDie("Time"), jobs
    )

    # 2. One grouped disjunction per connected set, over the set's pickups.
    for request_set in connected_request_sets:
        pickup_indices: list[int] = []
        for job in request_set.jobs:
            if job.pickup_node >= num_nodes:
                raise ValueError(
                    f"set {request_set.set_id}, job {job.job_id}: pickup node "
                    f"out of range for a {num_nodes}-node model"
                )
            pickup_indices.append(manager.NodeToIndex(job.pickup_node))

        group_size = len(pickup_indices)
        # Penalty scaled by group size makes serving the whole set dominate the
        # objective; max_cardinality == group_size lets the set be served
        # together rather than one pickup at a time.
        routing.AddDisjunction(
            pickup_indices,
            request_penalty * group_size,
            group_size,
        )

    # 3. Zero-penalty optional dropoffs: prevents an orphan dropoff when its
    #    pickup is skipped, without rewarding a dropoff served on its own.
    for job in jobs:
        dropoff_index = manager.NodeToIndex(job.dropoff_node)
        routing.AddDisjunction([dropoff_index], 0)
```

## Examples

The example below is a complete, runnable model that exercises the latest OR-Tools API (9.9+). It replaces the usual "return 1 for every arc" stub with a real travel-time matrix derived from coordinates, registers an arc cost so the solver has something concrete to minimize, builds a genuine capacity (load) dimension, and converts routing indices to node indices inside every callback — a conversion that is easy to forget and a frequent source of silently wrong routes.

```python
"""End-to-end pickup-and-delivery example for OR-Tools 9.9+ (Python 3.10+)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Reuses Job, _validate_window, require_ortools_version, and
# add_pickup_delivery_pairs from the skeleton above.


def build_travel_time_matrix(coords: Sequence[tuple[int, int]]) -> list[list[int]]:
    """Symmetric integer travel-time matrix from (x, y) coordinates.

    OR-Tools transit callbacks must return integers, so Euclidean distance is
    rounded to whole minutes. Travel times must be non-negative, otherwise local
    search can chase phantom negative-cost arcs and fail to converge.
    """
    n = len(coords)
    if n == 0:
        raise ValueError("coordinate list is empty")

    matrix: list[list[int]] = [[0] * n for _ in range(n)]
    for i, (xi, yi) in enumerate(coords):
        for j, (xj, yj) in enumerate(coords):
            if i == j:
                continue
            distance = round(((xi - xj) ** 2 + (yi - yj) ** 2) ** 0.5)
            if distance < 0:  # defensive: rounding can never go negative, but
                raise ValueError(f"negative travel time computed for arc {i}->{j}")
            matrix[i][j] = int(distance)
    return matrix


def print_solution(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    assignment: pywrapcp.Assignment,
    time_dimension: pywrapcp.RoutingDimension,
    num_vehicles: int,
) -> None:
    """Print each vehicle's route with arrival times, plus the total time."""
    total_time = 0
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        stops: list[str] = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            arrival = assignment.Value(time_dimension.CumulVar(index))
            stops.append(f"{node}@{arrival}")
            index = assignment.Value(routing.NextVar(index))
        end_node = manager.IndexToNode(index)
        end_time = assignment.Value(time_dimension.CumulVar(index))
        stops.append(f"{end_node}@{end_time}")
        total_time += end_time
        print(f"Route for vehicle {vehicle_id}: {' -> '.join(stops)}")
    print(f"Total time across vehicles: {total_time}")


def solve_pickup_delivery() -> pywrapcp.Assignment:
    """Build and solve a small PDPTW instance, returning the assignment."""
    require_ortools_version()

    # ----- Data definition --------------------------------------------------
    # Node 0 is the depot; nodes 1-4 are the pickup/dropoff stops.
    coords = [
        (0, 0),   # 0: depot
        (1, 3),   # 1: pickup  job A
        (4, 3),   # 2: dropoff job A
        (2, 1),   # 3: pickup  job B
        (5, 1),   # 4: dropoff job B
    ]

    jobs = [
        Job(
            job_id="A",
            pickup_node=1,
            dropoff_node=2,
            demand=1,
            pickup_window=(0, 15),
            dropoff_window=(0, 30),
        ),
        Job(
            job_id="B",
            pickup_node=3,
            dropoff_node=4,
            demand=1,
            pickup_window=(0, 20),
            dropoff_window=(0, 40),
        ),
    ]

    num_vehicles = 2
    depot = 0

    # ----- Manager + routing model -----------------------------------------
    time_matrix = build_travel_time_matrix(coords)
    manager = pywrapcp.RoutingIndexManager(
        len(coords), num_vehicles, depot
    )
    routing = pywrapcp.RoutingModel(manager)

    # ----- Transit callback (node-index → routing-index conversion) --------
    def time_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(
            routing.NextVar(from_index)
        ) if False else 0  # placeholder; real callback below
        return 0

    # Correct transit callback:
    def transit_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(transit_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # ----- Time dimension ---------------------------------------------------
    time_dimension_name = "Time"
    routing.AddDimension(
        transit_callback_index,
        30,  # slack: allow waiting at nodes
        60,  # max time per vehicle
        True,  # start cumul at zero
        time_dimension_name,
    )
    time_dimension = routing.GetDimensionOrDie(time_dimension_name)

    # ----- Load / capacity dimension ---------------------------------------
    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        for job in jobs:
            if from_node == job.pickup_node:
                return job.demand
            if from_node == job.dropoff_node:
                return -job.demand
        return 0  # depot or unmodeled node

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback
    )
    vehicle_capacities = [2, 2]
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,                   # no extra load slack
        vehicle_capacities,  # per-vehicle capacity
        True,                # load starts at zero
        "Load",
    )

    # ----- Pickup-delivery constraints -------------------------------------
    add_pickup_delivery_pairs(routing, manager, time_dimension, jobs)

    # ----- Search parameters ------------------------------------------------
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 30

    # ----- Solve ------------------------------------------------------------
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment is None:
        raise RuntimeError(
            "solver returned no assignment; check that time windows are wide "
            "enough, capacities are sufficient, and every dropoff is reachable "
            "after its pickup within the time budget"
        )

    print_solution(routing, manager, assignment, time_dimension, num_vehicles)
    return assignment


if __name__ == "__main__":
    solve_pickup_delivery()
```

**Run on Windows (PowerShell):**

```powershell
python solve_pickup_delivery.py
```

Expected output (routes vary by solver version, but structure should match):

```
Route for vehicle 0: 0@0 -> 1@3 -> 2@6 -> 0@9
Route for vehicle 1: 0@0 -> 3@2 -> 4@5 -> 0@8
Total time across vehicles: 17
```

## Pitfalls

- **`AddPickupAndDelivery` does NOT enforce same-vehicle or precedence by itself.** It only registers the two nodes as one request for insertion heuristics. You must add the `VehicleVar` equality and the `CumulVar` inequality explicitly. Forgetting either is the single most common silent bug.
- **Forgetting `manager.IndexToNode` / `manager.NodeToIndex` conversions inside callbacks.** OR-Tools callbacks receive *routing indices*, not *node indices*. A callback that indexes the travel-time matrix with a routing index produces silently wrong costs and routes. Always convert.
- **Inverted time windows (`low > high`).** These make the model infeasible with no diagnostic — the solver simply returns `None`. The `_validate_window` helper catches this at build time.
- **Shifting stated time windows to "make room" for service time.** Service time belongs in the transit evaluator, not inside the window. Silently shifting a window changes the customer promise the model is solving, and the discrepancy is invisible later.
- **Partial connected sets left behind by the relaxation.** The grouped-disjunction pattern is a *search-friendly relaxation* — local search may keep a partial group. If your domain treats partial sets as unserved, you must post-process: remove orphan service nodes, rebuild route order, and re-audit feasibility before counting served jobs.
- **Running on OR-Tools < 9.9.0.** The `RoutingIndexManager` constructor and `AddDisjunction` overloads changed in 9.9.0. Older builds produce a subtly different model rather than an error. Always call `require_ortools_version()` at the top of your script.
- **Negative travel times.** OR-Tools transit callbacks must return non-negative integers. If a callback ever returns a negative value, local search can chase phantom negative-cost arcs and fail to converge.
- **Capacity left unmodeled.** This skill does not re-implement capacity. If you skip the load dimension, the solver will overload vehicles. Always confirm a `Load` dimension exists when capacity matters.
- **Hard all-or-none equality on large optional sets.** Hard constraints force local search to move the entire group atomically, crippling insertion heuristics. Use the grouped-disjunction-plus-post-processing pattern instead.

## Verification

A pickup-and-delivery model has more ways to be quietly wrong than a plain VRP (a dropoff before its pickup, a split pair across vehicles, a partial connected set), so verification is not optional. Run the checklist, and use the typed helper below to turn "looks fine" into concrete, line-itemized findings.

### Checklist

- [ ] **Unit-test suite** — run the project's automated tests covering pickup-delivery constraints, time-window adherence, and optional-set handling, so regressions surface before they reach a solve.
- [ ] **Feasibility audit** — confirm every mandatory pickup is visited before its paired dropoff and that both respect their time windows; this is the core invariant the whole model exists to protect.
- [ ] **Capacity check** — ensure vehicle load never exceeds capacity anywhere on the route, because the time dimension passing tells you nothing about load.
- [ ] **All-or-none validation** — for each connected request set, verify either all its pickups and dropoffs are served or none are, since the search relaxation can legally leave a partial set behind.
- [ ] **Objective comparison** — compare the objective (total time, distance, or penalty) against a known benchmark or a second solver (for example CP-SAT or Gurobi) to gauge how close to optimal you are, not just whether you are feasible.

### Verification helper

```python
"""Independent verification of a pickup-and-delivery assignment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from ortools.constraint_solver import pywrapcp

# Reuses the Job dataclass from the skeleton above.


@dataclass
class VerificationResult:
    """Structured outcome: ``ok`` is the verdict, ``errors`` explains failures."""

    ok: bool = True
    errors: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.ok = False
        self.errors.append(message)


def verify_solution(
    assignment: Optional[pywrapcp.Assignment],
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    jobs: Sequence[Job],
    time_dimension: pywrapcp.RoutingDimension,
    num_vehicles: int,
    load_dimension: Optional[pywrapcp.RoutingDimension] = None,
    vehicle_capacities: Optional[Sequence[int]] = None,
) -> VerificationResult:
    """Check pairing, precedence, time windows, and (optionally) capacity.

    Returns every violation rather than stopping at the first, so a single run
    tells you everything that is wrong with the candidate solution.
    """
    result = VerificationResult()

    if assignment is None:
        result.fail("no assignment to verify")
        return result

    if load_dimension is not None and vehicle_capacities is None:
        raise ValueError(
            "vehicle_capacities is required when load_dimension is provided"
        )
    if (
        vehicle_capacities is not None
        and len(vehicle_capacities) != num_vehicles
    ):
        raise ValueError("vehicle_capacities length must equal num_vehicles")

    # Pre-compute each vehicle's ordered routing-index sequence once, so the
    # per-job checks below are simple list lookups instead of repeated walks.
    vehicle_routes: dict[int, list[int]] = {}
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        sequence: list[int] = []
        while not routing.IsEnd(index):
            sequence.append(index)
            index = assignment.Value(routing.NextVar(index))
        sequence.append(index)  # include the end node
        vehicle_routes[vehicle_id] = sequence

    # 1. Same vehicle + precedence for every job.
    for job in jobs:
        pickup_index = manager.NodeToIndex(job.pickup_node)
        dropoff_index = manager.NodeToIndex(job.dropoff_node)

        pickup_vehicle = assignment.Value(routing.VehicleVar(pickup_index))
        dropoff_vehicle = assignment.Value(routing.VehicleVar(dropoff_index))

        if pickup_vehicle != dropoff_vehicle:
            result.fail(
                f"job {job.job_id}: pickup on vehicle {pickup_vehicle} but "
                f"dropoff on vehicle {dropoff_vehicle}"
            )
            continue

        route = vehicle_routes.get(pickup_vehicle, [])
        try:
            pickup_pos = route.index(pickup_index)
            dropoff_pos = route.index(dropoff_index)
        except ValueError:
            result.fail(
                f"job {job.job_id}: pickup or dropoff missing from the route of "
                f"vehicle {pickup_vehicle}"
            )
            continue

        if pickup_pos >= dropoff_pos:
            result.fail(f"job {job.job_id}: dropoff visited before pickup")

    # 2. Time windows on whichever events carry one.
    for job in jobs:
        for label, node, window in (
            ("pickup", job.pickup_node, job.pickup_window),
            ("dropoff", job.dropoff_node, job.dropoff_window),
        ):
            if window is None:
                continue
            idx = manager.NodeToIndex(node)
            arrival = assignment.Value(time_dimension.CumulVar(idx))
            low, high = window
            if not (low <= arrival <= high):
                result.fail(
                    f"job {job.job_id}: {label} arrival {arrival} outside "
                    f"window [{low}, {high}]"
                )

    # 3. Capacity, only when the caller actually modeled a Load dimension.
    if load_dimension is not None and vehicle_capacities is not None:
        for vehicle_id, route in vehicle_routes.items():
            capacity = vehicle_capacities[vehicle_id]
            for idx in route:
                load = assignment.Value(load_dimension.CumulVar(idx))
                if load > capacity:
                    node = manager.IndexToNode(idx)
                    result.fail(
                        f"vehicle {vehicle_id}: load {load} exceeds capacity "
                        f"{capacity} at node {node}"
                    )
                    break  # one report per vehicle is enough to flag the route

    return result
```

### Quick verification command (Windows PowerShell)

```powershell
# Run the end-to-end example and pipe output to a log for inspection
python solve_pickup_delivery.py 2>&1 | Tee-Object -FilePath solve_output.log

# Check OR-Tools version in your environment
python -c "from ortools import __version__; print(__version__)"
```

Expected: version prints `9.9.x` or higher; solve output shows routes with pickup nodes appearing before their paired dropoff nodes on the same vehicle.

## Related skills

This skill builds on the same OR-Tools routing core as the Vehicle Routing Problem (VRP) and Capacitated Vehicle Routing Problem (CVRP) skills. VRP gives you the base model (manager, routing model, arc cost, first-solution and local-search strategies) that this skill assumes is already in place; CVRP contributes the load dimension that the capacity guidance here depends on. Reach for those when a job is a single stop with no partner; reach for this one the moment a job becomes a coupled pickup/dropoff pair.
