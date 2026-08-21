---
name: radar-vital-signs
version: 1.1.1
description: "Recovers heart and breathing rates in bpm from short-range CW (24 GHz) or FMCW mmWave (60/77 GHz, TI IWR/AWR) I/Q using Range FFT, clutter subtract, phase unwrap, bandpass, and PSD peak picking with harmonic rejection. Trigger on radar vital-sign captures or interleaved I/Q binary. Never a UWB pulse, MIMO angle-of-arrival, gesture-Doppler, arrhythmia beat-to-beat, multi-chest, or exercise-ramp spectrogram pipeline."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Radar Vital-Sign Extraction

End-to-end pipeline: raw radar I/Q → cleaned phase signal → HR and BR in bpm.

The whole skill rests on one physical fact: a beating heart and a breathing chest move the skin surface by sub-millimetre to centimetre distances, and that motion shows up as a *phase* change in the reflected radar wave. Everything below is about recovering that tiny phase signal cleanly and then reading two rates out of it without being fooled by harmonics. Each instruction carries the reason it exists, because the edge cases (slow breathers, bradycardia, post-exercise tachycardia, harmonic imposters) are exactly where blindly-followed textbook recipes fail.

## When to Use

Use this skill when you need to extract heart rate (HR) and breathing rate (BR) from raw short-range radar I/Q captures — both continuous-wave (CW, 24 GHz clinical boards) and FMCW mmWave (60/77 GHz, TI IWR/AWR). Specifically when you need to:

- Parse interleaved I/Q binary
- Do a Range FFT on FMCW chirps
- Remove static clutter
- Pick a subject range bin
- Extract phase with unwrapping
- Design HR/BR bandpass filters
- Pick a peak frequency via PSD
- Reject the HR second harmonic that often dominates the fundamental
- Handle respiration-harmonic leakage on slow breathers

### Do NOT use for

These are out of scope because each one needs a *different* signal model, not a tweak to this one:

- **Pulse / UWB range-gated radar** — energy arrives as discrete time-of-flight echoes; range-gate in fast time rather than doing the Range-FFT + phase pipeline here.
- **MIMO angle-of-arrival** — the subject's direction is unknown; beamform across the virtual array *before* any per-bin phase makes sense.
- **Doppler-only gesture radar** — gestures are characterised by their velocity signature, read from a slow-time (Doppler) FFT, not from the quasi-static chest phase.
- **Arrhythmia / irregular rhythms** — a PSD assumes a near-stationary rate; irregular beats need beat-to-beat R-peak / foot detection and RR-interval analysis instead.
- **Multiple subjects in one signal** — two overlapping chests produce two phase signals you cannot separate by filtering; run source separation (or spatial gating) first.
- **Rapidly non-stationary rate (exercise ramp)** — a single-window PSD smears a changing rate into a wide blur; track it with a spectrogram / short-time analysis.

## Prerequisites

### Python and library versions

- **Python ≥ 3.9** — examples use built-in generic types (`list[int]`, `tuple[float, float]`, `dict[str, float]`). `from __future__ import annotations` keeps hints lazy so they cost nothing at runtime.
- **NumPy ≥ 1.21** — `numpy.typing.NDArray` enables precise array typing (`NDArray[np.complex128]`) instead of falling back to untyped `Any`.
- **SciPy ≥ 1.4** — `butter`, `welch`, and `iirnotch` all accept the `fs=` keyword, making band edges readable in Hz rather than normalised-to-Nyquist fractions. `zero_phase=True` on `decimate` also needs a reasonably recent SciPy.

Keeping dependencies current is not box-ticking: an outdated SciPy silently changes filter-design defaults and an outdated NumPy forces you back onto untyped arrays, which is precisely the class of bug this skill is built to prevent.

### Install (Windows PowerShell, primary host)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "numpy>=1.21" "scipy>=1.4"
```

### Reference files

Load these from the skill's `references/` directory when the corresponding step is reached:

| Reference | When to load |
|---|---|
| `references/iq-formats.md` | Before Step 1 (parsing binary I/Q) — details all supported formats and sidecar requirements |
| `references/range-bin.md` | Before Step 4 (FMCW range-bin selection) — physical prior windows, coherent neighbour summing |
| `references/harmonic-pitfalls.md` | Before Step 8 (HR harmonic rejection) — why the 2nd harmonic dominates and how to reject it |
| `references/band-rationale.md` | Before Step 7 (bandpass design) — justification for BR_BAND_HZ and HR_BAND_HZ edges |
| `references/debugging.md` | When output looks like garbage — ordered checklist for ingestion and SNR bugs |

## Procedure

Treat every code block in this skill as part of a single module, `radar_vitals.py`. The preamble below defines the type aliases and validation helpers that every later function reuses. Centralising validation here is deliberate: each public function fails *fast and loudly* at its boundary, which is far easier to debug than a `NaN` that silently propagates three stages down the pipeline.

### Shared module preamble

```python
from __future__ import annotations

import numbers
import os
from typing import Final, Union

import numpy as np
from numpy.typing import NDArray
from scipy.signal import butter, cheby2, decimate, filtfilt, iirnotch, welch

