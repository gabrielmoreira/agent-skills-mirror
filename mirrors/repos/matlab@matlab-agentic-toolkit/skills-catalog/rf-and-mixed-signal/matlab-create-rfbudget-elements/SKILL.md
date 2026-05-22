---
name: matlab-create-rfbudget-elements
description: >
  Create and configure all rfbudget-compatible element objects -- active (amplifier, modulator,
  rfelement, nport, rffilter, rfantenna, attenuator, phaseshift) and passive (seriesRLC, shuntRLC,
  lcladder, txline*) -- for use in rfbudget cascade analysis and circuit composition. Use when
  defining amplifiers, mixers, filters, attenuators, phase shifters, antennas, generic RF components,
  inline passive networks (DC blocks, bias tees, matching sections), LC ladders, or transmission
  line segments. Trigger on amplifier, modulator, rfelement, nport, rffilter, rfantenna, attenuator,
  phaseshift, mixer, LNA, noise figure, OIP3, IIP3, antenna element, link budget, EIRP, seriesRLC,
  shuntRLC, lcladder, txlineMicrostrip, txlineCoaxial, txlineCPW, txlineStripline, transmission
  line, bias tee, DC block, inline passive.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "2.0"
---

# rfbudget Element Objects

Create and configure all rfbudget-compatible elements -- active components (amplifier, modulator, attenuator, phaseshift) and passive networks (seriesRLC, shuntRLC, lcladder, rffilter, nport, transmission lines). These are the building blocks for `rfbudget` cascade analysis and `circuit` composition.

## When to Use

- Defining amplifiers, mixers, filters, attenuators, phase shifters, antennas for rfbudget
- Creating generic RF components with gain, NF, IP3 specifications
- Synthesizing LC filters with rffilter (Butterworth, Chebyshev)
- Loading measured S-parameter data as nport elements
- Setting up link budgets with rfantenna (EIRP, path loss)
- Creating inline passive networks (DC blocks, bias tees, matching sections) for rfbudget
- Building LC ladder filters for cascade analysis
- Adding transmission line segments to an rfbudget signal chain

## When NOT to Use

- Building arbitrary circuit topologies with node wiring -- use `matlab-compose-rf-circuit`
- Computing rfbudget cascade analysis -- use `matlab-analyze-rf-budget`
- Analyzing amplifier stability or gain -- use `matlab-analyze-rf-amplifier`
- Impedance matching network design and optimization -- use `matlab-design-matching-network`
- Signal integrity channel modeling -- use `matlab-model-si-channel`

## Workflow

1. **Select element type** -- Choose from active, passive, or transmission line elements
2. **Configure properties** -- Set gain, NF, IP3, impedance, R/L/C values, or physical line parameters
3. **Validate** -- Extract S-parameters or inspect properties to verify behavior
4. **Use in chain** -- Add to `rfbudget` or `circuit` for cascade or circuit analysis

## Element Hierarchy

All rfbudget elements subclass from a circuit Element class, so every element below also works in `circuit` via `add()`.

### Active Elements

| Object | Represents | Key Properties |
|--------|-----------|----------------|
| `amplifier` | Active gain stage (LNA, PA, driver) | Gain, NF, OIP3, nonlinear model |
| `modulator` | Frequency converter (mixer) | Gain, NF, OIP3, LO, ConverterType |
| `rfelement` | Generic 2-port (cable, coupler) | Gain, NF, OIP3 |
| `attenuator` | Matched attenuator pad | Attenuation, Zin, Zout |
| `phaseshift` | Lossless phase shifter | PhaseShift (degrees) |

### Passive / Data-Driven Elements

| Object | Represents | Key Properties |
|--------|-----------|----------------|
| `nport` | Component from S-parameter data | Touchstone file or sparameters object |
| `rffilter` | Synthesized LC filter | ResponseType, FilterType, FilterOrder |
| `rfantenna` | Antenna in link budget | Type, Gain, TxEIRP, PathLoss |
| `seriesRLC` | Series R+L+C in signal path | R, L, C |
| `shuntRLC` | Shunt R+L+C to ground | R, L, C |
| `lcladder` | LC ladder filter (pi/tee topologies) | Topology, L, C values |

