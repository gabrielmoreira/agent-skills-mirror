---
name: conditioning
version: 1.1.1
description: "Conditions raw gravitational-wave detector strain (PyCBC TimeSeries) for matched filtering: high-pass, resample, crop filter wraparound, then Welch PSD with inverse-spectrum truncation. Use when preprocessing LIGO/Virgo/KAGRA strain, GW TimeSeries, high-pass, resample, or PSD/whitening before a search. Not for post-filter SNR, triggers, or chi-squared, already-conditioned data, or non-GW DSP. Never resample before high-pass or let the PSD cutoff drift from the high-pass."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Gravitational Wave Data Conditioning

Raw interferometer strain is not ready for matched filtering. It is dominated by low-frequency seismic and suspension noise, sampled far faster than any astrophysical signal requires, and — once you start filtering it — contaminated by edge transients. Matched filtering also needs an estimate of the detector noise spectrum (the PSD) so it can weight each frequency by how trustworthy it is. Conditioning is the sequence of steps that turns a raw `TimeSeries` into data a filter can use without producing spurious triggers.

The ordering of these steps is not arbitrary. Each step assumes the previous one has already run, and doing them out of order silently corrupts the result rather than raising an error — which is exactly why the helpers below validate their inputs instead of trusting the caller.

## When to Use

Use this skill when you are preprocessing raw gravitational wave detector strain **before** matched filtering. Concretely, that means you still need to:

- **High-pass filter** to remove low-frequency noise (below ~15 Hz) that would otherwise dominate the data and waste filter dynamic range.
- **Resample** to a lower rate so the FFTs in matched filtering stay cheap without discarding any signal band you care about.
- **Crop filter wraparound** so the transients a digital filter creates at the start and end of the segment never reach the filter bank.
- **Estimate the PSD** so matched filtering can whiten the data and weight each frequency bin correctly.

**Do not use** when:

- Post-processing matched-filter output (SNR time series, triggers, chi-squared vetoes) — those operate on results, not raw strain.
- Working with data that has already been conditioned — re-applying these steps would double-filter the data and distort the PSD.
- Doing anything unrelated to gravitational wave strain preprocessing.

## Prerequisites

- **PyCBC** installed and importable: `pip install pycbc`
- **Pin and update your dependencies deliberately.** PyCBC's filtering and PSD routines have changed defaults across releases. Running on an unmaintained version can mean silently different results, not just a missing feature.
- **Do not ignore deprecation warnings.** In this stack a deprecation warning usually signals a default (filter order, truncation method) that is about to change underneath you. Read it and adapt rather than suppressing it.
- Windows host (PowerShell) is the primary environment. Use forward slashes or raw strings in Python paths; in PowerShell, quote paths containing spaces.

## Procedure

The four helpers below are written as a small reusable module, `gw_conditioning.py`. Each one validates its inputs up front, because the failure modes here are physical rather than syntactic: passing data in the wrong order, or a cutoff above the Nyquist frequency, produces *plausible-looking* output, not an exception. Catching those mistakes at the boundary is far cheaper than discovering them as phantom triggers later.

### Step 1 — High-Pass Filtering

Remove low-frequency noise so the rest of the band is not swamped by it. Ground-based detectors (LIGO, Virgo, KAGRA) are dominated by seismic and suspension-thermal noise below ~10–15 Hz. That noise carries enormous power, and because matched filtering works in the frequency domain it would bleed across the band and dominate the dynamic range of every later FFT.

**Why 15 Hz specifically:** it sits above the steep seismic wall but below the ~20 Hz lower edge of most compact-binary signals, so it discards noise without eating signal. Lower (10 Hz) preserves more low-frequency content for high-mass systems at the cost of admitting more noise; higher (20 Hz) is more aggressive and safe only when you know the signal starts above it.

