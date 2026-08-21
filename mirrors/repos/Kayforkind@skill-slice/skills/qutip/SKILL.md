---
name: qutip
version: 1.1.1
description: "Simulates quantum states and open systems in QuTiP 5.x (sesolve, mesolve, mcsolve, entanglement, Bloch/Wigner, Floquet, HEOM). Use when evolving Qobj states, measuring fidelity or entropy, or visualizing Bloch/Wigner plots. Not for classical ODEs, large-scale circuit transpilation (qiskit/cirq), or loading untrusted .qu pickles."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# QuTiP: Quantum Toolbox in Python

## When to Use

Reach for QuTiP whenever the object you care about is a quantum state or operator on a finite-dimensional Hilbert space and you need to evolve it, measure it, or visualize it. The library represents `Qobj` (quantum objects) together with their tensor-product *dimension* structure, so composite systems, partial traces, and superoperators all stay bookkeeping-correct without you tracking index order by hand.

Concretely, it fits when you are:

1. **Modeling closed (unitary) or open (dissipative) systems.** Closed systems conserve probability and you only need the Hamiltonian; open systems leak into an environment, so you also supply collapse operators. QuTiP lets you switch between the two by changing a single argument.
2. **Working with states and operators directly.** Kets, bras, and density matrices share one `Qobj` type, so the same code path handles pure and mixed states — important because real experiments almost always produce mixed states.
3. **Solving the Schrödinger or master equation for dynamics.** You rarely have closed-form solutions for driven or dissipative systems, so a numerical integrator is the practical tool.
4. **Quantifying quantum information** (entanglement, fidelity, von Neumann entropy). These scalar diagnostics let you compare a noisy simulation against an ideal target.
5. **Visualizing states** via Bloch spheres, Wigner functions, or Hinton diagrams, because a phase-phase or sphere picture often reveals structure (squeezing, interference fringes) that a raw density matrix hides.
6. **Running advanced dynamics** such as Floquet theory (periodic driving) or HEOM (strong, non-Markovian system–bath coupling) where the simple Born–Markov master equation is no longer valid.

### Do Not Use

- **Classical physics simulations.** QuTiP has no advantage over plain NumPy/SciPy for classical ODEs, and forcing classical problems through `Qobj` only adds overhead.
- **Large-scale circuit synthesis / transpilation.** Use the `qutip-qip` extension for small pedagogical circuits, but for hardware-targeted compilation prefer `qiskit` or `cirq`. The legacy `qutip-qip` namespace is deprecated; new code should import from `qutip_qip`.
- **Hilbert spaces that exceed available RAM.** A dense density matrix costs `O(d^2)` complex numbers, so a 10-qubit open system (`d = 1024`) already needs ~16 MB per stored matrix and far more transiently. Before scaling up, switch to sparse representations, Krylov-subspace methods (`options={"method": "krylov"}`), Monte-Carlo trajectories (state vectors instead of density matrices), or a GPU back-end.
- **Loading untrusted serialized objects.** `Qobj` pickles and `.qu` files can carry arbitrary Python objects. Deserializing attacker-controlled data is equivalent to running attacker code. Only load files whose provenance you trust, and prefer interchange formats (`.npy`, HDF5 with array-only payloads) for data from third parties.

## Prerequisites

### Installation

Pin to the 5.x series. QuTiP 5 changed several public APIs (solver options are now plain dictionaries, Floquet uses `FloquetBasis`, HEOM moved to `qutip.solver.heom`), so pinning a major version protects your scripts from silent breakage on the next release:

```bash
uv pip install "qutip>=5.0,<6.0"
```

Optional companion packages — install only what a given project needs, since each pulls in extra dependencies:

```bash
# Quantum information processing (circuits, gates) — modern namespace is `qutip_qip`
uv pip install "qutip-qip>=0.4"

# Optimal-control / pulse-engineering tools
uv pip install "qutip-qtrl>=0.3"
```

Verify the install and surface the exact version, because feature availability (Floquet, HEOM, solver option keys) differs across point releases:

```python
import qutip

print(f"QuTiP {qutip.__version__}")
# Run the built-in self-test on a fresh environment to catch a broken BLAS/SciPy link
# before it shows up as a wrong numerical answer.
# qutip.about()  # prints versions of NumPy, SciPy, Cython, and compiled extensions
```

### Coding Conventions

Every code block below is a complete, runnable snippet that follows three rules. Each rule prevents a specific, common failure mode:

1. **Explicit imports and explicit type hints (no `Any`).** `from qutip import *` pulls in names like `num`, `create`, and `position` that shadow ordinary identifiers and make it hard to tell where a symbol came from. Naming imports and annotating with concrete types (`Qobj`, `NDArray[np.float64]`, `list[Qobj]`) lets a type checker catch a ket/operator mix-up *before* you wait through a long integration.
2. **Validation at the boundary.** Numerical solvers do not reject unphysical input — a negative decay rate or mismatched Hilbert-space dimension produces a cryptic error deep in the integrator, or worse, a plausible-looking but wrong answer. Validating dimensions and rates where data enters the function converts those into clear, early errors.
3. **Defensive handling of solver output.** An ODE integrator that diverges returns `NaN` or `inf` rather than raising. Checking that results are finite (and, for steady states, that the residual is actually small) is the difference between trusting a number and being misled by one.

The examples share a small helper module. Save it once as `qutip_helpers.py`:

```python
# qutip_helpers.py
"""Reusable validation helpers for QuTiP simulations (Python >= 3.11)."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qutip import Qobj


def require_dimension(name: str, value: int, *, minimum: int = 1) -> int:
    """Validate a Hilbert-space dimension.

    A solver given a non-positive or non-integer dimension fails with an opaque
    shape error; checking here names the offending argument instead.
    """
    if not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an int >= {minimum}, got {value!r}")
    return value


def require_nonnegative_rate(name: str, value: float) -> float:
    """Validate a physical rate (decay, dephasing, coupling magnitude).

    Negative or non-finite rates correspond to an unphysical, norm-amplifying
    master equation; the integrator would diverge silently.
    """
    rate = float(value)
    if not np.isfinite(rate) or rate < 0.0:
        raise ValueError(f"{name} must be a finite, non-negative rate, got {value!r}")
    return rate


def require_time_grid(tlist: NDArray[np.float64]) -> NDArray[np.float64]:
    """Validate the integration time grid.

    QuTiP samples results at these points; a non-monotonic or single-point grid
    yields meaningless output rather than an error.
    """
    grid = np.asarray(tlist, dtype=np.float64)
    if grid.ndim != 1 or grid.size < 2:
        raise ValueError("tlist must be a 1-D array with at least two time points")
    if not np.all(np.diff(grid) > 0.0):
        raise ValueError("tlist must be strictly increasing")
    return grid


def require_hermitian(name: str, operator: Qobj) -> Qobj:
    """Validate that an operator is Hermitian.

    A non-Hermitian Hamiltonian breaks unitarity and the conservation of
    probability. (Relax this guard only for deliberately non-Hermitian effective
    Hamiltonians, e.g. PT-symmetric models.)
    """
    if not operator.isherm:
        raise ValueError(f"{name} must be Hermitian for standard time evolution")
    return operator


def require_density_matrix(name: str, rho: Qobj, *, atol: float = 1e-6) -> Qobj:
    """Validate that `rho` is a unit-trace density operator.

    Information measures (entropy, concurrence) are only meaningful for a valid
    normalized state; a trace far from 1 signals an upstream bug.
    """
    if not rho.isoper:
        raise TypeError(f"{name} must be a density operator (got type={rho.type!r})")
    trace = complex(rho.tr())
    if abs(trace - 1.0) > atol:
        raise ValueError(f"{name} trace must equal 1, got {trace.real:.6f}")
    return rho
```

## Procedure

### 1. Quantum Objects and States

States and operators are both `Qobj` instances; the difference is encoded in the `.type` attribute and the `.dims` structure. Building them through small validated constructors keeps the *truncation dimension* explicit, which matters because every infinite-dimensional mode (a cavity, an oscillator) must be cut off somewhere, and choosing that cutoff too low silently corrupts the physics.

