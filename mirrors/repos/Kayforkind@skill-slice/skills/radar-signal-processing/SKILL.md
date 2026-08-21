---
name: radar-signal-processing
version: 1.1.1
description: "Turns raw CW/FMCW mmWave I/Q captures into a cleaned 1-D slow-time phase trace: Range FFT, clutter removal, range-bin pick, unwrap, then FIR decimate before sub-Hz filters. Use when parsing radar I/Q, vital-signs/breathing phase, or debugging a garbage radar pipeline. Not for pulse/UWB time-of-flight, MIMO angle-of-arrival, or micro-Doppler gesture spectrograms. Never use scipy decimate IIR (phase distortion) or unwrap undersampled jumps greater than pi."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

This skill covers the complete pipeline from a raw binary radar I/Q capture to a clean, decimated 1-D phase trace suitable for downstream vital-signs or motion analysis. The entire pipeline exists to answer one question: *how is the phase of the reflected wave changing over slow time?*

Sub-millimetre chest or wrist motion shows up almost entirely in **phase**, barely at all in amplitude. Every step below is about protecting the phase estimate — removing the static energy that biases it, choosing the range bin that carries it, and unwrapping it without tearing it.

### When NOT to use

This skill does **not** cover:

- **Pulse / UWB time-of-flight ranging** — needs matched filtering, not phase extraction.
- **MIMO angle-of-arrival (beamforming)** — needs spatial covariance processing.
- **Doppler-only gesture radar** — needs micro-Doppler spectrograms.

Those need different front ends, and the phase-centric pipeline here will mislead you.

### Tool-level caveats (real failure modes, not style preferences)

- **`scipy.signal.decimate(x, q, ftype='iir')` distorts the phase you are trying to measure.** The IIR (Chebyshev type-I) path has non-linear phase response, introducing frequency-dependent group delay — exactly the kind of distortion that corrupts a vital-signs phase trace — and it can go numerically unstable for decimation factors above ~13. Always use `ftype='fir'` with `zero_phase=True`: the FIR filter has linear phase and `zero_phase` runs it forward-and-back (`filtfilt`) so the net group delay is zero.
- **`np.unwrap` silently mis-stitches when true per-sample jumps exceed π.** It assumes any adjacent difference larger than π is a 2π wrap and "corrects" it. If the subject genuinely moves fast enough that the real phase steps more than π between two samples (undersampled motion), unwrap inserts phantom 2π jumps. The fix is upstream: raise the sample rate, or apply a mild low-pass before unwrapping so the per-sample step stays below π.
- **Low SNR breaks phase estimation before any of the above matters.** When the reflected signal is buried in noise or interference, `np.angle` returns a near-uniform random walk and nothing downstream recovers it. Diagnose with the scatter / PSD steps in `references/debugging.md` and fix it at the source (better clutter removal, a higher-SNR range bin, or a cleaner capture) rather than filtering harder.

## When to Use

Use this skill when the agent needs to:

- Read interleaved I/Q binary captures (int16, float32, complex64/128) with a sidecar-declared format
- Run a Range FFT on FMCW chirps to produce a 2-D range matrix
- Remove static clutter (DC offset, static reflectors) from CW or FMCW data
- Pick the subject's range bin within a physical prior distance window
- Extract phase with unwrapping from a complex slow-time signal
- Decimate a high-rate slow-time trace before applying sub-Hz narrowband filters
- Debug a radar pipeline that is returning garbage (wrong format, low SNR, unwrap tearing)

## Prerequisites

- **Python 3.9+** with `numpy >= 1.21` (for `numpy.typing`) and `scipy`.
- A **sidecar file** (JSON or YAML) describing the capture format: I/Q dtype, interleave layout, endianness, sample rate, duration, scale factor, and (for FMCW) samples per chirp, chirp rate, and metres per range bin.
- The raw binary capture file on disk.

### Reference files

Load these reference files at the indicated points:

