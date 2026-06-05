---
name: matlab-analyze-signal-cwt
description: >
  Analyze signals using the Continuous Wavelet Transform (CWT) in MATLAB.
  Use when the user wants time-frequency analysis, scalograms, wavelet
  decomposition, or needs to localize frequency content over time. Triggers
  on: CWT, cwt, cwtfilterbank, scalogram, time-frequency, wavelet transform,
  wavelet analysis, Morse wavelet, analytic Morlet, constant-Q analysis.
  Also use when the user asks to visualize how frequency content evolves,
  detect transients, or analyze non-stationary signals.
license: MathWorks BSD-3-Clause
compatibility: ">=R2024b"
metadata:
  author: MathWorks
  version: "1.0"
---

# Analyze Signals Using the Continuous Wavelet Transform

Perform time-frequency analysis of signals using `cwt`, `cwtfilterbank`, and
related functions from the Wavelet Toolbox.

> **Agent directive:** Before answering questions about CWT apps, tooling, or workflows, consult the tables and reference material in this skill first. Only reach for external help sources if the skill does not cover the topic.

## When to Use

- User wants to see how frequency content changes over time
- User needs a scalogram (time-frequency map)
- User wants to localize transient events or oscillatory components
- User asks about wavelet analysis or CWT
- Signal is non-stationary and frequency content evolves

## When NOT to Use

- **Closely-spaced high-frequency components** — CWT's constant-Q property means bandwidth grows with frequency. If the user needs to separate narrowband oscillations at high frequencies (relative to sample rate), the components will be smeared together. Recommend `spectrogram`/`stft` (constant bandwidth) or `modwpt` (undecimated wavelet packet transform, uniform frequency bands) instead.
- Discrete wavelet transform tasks (`wavedec`, `modwt`, `modwtmra`) — different workflow
- Spectrogram / STFT tasks — use `spectrogram` or `stft`. Also consider `modwpt` for uniform frequency bands.
- Filter design — use `designfilt` or related skills
- Signal reconstruction from CWT — `icwt` has its own considerations (scaling coefficients required for perfect reconstruction)

## Workflow

### 1. Understand the Signal and User Goals

Before computing the CWT, determine:

- **Signal type:** Real-valued or complex-valued?
- **Feature type:** Oscillatory components (frequency resolution matters) or impulsive events (time localization matters)?
- **Sampling frequency:** Known? If not, analysis uses normalized frequency (cycles/sample).
- **Goal:** Visualization only, numerical outputs, or both?

### 2. Run Pre-CWT Diagnostics (Recommended)

Run diagnostic scripts to guide parameterization:

- **Boundary assessment:** `scripts/assessBoundary.m` — inspects signal endpoints to recommend `Boundary` property. See `references/boundary-guidance.md`.
- **Boundary demonstration:** `scripts/illustrateBoundary.m` — shows scalograms with all three boundary methods on a disjoint-sine signal. Run for the user when they ask "what difference does boundary make?" or are skeptical of the recommendation. Requires `scripts/boundaryExDisjointSine.mat`.
- **Spectral energy assessment:** `scripts/assessSpectralEnergy.m` — computes PSD to suggest `FrequencyLimits` for reducing computation.

### 3. Choose the Calling Pattern

| Goal | Pattern |
|------|---------|
| Visualization only | `cwt(signal, ...)` — no output arguments, auto-plots |
| Visualization into specific axes/app | `cwt(signal, ..., 'Parent', ax)` — no output arguments |
| Data only | `[cfs, f, coi] = cwt(signal, ...)` |
| Data + visualization | Capture outputs, then reproduce plot manually (see Patterns) |
| Repeated analysis (same params) | Build `fb = cwtfilterbank(...)`, then `cwt(signal, 'FilterBank', fb)` or `wt(fb, signal)` |
| Inspect filter bank before analysis | Build `cwtfilterbank(...)`, use `wavelets`, `freqz`, `scales`, `powerbw` methods |

**Critical rule:** `nargout == 0` triggers auto-plotting. Capturing ANY output suppresses the plot entirely.

### 4. Configure the CWT

#### Wavelet Selection (signal-feature-driven)