# Precise array element types — never a bare ``Any``.
ComplexArray = NDArray[np.complex128]
FloatArray = NDArray[np.float64]
# Some stages (range FFT) legitimately accept real *or* complex chirps.
# ``Union`` (not the ``|`` operator) keeps this module-level alias importable on
# Python 3.9, where ``|`` between typing objects is not yet supported at runtime.
SignalArray = Union[NDArray[np.floating], NDArray[np.complexfloating]]

# Default vital bands, justified in references/band-rationale.md.
BR_BAND_HZ: Final[tuple[float, float]] = (0.08, 0.5)
HR_BAND_HZ: Final[tuple[float, float]] = (0.7, 3.0)


def _ensure_finite_positive(value: float, name: str) -> float:
    """Coerce ``value`` to a finite, strictly positive float or raise.

    ``bool`` is rejected explicitly because ``True``/``False`` are ints in
    Python and would otherwise sneak through as 1.0 / 0.0.
    """
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a real number, got {type(value).__name__}")
    v = float(value)
    if not np.isfinite(v) or v <= 0.0:
        raise ValueError(f"{name} must be finite and > 0, got {value!r}")
    return v


def _ensure_1d_signal(signal: NDArray, name: str, *, min_len: int = 1) -> None:
    """Validate a 1-D numeric signal: right type, right rank, long enough."""
    if not isinstance(signal, np.ndarray):
        raise TypeError(f"{name} must be a numpy.ndarray, got {type(signal).__name__}")
    if signal.ndim != 1:
        raise ValueError(f"{name} must be 1-D, got shape {signal.shape}")
    if signal.size < min_len:
        raise ValueError(
            f"{name} needs at least {min_len} samples for stable processing, "
            f"got {signal.size}"
        )


def _ensure_2d_complex(matrix: NDArray, name: str) -> ComplexArray:
    """Validate and up-cast an FMCW range matrix to ``complex128``."""
    if not isinstance(matrix, np.ndarray):
        raise TypeError(f"{name} must be a numpy.ndarray, got {type(matrix).__name__}")
    if matrix.ndim != 2:
        raise ValueError(
            f"{name} must be 2-D [n_chirp, n_range_bin], got shape {matrix.shape}"
        )
    if matrix.shape[0] < 2 or matrix.shape[1] < 1:
        raise ValueError(f"{name} too small to process: shape {matrix.shape}")
    out = matrix.astype(np.complex128, copy=False)
    if not np.all(np.isfinite(out)):
        raise ValueError(f"{name} contains NaN/Inf; clean or reject the capture first.")
    return out


def _ensure_band(lo: float, hi: float, fs: float) -> tuple[float, float, float]:
    """Validate a passband against the sampling rate (Nyquist) and ordering."""
    lo = _ensure_finite_positive(lo, "lo")
    hi = _ensure_finite_positive(hi, "hi")
    fs = _ensure_finite_positive(fs, "fs")
    if lo >= hi:
        raise ValueError(f"band lower edge lo={lo} Hz must be < upper edge hi={hi} Hz")
    nyquist = fs / 2.0
    if hi >= nyquist:
        raise ValueError(
            f"band upper edge hi={hi} Hz must stay below Nyquist {nyquist} Hz "
            f"(fs={fs} Hz); decimate first or widen fs"
        )
    return lo, hi, fs


def _ensure_psd_pair(f: NDArray, p: NDArray) -> tuple[FloatArray, FloatArray]:
    """Validate a (frequency, power) PSD pair for interpolation/argmax use."""
    for arr, label in ((f, "f"), (p, "p")):
        if not isinstance(arr, np.ndarray) or arr.ndim != 1:
            raise TypeError(f"{label} must be a 1-D numpy array")
    if f.shape != p.shape:
        raise ValueError(f"f and p must share shape, got {f.shape} vs {p.shape}")
    if f.size < 2:
        raise ValueError("PSD must have at least 2 frequency bins")
    if np.any(np.diff(f) <= 0.0):
        raise ValueError("PSD frequency axis f must be strictly increasing")
    return f.astype(np.float64, copy=False), p.astype(np.float64, copy=False)


def _decimation_stages(q: int, max_stage: int = 13) -> list[int]:
    """Split a large integer decimation factor into IIR-stable stages.

    SciPy's IIR ``decimate`` becomes numerically fragile for a single factor
    above ~13, so a factor like 20 is cascaded as 4 then 5. A large prime is
    approximated with ``max_stage`` and the tiny resulting fs error is accepted.
    """
    if q < 1:
        raise ValueError(f"decimation factor must be >= 1, got {q}")
    stages: list[int] = []
    remaining = q
    while remaining > max_stage:
        divisor = next(
            (d for d in range(max_stage, 1, -1) if remaining % d == 0), None
        )
        if divisor is None:
            divisor = max_stage
            remaining = max(1, round(remaining / divisor))
        else:
            remaining //= divisor
        stages.append(divisor)
    if remaining > 1:
        stages.append(remaining)
    return stages or [1]
