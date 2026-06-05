---
name: matlab-fit-simbiology-model
description: "Fit SimBiology model parameters to data — fitproblem, population NLME, virtual patients, and NCA. Use when asked to fit, estimate, calibrate, or compute PK metrics."
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# Fit SimBiology Models

Estimate parameters from data using `fitproblem`, fit population models
with NLME, generate virtual patients, and compute NCA metrics.

## When to Use

- "fit", "estimate", "calibrate" model parameters
- Parameter estimation from experimental/observed data
- Population PK/PD, NLME, mixed effects, inter-individual variability
- Virtual patients, virtual cohorts
- NCA, AUC, Cmax, Tmax, half-life, clearance
- Keywords: "fit", "estimate", "calibrate", "population", "NCA", "AUC"

## When NOT to Use

- Model construction or diagram (use `matlab-build-simbiology-model`)
- Simulation without fitting (use `matlab-simulate-simbiology-model`)
- Sensitivity analysis (use `matlab-simulate-simbiology-model`)

## Must-Follow Rules

### 1. Use `fitproblem` for parameter estimation

Always use `fitproblem` instead of calling `sbiofit` or `sbiofitmixed`
directly. `fitproblem` provides a unified, declarative interface:
```matlab
prob = fitproblem;
prob.Model = model;
prob.Data = data;
prob.ResponseMap = "Species = DataColumn";
prob.Estimated = estimatedInfo({'param'}, 'Bounds', [lo hi]);
results = fit(prob);
```
Do NOT call `sbiofit(model, data, ...)` or `sbiofitmixed(model, data, ...)`
directly — their positional argument signatures are error-prone.

### 2. Fitting requires `groupedData`, NOT a plain table

Always wrap data:
```matlab
data = groupedData(table(...));
data.Properties.IndependentVariableName = 'Time';
```

### 3. `ResponseMap` maps model outputs to data columns

Format is always `"ModelOutput = DataColumnName"`:

```matlab
% Single compartment — use species name on the left
prob.ResponseMap = "Drug = DrugConc";

% Multi-compartment — use qualified name to disambiguate
prob.ResponseMap = "Central.Drug = DrugConc";

% When species name matches data column name, still use the = format
prob.ResponseMap = "Drug = Drug";
```

Use the unqualified species name unless the same species name exists
in multiple compartments (then qualify with `Compartment.Species`).

### 4. Always set bounds

Prevent non-physical values (negative rates, etc.):
```matlab
estimParams = estimatedInfo({'ke','ka'}, ...
    'InitialValue', [0.2, 1.0], ...
    'Bounds', [0.01 1; 0.1 5]);
```

### 5. Use log transform for rate constants

Parameters spanning orders of magnitude (clearances, rate constants)
benefit from log-transform estimation. Set `.Transform` after creation:
```matlab
ei = estimatedInfo({'ke','ka'}, 'InitialValue', [0.1, 0.5], 'Bounds', [0.01 1; 0.1 5]);
ei(1).Transform = 'log';
ei(2).Transform = 'log';
```

Alternative: use `'log(param)'` name syntax (equivalent result):
```matlab
ei = estimatedInfo({'log(ke)','log(ka)'}, 'InitialValue', [0.1, 0.5], 'Bounds', [0.01 1; 0.1 5]);
```

**Important:** `InitialValue` and `Bounds` are always in the
**untransformed** (natural) domain. Do NOT pass `log(value)`.

Available transforms: `'log'`, `'logit'`, `'probit'`

Do NOT pass `'Transform'` as a name-value pair to the `estimatedInfo`
constructor — it errors. Always set the `.Transform` property after.

### 6. Error models for population fitting

Choose the error model that matches the noise structure:
- `'constant'` — absolute noise uniform
- `'proportional'` — noise scales with magnitude (most PK data)
- `'combined'` — both constant and proportional
- `'exponential'` — log-normal residual

### 7. NCA requires `sbioncaoptions` object

Do not use name-value pairs. Column names are camelCase.
EVDose column uses `NaN` for non-dose rows.

## Decision Table

| Scenario | Approach |
|----------|----------|
| Single subject or pooled fit | `fitproblem` with `FitFunction="sbiofit"` |
| Individual fits per subject | `fitproblem` with `Pooled=false` |
| Population NLME (IIV, random effects) | `fitproblem` with `FitFunction="sbiofitmixed"` |
| Model-independent PK metrics | `sbionca` |

## `fitproblem` Workflow (Preferred)

