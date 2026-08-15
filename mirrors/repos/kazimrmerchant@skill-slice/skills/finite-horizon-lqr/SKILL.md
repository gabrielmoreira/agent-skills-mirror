---
name: finite-horizon-lqr
version: 1.2.1
description: "Finite-horizon discrete-time LQR via the backward Riccati recursion, producing the time-varying gain schedule that a single ARE solve cannot. Use when controlling a linear plant x_{k+1} = A x_k + B u_k under a quadratic cost over a fixed N-step horizon — receding-horizon MPC inner loops, finite-time stabilization, terminal-cost design. Not for nonlinear plants (linearize first), continuous-time models (discretize first), pure steady-state regulation (solve the ARE once), or hard input/state constraints (use QP-based MPC)."
category: control-engineering
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
last_updated: 2026-07-01
trigger: "User asks to design or debug a finite-horizon LQR controller, compute time-varying LQR gains, implement a backward Riccati recursion, or build the unconstrained core of a linear MPC (e.g. 'LQR gains for a 50-step horizon', 'my Riccati recursion loses symmetry', 'apply only the first control in the MPC loop')."
action: "Validate (A, B, Q, R, Q_f) shapes and definiteness, run the backward Riccati recursion using Cholesky-based solves and the symmetric (Joseph-form) update, return the full gain schedule and cost-to-go matrices, and apply only the first gain at each receding-horizon step."
exception: "Nonlinear or continuous-time plants fed in without linearization/discretization; treating the u_min/u_max clamp as optimal under binding constraints; forming gains with an explicit matrix inverse instead of a linear solve; rebuilding an N-long gain schedule when the steady-state ARE gain suffices."
not-triggered: "Constrained QP-based MPC formulation, Kalman filter or state-estimator design, system identification, PID tuning, or continuous-time LQR without discretization."
---

# Finite-Horizon LQR for MPC

## When to Use

Reach for this skill when you are controlling a **linear, discrete-time** plant
`x_{k+1} = A x_k + B u_k`, your objective is a **quadratic** cost in state and
input, and you only care about a **finite** number of steps into the future.

The reason finite-horizon LQR matters for Model Predictive Control (MPC) is that
the optimal feedback gain is *time-varying*: near the end of the horizon the
controller "knows" the episode is about to stop, so it behaves differently than
at the start. Solving the finite-horizon problem captures that end-of-horizon
transient exactly, which is what you want for trajectory tracking or
finite-time stabilization. In a receding-horizon MPC loop you re-solve this
problem each timestep from the freshly measured state and apply only the first
control — that is what turns an open-loop optimal plan into closed-loop feedback.

You do not need to write the recursion from scratch in production. `numpy` and
`scipy` cover the linear-algebra primitives and the steady-state ARE solver
(`scipy.linalg.solve_discrete_are`). The hand-rolled recursion below exists so
you understand *what those solvers do* and so you can compute the genuinely
time-varying gains that a single ARE solve does **not** give you.

### Do not use

Skip this approach — or adapt it first — in the following situations, and here is
*why* each one is a problem rather than just a rule:

- **Non-linear plants.** The recursion assumes `x_{k+1} = A x_k + B u_k` holds
  exactly. If your dynamics are non-linear, linearize around the operating point
  or trajectory first (Jacobians of `f(x, u)`), otherwise the gains optimize the
  wrong model and the closed loop can diverge.
- **Truly infinite-horizon / steady-state regulation.** If you regulate to a
  fixed point forever, the time-varying gain converges to a single steady-state
  gain after a few dozen backward steps. Re-deriving an `N`-long schedule wastes
  computation and accumulates round-off; solve the Algebraic Riccati Equation
  (ARE) once with `scipy.linalg.solve_discrete_are` instead — see
  `steady_state_lqr_control` below.
- **Continuous-time plants.** This is a *discrete-time* recursion. Feeding it a
  continuous `(A, B)` gives meaningless gains. Discretize first with, e.g.,
  `scipy.signal.cont2discrete((A, B, C, D), dt)` (or `control.sample_system` if
  you already use the `python-control` package), then apply this skill.
