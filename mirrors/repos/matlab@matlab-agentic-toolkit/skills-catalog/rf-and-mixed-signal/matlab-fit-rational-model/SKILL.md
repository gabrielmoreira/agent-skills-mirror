---
name: matlab-fit-rational-model
description: >
  Fit S-parameters to rational function models and compute time-domain responses using RF Toolbox.
  Use when performing vector fitting, building broadband circuit models, computing TDR (time-domain
  reflectometry), impulse or step responses from S-parameter data, exporting to SPICE or Verilog-A,
  or analyzing signal integrity. Trigger on rational, rationalfit, vector fitting, TDR, time-domain
  reflectometry, impulse response, step response, stepresp, timeresp, pwlresp, freqresp,
  generateSPICE, writeva, signal integrity, broadband model, rational fit.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# Rational Fitting and Time-Domain Analysis

Fit S-parameter data to rational function models using the `rational` object, then compute time-domain responses (TDR, impulse, step) and export to SPICE/Verilog-A.

## When to Use

- Fitting S-parameter data to rational function models (vector fitting, AAA)
- Computing time-domain responses: TDR, impulse, step, arbitrary waveform
- Exporting broadband circuit models to SPICE or Verilog-A
- Verifying fit accuracy in frequency domain with `freqresp`
- Enforcing causality or passivity on fitted models
- Extracting poles, zeros, and state-space matrices from fits

## When NOT to Use

- Loading or plotting S-parameter data -- use `matlab-manage-sparameters`
- Converting between network parameter types -- use `matlab-convert-network-parameters`
- RF budget or cascade analysis -- use `matlab-analyze-rf-budget` or `matlab-deembed-rf-cascade`

## Workflow

1. **Load S-parameters** — See `matlab-manage-sparameters` skill
2. **Fit** — Create a `rational` model from the S-parameter data
3. **Verify** — Compare fit against original data in frequency domain
4. **Analyze** — Compute time-domain responses (TDR, impulse, step)
5. **Export** — Generate SPICE subcircuit or Verilog-A model

## The `rational` Object (R2020a+)

Prefer the `rational` object (AAA algorithm) over `rationalfit` (vector-fitting algorithm). Both provide the same analysis methods (`impulse`, `stepresp`, `timeresp`, `zpk`, `generateSPICE`, `pwlresp`, `iscausal`, `ispassive`, `makepassive`, `passivity`, `freqresp`, `abcd`, `writeva`). The advantage of `rational` is that it tends to converge more robustly. The advantage of `rationalfit` is that it enables delay removal.

**Note:** `rationalfit` still ships and uses the vector-fitting algorithm. It returns the legacy `rfmodel.rational` object. Use `rational` (without the "fit" suffix) for new code unless you specifically need vector fitting.

### Fitting S-Parameters

```matlab
% Fit entire S-parameter object (all ports)
[fit, errdb] = rational(s);
fprintf('Ports: %d, Poles: %d, Error: %.1f dB\n', fit.NumPorts, fit.NumPoles, errdb);

% Fit a single parameter from (freq, data)
s21 = rfparam(s, 2, 1);
[fit21, err21] = rational(s.Frequencies, s21);
```

### Tuning the Fit

```matlab
[fit, errdb] = rational(s, ...
    'Tolerance', -50, ...              % Target accuracy in dB
    'MaxPoles', 30);                   % Limit pole count
```

| Option | Default | Purpose |
|--------|---------|---------|
| `Tolerance` | -40 | Target error in dB |
| `MaxPoles` | 1000 | Upper bound on poles |
| `Causal` | true | Enforce causal (stable) poles |
| `TendsToZero` | true | Force fit to decay to zero as frequency → ∞ |
| `NoiseFloor` | -Inf | Ignore data below this level (dB) |
| `Display` | `'off'` | Set to `'plot'` to visualize fit progress |