```

### Step 1 — Parse binary I/Q into a usable array

Captures are tightly-packed binary, and the *only* reliable source of truth for the layout is the sidecar (JSON/YAML) shipped with the file — guessing the dtype or interleave is the single most common ingestion bug. CW data becomes a complex 1-D array; FMCW real-only data becomes a 2-D `[n_chirp, samples_per_chirp]` matrix you Range-FFT next.

**Load `references/iq-formats.md` now** for the full format catalogue and sidecar field names.

```python
def parse_iq(path: str, fmt: str, *, scale: float = 1.0) -> ComplexArray:
    """Parse interleaved/complex I/Q binary into a 1-D ``complex128`` array.

    ``fmt`` must match the capture's sidecar exactly. ``scale`` rescales raw
    ADC counts (int16) back to a physical unit when the sidecar provides it.
    """
    allowed = {
        "complex64_le_interleaved",   # float32 I, float32 Q, repeating
        "int16_le_interleaved",       # int16 I, int16 Q, repeating (DCA1000, Xethru)
        "complex128_le",              # two float64 per sample (post-processed pickles)
    }
    if fmt not in allowed:
        raise ValueError(f"unknown fmt {fmt!r}; expected one of {sorted(allowed)}")
    if not isinstance(path, str) or not path:
        raise TypeError("path must be a non-empty string")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"I/Q file not found: {path!r}")
    scale = _ensure_finite_positive(scale, "scale")

    if fmt == "complex64_le_interleaved":
        raw = np.fromfile(path, dtype="<f4").astype(np.float64)
        if raw.size % 2 != 0:
            raise ValueError(
                f"interleaved float32 stream has odd sample count {raw.size}; "
                "truncated capture or wrong fmt?"
            )
        iq = raw[0::2] + 1j * raw[1::2]
    elif fmt == "int16_le_interleaved":
        raw = np.fromfile(path, dtype="<i2").astype(np.float64)
        if raw.size % 2 != 0:
            raise ValueError(
                f"interleaved int16 stream has odd sample count {raw.size}; "
                "truncated capture or wrong fmt?"
            )
        iq = (raw[0::2] + 1j * raw[1::2]) * scale
    else:  # complex128_le
        iq = np.fromfile(path, dtype="<c16")

    iq = np.asarray(iq, dtype=np.complex128)
    if iq.size == 0:
        raise ValueError(f"no samples read from {path!r}; empty file or wrong fmt?")
    if not np.all(np.isfinite(iq)):
        raise ValueError(f"parsed I/Q from {path!r} contains NaN/Inf.")
    return iq


def parse_real_chirps(path: str, n_chirps: int, samples_per_chirp: int) -> FloatArray:
    """Parse a real-only int16 FMCW dump into a ``[n_chirp, samples]`` matrix.

    The length must equal ``n_chirps * samples_per_chirp`` exactly — a mismatch
    means the chirp geometry from the sidecar is wrong, which would silently
    shear every chirp if reshaped anyway.
    """
    if n_chirps < 1 or samples_per_chirp < 1:
        raise ValueError(
            f"n_chirps and samples_per_chirp must be >= 1, "
            f"got {n_chirps} and {samples_per_chirp}"
        )
    if not os.path.isfile(path):
        raise FileNotFoundError(f"FMCW file not found: {path!r}")
    raw = np.fromfile(path, dtype="<i2").astype(np.float64)
    expected = n_chirps * samples_per_chirp
    if raw.size != expected:
        raise ValueError(
            f"expected {expected} samples ({n_chirps} x {samples_per_chirp}), "
            f"got {raw.size}; check chirp geometry in the sidecar"
        )
    return np.asarray(raw.reshape(n_chirps, samples_per_chirp), dtype=np.float64)
```

After parsing, validate `len(iq) == fs * duration` (CW) — being off by exactly 2× almost always means you forgot to de-interleave, and 0.5× means you de-interleaved data that was already complex.

### Step 2 — (FMCW only) Range FFT across fast-time samples

Each FMCW chirp's beat frequency encodes target distance, so an FFT across the ADC samples of one chirp turns it into a range profile. Stacking chirps gives the range matrix `R[n_chirp, n_range_bin]` that the rest of the FMCW path operates on. CW boards transmit a single tone, so they skip this entirely.

```python
def range_fft(chirps: SignalArray, *, axis: int = 1) -> ComplexArray:
    """Range FFT across fast-time (ADC) samples → complex range matrix.

    The per-chirp mean is removed first to suppress the transmit-leakage DC
    spike that would otherwise dominate bin 0. Real-only captures use ``rfft``
    (their range profile is the first half of the spectrum); complex captures
    use the full ``fft``.
    """
    if not isinstance(chirps, np.ndarray):
        raise TypeError(f"chirps must be a numpy.ndarray, got {type(chirps).__name__}")
    if chirps.ndim != 2:
        raise ValueError(f"chirps must be 2-D [n_chirp, samples], got {chirps.shape}")
    if axis not in (0, 1):
        raise ValueError(f"axis must be 0 or 1, got {axis}")
    if not np.all(np.isfinite(chirps)):
        raise ValueError("chirps contains NaN/Inf; reject or repair the capture.")

    centered = chirps - chirps.mean(axis=axis, keepdims=True)
    if np.iscomplexobj(centered):
        spectrum = np.fft.fft(centered, axis=axis)
    else:
        spectrum = np.fft.rfft(centered, axis=axis)
    return np.asarray(spectrum, dtype=np.complex128)
