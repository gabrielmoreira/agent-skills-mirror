---
name: matlab-compose-rf-circuit
description: >
  Compose general-purpose RF circuits from R/L/C elements, amplifiers, modulators, mixers, nport
  S-parameter blocks, and other RF elements using RF Toolbox. Use when building arbitrary circuit
  topologies wired between nodes with add(), extracting S-parameters with setports, embedding
  subcircuits with setterminals, or converting lumped designs to distributed via Richards/Kuroda.
  Trigger on resistor, capacitor, inductor, mutualInductor, rfdivider, circuit, add, setports,
  setterminals, clone, subcircuit, netlist, SPICE-like, RC network, RLC network, circuit composition,
  node, terminal, richards, kuroda, insertUnitElement, realize, txlineElectricalLength, lumped to
  distributed, stub filter, amplifier in circuit, modulator in circuit, mixerIMT in circuit, nport
  in circuit, active circuit, nonlinear circuit, mixer circuit, RF front end circuit, filter circuit.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "2.0"
---

# General-Purpose RF Circuit Composition

Build RF circuits from primitive R/L/C elements, active components (amplifier, modulator, mixerIMT), and `nport` S-parameter blocks -- all wired between nodes in a SPICE-like netlist. Extract S-parameters, embed subcircuits hierarchically, and convert lumped designs to distributed implementations.

## When to Use

- Building arbitrary RF circuit topologies with node wiring (SPICE-like netlist)
- Combining R/L/C elements with active components (amplifier, modulator, mixerIMT)
- Embedding nport S-parameter blocks alongside lumped elements
- Creating reusable subcircuits with setterminals for hierarchical composition
- Converting lumped designs to distributed implementations (Richards/Kuroda)

## When NOT to Use

- Building SI channel models from nport + transmission lines -- use `matlab-model-si-channel`
- Creating 2-port circuit blocks for rfbudget (seriesRLC, shuntRLC, lcladder) -- use `matlab-create-rfbudget-elements`
- Defining standalone RF elements for rfbudget cascade -- use `matlab-create-rfbudget-elements`
- Cascading or de-embedding S-parameter blocks -- use `matlab-deembed-rf-cascade`

## Workflow

1. **Create circuit** — Instantiate with `circuit('Name')`
2. **Add elements** — Wire R/L/C, active components, and nport blocks to nodes with `add`
3. **Define ports** — Call `setports` for S-parameter extraction or `setterminals` for subcircuit embedding
4. **Analyze** — Extract S-parameters with `sparameters(ckt, freq)`

## Primitive Elements (2-Terminal)

Each has terminals `p` (positive) and `n` (negative). Connect to any two circuit nodes.

```matlab
r = resistor(100, 'R1');          % 100 Ohm
c = capacitor(1e-12, 'C1');       % 1 pF
l = inductor(10e-9, 'L1');        % 10 nH
```

**Gotcha:** Primitive constructors (`resistor`, `capacitor`, `inductor`) accept only a positional value and an optional name string: `resistor(100, 'R1')`. Name-value syntax like `resistor('Resistance', 100, 'Name', 'R1')` is **not** supported.

Properties: `Resistance`, `Capacitance`, `Inductance`, `Name`, `Terminals`.

**Handle semantics:** Changing a property (e.g., `r.Resistance = 200`) after adding to a circuit immediately affects the circuit -- no need to re-add.

### mutualInductor (4-Terminal, R2023a+)

Coupled inductors for transformer modeling:

```matlab
mi = mutualInductor('Name', 'Xfmr', ...
    'Inductance1', 10e-9, 'Inductance2', 10e-9, ...
    'CouplingCoefficient', 0.95);
```

Terminals: `p1+`, `p2+`, `p1-`, `p2-`. Use `CouplingCoefficient = 1` for an ideal transformer.

**Gotcha:** Constructor uses name-value pairs only -- no positional arguments. The coupling parameter is `CouplingCoefficient`, **not** `MutualInductance`.