```python
from qutip import (
    Qobj,
    basis,
    coherent,
    thermal_dm,
    destroy,
    create,
    num,
    qeye,
    sigmax,
    sigmay,
    sigmaz,
    tensor,
)

from qutip_helpers import require_dimension, require_nonnegative_rate


def fock_state(dimension: int, level: int) -> Qobj:
    """Return the Fock (number) state |level> in a `dimension`-sized space."""
    require_dimension("dimension", dimension)
    if not isinstance(level, int) or not (0 <= level < dimension):
        raise ValueError(
            f"level must satisfy 0 <= level < {dimension}, got {level!r}"
        )
    return basis(dimension, level)


def coherent_state(dimension: int, alpha: complex) -> Qobj:
    """Return a coherent state |alpha> with a truncation safety check."""
    require_dimension("dimension", dimension)
    amplitude = complex(alpha)
    mean_photons = abs(amplitude) ** 2
    # A coherent state populates Fock levels up to ~|alpha|^2 with a spread of
    # ~|alpha|. If the truncation is too small the tail wraps around and aliases
    # back into low levels, so refuse rather than return a corrupted state.
    if mean_photons > 0.5 * dimension:
        raise ValueError(
            f"dimension={dimension} too small for <n>={mean_photons:.1f}; "
            f"use dimension >= {int(4 * mean_photons) + 1} to contain the tail"
        )
    return coherent(dimension, amplitude)


def thermal_state(dimension: int, mean_photons: float) -> Qobj:
    """Return a thermal density matrix with the given average occupation."""
    require_dimension("dimension", dimension)
    n_avg = require_nonnegative_rate("mean_photons", mean_photons)
    if n_avg > 0.25 * dimension:
        raise ValueError(
            f"dimension={dimension} too small for a thermal state with "
            f"<n>={n_avg:.1f}; increase the truncation"
        )
    return thermal_dm(dimension, n_avg)


def mode_operators(dimension: int) -> tuple[Qobj, Qobj, Qobj]:
    """Return (annihilation, creation, number) operators for one bosonic mode."""
    require_dimension("dimension", dimension)
    annihilation = destroy(dimension)
    creation = create(dimension)
    number = num(dimension)
    return annihilation, creation, number


def two_qubit_observable() -> Qobj:
    """Build sigma_z ⊗ I on a two-qubit space, demonstrating composition.

    `tensor` tracks the [[2, 2], [2, 2]] dims so later partial traces and
    expectation values address the correct subsystem automatically.
    """
    sz_on_first = tensor(sigmaz(), qeye(2))
    return sz_on_first


# Example usage
psi_fock = fock_state(dimension=20, level=2)            # |2>
psi_coherent = coherent_state(dimension=20, alpha=2.0)  # |alpha=2>
rho_thermal = thermal_state(dimension=20, mean_photons=1.5)
a_op, adag_op, n_op = mode_operators(20)
sx, sy, sz = sigmax(), sigmay(), sigmaz()
```

**Load** `references/core_concepts.md` **when** you need comprehensive coverage of quantum objects, states, operators, tensor products, partial traces, or superoperator formalism.

### 2. Time Evolution and Dynamics

Pick the solver that matches the physics, not out of habit — the wrong choice is either needlessly slow or silently inapplicable. The wrapper below validates the model, supplies sane solver options as a QuTiP 5 dictionary, and verifies the output is finite so a diverged integration cannot masquerade as a result.

```python
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray
from qutip import Qobj, Result, mesolve, mcsolve, sesolve

from qutip_helpers import require_hermitian, require_time_grid, require_nonnegative_rate


def evolve_closed_system(
    hamiltonian: Qobj,
    initial_state: Qobj,
    tlist: NDArray[np.float64],
    expect_ops: Sequence[Qobj],
    *,
    options: dict[str, object] | None = None,
) -> Result:
    """Unitary evolution via the Schrödinger equation (fastest, pure states)."""
    grid = require_time_grid(tlist)
    require_hermitian("hamiltonian", hamiltonian)
    if not initial_state.isket:
        raise TypeError("sesolve expects a ket initial state; use mesolve for mixed states")

    solver_options: dict[str, object] = {"atol": 1e-8, "rtol": 1e-6, "nsteps": 10_000}
    if options:
        solver_options.update(options)
    try:
        result = sesolve(
            hamiltonian, initial_state, grid,
            e_ops=list(expect_ops), options=solver_options,
        )
    except Exception as exc:  # surface integrator failure with context
        raise RuntimeError("sesolve failed to integrate the Schrödinger equation") from exc
    _assert_finite_expectations(result)
    return result


def evolve_open_system(
    hamiltonian: Qobj,
    initial_state: Qobj,
    tlist: NDArray[np.float64],
    collapse_ops: Sequence[Qobj],
    expect_ops: Sequence[Qobj],
    *,
    options: dict[str, object] | None = None,
) -> Result:
    """Dissipative evolution via the Lindblad master equation (mixed states)."""
    grid = require_time_grid(tlist)
    require_hermitian("hamiltonian", hamiltonian)
    # Mismatched dims are the most common open-systems bug; check before the
    # integrator turns them into an inscrutable broadcasting error.
    for index, c_op in enumerate(collapse_ops):
        if c_op.dims != hamiltonian.dims:
            raise ValueError(
                f"collapse_ops[{index}] dims {c_op.dims} != H dims {hamiltonian.dims}"
            )

    solver_options: dict[str, object] = {
        "atol": 1e-8,
        "rtol": 1e-6,
        "nsteps": 10_000,
        "store_states": False,  # keep only e_ops unless states are explicitly needed
    }
    if options:
        solver_options.update(options)
    try:
        result = mesolve(
            hamiltonian, initial_state, grid,
            c_ops=list(collapse_ops), e_ops=list(expect_ops),
            options=solver_options,
        )
    except Exception as exc:
        raise RuntimeError("mesolve failed to integrate the master equation") from exc
    _assert_finite_expectations(result)
    return result


def evolve_trajectories(
    hamiltonian: Qobj,
    initial_state: Qobj,
    tlist: NDArray[np.float64],
    collapse_ops: Sequence[Qobj],
    expect_ops: Sequence[Qobj],
    *,
    ntraj: int = 500,
    options: dict[str, object] | None = None,
) -> Result:
    """Quantum-jump (Monte Carlo) unravelling; cheaper memory than mesolve at large d."""
    if ntraj < 1:
        raise ValueError(f"ntraj must be >= 1, got {ntraj}")
    grid = require_time_grid(tlist)
    require_hermitian("hamiltonian", hamiltonian)

    solver_options: dict[str, object] = {"atol": 1e-8, "rtol": 1e-6, "map": "parallel"}
    if options:
        solver_options.update(options)
    try:
        result = mcsolve(
            hamiltonian, initial_state, grid,
            c_ops=list(collapse_ops), e_ops=list(expect_ops),
            ntraj=ntraj, options=solver_options,
        )
    except Exception as exc:
        raise RuntimeError("mcsolve failed to run the trajectory ensemble") from exc
    _assert_finite_expectations(result)
    return result


def _assert_finite_expectations(result: Result) -> None:
    """Reject diverged integrations: a runaway ODE returns NaN/inf, not an error."""
    for index, series in enumerate(result.expect):
        values = np.asarray(series)
        if not np.all(np.isfinite(values)):
            raise RuntimeError(
                f"expectation series {index} is non-finite; the solver likely diverged. "
                "Reduce the time step, lower the rates, or set options['method']='bdf'."
            )
```

