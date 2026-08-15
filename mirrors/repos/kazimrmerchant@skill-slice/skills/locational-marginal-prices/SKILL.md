---
name: locational-marginal-prices
version: 1.1.1
description: "Extracts locational marginal prices (LMPs) as DC-OPF nodal-balance duals (CVXPY + CLARABEL/OSQP), plus reserve MCP. Use for nodal electricity prices, congestion, or transmission counterfactuals. Not for AC-OPF (voltage/Q), unsolved duals, inventory EOQ (inventory-demand-planning), or NVIDIA cuOpt routing (cuopt-user-rules)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Locational Marginal Prices (LMPs)

LMPs are the marginal cost of serving one additional MW of load at each bus. In optimization terms, they are the **dual values** (shadow prices) of the nodal power-balance constraints in a DC-OPF (Direct Current Optimal Power Flow) formulation.

## When to Use

- When computing **nodal electricity prices** for a power system solved via DC-OPF.
- When calculating **reserve clearing prices** (MCP) from a system-wide reserve requirement constraint.
- When performing **price-impact or counterfactual analysis** to see how transmission upgrades affect costs and congestion.
- When identifying **congestion points** (binding lines) in a DC-OPF solution.

### Do Not Use

- **AC-OPF**: Do not use for AC-OPF calculations where voltage magnitude and reactive power (Q) are critical; LMPs will differ.
- **Non-optimal solves**: Do not use if the optimization problem is not solved to optimality; dual values may be unstable or incorrect.
- **Deprecated solvers**: Avoid legacy solvers such as `ECOS` for large-scale DC-OPF; they may produce inaccurate duals. Prefer `CLARABEL` (v0.7+) or `OSQP` (v0.6+) with dual extraction support.
- **Insecure data handling**: Never expose raw dual values or model data through unauthenticated APIs; they can reveal system operating points. Apply proper access controls and sanitise outputs.

## Prerequisites

- **Python 3.9+** with `cvxpy>=1.4.0`, `numpy`.
- A solver that returns reliable duals: **CLARABEL v0.7+** (recommended default) or **OSQP v0.6+**.
- A solved or solvable DC-OPF problem with nodal power-balance constraints stored as references.
- If using `OSQP`, enable `eps_dual_inf` and verify dual feasibility explicitly.

## Procedure

### Step 1 — Store references to balance constraints

You must keep a handle to each nodal balance constraint so duals can be read after solving.

```python
import cvxpy as cp
import numpy as np

# --- Problem data (example placeholders) ---
n_bus, n_gen, n_branch = 5, 8, 7
baseMVA = 100.0
B = np.random.randn(n_bus, n_bus)          # susceptance matrix
theta = cp.Variable(n_bus)                 # voltage angles
Pg = cp.Variable(n_gen)                    # generator outputs
Rg = cp.Variable(n_gen)                    # reserve provision
gen_bus = np.random.randint(0, n_bus, n_gen)
buses = np.random.rand(n_bus, 3)           # [bus_id, ?, load_MW]
branches = np.random.rand(n_branch, 6)     # [from, to, ?, x, ?, rate_MW]

# --- Build constraints ---
constraints = []
balance_constraints = []   # keep a handle for dual extraction

for i in range(n_bus):
    pg_at_bus = cp.sum(Pg[g] for g in range(n_gen) if gen_bus[g] == i)
    pd = buses[i, 2] / baseMVA

    bal = pg_at_bus - pd == B[i, :] @ theta
    balance_constraints.append(bal)
    constraints.append(bal)

# Example system-wide reserve requirement
reserve_requirement = 50.0
reserve_con = cp.sum(Rg) >= reserve_requirement
constraints.append(reserve_con)

# Objective (simple quadratic cost placeholder)
cost = cp.sum_squares(Pg) + 0.01 * cp.sum_squares(theta)
```

### Step 2 — Solve with a dual-enabled solver

```python
# Solve with Clarabel (default dual-enabled solver)
prob = cp.Problem(cp.Minimize(cost), constraints)
prob.solve(solver=cp.CLARABEL, verbose=False)   # set verbose=True for debugging
```

