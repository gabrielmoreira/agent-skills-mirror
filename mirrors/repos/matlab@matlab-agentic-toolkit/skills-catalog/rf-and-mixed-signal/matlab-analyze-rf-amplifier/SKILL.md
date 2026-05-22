---
name: matlab-analyze-rf-amplifier
description: >
  Analyze RF amplifier stability, power gain, and matching using RF Toolbox. Use when evaluating
  unconditional stability, computing Rollett K-factor or Edwards-Sinsky mu, calculating maximum
  available gain (Gmag), maximum stable gain (Gmsg), transducer gain, available gain, operating
  power gain, input/output reflection coefficients, or simultaneous conjugate match conditions.
  Also covers passivity and causality validation. Trigger on stability factor, stabilityk,
  stabilitymu, power gain, powergain, Gmag, Gmsg, gammain, gammaout, gammams, gammaml,
  unconditionally stable, amplifier analysis, ispassive, makepassive, iscausal, passivity,
  causality, active device.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.1"
---

# RF Amplifier Analysis

Evaluate stability, power gain, matching, and quality of active RF devices using S-parameter data.

## When to Use

- Evaluating unconditional stability via Rollett K-factor or Edwards-Sinsky mu
- Computing maximum available gain (Gmag), maximum stable gain (Gmsg), or transducer gain
- Computing input/output reflection coefficients for matching design
- Checking passivity and causality of S-parameter data
- Simultaneous conjugate match analysis with gammams/gammaml

## When NOT to Use

- Loading or plotting S-parameter data -- use `matlab-manage-sparameters`
- Fitting rational models or computing TDR -- use `matlab-fit-rational-model`
- Designing impedance matching networks -- use `matlab-design-matching-network`
- Defining amplifier elements for rfbudget -- use `matlab-create-rfbudget-elements`

## Workflow

1. **Load device data** — Load amplifier S-parameters (see `matlab-manage-sparameters` skill)
2. **Check passivity/causality** — Confirm data quality; active devices are expected to be non-passive
3. **Evaluate stability** — Compute K-factor and/or mu across frequency
4. **Compute gain** — Select appropriate gain metric based on stability and application
5. **Analyze matching** — Compute reflection coefficients for impedance matching design

## Passivity and Causality

### Passivity

A passive network cannot produce energy. Active devices (amplifiers) are expected to fail passivity — that is normal.

```matlab
[isPass, idxNonPass] = ispassive(s);
if ~isPass
    fprintf('Non-passive at %d of %d frequencies\n', numel(idxNonPass), numel(s.Frequencies));
    sFixed = makepassive(s);            % Enforce passivity
end
```

**Gotcha:** `makepassive(sparametersObj)` directly modifies S-parameter data point-by-point to force passivity — it does not optimize. This is different from `makepassive(fitObj)` on a rational fit, which performs an optimization over the fit residues (see `matlab-fit-rational-model` skill). Only use `makepassive` on S-parameter data for small numerical violations (e.g., measurement noise on passive devices). It is NOT appropriate for active devices — the result will not represent the original network.

### Causality

```matlab
if iscausal(s)
    disp('S-parameters are causal');
end
```

## Stability Analysis

### Rollett Stability Factor (K)

The classic two-condition test for unconditional stability:

```matlab
[k, b1, b2, delta] = stabilityk(s);
% Unconditionally stable when K > 1 AND |delta| < 1
isUnconditional = (k > 1) & (abs(delta) < 1);

fprintf('K range: %.3f to %.3f\n', min(k), max(k));
fprintf('Unconditionally stable at %d of %d frequencies\n', ...
    sum(isUnconditional), numel(k));
```