- **Hard input/state constraints.** Plain LQR is unconstrained. Clipping the LQR
  output (shown in `mpc_step`) is only a safety clamp and is *not* optimal under
  active constraints — a saturated LQR move can violate stability guarantees. For
  real actuator/state limits use a QP-based MPC (e.g. `cvxpy`, `osqp`, or
  `do-mpc`).

## Prerequisites

- **Python 3.10+** with `numpy`, `scipy`, and `pytest` installed.
- On Windows (primary host, PowerShell):

  ```powershell
  pip install numpy scipy pytest
  ```

- On Linux/macOS:

  ```bash
  pip install numpy scipy pytest
  ```

- The reference implementation is self-contained — no optional dependencies
  beyond `numpy` and `scipy`.

## Procedure

### 1. Problem formulation

Minimize the quadratic cost over an `N`-step horizon

```
J = Σ_{k=0}^{N-1} ( xₖᵀ Q xₖ + uₖᵀ R uₖ )  +  x_Nᵀ Q_f x_N
```

subject to the linear dynamics `xₖ₊₁ = A xₖ + B uₖ`, where:

- `Q` (state weight) is symmetric positive **semi**-definite,
- `R` (input weight) is symmetric positive **definite** (this is what makes
  `R + Bᵀ P B` invertible at every step),
- `Q_f` (terminal weight) is symmetric positive semi-definite; defaulting it to
  `Q` is common, but setting it to the ARE solution makes the finite-horizon
  controller agree with the infinite-horizon one at the start of the horizon.

### 2. Backward Riccati recursion

Dynamic programming solves this *backward in time* because the cost-to-go at step
`k` depends on the optimal cost-to-go at step `k+1`. Initialize the terminal
cost-to-go `P_N = Q_f`, then for `k = N-1` down to `0`:

```python
# S is symmetric positive definite, so solve (don't invert) with a Cholesky path.
S   = R + B.T @ P_next @ B
K_k = scipy.linalg.solve(S, B.T @ P_next @ A, assume_a="pos")

# Joseph (symmetric) form of the cost-to-go update — numerically robust.
closed_loop = A - B @ K_k
P_k = Q + K_k.T @ R @ K_k + closed_loop.T @ P_next @ closed_loop
```

`K_0` (computed last) is the gain you apply to the current state; `K_{N-1}`
(computed first) is the end-of-horizon gain.

### 3. Forward simulation

Once the gain schedule exists, roll the closed loop forward from `x_0`:

```python
u_k     = -K_k @ x_k
x_{k+1} =  A @ x_k + B @ u_k
```

### 4. MPC application (receding horizon)

At each control instant:

1. Measure the current state `x`.
2. Solve the finite-horizon LQR problem starting from `x`.
3. Apply **only** the first control `u_0 = -K_0 @ x`.
4. Discard the rest of the plan and repeat at the next timestep.

Re-solving every step is what gives MPC its feedback and disturbance-rejection
properties: each new measurement corrects for model error and unmeasured
disturbances.

### 5. Reference implementation

The module below is self-contained and runnable with only `numpy` and `scipy`.
It uses explicit `numpy` typing aliases (no `Any`), validates every argument,
and wraps the linear solve in defensive error handling so failures report
*which* Riccati step broke and *why*.

Save this as `finite_horizon_lqr.py` in your project's `scripts/` directory:

```python
"""finite_horizon_lqr.py — finite-horizon discrete-time LQR for MPC."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from numpy.linalg import LinAlgError
from scipy.linalg import solve, solve_discrete_are

# Explicit aliases keep every signature concrete and avoid `Any`.
FloatMatrix = npt.NDArray[np.float64]
FloatVector = npt.NDArray[np.float64]


@dataclass(frozen=True)
class LQRSolution:
    """Output of the backward Riccati recursion.

    Attributes:
        gains:      Stacked feedback gains, shape (N, nu, nx).
                    gains[k] is K_k, the optimal gain at step k.
        cost_to_go: Stacked cost-to-go matrices, shape (N + 1, nx, nx).
                    cost_to_go[k] is P_k; cost_to_go[N] is the terminal weight.
    """

    gains: FloatMatrix
    cost_to_go: FloatMatrix


def _as_float_matrix(
    name: str,
    matrix: npt.ArrayLike,
    *,
    expected_shape: tuple[int, int] | None = None,
) -> FloatMatrix:
    """Coerce input to a finite 2-D float64 matrix, with clear error messages."""
    arr = np.asarray(matrix, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"{name} must be a 2-D matrix, got ndim={arr.ndim}, shape={arr.shape}.")
    if expected_shape is not None and arr.shape != expected_shape:
        raise ValueError(f"{name} must have shape {expected_shape}, got {arr.shape}.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite entries (NaN or inf).")
    return arr


def _check_symmetric(name: str, matrix: FloatMatrix, *, tol: float = 1e-8) -> None:
    asymmetry = float(np.max(np.abs(matrix - matrix.T)))
    if asymmetry > tol:
        raise ValueError(f"{name} must be symmetric; max |M - Mᵀ| = {asymmetry:.2e} > {tol:.0e}.")


def _check_positive_semidefinite(name: str, matrix: FloatMatrix, *, tol: float = 1e-8) -> None:
    # eigvalsh is exact for symmetric matrices; the smallest eigenvalue gives definiteness.
    min_eig = float(np.min(np.linalg.eigvalsh(matrix)))
    if min_eig < -tol:
        raise ValueError(f"{name} must be positive semi-definite; min eigenvalue = {min_eig:.2e}.")


def _check_positive_definite(name: str, matrix: FloatMatrix, *, tol: float = 1e-8) -> None:
    min_eig = float(np.min(np.linalg.eigvalsh(matrix)))
    if min_eig <= tol:
        raise ValueError(f"{name} must be positive definite; min eigenvalue = {min_eig:.2e}.")


def solve_finite_horizon_lqr(
    A: npt.ArrayLike,
    B: npt.ArrayLike,
    Q: npt.ArrayLike,
    R: npt.ArrayLike,
    N: int,
    *,
    terminal_cost: npt.ArrayLike | None = None,
) -> LQRSolution:
    """Compute the time-varying optimal gains via the backward Riccati recursion.

    Args:
        A: State matrix, shape (nx, nx).
        B: Input matrix, shape (nx, nu).
        Q: State weight, symmetric PSD, shape (nx, nx).
        R: Input weight, symmetric PD, shape (nu, nu).
        N: Horizon length (positive integer).
        terminal_cost: Optional terminal weight Q_f, symmetric PSD, shape (nx, nx).
                       Defaults to Q.

    Returns:
        LQRSolution with the gain schedule and cost-to-go matrices.

    Raises:
        ValueError:   On malformed or mis-shaped inputs, or violated definiteness.
        LinAlgError:  If (R + Bᵀ P B) is singular at some recursion step.
    """
    if not isinstance(N, (int, np.integer)) or int(N) < 1:
        raise ValueError(f"Horizon N must be a positive integer, got {N!r}.")
    N = int(N)

    A_mat = _as_float_matrix("A", A)
    nx = A_mat.shape[0]
    if A_mat.shape[1] != nx:
        raise ValueError(f"A must be square (nx, nx); got {A_mat.shape}.")

    B_mat = _as_float_matrix("B", B)
    if B_mat.shape[0] != nx:
        raise ValueError(f"B must have {nx} rows to match A; got {B_mat.shape}.")
    nu = B_mat.shape[1]

    Q_mat = _as_float_matrix("Q", Q, expected_shape=(nx, nx))
    R_mat = _as_float_matrix("R", R, expected_shape=(nu, nu))
    _check_symmetric("Q", Q_mat)
    _check_positive_semidefinite("Q", Q_mat)
    _check_symmetric("R", R_mat)
    _check_positive_definite("R", R_mat)  # PD guarantees (R + Bᵀ P B) stays invertible.

    if terminal_cost is None:
        P_terminal = Q_mat.copy()
    else:
        P_terminal = _as_float_matrix("terminal_cost", terminal_cost, expected_shape=(nx, nx))
        _check_symmetric("terminal_cost", P_terminal)
        _check_positive_semidefinite("terminal_cost", P_terminal)

    gains = np.zeros((N, nu, nx), dtype=np.float64)
    cost_to_go = np.zeros((N + 1, nx, nx), dtype=np.float64)
    cost_to_go[N] = P_terminal

    for k in range(N - 1, -1, -1):
        P_next = cost_to_go[k + 1]
        S = R_mat + B_mat.T @ P_next @ B_mat  # symmetric positive definite by construction
        rhs = B_mat.T @ P_next @ A_mat
        try:
            K_k = solve(S, rhs, assume_a="pos")  # Cholesky solve; never explicit inverse
        except LinAlgError as exc:
            raise LinAlgError(
                f"Riccati step k={k} failed: (R + Bᵀ P B) is singular or ill-conditioned."
            ) from exc

        closed_loop = A_mat - B_mat @ K_k
        # Joseph (symmetric) form: keeps P_k symmetric PSD despite floating-point round-off.
        P_k = Q_mat + K_k.T @ R_mat @ K_k + closed_loop.T @ P_next @ closed_loop
        P_k = 0.5 * (P_k + P_k.T)  # scrub residual asymmetry

        gains[k] = K_k
        cost_to_go[k] = P_k

    return LQRSolution(gains=gains, cost_to_go=cost_to_go)


def first_control(solution: LQRSolution, x: npt.ArrayLike) -> FloatVector:
    """Return u_0 = -K_0 @ x, the control to apply in the current MPC step."""
    K0 = solution.gains[0]
    nx = K0.shape[1]
    x_vec = np.asarray(x, dtype=np.float64).reshape(-1)
    if x_vec.shape[0] != nx:
        raise ValueError(f"State x must have length {nx}, got {x_vec.shape[0]}.")
    if not np.all(np.isfinite(x_vec)):
        raise ValueError("State x contains non-finite entries (NaN or inf).")
    return -K0 @ x_vec


def simulate(
    A: npt.ArrayLike,
    B: npt.ArrayLike,
    solution: LQRSolution,
    x0: npt.ArrayLike,
) -> tuple[FloatMatrix, FloatMatrix]:
    """Roll the closed loop forward using the full time-varying gain schedule.

    Returns:
        states:   shape (N + 1, nx), states[0] == x0.
        controls: shape (N, nu).
    """
    B_mat = _as_float_matrix("B", B)
    nx, nu = B_mat.shape
    A_mat = _as_float_matrix("A", A, expected_shape=(nx, nx))

    x_vec = np.asarray(x0, dtype=np.float64).reshape(-1)
    if x_vec.shape[0] != nx:
        raise ValueError(f"x0 must have length {nx}, got {x_vec.shape[0]}.")

    horizon = solution.gains.shape[0]
    states = np.zeros((horizon + 1, nx), dtype=np.float64)
    controls = np.zeros((horizon, nu), dtype=np.float64)
    states[0] = x_vec
    for k in range(horizon):
        u = -solution.gains[k] @ states[k]
        controls[k] = u
        states[k + 1] = A_mat @ states[k] + B_mat @ u
    return states, controls


def mpc_step(
    A: npt.ArrayLike,
    B: npt.ArrayLike,
    Q: npt.ArrayLike,
    R: npt.ArrayLike,
    N: int,
    x: npt.ArrayLike,
    *,
    u_min: npt.ArrayLike | None = None,
    u_max: npt.ArrayLike | None = None,
    terminal_cost: npt.ArrayLike | None = None,
) -> FloatVector:
    """One receding-horizon step: solve, take the first move, clamp to limits.

    NOTE: clamping is a *safety clamp only*. Under active constraints it is not
    optimal — use a QP-based MPC if your limits bind frequently.
    """
    solution = solve_finite_horizon_lqr(A, B, Q, R, N, terminal_cost=terminal_cost)
    u = first_control(solution, x)
    if u_min is not None or u_max is not None:
        lower = -np.inf if u_min is None else np.asarray(u_min, dtype=np.float64).reshape(-1)
        upper = np.inf if u_max is None else np.asarray(u_max, dtype=np.float64).reshape(-1)
        u = np.clip(u, lower, upper)
    return u


def steady_state_lqr_control(
    A: npt.ArrayLike,
    B: npt.ArrayLike,
    Q: npt.ArrayLike,
    R: npt.ArrayLike,
    x: npt.ArrayLike,
) -> FloatVector:
    """Infinite-horizon (steady-state) LQR control via the discrete ARE.

    This is the N -> infinity limit of the finite-horizon gain, so it ignores any
    horizon length: use it when the horizon is long enough that the end-of-horizon
    transient is negligible. `scipy.linalg.solve_discrete_are` returns the Riccati
    solution X directly — no optional dependencies required.
    """
    A_mat = _as_float_matrix("A", A)
    nx = A_mat.shape[0]
    if A_mat.shape[1] != nx:
        raise ValueError(f"A must be square (nx, nx); got {A_mat.shape}.")
    B_mat = _as_float_matrix("B", B)
    if B_mat.shape[0] != nx:
        raise ValueError(f"B must have {nx} rows to match A; got {B_mat.shape}.")

    Q_mat = _as_float_matrix("Q", Q, expected_shape=(nx, nx))
    R_mat = _as_float_matrix("R", R, expected_shape=(B_mat.shape[1], B_mat.shape[1]))
    _check_symmetric("Q", Q_mat)
    _check_positive_semidefinite("Q", Q_mat)
    _check_symmetric("R", R_mat)
    _check_positive_definite("R", R_mat)

    X = solve_discrete_are(A_mat, B_mat, Q_mat, R_mat)
    K_inf = solve(R_mat + B_mat.T @ X @ B_mat, B_mat.T @ X @ A_mat, assume_a="pos")

    x_vec = np.asarray(x, dtype=np.float64).reshape(-1)
    if x_vec.shape[0] != nx:
        raise ValueError(f"State x must have length {nx}, got {x_vec.shape[0]}.")
    return -K_inf @ x_vec


if __name__ == "__main__":
    # Double integrator (position/velocity) discretized at dt = 0.1 s.
    dt = 0.1
    A = np.array([[1.0, dt], [0.0, 1.0]])
    B = np.array([[0.5 * dt**2], [dt]])
    Q = np.diag([10.0, 1.0])  # penalize position error 10x more than velocity
    R = np.array([[0.1]])     # cheap control effort
    N = 50
    x0 = np.array([1.0, 0.0])

    solution = solve_finite_horizon_lqr(A, B, Q, R, N)
    states, controls = simulate(A, B, solution, x0)

    print(f"Initial state : {x0}")
    print(f"Final state   : {states[-1]}    (should be near the origin)")
    print(f"First control : {controls[0]}")
    print(f"Gain K_0      : {solution.gains[0]}")
```