**`TendsToZero`:** When `true` (default), the rational model has strictly proper form (numerator order < denominator order), so the response decays to zero at high frequencies. This is appropriate for bandpass or lowpass responses (e.g., insertion loss S21 of a lossy channel). Set `TendsToZero=false` for responses that do not vanish at infinity (e.g., reflection coefficients, allpass networks, or broadband matched loads where S11 plateaus). The `false` setting produces a more general model with a nonzero direct-feedthrough term (D ≠ 0).

## Verify the Fit

```matlab
% Frequency response of the fit
resp = freqresp(fit, s.Frequencies);   % Returns N×N×K for N-port fit

% For multi-port fit, extract S21 element
figure;
plot(s.Frequencies/1e9, 20*log10(abs(rfparam(s, 2, 1))), ...
     s.Frequencies/1e9, 20*log10(abs(squeeze(resp(2,1,:)))), '--');
xlabel('Frequency (GHz)'); ylabel('Magnitude (dB)');
legend('Original', 'Rational Fit'); title('S21 Fit Verification');
```

### Extract Poles, Zeros, and State-Space

```matlab
% Direct property access (preferred)
poles = fit.Poles;                     % Pole vector
nPoles = fit.NumPoles;                 % Number of poles

% zpk form
[z, p, k] = zpk(fit);                 % Zeros, poles, gain
[A, B, C, D] = abcd(fit);             % State-space matrices
```

**Gotcha:** Use `fit.NumPoles` and `fit.Poles` for direct access. The `zpk(fit)` form returns a struct with cell arrays (`.Z`, `.P`, `.K`), which requires indexing like `z.P{1}` — the direct properties are simpler.

### Causality and Passivity Enforcement

```matlab
% Step 1: Fit with causal poles enforced (default Causal=true)
fit = rational(s, Causal=true);

% Step 2: Verify causality and passivity
iscausal(fit)                          % logical: true if all poles in left half-plane
ispassive(fit)                         % logical: true if passive at all frequencies

% For numeric quality metrics per IEEE P370 (R2023b+), use on sparameters:
% [cm, rm, pm] = ieee370QualityCheckFrequencyDomain(s)

% Step 3: Visualize passivity across frequency
figure;
passivity(fit);                        % Plots H-infinity norm vs frequency
                                       % Passive where norm <= 1

% Step 4: Enforce passivity if needed
if ~ispassive(fit)
    fit = makepassive(fit);            % Perturbs residues to enforce passivity
    passivity(fit);                    % Re-plot to confirm
end
```

**`Causal=true`** (the default) constrains all poles to the left half-plane during fitting, ensuring a stable/causal model. Set `Causal=false` only when fitting active devices or when stability is not required.

**`passivity(fit)`** plots the 2-norm of the transfer function vs frequency — the fit is passive wherever the norm is at or below 1. With output arguments, `pNorm = passivity(fit)` returns the scalar maximum passivity norm. Call without arguments for reliable results — `passivity(fit, freqVector)` with a custom frequency vector is not supported in all releases.

**`makepassive(fitObj)`** enforces passivity by running an optimization that perturbs the fit residues. This is different from `makepassive(sparametersObj)` on raw S-parameter data, which simply modifies data point-by-point without optimization (see `matlab-analyze-rf-amplifier` skill). Be aware:
- It can be slow for high-order fits (many poles) or large multi-port networks
- It may decrease fit accuracy because it modifies residues to satisfy passivity constraints — verify the fit error after calling it
- Passivity enforcement is important for SPICE export and time-domain simulation to avoid non-physical energy generation

## Time-Domain Reflectometry (TDR)

Compute TDR from S11 by fitting the voltage reflection response and computing the step response.

