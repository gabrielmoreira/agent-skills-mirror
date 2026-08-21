---
name: excitation-signal-design
version: 1.2.1
description: "Design the excitation experiment for system identification — pick the input signal (step, multi-level step, PRBS, multisine, chirp), size the step magnitude, test duration, and sample rate, and collect a clean input/output record from a plant you can safely perturb. Triggers on 'step test', 'excitation signal', 'identification experiment', 'how long should the test run', 'what sample rate for identification'. Not for fitting parameters to an already-recorded response (use first-order-model-fitting) or turning an identified model into controller gains (use imc-tuning-rules)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Excitation Signal Design for System Identification

## When to Use

Identifying an unknown system means learning how its output reacts to a known input. You cannot estimate a model from passive observation alone, because if the input never moves you never see the dynamics — so you deliberately *excite* the system and watch it respond. This skill covers designing that experiment: choosing the signal, sizing it, and collecting a trustworthy record. Use it when:

- You are planning or running a **step test** to capture the dominant **process gain** and **time constant** of a first-order (or gently higher-order) plant — the two numbers that already determine most of a PID tuning.
- You need to decide **how large a step, how long to hold it, and how fast to sample** before touching the plant.
- You must choose **between excitation signals** (step vs. multi-level steps vs. PRBS vs. multisine vs. chirp) for the dynamics you care about.
- You need a clean, validated input-output record to hand to a fitting stage, and you can command the input directly from a known steady operating point.

If you only need a rough feel for the system, one good step test is usually enough; the value of extra tests drops quickly once the response is repeatable.

### When NOT to use

Route to the sibling skill when the question is downstream of the experiment:

| You actually need | Use instead |
| --- | --- |
| Fit `K` and `tau` to an already-recorded step response, with diagnostics | `first-order-model-fitting` |
| PI/PID gains from an identified first-order model | `imc-tuning-rules` |
| Implement the feedback loop itself | `pid-controller` |

Avoid an open-loop step test — and reach for a richer or safer method — when its assumptions break:

- **The system is unstable or unsafe to perturb.** An open-loop step on an unstable plant can run away before you collect useful data. Identify it in closed loop or with a bounded, reversible excitation instead.
- **Significant nonlinearities are present.** A single step only probes one amplitude in one direction. If gain depends on operating point, use multi-level steps, PRBS, or a chirp so you excite a range of conditions.
- **You need frequency-domain information.** Resonances and phase margins are far easier to read from a multisine or chirp than from a single transient.
- **You cannot reach a steady state.** Without a flat starting baseline you cannot separate the step response from drift already in progress.
- **Safety or regulatory constraints forbid open-loop testing.** Respect them; there is usually a closed-loop or simulation-based alternative.

## Prerequisites

