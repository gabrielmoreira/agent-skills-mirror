---
name: external-model-validation
description: Use when validating an existing prognostic risk signature on an external bulk expression cohort with survival outcomes, producing risk scores, Kaplan-Meier survival curves, risk distribution plots, heatmap, and time-dependent ROC curves. NOT for: model training, feature selection, nomogram construction, calibration analysis, or single-cell data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# External Model Validation

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need to run the analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --exp_file ... --cli_file ... --model_file ...` |
| **Need workflow order or output generation steps** | `scripts/run_analysis.R` | Review the 4-step orchestration of loading, scoring, plotting, and metadata export |
| **Need risk score or sample matching logic** | `scripts/functions.R` | Inspect core data preparation and validation logic |
| **Need output writing or metadata export details** | `scripts/io.R` | Inspect output directory creation and file-writing helpers |
| **Need plotting implementation details** | `scripts/plotting.R` | Inspect Kaplan-Meier, risk, heatmap, and ROC plot generation |
| **Need input validation, logging, timeout, or dependency logic** | `scripts/utils.R` | Review validation helpers, `SKILL_*` error handling, logging, and runtime safeguards |
| **Need statistical assumptions or method details** | `references/algorithm.md` | Risk score formula, group cutoff, survival analysis, ROC, and heatmap assumptions |
| **Need troubleshooting help** | `references/troubleshooting.md` | Common failures, warnings, and concrete fixes |
| **Need CLI usage examples** | `references/cli-guide.md` | Parameter explanations, examples, and command patterns |
| **Need expected outputs or benchmark run** | `references/baseline-run.md` | Real-data baseline command, runtime, memory checkpoints, and output inventory |
| **Need test inputs** | `tests/data/` | Example expression, clinical, and model files for validation |
| **Need to refresh the retained example output** | `tests/refresh_example_output.R` | Rebuild `tests/output/` with `--overwrite` using the bundled test data |

---

## Usage

```bash
Rscript scripts/main.R \
  --exp_file ./expression.csv \
  --cli_file ./clinical.csv \
  --model_file ./model.csv \
  --output_dir ./output/ \
  --time_unit month \
  --seed 42
```

---

## Arguments

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-e` | `--exp_file` | character | **required** | Expression matrix CSV with genes as rows and samples as columns |
| `-c` | `--cli_file` | character | **required** | Clinical CSV with sample IDs as row names and `OS`, `OS.time` columns |
| `-m` | `--model_file` | character | **required** | Model coefficient CSV with `Gene` and `Coef` columns |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
|  | `--overwrite` | flag | `FALSE` | Allow writing into a non-empty output directory |
| `-u` | `--time_unit` | character | `month` | Survival time unit in input clinical file: `day`, `month`, `year` |
|  | `--col_high` | character | `#E64B35` | Color for high-risk samples |
|  | `--col_low` | character | `#4DBBD5` | Color for low-risk samples |
|  | `--roc_cols` | character | `#E64B35,#00A087,#3C5488` | Comma-separated colors for ROC curves |
|  | `--roc_times` | character | `1,3,5` | Comma-separated ROC time points in years |
|  | `--roc_pos` | character | `bottomright` | ROC legend position |
|  | `--km_breaks` | integer | `0` | Kaplan-Meier x-axis break in years; `0` selects automatically |
| `-s` | `--seed` | integer | `42` | Random seed for reproducibility |
|  | `--timeout_seconds` | integer | `3600` | Elapsed timeout limit in seconds |

---

## When to Use

- You already have a fixed prognostic gene signature and coefficients.
- You need to test that model on an independent cohort with bulk expression and survival data.
- You want standard outputs for external validation: risk table, Kaplan-Meier curve, risk score plot, survival status plot, expression heatmap, and time-dependent ROC.

## When Not to Use

- Do not use this Skill to train or re-fit a prognostic model.
- Do not use it for nomogram construction, calibration curves, DCA, or diagnostic classification.
- Do not use it for single-cell expression matrices or cohorts without survival endpoints.
- Do not use identifiable patient data without de-identification and local compliance approval.