**Solver selection guide — and *why* each one exists:**

| Solver | Use case | Cost |
|--------|----------|------|
| `sesolve` | Pure states under unitary evolution. Propagates a state *vector* (`d` amplitudes). | Cheapest |
| `mesolve` | Mixed states and general dissipation. Propagates a *density matrix* (`d^2` numbers). | Exact ensemble-averaged dynamics |
| `mcsolve` | Stochastic quantum jumps. Averages many `d`-dimensional trajectories instead of storing one `d^2` matrix. | Wins on memory for large open systems; exposes individual quantum-jump records |
| `brmesolve` | Bloch–Redfield, for *weak* system–bath coupling specified through a noise spectrum rather than explicit collapse operators. | Use when you know the bath's spectral density but not a phenomenological decay rate |
| `fmmesolve` | Floquet–Markov, for time-*periodic* driving where dissipation is best treated in the Floquet basis. | For periodically driven open systems |

**Load** `references/time_evolution.md` **when** you need time-dependent Hamiltonians, propagators, or the full solver option set.

### 3. Analysis and Measurement

These functions turn a state into a scalar you can track or compare. Each guard reflects the domain of validity: entropy and concurrence require a *normalized density matrix*, fidelity requires two states on the *same* space, and a steady state is only trustworthy if its Liouvillian residual is actually near zero.

```python
import numpy as np
from numpy.typing import NDArray
from qutip import (
    Qobj,
    concurrence,
    correlation_2op_1t,
    entropy_vn,
    expect,
    fidelity,
    liouvillian,
    operator_to_vector,
    spectrum_correlation_fft,
    steadystate,
    tracedist,
)

from qutip_helpers import require_density_matrix


def von_neumann_entropy(rho: Qobj) -> float:
    """S(rho) = -Tr(rho ln rho), in nats. 0 for a pure state, ln(d) when maximally mixed."""
    require_density_matrix("rho", rho)
    return float(entropy_vn(rho))


def two_qubit_concurrence(rho: Qobj) -> float:
    """Wootters concurrence in [0, 1]; 0 = separable, 1 = maximally entangled."""
    require_density_matrix("rho", rho)
    if rho.dims != [[2, 2], [2, 2]]:
        raise ValueError(f"concurrence is defined for two qubits, got dims {rho.dims}")
    return float(concurrence(rho))


def state_fidelity(state_a: Qobj, state_b: Qobj) -> float:
    """Jozsa fidelity in [0, 1]; accepts kets or density matrices on the same space."""
    if state_a.dims[0] != state_b.dims[0]:
        raise ValueError(
            f"states live on different spaces: {state_a.dims[0]} vs {state_b.dims[0]}"
        )
    return float(fidelity(state_a, state_b))


def trace_distance(rho_a: Qobj, rho_b: Qobj) -> float:
    """Trace distance in [0, 1]; the maximal single-shot distinguishability of two states."""
    require_density_matrix("rho_a", rho_a)
    require_density_matrix("rho_b", rho_b)
    return float(tracedist(rho_a, rho_b))


def expectation_value(operator: Qobj, state: Qobj) -> float | complex:
    """Compute <operator> for a ket or density matrix."""
    return expect(operator, state)


def stationary_state(
    hamiltonian: Qobj,
    collapse_ops: list[Qobj],
    *,
    tol: float = 1e-10,
) -> Qobj:
    """Solve for the steady state of a Liouvillian and verify the residual is small."""
    L = liouvillian(hamiltonian, collapse_ops)
    try:
        rho_ss = steadystate(L, method="svd", tol=tol)
    except Exception as exc:
        raise RuntimeError("steadystate failed to converge") from exc
    # Verify: L(rho_ss) should be ~0. If it is not, the solver returned garbage.
    residual = (L * operator_to_vector(rho_ss)).norm()
    if residual > 1e-6:
        raise RuntimeError(
            f"steady-state residual {residual:.2e} exceeds tolerance; "
            "the Liouvillian may be singular or the system may not have a unique steady state"
        )
    return rho_ss


def power_spectrum(
    hamiltonian: Qobj,
    collapse_ops: list[Qobj],
    operator_a: Qobj,
    *,
    tlist: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Compute the emission spectrum S(omega) via the two-time correlation function."""
    corr = correlation_2op_1t(
        hamiltonian, None, tlist, collapse_ops, operator_a.dag(), operator_a,
    )
    spectrum, frequencies = spectrum_correlation_fft(tlist, corr)
    return np.asarray(spectrum, dtype=np.float64)
```