```

### Step 3 — Remove static clutter

The wall behind the subject, the radome, and DC offset are all *static* reflectors. They are enormous compared with chest motion and they sit at zero Doppler, so subtracting the temporal mean cancels them while leaving the moving chest untouched. Doing this *before* taking the phase angle matters: a large DC offset anchors the phasor away from the origin and wastes the limited ±π unwrap budget.

```python
def remove_clutter_cw(iq: ComplexArray) -> ComplexArray:
    """CW: subtract the temporal mean (DC + static reflectors)."""
    _ensure_1d_signal(iq, "iq")
    if not np.iscomplexobj(iq):
        raise TypeError(
            f"iq must be complex-valued; got real dtype {iq.dtype}. "
            "Parse interleaved I/Q into a complex array first."
        )
    iq = iq.astype(np.complex128, copy=False)
    if not np.all(np.isfinite(iq)):
        raise ValueError("iq contains NaN/Inf; clean or reject the capture first.")
    return np.asarray(iq - iq.mean(), dtype=np.complex128)


def remove_clutter_fmcw(range_matrix: ComplexArray) -> ComplexArray:
    """FMCW: subtract the per-range-bin temporal mean across the chirp axis."""
    matrix = _ensure_2d_complex(range_matrix, "range_matrix")
    static = matrix.mean(axis=0, keepdims=True)
    return np.asarray(matrix - static, dtype=np.complex128)
```

### Step 4 — (FMCW only) Pick the subject range bin

Only one or a few bins actually contain the subject; everything else is noise or static. Restrict the search to a *physical prior window* (e.g. 0.3–1.5 m for a seated subject) so a bright static reflector or the DC bin can't win. A real chest spans 2–3 adjacent bins and the peak jitters frame-to-frame, so summing neighbours **coherently** (complex sum, not magnitude) recovers SNR a single bin would lose.

**Load `references/range-bin.md` now** for physical prior windows by subject posture and coherent-neighbour rationale.

```python
def select_range_bin(
    range_matrix: ComplexArray,
    m_per_bin: float,
    *,
    near_m: float = 0.3,
    far_m: float = 1.5,
    coherent_neighbors: int = 1,
) -> tuple[ComplexArray, int]:
    """Pick the subject bin within a physical window and coherently sum neighbours.

    Returns the slow-time complex signal (one value per chirp) and the index of
    the chosen peak bin. ``coherent_neighbors=1`` sums the peak plus one bin on
    each side, matching the 3–10 cm depth of a real chest.
    """
    matrix = _ensure_2d_complex(range_matrix, "range_matrix")
    m_per_bin = _ensure_finite_positive(m_per_bin, "m_per_bin")
    near_m = _ensure_finite_positive(near_m, "near_m")
    far_m = _ensure_finite_positive(far_m, "far_m")
    if near_m >= far_m:
        raise ValueError(f"near_m={near_m} must be < far_m={far_m}")
    if not isinstance(coherent_neighbors, int) or coherent_neighbors < 0:
        raise ValueError(f"coherent_neighbors must be a non-negative int, got {coherent_neighbors!r}")

    n_bins = matrix.shape[1]
    lo_bin = max(0, int(np.floor(near_m / m_per_bin)))
    hi_bin = min(n_bins, int(np.ceil(far_m / m_per_bin)) + 1)
    if hi_bin <= lo_bin:
        raise ValueError(
            f"prior window [{near_m}, {far_m}] m maps to empty bin range "
            f"[{lo_bin}, {hi_bin}) for m_per_bin={m_per_bin}; check resolution"
        )

    window = slice(lo_bin, hi_bin)
    mean_mag = np.abs(matrix[:, window]).mean(axis=0)
    best = lo_bin + int(np.argmax(mean_mag))

    left = max(0, best - coherent_neighbors)
    right = min(n_bins, best + coherent_neighbors + 1)
    combined = matrix[:, left:right].sum(axis=1)
    return np.asarray(combined, dtype=np.complex128), best
```

### Step 5 — Extract phase with unwrap

The phase of the (clutter-removed) phasor *is* the displacement signal — at 24 GHz, 1 mm of chest motion is roughly 1 radian, so phase carries the vital signs at full sensitivity. `np.angle` wraps to (−π, π]; `np.unwrap` stitches the jumps back into a continuous displacement trace. Removing the mean centres it for the filters that follow.

```python
def extract_phase(signal: ComplexArray) -> FloatArray:
    """Unwrap the phase of a complex slow-time signal into a centred displacement."""
    _ensure_1d_signal(signal, "signal", min_len=2)
    if not np.iscomplexobj(signal):
        raise TypeError(
            f"signal must be complex; got real dtype {signal.dtype}. "
            "Use the complex bin/IQ output of clutter removal."
        )
    signal = signal.astype(np.complex128, copy=False)
    if not np.all(np.isfinite(signal)):
        raise ValueError("signal contains NaN/Inf before phase extraction.")
    if np.any(signal == 0):
        raise ValueError(
            "signal contains zero-valued samples; phase is undefined there. "
            "Pick a different range bin or check for clipping."
        )
    phase = np.unwrap(np.angle(signal))
    return np.asarray(phase - phase.mean(), dtype=np.float64)
