---
name: logistics-rules-to-optimization
version: 1.1.1
description: "Maps operations prose onto mixed-integer sets, decision variables, and constraint patterns for Gurobi, CPLEX, or SCIP. Use when dispatch, vehicle routing, warehouse rebalancing, staffing, or production limits need a solver model. Not for already-posed mathematical programs, millisecond control loops, or quantum formulations."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Logistics Rules To Optimization

Translate natural-language operations rules into a formal optimization model — variables, constraints, and objective — using a repeatable pattern library.

The same translation workflow applies to transportation, dispatch, rebalancing, warehouse moves, staffing, scheduling, assignment, capacity planning, production, and service-level problems.

## When to Use

- Converting natural-language operations rules into mathematical optimization models
- Vehicle routing, pickup/delivery, and rebalancing problems
- Warehouse inventory movement and storage optimization
- Staff scheduling and assignment with capacity constraints
- Production planning with resource limits and time windows
- Any problem with entities (vehicles, locations, jobs, workers), decisions (assignments, sequences, quantities), and constraints (capacity, time windows, compatibility)

**Do not use when:**

- Pure machine learning tasks without optimization components
- Problems that only require heuristic or rule-based solutions without formal modeling
- The problem is already formulated as a mathematical program
- Real-time control systems requiring millisecond-level decisions (use pre-computed policies instead)
- Problems requiring quantum optimization (use specialized quantum formulations)
- Models with non-convex constraints unless using appropriate solvers (Gurobi 11.0+, SCIP 9.0+)
- Legacy Python 2.7 or Python 3.7 environments (requires Python 3.10+)

## Prerequisites

- **Python 3.10+** — older versions are not supported
- A MIP solver installed: Gurobi 11.0+, CPLEX 23.1+, or SCIP 9.0+
- PySCIPOpt, gurobipy, or docplex Python bindings depending on solver choice
- Basic familiarity with mixed-integer programming concepts

## Procedure

### Step 1 — List Entities

Extract every entity from the problem statement:

- Vehicles, locations, depots, jobs, workers, machines, products, arcs, time periods
- Write them as explicit sets: `vehicles`, `locations`, `customers`, `arcs`, `periods`, etc.

### Step 2 — Choose Decision Variables

Follow these patterns based on the decision type:

**Binary (yes/no choices):**

```python
x = {(i, j): model.addVar(vtype="B", name=f"x_{i}_{j}") for i in I for j in J}
```

**Integer (counts, loads, inventory, units moved):**

```python
load = {(v, i): model.addVar(vtype="I", lb=0, ub=vehicle_capacity, name=f"load_{v}_{i}") for v in vehicles for i in nodes}
inventory = {(i, t): model.addVar(vtype="I", lb=0, ub=storage_capacity[i], name=f"inventory_{i}_{t}") for i in locations for t in periods}
```

**Continuous (time, flow, cost, utilization, fractional quantities):**

```python
arrival = {(v, i): model.addVar(vtype="C", lb=0, name=f"arrival_{v}_{i}") for v in vehicles for i in nodes}
```

**Route arc variables** (when order of visits matters):

```python
x = {
    (v, i, j): model.addVar(vtype="B", name=f"x_{v}_{i}_{j}")
    for v in vehicles
    for i, j in arcs
}
```

`x[v, i, j] = 1` means vehicle/resource `v` goes directly from node `i` to node `j`.

**Visit indicator** — derive from route arcs instead of creating a second binary unless the model needs it repeatedly:

```python
visit = quicksum(x[v, i, j] for j in to_nodes if j != i)
```

If a standalone variable is useful:

```python
visit = {(v, i): model.addVar(vtype="B", name=f"visit_{v}_{i}") for v in vehicles for i in locations}

for v in vehicles:
    for i in locations:
        model.addCons(visit[v, i] == quicksum(x[v, i, j] for j in to_nodes if j != i))
```

### Step 3 — Translate Each Business Rule

Convert each rule into one of these canonical patterns:

| Pattern | Meaning | Example |
| --- | --- | --- |
| Conservation | What enters equals what leaves, plus/minus changes | Inventory balance |
| Capacity | Quantity cannot exceed a limit | Vehicle load ≤ capacity |
| Linking | A quantity is allowed only if a binary decision is active | `q[i] ≤ M * use[i]` |
| Assignment | Exactly one, at most one, or at least one choice | `sum_j x[i,j] == 1` |
| Sequence | If one action follows another, update load/time/state | Arrival time propagation |
| Compatibility | Prohibit impossible combinations | `x[a] + x[b] ≤ 1` |
| Soft penalty | Add slack for unmet demand or violation cost | `served[i] + unmet[i] ≥ demand[i]` |

#### Common Logistics Rules Reference Table