```matlab
s11 = rfparam(s, 1, 1);
tdrFreqData = (s11 + 1) / 2;           % Voltage TDR response in frequency domain
tdrFit = rational(s.Frequencies, tdrFreqData);

[tdr, tOut] = stepresp(tdrFit, 1e-11, 10000, 1e-10);  % (fit, ts, nPts, tRise)
figure;
plot(tOut*1e9, real(tdr));
xlabel('Time (ns)'); ylabel('TDR Impedance (normalized)');
title('Time-Domain Reflectometry');
```

**Note:** The Signal Integrity Toolbox provides a more advanced `tdr` function (built on RF Toolbox infrastructure) with additional features for signal integrity analysis. The rational-fit approach above works with RF Toolbox alone.

## Time-Domain Responses

### Impulse Response

```matlab
[yImp, tImp] = impulse(fit21, 1e-12, 5000);   % (fit, ts, nPts)
```

### Step Response

```matlab
[yStep, tStep] = stepresp(fit21, 1e-11, 10000, 1e-10);  % (fit, Ts_seconds, N_samples, tRise)
```

### Arbitrary Waveform via `timeresp`

```matlab
u = zeros(1, 5001); u(1) = 1/1e-12;   % Impulse input
[yTime, tTime] = timeresp(fit21, u, 1e-12);
```

**Gotcha:** For multi-port fits, `stepresp`, `impulse`, and `timeresp` return `{N,N}` cell arrays for **both** the response and the time vector. Access element (i,j) as `resp{i,j}` and `t{i,j}` — do not index `t` as a plain vector.

### Piece-Wise Linear Transient (`pwlresp`)

For periodic or arbitrary piece-wise linear excitation:

```matlab
tfData = s2tf(s);
fitTF = rational(s.Frequencies, tfData);
sigTime = [0, 0.1, 0.6, 0.7]*1e-9;    % Waveform breakpoints
sigValue = [0, 5, 5, 0];               % Values at breakpoints
tPer = 1.5e-9;                         % Period
tSim = 0:2e-11:3*tPer;
[tran, tPwl] = pwlresp(fitTF, sigTime, sigValue, tSim, tPer);
```

## SPICE and Verilog-A Export

```matlab
generateSPICE(fit, 'model.sp');        % Export to SPICE subcircuit
writeva(fit, 'model.va', 'in', 'out', 'electrical');  % Verilog-A
```

## Gotchas

1. **`rational` vs `rationalfit`** -- Both provide the same methods. `rational` (AAA) converges more robustly. `rationalfit` (vector fitting) enables delay removal. Both return objects with `impulse`, `stepresp`, `iscausal`, `ispassive`, `makepassive`, `generateSPICE`, `zpk`, `abcd`, etc.
2. **Multi-port time-domain responses return cell arrays** -- `stepresp`, `impulse`, and `timeresp` return `{N,N}` cell arrays for BOTH the response and the time vector. Access as `resp{i,j}` and `t{i,j}`, not as plain vectors.
3. **Use `fit.NumPoles` and `fit.Poles` for direct access** -- The `zpk(fit)` form returns a struct with cell arrays (`.Z`, `.P`, `.K`), requiring indexing like `z.P{1}`. Direct properties are simpler.
4. **`makepassive(fitObj)` can be slow and reduce accuracy** -- It optimizes residues to enforce passivity, which may decrease fit accuracy. Always verify fit error after calling it.
5. **`passivity(fit, freqVector)` not universally supported** -- Call `passivity(fit)` without arguments for reliable results across releases.
6. **`makepassive` on fit vs S-parameters** -- `makepassive(fitObj)` runs an optimization over residues. `makepassive(sparametersObj)` modifies data point-by-point without optimization (see `matlab-analyze-rf-amplifier` skill). The fit version is more sophisticated but slower.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel fit verification figures
- Always label axes with units (GHz, dB, ns) and include figure titles
- Plot original and fit data together for visual verification
- Prefer `rational` (AAA algorithm) over `rationalfit` (vector fitting) for new code

----

Copyright 2026 The MathWorks, Inc.

----