```

### Step 6 — Decimate to a target sampling rate

Radar captures often arrive at hundreds of Hz to kHz, but vital signs live below 3 Hz. Decimating to ~50 Hz before filtering keeps the IIR filters numerically stable (band edges well below Nyquist) and speeds up the PSD. The `_decimation_stages` helper cascades factors ≤ 13 to avoid IIR instability.

```python
def decimate_to_target(
    signal: FloatArray, fs: float, target_fs: float = 50.0
) -> tuple[FloatArray, float]:
    """Decimate a 1-D signal from ``fs`` to approximately ``target_fs`` Hz.

    Returns (decimated_signal, actual_fs). The actual fs may differ slightly
    from target when the ratio is not an integer.
    """
    _ensure_1d_signal(signal, "signal", min_len=4)
    fs = _ensure_finite_positive(fs, "fs")
    target_fs = _ensure_finite_positive(target_fs, "target_fs")
    if target_fs >= fs:
        return np.asarray(signal, dtype=np.float64), fs

    q = int(round(fs / target_fs))
    if q < 2:
        return np.asarray(signal, dtype=np.float64), fs

    stages = _decimation_stages(q)
    out = np.asarray(signal, dtype=np.float64)
    actual_fs = fs
    for s in stages:
        out = decimate(out, s, zero_phase=True)
        actual_fs /= s
    return out, actual_fs
```

### Step 7 — Bandpass filter for BR and HR

**Load `references/band-rationale.md` now** for the full justification of why these exact band edges were chosen.

Default bands:
- **BR_BAND_HZ = (0.08, 0.5)** — 4.8 to 30 bpm. The 0.08 Hz lower edge captures slow breathers below 6 bpm. The 0.5 Hz upper edge (30 bpm) is above any realistic adult respiration but below the HR band.
- **HR_BAND_HZ = (0.7, 3.0)** — 42 to 180 bpm. The 0.7 Hz lower edge captures bradycardia below 48 bpm. The 3.0 Hz upper edge captures tachycardia above 150 bpm.

```python
def bandpass(
    signal: FloatArray, fs: float, lo: float, hi: float, order: int = 4
) -> FloatArray:
    """Zero-phase Butterworth bandpass (filtfilt for no group delay)."""
    _ensure_1d_signal(signal, "signal", min_len=2 * (order + 1))
    lo, hi, fs = _ensure_band(lo, hi, fs)
    if not np.all(np.isfinite(signal)):
        raise ValueError("signal contains NaN/Inf before bandpass.")
    sos = butter(order, [lo, hi], btype="band", fs=fs, output="sos")
    from scipy.signal import sosfiltfilt
    filtered = sosfiltfilt(sos, signal)
    return np.asarray(filtered, dtype=np.float64)
```

### Step 8 — Pick peak frequency via PSD

```python
def peak_frequency(
    signal: FloatArray, fs: float, lo: float, hi: float, *, nperseg: int | None = None
) -> tuple[float, FloatArray, FloatArray]:
    """Welch PSD → peak frequency in [lo, hi] Hz.

    Returns (peak_hz, freq_axis, power_axis).
    """
    _ensure_1d_signal(signal, "signal", min_len=8)
    lo, hi, fs = _ensure_band(lo, hi, fs)
    if nperseg is None:
        nperseg = min(len(signal), 1024)
    f, p = welch(signal, fs=fs, nperseg=nperseg)
    mask = (f >= lo) & (f <= hi)
    if not np.any(mask):
        raise ValueError(f"no PSD bins in [{lo}, {hi}] Hz; check fs or band edges")
    f_band = f[mask]
    p_band = p[mask]
    peak_idx = int(np.argmax(p_band))
    return float(f_band[peak_idx]), f_band, p_band
```

### Step 9 — Reject HR second harmonic

**Load `references/harmonic-pitfalls.md` now** for the full harmonic-rejection logic and respiration-leakage handling.

The HR second harmonic (2× HR) often has more PSD power than the fundamental because chest displacement from the heartbeat is non-sinusoidal. The rejection strategy: find the PSD peak in the HR band, then check if half that frequency also has significant power. If the half-frequency peak is comparable in amplitude, the detected peak is likely the harmonic and the true HR is at half the frequency.

```python
def reject_hr_harmonic(
    hr_hz: float, f: FloatArray, p: FloatArray
) -> float:
    """If the detected HR peak looks like a 2nd harmonic, return half the frequency.

    Heuristic: compare the PSD at hr_hz/2 to the PSD at hr_hz. If the
    half-frequency power is at least 60% of the peak power, the peak is
    likely the harmonic.
    """
    f, p = _ensure_psd_pair(f, p)
    if hr_hz <= 0:
        return hr_hz

    half_hz = hr_hz / 2.0
    if half_hz < f[0] or half_hz > f[-1]:
        return hr_hz  # can't check; trust the peak

    # Interpolate power at half_hz
    p_half = float(np.interp(half_hz, f, p))
    p_peak = float(np.interp(hr_hz, f, p))

    if p_peak <= 0:
        return hr_hz
    ratio = p_half / p_peak
    if ratio >= 0.6:
        return half_hz
    return hr_hz