### Transmission Lines

| Object | Description |
|--------|-------------|
| `txlineDelayLossless` | Ideal lossless delay line (Z0 + TimeDelay) |
| `txlineDelayLossy` | Ideal lossy delay line (Z0 + TimeDelay + Resistance) |
| `txlineMicrostrip` | Microstrip line |
| `txlineCoaxial` | Coaxial cable |
| `txlineCPW` | Coplanar waveguide |
| `txlineStripline` | Stripline |
| `txlineRLCGLine` | RLCG per-unit-length model |
| `txlineWRLGC` | Frequency-dependent W-element RLGC model |
| `txlineWtable` | Table-based frequency-dependent R/L/C/G model |
| `txlineParallelPlate` | Parallel plate line |
| `txlineTwoWire` | Two-wire line |

**Not rfbudget-compatible:** `resistor`, `capacitor`, `inductor`, `circuit` -- these are primitive elements for general circuit composition only (see `matlab-compose-rf-circuit` skill).

## `amplifier` -- Active Gain Stages

```matlab
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');
ampFromFile = amplifier('FileName', 'default.s2p', 'Name', 'LNAMeasured');
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `Gain` | 0 | Small-signal gain (dB) |
| `NF` | 0 | Noise figure (dB) |
| `OIP3` / `IIP3` | Inf | Third-order intercept (dBm) -- related: OIP3 = IIP3 + Gain |
| `OIP2` | Inf | Output second-order intercept (dBm) |
| `OP1dB` / `IP1dB` | Inf | 1-dB compression (dBm) -- related: OP1dB = IP1dB + Gain - 1 |
| `OPsat` / `IPsat` | Inf | Saturation power (dBm) -- independent of each other |
| `Model` | `'poly'` | Nonlinear model: `'poly'`, `'cubic'`, `'ampm'`, `'sparam'` |
| `Zin` / `Zout` | 50 | Impedance (Ohm) |
| `Name` | `''` | Element name (must be valid MATLAB identifier) |

**Conventions:** Amplifiers use output-referred (OIP3, OP1dB, OPsat). Mixers/modulators use input-referred (IIP3, IP1dB, IPsat). For `'poly'` model, set all compression params you have. For `'cubic'`, set `Nonlinearity` to select which ONE param shapes the curve.

See `reference/amplifier-models.md` for detailed model comparison, compression parameter relationships, and S-parameter file loading.

## `modulator` -- Mixers and Frequency Converters

```matlab
downMixer = modulator('Gain', -6, 'NF', 10, 'OIP3', 20, ...
    'LO', 2.1e9, 'ConverterType', 'Down', 'Name', 'Mixer');

upMixer = modulator('Gain', -8, 'NF', 12, 'OIP3', 18, ...
    'LO', 1.5e9, 'ConverterType', 'Up', 'Name', 'UpConv');
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `LO` | 0 | Local oscillator frequency (Hz) |
| `ConverterType` | `'Down'` | `'Down'` or `'Up'` conversion |
| `Gain` | 0 | Conversion gain/loss (dB) |
| `NF` | 0 | Noise figure (dB) |
| `OIP3` | Inf | Output IP3 (dBm) |
| `ImageReject` | true | Reject image frequency |
| `ChannelSelect` | true | Select desired channel |

**Gotcha:** After a `modulator`, the signal frequency changes. In an `rfbudget`, subsequent stages operate at the converted frequency. For a down-converter: `fOut = fIn - LO` (or `LO - fIn` depending on sideband).

## `rfelement` -- Generic 2-Port Components

Use for cables, couplers, or any passive/active component defined by scalar specs:

```matlab
atten = rfelement('Gain', -10, 'NF', 10, 'Name', 'Atten');
cable = rfelement('Gain', -1.5, 'NF', 1.5, 'Name', 'Cable');
```

Properties: `Gain`, `NF`, `OIP3`, `OIP2`, `Zin`, `Zout`, `Name`.

