---
name: matlab-design-antenna-matching-network
description: Design impedance matching networks for antennas using MATLAB RF Toolbox matchingnetwork object. Synthesizes L/C topologies (L, Pi, Tee, 2-element, 3-element), ranks designs by return loss or gain, exports to circuit objects, and converts to distributed elements via Richards transformation. Supports antenna objects, sparameters, Touchstone files, and function handles as load impedance. Use when the user wants to match an antenna, design a matching network, improve return loss, or transform impedance.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-or-load> <frequency> [topology]
metadata:
  author: MathWorks
  version: "1.0"
---

# Matching Network Design Skill

You are an expert RF and antenna engineer assisting a professional with impedance matching network design. Use MATLAB RF Toolbox `matchingnetwork` to synthesize, evaluate, and export L/C matching networks for antennas and RF loads.

## Core Concept

`matchingnetwork` synthesizes lumped L/C networks that transform a complex load impedance to a source impedance (default 50 ohm). It generates multiple candidate topologies, ranks them by performance goals (return loss, transducer gain), and exports the best designs as RF Toolbox `circuit` objects.

## When to Use

- User wants to match an antenna to a target impedance (typically 50 ohm)
- User asks about improving return loss or VSWR
- User wants to design an L, Pi, or Tee matching network
- User wants to transform impedance between stages
- User asks about distributed element matching (microstrip stubs)

## When NOT to Use

- User wants to design the antenna itself — use `matlab-design-antenna`
- User wants a PCB antenna with integrated matching — use `matlab-designing-pcb-antennas`
- User wants S-parameter analysis without matching — use `matlab-design-antenna`

## Core Workflow

1. **Parse the request** -- Identify the load (antenna, impedance, file), frequency, bandwidth, topology preference, and performance goals.
2. **Create the matchingnetwork** -- Set `CenterFrequency` FIRST, then `LoadImpedance`, `Bandwidth`, `Components`.
3. **Add evaluation parameters** -- Rank/filter designs by `gammain` or `Gt` over a frequency band.
4. **Inspect results** -- `circuitDescriptions` returns a table of all candidate circuits with component values.
5. **Visualize** -- `rfplot` (S11/gain vs frequency), `smithplot` (impedance transformation).
6. **Export** -- `exportCircuits` produces RF Toolbox `circuit` objects for further analysis.

## Key Properties

| Property | Default | Description |
|----------|---------|-------------|
| `SourceImpedance` | 50 | Source impedance (real scalar, ohms) |
| `LoadImpedance` | 100 | Load: scalar, antenna, sparameters, file, or function handle |
| `CenterFrequency` | 1e9 | Design center frequency (Hz) |
| `Bandwidth` | `CenterFrequency/20` | Design bandwidth (Hz) |
| `Components` | 2 | Topology: 2, 3, `"L"`, `"Pi"`, `"Tee"` |
| `LoadedQ` | Inf | Component quality factor (finite for realistic losses) |

**Critical constraint:** Set `CenterFrequency` BEFORE `LoadImpedance` when the load is a frequency-dependent object (antenna, sparameters, file). MATLAB errors if it cannot evaluate the load at the current center frequency.

## Load Impedance Options

| Type | Example | Notes |
|------|---------|-------|
| Complex scalar | `25 + 1j*30` | Frequency-independent |
| Antenna object | `design(pifa, freq)` | Evaluated at CenterFrequency |
| sparameters | `sparameters(ant, freqRange)` | 1-port S-params |
| Touchstone file | `"antenna.s1p"` | .s1p or .s2p file path |
| Function handle | `@(f) 36 + 1j*21*(f/2.4e9-1)` | Z(f) in ohms |

## Topology Selection

| Components | Topologies Generated | Use Case |
|------------|---------------------|----------|
| 2 | All 2-element L-sections | Narrowband, simplest |
| 3 | All 3-element networks | Wider bandwidth |
| `"L"` | L-section variants only | Equivalent to 2 |
| `"Pi"` | Pi (shunt-series-shunt) | Low-pass or band-pass |
| `"Tee"` | Tee (series-shunt-series) | High-impedance loads |

## Workflow 1: Antenna Impedance Matching

Match an antenna to 50 ohm with automatic topology selection:

```matlab
freq = 2.4e9;
ant = design(pifa, freq);

mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 200e6;
mn.LoadImpedance = ant;
mn.Components = 2;

% Add performance goal: S11 < -15 dB in band
addEvaluationParameter(mn, 'gammain', '<', -15, [2.3e9 2.5e9], 1);

% View ranked circuits
cd = circuitDescriptions(mn);
disp(cd)

% Visualize matched performance
figure; rfplot(mn);
figure; smithplot(mn);

% Report best design
fprintf("Best: %s = %.3g F, %s = %.3g H\n", ...
    cd.component1Type(1), cd.component1Value(1), ...
    cd.component2Type(1), cd.component2Value(1));
```