```

### Step 10 — Handle slow breathers (respiration harmonic leakage)

When BR < 10 bpm (0.167 Hz), the respiration harmonics (2× BR, 3× BR) can land inside the HR band and masquerade as heart rate. Notch them out before re-estimating HR.

```python
def notch_respiration_harmonics(
    signal: FloatArray, fs: float, br_bpm: float, *, harmonics: list[int] | None = None
) -> FloatArray:
    """Notch out respiration harmonics that leak into the HR band."""
    _ensure_1d_signal(signal, "signal", min_len=4)
    fs = _ensure_finite_positive(fs, "fs")
    br_hz = br_bpm / 60.0
    if harmonics is None:
        harmonics = [2, 3, 4]
    out = np.asarray(signal, dtype=np.float64)
    for h in harmonics:
        f_notch = br_hz * h
        if f_notch >= fs / 2.0:
            continue
        w0 = f_notch / (fs / 2.0)
        if w0 <= 0 or w0 >= 1:
            continue
        b, a = iirnotch(w0, Q=30.0)
        out = filtfilt(b, a, out)
    return out
```

### Step 11 — Autocorrelation cross-check

```python
def autocorr_bpm(
    signal: FloatArray, fs: float, lo: float, hi: float
) -> float:
    """Estimate bpm from autocorrelation lag as a cross-check on PSD peak."""
    _ensure_1d_signal(signal, "signal", min_len=8)
    lo, hi, fs = _ensure_band(lo, hi, fs)
    sig = np.asarray(signal, dtype=np.float64)
    sig = sig - sig.mean()
    n = len(sig)
    corr = np.correlate(sig, sig, mode="full")[n - 1:]
    corr = corr / corr[0] if corr[0] != 0 else corr
    lo_lag = max(1, int(fs / hi))
    hi_lag = min(n - 1, int(fs / lo))
    if hi_lag <= lo_lag:
        return 0.0
    search = corr[lo_lag:hi_lag + 1]
    peak_lag = lo_lag + int(np.argmax(search))
    if corr[peak_lag] <= 0:
        return 0.0
    return 60.0 * fs / peak_lag
```

### Step 12 — Sanity checks before reporting

Run these last — they are cheap cross-checks that catch the embarrassing mistakes (swapped bands, harmonic doubling) before a wrong number leaves the pipeline.

- **BR < HR** always holds for a live adult at rest. If your output violates it, you almost certainly swapped the two bands.
- **HR × duration_minutes ≈ peak count** in `find_peaks(hr_sig)`. If the count is off by roughly 2×, a harmonic error slipped past the rejection step.
- **Resting-adult plausibility**: HR 50–90 bpm, BR 10–20 bpm. Landing well outside this means re-checking band edges, decimation, and harmonic rejection — not reporting the outlier as fact.

```python
def sanity_check(
    hr_bpm: float, br_bpm: float, hr_sig: FloatArray, duration_s: float
) -> dict[str, bool]:
    """Return per-check pass/fail flags. All-true is a necessary, not sufficient, OK."""
    from scipy.signal import find_peaks

    hr_bpm = _ensure_finite_positive(hr_bpm, "hr_bpm")
    br_bpm = _ensure_finite_positive(br_bpm, "br_bpm")
    duration_s = _ensure_finite_positive(duration_s, "duration_s")
    _ensure_1d_signal(hr_sig, "hr_sig", min_len=4)

    peaks, _ = find_peaks(np.asarray(hr_sig, dtype=np.float64))
    expected_beats = hr_bpm * (duration_s / 60.0)
    count_ok = (
        expected_beats == 0.0
        or 0.5 < (len(peaks) / expected_beats) < 1.8
    )
    return {
        "br_below_hr": br_bpm < hr_bpm,
        "peak_count_consistent": bool(count_ok),
        "hr_plausible": 30.0 <= hr_bpm <= 200.0,
        "br_plausible": 4.0 <= br_bpm <= 40.0,
    }
