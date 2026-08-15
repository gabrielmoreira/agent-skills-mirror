---
name: simulation-metrics
version: 1.1.1
description: "Scores control-loop step traces into 10-90 rise time, signed overshoot percent, tail-averaged steady-state error, and last-exit settling time with NumPy. Use for PID iteration or a written 2-percent-band spec. Not a Bode/Nyquist margin calculator and never a substitute for filtering a noisy measurement."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Control System Performance Metrics

## Overview

This skill provides a small, self-contained Python module (`simulation_metrics.py`) that computes the four classic time-domain performance metrics for a control system's step response: **rise time**, **overshoot percentage**, **steady-state error**, and **settling time**. These metrics turn a wiggly response curve into a small set of comparable scalars, enabling objective, repeatable evaluation against design specifications such as "≤10% overshoot, settle inside the 2% band in under 0.5 s."

Two deliberate engineering choices shape the implementation:

- **NumPy for the math.** Vectorized threshold detection (`np.flatnonzero`) and stable tail averaging (`np.mean`) stay fast and numerically well-behaved even on long, fine-grained traces, where a hand-rolled Python loop would be slow and easy to get subtly wrong.
- **Explicit type hints and up-front validation.** The annotations make the contract obvious to callers and to static checkers (no untyped/`Any` parameters), and the shared validator catches malformed data *before* any indexing happens. Every metric assumes `times[i]` lines up with `values[i]`; a length mismatch or a non-monotonic time vector would otherwise yield a plausible but incorrect answer instead of an error.

## When to Use

Reach for this skill when you need to put hard numbers on a control system's step response — quantitative, time-domain figures you can check against a design spec. Rise time, overshoot, steady-state error, and settling time answer, respectively: *how fast does it react, how far does it overshoot, where does it finally land, and when is it effectively done?*

**Trigger keywords:** rise time, overshoot, settling time, steady-state error, step response, PID tuning, control system performance, simulation metrics, time-domain analysis, 2% band, 10-90 rise.

In practice you want these whenever you are:

1. Tuning a PID loop and need quantitative feedback on each iteration.
2. Comparing two controller designs head-to-head on the same step input.
3. Proving that a simulation meets a written requirement (e.g., "≤10% overshoot, settle inside the 2% band in under 0.5 s").

### When *not* to use (and why it matters)

- **These are time-domain metrics, not frequency-domain ones.** They are computed directly from a response-versus-time curve, so they say nothing about Bode/Nyquist behavior or gain/phase stability margins. A system can post excellent time-domain numbers and still be fragile to phase lag or modeling error — if margins are what you care about, use a frequency-domain tool instead.
- **They assume a reasonably clean signal.** Every function reads the trajectory you hand it literally, noise and all. On a high-bandwidth, noisy trace a single spike can register as overshoot or kick the settling time far to the right, producing pessimistic-but-wrong results. Low-pass filter or smooth the data first so the metrics describe the underlying response rather than the measurement noise.
- **A zero setpoint is rejected on purpose.** Overshoot and the tolerance band are normalized by the target, so `target == 0` would divide by zero. Rather than return a misleading number, the functions raise `ValueError`. The same philosophy applies to empty, length-mismatched, or non-finite arrays: a silently-wrong metric buried in a tuning report is far more dangerous than a loud, early failure.

## Prerequisites

- **Python 3.10+** (uses `from __future__ import annotations` and `X | Y` union syntax).
- **NumPy** installed: `pip install numpy`
- **NumPy type stubs** (optional but recommended for static checking): `pip install numpy-types`
- On Windows (PowerShell), ensure Python is on your `PATH`:
  ```powershell
  python --version
  python -c "import numpy; print(numpy.__version__)"
  ```

## Procedure

### Step 1 — Create the module file

Create `simulation_metrics.py` in your project. The module contains shared validation helpers and four metric functions. All definitions below belong in this single file.

### Step 2 — Add shared imports and validation helpers