### Before/After Comparison

```matlab
freqRange = linspace(2e9, 3e9, 101);
sAnt = sparameters(ant, freqRange);
sMN = sparameters(mn, freqRange);
S = sMN.Parameters;
gammaL = squeeze(sAnt.Parameters(1,1,:));
gammain = squeeze(S(1,1,:)) + squeeze(S(1,2,:)).*squeeze(S(2,1,:)).*gammaL ./ ...
    (1 - squeeze(S(2,2,:)).*gammaL);

figure;
plot(freqRange/1e9, 20*log10(abs(gammaL)), ...
     freqRange/1e9, 20*log10(abs(gammain)));
xlabel("Frequency (GHz)"); ylabel("S_{11} (dB)");
legend("Before", "After"); grid on;
title("Impedance Matching Improvement");
```

## Workflow 2: Topology Comparison

```matlab
freq = 5.8e9;
Zload = 15 + 1j*40;

topologies = {2, 3, "Pi", "Tee"};
for k = 1:numel(topologies)
    mn = matchingnetwork;
    mn.CenterFrequency = freq;
    mn.Bandwidth = 500e6;
    mn.LoadImpedance = Zload;
    mn.Components = topologies{k};
    addEvaluationParameter(mn, 'gammain', '<', -15, [5.5e9 6.1e9], 1);
    cd = circuitDescriptions(mn);
    fprintf("Components=%s: %d candidates\n", string(topologies{k}), height(cd));
end
```

### Three-Element for Wider Bandwidth

```matlab
freq = 2.4e9;
mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 400e6;
mn.LoadImpedance = design(pifa, freq);
mn.Components = 3;
addEvaluationParameter(mn, 'gammain', '<', -10, [2.2e9 2.6e9], 1);

figure; rfplot(mn);
cd = circuitDescriptions(mn);
disp(cd(1,:))
```

## Workflow 3: Evaluation Parameters (Ranking & Filtering)

```matlab
mn = matchingnetwork;
mn.CenterFrequency = 2.4e9;
mn.Bandwidth = 200e6;
mn.LoadImpedance = design(dipole, 2.4e9);
mn.Components = 2;

% Goal 1: Return loss < -15 dB in passband (weight 2)
addEvaluationParameter(mn, 'gammain', '<', -15, [2.3e9 2.5e9], 2);

% Goal 2: Transducer gain > -1 dB (weight 1)
addEvaluationParameter(mn, 'Gt', '>', -1, [2.3e9 2.5e9], 1);

% View all active parameters
ep = getEvaluationParameters(mn);
disp(ep)

% Remove a specific evaluation parameter (by index in table)
clearEvaluationParameter(mn, 2);
```

**Parameters:**
- `'gammain'`: Input reflection coefficient (dB). Use `'<'` with negative target.
- `'Gt'`: Transducer power gain (dB). Use `'>'` with target near 0 dB.
- `band`: Frequency range `[fLow fHigh]` in Hz.
- `weight`: Higher weight = more influence on ranking.

## Workflow 4: Export and Circuit Analysis

Export the best matching network as an RF Toolbox `circuit` object:

```matlab
freq = 2.4e9;
mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 200e6;
mn.LoadImpedance = design(pifa, freq);
mn.Components = 2;

% Export best circuit (index 1)
ckt = exportCircuits(mn, 1);
disp(ckt)

% Export specific circuits by index
ckt2 = exportCircuits(mn, 2);

% S-parameters of the matching network (2-port)
freqRange = linspace(2e9, 3e9, 101);
sCkt = sparameters(ckt, freqRange);
figure; rfplot(sCkt);
```

### S-Parameters of Matching Network

`sparameters(mn, freq)` returns the 2-port S-parameters of the best matching network circuit (without load):

```matlab
sMN = sparameters(mn, freqRange);
fprintf("Matching network: %d-port\n", sMN.NumPorts);

% For specific circuit indices
sMN_all = sparameters(mn, freqRange, 50, [1 2]);  % returns array
```

## Workflow 5: Touchstone File Interop

Export antenna S-parameters to Touchstone, then use the file as load:

```matlab
freq = 2.4e9;
ant = design(monopole, freq);
freqRange = linspace(2e9, 3e9, 51);

% Export antenna to Touchstone
sAnt = sparameters(ant, freqRange);
rfwrite(sAnt, "monopole_2p4GHz.s1p");

% Use Touchstone file as load
mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 200e6;
mn.LoadImpedance = "monopole_2p4GHz.s1p";
mn.Components = 2;

cd = circuitDescriptions(mn);
disp(cd(1,:))
figure; rfplot(mn);
```