| Business Rule | Variable Choice | Constraint Pattern |
| --- | --- | --- |
| Choose exactly one option | `x[i,j]` binary | `sum_j x[i,j] == 1` |
| Choose at most one option | `x[i,j]` binary | `sum_j x[i,j] <= 1` |
| Open facility before assigning to it | `open[j]`, `assign[i,j]` binary | `assign[i,j] <= open[j]` |
| Resource capacity | quantity variable | `sum_i q[i,j] <= capacity[j]` |
| Quantity only if selected | `q[i]`, `use[i]` | `q[i] <= M * use[i]` |
| Fixed cost if used | `use[i]` binary | add `fixed_cost[i] * use[i]` to objective |
| Mutually exclusive modes | mode binaries | `sum_m mode[i,m] <= 1` |
| Incompatible pair | two binaries | `x[a] + x[b] <= 1` |
| Demand must be met | flow/quantity | `supply_to[i] >= demand[i]` |
| Demand may be unmet | nonnegative slack | `served[i] + unmet[i] >= demand[i]` |
| Absolute deviation penalty | nonnegative slack | `actual-target <= dev`, `target-actual <= dev` |
| Inventory balance | inventory variables | `inv[t+1] = inv[t] + inbound - outbound` |
| Station/storage upper bound | inventory variable | `inv[i,t] <= capacity[i]` |
| Cannot remove unavailable stock | move variable | `outbound[i,t] <= inv[i,t]` |
| Vehicle starts at depot | arc variables | `sum_j x[v, START, j] == use_vehicle[v]` |
| Vehicle ends at depot | arc variables | `sum_i x[v, i, END] == use_vehicle[v]` |
| Route continuity | arc variables | `incoming[v,i] == outgoing[v,i]` |
| Visit at most once | arc variables | `outgoing[v,i] <= 1` |
| Split service allowed | arc/quantity variables | omit global single-visit; aggregate quantities over resources |
| Time window | arrival variable | `earliest[i] <= arrival[v,i] <= latest[i]` when visited |
| Travel time propagation | arc + arrival | `arrival[j] >= arrival[i] + service_time[i] + travel[i,j] - M(1-x[i,j])` |
| Precedence | start/arrival variables | `start[b] >= finish[a]` |
| Route duration limit | arc variables | `sum travel[i,j] * x[v,i,j] <= max_duration[v]` |

#### Constraint Examples

**Capacity:**

```python
for r in resources:
    model.addCons(quicksum(amount[i, r] for i in items) <= capacity[r])
```

**Quantity allowed only when active** — use the tightest possible `M`:

```python
for i in items:
    model.addCons(quantity[i] <= upper_bound[i] * use[i])
```

**Soft demand satisfaction:**

```python
unmet = {i: model.addVar(vtype="I", lb=0, name=f"unmet_{i}") for i in customers}

for i in customers:
    model.addCons(served[i] + unmet[i] >= demand[i])

penalty_cost = quicksum(penalty[i] * unmet[i] for i in customers)
```

**Absolute target deviation** — **NEVER use Python `abs()` on solver expressions**:

```python
dev = {i: model.addVar(vtype="C", lb=0, name=f"dev_{i}") for i in items}

for i in items:
    model.addCons(actual[i] - target[i] <= dev[i])
    model.addCons(target[i] - actual[i] <= dev[i])
```

**Depot start and end** — if every vehicle must be used:

```python
for v in vehicles:
    model.addCons(quicksum(x[v, START, j] for j in locations) == 1)
    model.addCons(quicksum(x[v, i, END] for i in locations) == 1)
```

If vehicles are optional:

```python
use_vehicle = {v: model.addVar(vtype="B", name=f"use_vehicle_{v}") for v in vehicles}

for v in vehicles:
    model.addCons(quicksum(x[v, START, j] for j in locations) == use_vehicle[v])
    model.addCons(quicksum(x[v, i, END] for i in locations) == use_vehicle[v])
```

**Route continuity and at-most-once visits:**

```python
for v in vehicles:
    for i in locations:
        incoming = quicksum(x[v, j, i] for j in from_nodes if j != i)
        outgoing = quicksum(x[v, i, j] for j in to_nodes if j != i)

        model.addCons(incoming == outgoing)
        model.addCons(outgoing <= 1)
```

This means vehicle `v` visits location `i` no more than once. It does **not** prevent a different vehicle from also visiting `i`.

**Global single-visit rule** — use only when the real rule forbids split service across vehicles/resources:

```python
for i in locations:
    model.addCons(
        quicksum(x[v, i, j] for v in vehicles for j in to_nodes if j != i) <= 1
    )
```

Do **not** add this rule when a large pickup/dropoff target may need multiple vehicles.

**Load or state transition along selected arcs** — if `state[j] = state[i] + change[j]` when arc `(i, j)` is used:

```python
M = 2 * vehicle_capacity

for v in vehicles:
    for i, j in arcs:
        change_at_j = service[v, j] if isinstance(j, int) else 0
        model.addCons(load[v, j] - load[v, i] - change_at_j <= M * (1 - x[v, i, j]))
        model.addCons(load[v, j] - load[v, i] - change_at_j >= -M * (1 - x[v, i, j]))
```

This pattern works for load, arrival time, battery charge, inventory state, and other route-dependent state variables. Pick `M` from real variable bounds.

**Time windows:**

