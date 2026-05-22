---
name: matlab-process-rf-baseband
description: >
  Process complex baseband RF signals using standalone System Objects in RF Toolbox: rf.Amplifier,
  rf.Mixer, rf.Filter, rf.Sparameter, and rf.PAmemory. Use when applying nonlinear amplifier models
  (polynomial, AM/PM, modified Rapp, Saleh) to baseband signals, modeling mixer impairments (I/Q
  imbalance, phase noise, LO offset), filtering RF signals in complex baseband, processing signals
  through S-parameter data, or modeling power amplifiers with memory effects. These System Objects
  process signals entirely in MATLAB -- no Simulink required. Trigger on rf.Amplifier, rf.Mixer,
  rf.Filter, rf.Sparameter, rf.PAmemory, rf.MismatchLoss, complex baseband amplifier, baseband
  mixer, IQ imbalance, phase noise mixer, modified Rapp, Saleh model, memory polynomial PA,
  AM/PM table, RF System Object, visualize amplifier, visualize mixer, EVM, error vector magnitude,
  ACPR, ACLR, spectral regrowth, PA characterization.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.1"
---

# RF Component System Objects

Process complex baseband RF signals through standalone System Objects -- amplifiers, mixers, filters, S-parameter models, and power amplifiers with memory. All objects follow the standard System Object lifecycle (`step`/`reset`/`release`) and process data entirely in MATLAB with no Simulink dependency.

## When to Use

- Processing complex baseband signals through nonlinear amplifier models (polynomial, AM/PM, modified Rapp, Saleh)
- Modeling mixer impairments: I/Q imbalance, phase noise, LO offset
- Filtering RF signals in complex baseband domain
- Processing signals through S-parameter data via rational fitting
- Modeling power amplifiers with memory effects (Volterra series)
- Running standalone RF signal processing without Simulink

## When NOT to Use

- Cascade budget analysis (gain, NF, IP3) -- use `matlab-analyze-rf-budget`
- Mixer spur analysis and intermodulation tables -- use `matlab-analyze-rf-mixer`
- Full system time-domain simulation from rfbudget -- use `matlab-simulate-rf-system`
- Frequency-domain S-parameter manipulation -- use `matlab-manage-sparameters`
- LC filter synthesis for rfbudget -- use `matlab-create-rfbudget-elements` (rffilter)

## Workflow

1. **Create object** — Instantiate rf.Amplifier, rf.Mixer, rf.Filter, or rf.Sparameter
2. **Configure** — Set model type, nonlinearity, noise, and impairment properties
3. **Process** — Call `obj(inputSignal)` to step through one frame of data
4. **Analyze** — Measure output power, EVM, spectrum; visualize with `visualize(obj)`
5. **Clean up** — Call `release(obj)` before modifying properties or ending

## System Object Lifecycle

All `rf.*` System Objects share this pattern:

```matlab
obj = rf.Amplifier(Gain=15, OIP3=35);   % Create
out = obj(in);                            % Step (process one frame)
reset(obj);                               % Reset internal state
out2 = obj(in2);                          % Step again
release(obj);                             % Release (allows property changes)
obj.Gain = 20;                            % Modify properties
out3 = obj(in3);                          % Re-setup on next step
```

**Properties are locked** between first `step` and `release`. Attempting to change a Nontunable property without calling `release` first errors. Tunable properties (like `Gain`) can be changed between step calls.

## rf.Amplifier -- Nonlinear Amplifier Models

### Construction

```matlab
amp = rf.Amplifier;                                    % All defaults
amp = rf.Amplifier(Gain=15, OIP3=35);                 % Polynomial (default)
amp = rf.Amplifier(Model='ampm', Table=ampmData);     % AM/PM table
amp = rf.Amplifier(Model='modified-rapp', MagnitudeGainDB=15, Vsat=1.5);
amp = rf.Amplifier(Model='saleh', InputScaleDB=-10);
```

### Nonlinear Models