| Reference | When to load |
|---|---|
| `references/iq-formats.md` | Before Step 1 — when parsing raw binary I/Q and you need to confirm the on-disk byte layout (int16 vs float32, interleaved vs real-only, endianness). |
| `references/range-bin.md` | Before Step 4 — when picking the subject range bin and you need details on the physical prior window, coherent neighbour summing, or bin jitter handling. |
| `references/debugging.md` | When the pipeline output is garbage — walk through it in order; it catches most ingestion/SNR bugs (file-size sanity, I-vs-Q scatter, length-vs-duration, mean range profile, wrapped/unwrapped phase, PSD checks). |

## Procedure

### Pipeline overview (order matters)

The steps are ordered so each one sees data the previous one has already cleaned. Two orderings are load-bearing:

1. **Clutter removal must happen before `np.angle`.** A static DC offset shifts the I/Q constellation off the origin, so the measured angle points at the offset, not at the moving target. Recentre first, then read phase.
2. **Decimation must happen before any narrowband (sub-Hz) filtering.** A 0.1 Hz cutoff against a 2 kHz signal is a normalized frequency of 5e-5, where biquad poles crowd the unit circle and SciPy quietly returns NaNs. Drop to ~50 Hz first.

### Shared imports and type aliases

```python
from __future__ import annotations

from pathlib import Path
from typing import Final, Literal

import numpy as np
import numpy.typing as npt
from scipy.signal import decimate, welch

ComplexArray = npt.NDArray[np.complex128]
FloatArray = npt.NDArray[np.float64]
ChirpArray = npt.NDArray[np.floating] | npt.NDArray[np.complexfloating]

IQFormat = Literal[
    "complex64_le_interleaved",
    "int16_le_interleaved_complex",
    "int16_le_real_only",
    "complex128",
]

_BYTES_PER_COMPLEX: Final[dict[str, int]] = {
    "complex64_le_interleaved": 8,
    "int16_le_interleaved_complex": 4,
    "complex128": 16,
}

_MIN_DECIMATE_LEN: Final[int] = 64
```

### Step 1 — Parse binary I/Q to complex samples

The on-disk byte layout (int16 vs float32, interleaved vs real-only, endianness) cannot be recovered from the bytes alone — the same buffer is a valid int16 stream *and* a valid float32 stream. Guessing silently corrupts every later step, so the format comes from the capture's JSON/YAML sidecar and is passed in explicitly. Load `references/iq-formats.md` if you need to confirm the layout.

