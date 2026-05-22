---
name: matlab-analyze-rf-budget
description: >
  Perform RF system cascade budget analysis using rfbudget in RF Toolbox. Use when computing
  cascaded gain, noise figure, IP2, IP3, SNR, or output power through an RF signal chain.
  Also covers visualization (rfplot, show), solver selection (Friis, HarmonicBalance),
  AM/PM compression tables, and export to RF Blockset, Communications Toolbox, or MATLAB script.
  Trigger on rfbudget, rfBudgetAnalyzer, cascade analysis, noise figure budget, gain budget,
  IP3 budget, link budget, receiver chain, transmitter chain, RF system analysis, signal chain,
  SNR budget, exportRFBlockset, exportScript, exportReceiver, exportTransmitter.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# RF Budget Analysis

Compute cascaded performance metrics (gain, noise figure, IP3, SNR, output power) through an RF signal chain using `rfbudget`.

## When to Use

- Computing cascaded gain, noise figure, IP3, SNR through an RF signal chain
- Visualizing per-stage budget metrics with rfplot or show
- Comparing Friis vs HarmonicBalance solver accuracy
- Exporting RF systems to RF Blockset, Communications Toolbox, or MATLAB scripts
- Computing AM/PM compression tables or mismatch loss

## When NOT to Use

- Creating or configuring rfbudget element objects -- use `matlab-create-rfbudget-elements`
- Composing arbitrary RF circuits with node wiring -- use `matlab-compose-rf-circuit`
- Time-domain simulation of RF systems -- use `matlab-simulate-rf-system`

## Workflow

1. **Define elements** — Create RF elements (see `matlab-create-rfbudget-elements` skill)
2. **Build budget** — Pass element array, input frequency, power, and bandwidth to `rfbudget`
3. **Inspect results** — Read cumulative per-stage properties or use `show` for tabular view
4. **Visualize** — Plot with `rfplot` or `smithplot`
5. **Export** — Generate MATLAB script, RF Blockset model, or Communications Toolbox objects

## Creating an RF Budget

```matlab
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');
bpf = rfelement('Gain', -3, 'NF', 3, 'Name', 'BPF');
mix = modulator('Gain', -6, 'NF', 10, 'OIP3', 20, ...
    'LO', 2.1e9, 'ConverterType', 'Down', 'Name', 'Mixer');
ifAmp = amplifier('Gain', 20, 'NF', 4, 'OIP3', 30, 'Name', 'IFAmp');

b = rfbudget([lna bpf mix ifAmp], 2.4e9, -30, 10e6);
```

Constructor: `rfbudget(elements, inputFreq, availInputPower_dBm, signalBW)`

### Key Properties (Read-Only Results)

All result properties return a vector with one value per stage (cumulative through the chain):

| Property | Description | Units |
|----------|-------------|-------|
| `TransducerGain` | Cumulative gain at each stage | dB |
| `NF` | Cumulative noise figure | dB |
| `OIP3` | Cumulative output third-order intercept | dBm |
| `IIP3` | Cumulative input third-order intercept | dBm |
| `OIP2` | Cumulative output second-order intercept | dBm |
| `IIP2` | Cumulative input second-order intercept | dBm |
| `OutputPower` | Output power at each stage | dBm |
| `OutputFrequency` | Frequency at each stage output | Hz |
| `SNR` | Signal-to-noise ratio at each stage | dB |
| `EIRP` | Effective isotropic radiated power (with rfantenna) | dBm |
| `Directivity` | Antenna directivity (with rfantenna) | dB |

System-level results are the last element of each vector:
```matlab
systemGain = b.TransducerGain(end);    % Total chain gain in dB
systemNF = b.NF(end);                  % System noise figure in dB
systemOIP3 = b.OIP3(end);             % System OIP3 in dBm
systemSNR = b.SNR(end);               % Output SNR in dB
```

### Input Properties (Read-Write)

| Property | Description |
|----------|-------------|
| `Elements` | Array of RF element objects |
| `InputFrequency` | Input signal frequency (Hz) |
| `AvailableInputPower` | Available input power (dBm) |
| `SignalBandwidth` | Signal bandwidth (Hz) |
| `Solver` | `'Friis'` (default) or `'HarmonicBalance'` |
| `AutoUpdate` | `true` (default) — recompute on property change |

## Visualization

### Tabular View

```matlab
show(b);               % Opens interactive GUI table — no command-window output
```

**Gotcha:** `show(b)` opens a GUI table widget but produces no text in the command window. For programmatic access, use `b.TransducerGain`, `b.NF`, `b.OIP3`, `b.OutputPower`, etc.

### RF Budget Analyzer App

```matlab
rfBudgetAnalyzer(b);   % Launch interactive RF Budget Analyzer app with pre-loaded budget
rfBudgetAnalyzer;      % Launch empty app for manual entry
```

### Plotting