**Gotcha:** For a passive device, NF equals the absolute value of gain in dB (NF = |Gain|). A -3 dB attenuator has NF = 3 dB. Setting inconsistent values (e.g., Gain=-3, NF=0) produces incorrect budget results. Prefer the `attenuator` object for attenuation -- it handles NF automatically.

## `rfantenna` -- Antenna Element for Link Budgets

Models a transmit or receive antenna in an `rfbudget` chain, computing EIRP and received power from `TxEIRP`, `PathLoss`, and antenna `Gain`.

```matlab
tx = rfantenna('Type', 'Transmitter', 'Gain', 6, 'Name', 'TxAnt');
rx = rfantenna('Type', 'Receiver', 'Gain', 3, 'TxEIRP', 30, ...
    'PathLoss', 60, 'Name', 'RxAnt');
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `Type` | `'Transmitter'` | `'Transmitter'`, `'Receiver'`, or `'TransmitReceive'` |
| `Gain` | 0 | Antenna gain (dB) -- scalar for Tx/Rx, 1x2 `[TxGain RxGain]` for TransmitReceive |
| `Z` | 50 | Impedance (Ohm) -- scalar or 1x2 for TransmitReceive |
| `TxEIRP` | -30 | Transmitter EIRP (dBm) -- used by Receiver to compute input power |
| `PathLoss` | 0 | Path loss between Tx and Rx (dB) |

### Behavior in rfbudget

- **Transmitter:** Placed at end of chain. Adds antenna `Gain` to `TransducerGain` and `OutputPower`. EIRP = OutputPower at the antenna stage.
- **Receiver:** Placed at start of chain. Computes received power as `TxEIRP - PathLoss + Gain`. Adds 0 dB to `TransducerGain`. The `AvailableInputPower` argument to `rfbudget` is **ignored** (warning issued).
- **TransmitReceive:** Can go anywhere in the chain. `Gain` must be 1x2 vector `[TxGain RxGain]`.

```matlab
% Receiver link budget: Rx computes its own input power
rx = rfantenna('Type', 'Receiver', 'Gain', 3, 'TxEIRP', 30, ...
    'PathLoss', 60, 'Name', 'RxAnt');
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');
b = rfbudget([rx lna], 2.4e9, -30, 10e6);
% Input power = TxEIRP - PathLoss + Gain = 30 - 60 + 3 = -27 dBm
```

**Gotcha:** Only one `rfantenna` element is allowed per `rfbudget` chain.

**Gotcha:** `rfantenna` is a 1-port element (2 terminals: `p1+`, `p1-`). In a `circuit`, use `add(ckt, [1 0], ant)` with 2 nodes, not 4.

**Gotcha:** The received power property is `RxP`, not `AvailableInputPower`. `AvailableInputPower` is a parameter on `rfbudget`, not on `rfantenna`. Receiver computes input power from `TxEIRP - PathLoss + Gain`.

**Gotcha:** You cannot call `sparameters()` directly on an `rfbudget` object. To extract S-parameters from a budget, first convert to a circuit: `sp = sparameters(circuit(b), freq)`.

## `attenuator` -- Matched Attenuator Pad

A dedicated attenuator element that automatically handles NF derivation and impedance matching.

```matlab
pad = attenuator('Attenuation', 6, 'Name', 'Pad6dB');
pad50to75 = attenuator('Attenuation', 10, 'Zin', 50, 'Zout', 75, 'Name', 'MatchPad');
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `Attenuation` | 3 | Attenuation in dB (positive value) |
| `Zin` | 50 | Input impedance (Ohm) |
| `Zout` | 50 | Output impedance (Ohm) |

In `rfbudget`, NF equals `Attenuation` automatically -- no manual NF setting needed.

**Gotcha:** When `Zin != Zout`, there is a **minimum attenuation** requirement. For example, `Zin=50, Zout=75` requires `Attenuation > 5.72 dB`. MATLAB reports the exact threshold in the error message. Matched impedances (`Zin == Zout`) have no minimum.

## `phaseshift` -- Lossless Phase Shifter

Adds a frequency-independent phase shift with zero insertion loss.