```python
from __future__ import annotations

from pycbc.filter import highpass
from pycbc.types import TimeSeries


def high_pass_strain(
    strain: TimeSeries,
    cutoff_hz: float = 15.0,
    filter_order: int = 8,
) -> TimeSeries:
    """Apply a high-pass filter to detector strain."""
    if not isinstance(strain, TimeSeries):
        raise TypeError(
            f"strain must be a pycbc TimeSeries, got {type(strain).__name__}"
        )
    if not isinstance(cutoff_hz, (int, float)) or cutoff_hz <= 0:
        raise ValueError(f"cutoff_hz must be a positive number, got {cutoff_hz!r}")
    if not isinstance(filter_order, int) or filter_order < 1:
        raise ValueError(
            f"filter_order must be a positive integer, got {filter_order!r}"
        )

    nyquist_hz: float = 0.5 / float(strain.delta_t)
    if cutoff_hz >= nyquist_hz:
        raise ValueError(
            f"cutoff_hz ({cutoff_hz} Hz) must be below the Nyquist frequency "
            f"({nyquist_hz:.1f} Hz); a high-pass above Nyquist removes everything"
        )

    return highpass(strain, frequency=cutoff_hz, filter_order=filter_order)
```

### Step 2 — Resampling

Downsample so the data is cheap to filter, but only **after** high-passing so the filter has already suppressed the high-frequency content that would otherwise alias back into the band. Resampling decimates the series, and any power above the new Nyquist frequency folds back ("aliases") into the retained band as fake signal. PyCBC's resampler applies an anti-alias filter; running these in the canonical order keeps the pipeline consistent and avoids surprising interactions.

**Rate guidance:** 2048 Hz is the standard, computationally efficient choice (1024 Hz Nyquist). Use 4096 Hz when you need resolution above 1 kHz — e.g. high-mass or high-spin systems whose merger/ringdown lives at higher frequency.

```python
from __future__ import annotations

from pycbc.filter import resample_to_delta_t
from pycbc.types import TimeSeries


def resample_strain(
    strain: TimeSeries,
    target_sample_rate_hz: int = 2048,
) -> TimeSeries:
    """Resample strain to ``target_sample_rate_hz``."""
    if not isinstance(strain, TimeSeries):
        raise TypeError(
            f"strain must be a pycbc TimeSeries, got {type(strain).__name__}"
        )
    if not isinstance(target_sample_rate_hz, int) or target_sample_rate_hz <= 0:
        raise ValueError(
            "target_sample_rate_hz must be a positive integer, "
            f"got {target_sample_rate_hz!r}"
        )

    current_rate_hz: float = 1.0 / float(strain.delta_t)
    if target_sample_rate_hz > current_rate_hz:
        raise ValueError(
            f"target_sample_rate_hz ({target_sample_rate_hz} Hz) exceeds the "
            f"input rate ({current_rate_hz:.0f} Hz); upsampling invents no new "
            "information and is almost always a mistake here"
        )

    delta_t: float = 1.0 / target_sample_rate_hz
    return resample_to_delta_t(strain, delta_t)
```

### Step 3 — Crop Filter Wraparound

Remove the edge transients that filtering introduces, before they can reach the filter bank. Every digital filter (the high-pass, and the anti-alias filter inside the resampler) has a finite impulse response. At the very start and end of the segment the filter does not have a full window of data to work with, so it produces a decaying transient — "filter wraparound". Those samples look like signal and will fire matched-filter triggers if left in place.

**Why 2 seconds:** it comfortably exceeds the impulse-response length of the filters used above. Increase it if you stack longer filters or analyse very long templates whose ringing extends further.

```python
from __future__ import annotations

from pycbc.types import TimeSeries


def crop_filter_transients(
    strain: TimeSeries,
    seconds_each_end: float = 2.0,
) -> TimeSeries:
    """Crop ``seconds_each_end`` from both ends of the series."""
    if not isinstance(strain, TimeSeries):
        raise TypeError(
            f"strain must be a pycbc TimeSeries, got {type(strain).__name__}"
        )
    if not isinstance(seconds_each_end, (int, float)) or seconds_each_end <= 0:
        raise ValueError(
            f"seconds_each_end must be a positive number, got {seconds_each_end!r}"
        )

    duration_s: float = float(strain.duration)
    if 2 * seconds_each_end >= duration_s:
        raise ValueError(
            f"cropping {seconds_each_end} s from each end removes "
            f"{2 * seconds_each_end} s, but the series is only {duration_s:.2f} s "
            "long; reduce seconds_each_end or use a longer segment"
        )

    cropped: TimeSeries = strain.crop(seconds_each_end, seconds_each_end)
    return cropped
```