```matlab
rfplot(b, 'Pout');     % Output power per stage
rfplot(b, 'GainT');    % Transducer gain per stage
rfplot(b, 'NF');       % Noise figure per stage
rfplot(b, 'OIP3');     % OIP3 per stage
rfplot(b, 'IIP3');     % IIP3 per stage
rfplot(b, 'SNR');      % SNR per stage
```

Valid `rfplot` parameter strings: `'Pout'`, `'GainT'`, `'NF'`, `'OIP3'`, `'IIP3'`, `'SNR'`, `'Sparameters'`, `'OneTone'`, `'TwoTone'`.

**Note:** `rfplot(b)` with no parameter string plots S-parameters (like `rfplot(sparametersObj)`). To plot budget metrics, specify a parameter string: `rfplot(b, 'Pout')`, `rfplot(b, 'GainT')`, etc.

**Note:** `'OneTone'` and `'TwoTone'` require `Solver='HarmonicBalance'` — they error with "Harmonic balance solutions must be computed" if the Friis solver is active.

### Polar and Smith Chart Visualization

Plot S-parameters of each cascade stage vs. frequency:

```matlab
polar(b, 2, 2);        % S22 of each stage on a polar plot
smithplot(b, 1, 1);    % S11 reflection coefficient on Smith chart
```

## Solvers

| Solver | Use Case |
|--------|----------|
| `'Friis'` (default) | Linear cascade analysis — fast, sufficient for most system budgets |
| `'HarmonicBalance'` | Nonlinear analysis — more accurate than Friis, matches RF Blockset Circuit Envelope simulation |

`HarmonicBalance` accounts for compression, intermodulation, and mixer spurs that Friis ignores. Use it when accuracy matters — the results match the highly accurate Circuit Envelope simulation in RF Blockset.

```matlab
b = rfbudget(elements, 2.4e9, -30, 10e6, 'Solver', 'HarmonicBalance');
```

For HarmonicBalance, control harmonic content:
```matlab
b = rfbudget(elements, 2.4e9, -30, 10e6, ...
    'Solver', 'HarmonicBalance', ...
    'HarmonicOrder', 3);
```

## AM/PM Compression Table

Compute the system's AM/AM and AM/PM characteristic:

```matlab
ampmTable = computeAMPMTable(b);
% ampmTable: M×3 matrix [Pin_dBm, Pout_dBm, PhaseShift_deg]

% With custom input power range
pinRange = -40:0.5:10;
ampmTable = computeAMPMTable(b, pinRange);
```

## Mismatch Loss

```matlab
ml = mismatchLoss(b, 1);     % Mismatch loss at stage 1 input boundary (per frequency)
ml = mismatchLoss(b, 2);     % Mismatch loss at stage 2 input boundary (per frequency)
```

Arguments: `(rfbudgetObj, stageNum)` — `stageNum` is required (1 to number of elements). Returns a **vector** of linear loss factors (one per frequency point, 0 to 1, where 1 = perfect match).

## AutoUpdate and Manual Computation

By default, `rfbudget` recomputes whenever a property changes. For batch modifications, disable auto-update:

```matlab
b = rfbudget(elements, 2.4e9, -30, 10e6, 'AutoUpdate', false);
b.InputFrequency = 5.8e9;
b.AvailableInputPower = -20;
computeBudget(b);     % Explicitly trigger computation
```

## Export

### MATLAB Script

```matlab
exportScript(b);                   % Opens generated MATLAB script in the editor
```

### RF Blockset (Simulink)

```matlab
exportRFBlockset(b);               % Opens Simulink model with RF Blockset blocks
```

### Communications Toolbox

```matlab
exportReceiver(b);                 % Opens receiver configuration script in the editor
exportTransmitter(b);              % Opens transmitter configuration script in the editor
```

### Circuit Object

```matlab
c = circuit(b);     % Convert budget to circuit object for S-parameter analysis
s = sparameters(c, freq);
```

## Gotchas

1. **Elements cannot appear twice** — The same element object cannot be used more than once, whether in the same chain (e.g., `rfbudget([lna filt lna], ...)`) or across separate budgets. Use `clone(element)` to create an independent copy: `rfbudget([lna filt clone(lna)], ...)`.
2. **Name must be valid MATLAB identifier** — Element `Name` property cannot contain spaces or special characters. Use `'IFAmp'` not `'IF Amp'`.
3. **Per-stage results are cumulative** — `TransducerGain`, `NF`, `OIP3` etc. are cumulative through the chain, not per-element deltas. The system result is always the last element.
4. **rfplot default is S-parameters** — `rfplot(b)` with no parameter string plots S-parameters. Specify a string for budget metrics: `rfplot(b, 'Pout')`, `rfplot(b, 'GainT')`, etc.
5. **Frequency changes at mixers** — `OutputFrequency` changes after a `modulator` element (down/up conversion). Subsequent stages operate at the new frequency.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel budget comparison plots
- Always label plots with units (dBm, dB, GHz)
- Use `show(b)` for quick inspection before plotting
- Name elements descriptively for readable `show` output

----

Copyright 2026 The MathWorks, Inc.

----