| Model | Description | Key Properties |
|-------|-------------|----------------|
| `'poly'` (default) | Higher-order polynomial from multiple compression params | Gain, OIP3/IIP3, IP1dB/OP1dB, IPsat/OPsat (uses all that are set) |
| `'cubic'` | 3rd-order polynomial from ONE compression param | Gain, Nonlinearity (selects which param), OIP3/IIP3/IP1dB/OP1dB/IPsat/OPsat |
| `'ampm'` | AM/AM and AM/PM lookup table | Table (M-by-3: [Pin_dBm, Pout_dBm, Phase_deg]) |
| `'modified-rapp'` | Modified Rapp model | MagnitudeGainDB, Vsat, MagnitudeSmooth, PhaseGainRadian, PhaseSaturation, PhaseSmooth |
| `'saleh'` | Saleh model | InputScaleDB, AmAmParameters, AmPmParameters, OutputScaleDB |

### `poly` vs `cubic` Model

- **`poly`** (default): Fits a higher-order polynomial using ALL compression parameters you provide (IP3, P1dB, Psat). The `Nonlinearity` property is irrelevant -- do not set it. Just set whichever compression params you have data for and the polynomial uses all of them to shape the AM/AM curve.
- **`cubic`**: Fits a 3rd-order (cubic) polynomial from a SINGLE compression parameter, selected by the `Nonlinearity` property. Extra params are stored but ignored in the model.

```matlab
% poly: uses ALL set compression params to shape the polynomial
amp = rf.Amplifier(Gain=15, Model='poly', OIP3=35, OP1dB=25, OPsat=30);

% cubic: uses ONLY the ONE param selected by Nonlinearity
amp = rf.Amplifier(Gain=15, Model='cubic', Nonlinearity='OIP3', OIP3=35);
```

### Compression Parameters -- Input vs Output

Each compression metric has an input-referred and output-referred form, related through the gain:

| Metric | Output-referred | Input-referred | Relationship |
|--------|----------------|----------------|--------------|
| IP3 | `OIP3` | `IIP3` | OIP3 = IIP3 + Gain (set either one) |
| P1dB | `OP1dB` | `IP1dB` | OP1dB = IP1dB + Gain - 1 (set either one) |
| Psat | `OPsat` | `IPsat` | Independent -- both can be set simultaneously |

For IP3 and P1dB, set whichever form your datasheet provides -- MATLAB converts internally via the gain. For Psat, `IPsat` and `OPsat` are truly independent parameters (input saturation and output saturation) and both can be specified together. Convention:
- **Amplifiers** typically specify output values: `OIP3`, `OP1dB`, `OPsat`
- **Mixers and modulators** typically specify input values: `IIP3`, `IP1dB`, `IPsat`

```matlab
% Amplifier -- use output-referred (datasheet convention)
amp = rf.Amplifier(Gain=15, OIP3=35, OP1dB=25);

% Mixer -- use input-referred (datasheet convention)
mix = rf.Mixer(Model='demod', Gain=-6, RF=2.4e9, LO=2.1e9, IIP3=10);
```

### Nonlinearity Property (cubic model only)

The `Nonlinearity` property selects which single compression parameter defines the 3rd-order nonlinearity for `Model='cubic'`. It is **not relevant** for `Model='poly'` (which uses all set params).

Options: `'IIP3'`, `'OIP3'` (default), `'IP1dB'`, `'OP1dB'`, `'IPsat'`, `'OPsat'`.

**Gotcha -- `Nonlinearity` is irrelevant for poly:** Setting `Nonlinearity` with `Model='poly'` emits "not relevant" warning. For poly, just set the compression params directly -- the model uses all of them.

**Gotcha -- constructor NV-pair processing order:** When setting `Nonlinearity` in the constructor (for cubic), MATLAB processes NV pairs in internal order, not your order. This causes "not relevant" warnings. The warnings are harmless -- values ARE applied and the object works correctly.

**Gotcha -- silent misuse with OPsat in cubic:** `rf.Amplifier(Gain=15, Model='cubic', OPsat=30)` accepts `OPsat` silently but `Nonlinearity` stays `'OIP3'` with `OIP3=Inf` -- meaning no compression is applied. Always set `Nonlinearity` to match your param when using cubic.

**Gotcha -- differs from rfbudget amplifier:** The rfbudget `amplifier` element uses `OIP3` directly without a `Nonlinearity` selector. Do not confuse the two APIs.

### Noise

```matlab
amp = rf.Amplifier(Gain=15, OIP3=35, ...
    IncludeNoise=true, NoiseType='NF', NF=2, ...
    SampleRate=10e6);
```