**Load** `references/analysis.md` **when** you need detailed coverage of correlation functions, spectrum computation, or advanced steady-state methods.

### 4. Visualization

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qutip import Qobj, Bloch, wigner, plot_wigner, plot_fock_distribution


def render_bloch(
    states: list[Qobj],
    *,
    save_path: str | None = None,
    figsize: tuple[int, int] = (5, 5),
) -> None:
    """Plot one or more single-qubit states on a Bloch sphere.

    Works headless: if `save_path` is given, the figure is written to disk
    without calling `plt.show()`.
    """
    import matplotlib.pyplot as plt

    bloch = Bloch(figsize=figsize)
    for state in states:
        if not state.isket or state.dims != [[2], [1]]:
            raise ValueError(
                f"render_bloch expects single-qubit kets, got dims={state.dims}, type={state.type}"
            )
        bloch.add_states(state)
    bloch.render()

    if save_path is not None:
        fig = plt.gcf()
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


def render_wigner(
    state: Qobj,
    *,
    save_path: str | None = None,
    xvec: NDArray[np.float64] | None = None,
) -> None:
    """Plot the Wigner function of a single-mode state."""
    import matplotlib.pyplot as plt

    if xvec is None:
        xvec = np.linspace(-5, 5, 200)
    wigner_values = wigner(state, xvec, xvec)

    fig, ax = plt.subplots(figsize=(6, 5))
    contour = ax.contourf(xvec, xvec, wigner_values, 100, cmap="RdBu_r")
    ax.set_xlabel(r"Re($\alpha$)")
    ax.set_ylabel(r"Im($\alpha$)")
    fig.colorbar(contour, ax=ax)
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
```

**Load** `references/visualization.md` **when** you need advanced plotting (Hinton diagrams, Wigner animation, sphere customization, or multi-panel figures).

### 5. Damped Harmonic Oscillator (Complete Example)

A cavity mode with photon loss: the coherent state amplitude decays as `alpha(t) = alpha(0) * exp(-kappa*t/2)`, so the mean photon number follows `|alpha|^2 * exp(-kappa*t)`.

```python
"""Damped harmonic oscillator: coherent state losing photons to a cold bath."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qutip import Qobj, coherent, destroy, mesolve, num, qeye

from qutip_helpers import (
    require_dimension,
    require_nonnegative_rate,
    require_time_grid,
    require_hermitian,
)


def run_damped_oscillator(
    dimension: int,
    frequency: float,
    decay_rate: float,
    initial_alpha: complex,
    tlist: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return <n>(t) for a damped cavity initially in a coherent state."""
    require_dimension("dimension", dimension)
    kappa = require_nonnegative_rate("decay_rate", decay_rate)
    grid = require_time_grid(tlist)

    a = destroy(dimension)
    hamiltonian = frequency * a.dag() * a
    require_hermitian("hamiltonian", hamiltonian)
    collapse_ops = [np.sqrt(kappa) * a]
    initial_state = coherent(dimension, initial_alpha)

    # Truncation safety: coherent state tail must fit in the Fock space
    mean_photons = abs(complex(initial_alpha)) ** 2
    if mean_photons > 0.5 * dimension:
        raise ValueError(
            f"dimension={dimension} too small for |alpha|={abs(complex(initial_alpha)):.1f} "
            f"(<n>={mean_photons:.1f}); use dimension >= {int(4 * mean_photons) + 1}"
        )

    try:
        result = mesolve(
            hamiltonian, initial_state, grid,
            c_ops=collapse_ops, e_ops=[num(dimension)],
            options={"atol": 1e-8, "rtol": 1e-6, "nsteps": 10_000},
        )
    except Exception as exc:
        raise RuntimeError("mesolve failed for the damped oscillator") from exc

    photon_number = np.asarray(result.expect[0], dtype=np.float64)
    if not np.all(np.isfinite(photon_number)):
        raise RuntimeError("non-finite photon number; the integration diverged")
    return photon_number