```python
def load_iq(
    path: str | Path,
    fmt: IQFormat,
    *,
    scale: float = 1.0,
    big_endian: bool = False,
    expected_samples: int | None = None,
) -> ComplexArray:
    """Read a packed radar capture into complex baseband samples."""
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(f"I/Q capture not found: {src}")
    if fmt == "int16_le_real_only":
        raise ValueError(
            "int16_le_real_only is a real-valued ADC dump; load it with "
            "load_real_chirps(path, samples_per_chirp=N) so it can be reshaped into "
            "chirps and Range-FFT'd"
        )
    if fmt not in _BYTES_PER_COMPLEX:
        raise ValueError(
            f"unknown I/Q format {fmt!r}; expected one of {sorted(_BYTES_PER_COMPLEX)}"
        )
    if not np.isfinite(scale) or scale == 0.0:
        raise ValueError(f"scale must be finite and non-zero, got {scale!r}")

    n_bytes = src.stat().st_size
    if n_bytes == 0:
        raise ValueError(f"capture {src} is empty (0 bytes)")
    bytes_per_complex = _BYTES_PER_COMPLEX[fmt]
    if n_bytes % bytes_per_complex:
        raise ValueError(
            f"file size {n_bytes} B is not a multiple of {bytes_per_complex} B/sample "
            f"for {fmt!r}: the file is truncated or carries an unstripped header"
        )

    endian = ">" if big_endian else "<"
    if fmt == "complex64_le_interleaved":
        raw = np.fromfile(src, dtype=f"{endian}f4").astype(np.float64)
        iq = raw[0::2] + 1j * raw[1::2]
    elif fmt == "int16_le_interleaved_complex":
        raw = np.fromfile(src, dtype=f"{endian}i2").astype(np.float64)
        iq = raw[0::2] + 1j * raw[1::2]
    else:  # complex128
        iq = np.fromfile(src, dtype=f"{endian}c16").astype(np.complex128)

    iq = (iq * scale).astype(np.complex128, copy=False)
    if iq.size == 0:
        raise ValueError(f"decoded zero samples from {src}")
    if expected_samples is not None and iq.size != expected_samples:
        ratio = iq.size / expected_samples
        raise ValueError(
            f"decoded {iq.size} complex samples but the sidecar implies "
            f"{expected_samples} ({ratio:.3g}x). A ~2x or ~0.5x ratio usually means a "
            f"format/interleave mismatch; any other ratio usually means a truncated "
            f"file, an unstripped header, or a wrong fs/duration in the sidecar."
        )
    return iq


def load_real_chirps(
    path: str | Path,
    *,
    samples_per_chirp: int,
    big_endian: bool = False,
    scale: float = 1.0,
) -> FloatArray:
    """Load a real-only int16 FMCW dump as a (n_chirp, samples_per_chirp) matrix."""
    if samples_per_chirp < 2:
        raise ValueError(f"samples_per_chirp must be >= 2, got {samples_per_chirp}")
    if not np.isfinite(scale) or scale == 0.0:
        raise ValueError(f"scale must be finite and non-zero, got {scale!r}")
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(f"I/Q capture not found: {src}")

    n_bytes = src.stat().st_size
    if n_bytes % 2:
        raise ValueError(f"file size {n_bytes} B is not a whole number of int16 samples")
    endian = ">" if big_endian else "<"
    raw = np.fromfile(src, dtype=f"{endian}i2").astype(np.float64) * scale
    if raw.size % samples_per_chirp:
        raise ValueError(
            f"{raw.size} samples is not a whole number of "
            f"{samples_per_chirp}-sample chirps; check samples_per_chirp"
        )
    return raw.reshape(-1, samples_per_chirp)
```

### Step 2 — (FMCW only) Range FFT across fast time

Produces a 2-D range matrix `R[n_chirp, n_bin]`. CW captures skip this entirely — they already carry one complex sample per slow-time instant.

```python
def range_fft(chirps: ChirpArray) -> ComplexArray:
    """Range FFT across fast time -> range matrix R[n_chirp, n_bin].

    Per-chirp mean is subtracted first to keep ADC bias + transmit leakage out of
    bin 0. Real ADC dumps use rfft (one-sided); complex baseband uses full fft,
    keeping the positive-range half.
    """
    if chirps.ndim != 2:
        raise ValueError(
            f"chirps must be 2-D [n_chirp, samples_per_chirp], got shape {chirps.shape}"
        )
    if chirps.shape[1] < 2:
        raise ValueError("each chirp needs >= 2 fast-time samples for a Range FFT")
    if not np.all(np.isfinite(chirps)):
        raise ValueError("chirp data contains non-finite values (NaN/inf)")

    centered = chirps - chirps.mean(axis=1, keepdims=True)
    if np.iscomplexobj(chirps):
        spectrum = np.fft.fft(centered, axis=1)
        half = spectrum.shape[1] // 2
        return spectrum[:, :half].astype(np.complex128, copy=False)
    return np.fft.rfft(centered, axis=1).astype(np.complex128, copy=False)
```

### Step 3 — Remove static clutter

Subtract the temporal (slow-time) mean so the moving target's arc is recentred on the origin. A residual DC offset would anchor the phase off zero and eat the unwrap budget.