These definitions are the foundation for every metric that follows; keep them at the top of the same module so the functions below can reuse them. The helpers exist so the *why* of each guard lives in one place rather than being copy-pasted (and drifting) across four functions.

```python
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

# A concrete, dense float array is what every metric operates on internally.
FloatArray = npt.NDArray[np.float64]
# Callers may pass plain Python sequences or numpy arrays; both are accepted.
SignalInput = Sequence[float] | FloatArray


def _as_validated_signal(
    times: SignalInput,
    values: SignalInput,
) -> tuple[FloatArray, FloatArray]:
    """Coerce raw inputs into aligned float64 arrays and reject malformed data.

    Why validate up front: every metric indexes by position and assumes that
    ``times[i]`` corresponds to ``values[i]``. A length mismatch, a stray NaN, or a
    non-monotonic time vector would silently produce a plausible-but-wrong number,
    which is worse in a tuning report than a hard failure. Strictly increasing time
    is required because the interpolation steps below need distinct, ordered x-values.
    """
    t = np.asarray(times, dtype=np.float64)
    v = np.asarray(values, dtype=np.float64)

    if t.ndim != 1 or v.ndim != 1:
        raise ValueError("times and values must be one-dimensional sequences.")
    if t.size == 0 or v.size == 0:
        raise ValueError("times and values must be non-empty.")
    if t.size != v.size:
        raise ValueError(
            f"times and values must be the same length (got {t.size} and {v.size})."
        )
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(v)):
        raise ValueError("times and values must not contain NaN or infinity.")
    if np.any(np.diff(t) <= 0.0):
        raise ValueError("times must be strictly increasing.")
    return t, v


def _validate_target(target: float) -> float:
    """Validate the setpoint, guarding the division-by-zero that a 0 target causes.

    Overshoot and the settling tolerance band are both normalized by the target, so a
    zero setpoint is undefined for these metrics rather than merely inconvenient.
    """
    target = float(target)
    if not np.isfinite(target):
        raise ValueError("target must be a finite number.")
    if target == 0.0:
        raise ValueError(
            "target must be non-zero; metrics are normalized by the target and a "
            "zero setpoint would divide by zero."
        )
    return target


def _first_crossing_time(
    times: FloatArray,
    normalized: FloatArray,
    level: float,
) -> float | None:
    """Return the linearly interpolated time at which ``normalized`` first reaches ``level``.

    Interpolating between the two bracketing samples removes the discretization bias
    you get from snapping to the nearest sample time, which matters when the solver
    step is coarse relative to how quickly the response moves. Returns ``None`` when the
    level is never reached within the captured window.
    """
    reached = np.flatnonzero(normalized >= level)
    if reached.size == 0:
        return None

    idx = int(reached[0])
    if idx == 0:
        # Already at/above the level at the first sample; there is no earlier point
        # to interpolate against, so report the first timestamp as-is.
        return float(times[0])

    n_prev, n_curr = float(normalized[idx - 1]), float(normalized[idx])
    t_prev, t_curr = float(times[idx - 1]), float(times[idx])
    if n_curr == n_prev:
        return t_curr

    fraction = (level - n_prev) / (n_curr - n_prev)
    return t_prev + fraction * (t_curr - t_prev)
```

### Step 3 — Add `rise_time`

Rise time is the interval taken to climb from 10% to 90% of the target. The 10–90 band is the convention rather than 0–100% for a concrete reason: a step response approaches its final value asymptotically, so "time to reach 100%" is often *never* well-defined, while the first instants near 0% are dominated by sensor dead-zone. The 10–90 window is the standard, reproducible way to capture *how fast* the system reacts. Returning `None` when the 90% level is never reached is itself a useful diagnostic — it means the system is too slow or unstable to qualify within the simulated window.