| Property | Default | Description |
|----------|---------|-------------|
| `IncludeNoise` | false | Enable thermal noise injection |
| `NoiseType` | `'noise-temperature'` | `'noise-temperature'`, `'NF'`, or `'noise-factor'` |
| `NoiseTemperature` | 290 | Noise temperature (K) |
| `NF` | ~3.01 | Noise figure (dB) |
| `NoiseFactor` | 2 | Noise factor (linear) |
| `SeedSource` | `'auto'` | `'auto'` or `'user'` for RNG seed |
| `Seed` | 67987 | RNG seed (when SeedSource='user') |
| `SampleRate` | 1e6 | Sample rate (Hz) -- only set when `IncludeNoise=true`; emits "not relevant" warning otherwise |

### Visualization

```matlab
amp = rf.Amplifier(Gain=15, OIP3=35);
visualize(amp);   % Plots AM/AM and AM/PM curves
```

### Example: 16-QAM Through Nonlinear Amplifier

```matlab
amp = rf.Amplifier(Gain=15, OIP3=35);

% Generate 16-QAM signal
rng(42);
data = randi([0 15], 1000, 1);
modSig = qammod(data, 16, UnitAveragePower=true);

% Scale to desired input power level
Pin_dBm = -20;
Pin_W = 10^((Pin_dBm - 30) / 10);
Vin = sqrt(2 * 50 * Pin_W);
inSig = Vin * modSig;

% Amplify
outSig = amp(inSig);

% Measure
Pout = 10*log10(mean(abs(outSig).^2 / (2*50))) + 30;
gain = 10*log10(mean(abs(outSig).^2) / mean(abs(inSig).^2));
fprintf('Gain: %.2f dB, Pout: %.2f dBm\n', gain, Pout);

release(amp);
```

## rf.Mixer -- Modulator/Demodulator with Impairments

### Construction

```matlab
mix = rf.Mixer;                                       % All defaults (modulator)
mix = rf.Mixer(Model='demod', Gain=-6, RF=2.4e9, LO=2.1e9);
mix = rf.Mixer(Model='iqmod', Gain=-8);               % No RF or PhaseOffset needed
mix = rf.Mixer(Model='iqdemod', Gain=-6, RF=2.4e9);  % RF relevant; no LO or PhaseOffset
```

### Models

| Model | Description | Input | Output |
|-------|-------------|-------|--------|
| `'mod'` (default) | RF modulator (up-convert) | Real baseband | Complex RF |
| `'demod'` | RF demodulator (down-convert) | Complex RF | Real baseband |
| `'iqmod'` | IQ modulator (up-convert) | Complex baseband (I+jQ) | Complex RF |
| `'iqdemod'` | IQ demodulator (down-convert) | Complex RF | Complex baseband (I+jQ) |

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `Model` | `'mod'` | Mixer type |
| `Sideband` | `'upper'` | `'upper'` or `'lower'` sideband selection |
| `Gain` | 0 | Conversion gain (dB) |
| `RF` | 1e9 | RF carrier frequency (Hz) |
| `LO` | 1e8 | Local oscillator frequency (Hz) |

### Impairments

```matlab
mix = rf.Mixer(Model='iqdemod', Gain=-6, RF=2.4e9, ...
    GainImbalance=0.5, ...     % I/Q gain imbalance (dB)
    PhaseImbalance=2);         % I/Q phase imbalance (degrees)
% Note: LO and PhaseOffset are not relevant for iqmod/iqdemod -- omit them
```

### Nonlinearity

```matlab
mix = rf.Mixer(Model='demod', Gain=-6, RF=2.4e9, LO=2.1e9, ...
    Nonlinearity='IIP3', IIP3=10);
```

Same compression options as rf.Amplifier: IIP3, OIP3, IP1dB, OP1dB, IPsat, OPsat.

### Phase Noise

```matlab
mix = rf.Mixer(Model='demod', Gain=-6, RF=2.4e9, LO=2.1e9, ...
    IncludePhaseNoise=true, ...
    PhaseNoiseLevel=[-80 -100 -120], ...           % dBc/Hz at offsets
    PhaseNoiseFrequencyOffset=[1e3 10e3 100e3], ... % Hz offsets
    SampleRate=10e6);   % SampleRate only relevant when noise/phase-noise enabled
```

### Visualization

```matlab
visualizePower(mix);       % Plot power characteristics
visualizePhaseNoise(mix);  % Plot phase noise spectrum
```