```python
def remove_static_clutter(data: ComplexArray) -> ComplexArray:
    """Subtract the slow-time mean to null static reflectors and DC.

    1-D CW stream  -> subtract scalar temporal mean.
    2-D FMCW matrix -> subtract per-bin mean across chirps (axis 0 = slow time).
    """
    if not np.all(np.isfinite(data)):
        raise ValueError("input contains non-finite values before clutter removal")
    if data.ndim == 1:
        return (data - data.mean()).astype(np.complex128, copy=False)
    if data.ndim == 2:
        per_bin_mean = data.mean(axis=0, keepdims=True)
        return (data - per_bin_mean).astype(np.complex128, copy=False)
    raise ValueError(f"expected 1-D CW or 2-D FMCW data, got {data.ndim}-D")
```

### Step 4 — (FMCW only) Pick the subject range bin

One or a few bins carry the subject; the rest are noise or static reflectors. Load `references/range-bin.md` for details on the physical prior window and coherent neighbour summing.

```python
def select_range_bin(
    R: ComplexArray,
    m_per_bin: float,
    *,
    min_range_m: float = 0.3,
    max_range_m: float = 1.5,
    n_neighbors: int = 1,
) -> tuple[int, ComplexArray]:
    """Pick the subject's range bin within a physical prior window and coherently
    sum its neighbours into a single 1-D complex slow-time signal.

    A physical prior window (default 0.3-1.5 m for a seated person) keeps the peak
    on the subject, not on DC (bin 0) or bright static reflectors. A coherent
    (complex) sum of neighbours preserves phase and adds ~sqrt(N) SNR; a magnitude
    sum would discard the phase.
    """
    if R.ndim != 2:
        raise ValueError(f"R must be 2-D [n_chirp, n_bin], got shape {R.shape}")
    if not np.all(np.isfinite(R)):
        raise ValueError("range matrix contains non-finite values")
    if not np.isfinite(m_per_bin) or m_per_bin <= 0:
        raise ValueError(f"m_per_bin must be positive and finite, got {m_per_bin!r}")
    if not 0 <= min_range_m < max_range_m:
        raise ValueError(
            f"need 0 <= min_range_m < max_range_m, got {min_range_m}, {max_range_m}"
        )
    if n_neighbors < 0:
        raise ValueError(f"n_neighbors must be >= 0, got {n_neighbors}")

    n_bins = R.shape[1]
    lo = int(min_range_m / m_per_bin)
    hi = min(int(max_range_m / m_per_bin) + 1, n_bins)
    if lo >= hi:
        raise ValueError(
            f"prior window [{min_range_m}, {max_range_m}] m maps to the empty bin "
            f"range [{lo}, {hi}) at {m_per_bin} m/bin; check the sidecar's range "
            f"resolution or widen the window"
        )

    window = slice(lo, hi)
    mean_profile = np.abs(R[:, window]).mean(axis=0)
    best = lo + int(np.argmax(mean_profile))

    left = max(0, best - n_neighbors)
    right = min(n_bins, best + n_neighbors + 1)
    combined = R[:, left:right].sum(axis=1).astype(np.complex128, copy=False)
    return best, combined
```

### Step 5 — Extract phase with unwrap

Read the angle, unwrap the 2π wraps into a continuous trace, and remove the mean so downstream filters see a zero-centred signal.

```python
def extract_phase(signal: ComplexArray) -> FloatArray:
    """Unwrap the phase of a 1-D complex slow-time signal and zero-centre it.

    At 24 GHz, ~1 mm of chest motion is ~1 radian of phase but a negligible
    amplitude change — phase has roughly 40 dB better motion SNR.

    Caveat: np.unwrap assumes true adjacent jumps stay below pi. Undersampled
    fast motion violates that and mis-stitches; raise fs or low-pass before
    unwrapping.
    """
    if signal.ndim != 1:
        raise ValueError(f"expected a 1-D complex signal, got shape {signal.shape}")
    if signal.size < 2:
        raise ValueError("need >= 2 samples to unwrap a phase trace")
    if not np.all(np.isfinite(signal)):
        raise ValueError("signal contains non-finite values; clean upstream first")

    phase = np.unwrap(np.angle(signal)).astype(np.float64, copy=False)
    phase -= phase.mean()
    return phase
```