- **Python 3.10+** with `numpy>=1.24` and `scipy>=1.10` installed.
- A plant or simulator you can safely command with a step input and that exposes a `step(command: float) -> StepResult` interface (see Procedure for the protocol definition).
- A known steady-state operating point from which to apply the step.
- On Windows hosts (primary), use PowerShell for any CLI commands. Example environment setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "numpy>=1.24" "scipy>=1.10"
```

## Procedure

### 1. Choose the excitation signal

A step is the default because it is simple, interpretable, and gentle on the plant. Move along the table only when the step's limitations bite:

| Signal | Choose when | It identifies |
| --- | --- | --- |
| Single step | Plant parks at steady state; dominant `K` and `tau` suffice | Gain and time constant of the dominant lag |
| Multi-level steps | Gain may vary with operating point; analysis must stay simple | `K` per operating level, local `tau` |
| PRBS | Process must keep running; amplitude must stay tightly bounded | Broadband linear dynamics up to the bit-rate bandwidth |
| Multisine | Energy wanted only at chosen frequencies; best SNR per test minute | Frequency response at the selected lines |
| Chirp (swept sine) | Quick frequency-response survey, resonances included | Magnitude/phase across the sweep band |

Two sizing rules carry over from steps to the richer signals: place the excitation bandwidth around the dynamics you expect (for PRBS, clock the bit period near `tau/3`), and keep amplitudes large enough to clear sensor noise but small enough to stay in the linear region.

The rest of this skill develops the step test fully, since it is the workhorse and its design logic (baseline, duration, sampling) transfers to every signal above.

### 2. Confirm the plant is at steady state

A step is only meaningful relative to a known baseline. If the output is still moving, you cannot attribute the response to your input. Wait until the output has been flat for at least one estimated time constant before proceeding.

### 3. Size the step magnitude

- **Too small:** the response drowns in sensor noise.
- **Too large:** you leave the linear region or saturate the actuator.
- **Target:** large enough that the steady-state change is clearly visible above noise (SNR > 10:1 as a rule of thumb), small enough that the actuator does not saturate and the plant stays in its linear operating range.

### 4. Set the test duration

The output of a first-order system reaches ~63% of its final change after one time constant, ~95% after three, and ~99% after five. Duration is expressed in time constants, not seconds:

- **Minimum (~3 τ):** enough to see the shape and a near-final value.
- **Recommended (3–5 τ):** the steady state is well defined, which sharply improves the gain estimate.
- **Why not "until it looks settled":** "looks settled" is biased by noise and by your monitor's scale. Sizing the test in time constants is objective and repeatable.

### 5. Set the sample rate

The sample period sets how well you resolve the fast initial rise:

- **Too slow:** you skip over the rise, losing the very information that pins down the time constant.
- **Too fast:** you collect redundant, noise-dominated points that add cost without adding information.
- **Target 10–20 samples per time constant.** That resolves the transient while keeping the dataset lean — the `StepTestConfig` below enforces this floor.

### 6. Define the data types and validated configuration

Record time, the output measurement (noise included), and the input command at each sample. The code below is the reusable core: the data types, a validated test configuration, and the collection loop. It is written with explicit type hints, validates its inputs up front, and refuses malformed samples so the fitting stage never sees corrupt data.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypedDict, runtime_checkable

import numpy as np


class StepResult(TypedDict):
    """One observation returned by the plant per sample period."""

    time: float    # seconds since the start of the test
    output: float  # measured output, including sensor noise
    input: float   # commanded input applied during this sample


@runtime_checkable
class SteppableSystem(Protocol):
    """Minimal interface a plant must expose to be driven by a step test.

    A Protocol (structural typing) is used rather than a base class because
    identification code must run against many backends — a simulated transfer
    function, a hardware-in-the-loop rig, a historian replay — none of which
    should have to inherit from us to be usable here.
    """

    def step(self, command: float) -> StepResult:
        """Apply ``command`` for one sample period and return the measurement."""
        ...


@dataclass(frozen=True)
class StepTestConfig:
    """Validated parameters for a single open-loop step test.

    Validation happens in ``__post_init__`` so a bad parameter is caught before
    any actuation. On real hardware a step test is a physical experiment; an
    invalid sample rate or a zero-duration run wastes a real opportunity, so
    failing fast with a clear message is far cheaper than discovering the
    mistake afterward.
    """

    step_magnitude: float            # commanded input level u
    estimated_time_constant: float   # best prior guess of tau, in seconds
    sample_period: float             # seconds between samples (dt)
    num_time_constants: float = 5.0  # how many tau to record

    def __post_init__(self) -> None:
        if not np.isfinite(self.step_magnitude) or self.step_magnitude == 0.0:
            raise ValueError("step_magnitude must be a non-zero, finite value.")
        if self.estimated_time_constant <= 0.0:
            raise ValueError("estimated_time_constant must be positive.")
        if self.sample_period <= 0.0:
            raise ValueError("sample_period must be positive.")
        if self.num_time_constants < 3.0:
            raise ValueError(
                "Record at least 3 time constants; fewer leaves the steady "
                "state poorly defined and the fit ill-conditioned."
            )
        samples_per_tau = self.estimated_time_constant / self.sample_period
        if samples_per_tau < 10.0:
            raise ValueError(
                f"sample_period too coarse: {samples_per_tau:.1f} samples per "
                "time constant (need >= 10 to capture the initial rise)."
            )

    @property
    def num_steps(self) -> int:
        """Total samples to collect across the requested test duration."""
        duration = self.num_time_constants * self.estimated_time_constant
        return max(1, int(round(duration / self.sample_period)))


def collect_step_test(
    system: SteppableSystem,
    config: StepTestConfig,
) -> list[StepResult]:
    """Drive ``system`` with one step and return the recorded time trace.

    Each returned sample is checked for completeness and finiteness, because a
    real driver can drop a field or emit a NaN on a transient glitch, and a
    single bad point can derail a least-squares fit.
    """
    if not isinstance(system, SteppableSystem):
        raise TypeError(
            "system must implement step(command: float) -> StepResult."
        )

    trace: list[StepResult] = []
    for _ in range(config.num_steps):
        sample = system.step(config.step_magnitude)
        for key in ("time", "output", "input"):
            value = sample.get(key)
            if value is None or not np.isfinite(value):
                raise ValueError(f"Plant returned invalid {key!r}: {value!r}.")
        trace.append(sample)
    return trace
```