## Research Use Notice

- This Skill is for research and validation workflows only.
- It does not provide diagnosis, treatment recommendations, or clinical decision support.
- Use de-identified data and follow IRB, ethics, and data-use requirements before running on human cohorts.

---

## Input Format

### Expression Matrix (`exp_file`)

CSV with genes as rows and samples as columns. The first column must contain gene identifiers.

```csv
"","Sample_1","Sample_2","Sample_3"
"TSPAN6",3.87,4.54,8.12
"TNMD",9.98,5.86,5.38
"DPM1",7.95,6.11,5.41
```

### Clinical File (`cli_file`)

CSV with sample IDs as row names and at least `OS` and `OS.time` columns.

```csv
,Age,OS,OS.time
Sample_1,59,0,133.5
Sample_2,60,0,49.13
Sample_3,59,1,22.40
```

- `OS` must use `0/1` encoding.
- `OS.time` must be positive and interpretable under `--time_unit`.

### Model Coefficient File (`model_file`)

CSV with two required columns: `Gene` and `Coef`.

```csv
Gene,Coef
TSPAN6,-0.25
TNMD,0.15
DPM1,0.32
```

---

## Output Files

| File | Description |
|------|-------------|
| `data/risk_data.rds` | Serialized analysis dataset containing survival data, model gene expression, risk scores, and risk groups |
| `table/out_varifyRisk.txt` | Tab-delimited risk table for all matched samples |
| `plot/out_varifySurv.pdf` | Kaplan-Meier survival curve with risk table |
| `plot/out_varify.riskScore.pdf` | Ordered risk score plot |
| `plot/out_varify.survStat.pdf` | Survival status plot |
| `plot/out_varify.heatmap.pdf` | Heatmap of model genes across ordered samples |
| `plot/out_varify.ROC.pdf` | Time-dependent ROC curve PDF |
| `analysis.log` | Runtime log including memory checkpoints and processing steps |
| `run_parameters.tsv` | Exact parameter values used for the run |
| `session_info.txt` | R version, platform, and package session information |

---

## Workflow

### Step 1: Validate Inputs
- Check required files and CSV extensions.
- Validate color strings, timeout, seed, KM break setting, and time unit choice.
- Parse `--roc_times` and `--roc_cols`.

### Step 2: Build Matched Validation Dataset
- Read expression, clinical, and model files.
- Match samples shared by expression columns and clinical row names.
- Check all model genes exist in the expression matrix.
- Remove incomplete cases before downstream analysis.

### Step 3: Calculate Risk Scores and Groups
- Compute risk scores with the supplied linear predictor.
- Convert follow-up time into years.
- Split patients into `low` and `high` groups using the median risk score.

### Step 4: Generate Validation Outputs
- Save the full risk table and RDS object.
- Produce Kaplan-Meier, risk score, survival status, heatmap, and time-dependent ROC plots.
- Save session metadata and exact run parameters.

---

## Methods

### Risk Score Formula

For sample `i`, the Skill computes:

```text
riskScore_i = sum(expression_ig * coefficient_g)
```

using all genes listed in `model_file`.

### Risk Stratification

- Samples are ordered by `riskScore`.
- The median risk score is used as the cutoff.
- Samples with scores above the median are labeled `high`; the others are labeled `low`.

### Survival Analysis

- Kaplan-Meier curves are fit with `survival::survfit`.
- Group difference is shown with the default log-rank p-value in `survminer::ggsurvplot`.

### Time-Dependent ROC

- ROC analysis is performed with `timeROC::timeROC` using follow-up time in years.
- All `--roc_times` values must be smaller than the maximum observed follow-up time.

---

## Examples

### Basic Usage

```bash
Rscript scripts/main.R \
  -e tests/data/BRCA_data.csv \
  -c tests/data/BRCA_clinic.csv \
  -m tests/data/BRCA_coef.csv \
  -o ./output/
```

### Input Follow-up Recorded in Days

```bash
Rscript scripts/main.R \
  -e expression.csv \
  -c clinical.csv \
  -m model.csv \
  -o ./output \
  -u day \
  --roc_times 1,2,3
```