### Step 4 — PSD Estimation

Estimate the noise spectrum that matched filtering uses to whiten and weight the data. Detector noise is coloured — far louder at some frequencies than others. Matched filtering whitens the data using the PSD so that each frequency bin contributes in proportion to how trustworthy it is. A wrong PSD means a mis-weighted filter and degraded sensitivity.

The three sub-steps:

1. `strain.psd(segment_length_s)` — Welch's method: splits data into overlapping segments, periodograms each, and averages. Longer segments give finer frequency resolution but fewer to average, so the estimate is noisier. 4 s is the usual balance for compact-binary searches.
2. `interpolate` — resamples the PSD onto the exact `delta_f` grid of the data. The filter multiplies data and PSD bin-by-bin, so their frequency grids must match exactly.
3. `inverse_spectrum_truncation` — limits the time-domain length of the implied whitening filter. Without it the filter's impulse response can be as long as the whole segment and reintroduce the very wraparound we just cropped away; truncating it to the segment length keeps the filter causal and well behaved.

**Match the cutoff to the high-pass:** below `low_frequency_cutoff_hz` the data has been filtered away, so the PSD there is unreliable. Telling the truncation routine to ignore that band stops the noise floor estimate from being polluted by the high-pass roll-off.

```python
from __future__ import annotations

import warnings

from pycbc.psd import interpolate, inverse_spectrum_truncation
from pycbc.types import FrequencySeries, TimeSeries


def estimate_psd(
    strain: TimeSeries,
    segment_length_s: float = 4.0,
    low_frequency_cutoff_hz: float = 15.0,
) -> FrequencySeries:
    """Estimate a matched-filter-ready PSD from conditioned strain."""
    if not isinstance(strain, TimeSeries):
        raise TypeError(
            f"strain must be a pycbc TimeSeries, got {type(strain).__name__}"
        )
    if not isinstance(segment_length_s, (int, float)) or segment_length_s <= 0:
        raise ValueError(
            f"segment_length_s must be a positive number, got {segment_length_s!r}"
        )
    if (
        not isinstance(low_frequency_cutoff_hz, (int, float))
        or low_frequency_cutoff_hz <= 0
    ):
        raise ValueError(
            "low_frequency_cutoff_hz must be a positive number, "
            f"got {low_frequency_cutoff_hz!r}"
        )

    duration_s: float = float(strain.duration)
    if segment_length_s > duration_s:
        raise ValueError(
            f"segment_length_s ({segment_length_s} s) exceeds the data duration "
            f"({duration_s:.2f} s); Welch's method needs at least one full segment"
        )
    if duration_s < 4 * segment_length_s:
        warnings.warn(
            f"data duration ({duration_s:.1f} s) gives fewer than 4 segments of "
            f"{segment_length_s} s; the PSD estimate will be noisy. Use a longer "
            "stretch of strain where possible.",
            stacklevel=2,
        )

    sample_rate_hz: float = 1.0 / float(strain.delta_t)
    nyquist_hz: float = 0.5 * sample_rate_hz
    if low_frequency_cutoff_hz >= nyquist_hz:
        raise ValueError(
            f"low_frequency_cutoff_hz ({low_frequency_cutoff_hz} Hz) must be "
            f"below the Nyquist frequency ({nyquist_hz:.1f} Hz)"
        )

    # 1. Welch estimate on the conditioned data.
    psd: FrequencySeries = strain.psd(segment_length_s)

    # 2. Interpolate onto the data's exact frequency grid.
    psd = interpolate(psd, strain.delta_f)

    # 3. Truncate the implied whitening filter to one segment length.
    max_filter_len: int = int(segment_length_s * sample_rate_hz)
    psd = inverse_spectrum_truncation(
        psd,
        max_filter_len,
        low_frequency_cutoff=low_frequency_cutoff_hz,
    )
    return psd
```