```python
for v in vehicles:
    for i in locations:
        visit_i = quicksum(x[v, i, j] for j in to_nodes if j != i)
        model.addCons(arrival[v, i] >= earliest[i] - horizon * (1 - visit_i))
        model.addCons(arrival[v, i] <= latest[i] + horizon * (1 - visit_i))

    for i, j in arcs:
        if j in locations:
            model.addCons(
                arrival[v, j] >= arrival[v, i] + service_time.get(i, 0) + travel_time[i, j] - horizon * (1 - x[v, i, j])
            )
```

### Step 4 — Inventory Pickup/Dropoff Pattern

For rebalancing or material movement, define one signed service variable. Recommended convention:

- `service[v, i] > 0`: pickup from location `i`, vehicle load increases, location inventory decreases
- `service[v, i] < 0`: dropoff to location `i`, vehicle load decreases, location inventory increases

```python
service = {
    (v, i): model.addVar(vtype="I", lb=-vehicle_capacity, ub=vehicle_capacity, name=f"service_{v}_{i}")
    for v in vehicles
    for i in locations
}

for v in vehicles:
    for i in locations:
        visit_i = quicksum(x[v, i, j] for j in to_nodes if j != i)
        model.addCons(service[v, i] <= vehicle_capacity * visit_i)
        model.addCons(service[v, i] >= -vehicle_capacity * visit_i)

for i in locations:
    net_change = quicksum(service[v, i] for v in vehicles)
    free_space = storage_capacity[i] - initial_inventory[i]

    model.addCons(net_change <= initial_inventory[i])  # pickup cannot exceed stock
    model.addCons(net_change >= -free_space)           # dropoff cannot exceed space
```

If the target is a desired net pickup/dropoff:

```python
unmet = {i: model.addVar(vtype="I", lb=0, name=f"unmet_{i}") for i in locations}

for i in locations:
    net_change = quicksum(service[v, i] for v in vehicles)
    model.addCons(net_change - target[i] <= unmet[i])
    model.addCons(target[i] - net_change <= unmet[i])
```

Extract pickup/dropoff output as:

```python
picked_up = max(service_value, 0)
dropped_off = max(-service_value, 0)
```

### Step 5 — Build the Objective

Add the objective **last**, keeping named components:

```python
travel_cost = quicksum(distance[i, j] * x[v, i, j] for v in vehicles for i, j in arcs)
fixed_cost = quicksum(vehicle_fixed_cost[v] * use_vehicle[v] for v in vehicles)
penalty_cost = quicksum(penalty[i] * unmet[i] for i in customers)

model.setObjective(travel_cost + fixed_cost + penalty_cost, "minimize")
```

### Step 6 — Extract and Independently Validate

Recompute routes, loads, assignments, inventory, penalties, and the objective value from the solver output data — do not trust the solver's reported objective alone. Independently verify every extracted quantity against the model's constraints.

## Pitfalls

- **Never use Python `abs()` on solver expressions.** It does not linearize correctly. Always use paired slack constraints (`actual - target ≤ dev` and `target - actual ≤ dev`).
- **Do not add a global single-visit rule when split service is allowed.** Large pickup/dropoff targets may legitimately require multiple vehicles.
- **Use the tightest possible big-M.** Overly large `M` values cause numerical issues and weak relaxations. Derive `M` from real variable bounds (e.g., `M = 2 * vehicle_capacity` for load transitions).
- **Route continuity `incoming == outgoing` is per-vehicle, not global.** It does not prevent other vehicles from visiting the same node.
- **Visit indicators derived from arcs are expressions, not variables.** Do not add constraints on them as if they were standalone variables unless you explicitly declare them.
- **Python 3.10+ required.** Do not attempt to run in Python 2.7 or 3.7 environments.
- **Non-convex constraints require specialized solvers** (Gurobi 11.0+, SCIP 9.0+). Standard MIP solvers may silently produce wrong results or fail.
- **Integer variables for physical unit counts** — use `vtype="I"` when the output must be integer-valued; continuous variables will produce fractional loads/units.

## Verification

- [ ] Run the test suite with sample logistics problems
- [ ] Verify all constraint patterns produce feasible solutions
- [ ] Check that objective components match business requirements
- [ ] Validate extracted output against manual recomputation of routes, loads, assignments, inventory, penalties, and objective
- [ ] **Confirm no Python `abs()` used on solver expressions** — search the codebase for `abs(` in model code
- [ ] Test with latest solver versions (Gurobi 11.0+, CPLEX 23.1+, SCIP 9.0+)
- [ ] Validate against edge cases: zero demand, single vehicle, full capacity, empty arcs, single-node problems
- [ ] Confirm big-M values are derived from real variable bounds, not arbitrary large numbers
- [ ] Verify that split-service rules (or their absence) match the business requirement

## Related Skills

- optimization-modeling-fundamentals
- vehicle-routing-problem-formulation
- inventory-optimization-patterns
- scheduling-with-time-windows
- mixed-integer-programming-best-practices
- quantum-optimization-for-logistics
- explainable-ai-for-operations