```matlab
ps = phaseshift('PhaseShift', 90, 'Name', 'PS90');
```

### Properties

| Property | Default | Description |
|----------|---------|-------------|
| `PhaseShift` | 90 | Phase shift in degrees |

In `rfbudget`: Gain = 0 dB, NF = 0 dB (lossless). In S-parameters: `|S21| = 1`, `angle(S21) = PhaseShift`.

**Gotcha:** The `PhaseShift` value maps directly to the S21 phase angle (positive = phase lead, negative = phase lag). `PhaseShift=45` gives `angle(S21) = +45 deg`.

## `nport` -- S-Parameter-Based Components

Use when you have measured or simulated S-parameter data. Accepts `.s1p` through any `.snp` Touchstone file:

```matlab
filter = nport('passive.s2p', 'BPFilter');   % Name is positional (2nd arg)

% Or from a sparameters object
s = sparameters(data, freq, 50);
comp = nport(s, 'CustomComp');
```

**Note:** `nport` accepts 1-port (`.s1p`) files, but `rfbudget` requires 2+ port elements. Use 1-port nport in `circuit` objects (e.g., as a shunt load: `add(ckt, [1 0], np)`).

**Note:** `.amp` files are NOT supported by `nport` or `sparameters`. Use the legacy `rfckt.amplifier` to read `.amp` files.

### Multi-Port Selection

For components with more than 2 ports, specify which ports to use:

```matlab
n = nport('default.s4p');
n.Input = 1;          % Input port number
n.Output = 3;         % Output port number
n.Termination = 50;   % Terminate unused ports
```

## `rffilter` -- Synthesized LC Filters

```matlab
bpf = rffilter('ResponseType', 'Bandpass', 'FilterType', 'Butterworth', ...
    'FilterOrder', 5, 'PassbandFrequency', [2.3e9 2.5e9], 'Name', 'BPF');
```

Key properties: `ResponseType` (Lowpass/Highpass/Bandpass/Bandstop), `FilterType` (Butterworth/Chebyshev/InverseChebyshev), `FilterOrder`, `PassbandFrequency` (scalar for LP/HP, 2-vector for BP/BS).

**Gotcha:** `FilterType` is the design algorithm, `ResponseType` is the frequency shape. `rffilter('FilterType', 'Bandpass')` errors.

See `reference/rffilter-synthesis.md` for implementation options, design data access, and full property list.

## `seriesRLC` and `shuntRLC` -- Inline Passive Networks

### Series Elements (In-Line with Signal Path)

```matlab
L1 = seriesRLC('L', 2.7e-9, 'Name', 'Lseries');          % Inductor only
C1 = seriesRLC('C', 1.2e-12, 'Name', 'DCBlock');          % DC blocking cap
R1 = seriesRLC('R', 50, 'Name', 'Rpad');                   % Resistor only
rlc = seriesRLC('R', 10, 'L', 1e-9, 'C', 0.5e-12, 'Name', 'RLC1');
```

### Shunt Elements (To Ground)

```matlab
Cbypass = shuntRLC('C', 100e-12, 'Name', 'Cbypass');       % Bypass cap
Lchoke = shuntRLC('L', 100e-9, 'Name', 'Lchoke');          % RF choke
Rterm = shuntRLC('R', 50, 'Name', 'Rterm');                 % Termination
```

Omitted values default to "absent": seriesRLC uses R=0, L=0, C=Inf (wire-through); shuntRLC uses R=Inf, L=Inf, C=0 (open-circuit).

**`rfbudget` vs `circuit` behavior:** In `rfbudget`, shuntRLC is modeled as a 2-port inline element (computing insertion loss from its shunt impedance to ground). In a `circuit` object, `add(ckt, [node 0], shuntRLC(...))` wires the element literally between a signal node and ground — this is a different topology. For example, a bias-tee inductor (`shuntRLC('L', 100e-9)`) shows near-zero insertion loss in `rfbudget` at RF frequencies, but if wired as `add(ckt, [2 0], ...)` in a circuit it appears as a shunt path to ground and dominates the S21 response. Use `rfbudget` for cascade analysis of bias tees; use `circuit` only when modeling the full node-level topology.