> **Note**: `CLARABEL` (v0.7+) provides high-precision duals and is the recommended default for DC-OPF. If you must use `OSQP`, enable `eps_dual_inf` and verify dual feasibility.

### Step 3 — Extract LMPs from dual values

Read dual values **only after** `prob.solve()` completes without errors. Convert from per-unit to $/MWh by multiplying by `baseMVA`.

```python
# --- Extract LMPs ---
lmp_by_bus = []
for i, bal in enumerate(balance_constraints):
    bus_num = int(buses[i, 0])
    dual_val = bal.dual_value

    # Convert from per-unit to $/MWh
    lmp = float(dual_val) * baseMVA if dual_val is not None else 0.0
    lmp_by_bus.append({
        "bus": bus_num,
        "lmp_dollars_per_MWh": round(lmp, 2)
    })
```

### Step 4 — Extract reserve clearing price (MCP)

The reserve MCP is the dual of the system-wide reserve requirement constraint.

```python
# After solving (see above)
reserve_mcp = float(reserve_con.dual_value) if reserve_con.dual_value is not None else 0.0
print(f"Reserve MCP: ${reserve_mcp:.2f}/MWh")
```

### Step 5 — Identify binding lines

Lines operating at or above a configurable loading threshold are considered binding.

```python
BINDING_THRESHOLD = 99.0  # percent loading

binding_lines = []
for k, br in enumerate(branches):
    f_idx = int(br[0])
    t_idx = int(br[1])
    x, rate = br[3], br[5]

    if x == 0 or rate <= 0:
        continue

    b = 1.0 / x
    flow_MW = b * (theta.value[f_idx] - theta.value[t_idx]) * baseMVA
    loading_pct = abs(flow_MW) / rate * 100

    if loading_pct >= BINDING_THRESHOLD:
        binding_lines.append({
            "from": int(br[0]),
            "to": int(br[1]),
            "flow_MW": round(float(flow_MW), 2),
            "limit_MW": round(float(rate), 2),
            "loading_pct": round(loading_pct, 1)
        })
```

### Step 6 — Counterfactual analysis (transmission upgrade)

Assess the impact of relaxing a transmission constraint by increasing a line's thermal limit and re-solving.

```python
def relax_line(branches, target_from, target_to, factor=1.20):
    """Increase thermal limit of a specific line by `factor`."""
    for k in range(branches.shape[0]):
        f, t = int(branches[k, 0]), int(branches[k, 1])
        if (f == target_from and t == target_to) or (f == target_to and t == target_from):
            branches[k, 5] *= factor
            break
    return branches

# 1. Base case solved above -> store results
base_cost = prob.value
base_lmp_map = {item["bus"]: item["lmp_dollars_per_MWh"] for item in lmp_by_bus}
base_binding = binding_lines.copy()

# 2. Modify constraint
branches_cf = relax_line(branches.copy(), target_from=2, target_to=5, factor=1.20)

# 3. Re-solve with modified data
cf_constraints = []
cf_balance_constraints = []

for i in range(n_bus):
    pg_at_bus = cp.sum(Pg[g] for g in range(n_gen) if gen_bus[g] == i)
    pd = buses[i, 2] / baseMVA

    bal = pg_at_bus - pd == B[i, :] @ theta
    cf_balance_constraints.append(bal)
    cf_constraints.append(bal)

cf_constraints.append(cp.sum(Rg) >= reserve_requirement)

# Re-solve
cf_prob = cp.Problem(cp.Minimize(cost), cf_constraints)
cf_prob.solve(solver=cp.CLARABEL, verbose=False)

# Extract counterfactual LMPs
cf_lmp_by_bus = []
for i, bal in enumerate(cf_balance_constraints):
    bus_num = int(buses[i, 0])
    dual_val = bal.dual_value
    lmp = float(dual_val) * baseMVA if dual_val is not None else 0.0
    cf_lmp_by_bus.append({
        "bus": bus_num,
        "lmp_dollars_per_MWh": round(lmp, 2)
    })

# 4. Compare
cost_reduction = base_cost - cf_prob.value
cf_lmp_map = {item["bus"]: item["lmp_dollars_per_MWh"] for item in cf_lmp_by_bus}
lmp_deltas = {bus: cf_lmp_map[bus] - base_lmp_map[bus] for bus in base_lmp_map}

# Find new binding lines for counterfactual
cf_binding_lines = []
for k, br in enumerate(branches_cf):
    f_idx = int(br[0])
    t_idx = int(br[1])
    x, rate = br[3], br[5]
    if x == 0 or rate <= 0:
        continue
    b = 1.0 / x
    flow_MW = b * (theta.value[f_idx] - theta.value[t_idx]) * baseMVA
    loading_pct = abs(flow_MW) / rate * 100
    if loading_pct >= BINDING_THRESHOLD:
        cf_binding_lines.append({
            "from": int(br[0]),
            "to": int(br[1]),
            "flow_MW": round(float(flow_MW), 2),
            "limit_MW": round(float(rate), 2),
            "loading_pct": round(loading_pct, 1)
        })

target_from = 2
target_to = 5
congestion_relieved = any(
    b["from"] == target_from and b["to"] == target_to for b in base_binding
) and not any(
    b["from"] == target_from and b["to"] == target_to for b in cf_binding_lines
)

print(f"Cost reduction: ${cost_reduction:.2f}")
print(f"LMP changes: {lmp_deltas}")
print(f"Congestion relieved: {congestion_relieved}")
```