def main() -> None:
    import matplotlib.pyplot as plt

    dimension = 20
    decay_rate = 0.1
    tlist = np.linspace(0.0, 50.0, 200)
    photon_number = run_damped_oscillator(
        dimension=dimension, frequency=1.0, decay_rate=decay_rate,
        initial_alpha=3.0, tlist=tlist,
    )

    expected = (abs(3.0) ** 2) * np.exp(-decay_rate * tlist)  # analytic envelope
    figure, ax = plt.subplots(figsize=(8, 4))
    ax.plot(tlist, photon_number, label="mesolve")
    ax.plot(tlist, expected, "--", label=r"$|\alpha|^2 e^{-\kappa t}$")
    ax.set_xlabel("Time")
    ax.set_ylabel(r"$\langle n \rangle$")
    ax.set_title("Photon-number decay")
    ax.legend()
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
```

### 6. Two-Qubit Entanglement Dynamics (Complete Example)

Pure dephasing destroys the off-diagonal coherences of a Bell state without changing populations, so the concurrence should decay smoothly to zero. The Hamiltonian is set to zero deliberately, to isolate the effect of dephasing from any coherent rotation.

```python
"""Concurrence decay of a Bell state under independent local dephasing."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qutip import Qobj, bell_state, mesolve, qeye, sigmaz, tensor

from qutip_helpers import require_nonnegative_rate, require_time_grid, require_density_matrix
from qutip import concurrence


def run_dephasing(
    dephasing_rate: float,
    tlist: NDArray[np.float64],
) -> NDArray[np.float64]:
    """Return concurrence C(t) for |Phi+> under sigma_z dephasing on each qubit."""
    gamma = require_nonnegative_rate("dephasing_rate", dephasing_rate)
    grid = require_time_grid(tlist)

    initial_state: Qobj = bell_state("00")  # (|00> + |11>)/sqrt(2)
    # Zero Hamiltonian: no coherent dynamics, so we observe dephasing in isolation.
    hamiltonian: Qobj = 0.0 * tensor(qeye(2), qeye(2))
    collapse_ops: list[Qobj] = [
        np.sqrt(gamma) * tensor(sigmaz(), qeye(2)),
        np.sqrt(gamma) * tensor(qeye(2), sigmaz()),
    ]

    try:
        result = mesolve(
            hamiltonian, initial_state, grid,
            c_ops=collapse_ops, e_ops=[], options={"store_states": True},
        )
    except Exception as exc:
        raise RuntimeError("mesolve failed for the dephasing model") from exc

    # With collapse operators present, result.states are already density matrices,
    # so concurrence is computed on them directly (no .proj() needed).
    concurrences: list[float] = []
    for state in result.states:
        require_density_matrix("state", state, atol=1e-4)
        concurrences.append(float(concurrence(state)))
    return np.asarray(concurrences, dtype=np.float64)


def main() -> None:
    import matplotlib.pyplot as plt

    tlist = np.linspace(0.0, 10.0, 100)
    concurrences = run_dephasing(dephasing_rate=0.1, tlist=tlist)

    if concurrences[-1] >= concurrences[0]:
        raise RuntimeError("entanglement did not decay under dephasing — model is wrong")

    figure, ax = plt.subplots(figsize=(8, 4))
    ax.plot(tlist, concurrences)
    ax.set_xlabel("Time")
    ax.set_ylabel("Concurrence")
    ax.set_title("Entanglement decay under local dephasing")
    ax.set_ylim(0.0, 1.05)
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
```

### 7. Jaynes–Cummings Model (Complete Example)

A cavity field coupled to a two-level atom exchanges energy coherently (vacuum Rabi oscillations) while both subsystems leak to the environment. This example exercises tensor products, multiple collapse channels, and per-subsystem observables at once.

```python
"""Jaynes–Cummings model: cavity and atom occupation under joint dissipation."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qutip import (
    Qobj,
    basis,
    coherent,
    destroy,
    mesolve,
    qeye,
    sigmam,
    tensor,
)

from qutip_helpers import (
    require_dimension,
    require_nonnegative_rate,
    require_time_grid,
    require_hermitian,
)