```python
def rise_time(
    times: SignalInput,
    values: SignalInput,
    target: float,
    low: float = 0.10,
    high: float = 0.90,
) -> float | None:
    """Time to climb from ``low`` (10%) to ``high`` (90%) of the target.

    The thresholds are exposed as parameters but default to the standard 10/90 band so
    callers can switch to, say, 5/95 without rewriting the function. The crossings are
    interpolated between samples for sub-step accuracy, and the calculation is sign-aware
    via the normalized signal, so it works for negative setpoints too. Returns ``None``
    if the response never reaches the high threshold in the captured window.
    """
    t, v = _as_validated_signal(times, values)
    target = _validate_target(target)
    if not (0.0 <= low < high <= 1.0):
        raise ValueError(f"Require 0 <= low < high <= 1 (got low={low}, high={high}).")

    # Dividing by the target maps the response onto a 0 -> 1 progress curve regardless
    # of the target's sign, so the same >= comparison detects crossings either way.
    normalized = v / target
    t_low = _first_crossing_time(t, normalized, low)
    t_high = _first_crossing_time(t, normalized, high)
    if t_low is None or t_high is None:
        return None
    return t_high - t_low
```

### Step 4 — Add `overshoot_percent`

Overshoot is the peak excursion beyond the target, expressed as a percentage of the target. Normalizing by the target is what makes the figure meaningful across setpoints: a 2-unit overshoot is trivial for a setpoint of 500 but enormous for a setpoint of 5. The percentage form is the dimensionless number engineers compare against a spec like "≤10% overshoot." It matters physically because excessive overshoot can saturate or damage actuators, trip safety limits, or signal an under-damped, ringing loop.

```python
def overshoot_percent(
    values: SignalInput,
    target: float,
) -> float:
    """Peak excursion beyond the target, as a percentage of the target.

    Sign-aware: for a negative setpoint the worst-case excursion is the *minimum*, not
    the maximum, so the peak is taken in the direction of the target's sign. Returns
    ``0.0`` for critically- or over-damped responses that never pass the target, which
    is the correct answer rather than a small negative artifact.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        raise ValueError("values must be non-empty.")
    if not np.all(np.isfinite(v)):
        raise ValueError("values must not contain NaN or infinity.")
    target = _validate_target(target)

    # The most extreme sample in the direction the system was commanded to move.
    peak = float(np.max(v)) if target > 0 else float(np.min(v))
    # Positive only when the peak actually exceeds the target; clamp so a response
    # that never reaches the target reports 0.0 overshoot rather than a negative value.
    excess_fraction = (peak - target) / target
    return max(0.0, excess_fraction * 100.0)
```

### Step 5 — Add `steady_state_error`

Steady-state error is the absolute residual gap between the target and the value the system finally settles at. The function averages the last `final_fraction` of the record rather than reading the single last sample, and the reason is robustness: the final sample can still carry ripple or measurement noise, whereas averaging the tail gives a stable estimate of where the response truly settled. A non-zero result on a loop with integral action usually points to actuator saturation or an un-modeled disturbance — i.e. it is diagnostic, not just a pass/fail number.

```python
def steady_state_error(
    values: SignalInput,
    target: float,
    final_fraction: float = 0.10,
) -> float:
    """Absolute residual error between the target and the settled output.

    Averaging the final ``final_fraction`` of the record smooths out late ripple so the
    estimate reflects the steady value rather than a single noisy endpoint. The window is
    clamped to contain at least one sample, so short runs do not produce an empty slice.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        raise ValueError("values must be non-empty.")
    if not np.all(np.isfinite(v)):
        raise ValueError("values must not contain NaN or infinity.")
    target = _validate_target(target)
    if not (0.0 < final_fraction <= 1.0):
        raise ValueError(f"final_fraction must be in (0, 1] (got {final_fraction}).")

    n = v.size
    # Guarantee at least one sample in the averaging window even when final_fraction
    # rounds the window size below one on a short run.
    start = min(n - 1, int(n * (1.0 - final_fraction)))
    final_avg = float(np.mean(v[start:]))
    return abs(target - final_avg)
```