**Gotcha:** For `'iqmod'`, `RF` and `PhaseOffset` are irrelevant (emit "not relevant" warnings). `LO` does not warn and does not affect frequency conversion, but it scales phase noise when `IncludePhaseNoise=true` -- set it to the intended carrier frequency only if modeling phase noise. For `'iqdemod'`, `RF` IS relevant (no warning), but `LO` and `PhaseOffset` are not relevant and emit warnings. This asymmetry is because iqdemod needs the carrier reference for demodulation while iqmod operates purely at baseband (no frequency conversion).

### Example: IQ Demodulation

```matlab
mix = rf.Mixer(Model='iqdemod', Gain=-6, RF=2.4e9, ...
    GainImbalance=0.3, PhaseImbalance=1.5);

% Simulate received RF signal (complex)
t = (0:999)' / 10e6;
rfSig = exp(1j * 2*pi * 5e6 * t);   % 5 MHz tone at carrier

bbOut = mix(rfSig);                   % Complex baseband output with impairments
release(mix);
```

## rf.Filter -- Complex Baseband Filter

### Construction

```matlab
filt = rf.Filter;
filt = rf.Filter(DesignMethod='Butterworth', ResponseType='Bandpass', ...
    PassFreq_bp=[2.395e9 2.405e9], RF=2.4e9, SampleRate=100e6);
```

### Frequency Convention (Critical)

All `PassFreq_*` and `StopFreq_*` properties specify **absolute RF frequencies** (not baseband offsets). The `RF` property defines the carrier center, and the filter internally translates to baseband representation.

```matlab
% CORRECT: 10 MHz channel filter centered at 2.4 GHz
filt = rf.Filter(ResponseType='Bandpass', ...
    PassFreq_bp=[2.395e9 2.405e9], ...   % Absolute: carrier +/- 5 MHz
    RF=2.4e9, SampleRate=100e6);

% WRONG: This creates a filter passing 0-5 MHz absolute (2.4 GHz away from carrier)
filt = rf.Filter(ResponseType='Lowpass', ...
    PassFreq_lp=5e6, RF=2.4e9, SampleRate=100e6);  % Near-zero output!
```

For a lowpass channel filter of bandwidth B around carrier fc, use `ResponseType='Bandpass'` with `PassFreq_bp=[fc-B/2, fc+B/2]` and `RF=fc`.

**Gotcha:** `RF` must be positive -- `RF=0` errors with "Value must be positive."

### UseFilterOrder

By default (`UseFilterOrder=false`), filter order is computed automatically from passband/stopband attenuation specs. When `UseFilterOrder=true`, specify `FilterOrder` directly and `StopFreq_*`/`StopAtten` properties are ignored (warnings emitted if set).

```matlab
% Auto-order from specs (UseFilterOrder=false, the default)
filt = rf.Filter(ResponseType='Bandpass', ...
    PassFreq_bp=[2.395e9 2.405e9], StopFreq_bp=[2.39e9 2.41e9], ...
    StopAtten=40, RF=2.4e9, SampleRate=100e6);

% Fixed order (UseFilterOrder=true) -- StopFreq/StopAtten ignored
filt = rf.Filter(ResponseType='Bandpass', UseFilterOrder=true, FilterOrder=5, ...
    PassFreq_bp=[2.395e9 2.405e9], RF=2.4e9, SampleRate=100e6);
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `DesignMethod` | `'Butterworth'` | `'Butterworth'`, `'Chebyshev'`, `'InverseChebyshev'` |
| `ResponseType` | `'Lowpass'` | `'Lowpass'`, `'Highpass'`, `'Bandpass'`, `'Bandstop'` |
| `UseFilterOrder` | false | If true, specify order directly instead of stopband |
| `FilterOrder` | 3 | Filter order (when UseFilterOrder=true) |
| `PassFreq_lp` | 1e9 | Lowpass passband frequency |
| `PassFreq_bp` | [2e9 3e9] | Bandpass passband frequencies |
| `StopFreq_lp` | 2e9 | Lowpass stopband frequency |
| `StopFreq_bp` | [1.5e9 3.5e9] | Bandpass stopband frequencies |
| `PassAtten` | ~3.01 | Passband attenuation (dB) |
| `StopAtten` | 40 | Stopband attenuation (dB) |
| `RF` | 1e9 | Carrier frequency (Hz) |
| `SampleRate` | 1e6 | Sample rate (Hz) |

**Gotcha:** Passband/stopband frequency properties change name based on `ResponseType`: `PassFreq_lp`, `PassFreq_hp`, `PassFreq_bp`, `PassFreq_bs`. Setting the wrong suffix for the current ResponseType has no effect.

### Visualization

```matlab
visualize(filt);   % Plot filter frequency response
```

## rf.Sparameter -- S-Parameter System Model

Process complex baseband signals through S-parameter data using rational fitting:

### Construction

```matlab
% From Touchstone file (default)
sp = rf.Sparameter(FileName='passive.s2p', CarrierFrequency=2.4e9, SampleRate=10e6);

