---
name: decision-tree-analysis
description: Use when building a decision tree model in R and generating feature importance ranking outputs. Supports classification and regression, automatic task detection, parameter validation, model evaluation summaries, and exports of feature-importance tables and figures.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Decision Tree Analysis

Use this skill to train a decision tree model from a tabular file and export feature importance ranking results.

## Use This Skill When

- You need a decision tree workflow in R for either classification or regression.
- You need feature importance ranking as a table and a figure.
- You need a command-line workflow with parameter validation and standardized output folders.

## Primary Command

```bash
Rscript scripts/main.R \
  --data_file <input_file> \
  --target_var <target_column> \
  --task_type <auto|classification|regression> \
  --output_dir <output_dir>
```

## Prerequisites

- `Rscript` is available in the shell.
- Required R packages: `optparse`, `data.table`, `rpart`.
- Install missing packages with `Rscript -e 'install.packages(c("optparse", "data.table", "rpart"), repos="https://cloud.r-project.org")'`.

## Core Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--data_file` | Yes | Input data file in CSV, TXT, or TSV format |
| `--target_var` | Yes | Target column to predict |
| `--task_type` | No | `auto`, `classification`, or `regression`. Default `auto` |
| `--output_dir` | No | Output directory, default `./Decision_Tree_Results` |
| `--train_ratio` | No | Train set ratio between 0 and 1, default `0.7` |
| `--max_depth` | No | Maximum tree depth, default `5` |
| `--minsplit` | No | Minimum observations required to attempt a split, default `10` |
| `--minbucket` | No | Minimum observations allowed in a terminal node, default `3` |
| `--cp` | No | Complexity parameter for pruning, default `0.001` |
| `--seed` | No | Random seed, default `42` |
| `--exclude_vars` | No | Comma-separated columns to exclude from modeling |
| `--importance_top_n` | No | Number of top features to show in the importance plot, default `15` |
| `--output_format` | No | Table output format: `csv` or `txt`, default `csv` |

## Input Requirements

- The input file must contain the target column.
- All predictor columns come from the remaining columns after excluding `target_var` and `exclude_vars`.
- If the first column is unnamed or uses an ID-like name such as `id` or `rowname`, and its values are unique, the skill automatically treats it as row names instead of a predictor.
- Rows with missing values in any modeling column are removed before training.
- Character predictors are automatically converted to factors.
- In `auto` mode, a numeric target with more than 10 unique values is treated as regression; otherwise it is treated as classification.
- At least 5 complete rows are required after filtering.

Example input:

```csv
study_hours,sleep_hours,attendance,score_band
3.5,7.0,0.88,medium
5.0,6.5,0.95,high
2.0,8.0,0.75,low
```

## Minimal Workflow

1. Confirm the input file exists and the target column name is correct.
2. Run `scripts/main.R` with the target column and optional modeling parameters.
3. Check the output directory for feature importance tables under `table/` and the ranking plot under `figure/`.

If you omit `--data_file` or `--target_var`, the script exits with `SKILL_MISSING_INPUT`.

## Outputs

Expected output structure:

```text
<output_dir>/
├── data/
├── table/
└── figure/
```

Primary result files:

- `table/decision_tree_feature_importance.<csv|txt>`
- `table/decision_tree_metrics.csv`
- `figure/decision_tree_feature_importance.pdf`

Additional files:

- `data/decision_tree_predictions.csv`
- `data/decision_tree_model.rds`

Notes:

- Exactly one feature-importance table is written per run. The file extension is controlled by `--output_format`.
- Evaluation metrics are saved to `table/decision_tree_metrics.csv`.
- If the fitted tree does not split, the run completes but emits a warning because feature importances and predictions may be degenerate on very small training sets.

Feature importance result fields include:

- `rank`
- `feature`
- `importance`
- `relative_importance`

## Choose the Task Type

- Use `classification` for categorical targets such as `yes/no`, `risk_level`, or `species`.
- Use `regression` for continuous numeric targets such as `price`, `score`, or `yield`.
- Use `auto` when the target type is obvious and you want the script to infer it.

## Read These Files When Needed

| Need | File |
|------|------|
| Decision tree method and feature importance details | `references/algorithm.md` |
| More CLI examples | `references/cli-guide.md` |
| Error diagnosis | `references/troubleshooting.md` |
| Main execution entry point | `scripts/main.R` |
| Sample test data | `tests/data/` |

## Test Data

- `tests/data/dt_sample1.csv`: CSV classification sample with an unnamed first column automatically recognized as row names. Suggested target: `fustat`.
- `tests/data/dt_sample2.csv`: CSV classification sample with an unnamed first column automatically recognized as row names. Suggested target: `fustat`.
- `tests/data/dt_sample3.txt`: Tab-delimited high-dimensional classification sample with an unnamed first column automatically recognized as row names. Suggested target: `Group`.

## Quick Examples

Classification:

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample1.csv \
  --target_var fustat \
  --task_type classification \
  --max_depth 4 \
  --output_dir tests/output_dt_sample1_classification
```

Classification on a second CSV sample:

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample2.csv \
  --target_var fustat \
  --task_type classification \
  --output_dir tests/output_dt_sample2_classification
```

TXT input example:

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample3.txt \
  --target_var Group \
  --task_type classification \
  --max_depth 4 \
  --output_dir tests/output_dt_sample3_classification
```

## Validation

```bash
Rscript scripts/main.R --help
```

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample1.csv \
  --target_var fustat \
  --task_type classification \
  --output_dir tests/validation_dt_sample1
```

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample2.csv \
  --target_var fustat \
  --task_type classification \
  --output_dir tests/validation_dt_sample2
```

```bash
Rscript scripts/main.R \
  --data_file tests/data/dt_sample3.txt \
  --target_var Group \
  --task_type classification \
  --output_dir tests/validation_dt_sample3
```

After running analysis, verify that the following exist:

- `tests/validation_dt_sample1/table/decision_tree_feature_importance.csv`
- `tests/validation_dt_sample1/table/decision_tree_metrics.csv`
- `tests/validation_dt_sample1/figure/decision_tree_feature_importance.pdf`
- `tests/validation_dt_sample2/table/decision_tree_feature_importance.csv`
- `tests/validation_dt_sample2/table/decision_tree_metrics.csv`
- `tests/validation_dt_sample2/figure/decision_tree_feature_importance.pdf`
- `tests/validation_dt_sample3/table/decision_tree_feature_importance.csv`
- `tests/validation_dt_sample3/table/decision_tree_metrics.csv`
- `tests/validation_dt_sample3/figure/decision_tree_feature_importance.pdf`

## Common Errors

- `SKILL_FILE_NOT_FOUND`: Input file path is wrong or inaccessible.
- `SKILL_MISSING_COLUMNS`: The target column or requested excluded columns are missing.
- `SKILL_INVALID_DATA`: Input data is malformed or unsuitable for model training.
- `SKILL_INVALID_PARAMETER`: An argument value is invalid.
- `SKILL_INSUFFICIENT_DATA`: Too few usable rows or classes remain after filtering.
- `SKILL_DEPENDENCY_MISSING`: A required R package such as `optparse`, `data.table`, or `rpart` is unavailable.

If a run succeeds but logs that the decision tree did not split, lower `--minsplit` and `--minbucket` or provide more training rows before trusting the ranking output.

If the issue is not obvious, read `references/troubleshooting.md`.