## Workflow 6: Richards Transformation (Lumped to Distributed)

Convert lumped L/C matching network to transmission-line-based circuit for PCB/microstrip realization:

```matlab
freq = 2.4e9;
mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 200e6;
mn.LoadImpedance = 25 + 1j*30;
mn.Components = 3;

% Convert best circuit to transmission lines
txCkt = richards(mn, freq);
disp(txCkt)

% Convert specific circuits
txCkts = richards(mn, freq, [1 2 3]);

% Analyze distributed circuit
freqRange = linspace(1e9, 4e9, 201);
sTx = sparameters(txCkts(1), freqRange);
figure; rfplot(sTx);
```

The output circuit uses `txlineElectricalLength` elements -- quarter-wave stubs replacing inductors and capacitors.

## Workflow 7: Custom Network Topology

Add your own circuit topology to the candidate pool:

```matlab
mn = matchingnetwork;
mn.CenterFrequency = 2.4e9;
mn.LoadImpedance = 25 + 1j*30;

% Build custom 2-port matching circuit
c1 = circuit("my_match");
add(c1, [1 2], inductor(2e-9));
add(c1, [2 0], capacitor(1e-12));
setports(c1, [1 0], [2 0]);

% Disable automatic generation, add only custom
disableAutomaticNetworks(mn);
addNetwork(mn, c1);

% Or keep automatic + add custom
mn2 = matchingnetwork;
mn2.CenterFrequency = 2.4e9;
mn2.LoadImpedance = 25 + 1j*30;
addNetwork(mn2, c1);  % added alongside auto-generated

cd = circuitDescriptions(mn2);
disp(cd)
```

## Workflow 8: Realistic Components (Lossy Q)

Set finite component Q to model real-world losses:

```matlab
freq = 2.4e9;
mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 200e6;
mn.LoadImpedance = design(pifa, freq);
mn.Components = 2;
mn.LoadedQ = 50;  % typical SMD inductor Q at 2.4 GHz

addEvaluationParameter(mn, 'gammain', '<', -10, [2.3e9 2.5e9], 1);
cd = circuitDescriptions(mn);
disp(cd(1,:))
figure; rfplot(mn);
```

Lower `LoadedQ` values model lossier components and reduce achievable bandwidth.

## Workflow 9: Non-50-Ohm Source

Match between arbitrary source and load impedances:

```matlab
freq = 900e6;
mn = matchingnetwork;
mn.SourceImpedance = 75;       % 75-ohm system
mn.CenterFrequency = freq;
mn.Bandwidth = 50e6;
mn.LoadImpedance = 150 + 1j*20;
mn.Components = 2;

cd = circuitDescriptions(mn);
disp(cd(1,:))
figure; rfplot(mn);
```

## Workflow 10: Function Handle Load (Frequency-Dependent)

Model loads with known analytical impedance behavior:

```matlab
freq = 1e9;
% Series RLC: Z(f) = R + j*(wL - 1/(wC))
R = 30; L = 5e-9; C = 2e-12;
Zfunc = @(f) R + 1j*(2*pi*f*L - 1./(2*pi*f*C));

mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = 100e6;
mn.LoadImpedance = Zfunc;
mn.Components = 2;

fprintf("Load at center: %.1f + j%.1f ohm\n", real(Zfunc(freq)), imag(Zfunc(freq)));
cd = circuitDescriptions(mn);
disp(cd(1,:))
```

## Workflow 11: Multi-Band Matching

Design a matching network covering two separate frequency bands (e.g., dual-band Wi-Fi):

```matlab
ant = design(pifa, 2.4e9);

% Use 3-element network for multi-band capability
mn = matchingnetwork;
mn.CenterFrequency = 3.5e9;
mn.Bandwidth = 3e9;
mn.LoadImpedance = sparameters(ant, linspace(2e9, 6e9, 101));
mn.Components = 3;

% Band 1: 2.4 GHz Wi-Fi (higher weight — primary band)
addEvaluationParameter(mn, 'gammain', '<', -10, [2.4e9 2.5e9], 2);

% Band 2: 5 GHz Wi-Fi (lower weight — secondary band)
addEvaluationParameter(mn, 'gammain', '<', -10, [5.15e9 5.85e9], 1);

cd = circuitDescriptions(mn);
disp(cd)

figure; rfplot(mn);
figure; smithplot(mn);
```

Set `CenterFrequency` between the two bands with `Bandwidth` wide enough to span both. Weight the primary band higher.

## Workflow 12: Off-Resonance / Offset Frequency Matching

When an antenna is designed at one frequency but must operate at another:

```matlab
designFreq = 3e9;
operatingFreq = 2.4e9;
bw = 200e6;

ant = design(patchMicrostrip, designFreq);
sAntLoad = sparameters(ant, linspace(operatingFreq - bw, operatingFreq + bw, 51));

% Match at operating frequency, not design frequency
mn = matchingnetwork;
mn.CenterFrequency = operatingFreq;
mn.Bandwidth = bw;
mn.LoadImpedance = sAntLoad;
mn.Components = 2;

addEvaluationParameter(mn, 'gammain', '<', -15, [operatingFreq-bw/2 operatingFreq+bw/2], 1);
cd = circuitDescriptions(mn);
disp(cd)

Zant = impedance(ant, operatingFreq);
fprintf("Antenna impedance at %.2f GHz: %.2f %+.2fj ohm\n", ...
    operatingFreq/1e9, real(Zant), imag(Zant));
figure; rfplot(mn);
```

Off-resonance antennas have large reactive impedance. Use `Components = 3` if the mismatch is severe.

## Workflow 13: Pre-computed S-Parameters as Load (Speed)

Using an antenna object directly as `LoadImpedance` causes repeated EM solves. Pre-compute once:

```matlab
freq = 2.4e9;
bw = 200e6;
ant = design(patchMicrostrip, freq);

% FAST: single EM solve, then interpolation during evaluation
sAntLoad = sparameters(ant, linspace(freq - bw, freq + bw, 51));

mn = matchingnetwork;
mn.CenterFrequency = freq;
mn.Bandwidth = bw;
mn.LoadImpedance = sAntLoad;
mn.Components = 2;

addEvaluationParameter(mn, 'gammain', '<', -15, [freq-bw/2 freq+bw/2], 1);
cd = circuitDescriptions(mn);
disp(cd)
```

Use 51–101 frequency points spanning at least the matching bandwidth. See `references/advanced-workflows.md` for a 2-element vs 3-element bandwidth comparison.

## Property Setting Order

**Critical:** For frequency-dependent loads, properties must be set in this order:

```matlab
mn = matchingnetwork;
mn.CenterFrequency = freq;    % 1. Set frequency FIRST
mn.Bandwidth = bw;            % 2. Bandwidth (optional)
mn.LoadImpedance = load;      % 3. Load AFTER frequency
mn.Components = 2;            % 4. Topology (any time)
```

Setting `LoadImpedance` before `CenterFrequency` when the load is frequency-dependent errors: *"Cannot evaluate source impedance and/or load impedance at given center frequency."*

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- Common bands: 900 MHz (IoT), 2.4 GHz (Wi-Fi/BT), 5.8 GHz (Wi-Fi 5/6), 28 GHz (5G mmWave)

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to RF Toolbox plots (`rfplot`, `smithplot`).
- **Do** add titles to manual `plot()` figures.
- Use `fprintf` for formatted numerical output.
- Show all plots in separate figures. Include units in all output.

## Guidelines

- **Do not over-explain** matching network theory. The user is a professional.
- **Set CenterFrequency before LoadImpedance** -- this is the most common error.
- **Property is `Bandwidth`** not `BandWidth` -- case-sensitive.
- **`rfplot(mn)` shows matched system performance** (gammain and Gt with load connected).
- **`sparameters(mn, freq)` returns the matching circuit as a 2-port** (without load termination).
- **`addEvaluationParameter` requires all 5 args:** parameter, comparison, targetdB, band, weight.
- **`circuitDescriptions` returns a table** -- index by row for specific circuits.
- **`exportCircuits(mn, idx)` returns a `circuit` object** for further RF Toolbox analysis.
- **`disableAutomaticNetworks` and `addNetwork` do not return** -- they mutate the object in place (handle class).
- **When user says "match" or "improve S11"**, use this skill with the antenna as `LoadImpedance`.
- **When user says "distributed" or "microstrip matching"**, use `richards` after designing lumped network. When user says "realistic" or "lossy", set `LoadedQ` to a finite value (30-100 typical).
- **Default to `Components = 2`** unless user needs wider bandwidth (then use 3 or specific topology). 2-element for BW < 5% of center freq; 3-element when fractional BW > 5% or load has high Q.
- **Prefer `sparameters(ant, freqRange)` over raw antenna object as `LoadImpedance`** — avoids repeated EM solves (see Workflow 13). When antenna design freq ≠ operating freq, set `CenterFrequency` to the operating frequency and pre-compute S-params around that band (see Workflow 12).
- **`deleteNetwork(mn, idx)`** removes a circuit from the candidate pool; **`clearEvaluationParameter(mn, idx)`** removes an evaluation parameter by row index.

----

Copyright 2026 The MathWorks, Inc.
