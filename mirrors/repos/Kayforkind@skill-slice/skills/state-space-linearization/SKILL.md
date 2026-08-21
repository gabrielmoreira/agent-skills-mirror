---
name: state-space-linearization
version: 1.2.1
description: "Linearizes nonlinear plants to local (A,B) via Jacobian or autodiff, then ZOH/Tustin discretize for LTI design. Use when a nonlinear model must feed LQR, MPC, Kalman, or gain scheduling. Not for finite-horizon LQR itself (finite-horizon-lqr), hard discontinuities, or naive Euler on stiff dynamics."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# State-Space Linearization

## Overview

This skill bridges nonlinear physics and the linear time-invariant (LTI) control toolbox. Given a nonlinear plant — continuous-time $\dot{x} = f(x, u)$ or discrete-time $x_{k+1} = f(x_k, u_k)$ — you compute local linear approximations $(A, B)$ about an operating point $(x_0, u_0)$ so that mature tools (LQR, pole placement, PID tuning, MPC, Kalman filtering) can be applied. The linearization is valid in a neighborhood of the operating point; a working controller actively keeps the system there.

## When to Use

Use this skill when **any** of the following apply:

- You have a nonlinear plant model and want to design a controller with LQR, pole placement, PID, MPC, or Kalman filtering.
- You need discrete-time $(A_d, B_d)$ matrices from a continuous-time $(A_c, B_c)$ model for digital controller implementation.
- You are gain-scheduling across multiple operating points and need a linear model at each.
- You need to verify stability of a linearized or discretized system before handing it to a controller-design routine.

**Trigger keywords:** linearize, Jacobian, operating point, equilibrium, discretize, ZOH, Tustin, bilinear, state-space, A matrix, B matrix, LTI, LQR, MPC, Kalman, gain scheduling, LPV, roll-to-roll, web handling, R2R.

## Do Not Use

Each of these is a case where the local-linear assumption breaks:

- **Dominant or non-smooth nonlinearity.** Hard discontinuities, saturation, backlash, Coulomb friction, or high-frequency switching have no meaningful single derivative at the kink. Prefer hybrid/switched models, describing functions, or sliding-mode control.
- **Fast-moving operating points.** A static $(A, B)$ pair is only accurate near the single point it was computed at. If the operating point slews quickly (robot arm sweeping workspace, engine across rev range), use a Linear Parameter-Varying (LPV) model or gain scheduling.
- **Naive Euler discretization of stiff/fast dynamics.** Forward Euler's stability region is a small disk in the complex plane. Fast modes or large $T_s$ push discrete eigenvalues outside that disk, causing numerical divergence even when the continuous model is stable. Use exact ZOH or Tustin instead.
- **Stale library versions.** Pin to current maintained releases of NumPy, SciPy, SymPy (and JAX/PyTorch if you autodiff). Older versions carry known numerical bugs and removed APIs (`numpy.matrix` is deprecated; `scipy.linalg` exponential routines have been hardened over time).
- **Unvalidated external parameters and sensor data.** A single `NaN`, `Inf`, or out-of-range value silently corrupts every downstream eigenvalue. Validate that every parameter is finite and within physical bounds *before* it reaches the linear algebra. If values arrive over a web boundary, apply transport-layer sanitation too — but the control-relevant risk is malformed numerics, not markup injection.

## Prerequisites

### Python environment

```powershell
# Windows PowerShell — create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Pin to current maintained releases
pip install "numpy>=2.0" "scipy>=1.13" "sympy>=1.13"
# Optional: for autodiff-based Jacobians
pip install "jax>=0.4.30" "jaxlib>=0.4.30"
```

### Hard rules

1. **Never skip the finite-check.** Every entry point must reject `NaN`/`Inf` in states, inputs, parameters, and dynamics outputs before any matrix operation.
2. **Never use forward Euler for stiff systems.** Use ZOH (for plants) or Tustin (for controllers/filters).
3. **Never use the inverse-based ZOH formula** $B_d = A_c^{-1}(A_d - I)B_c$ when $A_c$ may be singular (e.g., pure integrators). Use the Van Loan block-matrix construction.
4. **Never mix stability tests.** Continuous: $\operatorname{Re}(\lambda) < 0$. Discrete: $|\lambda| < 1$.
5. **Never linearize about a non-equilibrium point without acknowledging the affine term.** If $f(x_0, u_0) \neq 0$, the true linearized model is $\Delta\dot{x} = A\Delta x + B\Delta u + f(x_0, u_0)$; the pure $(A, B)$ form silently drops the constant.
6. **Never delete or overwrite calibrated parameter sets mid-design.** Use frozen dataclasses.
7. **Always state the validity region.** A linear model is trustworthy only within roughly $\pm 10\text{–}20\%$ of the operating point. Document it.