Use `fitproblem` for all parameter estimation. It provides a unified,
declarative interface that replaces direct calls to `sbiofit`/`sbiofitmixed`:

```matlab
% 1. Prepare data
data = groupedData(table(tSample, yData, 'VariableNames', {'Time','Drug'}));
data.Properties.IndependentVariableName = 'Time';

% 2. Define parameters with bounds
estimParams = estimatedInfo({'ke','ka'}, ...
    'InitialValue', [0.2, 1.0], ...
    'Bounds', [0.01 1; 0.1 5]);

% 3. Build the fit problem
prob = fitproblem;
prob.Model = model;
prob.Data = data;
prob.ResponseMap = "Drug = Drug";
prob.Estimated = estimParams;
prob.Doses = dose;                  % optional
prob.FunctionName = 'scattersearch';
prob.ProgressPlot = true;           % show live progress

% 4. Fit
results = fit(prob);

% 5. Inspect
disp(results.ParameterEstimates);
plot(results);
```

### Key `fitproblem` properties

| Property | Purpose |
|----------|---------|
| `Model` | The SimBiology model object |
| `Data` | `groupedData` table |
| `Estimated` | `estimatedInfo` object (**not** `EstimatedParameters`) |
| `ResponseMap` | Maps model species to data columns |
| `Doses` | Dose object(s) (**not** `Dose`) |
| `FitFunction` | `"sbiofit"` (default) or `"sbiofitmixed"` |
| `FunctionName` | Algorithm: `'scattersearch'`, `'nlinfit'`, `'fminsearch'`, `'lsqnonlin'`, `'particleswarm'` |
| `ProgressPlot` | `true` to show live fitting progress |
| `UseParallel` | `true` for parallel evaluation |
| `Pooled` | `true`/`false`/`"auto"` (sbiofit only) |
| `ErrorModel` | `"constant"`, `"proportional"`, `"combined"`, `"exponential"` |
| `Variants` | Variants to apply during fitting |

**Common property name mistakes:** `prob.Estimated` (not `EstimatedParameters`),
`prob.Doses` (not `Dose`), `prob.FunctionName` (not `Algorithm` or `Method`).

### Estimation algorithms

| Method | Use Case |
|--------|----------|
| `'scattersearch'` | Built-in global search, no extra toolbox — **start here** |
| `'nlinfit'` | Default local; smooth problems |
| `'lsqnonlin'` | Bounded least squares (Optimization Toolbox) |
| `'fminsearch'` | Derivative-free, simple problems |
| `'particleswarm'` | Global search (Global Optimization Toolbox) |

### Dosing from multi-subject data

When subjects receive different doses, use `createDoses` to extract
per-subject dose objects from the data. The dose column must have `NaN`
on non-dosing rows:

```matlab
% Data format: dose amount only at administration time, NaN elsewhere
%   ID  Time  Dose  DrugConc  Group
%   1   0     50    0         LowDose
%   1   1     NaN   2.05      LowDose
%   ...
%   3   0     200   0         HighDose

% Create template dose targeting the depot species
tempDose = sbiodose('StudyDose');
tempDose.TargetName = 'Depot.Drug';   % match your model's dose target

% Extract per-subject doses from groupedData
doseArray = createDoses(gData, 'Dose', '', tempDose);

% Pass to fitproblem
prob.Doses = doseArray;
```

**Critical:** If all rows have the dose value (not just dosing times),
`createDoses` will treat every row as a dose event. Use `NaN` on
non-dosing rows.

### Population fitting (pooled vs individual)

```matlab
data.Properties.GroupVariableName = 'SubjectID';

% Pooled — one parameter set for all
prob.Pooled = true;

% Individual — separate per subject
prob.Pooled = false;
```

### Category-based pooling (per-group estimates)

To estimate parameters separately per category (e.g., dose group), use
`CategoryVariableName` on the `estimatedInfo` object — **not** on
`fitproblem` or `sbiofit`:

```matlab
estimParams = estimatedInfo({'ke'}, 'InitialValue', 0.1, 'Bounds', [0.01 1]);
estimParams.CategoryVariableName = 'DoseGroup';  % column in data table
% Do NOT set prob.Pooled — leave it at the default
```

**Warning:** Do NOT set `prob.Pooled` when using `CategoryVariableName`.
Setting `Pooled=false` triggers per-subject individual fitting that
**ignores** `CategoryVariableName` (MATLAB issues a warning). Leave
`Pooled` unset to let the category-based pooling work correctly.

