---
name: matlab-optimize-antenna
description: Optimize antennas and arrays using MATLAB Antenna Toolbox SADEA and TR-SADEA algorithms. Supports catalog antenna/array optimization with built-in objectives (gain, bandwidth, SLL, F/B ratio) and constraints, plus custom evaluation functions for pcbStack and customAntenna. Use when the user wants to optimize, tune, improve, or search for the best antenna or array design parameters.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-or-array> <frequency> [objective]
metadata:
  author: MathWorks
  version: "1.0"
---

# Antenna and Array Optimization Skill

You are an expert RF and antenna engineer assisting a professional antenna engineer with design optimization. Use MATLAB Antenna Toolbox to optimize antennas and arrays using the built-in SADEA and TR-SADEA algorithms. The user is an antenna expert but not an optimization expert -- guide them through problem formulation and interpret results in antenna terms.

## When to Use

- User wants to optimize antenna dimensions for bandwidth, gain, or SLL
- User wants to find the best design parameters for a catalog antenna or array
- User asks about SADEA or surrogate-assisted optimization
- User wants to minimize sidelobe level or maximize front-to-back ratio
- User wants to optimize a pcbStack or customAntenna with a custom evaluation function

## When NOT to Use

- User wants to design (not optimize) an antenna — use `matlab-design-antenna`
- User wants to match an antenna to 50 ohm — use `matlab-design-matching-network`
- User wants beam steering (not optimization) — use `matlab-design-array`

## How SADEA Works (For Antenna Engineers)

SADEA (Surrogate model-Assisted Differential Evolution for Antenna optimization) builds a cheap mathematical approximation (surrogate) of your antenna's performance from a small number of real EM simulations. It then searches this surrogate model efficiently, only running actual EM simulations to verify promising candidates and refine the model. This is why it is well-suited for antenna work: full-wave EM solves are expensive, and SADEA minimizes how many you need.

The initial phase runs approximately m*N evaluations (N = number of design variables, m is calculated automatically) to build the surrogate model. This sampling phase is normal and expected -- it is not wasted computation. After that, each iteration refines the surrogate and proposes new candidates.

**TR-SADEA** (Training-Reduced SADEA) adds a local search mechanism that focuses on promising regions. It is better for high-dimensional problems (30+ design variables) such as large arrays, MIMO antennas, or reconfigurable surfaces. TR-SADEA requires the Statistics and Machine Learning Toolbox.

## First Step: Choose the Right Tier

Before writing code: (1) Is the antenna a catalog element? (2) Can the objective be expressed as a built-in string? If both YES → Tier 1. Only use Tier 2 for `customAntenna`/`pcbStack` or objectives that cannot be expressed with built-in strings. When the user specifies relationships between design variables (e.g., "no overlaps", "feed inside patch"), formulate them as `GeometricConstraints` — bounds constrain individual variables, geometric constraints enforce relationships.

## Two Optimization Approaches

Antenna Toolbox provides two tiers of optimization. Choose based on your antenna type and problem complexity.

### Tier 1: Built-in `optimize()` for Catalog Antennas and Arrays

Use this when your antenna is a catalog element (`dipole`, `patchMicrostrip`, `horn`, `yagiUda`, etc.) or a catalog array (`linearArray`, `rectangularArray`, etc.). Design variables are **property names** on the antenna or array object.

```matlab
% Start from a design()-generated antenna
ant = design(patchMicrostrip, 2.4e9);

% Optimize: objective + design variables + bounds
[optAnt, optinfo] = optimize(ant, 2.4e9, "maximizeGain", ...
    {'Length', 'Width'}, {0.02, 0.02; 0.06, 0.06}, ...
    Constraints={'S11 < -10'}, ...
    Iterations=50);
```

### Tier 2: OptimizerSADEA / OptimizerTRSADEA for Custom Designs

Use this when your antenna is a `customAntenna`, `pcbStack`, or when you need full control over the objective function. You write a **custom evaluation function** that creates the antenna from design variables, analyzes it, and returns a scalar fitness value. See `references/advanced-optimization.md` for detailed Tier 2 patterns.

```matlab
bounds = [lb1, lb2, lb3; ub1, ub2, ub3];
s = OptimizerSADEA(bounds);
s.CustomEvaluationFunction = @myEvalFunction;
s.optimizeWithPlots(50);    % run with live convergence plots
bestData = s.getBestMemberData;
```

## Problem Formulation Guide

The hardest step is translating an antenna requirement into an optimization problem. Use this decision tree:

| Primary Goal | Objective | Typical Constraints |
|-------------|-----------|-------------------|
| Highest possible gain | `"maximizeGain"` | `'S11 < -10'`, `'Area < 0.03'` |
| Widest impedance bandwidth | `"maximizeBandwidth"` | `'Gain > 5'` |
| Smallest physical size | `"minimizeArea"` | `'S11 < -10'`, `'Gain > 3'` |
| Best sidelobe suppression | `"maximizeSLL"` | `'S11 < -10'` |
| Best front-to-back ratio | `"frontToBackRatio"` | `'S11 < -10'` |
| Multiple competing goals | Custom evaluation function | Penalty-weighted in fitness |

When you have **one dominant goal** with side requirements, use a built-in objective string with string constraints. When you have **multiple competing goals** that must be carefully balanced, use a custom evaluation function with penalty weighting.

## Design Variables and Bounds

### Choosing Design Variables

Select properties that directly affect your performance metric. For catalog elements, use `properties(ant)` to list settable properties. Common choices per antenna type:

| Antenna Type | Typical Design Variables |
|-------------|------------------------|
| `patchMicrostrip` | `Length`, `Width`, `Height`, `FeedOffset` |
| `dipole` | `Length`, `Width` |
| `yagiUda` | `ReflectorLength`, `DirectorLength`, `ReflectorSpacing`, `DirectorSpacing` |
| `horn` | `FlareLength`, `FlareWidth`, `FlareHeight` |
| `linearArray` | `ElementSpacing` |
| `rectangularArray` | `RowSpacing`, `ColumnSpacing` |

**Keep design variables to 2-6 for catalog antennas.** More variables require more evaluations and longer optimization time.

### Setting Bounds

Start from `design()` dimensions and set bounds to +/-30-50% of those values. This keeps the search space physically reasonable.

```matlab
ant = design(patchMicrostrip, 2.4e9);
nominalLength = ant.Length;
nominalWidth = ant.Width;

% +/-40% bounds
lbLength = 0.6 * nominalLength;
ubLength = 1.4 * nominalLength;
lbWidth = 0.6 * nominalWidth;
ubWidth = 1.4 * nominalWidth;

[optAnt, optinfo] = optimize(ant, 2.4e9, "maximizeGain", ...
    {'Length', 'Width'}, {lbLength, lbWidth; ubLength, ubWidth}, ...
    Iterations=50);
```

Bounds are a **two-row cell array**: `{lower1, lower2, ...; upper1, upper2, ...}`. Each column corresponds to a design variable in the same order as `propertynames`.

**Bounds format warning:** Tier 1 `optimize()` uses a **cell array**. Tier 2 `OptimizerSADEA`/`OptimizerTRSADEA` uses a **numeric matrix** `[lb1, lb2, ...; ub1, ub2, ...]`. Do not mix.

**Constant components:** If a component has equal lower and upper bounds, remove it from design variables — it is a constant, not an optimization variable.

**Vector-valued properties** (like `FeedOffset = [x, y]`): specify bounds as vectors in the cell array.

```matlab
% FeedOffset is [x, y]
optimize(ant, freq, "maximizeGain", ...
    {'Length', 'Width', 'FeedOffset'}, ...
    {lbL, lbW, [0, 0]; ubL, ubW, [0.01, 0.005]}, ...
    Iterations=50);
```

## Built-in optimize() Reference

### Syntax

```matlab
optAnt = optimize(element, freq, objective, propertynames, bounds)
optAnt = optimize(___, Name=Value)
[optAnt, optinfo] = optimize(___)
```

### Built-in Objectives

| Objective String | Goal |
|-----------------|------|
| `"maximizeGain"` | Maximize peak gain |
| `"maximizeBandwidth"` | Maximize impedance bandwidth |
| `"minimizeBandwidth"` | Minimize bandwidth (narrowband filter antennas) |
| `"maximizeSLL"` | Maximize front-lobe to first-sidelobe ratio |
| `"frontToBackRatio"` | Maximize front-to-back ratio |
| `"minimizeArea"` | Minimize antenna footprint |

Custom function handles are also supported as objectives.

### String Constraints

```matlab
Constraints={'S11 < -10', 'Gain > 5', 'Area < 0.03'}
```

| Constraint | Units | Description |
|-----------|-------|-------------|
| `'S11 < value'` | dB | Maximum return loss |
| `'Gain > value'` | dBi | Minimum gain |
| `'F/B > value'` | dB | Minimum front-to-back ratio |
| `'SLL > value'` | dB | Minimum sidelobe level |
| `'Area < value'` | m^2 | Maximum antenna area |
| `'Volume < value'` | m^3 | Maximum antenna volume |