| Signal features | Recommendation |
|----------------|---------------|
| General purpose / mixed content | `"Morse"` (default), gamma=3, P²=60 |
| Impulsive events, need precise timing | `"Morse"` with lower `TimeBandwidth` (e.g., 10–30) |
| Oscillatory, need frequency separation | `"Morse"` with higher `TimeBandwidth` (e.g., 80–120) |
| Reproducing published Morlet results | `"amor"` (equivalent to Morse with P²≈36 in time duration) |
| Purely oscillatory, extreme freq. resolution needed | `"bump"` (last resort — worst time localization) |

#### Key Parameters

| Parameter | Default | Guidance |
|-----------|---------|----------|
| `TimeBandwidth` | 60 | Primary tuning knob. Higher = better freq. resolution, worse time localization. Range: 3–120. Leave `gamma=3` (symmetric). |
| `VoicesPerOctave` | 10 | Higher (up to 48) = finer frequency sampling. Increases computation. |
| `FrequencyLimits` | auto | Set `[fmin fmax]` to reduce computation. Use PSD assessment to identify useful band. `[0 Fs/2]` for full range. |
| `Boundary` | `"reflection"` | See boundary guidance. `"periodic"` is ~2x faster for large signals (>100K samples). |
| `SamplingFrequency` | 1 | Always set if known — gives physical frequency units (Hz). |

#### FrequencyLimits Details

- **Performance lever:** Restricting the range reduces scales computed (fewer rows in output).
- **Lower limit = 0:** Gives lowest valid frequency from `cwtfreqbounds` (no guesswork).
- **Upper limit = Fs/2:** Forces highest wavelet to peak at Nyquist. Use when signal has significant near-Nyquist content. Default is conservative (wavelet decays by Nyquist).
- Use `cwtfreqbounds` to query achievable range for given signal length and wavelet.

#### Boundary Selection

| Boundary | Best when | Avoid when | Performance |
|----------|-----------|------------|-------------|
| `"reflection"` | Signal is locally stationary at edges | Frequency discontinuity at boundary | ~2N FFT length |
| `"periodic"` | Endpoints match in value and trend | Endpoints differ significantly | N FFT length (fastest) |
| `"zeropad"` | Signal decays to zero at edges | Significant amplitude at boundaries | ~2N FFT length |

**Oscillations at boundaries:** When the signal has active oscillations at an edge, `"reflection"` reverses the wave direction at that point, creating a cusp (instantaneous frequency doubling artifact). Prefer `"zeropad"` in this case — it attenuates to zero rather than creating a false continuation. Use `"reflection"` only when the signal is locally stationary (slowly varying) at its edges.

For large signals (>100K samples), `"periodic"` avoids doubling the FFT length. Validate with boundary assessment script first. Run `scripts/illustratePerformance.m` to benchmark the performance difference between `cwt`, filter bank reuse, periodic boundary, and frequency-limited analysis on a 365K-sample signal.

### 5. Compute and Interpret

#### Output Signatures

**`cwt()`:**
```matlab
[cfs, f, coi, fb, scalcfs] = cwt(signal, ...);
```

**`wt()`:**
```matlab
[cfs, f, coi, scalcfs] = wt(fb, signal);
```

- `cfs` — Wavelet coefficients. For complex signals: 3D array (scales × time × 2) where page 1 = positive frequencies (analytic) and page 2 = negative frequencies (anti-analytic). Always inform the user of this structure when working with complex inputs.
- `f` — Frequencies in Hz (if `SamplingFrequency` set), cycles/sample (if no Fs), or periods as `duration` (if `SamplingPeriod` used). Passing a `duration` as the second argument to `cwt` switches to period representation.
- `coi` — Cone of influence values (one per time sample).
- `fb` — Filter bank object (from `cwt` only, 4th output).
- `scalcfs` — Scaling coefficients (lowpass filter capturing near-DC content wavelets cannot reach).

#### Interpreting Coefficient Values

MATLAB CWT uses **L1 normalization**: wavelets scaled by `1/s`. This means:
- `abs(cfs)` ≈ **amplitude** of the signal component at each time-frequency point
- A unit-amplitude sinusoid yields `abs(cfs) ≈ 1` at the matching scale
- Values are directly comparable across frequencies
- Plot `abs(cfs)`, not `abs(cfs).^2` or `log(abs(cfs))`