### Worked checks in this file

This folder ships `SKILL.md` only. Use the inline `linearize` / `discretize_*` / stability helpers above, the pendulum and R2R examples, and the four Verification checks below. Do not look for companion scripts in this folder.

## Procedure

### Step 1 — Define the nonlinear dynamics and operating point

Write the dynamics as a callable $f(x, u) \to \dot{x}$ (continuous) or $f(x_k, u_k) \to x_{k+1}$ (discrete). Identify the operating point $(x_0, u_0)$.

**Verify the operating point is an equilibrium** (for continuous-time): confirm $f(x_0, u_0) \approx 0$. If it is not, the linearization will have an affine term that the pure $(A, B)$ form drops.

### Step 2 — Compute the Jacobians $(A, B)$

The linearization about $(x_0, u_0)$ with $\Delta x = x - x_0$, $\Delta u = u - u_0$:

$$\Delta \dot{x} \approx A\,\Delta x + B\,\Delta u, \qquad
A = \left.\frac{\partial f}{\partial x}\right|_{(x_0, u_0)}, \qquad
B = \left.\frac{\partial f}{\partial u}\right|_{(x_0, u_0)}.$$

**Preference order:**

1. **Symbolic** (SymPy) — for closed-form models you control. No truncation error, no transcription error if you let SymPy differentiate.
2. **Autodiff** (JAX/PyTorch) — for complex differentiable models. Machine precision, no step-size tuning.
3. **Finite differences** (central) — fallback for black-box callables only.

#### Finite-difference linearization (fallback for black-box dynamics)

```python
from __future__ import annotations

from typing import Callable

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]
DynamicsFn = Callable[[FloatArray, FloatArray], FloatArray]


def _as_float_vector(value: npt.ArrayLike, name: str) -> FloatArray:
    """Coerce value to a 1-D float64 vector and reject non-finite data."""
    arr = np.asarray(value, dtype=np.float64).reshape(-1)
    if arr.size == 0:
        raise ValueError(f"{name} must contain at least one element.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains NaN or Inf; refusing to linearize.")
    return arr


def linearize(
    f: DynamicsFn,
    x0: npt.ArrayLike,
    u0: npt.ArrayLike,
    *,
    rel_step: float = 1e-6,
) -> tuple[FloatArray, FloatArray]:
    """Numerically linearize f about (x0, u0) via central differences.

    Returns (A, B) with shapes (n, n) and (n, m). Central differences have
    O(h^2) truncation error vs O(h) for one-sided. Per-coordinate step h is
    scaled by the magnitude of that coordinate.
    """
    x = _as_float_vector(x0, "x0")
    u = _as_float_vector(u0, "u0")
    if not (np.isfinite(rel_step) and rel_step > 0.0):
        raise ValueError(f"rel_step must be positive and finite; got {rel_step!r}.")

    f0 = np.asarray(f(x, u), dtype=np.float64).reshape(-1)
    if not np.all(np.isfinite(f0)):
        raise ValueError("f(x0, u0) returned NaN or Inf; check the model at the operating point.")
    n = f0.size

    A = np.zeros((n, x.size), dtype=np.float64)
    for j in range(x.size):
        h = rel_step * max(1.0, abs(x[j]))
        x_plus = x.copy(); x_plus[j] += h
        x_minus = x.copy(); x_minus[j] -= h
        f_plus = np.asarray(f(x_plus, u), dtype=np.float64).reshape(-1)
        f_minus = np.asarray(f(x_minus, u), dtype=np.float64).reshape(-1)
        A[:, j] = (f_plus - f_minus) / (2.0 * h)

    B = np.zeros((n, u.size), dtype=np.float64)
    for j in range(u.size):
        h = rel_step * max(1.0, abs(u[j]))
        u_plus = u.copy(); u_plus[j] += h
        u_minus = u.copy(); u_minus[j] -= h
        f_plus = np.asarray(f(x, u_plus), dtype=np.float64).reshape(-1)
        f_minus = np.asarray(f(x, u_minus), dtype=np.float64).reshape(-1)
        B[:, j] = (f_plus - f_minus) / (2.0 * h)

    if not (np.all(np.isfinite(A)) and np.all(np.isfinite(B))):
        raise ValueError("Computed Jacobian is non-finite; the model may be discontinuous here.")
    return A, B
```