### Name-Value Arguments

| Name | Default | Description |
|------|---------|-------------|
| `Constraints` | none | Cell array of constraint strings |
| `Weights` | equal | Penalty weights for constraints (1-100) |
| `FrequencyRange` | +/-5% of freq | Frequency vector for bandwidth analysis |
| `ReferenceImpedance` | 50 | Reference impedance (ohms) |
| `MainLobeDirection` | [0, 90] | [azimuth, elevation] for gain evaluation (deg) |
| `Iterations` | 200 | Number of optimization iterations |
| `UseParallel` | false | Parallel evaluation (needs Parallel Computing Toolbox) |
| `EnableCoupling` | true | Mutual coupling in arrays |
| `EnableLog` | false | Print iteration details to command window |
| `GeometricConstraints` | none | Structure from `initGeomConstraint` |
| `UseAlgorithm` | `"SADEA"` | `"SADEA"` or `"TR-SADEA"` |

**`FrequencyRange` trap:** Default is +/-5% of the design frequency. For bandwidth optimization, always set this explicitly to your target band. If you want 2.4-2.5 GHz, pass `FrequencyRange=linspace(2.4e9, 2.5e9, 11)`.

### Array Optimization

**Array + element co-optimization:** If you need to optimize both array-level and element-level properties simultaneously, prefer Tier 2 with a custom evaluation function.

For arrays, set `MainLobeDirection` to the desired beam direction and consider disabling mutual coupling for faster (but less accurate) evaluation:

```matlab
la = design(linearArray, 2.4e9);
[optArr, optinfo] = optimize(la, 2.4e9, "maximizeGain", ...
    {'ElementSpacing'}, {0.03; 0.08}, ...
    MainLobeDirection=[0, 90], ...
    EnableCoupling=true, ...
    Iterations=50);
```

## Geometric Constraints

Geometric constraints enforce relationships between design variables (e.g., "length must be at least 3 times the width"). They use the `Ax <= b` matrix form from linear programming.

### Translation Recipe

**Step 1: Write the constraint in English.**
"The patch length must be at most 5 times the width."

**Step 2: Convert to a mathematical inequality.**
`Length <= 5 * Width`

**Step 3: Rearrange to standard form (... <= 0).**
`Length - 5*Width <= 0`

**Step 4: Map coefficients to design variable order.**
List your design variables with indices:

```
x1 = Length
x2 = Width
```

Read off coefficients: `A_row = [1, -5]`, `b = 0`.

### Worked Example

```matlab
designVars = {'Length', 'Width', 'Height'};
%              x1       x2       x3

% Constraint 1: Length <= 3*Width  -->  x1 - 3*x2 <= 0
% Constraint 2: Height <= Width    -->  -x2 + x3 <= 0

gc = initGeomConstraint;
gc.A = [1, -3, 0;     % row 1: x1 - 3*x2 <= 0
        0, -1, 1];    % row 2: -x2 + x3 <= 0
gc.b = [0; 0];

[optAnt, optinfo] = optimize(ant, freq, "maximizeGain", ...
    designVars, {lbL, lbW, lbH; ubL, ubW, ubH}, ...
    GeometricConstraints=gc, Iterations=50);
```

### Common Constraint Templates

| Constraint (English) | Standard Form | A Row | b |
|---------------------|--------------|-------|---|
| Length <= k*Width | Length - k*Width <= 0 | `[1, -k, 0, ...]` | `0` |
| Prop_i - Prop_j >= gap | -Prop_i + Prop_j <= -gap | `[..., -1, ..., 1, ...]` | `-gap` |
| Sum of two <= max | Prop_i + Prop_j <= max | `[..., 1, ..., 1, ...]` | `max` |

### Nonlinear Geometric Constraints

For constraints like `Length * Width <= maxArea`, use a **named function** (not anonymous):

```matlab
gc = initGeomConstraint;
gc.nlcon = @areaConstraint;
gc.nrlv = [1, 1];    % relevance vector: MUST match total number of design variables
                     % Use 1 for participating, 0 for non-participating
                     % e.g., 5 vars, only 1st and 3rd participate: [1, 0, 1, 0, 0]

% Named function -- anonymous functions are NOT supported
function [c, ceq] = areaConstraint(x)
    c = x(1)*x(2) - 0.04;    % c <= 0: area must not exceed 0.04 m^2
    ceq = 0;                  % must return nonempty (use 0, not [])
    % For equality: set c = -1 (ignored) and ceq = x(1)*x(2) - 0.04
end
```