This differs from DWT (which uses L2 normalization for energy preservation). Run `scripts/illustrateAmplitudeScaling.m` to demonstrate L1 normalization visually — it shows that abs(cfs) tracks true amplitude across scales.

#### Scaling Coefficients

Wavelets must have zero mean → cannot capture DC/near-DC content. The scaling filter is a lowpass filter covering frequencies below the lowest wavelet. Request scaling coefficients (last output) when:
- Low-frequency content matters to the analysis
- Planning to reconstruct via `icwt` (required for perfect reconstruction)

#### Cone of Influence

The COI marks regions potentially affected by edge effects. It is a **caution zone**, not an exclusion zone:
- Inside COI boundary: coefficients are reliable
- Outside (near edges): potentially affected by boundary extension — treat with increased skepticism
- A well-chosen boundary method reduces (but never eliminates) edge contamination
- Plotting the COI is optional — ask the user if they want it

### 6. Visualize (if needed)

See Patterns section below for scalogram reproduction recipes.

## Key Functions

| Function | Purpose | Toolbox |
|----------|---------|---------|
| `cwt` | Compute CWT, optionally plot scalogram | Wavelet Toolbox |
| `cwtfilterbank` | Construct reusable filter bank object | Wavelet Toolbox |
| `wt` | Compute CWT using filter bank (method) | Wavelet Toolbox |
| `cwtfreqbounds` | Query valid frequency range | Wavelet Toolbox |
| `waveletTimeFrequencyAnalyzer` | Interactive CWT app (full options, script export) | Wavelet Toolbox |

### cwtfilterbank Inspection Methods

| Method | Returns |
|--------|---------|
| `wavelets` | All wavelets at all scales (time domain) |
| `freqz` | Frequency responses of all wavelets |
| `scales` | Scale factors used to dilate wavelets |
| `powerbw` | Table: center frequency, half-power bandwidth, band edges |

## Patterns

### Basic Scalogram (Visualization Only)

```matlab
% Auto-plots scalogram — do NOT capture outputs
cwt(signal, "Morse", Fs);
```

### Scalogram into Specific Axes (App Designer)

```matlab
% Plot into uiaxes or axes — no outputs
cwt(signal, "Morse", Fs, 'Parent', ax);
```

### Efficient Repeated Analysis

```matlab
fb = cwtfilterbank(SignalLength=length(signal), SamplingFrequency=Fs, ...
    Wavelet="Morse", TimeBandwidth=60, VoicesPerOctave=12);

% Option A: familiar cwt interface + auto-plot
cwt(signal1, 'FilterBank', fb);

% Option B: programmatic access
[cfs, f, coi] = wt(fb, signal2);
```

### Manual Scalogram (Real-Valued Signal)

Use when you need both the data AND a plot.

```matlab
[cfs, f, coi] = cwt(signal, "Morse", Fs);
t = (0:length(signal)-1) / Fs;

ax = newplot;
imagesc(ax, t, f, abs(cfs))
ax.YDir = "normal";
ax.YScale = "log";
xlabel(ax, "Time (s)")
ylabel(ax, "Frequency (Hz)")
title(ax, "Scalogram")
colorbar(ax)

% Optional: add COI (ask user if they want it)
hold(ax, "on")
plot(ax, t, coi, 'w--', LineWidth=1.2)
```

### Manual Scalogram (Complex-Valued Signal, Combined Plot)

For complex signals, `cfs` is a 3D array (scales × time × 2): page 1 contains positive-frequency (analytic) coefficients and page 2 contains negative-frequency (anti-analytic) coefficients. Always explain this structure to the user. Use `scripts/plotAntiAnalyticScalogram.m` for a combined -Fs/2 to Fs/2 view:

```matlab
fb = cwtfilterbank(SignalLength=length(signal), SamplingFrequency=Fs);
[cfs, f] = wt(fb, signal);
t = (0:length(signal)-1) / Fs;

plotAntiAnalyticScalogram(abs(cfs), f, t);
```