### Step 6 — Decimate before sub-Hz filtering

If the slow-time rate is `>= 500 Hz` and downstream wants sub-Hz filtering, decimate toward ~50 Hz first. Large decimation factors are split into a chain of small ones (each ≤ 13) because a single huge anti-alias filter is either very long (FIR) or unstable (IIR).

```python
def _factorize_decimation(q: int, *, max_factor: int = 13) -> list[int]:
    """Split a large integer decimation factor into a chain of factors <= max_factor."""
    if q < 1:
        raise ValueError(f"decimation factor must be >= 1, got {q}")
    if q == 1:
        return [1]
    factors: list[int] = []
    remaining = q
    f = max_factor
    while f >= 2 and remaining > 1:
        if remaining % f == 0:
            factors.append(f)
            remaining //= f
        else:
            f -= 1
    if remaining > 1:
        factors.append(remaining)
    return factors


def decimate_phase(
    phase: FloatArray,
    fs: float,
    *,
    target_fs: float = 50.0,
) -> tuple[FloatArray, float]:
    """Anti-alias and downsample a slow-time phase trace toward target_fs.

    Returns the decimated trace and its new sample rate. If fs is already at or
    below target_fs, the input is returned unchanged.
    """
    if phase.ndim != 1:
        raise ValueError(f"phase must be 1-D, got shape {phase.shape}")
    if not np.all(np.isfinite(phase)):
        raise ValueError("phase contains non-finite values; clean upstream first")
    if not np.isfinite(fs) or fs <= 0:
        raise ValueError(f"fs must be positive and finite, got {fs!r}")
    if not np.isfinite(target_fs) or not 0 < target_fs <= fs:
        raise ValueError(
            f"target_fs must be in (0, fs]; got target_fs={target_fs}, fs={fs}"
        )

    q_total = int(fs // target_fs)
    if q_total < 2:
        return phase.astype(np.float64, copy=True), float(fs)

    out: FloatArray = phase.astype(np.float64, copy=True)
    current_fs = float(fs)
    for q in _factorize_decimation(q_total):
        if q < 2:
            continue
        if out.size <= _MIN_DECIMATE_LEN:
            raise ValueError(
                f"signal too short ({out.size} samples) to zero-phase decimate by {q}; "
                f"capture more data or raise target_fs"
            )
        out = decimate(out, q=q, ftype="fir", zero_phase=True).astype(
            np.float64, copy=False
        )
        current_fs /= q
    return out, current_fs
```

### End-to-end orchestrator

```python
def process_capture(
    iq: ComplexArray,
    *,
    slow_time_fs: float,
    is_fmcw: bool,
    samples_per_chirp: int | None = None,
    m_per_bin: float | None = None,
    target_fs: float = 50.0,
) -> tuple[FloatArray, float]:
    """Full pipeline: complex baseband samples -> clean, decimated 1-D phase trace.

    For CW: pass a 1-D complex stream; slow_time_fs is the ADC rate.
    For FMCW: pass a flat complex stream that reshapes into (n_chirp, samples_per_chirp);
    slow_time_fs is the chirp-repetition frequency from the sidecar — NOT the ADC rate,
    since one phase sample is produced per chirp.

    For real-only FMCW, build the range matrix yourself via load_real_chirps ->
    range_fft and call the later steps directly.
    """
    if not np.isfinite(slow_time_fs) or slow_time_fs <= 0:
        raise ValueError(f"slow_time_fs must be positive and finite, got {slow_time_fs!r}")
    if iq.ndim != 1:
        raise ValueError(f"iq must be a 1-D complex stream, got shape {iq.shape}")

    if is_fmcw:
        if samples_per_chirp is None or samples_per_chirp < 2:
            raise ValueError("FMCW requires samples_per_chirp >= 2")
        if m_per_bin is None:
            raise ValueError("FMCW requires m_per_bin (from the sidecar) to pick a bin")
        if iq.size % samples_per_chirp:
            raise ValueError(
                f"{iq.size} samples is not a whole number of "
                f"{samples_per_chirp}-sample chirps"
            )
        chirps = iq.reshape(-1, samples_per_chirp)
        range_matrix = range_fft(chirps)
        range_matrix = remove_static_clutter(range_matrix)
        _, target = select_range_bin(range_matrix, m_per_bin)
    else:
        target = remove_static_clutter(iq)

    phase = extract_phase(target)
    out_fs = float(slow_time_fs)
    if out_fs >= 500.0:
        phase, out_fs = decimate_phase(phase, out_fs, target_fs=target_fs)
    return phase, out_fs
```