**Three gotchas that will cause errors:**

1. **Must use a named function handle** -- `@(x) deal(...)` throws *"must not be an anonymous function"*. Define a separate function and pass `@functionName`.
2. **Must set `gc.nrlv`** -- a vector of ones/zeros indicating which design variables the constraint depends on. Omitting it throws *"Either nlcon or nrlv is empty"*.
3. **`ceq` must be nonempty** -- return `ceq = 0` (not `[]`). Empty `ceq` throws *"expected function handle to return output 'ceq' as nonempty"*.

The function returns `[c, ceq]` following the `fmincon` convention: `c <= 0` for inequalities, `ceq = 0` for equalities.

### Validation Gotcha

If the optimizer throws *"Constraints might be too stringent or invalid"*, verify:
1. The initial antenna dimensions satisfy `A * x0 <= b` (where `x0` is the starting design).
2. Some region within your bounds satisfies all constraints.
3. Column indices in `A` match the order of design variables in `propertynames`.

## Custom Evaluation Functions (Tier 2)

Use `OptimizerSADEA` or `OptimizerTRSADEA` when you need full control over the objective. This is the path for `customAntenna` and `pcbStack` optimization.

### Evaluation Function Pattern

The function takes a vector of design variables and returns a **scalar fitness** value. SADEA **minimizes** fitness, so negate metrics you want to maximize.

**File requirement:** The evaluation function must be saved as a separate `.m` file on the MATLAB path. It cannot be defined inline in scripts or the command window.

```matlab
function fitness = evaluateAntenna(x)
    % x = [designVar1, designVar2, ...]
    freq = 2.4e9;

    % 1. Create antenna from design variables
    try
        ant = createMyAntenna(x);
    catch
        fitness = 1e6;    % large penalty for invalid geometry
        return;
    end

    % 2. Compute objective (negate to maximize)
    try
        gain = pattern(ant, freq, 0, 90, Type="realizedgain");
        objective = -gain;    % negate: SADEA minimizes
    catch
        objective = 1e6;
        return;
    end

    % 3. Compute constraint violations
    s = sparameters(ant, linspace(freq*0.9, freq*1.1, 11));
    s11_max = max(20*log10(abs(rfparam(s, 1, 1))));
    constraint = max(s11_max - (-10), 0);    % zero if S11 < -10 dB

    % 4. Combine: fitness = objective + penalty * constraint
    fitness = objective + 100 * constraint;
end
```

**Key pattern:** Wrap antenna creation and analysis in `try/catch`. Return a large penalty (`1e6`) for geometries that fail to mesh or analyze. This prevents the optimizer from crashing on invalid designs.

**Manual meshing:** Unlike catalog antennas (which auto-mesh), `customAntenna` objects require explicit `mesh(ant, MaxEdgeLength=lambda/8)` after creation.

**Interpolation sweep for faster optimization:** Optimization loops run repeated frequency sweeps. For substrate-backed antennas, use interpolation sweep to reduce compute time:
```matlab
try
    s = sparameters(ant, freqRange, SweepOption="interp");
catch
    s = sparameters(ant, freqRange);
end
```

**Geometry validity debugging:** If many evaluations return the penalty value, temporarily remove `try/catch` and run the function directly — the error message reveals which geometry relationship is violated. Then add geometric constraints to prevent it.

### Running the Optimizer

```matlab
% Define bounds: [lb; ub] for each design variable
bounds = [lb1, lb2, lb3; ub1, ub2, ub3];

% Create optimizer
s = OptimizerSADEA(bounds);
s.CustomEvaluationFunction = @evaluateAntenna;

% Optional: configure
setMaxFunctionEvaluations(s, 200);
defineInitialPopulation(s, 10);

% Run with live plots
s.optimizeWithPlots(50);    % 50 iterations

% Or run without plots (faster, use EnableLog for text output)
% s.EnableLog = true;
% s.optimize(50);
```

Use `optimizeWithPlots()` for live monitoring (Population Diversity + Convergence Trend plots). Use `optimize()` for headless runs with optional text logging via `EnableLog`.

### TR-SADEA for High-Dimensional Problems

For 30+ design variables, switch to TR-SADEA:

```matlab
s = OptimizerTRSADEA(bounds);
s.CustomEvaluationFunction = @evaluateAntenna;
s.optimizeWithPlots(100);
```