### 7. Run the collection loop

Call `collect_step_test(system, config)` with your plant and validated config. The loop applies the step magnitude for `config.num_steps` samples, validates each returned sample, and returns the complete trace.

### 8. Validate test adequacy with a quick fit

The quickest check that your *experiment* was adequate — long enough, finely enough sampled, step large enough — is whether a first-order model explains the trace. A quick least-squares fit and its R² answer exactly that. Full parameter extraction, bounds, and residual diagnostics belong to `first-order-model-fitting`; this is only the adequacy gate.

```python
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit


def test_adequacy(trace: Sequence[StepResult]) -> float:
    """Return the R^2 of a quick first-order fit to a step-test trace.

    A high value (> ~0.98 for a clean plant) confirms the test design was
    adequate. A low value means redesign the test (longer hold, finer
    sampling, larger step) before bothering with careful fitting.
    """
    if len(trace) < 4:
        raise ValueError(f"Need >= 4 samples to fit 3 parameters; got {len(trace)}.")

    times = np.asarray([s["time"] for s in trace], dtype=np.float64)
    outputs = np.asarray([s["output"] for s in trace], dtype=np.float64)
    u = float(trace[-1]["input"])
    if abs(u) < np.finfo(np.float64).eps:
        raise ValueError("Step magnitude is ~0; the input never moved.")

    def model(
        t: NDArray[np.float64], gain: float, tau: float, y0: float
    ) -> NDArray[np.float64]:
        return y0 + gain * u * (1.0 - np.exp(-t / tau))

    span = float(times[-1] - times[0])
    tiny = float(np.finfo(np.float64).eps)
    initial_guess = (
        float((outputs[-1] - outputs[0]) / u),  # K
        max(span / 5.0, tiny),                  # tau
        float(outputs[0]),                      # y0
    )
    params, _ = curve_fit(
        model,
        times,
        outputs,
        p0=initial_guess,
        # tau bounded strictly positive; zero/negative tau is unphysical.
        bounds=((-np.inf, tiny, -np.inf), (np.inf, np.inf, np.inf)),
        maxfev=10_000,
    )
    predicted = model(times, *params)
    residual_ss = float(np.sum((outputs - predicted) ** 2))
    total_ss = float(np.sum((outputs - float(np.mean(outputs))) ** 2))
    return 1.0 - residual_ss / total_ss if total_ss > 0.0 else 0.0
```

### 9. Hand the trace to the fitting stage

Pass the validated trace to `first-order-model-fitting` for full parameter extraction (`K`, `tau`, `y0`) with confidence intervals and residual diagnostics. Validate the identified model against an **independent** trace, not just the data it was fitted on.

## Expected Response Shape

For a first-order system the step response is a single exponential, which is exactly why two parameters suffice to describe it:

- **Initial:** output sits at its starting value `y0`.
- **Rising:** the output approaches the new steady state exponentially; the *rate* of approach is governed by the time constant `tau`.
- **Final:** it asymptotes to `y0 + K*u`, where the *distance moved per unit input* is the gain `K`.

The closed-form response is:

```
y(t) = y0 + K * u * (1 - exp(-t / tau))
```

where `K` is the process gain, `tau` the time constant, `u` the step magnitude, and `y0` the initial output.

## Examples

### End-to-end step test with a simulated plant

This concrete plant stands in for the "unknown" system so the example runs end to end. It integrates the first-order lag exactly one sample period at a time and adds optional Gaussian sensor noise. It builds on the imports and types defined in **Procedure step 6** above (only `field` is newly required).

