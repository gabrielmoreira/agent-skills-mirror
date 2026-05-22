---
name: matlab-convert-network-parameters
description: >
  Convert between network parameter types (S, Z, Y, ABCD, T, H, G) and compute mixed-mode
  (differential/common) S-parameters using RF Toolbox. Use when converting S-parameters to
  impedance or admittance, working with differential pairs, extracting ports, or computing
  transfer functions. Trigger on zparameters, yparameters, abcdparameters, tparameters,
  hparameters, gparameters, mixed-mode, differential S-parameters, s2sdd, s2scc, s2sdc, s2scd,
  snp2smp, s2tf, network parameter conversion, port reduction, port reordering.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# Network Parameter Conversions

Convert between S, Z, Y, ABCD, T, H, and G parameter representations. Compute mixed-mode (differential/common) S-parameters and reduce or reorder ports.

## When to Use

- Converting S-parameters to Z, Y, ABCD, T, H, or G representations
- Computing mixed-mode (differential/common) S-parameters from single-ended data
- Reducing N-port networks to M-port with `snp2smp`
- Reordering ports in S-parameter data
- Computing voltage transfer functions with `s2tf`
- Verifying conversion fidelity via round-trip tests

## When NOT to Use

- Loading or visualizing Touchstone files -- use `matlab-manage-sparameters`
- Cascading or de-embedding networks -- use `matlab-deembed-rf-cascade`
- Fitting rational models to S-parameter data -- use `matlab-fit-rational-model`

## Workflow

1. **Start with S-parameters** — Load via `sparameters` (see `matlab-manage-sparameters` skill)
2. **Convert** — Use object constructors for clean impedance tracking, or array functions for raw data
3. **Validate** — Round-trip convert (S→Z→S) to verify numerical accuracy

## Object-Based Conversions (Preferred)

Object constructors automatically handle impedance bookkeeping. This is the modern approach.

```matlab
z = zparameters(s);                    % S → Z
y = yparameters(s);                    % S → Y
a = abcdparameters(s);                 % S → ABCD
t = tparameters(s);                    % S → T (transfer/chain scattering)
h = hparameters(s);                    % S → H (2-port only)
g = gparameters(s);                    % S → G (2-port only)

% Convert back
sRoundTrip = sparameters(z);           % Z → S (uses z.Impedance)
sCustomZ0 = sparameters(y, 75);        % Y → S with 75 Ohm reference
```

All parameter objects share the same interface: `.Parameters`, `.Frequencies`, `.Impedance`, `.NumPorts`.

### Port Count Limitations

| Parameter type | Port requirement |
|---------------|-----------------|
| S, Y, Z | N-port (any size) |
| ABCD, T | 2N-port only |
| H, G | 2-port only |

## Array-Based Conversions

Use when you need raw numeric arrays without object overhead.

```matlab
yData = s2y(s.Parameters, s.Impedance);
zData = s2z(s.Parameters, s.Impedance);
abcdData = s2abcd(s.Parameters, s.Impedance);
tData = s2t(s.Parameters);             % No Z0 needed for T-parameters
```

## Mixed-Mode (Differential/Common) S-Parameters

Convert 2N-port single-ended to N-port differential or common mode. Critical for high-speed serial link analysis.

```matlab
s4 = sparameters('connector.s4p');

% Differential mode (Sdd)
sdd = s2sdd(s4.Parameters);            % Default: option 1 port pairing

% Common mode (Scc)
scc = s2scc(s4.Parameters);

% Cross-mode (differential-to-common and vice versa)
sdc = s2sdc(s4.Parameters);
scd = s2scd(s4.Parameters);
```

### Port Ordering Options — The #1 Source of Mixed-Mode Errors

For a 4-port network, the option selects which physical ports form each differential pair:

| Option | Differential Pairs (4-port) | Description |
|--------|---------------------------|-------------|
| 1 (default) | (1,2) and (3,4) | Adjacent ports paired |
| 2 | (1,3) and (2,4) | First half paired with second half |
| 3 | (1,4) and (2,3) | Input ascending, output descending |

```matlab
sdd_opt2 = s2sdd(s4.Parameters, 2);   % Option 2 port ordering
```

**Gotcha:** Verify which option matches your VNA port numbering before converting to mixed-mode. Wrong port ordering produces subtly incorrect results that look plausible but are wrong.

**Gotcha:** Differential impedance = 2 × single-ended impedance. When wrapping `s2sdd` output in a `sparameters` object, double the reference impedance:
```matlab
sdd = s2sdd(s4.Parameters);
sDiff = sparameters(sdd, s4.Frequencies, 2*s4.Impedance);  % 100 Ohm for 50 Ohm single-ended
```

## Port Reduction and Reordering: `snp2smp`

Reduce N-port to M-port by selecting ports and terminating the rest.

**Gotcha:** Argument order is `snp2smp(s, portList, Z0)` — the port list comes **before** the termination impedance. Swapping them (e.g., `snp2smp(s, 50, [1 3])`) treats the scalar as a port index and errors.

```matlab
% Extract ports 1 and 3 from a 4-port, terminate ports 2 and 4 with 50 Ohm
s2 = snp2smp(s4, [1 3], 50);

% Swap ports of a 2-port
sSwapped = snp2smp(s, [2 1]);

% Terminate with different impedances per port
s2 = snp2smp(s4, [1 3], {50, 75, 50, 75});
```

## Transfer Function

```matlab
tf = s2tf(s);                          % Voltage transfer function (option 1, default)
tf = s2tf(s, 60, 75, 2);              % Zs=60, Zl=75, option 2: Vl/Vs
```

Options: 1 = Vl/Va (default), 2 = Vl/Vs, 3 = power-wave gain.

## Gotchas

1. **H and G parameters are 2-port only** -- `hparameters(s)` and `gparameters(s)` error for networks with more than 2 ports. ABCD and T require 2N-port (even number).
2. **Mixed-mode port ordering is the #1 error source** -- `s2sdd`, `s2scc`, `s2sdc`, `s2scd` accept an option argument (1, 2, or 3) for port pairing. Verify which option matches your VNA port numbering before converting -- wrong ordering produces subtly incorrect results that look plausible.
3. **Differential impedance = 2x single-ended** -- If single-ended Z0 is 50 Ohm, differential Z0 is 100 Ohm.
4. **`snp2smp` argument order: ports before impedance** -- `snp2smp(s, portList, Z0)`, not `snp2smp(s, Z0, portList)`. Swapping them treats the scalar as a port index and errors.

## Conventions

- Prefer object-based conversions over array-based — they track impedance automatically
- Always verify round-trip accuracy (S→Z→S) when conversion fidelity matters
- Use `rfparam` to extract individual parameters from any network parameter object

----

Copyright 2026 The MathWorks, Inc.

----