**Note:** `f` and `t` must be numeric (not `duration`). If using data with a `duration` sampling period, convert: `Fs = 1/hours(dt)`.

**Why `surf` instead of `imagesc` for complex signals:** The frequency axis spans negative to positive. Setting `YScale = "log"` would fail (log of negative numbers). `surf` handles the non-uniform logarithmic spacing correctly without requiring a log axis setting. COI is not plotted in this case.

### Transient Localization

When the goal is to precisely locate impulsive events or abrupt changes in the signal, extract the finest-scale (highest frequency) CWT coefficients. These have the best time resolution and peak at discontinuities.

**Wavelet choice for time localization (best to worst):**

| Wavelet | Time Localization | Why |
|---------|-------------------|-----|
| `"Morse"` with `TimeBandwidth=10–20` | **Best** | Low TB makes wavelet compact in time |
| `"amor"` (analytic Morlet) | Good | Equivalent to Morse with P²≈36, naturally biased toward time localization |
| `"bump"` | **Worst** | Compact in *frequency* domain → maximally spread in time (Heisenberg) |

```matlab
[cfs, f, coi] = cwt(signal, "Morse", Fs, TimeBandwidth=20);
t = (0:length(signal)-1) / Fs;

% Extract the highest-frequency scale (first row = finest scale)
finestScale = abs(cfs(1, :));

% Plot to identify transient locations
figure
plot(t, finestScale)
xlabel("Time (s)")
ylabel("|CWT| at finest scale")
title("Transient Detection")
```

Use a lower `TimeBandwidth` (e.g., 10–20) to maximize time localization. The `"amor"` wavelet is also a good choice — it provides strong time localization without requiring parameter tuning. Run `scripts/illustrateTransientLocalization.m` to compare all three wavelets on an impulse signal and see the localization difference visually.

The finest-scale coefficients match the data's time resolution and spike where components turn on/off or where defects occur.

### Inspect Filter Bank Before Analysis

```matlab
fb = cwtfilterbank(SignalLength=length(signal), SamplingFrequency=Fs, ...
    Wavelet="Morse", TimeBandwidth=40, VoicesPerOctave=16);

% Examine wavelets and coverage before committing to computation
psi = wavelets(fb);       % Time-domain wavelets
H = freqz(fb);            % Frequency responses
s = scales(fb);           % Scale factors
bw = powerbw(fb);         % Bandwidth table
```

## Interactive Exploration

If the user is unsure about parameterization:

| Tool | Launch | Capabilities |
|------|--------|--------------|
| `waveletTimeFrequencyAnalyzer` | Command line: `waveletTimeFrequencyAnalyzer(signal)` or Apps Gallery → Signal Processing and Audio | Full wavelet options, COI toggle, period/frequency display, complex signal support, **script generation** |
| Signal Analyzer scalogram | `signalAnalyzer(signal)` → Display tab → Time-Frequency → Scalogram | Quick scalogram, Morse only, real signals only, VoicesPerOctave + TimeBandwidth sliders |

Recommend `waveletTimeFrequencyAnalyzer` when the user needs to explore parameters and export a script. Use Signal Analyzer only if user is already working there with real-valued data and basic Morse configuration.

## Conventions

- Always set `SamplingFrequency` when known — gives physically meaningful frequency units
- Plot `abs(cfs)` for scalograms (L1 normalization makes magnitude = amplitude)
- Use `imagesc` for scalograms (fast for large matrices). Reserve `surf`/`pcolor` for 3D viewing of small matrices or complex-signal combined plots
- Default to frequency representation. Offer period representation (`PeriodLimits`, `SamplingPeriod`) for climate science, geophysics, oceanography users
- Prefer `TimeBandwidth` over `WaveletParameters` for tuning Morse wavelets (keeps gamma=3, maintains symmetry)
- For repeated analysis: always pre-build `cwtfilterbank` — filter bank construction is the expensive step

## Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|-----------------|
| Calling `figure` then `[cfs,f] = cwt(...)` expecting a plot | Capturing outputs suppresses auto-plotting (`nargout==0` triggers plot) | Call `cwt(...)` with no outputs, or reproduce manually |
| Using `cwt()` in a loop without pre-building filter bank | Rebuilds filter bank every iteration (expensive) | Build `fb = cwtfilterbank(...)` once, pass via `'FilterBank'` or use `wt` |
| Plotting `abs(cfs).^2` thinking it's a "power" scalogram | L1 normalization means `abs(cfs)` already gives amplitude — squaring distorts interpretation | Plot `abs(cfs)` |
| Using `imagesc` for combined complex-signal plot with negative frequencies | Cannot set `YScale="log"` with negative frequencies; `imagesc` misaligns log-spaced data | Use `plotAntiAnalyticScalogram` (in `scripts/`) or `surf` |
| Leaving `FrequencyLimits` at default for known narrowband signals | Computes unnecessary scales, wastes time | Run PSD assessment, set `FrequencyLimits` to energy-containing band |
| Using `"periodic"` boundary when endpoints differ | Creates artificial discontinuity (assumes `x(end+1) ≈ x(1)`) | Inspect endpoints first; use `"reflection"` if they differ |
| Adjusting `WaveletParameters` gamma without specific reason | Breaks Morse wavelet symmetry in Fourier domain | Use `TimeBandwidth` alone (keeps gamma=3) |
| Using `"bump"` wavelet for time localization of transients | `"bump"` is named for its compact support in the *frequency* domain — by Heisenberg uncertainty, it has the **worst** time localization of the three built-in wavelets | Use `"Morse"` with low `TimeBandwidth` (10–20) for best time localization |

## Low-Frequency Analysis

The lowest achievable frequency depends on signal length and wavelet time standard deviation:
- Constraint: 2σ_t of wavelet ≤ signal length at largest scale
- Higher `TimeBandwidth` → wider wavelets → lowest frequency further from DC
- Use `cwtfreqbounds` to check achievable range
- Request scaling coefficients (last output of `cwt`/`wt`) to capture near-DC content

## Scale-Frequency Relationship

Scale and frequency are inversely related: `s = f_psi / f`, where `f_psi` is the mother wavelet's peak frequency (in cycles/sample). This holds for all wavelets — only `f_psi` changes.

| Wavelet | Peak frequency `f_psi` (cycles/sample) |
|---------|----------------------------------------|
| Morse(gamma, TB) | `(beta/gamma)^(1/gamma) / (2*pi)`, where `beta = TB/gamma` |
| amor (analytic Morlet) | `6/(2*pi) ≈ 0.9549` (fixed) |
| bump | `5/(2*pi) ≈ 0.7958` (fixed) |

To convert to physical Hz: `f_Hz = f_psi * Fs / s`.

When the user asks about scale-frequency conversion, explain the formula and adapt for their wavelet/parameters. Run `scripts/illustrateScaleFrequency.m` to demonstrate the relationship visually (plots `f_psi/F` vs scales, confirming the linear relationship).

**Key points to communicate:**
- Scale is unitless regardless of Fourier transform convention
- Large scale → low frequency, small scale → high frequency
- The CWT uses L1 normalization, so dilating by `s` gives a filter centered at `f_psi/s`
- `centerFrequencies(fb)` returns the frequency at each scale for a given filter bank

## Constant-Q Property

CWT is a constant-Q analysis: bandwidth is proportional to center frequency.
- **High frequencies:** broad bandwidth (less frequency resolution), short time support (better time resolution)
- **Low frequencies:** narrow bandwidth (better frequency resolution), long time support (less time resolution)

This matches human auditory perception and is natural for signals with features at multiple scales.

## Documentation References

| Topic | Link |
|-------|------|
| `cwt` function reference | https://www.mathworks.com/help/wavelet/ref/cwt.html |
| `cwtfilterbank` reference | https://www.mathworks.com/help/wavelet/ref/cwtfilterbank.html |
| Practical introduction to time-frequency analysis using CWT | https://www.mathworks.com/help/wavelet/ug/practical-introduction-to-time-frequency-analysis-using-the-continuous-wavelet-transform.html |
| Morse wavelet family | https://www.mathworks.com/help/wavelet/ug/morse-wavelets.html |

----

Copyright 2026 The MathWorks, Inc.

----