### Common Building Blocks

| Block | Implementation |
|-------|---------------|
| DC block | `seriesRLC('C', 100e-12, 'Name', 'DCBlk')` |
| Bias tee inductor | `shuntRLC('L', 100e-9, 'Name', 'Lbias')` |
| Pad attenuator | `seriesRLC('R', Rseries)` + `shuntRLC('R', Rshunt)` |
| Termination | `shuntRLC('R', 50, 'Name', 'Term')` |

## `lcladder` -- LC Ladder Filters

LC ladder filter networks. Created from a topology string, inductor values, and capacitor values.

```matlab
% From topology + values
lc = lcladder('lowpasspi', [10e-9 10e-9], [1e-12 1e-12 1e-12], 'LPF');

% From an rffilter object
filt = rffilter('ResponseType', 'Bandpass', 'FilterOrder', 3, ...
    'PassbandFrequency', [2.3e9 2.5e9]);
lc = lcladder(filt, 'BPF');
```

### Topologies

| Topology String | Description |
|----------------|-------------|
| `'lowpasspi'` | Low-pass pi |
| `'lowpasstee'` | Low-pass tee |
| `'highpasspi'` | High-pass pi |
| `'highpasstee'` | High-pass tee |
| `'bandpasspi'` | Band-pass pi |
| `'bandpasstee'` | Band-pass tee |
| `'bandstoppi'` | Band-stop pi |
| `'bandstoptee'` | Band-stop tee |

**Gotcha:** Topology strings are **all lowercase** (`'lowpasspi'`, `'bandpasstee'`). Using mixed-case like `'LowpassPi'` or abbreviations like `'CLC'` errors with "not a valid LC Ladder topology."

## Transmission Lines

All transmission line objects are 2-port and rfbudget-compatible. Use `LineLength` for physical length (not `Length`).

```matlab
% Ideal delay
tl = txlineDelayLossless('Z0', 50, 'TimeDelay', 33e-12);

% Physical lines
rlcg = txlineRLCGLine('R', 0.5, 'L', 250e-9, 'C', 100e-12, 'G', 0, ...
    'LineLength', 0.05, 'Name', 'RLCG1');

% Frequency-dependent W-element
tl = txlineWRLGC('Lo', 350e-9, 'Co', 130e-12, 'Ro', 2, ...
    'Rs', 5e-4, 'Gd', 1e-11, 'LineLength', 0.1, 'Name', 'WLine');
```

Available types: `txlineDelayLossless`, `txlineDelayLossy`, `txlineMicrostrip`, `txlineCoaxial`, `txlineCPW`, `txlineStripline`, `txlineParallelPlate`, `txlineTwoWire`, `txlineRLCGLine`, `txlineWRLGC`, `txlineWtable`.

See `reference/transmission-lines.md` for all types, properties, and gotchas.

## Using in rfbudget

All elements in this skill plug directly into rfbudget's element array:

```matlab
lna = amplifier('Name', 'LNA', 'Gain', 15, 'NF', 1.5, 'OIP3', 20);
dcblk = seriesRLC('C', 100e-12, 'Name', 'DCBlock');
bpf = lcladder(rffilter('ResponseType', 'Bandpass', 'FilterOrder', 3, ...
    'PassbandFrequency', [2.3e9 2.5e9]), 'BPF');

b = rfbudget([dcblk lna bpf], 2.4e9, -30, 10e6);
show(b);   % Opens GUI table; no command-window output
```

### circuit Objects Are NOT rfbudget-Compatible

A `circuit` object cannot be added to rfbudget directly. Workaround -- convert to nport via Touchstone:

```matlab
% Build circuit
ckt = circuit('MyNetwork');
add(ckt, [1 2], seriesRLC('L', 10e-9, 'Name', 'L1'));
add(ckt, [2 0], shuntRLC('C', 1e-12, 'Name', 'C1'));
setports(ckt, [1 0], [2 0]);

% Convert to nport for rfbudget
s = sparameters(ckt, linspace(1e9, 6e9, 500));
rfwrite(s, 'mynetwork.s2p');
np = nport('mynetwork.s2p', 'MyNetwork');
% np works in rfbudget
```