### rfdivider (6-Terminal / 3-Port, R2023a+)

Wilkinson power divider:

```matlab
d = rfdivider('Name', 'Split1', 'Impedance', 50);
```

Terminals: `p1+`, `p2+`, `p3+`, `p1-`, `p2-`, `p3-`. Add to a circuit with 6 nodes.

## Active Elements in Circuit

`amplifier`, `modulator`, and `mixerIMT` are 2-port (4-terminal) elements that work in `circuit` via `add()`. This lets you build complete RF front-end topologies with active and passive elements in a single netlist.

### amplifier in Circuit

```matlab
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');

ckt = circuit('RxFrontEnd');
add(ckt, [1 2], capacitor(1e-12, 'DCBlk'));   % DC block
add(ckt, [2 3 0 0], lna);                      % LNA: 4-node mapping
add(ckt, [3 4], inductor(2.7e-9, 'Lmatch'));   % matching inductor
setports(ckt, [1 0], [4 0]);

freq = linspace(1e9, 6e9, 500);
s = sparameters(ckt, freq);
```

### modulator in Circuit

```matlab
mix = modulator('Gain', -6, 'NF', 10, 'OIP3', 20, ...
    'LO', 2.1e9, 'ConverterType', 'Down', 'Name', 'Mixer');

ckt = circuit('DownConv');
add(ckt, [1 2 0 0], mix);
add(ckt, [2 3], resistor(50, 'Rload'));
setports(ckt, [1 0], [3 0]);
```

### mixerIMT in Circuit

```matlab
m = mixerIMT('LO', 2.1e9, 'ConverterType', 'Down', 'NF', 10, ...
    'ReferenceInputPower', -10, 'NominalOutputPower', -16, 'Name', 'Mixer');

ckt = circuit('MixerStage');
add(ckt, [1 2 0 0], m);    % 4-terminal: p1+->1, p2+->2, p1-->0, p2-->0
setports(ckt, [1 0], [2 0]);
```

### Active Element Node Mapping

All 2-port RF elements (amplifier, modulator, mixerIMT, nport, rffilter, attenuator, phaseshift) have 4 terminals (`p1+`, `p2+`, `p1-`, `p2-`). Use 4-node mapping in `add`:

```matlab
add(ckt, [nodeIn nodeOut nodeInRef nodeOutRef], element);
```

For grounded references, the shorthand `add(ckt, [nodeIn nodeOut 0 0], element)` is typical. Primitive 2-terminal elements (resistor, capacitor, inductor) use 2-node mapping: `add(ckt, [nodeA nodeB], element)`.

**Gotcha:** Active elements are handle objects -- modifying properties after `add` immediately affects the circuit. Use `clone()` for independent copies.

## nport Elements in Circuit

Embed measured or simulated S-parameter data as a circuit element:

```matlab
np = nport('measured.s2p');
np.Name = 'Filter';

ckt = circuit('RxChain');
add(ckt, [1 2 0 0], np);               % 4 nodes: p1+->1, p2+->2, p1-->0, p2-->0
add(ckt, [2 3], inductor(10e-9, 'L1')); % lumped element after nport
setports(ckt, [1 0], [3 0]);
```

A 2-port nport has 4 terminals (`p1+`, `p2+`, `p1-`, `p2-`), so `add` takes a 4-element node vector.

For multi-port nport (4-port, etc.), differential port mapping, and SI channel modeling with nport, see the `matlab-model-si-channel` skill.

### Identifying Input vs Output Ports

Before wiring a multi-port nport, determine which ports are inputs (near-end) and which are outputs (far-end). Look at the **lowest-frequency S-parameter data**: the off-diagonal elements closest to unity (0 dB) identify the through connections.

```matlab
% Inspect at the lowest frequency to find through paths
s4 = sparameters('device.s4p');
S = s4.Parameters(:,:,1);          % S-matrix at lowest frequency
disp(abs(S));                       % Through paths have magnitude ≈ 1
% If S(2,1) ≈ 1 and S(4,3) ≈ 1, then ports 1,3 are inputs and 2,4 are outputs
```

