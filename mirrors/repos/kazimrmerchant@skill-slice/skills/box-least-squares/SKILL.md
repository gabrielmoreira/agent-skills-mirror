---
name: box-least-squares
version: 1.1.1
description: "Runs Astropy BoxLeastSquares (BLS) on photometric time series: autopower/power grids, depth SNR, odd/even vetting. Use for periodic box-shaped transit dips or eclipsing binaries (Kovács 2002). Not for Transit Least Squares limb-darkened templates, Lomb-Scargle sinusoids, or non-photometric series. API: astropy.timeseries.BoxLeastSquares (Astropy 8)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

The Box Least Squares (BLS) periodogram detects transiting exoplanets and eclipsing binaries in photometric time series. It models a transit as a periodic, upside-down top hat (a "box") and reports the period, duration, depth, and reference epoch that best fit the data.

A box works well because a transit is, to first order, a flat-bottomed dip — the star's brightness drops while the companion is fully in front of it, then recovers. Describing that dip with only four numbers (period, epoch, duration, depth) keeps the model cheap to evaluate, so BLS can scan a very dense grid of trial periods in a reasonable amount of time. That efficiency is why BLS remains the default first pass for most transit searches.

BLS walks a grid of trial periods. At each period it phase-folds the light curve, slides a box of each trial duration across the folded phase, and finds the box placement that, when subtracted, best reduces the residual scatter. The "power" at that period is the value of the chosen objective at its best box placement.

Key parameters:

- **Duration grid.** You supply the set of trial transit durations. The search is only as good as this grid: if none of your trial durations is close to the true one, the box cannot line up with the real dip and the peak weakens. A handful of durations spanning the physically plausible range (often a few percent of a day up to a fraction of a day) is usually enough.
- **`frequency_factor` and `oversample`.** These set how finely the period and phase grids are sampled. Finer grids are less likely to step over a narrow transit's true period, but cost more compute. A factor that is too coarse can miss a real signal entirely; one that is too fine just wastes time. `autopower` picks sensible defaults from your duration grid and data baseline.
- **`objective`.** `'likelihood'` (Astropy's default) locates the peak using the proper statistical objective — the log-likelihood of the box model. `'snr'` instead ranks by depth signal-to-noise. The examples optimize on `'likelihood'` to *find* the peak and then report `depth_snr` as a separate vetting number, so you get the principled search and the interpretable metric.

Use the `autopower(durations)` method when you want Astropy to build the period grid for you from the duration set and the data baseline. Use `power(periods, durations)` when you already have a specific period grid in mind and want full control over it.

## When to Use

Reach for BLS when:

- You want a fast, dependency-light search — `BoxLeastSquares` ships inside Astropy's `astropy.timeseries`, so there is nothing extra to install or maintain.
- You need quantitative vetting statistics (depth signal-to-noise, an odd/even-transit comparison, per-transit counts) rather than just a "best period."
- You want fine control over the period and duration grids, because you already have a prior on the orbital period (for example from a previous detection or from the observing cadence).
- Your transits are reasonably well sampled and not extremely shallow, so the sharp-edged box is a good enough match to the true rounded transit shape.

**Do NOT use BLS when:**

- **Prefer Transit Least Squares (TLS) for maximum sensitivity, shallow transits, or grazing/partial transits.** TLS correlates the light curve against a physically motivated, limb-darkened transit template instead of a box. Because the template matches the real morphology, more of the transit signal lands in the detection statistic, which matters most exactly when the dip is small or the geometry is grazing. Note that BLS is *not* deprecated — it remains fully supported in Astropy. The choice between BLS and TLS is about signal shape and sensitivity, not obsolescence.
- **Prefer the Lomb-Scargle periodogram for smooth, continuous variability** such as stellar rotation, pulsations, or other quasi-sinusoidal signals. Those variations are well described by sinusoids, so a sinusoidal basis fits them with far fewer spurious harmonics than a box would. Forcing a box onto a sine wave produces a forest of misleading peaks.

## Prerequisites

- **Python 3.9+** with `astropy >= 3.1` (BLS has lived in `astropy.timeseries` since Astropy 3.1; it was previously `astropy.stats.BoxLeastSquares`).
- **NumPy and SciPy** — Astropy's compiled BLS core depends on these. Keep the stack reasonably current for speedups and upstream security/correctness fixes.
- **matplotlib** — required only for the phase-folded plotting step.

Install or verify on Windows PowerShell:

```powershell
python -m pip install astropy numpy scipy matplotlib
python -c "from astropy.timeseries import BoxLeastSquares; print('BLS available')"
```

## Procedure

### Step 1 — Validate and clean the light curve

Guarantee the invariants BLS relies on: one-dimensional, time-ordered samples, all finite, with strictly positive uncertainties for any point that will be weighted. Reject violations here, with a clear message, instead of letting them surface as a phantom periodogram peak later.

```python
from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray

import astropy.units as u
from astropy.units import Quantity


def _as_float_array(values: object, name: str) -> NDArray[np.float64]:
    """Coerce array-like (or a Quantity) to a 1-D float64 array."""
    if isinstance(values, Quantity):
        values = values.value
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be 1-D; got {array.ndim} dimensions.")
    return array


def _as_day_array(times: object) -> NDArray[np.float64]:
    """Coerce a time array to float64 days, converting units if needed."""
    if isinstance(times, Quantity):
        try:
            return np.asarray(times.to_value(u.day), dtype=np.float64)
        except u.UnitConversionError as exc:
            raise ValueError("time must be convertible to days.") from exc
    return _as_float_array(times, "time")


def validate_light_curve(
    time: NDArray[np.float64] | Quantity,
    flux: NDArray[np.float64] | Quantity,
    flux_err: NDArray[np.float64] | Quantity | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64] | None]:
    """Validate, clean, and time-sort a light curve for BLS.

    Returns finite, ascending-time arrays of (time_days, flux, flux_err).
    Points with non-finite values, or non-positive uncertainties, are dropped
    because they would corrupt the weighted chi-square that BLS minimizes.
    """
    t = _as_day_array(time)
    f = _as_float_array(flux, "flux")

    if t.shape != f.shape:
        raise ValueError(
            f"time and flux must match in length; got {t.shape} and {f.shape}."
        )
    if t.size < 3:
        raise ValueError("Need at least 3 samples to constrain a transit box.")

    finite = np.isfinite(t) & np.isfinite(f)

    e: NDArray[np.float64] | None = None
    if flux_err is not None:
        e = _as_float_array(flux_err, "flux_err")
        if e.shape != f.shape:
            raise ValueError("flux_err must match the shape of flux.")
        # A zero or negative error implies infinite weight; exclude those points.
        finite &= np.isfinite(e) & (e > 0.0)

    if not finite.any():
        raise ValueError("No finite, positively-weighted samples remain after cleaning.")

    order = np.argsort(t[finite])
    t_clean = t[finite][order]
    f_clean = f[finite][order]
    e_clean = e[finite][order] if e is not None else None
    return t_clean, f_clean, e_clean
```

### Step 2 — Run the BLS search

This wrapper attaches day units, picks a sensible default duration grid, and rejects non-physical arguments (negative durations, an unknown objective, a maximum period longer than the data span — which BLS could never actually confirm).

```python
from astropy.timeseries import BoxLeastSquares, BoxLeastSquaresResults


def build_bls_and_search(
    time: NDArray[np.float64] | Quantity,
    flux: NDArray[np.float64] | Quantity,
    flux_err: NDArray[np.float64] | Quantity | None = None,
    durations: Quantity | None = None,
    minimum_period: Quantity | None = None,
    maximum_period: Quantity | None = None,
    frequency_factor: float = 5.0,
    objective: str = "likelihood",
) -> tuple[BoxLeastSquares, BoxLeastSquaresResults]:
    """Validate inputs, build a BoxLeastSquares model, and run autopower.

    Optimizes the statistically principled log-likelihood by default; depth SNR
    is reported separately during vetting (see Step 3).
    """
    t_days, f_clean, e_clean = validate_light_curve(time, flux, flux_err)

    if durations is None:
        # A small spread of plausible transit durations, in days.
        durations = np.array([0.05, 0.08, 0.12, 0.16, 0.20]) * u.day
    if not isinstance(durations, Quantity):
        raise TypeError(
            "durations must be an astropy Quantity, e.g. np.array([0.05, 0.1, 0.2]) * u.day."
        )
    duration_days = np.atleast_1d(np.asarray(durations.to_value(u.day), dtype=np.float64))
    if np.any(duration_days <= 0.0):
        raise ValueError("All trial durations must be strictly positive.")

    if objective not in {"likelihood", "snr"}:
        raise ValueError("objective must be 'likelihood' or 'snr'.")

    if frequency_factor <= 0.0:
        raise ValueError("frequency_factor must be positive.")

    baseline_days = float(t_days[-1] - t_days[0])
    if np.any(duration_days >= baseline_days):
        raise ValueError("A trial duration is as long as the whole observing baseline.")
    if maximum_period is not None and float(maximum_period.to_value(u.day)) > baseline_days:
        warnings.warn(
            "maximum_period exceeds the observing baseline; BLS cannot confirm a "
            "period longer than the data span.",
            stacklevel=2,
        )

    model = BoxLeastSquares(t_days * u.day, f_clean, dy=e_clean)
    results = model.autopower(
        durations,
        minimum_period=minimum_period,
        maximum_period=maximum_period,
        frequency_factor=frequency_factor,
        objective=objective,
    )
    return model, results
```

### Step 3 — Summarize and vet the best candidate

`compute_stats` returns a dictionary whose depth-related entries are `(value, uncertainty)` pairs, *not* scalars — a detail that is easy to get wrong. The depth signal-to-noise lives on the periodogram result (`results.depth_snr`), not in the stats dictionary. The helper below extracts both correctly and packages them into an explicit, frozen dataclass so downstream code has a typed, immutable summary to work with.

The odd/even depth comparison is the single most useful vetting number here: an eclipsing binary often shows alternating deep (primary) and shallow (secondary) eclipses, so a large odd-vs-even depth difference relative to its uncertainty is a red flag that the signal is a binary, not a planet.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TransitCandidate:
    period: Quantity
    duration: Quantity
    transit_time: Quantity
    depth: float
    depth_err: float
    snr: float
    odd_even_delta: float
    transit_count: int


def _value_err(entry: object, name: str) -> tuple[float, float]:
    """Unpack a compute_stats (value, uncertainty) pair defensively."""
    if isinstance(entry, (tuple, list)) and len(entry) == 2:
        return float(entry[0]), float(entry[1])
    raise TypeError(f"Expected a (value, uncertainty) pair for '{name}', got {entry!r}.")


def summarise_candidate(
    model: BoxLeastSquares,
    results: BoxLeastSquaresResults,
) -> TransitCandidate:
    """Pick the strongest peak and compute its vetting statistics."""
    power = np.asarray(results.power, dtype=np.float64)
    if power.size == 0 or not np.isfinite(power).any():
        raise RuntimeError(
            "BLS returned no finite power. Widen the period range, add trial "
            "durations, or re-check the input light curve."
        )

    best = int(np.nanargmax(power))
    period = results.period[best]
    duration = results.duration[best]
    transit_time = results.transit_time[best]

    stats = model.compute_stats(period, duration, transit_time)
    depth_value, depth_err = _value_err(stats["depth"], "depth")
    odd_depth, _ = _value_err(stats["depth_odd"], "depth_odd")
    even_depth, _ = _value_err(stats["depth_even"], "depth_even")

    return TransitCandidate(
        period=period,
        duration=duration,
        transit_time=transit_time,
        depth=depth_value,
        depth_err=depth_err,
        snr=float(np.asarray(results.depth_snr, dtype=np.float64)[best]),
        odd_even_delta=abs(odd_depth - even_depth),
        transit_count=int(stats["transit_count"]),
    )
```

### Step 4 — End-to-end detection

```python
def detect_transit(
    time: NDArray[np.float64] | Quantity,
    flux: NDArray[np.float64] | Quantity,
    flux_err: NDArray[np.float64] | Quantity | None = None,
) -> TransitCandidate:
    """End-to-end: validate, search, and summarize the best transit candidate."""
    model, results = build_bls_and_search(time, flux, flux_err)
    candidate = summarise_candidate(model, results)

    print(f"Best period:        {candidate.period.to_value(u.day):.5f} day")
    print(f"Transit duration:   {candidate.duration.to_value(u.day):.5f} day")
    print(f"Reference epoch t0: {candidate.transit_time.to_value(u.day):.5f} day")
    print(f"Depth:              {candidate.depth:.6f} +/- {candidate.depth_err:.6f}")
    print(f"Depth SNR:          {candidate.snr:.2f}")
    print(f"Odd/even mismatch:  {candidate.odd_even_delta:.6f}")
    print(f"Number of transits: {candidate.transit_count}")
    return candidate
```

### Step 5 — Phase-fold and plot (visual confirmation)

The folding code below centers the transit at phase 0 and overlays the best-fit box on the data, which is the quickest visual confirmation that the peak is a genuine transit shape.

```python
import matplotlib.pyplot as plt


def fold_and_plot(
    time: NDArray[np.float64] | Quantity,
    flux: NDArray[np.float64] | Quantity,
    model: BoxLeastSquares,
    candidate: TransitCandidate,
    flux_err: NDArray[np.float64] | Quantity | None = None,
) -> NDArray[np.float64]:
    """Phase-fold the light curve at the candidate period and overlay the box model.

    Returns the (transit-centered) phase array, in case you want it for further checks.
    """
    t_days, f_clean, _ = validate_light_curve(time, flux, flux_err)

    period = float(candidate.period.to_value(u.day))
    t0 = float(candidate.transit_time.to_value(u.day))
    if period <= 0.0:
        raise ValueError("Candidate period must be positive to fold.")

    # Map each time to phase in [-0.5, 0.5) with the transit centered at 0.
    phase = (((t_days - t0) / period + 0.5) % 1.0) - 0.5

    # Evaluate the best-fit box at the observed times for a direct overlay.
    model_flux = np.asarray(
        model.model(
            t_days * u.day,
            candidate.period,
            candidate.duration,
            candidate.transit_time,
        ),
        dtype=np.float64,
    )

    order = np.argsort(phase)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(phase[order], f_clean[order], ".", color="0.5", markersize=3, label="data")
    ax.plot(phase[order], model_flux[order], "-", color="C3", linewidth=2, label="BLS box model")
    ax.set_xlabel("Phase (transit centered at 0)")
    ax.set_ylabel("Normalized flux")
    ax.set_title(f"Folded at P = {period:.5f} d")
    ax.legend(loc="lower right")
    fig.tight_layout()
    plt.show()
    return phase
```

## Examples

### Self-test: inject a known transit and recover it

For a fully self-contained sanity check, inject a known transit into synthetic data and confirm the pipeline recovers the planted period. If this round-trips, your installation and the parameter choices are sound.

```python
def self_test(seed: int = 42) -> None:
    """Plant a known transit in synthetic data and confirm BLS recovers it."""
    rng = np.random.default_rng(seed)

    true_period = 3.4         # days
    true_duration = 0.12      # days
    true_t0 = 1.0             # days
    true_depth = 0.01         # 1% dip

    t = np.sort(rng.uniform(0.0, 30.0, size=4000))
    flux = np.ones_like(t)

    phase = (((t - true_t0) / true_period + 0.5) % 1.0) - 0.5
    in_transit = np.abs(phase) < (0.5 * true_duration / true_period)
    flux[in_transit] -= true_depth

    flux_err = np.full_like(t, 0.001)
    flux += rng.normal(0.0, flux_err)

    candidate = detect_transit(t, flux, flux_err)

    recovered = candidate.period.to_value(u.day)
    rel_error = abs(recovered - true_period) / true_period
    assert rel_error < 0.01, (
        f"Recovered period {recovered:.5f} d differs from the planted "
        f"{true_period:.5f} d by {rel_error:.2%}."
    )
    print(f"Self-test passed: recovered P = {recovered:.5f} d (truth {true_period:.5f} d).")


if __name__ == "__main__":
    self_test()
```

Run on Windows PowerShell:

```powershell
python bls_pipeline.py
```

Expected output:

```
Best period:        3.40000 day
Transit duration:   0.12000 day
Reference epoch t0: 1.00000 day
Depth:              0.010000 +/- 0.000XXX
Depth SNR:          XX.XX
Odd/even mismatch:  0.000XXX
Number of transits: 8
Self-test passed: recovered P = 3.40000 d (truth 3.40000 d).
```

## Pitfalls

Two practical pitfalls quietly corrupt results rather than raising an error:

1. **Unvalidated input.** BLS minimizes a weighted chi-square. A single `NaN`, or a flux uncertainty of zero, can poison that sum and yield a confident-looking peak that is pure artifact. Clean and validate the light curve before you trust any periodogram. The `validate_light_curve` function in Step 1 does this explicitly — never skip it.

2. **Stale dependencies.** `BoxLeastSquares` has lived in `astropy.timeseries` since Astropy 3.1 (it was previously `astropy.stats.BoxLeastSquares`). Its core is compiled, so keeping Astropy and its NumPy/SciPy stack reasonably current buys you real speedups and the usual upstream security and correctness fixes.

3. **`compute_stats` returns tuples, not scalars.** The depth-related entries in the `compute_stats` dictionary are `(value, uncertainty)` pairs. Accessing them as if they were scalars will silently produce wrong numbers. Always unpack with a helper like `_value_err`.

4. **`depth_snr` is on the results object, not in stats.** The depth signal-to-noise lives at `results.depth_snr`, not inside the dictionary returned by `compute_stats`. Do not look for it there.

5. **Duration grid too narrow.** If none of your trial durations is close to the true transit duration, the box cannot line up with the real dip and the peak weakens or vanishes. Always span a physically plausible range.

6. **`maximum_period` exceeding the baseline.** BLS cannot confirm a period longer than the data span. The wrapper warns, but you should avoid it in the first place.

7. **Forcing a box onto sinusoidal variability.** If the light curve is dominated by smooth stellar rotation or pulsations, BLS will produce a forest of spurious harmonic peaks. Use Lomb-Scargle instead.

## Verification

Use this checklist to decide whether a peak is a real, plausible transit rather than an artifact. Each item targets a specific failure mode:

- [ ] **Peak is significant.** Confirm `candidate.snr` clears your detection threshold (commonly ~7 or higher for survey data). A low-SNR peak is usually noise.
- [ ] **Period grid was adequate.** Check that the recovered period is comfortably inside your `[minimum_period, maximum_period]` range and not pinned to an edge, which would hint the true period lies outside the searched window.
- [ ] **Duration is physical.** The fitted duration should be a small fraction of the period; a "transit" lasting a large fraction of the orbit is suspect.
- [ ] **Odd/even depths agree.** A `candidate.odd_even_delta` that is large compared with `candidate.depth_err` points to an eclipsing binary, not a planet.
- [ ] **The fold looks like a transit.** Phase-folding at the recovered period should show a single, coherent, flat-bottomed dip — not scattered noise or a sinusoid.
- [ ] **Cross-check when it matters.** For borderline detections, re-run with TLS; agreement between independent methods raises confidence.

Run the self-test to verify your installation:

```powershell
python -c "
import numpy as np, astropy.units as u
from astropy.timeseries import BoxLeastSquares
rng = np.random.default_rng(42)
t = np.sort(rng.uniform(0, 30, 4000))
flux = np.ones_like(t)
phase = (((t - 1.0) / 3.4 + 0.5) % 1.0) - 0.5
flux[np.abs(phase) < 0.5*0.12/3.4] -= 0.01
flux += rng.normal(0, 0.001, t.size)
model = BoxLeastSquares(t * u.day, flux, dy=np.full_like(t, 0.001))
r = model.autopower(np.array([0.05,0.08,0.12,0.16,0.20])*u.day, objective='likelihood')
best = np.argmax(r.power)
print(f'Recovered period: {r.period[best].value:.5f} d (expected ~3.4 d)')
assert abs(r.period[best].value - 3.4) / 3.4 < 0.01
print('Verification passed.')
"
```

## Related skills

- **Transit Least Squares (TLS):** the higher-sensitivity sibling for shallow, grazing, or low-SNR transits, since it correlates against a limb-darkened template rather than a box.
- **Lomb-Scargle periodogram:** the right tool for smooth, quasi-sinusoidal variability (stellar rotation, pulsations), where a sinusoidal basis avoids the spurious harmonics a box would generate. Also available in `astropy.timeseries`.
- **Light-curve preprocessing (e.g. Lightkurve, pandas):** detrending, normalization, and outlier removal before the search. Good detrending matters because BLS measures dips relative to the local baseline, so uncorrected instrumental trends inflate the noise and can hide a real transit.