### Step 6 — Add `settling_time`

Settling time is the earliest time after which the response stays inside a ±tolerance band around the target for the rest of the record. The subtle part is *why we key off the last exit from the band rather than the first entry*: an under-damped system can dip into the band, overshoot back out, and re-enter. The metric is defined as the instant after which it never leaves again, so the code locates the **last** out-of-band sample and reports the crossing into the band that follows it. The tolerance is a fraction of the target magnitude (0.02 → the classic 2% band, 0.05 → 5%), because "close enough" is naturally expressed relative to the commanded value.

```python
def settling_time(
    times: SignalInput,
    values: SignalInput,
    target: float,
    tolerance: float = 0.02,
) -> float | None:
    """Earliest time after which the response stays within ±tolerance of the target.

    Keying off the last out-of-band sample correctly handles a response that re-enters
    the band after an overshoot. The exact band-crossing instant is interpolated between
    the last out-of-band sample and the first in-band sample for sub-step accuracy.
    Returns ``None`` when the response is still outside the band at the end of the window
    (it has not settled within the captured time), and ``times[0]`` when it is already
    inside the band from the very first sample.
    """
    t, v = _as_validated_signal(times, values)
    target = _validate_target(target)
    if not (0.0 < tolerance < 1.0):
        raise ValueError(f"tolerance must be in (0, 1) (got {tolerance}).")

    band = abs(target) * tolerance
    outside = np.flatnonzero(np.abs(v - target) > band)

    if outside.size == 0:
        return float(t[0])  # Within tolerance from the very first sample.

    last_outside = int(outside[-1])
    settled_idx = last_outside + 1
    if settled_idx >= t.size:
        return None  # Never re-entered the band before the run ended.

    # Interpolate the exact moment the trajectory re-enters the band, crossing whichever
    # boundary (upper or lower) it last violated.
    v_out = float(v[last_outside])
    v_in = float(v[settled_idx])
    boundary = (target + band) if v_out > target else (target - band)
    denom = v_in - v_out
    if denom == 0.0:
        return float(t[settled_idx])

    fraction = (boundary - v_out) / denom
    fraction = min(1.0, max(0.0, fraction))  # Stay within the bracketing interval.
    return float(t[last_outside]) + fraction * (float(t[settled_idx]) - float(t[last_outside]))
```

### Step 7 — Call the functions on your simulation output

Import the module and call each function on paired `times` and `values` arrays plus the commanded `target` setpoint. Always handle `None` return values from `rise_time` and `settling_time` as first-class outcomes, not crashes.

## Examples

### Worked example: second-order-like step response

```python
from __future__ import annotations

# Each row is one simulation timestep captured from the solver.
results: list[dict[str, float]] = [
    {"time": 0.0, "value": 0.0},
    {"time": 0.1, "value": 5.0},
    {"time": 0.2, "value": 15.0},
    {"time": 0.3, "value": 32.0},   # transient peak -> overshoot
    {"time": 0.4, "value": 30.5},
    {"time": 0.5, "value": 30.1},
    {"time": 0.6, "value": 30.0},
]

times: list[float] = [row["time"] for row in results]
values: list[float] = [row["value"] for row in results]
target: float = 30.0

rt = rise_time(times, values, target)
st = settling_time(times, values, target)

print(f"Rise time:     {rt:.4f} s" if rt is not None else "Rise time:     never reached 90%")
print(f"Overshoot:     {overshoot_percent(values, target):.2f} %")
print(f"SS error:      {steady_state_error(values, target):.4f}")
print(f"Settling time: {st:.4f} s" if st is not None else "Settling time: never settled")

# Expected output:
# Rise time:     0.2106 s
# Overshoot:     6.67 %
# SS error:      0.0000
# Settling time: 0.3933 s
```

### Running on Windows (PowerShell)

```powershell
python simulation_metrics.py
```

Or run a quick inline check:

```powershell
python -c "from simulation_metrics import rise_time, overshoot_percent, steady_state_error, settling_time; print('all imports OK')"
```

## Pitfalls

1. **Noisy signals produce wrong metrics.** A single noise spike can register as overshoot or push the settling time far right. Always low-pass filter or smooth the data before computing metrics so they describe the underlying response, not measurement noise.

2. **`target == 0` raises `ValueError` by design.** Overshoot and the tolerance band are normalized by the target. Rather than returning a misleading number, the functions fail loudly. If your setpoint is zero, you need a different metric definition (e.g., absolute tolerance band instead of relative).

3. **Non-monotonic time vectors are rejected.** The interpolation steps require strictly increasing, distinct x-values. Duplicate or backwards timestamps raise `ValueError` immediately — this is intentional, as interpolation on non-monotonic data would produce silently wrong results.

4. **`settling_time` keys off the *last* out-of-band sample, not the first entry.** An under-damped system can dip into the band, overshoot back out, and re-enter. The metric is defined as the instant after which it *never* leaves again. If you mistakenly look for the first entry, you will report a settling time that is too optimistic.

5. **`steady_state_error` on a short run still works.** The averaging window is clamped to contain at least one sample even when `final_fraction` rounds the window below one. However, on very short runs the "steady-state" estimate is necessarily coarse — use a longer simulation window when possible.

6. **`overshoot_percent` returns `0.0` for over-damped responses.** This is the correct answer, not a bug. A response that never reaches the target has zero overshoot, not a negative overshoot.

7. **Negative setpoints are handled, but the peak direction flips.** For `target < 0`, the worst-case excursion is the *minimum* of the signal, not the maximum. The code handles this automatically via the sign check, but be aware when interpreting results.

8. **Plain Python lists and numpy arrays produce identical results.** The `_as_validated_signal` helper coerces both to `float64` arrays. Do not worry about which type you pass — but be aware that very large lists will consume memory during conversion.

## Verification

Run these checks after implementing the module to confirm correctness:

- [ ] **Import check** — all four functions import without error:
  ```powershell
  python -c "from simulation_metrics import rise_time, overshoot_percent, steady_state_error, settling_time; print('OK')"
  ```

- [ ] **Worked example** — run the worked example above and confirm output matches:
  ```
  Rise time:     0.2106 s
  Overshoot:     6.67 %
  SS error:      0.0000
  Settling time: 0.3933 s
  ```

- [ ] `rise_time` returns `None` when the 90% level is never reached, and interpolates the 10%/90% crossings between samples rather than snapping to the nearest sample time.

- [ ] `overshoot_percent` returns `0.0` for over- or critically-damped responses and is sign-correct for negative setpoints (it measures the minimum excursion when `target < 0`).

- [ ] `settling_time` keys off the *last* out-of-band sample (so re-entry after an overshoot is handled) and interpolates the band-crossing instant; it returns `None` when the response is still outside the band at the end of the window.

- [ ] `steady_state_error` averages at least one sample even when `final_fraction` rounds the window below one sample on a short run.

- [ ] Input validation rejects empty, length-mismatched, non-finite, or non-monotonic-time data with a clear `ValueError` instead of returning a plausible-but-wrong number:
  ```powershell
  python -c "from simulation_metrics import rise_time; rise_time([0,1,2], [1,2], 10)"
  # Should raise: ValueError: times and values must be the same length
  ```

- [ ] `target == 0` raises (the division-by-zero guard):
  ```powershell
  python -c "from simulation_metrics import overshoot_percent; overshoot_percent([1,2,3], 0)"
  # Should raise: ValueError: target must be non-zero...
  ```

- [ ] Inputs supplied as plain Python lists and as numpy arrays produce identical results.

- [ ] Validate against a known second-order step response: compare the computed metrics to the closed-form values for a chosen damping ratio (ζ) and natural frequency (ωn).

## Related skills

- system-stability-analysis
- pid-tuning-optimization
- signal-processing-filters
- time-series-analysis