#### JAX autodiff linearization (preferred for differentiable models)

```python
import jax
import jax.numpy as jnp
from jax import Array
from typing import Callable

# Control models need float64; JAX defaults to float32.
jax.config.update("jax_enable_x64", True)

JaxDynamicsFn = Callable[[Array, Array], Array]


def linearize_jax(
    f: JaxDynamicsFn,
    x0: npt.ArrayLike,
    u0: npt.ArrayLike,
) -> tuple[Array, Array]:
    """Machine-precision Jacobians (A, B) via JAX autodiff.

    f must be written with jax.numpy so it is differentiable.
    """
    x = jnp.asarray(x0, dtype=jnp.float64)
    u = jnp.asarray(u0, dtype=jnp.float64)
    if x.ndim != 1 or u.ndim != 1:
        raise ValueError(f"x0 and u0 must be 1-D vectors; got shapes {x.shape} and {u.shape}.")

    A = jax.jacobian(f, argnums=0)(x, u)
    B = jax.jacobian(f, argnums=1)(x, u)
    return A, B
```

### Step 3 — Discretize (if implementing a digital controller)

A digital controller updates at fixed $T_s$, so you need discrete $(A_d, B_d)$ with $x_{k+1} = A_d x_k + B_d u_k$.

**Which method to pick:**

| Method | Use for | Why |
|---|---|---|
| ZOH | Plant discretization | Exact when input is held constant between samples (DAC behavior) |
| Tustin | Controller/filter discretization | Preserves stability for any $T_s$; maps imaginary axis to unit circle |

#### Zero-order hold via Van Loan block matrix (recommended)

```python
from scipy.linalg import expm


def discretize_zoh(
    A_c: npt.ArrayLike,
    B_c: npt.ArrayLike,
    T_s: float,
) -> tuple[FloatArray, FloatArray]:
    """Exact ZOH discretization using the Van Loan block-matrix construction.

    The block construction:
        expm([[A_c, B_c], [0, 0]] * T_s) == [[A_d, B_d], [0, I]]
    computes the exact integral B_d = (integral_0^{T_s} e^{A_c tau} d tau) B_c
    directly and stays valid whether or not A_c is invertible.
    """
    A_c = np.asarray(A_c, dtype=np.float64)
    B_c = np.asarray(B_c, dtype=np.float64)
    if A_c.ndim != 2 or A_c.shape[0] != A_c.shape[1]:
        raise ValueError(f"A_c must be square (n x n); got shape {A_c.shape}.")
    n = A_c.shape[0]
    if B_c.ndim != 2 or B_c.shape[0] != n:
        raise ValueError(f"B_c must have shape ({n}, m) to match A_c; got {B_c.shape}.")
    if not (np.isfinite(T_s) and T_s > 0.0):
        raise ValueError(f"Sampling period T_s must be positive and finite; got {T_s!r}.")
    if not (np.all(np.isfinite(A_c)) and np.all(np.isfinite(B_c))):
        raise ValueError("A_c / B_c contain NaN or Inf.")

    m = B_c.shape[1]
    block = np.zeros((n + m, n + m), dtype=np.float64)
    block[:n, :n] = A_c
    block[:n, n:] = B_c
    phi = expm(block * T_s)
    A_d = np.ascontiguousarray(phi[:n, :n])
    B_d = np.ascontiguousarray(phi[:n, n:])
    return A_d, B_d
```

#### Tustin (bilinear) transformation