#### Economic Intuition

- **Relaxing a binding constraint** cannot increase total cost; it either reduces cost or leaves it unchanged.
- The **shadow price** of the original constraint equals the cost reduction per MW of capacity added.
- Convergence of LMPs after relief indicates diminished congestion and a more uniform price field.

### LMP Sign Convention

For a balance constraint written as `generation - load == net_export`:

- **Positive LMP**: Increasing load at that bus raises total system cost (typical).
- **Negative LMP**: Increasing load *decreases* total cost, often because cheap generation is trapped behind a congested line.

Negative LMPs are physically valid in congested networks and indicate that additional demand can relieve congestion.

## Pitfalls

- **Accessing duals before solve completes**: `dual_value` will be `None` if read before `prob.solve()` finishes. Always check `prob.status` first.
- **Forgetting `baseMVA` conversion**: Duals are in per-unit; without multiplying by `baseMVA`, LMPs will be off by a factor of 100 (or whatever `baseMVA` is).
- **Using `ECOS` for large DC-OPF**: Legacy solvers may produce inaccurate or unstable duals. Use `CLARABEL` v0.7+ or `OSQP` v0.6+.
- **Misinterpreting negative LMPs**: Negative LMPs are physically valid in congested networks; do not treat them as errors.
- **Counterfactual cost increase**: Relaxing a binding constraint must never increase total cost. If `cost_reduction < 0`, the solve likely failed or the wrong constraint was relaxed.
- **Exposing raw dual values via API**: Dual values reveal system operating points. Sanitise outputs and apply access controls before returning LMP data to any client.
- **Sign mismatch with constraint formulation**: If the balance constraint is written as `load - generation == net_import`, the LMP sign flips. Ensure the sign convention matches your formulation.

## Verification

- [ ] Verify that `dual_value` is accessed **only after** `prob.solve()` completes without errors.
- [ ] Confirm that `baseMVA` is applied to the dual value to convert per-unit prices to $/MWh.
- [ ] Check that the sign of each LMP matches the constraint formulation (`generation - load`).
- [ ] Validate that cost reduction is non-negative when relaxing a binding constraint.
- [ ] Ensure the selected solver reports `dual_feasibility` status (e.g., `prob.solver_stats.dual_feasibility`).
- [ ] Run a regression test: compare LMPs against a known benchmark case (e.g., IEEE 14-bus) with tolerance ±1 $/MWh.
- [ ] Perform a security audit: confirm no raw model data is logged or returned in API responses.

## Related Skills

- `dc-power-flow`: Used for calculating line flows and theta values.
- `optimal-power-flow`: The overarching optimization framework for LMPs.