def build_jaynes_cummings(
    cavity_dim: int,
    cavity_freq: float,
    atom_freq: float,
    coupling: float,
) -> tuple[Qobj, Qobj, Qobj]:
    """Return (H, cavity number op, atom number op) in the rotating-wave approximation."""
    require_dimension("cavity_dim", cavity_dim)
    wc = require_nonnegative_rate("cavity_freq", cavity_freq)
    wa = require_nonnegative_rate("atom_freq", atom_freq)
    g = require_nonnegative_rate("coupling", coupling)

    cavity = tensor(destroy(cavity_dim), qeye(2))
    atom = tensor(qeye(cavity_dim), sigmam())
    hamiltonian: Qobj = (
        wc * cavity.dag() * cavity
        + wa * atom.dag() * atom
        + g * (cavity.dag() * atom + cavity * atom.dag())
    )
    require_hermitian("hamiltonian", hamiltonian)
    return hamiltonian, cavity.dag() * cavity, atom.dag() * atom


def run_jaynes_cummings(
    cavity_dim: int,
    tlist: NDArray[np.float64],
    *,
    cavity_decay: float,
    atom_decay: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return (<n_cavity>(t), <n_atom>(t)) for a coherent field and a ground-state atom."""
    grid = require_time_grid(tlist)
    kappa = require_nonnegative_rate("cavity_decay", cavity_decay)
    gamma = require_nonnegative_rate("atom_decay", atom_decay)

    hamiltonian, n_cavity, n_atom = build_jaynes_cummings(
        cavity_dim=cavity_dim, cavity_freq=1.0, atom_freq=1.0, coupling=0.05
    )
    cavity = tensor(destroy(cavity_dim), qeye(2))
    atom = tensor(qeye(cavity_dim), sigmam())
    collapse_ops: list[Qobj] = [np.sqrt(kappa) * cavity, np.sqrt(gamma) * atom]
    initial_state: Qobj = tensor(coherent(cavity_dim, 2.0), basis(2, 0))

    try:
        result = mesolve(
            hamiltonian, initial_state, grid,
            c_ops=collapse_ops, e_ops=[n_cavity, n_atom],
            options={"atol": 1e-8, "rtol": 1e-6, "nsteps": 10_000},
        )
    except Exception as exc:
        raise RuntimeError("mesolve failed for the Jaynes–Cummings model") from exc

    cavity_occupation = np.asarray(result.expect[0], dtype=np.float64)
    atom_occupation = np.asarray(result.expect[1], dtype=np.float64)
    if not (np.all(np.isfinite(cavity_occupation)) and np.all(np.isfinite(atom_occupation))):
        raise RuntimeError("non-finite occupations; the integration diverged")
    return cavity_occupation, atom_occupation


def main() -> None:
    import matplotlib.pyplot as plt

    tlist = np.linspace(0.0, 50.0, 200)
    cavity_occupation, atom_occupation = run_jaynes_cummings(
        cavity_dim=10, tlist=tlist, cavity_decay=0.1, atom_decay=0.05
    )

    figure, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    axes[0].plot(tlist, cavity_occupation)
    axes[0].set_ylabel(r"$\langle n_\mathrm{cavity} \rangle$")
    axes[1].plot(tlist, atom_occupation)
    axes[1].set_ylabel(r"$\langle n_\mathrm{atom} \rangle$")
    axes[1].set_xlabel("Time")
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
```

## Pitfalls

1. **Truncation dimension too small for coherent/thermal states.** A coherent state with `|alpha|^2` mean photons populates Fock levels up to `~|alpha|^2` with a spread of `~|alpha`. If the truncation is too small the tail wraps around and aliases back into low levels, silently corrupting the state. Always use `dimension >= 4 * |alpha|^2 + 1` for coherent states and check that `mean_photons <= 0.25 * dimension` for thermal states.

2. **Collapse operator dimensions mismatched with Hamiltonian.** This is the most common open-systems bug. The integrator turns a dimension mismatch into an inscrutable broadcasting error. Always validate `c_op.dims == hamiltonian.dims` before calling `mesolve`.

3. **Negative or non-finite rates passed to the master equation.** These correspond to an unphysical, norm-amplifying master equation; the integrator diverges silently rather than raising. Always validate rates are finite and non-negative at the boundary.

4. **Diverged integrator returning NaN/inf instead of raising.** An ODE integrator that diverges returns `NaN` or `inf` rather than raising an exception. Always check `np.all(np.isfinite(values))` on expectation series after solving. If divergence occurs, reduce the time step, lower the rates, or set `options['method']='bdf'`.

5. **Non-Hermitian Hamiltonian for standard time evolution.** A non-Hermitian Hamiltonian breaks unitarity and conservation of probability. Only relax the Hermiticity guard for deliberately non-Hermitian effective Hamiltonians (e.g. PT-symmetric models).

6. **Steady state with large Liouvillian residual.** `steadystate` may return a result even when the Liouvillian residual is not near zero. Always verify `(L * operator_to_vector(rho_ss)).norm() < 1e-6` after solving. A large residual means the Liouvillian is singular or the system lacks a unique steady state.

7. **Using `from qutip import *`.** This pulls in names like `num`, `create`, and `position` that shadow ordinary identifiers. Use explicit imports instead.

8. **Loading untrusted serialized `Qobj` pickles or `.qu` files.** These can carry arbitrary Python objects. Deserializing attacker-controlled data is equivalent to running attacker code. Only load files whose provenance you trust; prefer `.npy` or HDF5 with array-only payloads for third-party data.

9. **Exceeding RAM with dense density matrices.** A dense density matrix costs `O(d^2)` complex numbers. A 10-qubit open system (`d = 1024`) needs ~16 MB per stored matrix and far more transiently. Switch to sparse representations, Krylov-subspace methods (`options={"method": "krylov"}`), Monte-Carlo trajectories, or a GPU back-end before scaling up.

10. **Using deprecated `qutip.qip` namespace.** The legacy `qutip.qip` namespace is deprecated. New code should import from `qutip_qip` (the `qutip-qip` package, installed separately).

11. **QuTiP 5 API changes.** Solver options are now plain dictionaries (not `Options` objects). Floquet uses `FloquetBasis`. HEOM moved to `qutip.solver.heom`. Pin to `"qutip>=5.0,<6.0"` to protect scripts from silent breakage.

12. **Non-monotonic or single-point time grid.** QuTiP samples results at `tlist` points; a non-monotonic or single-point grid yields meaningless output rather than an error. Always validate `tlist` is 1-D, has at least two points, and is strictly increasing.

## Verification

1. **Install and confirm version:**
   ```bash
   uv pip install "qutip>=5.0,<6.0"
   python -c "import qutip; print(qutip.__version__)"
   ```
   Confirm a 5.x version is printed.

2. **Save and import helpers:**
   ```bash
   python -c "import qutip_helpers; print('helpers OK')"
   ```

3. **Run the damped oscillator example** and confirm `<n>(t)` tracks the analytic `|alpha|^2 * exp(-kappa * t)` envelope:
   ```python
   import numpy as np
   from qutip import coherent, destroy, mesolve, num

   tlist = np.linspace(0.0, 50.0, 200)
   a = destroy(20)
   H = 1.0 * a.dag() * a
   c_ops = [np.sqrt(0.1) * a]
   psi0 = coherent(20, 3.0)
   result = mesolve(H, psi0, tlist, c_ops, [num(20)])
   n_t = result.expect[0]
   expected = 9.0 * np.exp(-0.1 * tlist)
   assert np.allclose(n_t, expected, atol=0.5), "photon decay does not match analytic envelope"
   print("damped oscillator: PASS")
   ```

4. **Run the two-qubit entanglement example** and confirm concurrence decays monotonically to ~0 and that `tensor()` produced the correct `[[2, 2], [2, 2]]` dims:
   ```python
   from qutip import bell_state, tensor, qeye, sigmaz, mesolve, concurrence
   import numpy as np

   psi0 = bell_state("00")
   H = 0.0 * tensor(qeye(2), qeye(2))
   c_ops = [np.sqrt(0.1) * tensor(sigmaz(), qeye(2)),
            np.sqrt(0.1) * tensor(qeye(2), sigmaz())]
   tlist = np.linspace(0.0, 10.0, 100)
   result = mesolve(H, psi0, tlist, c_ops, [], options={"store_states": True})
   concurrences = [concurrence(s) for s in result.states]
   assert concurrences[-1] < 0.1, "concurrence did not decay"
   assert concurrences[0] > 0.9, "initial state not maximally entangled"
   print("entanglement decay: PASS")
   ```

5. **Render a Bloch sphere headless** and confirm the file is written:
   ```python
   from qutip import basis, Bloch
   import matplotlib.pyplot as plt

   b = Bloch()
   b.add_states(basis(2, 0))
   b.render()
   fig = plt.gcf()
   fig.savefig("bloch.png", dpi=150)
   plt.close(fig)
   import os; assert os.path.exists("bloch.png"), "bloch.png not written"
   print("bloch render: PASS")
   ```

6. **Call `steadystate` and confirm it returns without raising the residual-tolerance error:**
   ```python
   import numpy as np
   from qutip import num, destroy, liouvillian, steadystate, operator_to_vector

   a = destroy(10)
   H = num(10)
   c_ops = [np.sqrt(0.1) * a]
   L = liouvillian(H, c_ops)
   rho_ss = steadystate(L, method="svd", tol=1e-10)
   residual = (L * operator_to_vector(rho_ss)).norm()
   assert residual < 1e-6, f"steady-state residual {residual:.2e} too large"
   print(f"steady state: PASS (residual={residual:.2e})")
   ```

## Related Skills

- Quantum Information Theory
- Numerical Linear Algebra
- Python Scientific Stack (NumPy, SciPy, Matplotlib)
- Quantum Optics