## NLME Population Fitting

For inter-individual variability and random effects estimation,
set `FitFunction` to `"sbiofitmixed"`:

```matlab
% 1. Load & tag grouped data
data = groupedData(readtable('pop_pk_data.csv'));
data.Properties.IndependentVariableName = 'Time';
data.Properties.GroupVariableName = 'SubjectID';

% 2. Define parameters (Bounds ignored by sbiofitmixed — use InitialValue only)
estimParams = estimatedInfo({'CL','Vd','ka'}, ...
    'InitialValue', [5, 50, 1.2]);

% 3. Build the fit problem
prob = fitproblem;
prob.Model = model;
prob.Data = data;
prob.ResponseMap = "DrugConc = Concentration";
prob.Estimated = estimParams;
prob.FitFunction = "sbiofitmixed";
prob.ErrorModel = "proportional";
prob.ProgressPlot = true;

% 4. Fit
results = fit(prob);

% 5. Inspect
results.FixedEffects
results.RandomEffectCovarianceMatrix
results.IndividualParameterEstimates
```

### When to use NLME vs sbiofit

| Criterion | `FitFunction="sbiofit"` | `FitFunction="sbiofitmixed"` |
|-----------|-----------|----------------|
| Single subject | Yes | |
| Multiple subjects, no IIV | Yes (pooled) | |
| Inter-individual variability | | Yes |
| Random effects estimation | | Yes |
| Covariate modeling | | Yes |
| Small datasets (< 5 subjects) | Yes | May not converge |
| Bounds on parameters | Yes (enforced) | **Ignored** — use good InitialValue instead |

## Virtual Patient Generation

### From assumed distributions

```matlab
rng(123);
nPat = 100;
ke_pop = lognrnd(log(0.1), 0.3, nPat, 1);
ka_pop = lognrnd(log(0.5), 0.25, nPat, 1);
paramMatrix = [ke_pop, ka_pop];

simfun = createSimFunction(model, {'ke','ka'}, {'Drug'}, []);
results = simfun(paramMatrix, 24);
```

### From NLME results

```matlab
mu    = results.FixedEffects;
omega = results.RandomEffectCovarianceMatrix;
rng(42);
nVP = 200;
eta = mvnrnd(zeros(size(mu)), omega, nVP);
vpParams = mu .* exp(eta);   % log-normal parameterization
simfun = createSimFunction(model, {'CL','Vd','ka'}, {'Cp'}, []);
vpSim = simfun(vpParams, 48);
```

## Non-Compartmental Analysis (NCA)

### From simulation output

Use explicit `OutputTimes` to ensure sufficient time-resolution for NCA
(the default solver output may have too few points near Cmax):

```matlab
cs = getconfigset(m, 'active');
cs.SolverOptions.OutputTimes = linspace(0, 24, 200);

[t, x, names] = sbiosimulate(m);
drugIdx = find(strcmp(names, 'Drug'));
Vd = sbioselect(m, 'Type', 'parameter', 'Name', 'Vd');
conc = x(:, drugIdx) ./ Vd.Value;
evDose = NaN(size(t)); evDose(1) = 100;
data = table(t, conc, evDose, 'VariableNames', {'Time','Concentration','EVDose'});

opt = sbioncaoptions;
opt.concentrationColumnName = 'Concentration';
opt.timeColumnName = 'Time';
opt.EVDoseColumnName = 'EVDose';
opt.AdministrationRoute = 'ExtraVascular';
ncaResults = sbionca(data, opt);
```

### Administration routes

| Route | Dose column | Extra config |
|-------|-------------|--------------|
| `'ExtraVascular'` | `opt.EVDoseColumnName` | — |
| `'IVBolus'` | `opt.IVDoseColumnName` | — |
| `'IVInfusion'` | `opt.IVDoseColumnName` | `opt.infusionRateColumnName` |

### Key NCA metrics

**All metric names use underscores** (e.g., `C_max` not `Cmax`):

| Metric | Description |
|--------|-------------|
| `AUC_0_last` | Area under curve (0 to last time) |
| `AUC_infinity` | AUC extrapolated to infinity |
| `C_max` | Maximum observed concentration |
| `T_max` | Time of Cmax |
| `T_half` | Terminal elimination half-life |
| `CL` | Clearance (dose / AUC) |
| `V_z` | Volume of distribution (terminal) |
| `MRT` | Mean residence time |

### Multi-subject NCA