```python
from dataclasses import dataclass, field

import numpy as np


@dataclass
class FirstOrderPlant:
    """A discrete-time first-order plant used to generate realistic test data.

    Implements y(t) = K*u*(1 - exp(-t/tau)) by recursively applying the exact
    one-step discretization of a first-order lag, with additive measurement
    noise. It satisfies the ``SteppableSystem`` protocol via its ``step`` method.
    """

    gain: float            # steady-state output per unit input (K)
    time_constant: float   # seconds (tau)
    sample_period: float   # seconds between samples (dt)
    noise_std: float = 0.0
    _rng: np.random.Generator = field(default_factory=np.random.default_rng)
    _elapsed: float = 0.0
    _state: float = 0.0

    def __post_init__(self) -> None:
        if self.time_constant <= 0.0:
            raise ValueError("time_constant must be positive.")
        if self.sample_period <= 0.0:
            raise ValueError("sample_period must be positive.")
        if self.noise_std < 0.0:
            raise ValueError("noise_std cannot be negative.")

    def step(self, command: float) -> StepResult:
        if not np.isfinite(command):
            raise ValueError(f"command must be finite, got {command!r}.")
        # Exact discretization of a first-order lag over one sample period:
        # the state relaxes toward K*command with factor alpha = exp(-dt/tau).
        alpha = float(np.exp(-self.sample_period / self.time_constant))
        target = self.gain * command
        self._state = alpha * self._state + (1.0 - alpha) * target
        self._elapsed += self.sample_period
        measured = self._state + float(self._rng.normal(0.0, self.noise_std))
        return StepResult(
            time=self._elapsed,
            output=float(measured),
            input=float(command),
        )


# Collect a trace from the (pretend unknown) plant.
plant = FirstOrderPlant(
    gain=2.0,
    time_constant=4.0,
    sample_period=0.2,
    noise_std=0.01,
    _rng=np.random.default_rng(seed=42),
)
config = StepTestConfig(
    step_magnitude=1.0,
    estimated_time_constant=4.0,
    sample_period=0.2,
    num_time_constants=5.0,
)
trace = collect_step_test(plant, config)
print(f"collected {len(trace)} samples over {trace[-1]['time']:.1f} s")
```

### Check adequacy

```python
r_squared = test_adequacy(trace)
print(f"fit R^2 : {r_squared:.4f}")  # ~1.0 => the test design was adequate
```

Running both blocks collects 100 samples over 20 seconds and yields an R² very close to 1.0, confirming the test was long enough and finely enough sampled to identify the plant.

## Pitfalls

- **Cutting the test short.** The tail is where the steady state — and therefore the gain — is read; a truncated test systematically underestimates `K`.
- **Wrong step size.** Too small and the response drowns in sensor noise; too large and you leave the linear region or saturate the actuator. Both extremes corrupt the estimate.
- **Starting before steady state.** Drift already in progress gets attributed to your input and biases both `K` and `tau`.
- **Over-smoothing the data.** A least-squares fit already averages noise across every sample. Aggressive pre-filtering distorts the transient and biases `tau`.
- **Piling up sloppy tests.** One clean step, started from a genuine steady state, usually identifies a first-order system to within a few percent — better than averaging several rushed runs.
- **Unsafe open-loop testing on unstable plants.** An open-loop step on an unstable plant can run away before you collect useful data. Use closed-loop identification or bounded, reversible excitation instead.
- **Ignoring nonlinearities.** A single step only probes one amplitude in one direction. If gain depends on operating point, use multi-level steps, PRBS, or a chirp.

## Verification

- [ ] Verify the system is at steady state before the step, so the response is attributable to your input and not to pre-existing drift.
- [ ] Confirm the test spans 3–5 time constants, so the steady state (and hence the gain) is well defined rather than read off a truncated tail.
- [ ] Validate 10–20 samples per time constant, so the fast initial rise that pins down `tau` is actually resolved.
- [ ] Check every recorded sample contains finite `time`, `input`, and `output` values (the collection loop enforces this).
- [ ] Ensure the step magnitude clears sensor noise without saturating the actuator, keeping the response both measurable and linear.
- [ ] Run `test_adequacy` and confirm R² is high (typically > 0.98 for a clean first-order test); a low value signals a test-design problem — fix the experiment before fitting.
- [ ] Hand the trace to `first-order-model-fitting` for parameter extraction, and validate the identified model against an independent trace, not just the data it was fitted on.
- [ ] Inspect residuals for structure (curvature, asymmetry); systematic patterns indicate nonlinearity or higher-order dynamics that warrant a richer excitation such as PRBS, multi-level steps, or a chirp.

## Related Skills

- `first-order-model-fitting` — fit `K` and `tau` (with diagnostics) to the trace this skill collects.
- `imc-tuning-rules` — turn the identified first-order model into PI/PID gains.
- `pid-controller` — implement the resulting feedback loop.