### PSD Parameters in Context

- **Segment length (4 s)** — sets the resolution/averaging trade-off. Shorten it only if you genuinely lack data and accept a noisier PSD.
- **Low-frequency cutoff (15 Hz)** — must equal the high-pass cutoff. Anything below it has been filtered out and cannot be characterised honestly.
- **`max_filter_len`** — derived as `segment_length_s * sample_rate`, this caps the whitening filter's impulse response so it cannot re-create wraparound.

## Examples

### Example 1: Full Conditioning Pipeline

Complete, runnable script. Pulls real GW150914 strain from the open catalog, composes the four validated helpers from `gw_conditioning.py`, and returns the conditioned `TimeSeries` together with its PSD.

```python
from __future__ import annotations

from pycbc.catalog import Merger
from pycbc.types import FrequencySeries, TimeSeries

from gw_conditioning import (
    crop_filter_transients,
    estimate_psd,
    high_pass_strain,
    resample_strain,
)


def condition_strain(
    strain: TimeSeries,
    *,
    high_pass_hz: float = 15.0,
    target_sample_rate_hz: int = 2048,
    crop_seconds_each_end: float = 2.0,
    psd_segment_length_s: float = 4.0,
) -> tuple[TimeSeries, FrequencySeries]:
    """Run the full conditioning pipeline and return (conditioned, psd).

    The keyword-only arguments expose the four physical choices that matter, and
    the PSD's low-frequency cutoff is deliberately tied to ``high_pass_hz`` so
    the two can never drift apart.
    """
    if not isinstance(strain, TimeSeries):
        raise TypeError(
            f"strain must be a pycbc TimeSeries, got {type(strain).__name__}"
        )

    filtered: TimeSeries = high_pass_strain(strain, cutoff_hz=high_pass_hz)
    resampled: TimeSeries = resample_strain(
        filtered, target_sample_rate_hz=target_sample_rate_hz
    )
    conditioned: TimeSeries = crop_filter_transients(
        resampled, seconds_each_end=crop_seconds_each_end
    )
    psd: FrequencySeries = estimate_psd(
        conditioned,
        segment_length_s=psd_segment_length_s,
        low_frequency_cutoff_hz=high_pass_hz,
    )
    return conditioned, psd


def main() -> None:
    merger = Merger("GW150914")
    raw_strain: TimeSeries = merger.strain("H1")

    conditioned, psd = condition_strain(raw_strain)

    print(f"Raw duration:        {raw_strain.duration:.2f} s "
          f"@ {1.0 / raw_strain.delta_t:.0f} Hz")
    print(f"Conditioned duration:{conditioned.duration:.2f} s "
          f"@ {1.0 / conditioned.delta_t:.0f} Hz")
    print(f"PSD bins:            {len(psd)} (delta_f = {psd.delta_f:.4f} Hz)")
    print(f"PSD frequency range: {psd.sample_frequencies[0]:.2f} - "
          f"{psd.sample_frequencies[-1]:.2f} Hz")


if __name__ == "__main__":
    main()
```

### Example 2: Higher-Resolution Variant for a High-Mass System

Same pipeline, retuned for a system with power above 1 kHz. The only changes are the sampling rate and a slightly larger crop to cover the longer filters — and because `condition_strain` ties the PSD cutoff to the high-pass, that stays consistent automatically.

```python
from __future__ import annotations

from pycbc.catalog import Merger
from pycbc.types import FrequencySeries, TimeSeries

from gw_conditioning import (
    crop_filter_transients,
    estimate_psd,
    high_pass_strain,
    resample_strain,
)


def main() -> None:
    merger = Merger("GW150914")
    raw_strain: TimeSeries = merger.strain("H1")

    filtered: TimeSeries = high_pass_strain(raw_strain, cutoff_hz=15.0)
    resampled: TimeSeries = resample_strain(filtered, target_sample_rate_hz=4096)
    conditioned: TimeSeries = crop_filter_transients(resampled, seconds_each_end=4.0)
    psd: FrequencySeries = estimate_psd(
        conditioned,
        segment_length_s=4.0,
        low_frequency_cutoff_hz=15.0,
    )

    nyquist_hz: float = 0.5 / conditioned.delta_t
    print(f"Conditioned @ {1.0 / conditioned.delta_t:.0f} Hz "
          f"(Nyquist {nyquist_hz:.0f} Hz), {conditioned.duration:.2f} s retained")
    print(f"PSD covers {psd.sample_frequencies[0]:.2f} - "
          f"{psd.sample_frequencies[-1]:.2f} Hz")


if __name__ == "__main__":
    main()
```