### Critical rules (and why they exist)

| Rule | Why |
|---|---|
| Use **phase**, not magnitude | 1 mm motion at 24 GHz ≈ 1 rad; magnitude is ~40 dB worse SNR |
| Clutter removal goes **before** `np.angle` | DC offset anchors phase off zero, eats the unwrap budget |
| **Never** design a 0.1 Hz filter against a 2 kHz signal | SciPy biquad silently NaNs; decimate to ~50 Hz first |
| **Never** `argmax(magnitude)` across all range bins | DC bin (bin 0) and static reflectors dominate — restrict to a physical subject-range window |
| Sum neighbour bins **coherently** (complex), not by magnitude | A chest spans 2-3 jittering bins; complex sum keeps phase and adds ~√N SNR |
| Decimate **FIR + zero_phase**, never IIR | IIR has non-linear phase / group delay that distorts the vital-signs trace |

## Examples

### End-to-end CW capture (float32 interleaved)

```python
# Sidecar says: fmt=complex64_le_interleaved, fs=2000 Hz, duration=30 s, scale=1.0
fs = 2000.0
duration_s = 30.0
iq = load_iq(
    "subject_cw.bin",
    "complex64_le_interleaved",
    expected_samples=round(fs * duration_s),
)
phase, fs_out = process_capture(iq, slow_time_fs=fs, is_fmcw=False)
print(f"{phase.size} samples at {fs_out:.1f} Hz, ready for 0.1-3 Hz analysis")
```

### End-to-end real-only FMCW capture (manual range-matrix path)

```python
# Sidecar says: int16 real-only, samples_per_chirp=256, chirp rate=200 Hz,
# range_per_bin_m=0.039
chirps = load_real_chirps("subject_fmcw.bin", samples_per_chirp=256)
R = range_fft(chirps)
R = remove_static_clutter(R)
best_bin, target = select_range_bin(R, m_per_bin=0.039)
phase = extract_phase(target)
# chirp rate (200 Hz) < 500, so no decimation needed here
print(f"subject at bin {best_bin}; phase trace of {phase.size} samples")
```

## Pitfalls

1. **Format sniffing from raw bytes is unreliable.** The same buffer is a valid int16 stream *and* a valid float32 stream. Always require the sidecar-declared format and pass it explicitly. A ~2x or ~0.5x sample-count ratio after decoding almost always means a format/interleave mismatch.

2. **Using `ftype='iir'` in `scipy.signal.decimate`.** The IIR path has non-linear phase response and introduces frequency-dependent group delay that corrupts the vital-signs trace. It can also go numerically unstable for decimation factors above ~13. Always use `ftype='fir'` with `zero_phase=True`.

3. **`np.unwrap` mis-stitching on undersampled motion.** If the subject moves fast enough that real phase steps exceed π between samples, unwrap inserts phantom 2π jumps. Fix upstream: raise the sample rate or apply a mild low-pass before unwrapping.

4. **Low SNR produces a random-walk phase.** When the reflected signal is buried in noise, `np.angle` returns a near-uniform random walk and nothing downstream recovers it. Fix at the source (better clutter removal, higher-SNR range bin, cleaner capture), not by filtering harder. Load `references/debugging.md` and walk through the scatter / PSD checks.