% From sparameters object
sObj = sparameters('device.s2p');
sp = rf.Sparameter(DataSource='sparameters', SParametersObject=sObj, ...
    CarrierFrequency=2.4e9, SampleRate=10e6);

% From rational fit object
fitObj = rational(sparameters('device.s2p'));
sp = rf.Sparameter(DataSource='rational', RationalObject=fitObj, ...
    CarrierFrequency=2.4e9, SampleRate=10e6);
```

| DataSource | Input Property | Description |
|------------|----------------|-------------|
| `'file'` (default) | `FileName` | 2-port Touchstone file |
| `'sparameters'` | `SParametersObject` | sparameters object |
| `'rational'` | `RationalObject` | rational fit object |

### Visualization

```matlab
visualize(sp);   % Plot S-parameter frequency response
```

## rf.PAmemory -- Power Amplifier with Memory

Model nonlinear power amplifiers with memory effects using Volterra series:

```matlab
pa = rf.PAmemory;
pa = rf.PAmemory(Model='Memory polynomial', CoefficientMatrix=coeffs);
pa = rf.PAmemory(Model='Cross-term memory', CoefficientMatrix=coeffs);
```

| Property | Default | Description |
|----------|---------|-------------|
| `Model` | `'Memory polynomial'` | `'Memory polynomial'` or `'Cross-term memory'` |
| `CoefficientMatrix` | `1+0i` | Complex coefficient matrix |
| `UnitDelay` | 1e-6 | Sample time of measured input-output data (s) |

The coefficient matrix dimensions encode the nonlinear order and memory depth. See the `ComputePACoefficientMatrixExample` for extracting coefficients from measured data.

## rf.MismatchLoss -- Impedance Mismatch

Model frequency-dependent impedance mismatch loss:

```matlab
ml = rf.MismatchLoss;
ml.MismatchLossData = lossValues;           % dB loss values
ml.MismatchLossFrequency = freqPoints;      % Hz
```

Inherits from rf.Sparameter. Typically used in idealized baseband simulation chains to model inter-stage mismatch.

## Common Patterns

### Power Measurement

```matlab
% Complex baseband power into 50 ohm
Pout_W = abs(out).^2 / (2 * 50);
Pout_dBm = 10*log10(mean(Pout_W)) + 30;
```

### EVM Measurement

```matlab
% After amplifier
outNorm = out / mean(abs(out)) * mean(abs(inSig));
evmPct = 100 * rms(outNorm - inSig) / rms(inSig);
```

### Cascading Multiple System Objects

```matlab
fc = 2.4e9;
fs = 100e6;

amp = rf.Amplifier(Gain=15, OIP3=35);
filt = rf.Filter(DesignMethod='Butterworth', ResponseType='Bandpass', ...
    PassFreq_bp=[fc-5e6, fc+5e6], RF=fc, SampleRate=fs);