```

## Examples

### End-to-end CW pipeline

```python
def estimate_vitals_cw(iq: ComplexArray, fs: float) -> dict[str, float | bool]:
    """Full CW pipeline: complex I/Q + sampling rate → HR/BR in bpm with a flag."""
    fs = _ensure_finite_positive(fs, "fs")
    _ensure_1d_signal(iq, "iq", min_len=int(fs))  # need >= ~1 s of data

    clean = remove_clutter_cw(iq)
    phase = extract_phase(clean)
    phase_ds, fs_ds = decimate_to_target(phase, fs, target_fs=50.0)

    br_sig = bandpass(phase_ds, fs_ds, *BR_BAND_HZ, order=4)
    hr_sig = bandpass(phase_ds, fs_ds, *HR_BAND_HZ, order=4)

    br_hz, _, _ = peak_frequency(br_sig, fs_ds, *BR_BAND_HZ)
    hr_hz, f_hr, p_hr = peak_frequency(hr_sig, fs_ds, *HR_BAND_HZ)
    hr_hz = reject_hr_harmonic(hr_hz, f_hr, p_hr)

    hr_bpm = hr_hz * 60.0
    br_bpm = br_hz * 60.0

    # Slow breather? Notch its harmonics and re-estimate HR before trusting it.
    if br_bpm < 10.0:
        hr_clean = notch_respiration_harmonics(phase_ds, fs_ds, br_bpm)
        hr_clean = bandpass(hr_clean, fs_ds, *HR_BAND_HZ, order=4)
        hr_hz, f_hr, p_hr = peak_frequency(hr_clean, fs_ds, *HR_BAND_HZ)
        hr_bpm = reject_hr_harmonic(hr_hz, f_hr, p_hr) * 60.0
        hr_sig = hr_clean

    hr_bpm_ac = autocorr_bpm(hr_sig, fs_ds, *HR_BAND_HZ)
    confident = abs(hr_bpm_ac - hr_bpm) <= 5.0 and br_bpm < hr_bpm
    return {
        "hr_bpm": round(hr_bpm, 1),
        "br_bpm": round(br_bpm, 1),
        "hr_bpm_autocorr": round(hr_bpm_ac, 1),
        "confident": bool(confident),
    }
```

### End-to-end FMCW pipeline

```python
def estimate_vitals_fmcw(
    chirps: SignalArray, fs_slow: float, m_per_bin: float
) -> dict[str, float | bool]:
    """Full FMCW pipeline from raw chirps to HR/BR.

    ``fs_slow`` is the slow-time rate (one sample per chirp = chirp repetition
    frequency). ``m_per_bin`` comes from the sidecar's range resolution.
    """
    fs_slow = _ensure_finite_positive(fs_slow, "fs_slow")
    m_per_bin = _ensure_finite_positive(m_per_bin, "m_per_bin")

    range_matrix = range_fft(chirps, axis=1)
    range_matrix = remove_clutter_fmcw(range_matrix)
    bin_signal, peak_bin = select_range_bin(range_matrix, m_per_bin)

    phase = extract_phase(bin_signal)
    phase_ds, fs_ds = decimate_to_target(phase, fs_slow, target_fs=50.0)

    br_sig = bandpass(phase_ds, fs_ds, *BR_BAND_HZ, order=4)
    hr_sig = bandpass(phase_ds, fs_ds, *HR_BAND_HZ, order=4)

    br_hz, _, _ = peak_frequency(br_sig, fs_ds, *BR_BAND_HZ)
    hr_hz, f_hr, p_hr = peak_frequency(hr_sig, fs_ds, *HR_BAND_HZ)
    hr_bpm = reject_hr_harmonic(hr_hz, f_hr, p_hr) * 60.0
    br_bpm = br_hz * 60.0

    hr_bpm_ac = autocorr_bpm(hr_sig, fs_ds, *HR_BAND_HZ)
    confident = abs(hr_bpm_ac - hr_bpm) <= 5.0 and br_bpm < hr_bpm
    return {
        "hr_bpm": round(hr_bpm, 1),
        "br_bpm": round(br_bpm, 1),
        "hr_bpm_autocorr": round(hr_bpm_ac, 1),
        "range_bin": float(peak_bin),
        "confident": bool(confident),
    }