```python
def discretize_tustin(
    A_c: npt.ArrayLike,
    B_c: npt.ArrayLike,
    T_s: float,
    *,
    cond_limit: float = 1e12,
) -> tuple[FloatArray, FloatArray]:
    """Tustin discretization with an explicit conditioning guard.

    With M = (I - (T_s/2) A_c)^{-1}:
        A_d = M (I + (T_s/2) A_c)
        B_d = T_s * (M @ B_c)

    Note: B_d scaling is T_s, NOT T_s/2. The factor of T_s makes the discrete
    DC gain equal the continuous DC gain. Using T_s/2 halves the steady-state
    response — a common, hard-to-spot bug.

    The inversion blows up when 2/T_s coincides with an eigenvalue of A_c.
    """
    A_c = np.asarray(A_c, dtype=np.float64)
    B_c = np.asarray(B_c, dtype=np.float64)
    if A_c.ndim != 2 or A_c.shape[0] != A_c.shape[1]:
        raise ValueError(f"A_c must be square (n x n); got shape {A_c.shape}.")
    n = A_c.shape[0]
    if B_c.ndim != 2 or B_c.shape[0] != n:
        raise ValueError(f"B_c must have shape ({n}, m) to match A_c; got {B_c.shape}.")
    if not (np.isfinite(T_s) and T_s > 0.0):
        raise ValueError(f"Sampling period T_s must be positive and finite; got {T_s!r}.")
    if not (np.isfinite(cond_limit) and cond_limit > 0.0):
        raise ValueError(f"cond_limit must be positive and finite; got {cond_limit!r}.")

    eye = np.eye(n, dtype=np.float64)
    p_matrix = eye - (T_s / 2.0) * A_c
    cond = float(np.linalg.cond(p_matrix))
    if not np.isfinite(cond) or cond > cond_limit:
        raise ValueError(
            f"(I - T_s/2 * A_c) is near-singular (cond={cond:.3e}); "
            f"2/T_s is colliding with an eigenvalue of A_c. Reduce T_s."
        )

    m_matrix = np.linalg.inv(p_matrix)
    A_d = m_matrix @ (eye + (T_s / 2.0) * A_c)
    B_d = T_s * (m_matrix @ B_c)
    return A_d, B_d
```

### Step 4 — Check stability

Run the time-domain-appropriate test. Mixing these is a frequent error.

```python
def is_continuous_stable(A_c: npt.ArrayLike, *, margin: float = 0.0) -> bool:
    """True iff every eigenvalue of A_c has real part < -margin (Hurwitz)."""
    if not (np.isfinite(margin) and margin >= 0.0):
        raise ValueError(f"margin must be non-negative and finite; got {margin!r}.")
    eigenvalues = np.linalg.eigvals(np.asarray(A_c, dtype=np.float64))
    return bool(np.all(eigenvalues.real < -margin))


def is_discrete_stable(A_d: npt.ArrayLike, *, margin: float = 0.0) -> bool:
    """True iff every eigenvalue of A_d lies inside the unit circle (Schur)."""
    if not (0.0 <= margin < 1.0) or not np.isfinite(margin):
        raise ValueError(f"margin must be in [0, 1); got {margin!r}.")
    eigenvalues = np.linalg.eigvals(np.asarray(A_d, dtype=np.float64))
    return bool(np.all(np.abs(eigenvalues) < 1.0 - margin))
```

### Step 5 — Document the validity region

State explicitly the range of states and inputs over which the linear model is trustworthy (commonly $\pm 10\text{–}20\%$ of the operating point). This tells the next engineer — and gain-scheduling logic — when to switch models.

## Examples

### Example 1: Pendulum linearization via SymPy

The downward position ($\theta = 0$) is the **stable** equilibrium. Eigenvalues come out purely imaginary, $\pm j\sqrt{g/l}$, which is why an undamped pendulum oscillates forever — you must add damping or feedback before this model is useful for control.