% Process in series
out1 = amp(inSig);
out2 = filt(out1);
```

When cascading, ensure `SampleRate` is consistent across all objects that use it (rf.Filter, rf.Sparameter, and rf.Amplifier/rf.Mixer when noise is enabled). The `RF` property on rf.Filter must match the carrier frequency of the signal being processed.

For full-system cascaded simulation with automatic Simulink model generation, use `rfsystem` instead (see `matlab-simulate-rf-system` skill).

### Clone for Independent Copies

```matlab
amp1 = rf.Amplifier(Gain=15, OIP3=35);
amp2 = clone(amp1);   % Independent copy
amp2.Gain = 20;       % Does not affect amp1
```

## Relationship to rfbudget Elements

| rf.* System Object | rfbudget Element | Key Difference |
|--------------------|------------------|----------------|
| `rf.Amplifier` | `amplifier` | rf.Amplifier adds modified-rapp, saleh models; processes baseband signals |
| `rf.Mixer` | `modulator` | rf.Mixer adds I/Q imbalance, phase noise; 4 model types |
| `rf.Filter` | `rffilter` | rf.Filter processes time-domain signals; rffilter is for frequency-domain LC synthesis |
| `rf.Sparameter` | `nport` | rf.Sparameter processes baseband signals through S-param data |

The `rf.*` objects process **complex baseband signals** frame-by-frame. The rfbudget elements define **frequency-domain specifications** for cascade analysis. Use `rfsystem` to bridge between them (see `matlab-simulate-rf-system` skill).

## Gotchas

1. **R2024b minimum** -- rf.Amplifier, rf.Mixer, rf.Filter, rf.Sparameter require R2024b+. rf.PAmemory requires R2024a+.
2. **No Simulink required** -- Unlike `rfsystem`, the rf.* objects run entirely in MATLAB.
3. **SampleRate relevance varies by object** -- For `rf.Amplifier`, only set `SampleRate` when `IncludeNoise=true` (emits "not relevant" warning otherwise). For `rf.Mixer`, only when `IncludePhaseNoise=true`. But `rf.Filter` and `rf.Sparameter` **always** require `SampleRate` -- it is a core property for those objects.
4. **rf.Filter frequency properties are ABSOLUTE RF frequencies** -- `PassFreq_bp=[2.395e9 2.405e9]` means the passband is 2.395-2.405 GHz absolute. The `RF` property defines the carrier center for internal baseband conversion. Do NOT use baseband offsets (e.g., `PassFreq_lp=5e6` with `RF=2.4e9` produces near-zero output). For a channel filter of bandwidth B at carrier fc, use `ResponseType='Bandpass'` with `PassFreq_bp=[fc-B/2, fc+B/2]`.
5. **rf.Filter frequency properties are ResponseType-dependent** -- `PassFreq_lp` for lowpass, `PassFreq_bp` for bandpass, etc. Wrong suffix emits "not relevant" warning and is silently ignored (defaults remain).
6. **rf.Filter RF must be positive** -- `RF=0` errors with "Value must be positive."
7. **rf.Filter UseFilterOrder and stopband specs** -- When `UseFilterOrder=true` (or when it defaults to true), `StopFreq_*` and `StopAtten` are "not relevant" and emit warnings. Set `UseFilterOrder=false` explicitly if you need to specify stopband attenuation goals.
8. **`Nonlinearity` is only for `Model='cubic'`** -- For the default `Model='poly'`, do NOT set `Nonlinearity` (it emits "not relevant" warning). Poly uses all compression params you provide (e.g., OIP3, OP1dB, OPsat for amplifiers) to fit the polynomial. For `Model='cubic'`, `Nonlinearity` selects which ONE param shapes the 3rd-order curve. Silent misuse: `rf.Amplifier(Gain=15, Model='cubic', OPsat=30)` without `Nonlinearity='OPsat'` applies no compression (Nonlinearity defaults to OIP3 with OIP3=Inf).
9. **rf.Mixer Model is not the same as modulator ConverterType** -- rf.Mixer uses `'mod'`/`'demod'`/`'iqmod'`/`'iqdemod'`. The rfbudget `modulator` uses `ConverterType='Up'`/`'Down'`.
10. **rf.Mixer IQ model property relevance is asymmetric** -- `'iqmod'`: RF and PhaseOffset are irrelevant (emit warnings). LO does not warn and does not affect frequency conversion, but scales phase noise when `IncludePhaseNoise=true`. `'iqdemod'`: RF is relevant, but LO and PhaseOffset are not. Setting irrelevant properties emits "not relevant" warnings.
11. **Properties locked during use** -- Nontunable properties cannot be changed between step calls. Call `release(obj)` first.
12. **Input must be column vectors or matrices** -- Row vectors error. Each column is an independent channel.
13. **rf.Sparameter default file is unitygain.s2p** -- This is a built-in identity file. Always set `FileName` or `SParametersObject` explicitly.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel signal analysis plots
- Always label axes with units (dBm, MHz, degrees) and include figure titles
- Call `release(obj)` before modifying Nontunable properties
- Use `visualize()` or `visualizePower()`/`visualizePhaseNoise()` to inspect component behavior before simulation

----

Copyright 2026 The MathWorks, Inc.

----