## Examples

### Quick smoke test (Windows PowerShell)

From the directory where you saved the module:

```powershell
python finite_horizon_lqr.py
```

Expected output (abbreviated):

```
Initial state : [1. 0.]
Final state   : [~0.0 ~0.0]    (should be near the origin)
First control : [~-2.4...]
Gain K_0      : [[~-2.4 ...]]
```

### Quick smoke test (Linux/macOS)

From the directory where you saved the module:

```bash
python finite_horizon_lqr.py
```

## Pitfalls

These produce wrong or drifting gains even on perfectly valid problems:

1. **Never invert matrices explicitly** (`np.linalg.inv`) to form the gain. Solve
   the linear system `(R + Bᵀ P B) K = Bᵀ P A` instead — it is faster and far more
   numerically stable. Because `R + Bᵀ P B` is symmetric positive definite, pass
   `assume_a="pos"` to `scipy.linalg.solve` so it uses a Cholesky-based solver.
   (The legacy `sym_pos=True` flag was deprecated in SciPy 1.9 and removed in
   SciPy 1.11; `assume_a="pos"` is the only supported spelling.)

2. **Guard the cost-to-go matrix against drift.** Use the symmetric "Joseph" form
   of the Riccati update and re-symmetrize `P` each step. The textbook
   `P = Q + Aᵀ P (A − B K)` form is algebraically correct but can lose symmetry to
   round-off over long horizons; the symmetric form stays positive
   semi-definite by construction.