```python
from __future__ import annotations
import sympy as sp


def pendulum_linearization() -> sp.Matrix:
    """Return the symbolic A matrix of a simple pendulum at theta = 0.

    Dynamics: theta_dot = omega,  omega_dot = -(g/l) sin(theta).
    Linearizing sin(theta) ~= theta at the origin yields [[0, 1], [-g/l, 0]].
    """
    theta, omega, g, length = sp.symbols("theta omega g l", real=True)
    if length == 0:
        raise ValueError("Pendulum length 'l' must be nonzero.")

    state = sp.Matrix([theta, omega])
    f = sp.Matrix([omega, -(g / length) * sp.sin(theta)])

    equilibrium = {theta: 0, omega: 0}
    if f.subs(equilibrium) != sp.zeros(2, 1):
        raise ValueError("theta = 0, omega = 0 is not an equilibrium of this model.")

    A_sym = sp.simplify(f.jacobian(state).subs(equilibrium))
    return A_sym


if __name__ == "__main__":
    A_matrix = pendulum_linearization()
    print(f"Linearized A matrix:\n{A_matrix}")
    # Linearized A matrix:
    # Matrix([[0, 1], [-g/l, 0]])
```

### Example 2: ZOH discretization with stability gate

```python
from __future__ import annotations
import numpy as np

# A_c: stable continuous system, eigenvalues at s = -1 and s = -2.
A_c = np.array([[0.0, 1.0], [-2.0, -3.0]], dtype=np.float64)
B_c = np.array([[0.0], [1.0]], dtype=np.float64)
T_s = 0.01

A_d, B_d = discretize_zoh(A_c, B_c, T_s)

if not is_discrete_stable(A_d):
    raise RuntimeError(
        "Discretized system is unstable; reduce T_s or recheck the continuous model."
    )

print(f"Discrete A:\n{A_d}\nDiscrete B:\n{B_d}")
# Discrete A:
# [[ 0.99990100  0.00980248]
#  [-0.01960496  0.97049356]]
# Discrete B:
# [[4.96683330e-05]
#  [9.80248334e-03]]
```

### Example 3: Roll-to-roll (R2R) web-handling linearization

R2R web handling (printing, coating, converting) has bilinear tension dynamics — the product of tension $T$ and web velocity $v$ means the linearization depends on the *current* operating point, not just constant parameters.

Nonlinear single-span model (state $x = [T, v]$, input $u =$ motor torque):

$$\dot{T} = \frac{v}{L}\,(EA - T), \qquad
\dot{v} = \frac{R}{J}\,u - \frac{R^2}{J}\,T.$$

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class WebSpanParams:
    """Physical parameters of a single R2R web span.

    Frozen so a calibrated parameter set cannot be mutated mid-design.
    """
    EA: float   # web axial stiffness E * A  [N]
    L: float    # free span length           [m]
    R: float    # driven-roller radius       [m]
    J: float    # roller + motor inertia     [kg*m^2]

    def __post_init__(self) -> None:
        for field_name in ("EA", "L", "R", "J"):
            value = getattr(self, field_name)
            if not (isinstance(value, (int, float)) and np.isfinite(value)):
                raise ValueError(f"{field_name} must be a finite number; got {value!r}.")
            if value <= 0.0:
                raise ValueError(f"{field_name} must be strictly positive; got {value}.")


def r2r_jacobian(
    params: WebSpanParams,
    tension_0: float,
    velocity_0: float,
) -> tuple[FloatArray, FloatArray]:
    """Linearize one R2R web span about (tension_0, velocity_0).

    Analytic Jacobian:
        d(dT/dt)/dT = -v / L
        d(dT/dt)/dv = (EA - T) / L
        d(dv/dt)/dT = -R**2 / J
        d(dv/dt)/dv = 0          (no mechanical damping in this model)
        d(dv/dt)/du =  R / J
    """
    if not (np.isfinite(tension_0) and np.isfinite(velocity_0)):
        raise ValueError("Operating point (tension_0, velocity_0) must be finite.")

    A = np.array([
        [-velocity_0 / params.L, (params.EA - tension_0) / params.L],
        [-(params.R**2) / params.J, 0.0],
    ], dtype=np.float64)
    B = np.array([[0.0], [params.R / params.J]], dtype=np.float64)
    return A, B