TR-SADEA requires the Statistics and Machine Learning Toolbox.

## Result Extraction and Validation

### Built-in optimize()

`optimize()` returns the optimized antenna and an `OptimizerSADEA` info object. It also auto-generates convergence plots (Population Diversity + Convergence Trend).

```matlab
[optAnt, optinfo] = optimize(ant, freq, "maximizeGain", vars, bounds, ...
    Iterations=50);

% Inspect optimizer results
bestData = optinfo.getBestMemberData;
fprintf("Best design variables: %s\n", mat2str(bestData.member, 4));
fprintf("Best fitness: %.4f\n", bestData.fitness);
fprintf("Converged: %d\n", optinfo.isConverged);
fprintf("Total EM evaluations: %d\n", optinfo.getNumberOfEvaluations);

% Post-optimization convergence plot
figure;
optinfo.showConvergenceTrend;
```

**Fitness sign convention:** For maximization objectives (gain, bandwidth), SADEA negates the value internally. The fitness plot trends **downward** as the objective improves.

### OptimizerSADEA / OptimizerTRSADEA

```matlab
bestData = s.getBestMemberData;
optimizedVars = bestData.member;       % best design variable values
bestFitness   = bestData.fitness;      % best fitness value
bestIter      = bestData.bestIterationId;

fprintf("Converged: %d\n", s.isConverged);
fprintf("Total evaluations: %d\n", s.getNumberOfEvaluations);

figure;
s.showConvergenceTrend;
```

### Post-Optimization Validation Checklist

Always verify the optimized design independently -- do not rely solely on the optimizer's fitness value.

```matlab
% 1. Visualize the optimized antenna
figure;
show(optAnt);

% 2. Full impedance sweep over the target band
freqRange = linspace(fmin, fmax, 51);
figure;
impedance(optAnt, freqRange);

% 3. S-parameters
figure;
sParams = sparameters(optAnt, freqRange);
rfplot(sParams);

% 4. Radiation pattern
figure;
pattern(optAnt, freq);

% 5. Report key metrics
Z = impedance(optAnt, freq);
fprintf("Impedance: %.2f + j%.2f ohm\n", real(Z), imag(Z));
bw = bandwidth(optAnt, freq, 50, -10);
fprintf("Bandwidth (-10 dB): %.2f MHz\n", bw/1e6);
```

For Tier 2, rebuild the antenna from the best design variables and run the same checks:

```matlab
bestVars = s.getBestMemberData.member;
optAnt = createMyAntenna(bestVars);
% ... run validation as above
```

## Iteration Guidelines

| Design Variables | Initial Sampling | Suggested Iterations | Expected Evaluations |
|-----------------|-----------------|---------------------|---------------------|
| 2-3 | ~10-30 | 30-50 | 40-80 |
| 4-6 | ~20-40 | 50-100 | 70-140 |
| 7-15 | ~30-60 | 100-200 | 130-260 |
| 16-30 | ~50-120 | 200+ (use TR-SADEA) | 250+ |

Not recommended to use more than 50 Initial Sampling for SADEA. These are rough estimates. Complex antennas (substrate, fine mesh) take longer per evaluation. Start with fewer iterations, inspect convergence, and continue if needed with additional iterations.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- The `optimize()` function auto-generates convergence plots -- do not add titles to these.
- **Do** add titles to manual `plot()` figures.
- Use `fprintf` for formatted numerical output.

## Guidelines

- **Do not over-explain** optimization theory. Give just enough for the antenna engineer to make good decisions.
- **Always start from `design()`** to get a physically reasonable initial antenna before optimizing. If `design()` fails, estimate from wavelength/physics. If that also fails, ask the user for initial dimensions.
- **Default to SADEA.** Only suggest TR-SADEA for 30+ design variables or when the user has the Statistics toolbox. If TR-SADEA converges to an unsatisfactory result, try SADEA for potentially better global search.
- **Set `FrequencyRange` explicitly** for any bandwidth-related optimization. The +/-5% default may not match the user's target band.
- **Wrap custom evaluation functions in `try/catch`** (return large penalties for invalid geometries) and negate metrics for maximization -- SADEA minimizes.
- **Check geometric constraint compatibility** with bounds and initial design if the optimizer reports constraints are too stringent.
- **Recommend `optimizeWithPlots()`** over `optimize()` for the Optimizer objects so the user can monitor convergence.
- **Always validate** the optimized design with a full analysis sweep and report the number of EM evaluations.

----

Copyright 2026 The MathWorks, Inc.