For typical 4-port differential pairs: through paths are S21 and S43, meaning ports 1,3 are near-end (input) and ports 2,4 are far-end (output).

### Multi-Port nport Node Mapping

A 4-port nport has **8 terminals** (`p1+`, `p2+`, `p3+`, `p4+`, `p1-`, `p2-`, `p3-`, `p4-`). Map all 8 to circuit nodes:

```matlab
np4 = nport('device.s4p');
ckt = circuit('FourPort');
add(ckt, [1 2 3 4 0 0 0 0], np4);  % 4 signal nodes + 4 ground refs
setports(ckt, [1 0], [2 0], [3 0], [4 0]);
```

### Adding Lossless Transmission Lines to Each Port

Use `txlineDelayLossless` (there is no generic `txline` constructor) and `clone()` for each instance:

```matlab
s4 = sparameters('device.s4p');
np = nport(s4);
tl = txlineDelayLossless('Z0', 50, 'TimeDelay', 33e-12, 'Name', 'TL');

ckt = circuit('Extended');
add(ckt, [1 2 3 4 0 0 0 0], np);           % 4-port nport: 8-node mapping
add(ckt, [5 0 1 0], tl);                    % TL on port 1
add(ckt, [6 0 2 0], clone(tl));             % TL on port 2 (must clone)
add(ckt, [7 0 3 0], clone(tl));             % TL on port 3 (must clone)
add(ckt, [8 0 4 0], clone(tl));             % TL on port 4 (must clone)
setports(ckt, [5 0], [6 0], [7 0], [8 0]);  % New external ports

freq = s4.Frequencies;
sNew = sparameters(ckt, freq);
rfwrite(sNew, 'device_with_lines.s4p');
```

**Key points:**
- `txlineDelayLossless` constructor only accepts `Z0`, `TimeDelay`, and `Name` (NOT `LineLength`)
- There is no generic `txline` constructor -- always use a specific type (e.g., `txlineDelayLossless`, `txlineMicrostrip`)
- Must `clone()` for each additional line -- same object cannot appear twice
- 4-port nport uses 8-node mapping: `[p1+ p2+ p3+ p4+ p1- p2- p3- p4-]`

### Cascading Two 4-Port nport Blocks

To cascade two 4-port blocks (e.g., two sections of a differential channel), connect the output ports of the first to the input ports of the second via internal nodes. For a file where through paths are S21 and S43 (ports 1,3 = input, ports 2,4 = output):

```matlab
n1 = nport('section.s4p');
n2 = nport('section.s4p');

ckt = circuit('Cascade');
% n1: port1(in)=node1, port2(out)=node5, port3(in)=node2, port4(out)=node6
add(ckt, [1 5 2 6 0 0 0 0], n1);
% n2: port1(in)=node5, port2(out)=node3, port3(in)=node6, port4(out)=node4
add(ckt, [5 3 6 4 0 0 0 0], n2);
% External ports: near-end pair (nodes 1,2), far-end pair (nodes 3,4)
setports(ckt, [1 0], [3 0], [2 0], [4 0]);

sCascade = sparameters(ckt, freq);
```

For simple series cascading without arbitrary topology control, `cascadesparams` (see `matlab-deembed-rf-cascade` skill) is more concise but requires standard port ordering (ports 1:N = input, N+1:2N = output).

### nport in rfbudget (Port Selection)

For `rfbudget` use, set `Input` and `Output` properties on the nport directly:

```matlab
np = nport('device.s4p');
np.Input = 1;      % default
np.Output = 3;     % select port 3 as output (default is 2)
b = rfbudget(np, 5e9, 0, 1e6);
```

**Gotcha:** `nport.Input`/`Output` are for rfbudget only -- in `circuit`, use node mapping and `setports` instead.

## Building Circuits with `add`