## Common Patterns

### Clone Elements for Reuse

An element object cannot appear more than once -- not in the same chain and not across separate budgets or circuits. Use `clone()` every time you need a second instance:

```matlab
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');

% ERROR: same object used twice in one chain
% b = rfbudget([lna filter lna], 2.4e9, -30, 10e6);

% CORRECT: clone for the second use
b = rfbudget([lna filter clone(lna)], 2.4e9, -30, 10e6);
```

### Standalone S-Parameter Analysis

Any element can compute S-parameters directly without wrapping in a circuit:

```matlab
freq = linspace(1e9, 10e9, 500);
s = sparameters(mstrip, freq);

figure;
tiledlayout(1, 2);
nexttile; rfplot(s, 2, 1); title('S21 -- Insertion Loss');
nexttile; rfplot(s, 1, 1); title('S11 -- Return Loss');
```

## Gotchas

1. **Name must be a valid MATLAB identifier** -- No spaces, no special characters. Use `'IFAmp'` not `'IF Amp'`.
2. **Elements are handle objects** -- Modifying an element after adding it to a budget changes the budget. Use `clone` for independent copies.
3. **Passive NF equals loss** -- For `rfelement` with negative gain, NF should equal `abs(Gain)`. Prefer `attenuator` which handles this automatically.
4. **nport default ports** -- `nport` uses ports 1 (input) and 2 (output) by default. For multi-port files, set `Input` and `Output` explicitly.
5a. **nport Name is positional, not NV** -- Use `nport('file.s2p', 'MyName')` or set `np.Name = 'MyName'` after construction. The NV syntax `nport('file.s2p', 'Name', 'X')` does NOT work (it sets Name to the literal string `'Name'`).
5. **rffilter is ideal** -- Synthesized filters assume ideal components with no parasitic effects. For realistic filters, use measured S-parameter data via `nport`.
6. **rfantenna is 1-port** -- Only one allowed per rfbudget chain. Receiver adds 0 to TransducerGain and computes input power from TxEIRP/PathLoss/Gain; it ignores `AvailableInputPower`. Transmitter adds its Gain to TransducerGain. TransmitReceive requires 1x2 `Gain` and `Z` vectors.
7. **attenuator minimum for mismatched Z** -- When `Zin != Zout`, there is a minimum attenuation floor. Matched impedances have no minimum.
8. **phaseshift sign convention** -- Positive `PhaseShift` = positive S21 phase angle (phase lead).
9. **rffilter `FilterType` is the design method** -- `FilterType` means Butterworth/Chebyshev/InverseChebyshev (design algorithm). `ResponseType` means Lowpass/Highpass/Bandpass/Bandstop (frequency shape). Using `rffilter('FilterType', 'Bandpass')` errors -- use `rffilter('ResponseType', 'Bandpass')` instead.
10. **`'poly'` vs `'cubic'` model** -- `'poly'` (default) uses ALL set compression params (e.g., OIP3, OP1dB, OPsat) to fit a higher-order polynomial. `'cubic'` uses only ONE param selected by the `Nonlinearity` property for a 3rd-order fit. Prefer `'poly'` for new code.
11. **`LineLength` not `Length`** -- all transmission line objects use `LineLength` for physical length.
12. **lcladder constructor is positional** -- `lcladder(topology, L, C, name)`, not name-value pairs.
13. **lcladder topology strings are all lowercase** -- `'lowpasspi'`, not `'LowpassPi'`.
14. **circuit objects don't work in rfbudget** -- convert to nport via Touchstone file as a workaround.
15. **Elements cannot be reused across rfbudget objects** -- use `clone()` to create independent copies.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel plots
- Always label axes with units and include figure titles
- Name elements descriptively (e.g., `'DCBlock'`, `'Lchoke'`, `'BPF'`)

----

Copyright 2026 The MathWorks, Inc.

----