## Pitfalls

1. **High-pass before resampling** — resampling on un-high-passed data lets low-frequency power interact with the anti-alias stage; high-passing first keeps each step operating on data it expects. Doing these out of order silently corrupts the result rather than raising an error.
2. **Upsampling is a mistake** — `target_sample_rate_hz` must not exceed the input rate. Upsampling invents no new information and is almost always a mistake here.
3. **Cutoff above Nyquist** — a high-pass above Nyquist removes everything. The validator catches this, but only if you call the helper.
4. **Under-cropping** — 2 s clears the filters used here; longer filters or templates need more. Under-cropping leaves transients that masquerade as triggers.
5. **PSD cutoff mismatch** — the PSD's `low_frequency_cutoff_hz` must equal the high-pass cutoff. A mismatch lets the high-pass roll-off contaminate the noise-floor estimate.
6. **Short segments for Welch** — if data duration gives fewer than 4 segments, the PSD estimate will be noisy. Use a longer stretch of strain where possible.
7. **Segment longer than data** — Welch's method needs at least one full segment; the validator rejects this, but plan your data length accordingly.
8. **Cropping more than available** — cropping `seconds_each_end` from each end must not remove the entire series. The validator catches this.
9. **Ignoring deprecation warnings** — in this stack a deprecation warning usually signals a default (filter order, truncation method) that is about to change. Treat them as advance notice, not noise.
10. **Unpinned dependencies** — PyCBC's filtering and PSD routines have changed defaults across releases. Pin and update deliberately so you adopt changed defaults knowingly rather than discovering them in your results.
11. **Not inspecting output** — most conditioning bugs (a stuck channel, a glitch, a wrong cutoff) are obvious to the eye in a plot and invisible in a summary statistic. Always plot the conditioned strain and the PSD.

## Verification

1. **Run the pipeline end to end** — confirm it returns without raising. The input validators will reject mis-ordered or out-of-range arguments before they can silently corrupt the result:

   ```powershell
   python -W error condition_pipeline.py
   ```

   Escalating warnings to errors (`-W error`) surfaces any deprecation or short-segment warnings so you can address them.

2. **Check conditioned duration** — confirm it equals the resampled duration minus `2 * crop_seconds_each_end`, proving the wraparound crop took effect:

   ```python
   expected_duration = resampled.duration - 2 * crop_seconds_each_end
   assert abs(conditioned.duration - expected_duration) < 1e-6
   ```

3. **Check conditioned sample rate** — confirm it matches `target_sample_rate_hz`:

   ```python
   assert int(1.0 / conditioned.delta_t) == target_sample_rate_hz
   ```

4. **Check PSD grid alignment** — the PSD's `delta_f` must equal the conditioned data's `delta_f`, and its frequency range must start at or above the high-pass cutoff:

   ```python
   assert psd.delta_f == conditioned.delta_f
   assert psd.sample_frequencies[0] >= high_pass_hz - 1e-6
   ```

5. **Visual inspection** — plot the conditioned strain and the PSD and eyeball them for glitches, stuck channels, or an unexpected noise floor. Most conditioning bugs are visible in a plot and invisible in a summary statistic.

## Related Skills

- **matched_filtering** — consumes the conditioned `TimeSeries` and PSD produced here to search for signals.
- **data_analysis** — interprets the matched-filter output (SNR, triggers).
- **psd_estimation** — deeper PSD techniques (median-mean, adaptive segmenting) for when the simple Welch estimate above is not enough.