3. **Do not treat the `u_min`/`u_max` clamp as optimal.** The `mpc_step` function
   clips the LQR output as a safety measure only. Under active constraints,
   clipping is *not* optimal and can violate stability guarantees. Use a
   QP-based MPC (e.g. `cvxpy`, `osqp`, or `do-mpc`) when actuator or state limits
   bind frequently.

4. **Do not feed continuous-time `(A, B)` matrices.** This is a discrete-time
   recursion. Discretize first with `scipy.signal.cont2discrete` or
   `control.sample_system`.

5. **Do not rebuild an `N`-long gain schedule when the steady-state ARE gain
   suffices.** For long horizons on stabilizable systems, `K_0` converges to the
   ARE gain. Solve the ARE once with `scipy.linalg.solve_discrete_are` and use
   `steady_state_lqr_control` instead.

6. **Do not apply the full gain schedule open-loop.** In receding-horizon MPC,
   apply only `u_0 = -K_0 @ x` at each step, then re-solve from the new measured
   state. Applying the entire schedule open-loop eliminates feedback and
   disturbance rejection.

## Verification

Each check below targets a specific failure mode; the reasoning is given so you
know what a failure actually tells you.

- [ ] **Gain converges to the steady state.** For a stabilizable system the
      earliest gain `K_0` over a long horizon should match the ARE gain. If it
      does not, your recursion indexing or terminal cost is wrong.