### Custom Plot Colors and ROC Settings

```bash
Rscript scripts/main.R \
  -e expression.csv \
  -c clinical.csv \
  -m model.csv \
  -o ./output \
  --col_high '#B2182B' \
  --col_low '#2166AC' \
  --roc_cols '#B2182B,#4D9221,#2166AC' \
  --roc_pos topleft \
  --km_breaks 2
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input path is missing or wrong | Check file path and permissions |
| `SKILL_MISSING_COLUMNS` | Clinical or model file lacks required columns | Ensure `OS`, `OS.time`, `Gene`, and `Coef` exist |
| `SKILL_SAMPLE_MISMATCH` | No overlapping samples between expression and clinical data | Align sample IDs exactly |
| `SKILL_EMPTY_DATA` | An input file is empty after loading | Verify the CSV contains at least one row and one column of usable data |
| `SKILL_INVALID_DATA` | Duplicate genes, empty data, non-numeric coefficients, or invalid survival values | Clean input tables and verify formats |
| `SKILL_ANALYSIS_ERROR` | Risk groups collapse or event count is too low | Use a valid signature and cohort with enough events |
| `SKILL_INVALID_PARAMETER` | Bad `--time_unit`, invalid color, or impossible ROC time point | Correct the parameter value |
| `SKILL_DEPENDENCY_MISSING` | Required R package is not installed | Install the missing package |
| `SKILL_PKG_VERSION` | Installed package version is below the required minimum | Upgrade the package to the required version |

**IF error persists**, READ: `references/troubleshooting.md`

---

## Testing

### Test with Included Data

```bash
# Check CLI
Rscript scripts/main.R --help

# Run with bundled test data in a fresh output directory
Rscript scripts/main.R \
  -e tests/data/BRCA_data.csv \
  -c tests/data/BRCA_clinic.csv \
  -m tests/data/BRCA_coef.csv \
  -o ./output/
```

### Validation Commands

```bash
# Run R tests
Rscript tests/testthat.R

# Refresh the retained example output bundle
Rscript tests/refresh_example_output.R

# Inspect the generated risk table
wc -l tests/output/table/out_varifyRisk.txt

# Review the retained example outputs
ls -la tests/output/
```

### Real-data Baseline

The repository stores a documented real-data baseline summary in `references/baseline-run.md`.

**IF you need exact benchmark outputs or runtime expectations**, READ: `references/baseline-run.md`

---

## Directory Structure

```text
external-model-validation/
├── SKILL.md
├── scripts/
│   ├── main.R
│   ├── run_analysis.R
│   ├── functions.R
│   ├── io.R
│   ├── plotting.R
│   └── utils.R
├── references/
│   ├── algorithm.md
│   ├── troubleshooting.md
│   ├── cli-guide.md
│   └── baseline-run.md
└── tests/
    ├── output/
    │   ├── analysis.log
    │   ├── run_parameters.tsv
    │   ├── session_info.txt
    │   ├── data/
    │   ├── table/
    │   └── plot/
    ├── refresh_example_output.R
    ├── testthat.R
    ├── testthat/
    │   └── test_external_model_validation.R
    └── data/
        ├── BRCA_data.csv
        ├── BRCA_clinic.csv
        └── BRCA_coef.csv
```

---

## Implementation Checklist

- [x] CLI parsing with `optparse`
- [x] `set.seed()` for reproducibility
- [x] Dependency checks with `requireNamespace()`
- [x] Structured logging to console and file
- [x] Timeout control with `setTimeLimit()`
- [x] Session info recording
- [x] Real test data provided in `tests/data/`
- [x] R tests provided in `tests/testthat/`
- [x] Overwrite protection for non-empty output directories
- [x] Retained-output refresh helper provided in `tests/refresh_example_output.R`
- [x] File reading instructions in `SKILL.md`
- [x] Modular script structure in `scripts/`
- [x] Error handling with `SKILL_*` codes
- [x] Baseline run captured for manual review and future audits

---

*Last updated: 2026-04-15 | Version: 1.0.0*