5. **Designing a sub-Hz biquad against a kHz-rate signal.** A 0.1 Hz cutoff against 2 kHz gives a normalized frequency of 5e-5, where biquad poles crowd the unit circle and SciPy silently returns NaNs. Always decimate to ~50 Hz first.

6. **`argmax(magnitude)` across all range bins.** Bin 0 (DC) and bright static reflectors (walls, radar enclosure) almost always out-power a breathing chest. Restrict the search to a physical subject-distance window (default 0.3–1.5 m).

7. **Summing neighbour bins by magnitude instead of coherently.** A magnitude sum discards the phase — the one quantity you need. Always sum complex values to preserve phase and gain ~√N SNR.

8. **Inferring FMCW slow-time rate from the ADC rate.** For FMCW, one phase sample is produced per chirp, so `slow_time_fs` is the chirp-repetition frequency, not the ADC rate. Inferring it from the ADC rate is a classic 2x error. Always pass it explicitly from the sidecar.

9. **Unstripped headers or truncated files.** If the file size is not a multiple of the expected bytes-per-complex-sample, the file is either truncated or carries an unstripped header. The `load_iq` function checks this and fails loudly — do not suppress the error.

## Verification

Run these checks to confirm the pipeline is working correctly:

### Self-test (synthetic breathing signal)

```python
def _self_test() -> None:
    """Smoke-test the pipeline on a synthetic breathing signal.

    Uses a known ground-truth frequency (0.3 Hz) so we can assert the recovered
    PSD peaks where it should — catching sign/scale/ordering regressions without
    needing a real capture on disk.
    """
    rng = np.random.default_rng(0)
    fs = 2000.0
    duration_s = 30.0
    t = np.arange(int(fs * duration_s)) / fs

    breaths_hz = 0.3
    motion_rad = 2.0 * np.sin(2 * np.pi * breaths_hz * t)
    static_clutter = 5.0 + 0.0j
    noise = 0.02 * (rng.standard_normal(t.size) + 1j * rng.standard_normal(t.size))
    iq: ComplexArray = (
        static_clutter + np.exp(1j * motion_rad) + noise
    ).astype(np.complex128)

    phase, fs_out = process_capture(iq, slow_time_fs=fs, is_fmcw=False)

    assert np.all(np.isfinite(phase)), "non-finite phase escaped the pipeline"
    assert fs_out < fs, f"expected decimation to lower the rate, got {fs_out} Hz"

    freqs, psd = welch(phase, fs=fs_out, nperseg=min(phase.size, int(fs_out * 25)))
    peak_hz = float(freqs[int(np.argmax(psd))])
    assert abs(peak_hz - breaths_hz) < 0.1, (
        f"recovered {peak_hz:.3f} Hz, expected {breaths_hz} Hz"
    )
    print(f"OK: recovered breathing at {peak_hz:.3f} Hz (truth {breaths_hz} Hz)")


if __name__ == "__main__":
    _self_test()
```

**Expected output:**
```
OK: recovered breathing at 0.300 Hz (truth 0.3 Hz)
```

### Checklist for real captures

- [ ] Confirm `len(iq) == round(fs * duration)` — pass `expected_samples` to `load_iq` so this is enforced automatically.
- [ ] Scatter `iq.real` vs `iq.imag`: expect an arc near the origin, not a tight blob (under-cluttered) or a uniformly filled plane (low SNR).
- [ ] For FMCW, plot `np.abs(R).mean(axis=0)` and confirm a discrete peak inside the prior window before trusting `select_range_bin`.
- [ ] Plot the unwrapped phase: a smooth low-frequency drift with ≤5 rad oscillations is healthy; exact-2π steps mean unwrap failed (raise SNR / fs first).
- [ ] If the output is garbage, load `references/debugging.md` and walk through it in order.

## Related skills

No related skills are specified.