**Output meanings:**
- `k` — Rollett stability factor (unconditionally stable when K > 1)
- `b1` — Auxiliary stability measure: `1 - |S11|^2 - |S22|^2 + |delta|^2`. Sign of `b1` indicates which stability circle (source or load) contains the Smith chart center. Positive `b1` means the stable region for the source includes the center.
- `b2` — Same as `b1` but for the load plane: `1 - |S22|^2 - |S11|^2 + |delta|^2` (symmetric formula)
- `delta` — Determinant of the S-matrix: `S11*S22 - S12*S21`. Unconditional stability requires `|delta| < 1` in addition to K > 1.

### Edwards-Sinsky Stability Factor (mu)

Single-condition test — preferred because one parameter suffices:

```matlab
mu = stabilitymu(s);
% Unconditionally stable when mu > 1

figure;
plot(s.Frequencies/1e9, mu, 'LineWidth', 1.5);
yline(1, 'r--', 'Stability Boundary');
xlabel('Frequency (GHz)'); ylabel('\mu');
title('Edwards-Sinsky Stability Factor'); grid on;
```

## Power Gain

### Gain Metrics

| Function Call | Metric | Description |
|--------------|--------|-------------|
| `powergain(s, 'Gmag')` | Maximum available gain | Valid only when unconditionally stable (K > 1) |
| `powergain(s, 'Gmsg')` | Maximum stable gain | Use when conditionally stable (K < 1) |
| `powergain(s, Zs, Zl, 'Gt')` | Transducer gain | Actual gain with specific source/load impedances |
| `powergain(s, Zs, 'Ga')` | Available gain | With specific source impedance |
| `powergain(s, Zl, 'Gp')` | Operating power gain | With specific load impedance |

**Gotcha:** The gain type string must be the **last** argument. `powergain(s, 'Gt', 50, 50)` errors — use `powergain(s, 50, 50, 'Gt')` instead.

```matlab
gmag = powergain(s, 'Gmag');           % Maximum available gain
gmsg = powergain(s, 'Gmsg');           % Maximum stable gain

gt = powergain(s, 50, 75, 'Gt');       % Transducer gain (Zs=50, Zl=75)
ga = powergain(s, 50, 'Ga');           % Available gain (Zs=50)
gp = powergain(s, 75, 'Gp');           % Operating power gain (Zl=75)
```

**Gotcha:** `powergain` returns linear gain, NOT dB. Convert with `10*log10(g)` (power gain uses 10×, not 20×).

**Gotcha:** `Gmag` returns `NaN` at frequencies where the device is conditionally stable (K < 1). Use `Gmsg` at those frequencies.

**Gotcha:** `Gmsg` returns `Inf` when S12 approaches zero (unilateral device). Guard with `isfinite(gmsg)` before converting to dB.

### Combined Gain Plot Pattern

```matlab
gmag = powergain(s, 'Gmag');
gmsg = powergain(s, 'Gmsg');

figure;
plot(s.Frequencies/1e9, 10*log10(gmag), ...
     s.Frequencies/1e9, 10*log10(gmsg), '--', 'LineWidth', 1.5);
xlabel('Frequency (GHz)'); ylabel('Gain (dB)');
title('Maximum Available / Stable Gain');
legend('Gmag', 'Gmsg'); grid on;
```

## Reflection Coefficients

For impedance matching design — compute the reflection coefficients needed for simultaneous conjugate match or for given termination impedances.

```matlab
gin  = gammain(s, zl);                 % Input reflection coefficient (given load Zl)
gout = gammaout(s, zs);                % Output reflection coefficient (given source Zs)
gms  = gammams(s);                     % Source match for simultaneous conjugate match
gml  = gammaml(s);                     % Load match for simultaneous conjugate match
```

### Converting Gamma to Impedance

To convert a reflection coefficient to impedance (e.g., for matching network targets):

```matlab
Z0 = 50;
Zs = Z0 * (1 + gms) ./ (1 - gms);    % Source impedance for conjugate match
Zl = Z0 * (1 + gml) ./ (1 - gml);    % Load impedance for conjugate match
```

### Frequency Interpolation

If the desired analysis frequency is not in the S-parameter data, interpolate first:

```matlab
sInterp = rfinterp1(s, targetFreq);   % Interpolate to specific frequency
gms_f0 = gammams(sInterp);            % Now compute at exact frequency
```

See `matlab-manage-sparameters` for full `rfinterp1` usage.

### Circuit Implementation of Matching Networks

After computing `gammams`/`gammaml`, translate to matching network circuits using `matlab-design-matching-network` (for lumped/stub synthesis) or `matlab-compose-rf-circuit` (for assembling `txlineMicrostrip` stubs with `nport` amplifier blocks). Key points for circuit assembly:

- Use `matlab-compose-rf-circuit` for the `nport` + transmission line + `setports` workflow
- Call `setports` only once per circuit, after all elements are `add()`ed and wired
- If combining sub-circuits (e.g., input match + amplifier + output match), build each as a separate `circuit` object, then compose them in a parent circuit using `setterminals`

## Noise Parameters

The `noiseParameters` object stores noise data (minimum noise figure, optimum reflection coefficient, equivalent noise resistance) that accompanies amplifier S-parameter data.

### Constructor

```matlab
np = noiseParameters(fmin, freq, z0);
% fmin: minimum noise figure (linear, not dB) at each frequency
% freq: frequency vector in Hz
% z0: reference impedance for Rn normalization
```

### Rn Normalization Convention

The `Rn` property (equivalent noise resistance) is **normalized to z0**:

```matlab
% If measured Rn data is in ohms (absolute):
np = noiseParameters(fmin, freq, 1);   % z0=1: Rn values ARE resistance in ohms
np.Rn = measuredRn_ohms;

% If Rn data is normalized to 50 ohm:
np = noiseParameters(fmin, freq, 50);  % z0=50: Rn = Rn_actual/50
np.Rn = measuredRn_normalized;
```

Many datasheets give Rn in ohms, so `z0=1` is more intuitive for direct entry.

**Gotcha:** `z0` only affects `Rn` normalization — it does NOT affect `Fmin` or `GammaOpt`. Do not confuse noise reference impedance with S-parameter reference impedance.

## Gotchas

1. **`powergain` gain type string must be the last argument** -- `powergain(s, 'Gt', 50, 50)` errors. Use `powergain(s, 50, 50, 'Gt')`.
2. **`powergain` returns linear gain, not dB** -- Convert with `10*log10(g)` (power gain uses 10x, not 20x).
3. **`Gmag` returns `NaN` when conditionally stable** -- At frequencies where K < 1, `Gmag` is undefined. Use `Gmsg` at those frequencies instead.
4. **`Gmsg` returns `Inf` for unilateral devices** -- When S12 approaches zero, `Gmsg` blows up. Guard with `isfinite(gmsg)` before converting to dB.
5. **Do not apply `makepassive` to amplifiers** -- Active devices are expected to be non-passive. `makepassive(sparametersObj)` modifies data point-by-point and does NOT represent the original active device.
6. **`makepassive` on S-parameters vs rational fits** -- `makepassive(sparametersObj)` is a crude point-by-point fix. `makepassive(fitObj)` on a rational fit runs an optimization over residues (see `matlab-fit-rational-model` skill). Only use on S-parameter data for small numerical violations on passive devices.
7. **`setports` can only be called once per circuit** -- If you get "terminals already set", you are calling `setports` on a circuit that already has ports defined. Build all elements and wiring first, then call `setports` once at the end. See `matlab-compose-rf-circuit` for the full circuit assembly workflow.
8. **`gammams`/`gammaml` return complex values** -- Convert to impedance with `Z = Z0*(1+gamma)./(1-gamma)`. Convert to magnitude/angle with `abs(gamma)` and `angle(gamma)*180/pi`.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel stability/gain figures
- Always label axes with units (GHz, dB) and include figure titles
- Plot a `yline(1, 'r--')` stability boundary on mu plots for visual clarity
- Active devices are expected to be non-passive — do not apply `makepassive` to amplifiers

----

Copyright 2026 The MathWorks, Inc.

----
