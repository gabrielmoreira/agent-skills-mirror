---
name: sample-correlation-analysis
description: Use when performing correlation analysis between two variables including Pearson and Spearman correlation methods. Supports command-line parameter input, automatic data format detection, parameter validation, result directory creation, and CSV or TXT format result export.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Correlation Analysis

Use this skill to run correlation analysis on two variables from a tabular data file.

## Use This Skill When

- You need Pearson or Spearman correlation between two variables stored either as columns or as first-column row labels.
- You need a command-line workflow with parameter validation.
- You need standardized output files in CSV or TXT format.

## Primary Command

```bash
Rscript scripts/main.R \
  --data_file <input_file> \
  --method <pearson|spearman> \
  --x_var <variable_name> \
  --y_var <variable_name> \
  --output_dir <output_dir>
```

## Prerequisites

- Rscript is available in the shell.
- Required R packages: `optparse`, `data.table`.
- Install missing packages with `Rscript -e 'install.packages(c("optparse", "data.table"), repos="https://cloud.r-project.org")'`.

## Core Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--data_file` | Yes | Input data file in CSV, TXT, or TSV format |
| `--method` | No | Correlation method: `pearson` or `spearman`. Default `pearson` |
| `--x_var` | No | First variable name. It can match a column name or a first-column row label. Default `variable1` |
| `--y_var` | No | Second variable name. It can match a column name or a first-column row label. Default `variable2` |
| `--output_dir` | No | Output directory, default `./Correlation_Results` |
| `--alternative` | No | `two.sided`, `less`, or `greater`. Default `two.sided` |
| `--conf_level` | No | Confidence level between 0 and 1, default `0.95` |
| `--output_format` | No | `csv` or `txt`, default `csv` |
| `--output_prefix` | No | Output filename prefix, default `correlation` |

## Input Requirements

- The input file must contain both target variables.
- Both variables must contain numeric values.
- If the first column stores variable names and the remaining columns are samples, the script automatically reads variables by row label.
- Rows with missing values in either variable are excluded.
- At least 3 complete observation pairs are needed.

Example input:

```csv
variable1,variable2
10.2,8.5
11.5,9.2
9.8,7.9
```

## Minimal Workflow

1. Confirm the input file exists and variable names are correct.
2. Run `scripts/main.R` with the requested method and variable names.
3. Check the output directory for result files under `table/`.

If you omit `--data_file`, the script exits with `SKILL_MISSING_INPUT`.

## Outputs

Expected output structure:

```text
<output_dir>/
├── table/
├── figure/
└── data/
```

Primary result file:

- `table/<output_prefix>_<method>.csv`
- `table/<output_prefix>_<method>.txt`

Result fields include:

- `method`
- `correlation`
- `statistic`
- `p_value`
- `conf_low`
- `conf_high`
- `sample_size`
- `x_variable`
- `y_variable`
- `variable_orientation`

## Choose the Method

- Use `pearson` for linear relationships between continuous variables.
- Use `spearman` for monotonic relationships, non-normal data, or outlier-prone data.

## Read These Files When Needed

| Need | File |
|------|------|
| Statistical details and assumptions | `references/algorithm.md` |
| More CLI examples | `references/cli-guide.md` |
| Error diagnosis | `references/troubleshooting.md` |
| Main execution entry point | `scripts/main.R` |
| Sample test data | `tests/data/` |

## Quick Examples

Pearson:

```bash
Rscript scripts/main.R \
  --data_file tests/data/sample_correlation_1.csv \
  --method pearson \
  --x_var variable1 \
  --y_var variable2 \
  --output_dir tests/output_pearson
```

Spearman:

```bash
Rscript scripts/main.R \
  --data_file tests/data/sample_correlation_3.csv \
  --method spearman \
  --x_var "Activated CD8 T cell" \
  --y_var "Central memory CD8 T cell" \
  --output_dir tests/output_spearman
```

## Validation

```bash
Rscript scripts/main.R --help
```

```bash
Rscript scripts/main.R \
  --data_file tests/data/sample_correlation_1.csv \
  --method pearson \
  --x_var variable1 \
  --y_var variable2 \
  --output_dir tests/validation_output
```

After running analysis, verify that `tests/validation_output/table/correlation_pearson.csv` exists.

## Common Errors

- `SKILL_FILE_NOT_FOUND`: Input file path is wrong or inaccessible.
- `SKILL_MISSING_COLUMNS`: One or both requested variables are missing.
- `SKILL_INVALID_DATA`: Input data is malformed or unsuitable for analysis.
- `SKILL_INVALID_PARAMETER`: An argument value is invalid.
- `SKILL_INSUFFICIENT_DATA`: Too few complete observations remain after filtering.
- `SKILL_DEPENDENCY_MISSING`: A required R package such as `optparse` or `data.table` is unavailable.

If the issue is not obvious, read `references/troubleshooting.md`.