```

### Wiring it to files

```python
def run_cw_capture(path: str, fmt: str, fs: float, duration_s: float) -> dict[str, float | bool]:
    """Parse a CW capture, validate its length, and estimate vitals."""
    fs = _ensure_finite_positive(fs, "fs")
    duration_s = _ensure_finite_positive(duration_s, "duration_s")
    iq = parse_iq(path, fmt)

    expected = int(round(fs * duration_s))
    if abs(iq.size - expected) > max(1, expected // 100):  # allow ~1% slack
        raise ValueError(
            f"length mismatch: parsed {iq.size} samples, expected ~{expected} "
            f"(fs={fs} Hz x {duration_s} s). Likely an interleave/dtype error."
        )
    return estimate_vitals_cw(iq, fs)
```

## Pitfalls

### Critical ordering rules (never reorder)

1. **Clutter removal BEFORE phase extraction** — a large DC offset anchors the phasor away from the origin and wastes the limited ±π unwrap budget. If you take `np.angle` first and then subtract the mean, you get a wrapped, discontinuous signal that `np.unwrap` cannot repair.
2. **Decimation BEFORE sub-Hz filtering** — IIR bandpass filters at 0.08 Hz are numerically unstable when the Nyquist is at 500 Hz. Decimate to ~50 Hz first so the band edges sit at a reasonable fraction of Nyquist.
3. **Harmonic rejection AFTER peak-picking** — you must first find the PSD peak to know where to look for the half-frequency impostor. Rejecting before picking gives you nothing to reject.
4. **Range-bin selection within a physical prior window** — without the 0.3–1.5 m constraint, a bright static reflector or the DC bin will win the `argmax` and you will extract noise instead of chest motion.

### Common ingestion bugs

- **2× length error**: you forgot to de-interleave (I and Q are stored as alternating real samples). Fix: use `raw[0::2] + 1j * raw[1::2]`.
- **0.5× length error**: you de-interleaved data that was already complex (e.g. `complex128_le` format). Fix: use `np.fromfile(path, dtype="<c16")` directly.
- **Wrong dtype**: the sidecar says `int16` but the file is actually `float32`. Always cross-check `os.path.getsize(path)` against `expected_bytes = n_samples * bytes_per_sample`.
- **Chirp geometry mismatch**: FMCW reshaping fails silently if `n_chirps * samples_per_chirp != file_size`. The `parse_real_chirps` function checks this explicitly — never bypass it.

### Harmonic imposters

- The HR **second harmonic** (2× HR) frequently has *more* PSD power than the fundamental because the heartbeat's chest displacement is non-sinusoidal (sharp systolic pulse, slower diastolic relaxation). This is the single most common source of doubled HR readings.
- **Slow breathers** (BR < 10 bpm = 0.167 Hz): the 2nd and 3rd respiration harmonics land at 0.33 Hz and 0.50 Hz, squarely inside the HR band (0.7–3.0 Hz is safe, but if your BR band upper edge is 0.5 Hz and the 3rd harmonic is at 0.50 Hz, it can leak). Always run `notch_respiration_harmonics` when BR < 10 bpm.

### Filter stability

- SciPy's IIR `decimate` becomes numerically fragile for a single decimation factor above ~13. The `_decimation_stages` helper cascades smaller factors (e.g. 20 → 4 then 5). Never call `decimate(signal, 50)` directly.
- `filtfilt` requires the signal to be at least ~2× the filter order long, or it will raise. The `bandpass` function enforces `min_len=2*(order+1)`.

### Zero-valued samples

- A zero-valued complex sample has undefined phase (`np.angle(0) = 0` but it is not a real measurement). `extract_phase` raises on zero samples — do not suppress this; it means the range bin is empty or the signal is clipped.

## Verification

Run through this checklist after implementing the pipeline:

1. **CW ground truth**: Run the full pipeline on a known CW capture and verify HR/BR against ground truth (e.g. pulse oximeter + respiration belt).
2. **FMCW ground truth**: Run the full pipeline on a known FMCW capture and verify HR/BR against ground truth.
3. **HR harmonic rejection**: Verify `reject_hr_harmonic` correctly identifies 2nd-harmonic dominance — feed a synthetic signal where 2× HR has more power than HR and confirm the output is halved.
4. **BR lower bound**: Verify BR_BAND_HZ lower edge (0.08 Hz = 4.8 bpm) captures slow breathers (< 6 bpm).
5. **HR lower bound**: Verify HR_BAND_HZ lower edge (0.7 Hz = 42 bpm) captures bradycardia (< 48 bpm).
6. **HR upper bound**: Verify HR_BAND_HZ upper edge (3.0 Hz = 180 bpm) captures tachycardia (> 150 bpm).
7. **PSD/autocorrelation cross-check**: Verify the `confident` flag is `False` when PSD and autocorrelation disagree by > 5 bpm.
8. **Swapped bands**: Verify `sanity_check` catches BR > HR (returns `br_below_hr: False`).
9. **2× peak-count error**: Verify `sanity_check` catches when `find_peaks` count is ~2× the expected beat count.
10. **Slow-breather notch**: Verify `notch_respiration_harmonics` recovers HR when BR < 10 bpm by removing the respiration harmonics from the HR band.
11. **Decimation stability**: Test at fs ≥ 500 Hz with a large decimation factor (e.g. fs=2000, target=50 → q=40, cascaded as 8→5 or 5→8) and confirm no NaN/Inf in output.
12. **Clutter before phase**: Verify that calling `extract_phase` on un-cluttered data produces a wrapped, discontinuous signal, while clutter-removed data produces a clean unwrapped trace.
13. **Range-bin prior window**: Verify `select_range_bin` never returns a bin outside `[near_m/m_per_bin, far_m/m_per_bin]`.
14. **Input validation**: Test that empty arrays, real-typed I/Q (where complex is expected), sub-Nyquist band edges, and NaN/Inf inputs all raise clear `TypeError` or `ValueError` messages.
15. **Debugging walkthrough**: Walk through `references/debugging.md` for common failure modes (wrong dtype, missed de-interleave, empty range bin, clutter not removed).

### Quick smoke test (Windows PowerShell)

```powershell
python -c "from radar_vitals import *; import numpy as np; fs=1000; t=np.arange(0,30,1/fs); phase=0.5*np.sin(2*np.pi*0.25*t)+0.1*np.sin(2*np.pi*1.2*t); iq=(1+0.01j)*np.exp(1j*phase); r=estimate_vitals_cw(iq, fs); print(r)"
```

Expected output: `hr_bpm` near 72, `br_bpm` near 15, `confident: True`.

## Related skills

- `references/iq-formats.md` — Binary I/Q parsing formats (load before Step 1)
- `references/range-bin.md` — Subject range bin selection (load before Step 4)
- `references/harmonic-pitfalls.md` — HR harmonic rejection and respiration harmonic leakage (load before Step 8)
- `references/band-rationale.md` — Band edge justification (load before Step 7)
- `references/debugging.md` — Debugging ingestion and SNR issues (load when output looks wrong)