- [ ] **Closed loop is stable on a known plant.** Simulate the double integrator
      (or an inverted pendulum) from a non-zero state; the trajectory must decay
      toward the origin. Divergence means the gains do not stabilize `A − B K`.
- [ ] **Bad inputs are rejected.** A non-positive-definite `R` or mis-shaped
      matrix must raise `ValueError` *before* any linear algebra runs — silent
      acceptance hides modeling bugs.
- [ ] **Controls respect actuator limits.** When you wrap `mpc_step` with
      `u_min`/`u_max`, confirm the returned control is clamped, and remember the
      clamp is not optimal under binding constraints.

### Test suite

Save the following as `test_finite_horizon_lqr.py` next to the module:

```python
import numpy as np
import pytest

from finite_horizon_lqr import (
    solve_finite_horizon_lqr,
    simulate,
    steady_state_lqr_control,
)


def _double_integrator(dt: float = 0.1):
    A = np.array([[1.0, dt], [0.0, 1.0]])
    B = np.array([[0.5 * dt**2], [dt]])
    Q = np.diag([10.0, 1.0])
    R = np.array([[0.1]])
    return A, B, Q, R


def test_gain_converges_to_steady_state():
    A, B, Q, R = _double_integrator()
    sol = solve_finite_horizon_lqr(A, B, Q, R, N=200)
    x_probe = np.array([1.0, 0.0])
    u_finite = -sol.gains[0] @ x_probe              # earliest gain, far from horizon end
    u_infinite = steady_state_lqr_control(A, B, Q, R, x_probe)
    np.testing.assert_allclose(u_finite, u_infinite, rtol=1e-4, atol=1e-6)


def test_closed_loop_is_stable():
    A, B, Q, R = _double_integrator()
    sol = solve_finite_horizon_lqr(A, B, Q, R, N=100)
    states, _ = simulate(A, B, sol, x0=np.array([1.0, 0.0]))
    assert np.linalg.norm(states[-1]) < 1e-2       # converged to the origin


def test_rejects_non_positive_definite_R():
    A, B, Q, _ = _double_integrator()
    bad_R = np.array([[0.0]])                       # min eigenvalue 0 -> not PD
    with pytest.raises(ValueError):
        solve_finite_horizon_lqr(A, B, Q, bad_R, N=10)


def test_rejects_mismatched_shapes():
    A, B, Q, R = _double_integrator()
    wrong_B = np.array([[1.0, 0.0]])                # shape (1, 2): rows != nx
    with pytest.raises(ValueError):
        solve_finite_horizon_lqr(A, wrong_B, Q, R, N=10)
```

### Run the validation commands

**Windows (PowerShell):**

```powershell
pip install numpy scipy pytest
python -m pytest test_finite_horizon_lqr.py -v
```

**Linux/macOS:**

```bash
pip install numpy scipy pytest
pytest test_finite_horizon_lqr.py -v
```

Expected output (abbreviated):

```
test_finite_horizon_lqr.py::test_gain_converges_to_steady_state PASSED
test_finite_horizon_lqr.py::test_closed_loop_is_stable PASSED
test_finite_horizon_lqr.py::test_rejects_non_positive_definite_R PASSED
test_finite_horizon_lqr.py::test_rejects_mismatched_shapes PASSED
```

## Related skills

- Infinite-horizon LQR (steady-state regulation via the ARE)
- Algebraic Riccati Equation (ARE) solvers (`scipy.linalg.solve_discrete_are`)
- Model Predictive Control (MPC), including constrained QP-based MPC
- Kalman filtering (the dual estimation problem; pairs with LQR to form LQG)