```

## Pitfalls

1. **Linearizing about a non-equilibrium point.** If $f(x_0, u_0) \neq 0$, the true model is affine: $\Delta\dot{x} = A\Delta x + B\Delta u + f(x_0, u_0)$. The pure $(A, B)$ form silently drops the constant term, producing a model that is wrong from the start. Always verify $f(x_0, u_0) \approx 0$ first.

2. **Using the inverse-based ZOH formula with singular $A_c$.** The closed form $B_d = A_c^{-1}(A_d - I)B_c$ requires $A_c$ invertible and silently explodes for a pure integrator (zero eigenvalue — extremely common in mechanical plants). Always use the Van Loan block-matrix construction.

3. **Tustin $B_d$ scaling bug.** The correct scaling is $T_s$, not $T_s/2$. Using $T_s/2$ halves the steady-state response and is hard to spot because the dynamics *look* reasonable.

4. **Mixing continuous and discrete stability tests.** Continuous stability requires $\operatorname{Re}(\lambda) < 0$ (left-half-plane). Discrete stability requires $|\lambda| < 1$ (unit circle). Using the wrong test gives false pass/fail results.

5. **Forward Euler for stiff systems.** Forward Euler's stability region is a small disk. Fast modes or large $T_s$ cause the discrete model to diverge numerically even when the continuous model is stable. This is a purely numerical artifact — use ZOH or Tustin.

6. **JAX float32 default.** JAX defaults to float32. Control models routinely need float64. Without `jax.config.update("jax_enable_x64", True)`, Jacobians will be quietly low-precision.

7. **Sign or index errors in hand-derived partials.** The single most common linearization bug. Always cross-check hand-derived or symbolic Jacobians against finite differences or autodiff to a few significant figures.

8. **Stale library versions.** Older NumPy/SciPy carry known numerical bugs (`numpy.matrix` deprecated, `expm` hardened over time). Pin to current maintained releases.

9. **Unvalidated sensor/parameter data.** A single `NaN` or `Inf` silently corrupts every downstream eigenvalue, potentially yielding a "stable-looking" but physically wrong controller. Validate all inputs *before* linear algebra.

10. **Not documenting the validity region.** A linear model is only trustworthy near $(x_0, u_0)$. Without documenting the $\pm 10\text{–}20\%$ range, the next engineer or gain-scheduling logic has no way to know when to switch models.

## Verification

Run all four checks before handing the linearized model to a controller-design routine:

1. **Numerical gradient check.** Compare the analytic/symbolic/autodiff Jacobian against the finite-difference `linearize` (or `scipy.optimize.approx_fprime` / `jax.jacrev`). Agreement to a few significant figures confirms you differentiated the right function.

   ```python
   # Cross-check symbolic vs finite-difference
   A_fd, B_fd = linearize(f_numpy, x0, u0, rel_step=1e-6)
   A_sym_np = np.array(A_sym.tolist(), dtype=np.float64)
   assert np.allclose(A_fd, A_sym_np, atol=1e-4), "Jacobian mismatch — check sign/index errors"
   ```

2. **Stability check.** Run the time-domain-appropriate test before and after discretization:

   ```python
   assert is_continuous_stable(A_c), "Continuous model is unstable — recheck physics"
   A_d, B_d = discretize_zoh(A_c, B_c, T_s)
   assert is_discrete_stable(A_d), "Discrete model is unstable — reduce T_s"
   ```

   A continuous model that is stable but discretizes to unstable is the signature of too large a $T_s$.

3. **Linearity validation.** Simulate the full nonlinear system and the linear model from the same perturbed initial condition. Confirm error $\epsilon = \lVert x_{\text{nl}} - x_{\text{lin}} \rVert$ stays small for small perturbations and *grows* for large ones — that growth defines the edge of the validity region.

   ```python
   # Inline linearity check (this folder does not ship a separate validation script)
   perturbation = 0.01 * np.ones_like(x0)  # small perturbation
   # ... simulate both models for T_sim seconds ...
   # assert error stays small
   ```

4. **Discretization consistency.** Confirm $A_d$ reproduces the continuous system's evolution at $t = T_s$:

   ```python
   from scipy.linalg import expm
   A_d_check = expm(A_c * T_s)
   assert np.allclose(A_d, A_d_check, atol=1e-10), "ZOH A_d does not match expm(A_c * T_s)"
   ```

   The four checks above are the ready-to-run versions; copy them into the project, do not expect extra files in this skill folder.

## Related Skills

- state-space-representation
- controller-design
- observer-design
- model-predictive-control
- lpv-modeling