The `add` method wires element terminals to circuit nodes -- like a SPICE netlist statement.

```matlab
ckt = circuit('PiFilter');
add(ckt, [1 0], capacitor(1e-12, 'C1'));     % C1: node 1 to node 0
add(ckt, [1 2], inductor(10e-9, 'L1'));      % L1: node 1 to node 2
add(ckt, [2 0], capacitor(1e-12, 'C2'));     % C2: node 2 to node 0
```

### Node Mapping Rules

- `add(ckt, [nodeA, nodeB], elem)` -- for 2-terminal elements, maps `p` to `nodeA`, `n` to `nodeB`
- `add(ckt, [n1, n2, n3, n4], elem)` -- for 4-terminal elements, maps `p1+`->`n1`, `p2+`->`n2`, `p1-`->`n3`, `p2-`->`n4`
- Node 0 is conventionally ground, but has no special meaning -- any node can be a reference
- Nodes are created on-the-fly when first referenced
- Optional terminal reordering: `add(ckt, [3 4], c1, {'n', 'p'})`

### Key Constraints

- **Elements cannot be shared** -- an element added to one circuit cannot be added to another. Use `clone()` first.
- **Duplicate names auto-suffix** -- adding a second `'R1'` creates `'R1_1'`
- **No remove method** -- elements cannot be removed once added. Rebuild the circuit to change topology.

## `setports` vs `setterminals`

These define how the outside world connects to a circuit. **Each can only be called once per circuit.**

### `setports` -- For S-Parameter Extraction

Defines port pairs (signal + reference node). Required before `sparameters()`.

```matlab
setports(ckt, [1 0], [2 0]);           % 2-port: port 1 at node 1, port 2 at node 2
setports(ckt, [1 0], [2 0], [3 0]);    % 3-port
```

Creates terminals `p1+`, `p1-`, `p2+`, `p2-`, etc.

### `setterminals` -- For Subcircuit Embedding

Defines individual terminals mapped to nodes. Used when a circuit will be embedded inside another.

```matlab
setterminals(ckt, [1 2 0], {'in', 'out', 'gnd'});
```

**Gotcha:** `setterminals` takes a **single node vector**, not separate node arguments. Use `setterminals(ckt, [1 2])`, not `setterminals(ckt, 1, 2)`. The optional second argument is a cell array of terminal names.

Terminal count is arbitrary (not necessarily even). Nodes must already exist in the circuit.

### When to Use Each

| Goal | Use |
|------|-----|
| Extract S-parameters from a standalone circuit | `setports` |
| Embed a circuit as a subcircuit in a parent | `setterminals` |
| Both (embed AND extract S-params from parent) | `setterminals` on sub, `setports` on parent |

## Subcircuit Hierarchy

A circuit with terminals/ports defined can be embedded inside another circuit via `add()`.

```matlab
% Build a reusable L-match subcircuit
lMatch = circuit('LMatch');
add(lMatch, [1 2], inductor(10e-9, 'Ls'));
add(lMatch, [2 0], capacitor(5e-12, 'Cp'));
setterminals(lMatch, [1 2 0], {'in', 'out', 'gnd'});

% Embed two stages in a parent circuit
top = circuit('Cascade');
add(top, [1 2 0], lMatch);           % in->1, out->2, gnd->0
add(top, [2 3 0], clone(lMatch));    % Must clone for reuse
setports(top, [1 0], [3 0]);

freq = linspace(1e9, 6e9, 500);
s = sparameters(top, freq);
```

**Gotcha:** A circuit with `setports` can also be embedded -- its 2N terminals (`p1+`, `p1-`, ...) map to 2N parent nodes.

## Multi-Port Networks

Pass multiple `[signal ground]` pairs to `setports` for N-port extraction:

```matlab
setports(ckt, [1 0], [2 0], [3 0]);    % 3-port -> 3x3 S-parameter matrix
```

## Complete RF Front-End Example

Combine passive and active elements in a single circuit:

```matlab
% Components
dcblk = capacitor(100e-12, 'DCBlock');
lna = amplifier('Gain', 15, 'NF', 2, 'OIP3', 35, 'Name', 'LNA');
bpf = nport('filter.s2p');  bpf.Name = 'BPF';
mix = modulator('Gain', -6, 'NF', 10, 'OIP3', 20, ...
    'LO', 2.1e9, 'ConverterType', 'Down', 'Name', 'Mixer');
ifMatch = circuit('IFMatch');
add(ifMatch, [1 2], inductor(10e-9, 'Ls'));
add(ifMatch, [2 0], capacitor(5e-12, 'Cp'));
setterminals(ifMatch, [1 2 0], {'in', 'out', 'gnd'});

% Assemble
rxCkt = circuit('Receiver');
add(rxCkt, [1 2], dcblk);
add(rxCkt, [2 3 0 0], lna);
add(rxCkt, [3 4 0 0], bpf);
add(rxCkt, [4 5 0 0], mix);
add(rxCkt, [5 6 0], ifMatch);
setports(rxCkt, [1 0], [6 0]);

freq = linspace(0.5e9, 4e9, 500);
s = sparameters(rxCkt, freq);

figure; tiledlayout(1, 2);
nexttile; rfplot(s, 2, 1); title('S21 -- Insertion/Gain');
nexttile; rfplot(s, 1, 1); title('S11 -- Return Loss');
```

## Lumped-to-Distributed Design (Richards, Kuroda, Realize)

Convert lumped L/C circuits to distributed transmission-line implementations.

### Richards Transformation

Convert inductors and capacitors to `txlineElectricalLength` stubs:

```matlab
% On an entire circuit
ckt = circuit('LPF');
add(ckt, [1 2], inductor(10e-9, 'L1'));
add(ckt, [2 0], capacitor(5e-12, 'C1'));
add(ckt, [2 3], inductor(15e-9, 'L2'));
setports(ckt, [1 0], [3 0]);
cktDist = richards(ckt, 2.4e9);     % All L/C -> stubs at 2.4 GHz

% On a single element
[txStub, nodes] = richards(inductor(10e-9, 'L1'), 2.4e9);
```

Also works on `lcladder`, `rffilter`, and `matchingnetwork` objects:
```matlab
cktDist = richards(rffilter('ResponseType','Lowpass','FilterOrder',3,'PassbandFrequency',1e9), 1e9);
```

Inductors become short-terminated stubs; capacitors become open-terminated stubs. Element names get a `_tx` suffix.

### Kuroda Transformation

Rearrange `txlineElectricalLength` elements using Kuroda identities to convert between series and shunt stubs:

```matlab
cktOut = kuroda(cktIn, 'TX1', 'TX2');        % 2-element Kuroda identity
cktOut = kuroda(cktIn, 'TX1', 'TX2', 'TX3'); % 3-element identity
```

Elements can be specified by name, handle, or index. Applies to `txlineElectricalLength` pairs only.

### Insert Unit Element

Insert a quarter-wave transmission line (unit element) at a specified port of an element:

```matlab
cktOut = insertUnitElement(cktIn, 'TL1', 1, 2.4e9, 50);
% Args: (circuit, element, port, opFreq, Z0)
```

### Realize as Physical Transmission Lines

Convert `txlineElectricalLength` stubs to physical microstrip (or other) lines:

```matlab
msTemplate = txlineMicrostrip;
msTemplate.Height = 0.8e-3;
msTemplate.EpsilonR = 4.4;
cktReal = realize(cktDist, msTemplate);
```

**Gotcha:** `realize` requires compatible physical dimensions -- the width/height ratio must be between 0.05 and 20. Adjust the template properties or the stub impedances if this constraint is violated.

### `txlineElectricalLength` -- Ideal Transmission Line

Used as the output of Richards transformation. Defined by electrical length rather than physical dimensions:

```matlab
tx = txlineElectricalLength('Name', 'Stub1', 'Z0', 75, ...
    'LineLength', pi/4, 'ReferenceFrequency', 2.4e9, ...
    'StubMode', 'Series', 'Termination', 'Short');
```

| Property | Description |
|----------|-------------|
| `Z0` | Characteristic impedance (Ohm) |
| `LineLength` | Electrical length (radians) |
| `ReferenceFrequency` | Frequency at which LineLength applies (Hz) |
| `StubMode` | `'NotAStub'`, `'Series'`, or `'Shunt'` |
| `Termination` | `'NotApplicable'`, `'Short'`, or `'Open'` |

## Circuit Methods

| Method | Purpose |
|--------|---------|
| `add(ckt, nodes, elem)` | Wire element to circuit nodes |
| `setports(ckt, ...)` | Define ports for S-parameter extraction |
| `setterminals(ckt, nodes, names)` | Define terminals for subcircuit embedding |
| `sparameters(ckt, freq)` | Compute S-parameters |
| `sparameters(ckt, freq, Z0)` | Compute with custom reference impedance |
| `groupdelay(ckt, freq)` | Compute group delay |
| `clone(ckt)` | Deep copy circuit and all elements |
| `richards(ckt, opFreq)` | Convert lumped L/C to distributed stubs |
| `kuroda(ckt, el1, el2)` | Apply Kuroda identity on txline pairs |
| `insertUnitElement(ckt, el, port, freq, Z0)` | Insert quarter-wave unit element |
| `realize(ckt, txTemplate)` | Convert electrical-length lines to physical |

## Circuit Properties (Read-Only Except Name)

| Property | Description |
|----------|-------------|
| `Elements` | Array of all elements |
| `ElementNames` | Cell array of element names |
| `Nodes` | Integer vector of all nodes |
| `Terminals` | Terminal names (empty until set) |
| `Ports` | Port names (empty until `setports`) |
| `ParentPath` | Path when embedded as subcircuit |
| `ParentNodes` | Parent nodes when embedded |

## Gotchas

1. **`setports`/`setterminals` can only be called once** -- calling either a second time errors with "The terminals for this circuit are already set." Plan your topology before defining terminals.
2. **Elements cannot be shared across circuits** -- always `clone()` before reusing an element or subcircuit in a second circuit.
3. **No element removal** -- once added, elements cannot be removed. Rebuild the circuit to change topology.
4. **Node 0 is not special** -- it is conventionally used as ground but has no built-in ground behavior. Any node can serve as a port reference.
5. **`setterminals` requires existing nodes** -- all nodes in the node vector must already exist in the circuit (created by prior `add` calls). `setports` creates nodes on the fly.
6. **mutualInductor uses name-value pairs only** -- no positional constructor arguments. `mutualInductor(10e-9, 10e-9, 0.8)` errors. The coupling parameter is `CouplingCoefficient`, not `MutualInductance`.
7. **Element Name must be a valid MATLAB identifier** -- no spaces, no leading digits.
8. **Primitive constructors are positional** -- `resistor(100)`, `capacitor(1e-12)`, `inductor(10e-9)` take a value and optional name string. Name-value syntax like `resistor('Resistance', 100)` errors.
9. **`setterminals` takes a node vector** -- `setterminals(ckt, [1 2])`, not `setterminals(ckt, 1, 2)`. Separate scalar arguments error.
10. **Active elements use 4-node mapping** -- `add(ckt, [in out inRef outRef], elem)` for amplifier, modulator, mixerIMT, nport. Using only 2 nodes errors for these elements.
11. **`nport.Input`/`Output` are for rfbudget only** -- these numeric port indices select the through-path for `rfbudget`. In `circuit`, use node mapping and `setports` instead.

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel circuit analysis plots
- Always label axes with units and include figure titles
- Name elements descriptively for readable circuit topology (like SPICE net names)
- Use `clone()` liberally -- it deep-copies all nested elements and subcircuits

----

Copyright 2026 The MathWorks, Inc.

----