```matlab
data.Properties.GroupVariableName = 'SubjectID';
opt.groupColumnName = 'SubjectID';
ncaResults = sbionca(data, opt);
```

## Confidence Intervals and Profile Likelihood

After fitting, compute confidence intervals with `sbioparameterci`:

### Gaussian (asymptotic) CI — fast, default

```matlab
ciResults = sbioparameterci(fitResults);
disp(ciResults.Results);  % table: Name (cell), Estimate, Bounds, ConfidenceInterval (Nx2 double), Status (categorical)
plot(ciResults);
```

**Column types in `.Results` table:**
- `Name` — cell array of char (`Results.Name{i}`)
- `ConfidenceInterval` — Nx2 double matrix (`Results.ConfidenceInterval(i,:)`)
- `Status` — **categorical** (`Results.Status(i)`, NOT `{i}`)

### Profile likelihood CI — more accurate for nonlinear models

```matlab
ciPL = sbioparameterci(fitResults, 'Type', 'ProfileLikelihood');
disp(ciPL.Results);
plot(ciPL);  % shows profile likelihood curves with CI bounds
```

The `plot` method on a profile likelihood result automatically shows the
log-likelihood profile curves. No extra flags needed.

### Options

```matlab
% Custom confidence level (default Alpha=0.05 → 95% CI)
ci90 = sbioparameterci(fitResults, 'Type', 'ProfileLikelihood', 'Alpha', 0.10);
```

| Type | Speed | Accuracy | Use when |
|------|-------|----------|----------|
| `'Gaussian'` (default) | Fast | Approximate | Quick check, well-behaved problems |
| `'ProfileLikelihood'` | Slower | Exact for nonlinear | Final results, parameter identifiability |

## Conventions

- **Species names must differ from compartment names.** SimBiology errors if a species shares the same name as its parent compartment (e.g., species `Depot` inside compartment `Depot`). Use distinct names: compartment `Depot` with species `DrugDepot`, or compartment `GI` with species `Drug`.
- **Units required when compartment Volume != 1:** When a compartment has `Value` (capacity) set to something other than 1 (e.g., `Vd=50`), you **must** specify units on all components (`'liter'`, `'milligram'`, `'1/hour'`, etc.), enable `DimensionalAnalysis = true` in the configset, **and** set `VariableUnits` on the `groupedData` table (e.g., `data.Properties.VariableUnits = {'hour','milligram'}`). Without units, the fitting engine produces Inf/NaN values during optimization. If you don't need volume-based concentration, set compartment `Value = 1` instead (pure amount-based, no units needed).
- **Loading `.sbproj` files:** `sbioloadproject` returns a struct with the model name as field — extract dynamically:
  ```matlab
  proj = sbioloadproject('file.sbproj');
  fn = fieldnames(proj);
  model = proj.(fn{1});
  ```
- **Extracting simulation data for fitting:** Use `selectbyname` — it handles qualified names automatically: `result = selectbyname(sbiosimulate(m), 'Drug'); drugVals = result.Data; t = result.Time;`. The three-output form `[t, x, names] = sbiosimulate(m)` returns **qualified** names (e.g., `'Central.Drug'`), so use `contains(names, 'Drug')` or the full qualified name with `strcmp`. When sampling at specific times, remove duplicate time points first (ODE solvers may produce them), then interpolate:
  ```matlab
  [tU, ia] = unique(result.Time);
  yAtSamples = interp1(tU, result.Data(ia), tSample);
  ```
- Start with `'scattersearch'` if unsure about parameter landscape
- Use `'log'` transform for parameters spanning orders of magnitude (see Rule 5)
- Use `sbioaccelerate(model)` before fitting for speed (requires MEX compiler; if unavailable, skip — fitting still works, just slower)
- Set `cs.MaximumWallClock = 60` before fitting — bad parameter guesses can make individual simulations hang; this configset property stops any single simulation exceeding the time limit
- Set `prob.ProgressPlot = true` for long-running fits so the user sees progress
- Check fit quality with `plot(results)` and `results.ParameterEstimates`
- Compute confidence intervals with `sbioparameterci` (see above)
- Pass **model objects** (not UUID strings) to fitting functions
- Do NOT call `sbiofit`/`sbiofitmixed`/`sbionlmefit` directly — use `fitproblem`

## References

Load on demand for detailed guidance:

- `references/nca-analysis-guidance.md` — full NCA patterns, IV infusion, metrics interpretation


----

Copyright 2026 The MathWorks, Inc.

----
