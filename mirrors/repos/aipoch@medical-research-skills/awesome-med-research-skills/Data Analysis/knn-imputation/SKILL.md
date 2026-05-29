---
name: knn-imputation
description: "Use when filtering genes with high missingness and then imputing missing values in a bulk expression matrix with group-aware KNN through DMwR2, where donor samples are restricted by one annotation column before imputation. For strata with 10 or fewer samples, the script falls back to row-wise direct filling with mean or median. NOT for: single-cell data, multi-column stratification, non-tabular inputs, network access, or interactive workflows."
license: MIT
skill-author: AIPOCH
---

# KNN Imputation

## When to Use

Use this skill when you need to remove genes with more than 50% missing values from a bulk expression matrix and then run group-aware KNN imputation, with the donor pool restricted by one grouping column.

Do not use this skill for:
- single-cell data
- multi-column stratification
- non-tabular inputs
- network-dependent workflows
- interactive analysis sessions

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | Group-stratified KNN method, fallback rules, and assumptions |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --input_file ... --group_file ...` |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed CLI usage examples |
| **Need sample input fixtures** | `tests/data/` | Repository fixtures for local validation and examples |

## Input Validation

This skill accepts: a bulk expression matrix CSV (features × samples) and a sample annotation CSV file with a single grouping column for KNN stratification.

If the user's request does not involve imputing missing values in a bulk expression matrix — for example, asking to impute single-cell data, use multi-column stratification, or run network-dependent workflows — do not proceed with the workflow. Instead respond:
> "knn-imputation is designed to filter and impute missing values in bulk expression matrices using group-aware KNN with DMwR2. Your request appears to be outside this scope. Please provide a bulk expression matrix with a single grouping column, or use a more appropriate tool for your task."

## Prerequisites

DMwR2 is **not available on CRAN**. Install it from GitHub before running:

```r
install.packages("remotes")
remotes::install_github("cran/DMwR2")
```

If `SKILL_DEPENDENCY_MISSING` is raised, use the command above to install DMwR2 before retrying. Standard `install.packages("DMwR2")` will not work.

---

## Usage

```bash
Rscript scripts/main.R \
  --input_file tests/data/sample_expression_matrix.csv \
  --group_file tests/data/sample_groups.csv \
  --output_dir tests/output/basic_run \
  --sample_column sample \
  --group_column group \
  --k 10 \
  --small_strata_fill_method mean \
  --overwrite \
  --timeout_seconds 0 \
  --seed 42
```

If re-running into an existing `output_dir`, pass `--overwrite`. Otherwise use a fresh output directory.

---

## Arguments

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-i` | `--input_file` | character | **required** | Expression matrix CSV file with features in rows and samples in columns |
| `-g` | `--group_file` | character | **required** | Sample annotation CSV file |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
| `-c` | `--sample_column` | character | `sample` | Sample ID column in the group file |
| `-l` | `--group_column` | character | `group` | Single grouping column used to define imputation strata |
| `-k` | `--k` | integer | `10` | Number of nearest neighbors used inside each stratum |
| `-m` | `--small_strata_fill_method` | character | `mean` | Fill method for strata with 10 or fewer samples: `mean` or `median` |
|  | `--overwrite` | flag | `FALSE` | Overwrite existing output files in `output_dir` |
| `-t` | `--timeout_seconds` | integer | `0` | Optional elapsed timeout in seconds, `0` disables timeout |
| `-s` | `--seed` | integer | `42` | Random seed for reproducibility |

---

## Input Format

### Expression Matrix (`input_file`)

Features as rows, samples as columns, CSV format with feature ID in the first column.

```csv
,Sample01,Sample02,Sample03
TSPAN6,1.84,1.83,3.82
SEMA3F,4.83,4.04,5.28
```

Requirements:
- The first column stores feature IDs.
- All remaining columns must be numeric or empty.
- Missing values must be encoded as empty cells or `NA`.

### Group File (`group_file`)

CSV with one sample ID column and one grouping column.

```csv
sample,group
Sample01,case
Sample02,control
Sample03,case
```

Requirements:
- `sample_column` must match the expression matrix sample names exactly.
- The column named in `group_column` must exist in the group file.
- `sample_column` and the selected grouping column must be non-missing.
- KNN only runs for strata with at least 11 samples.
- Strata with 10 or fewer samples use row-wise direct filling with `--small_strata_fill_method`.

---

## Output Files

| File | Format | Description |
|------|--------|-------------|
| `imputed_expression_matrix.csv` | CSV | Complete imputed expression matrix |
| `session_info.txt` | TXT | R session and package version information |

---

## Workflow

### Step 1: Validate Input
- Check file existence.
- Validate sample matching between expression matrix and group file.
- Verify that the requested grouping column exists.

### Step 2: Filter Genes
- Remove genes whose missing-value fraction across all samples is at least 50%.
- Stop if all genes are removed by this filter.

### Step 3: Build Strata
- Construct one stratum per unique value in `group_column`.
- Keep strata even when they are small; only strata with at least 11 samples run KNN.

### Step 4: Run Imputation
- Run group-stratified KNN imputation only within strata that contain at least 11 samples.
- Within each stratum, skip imputation for any gene whose missing-value fraction in that stratum is at least 50%; leave those values as `NA`.
- For strata with 10 or fewer samples, fill missing values by the row-wise mean or median within that stratum.
- If a small stratum has an all-missing gene row that is still imputable, fall back to the global row-wise mean or median.

### Step 5: Save Results
- Write the imputed matrix.
- Save `session_info.txt` to the output directory.

---

## Methods

### Missingness Filter + Group-Stratified DMwR2 KNN

Genes with at least 50% missing values are removed first. KNN imputation is then applied within user-defined strata built from one grouping column when the stratum contains at least 11 samples.

If the chosen grouping scheme splits the data into strata of 10 samples or fewer, the command falls back to row-wise direct filling by mean or median inside that stratum. Genes that reach at least 50% missingness within a stratum are skipped in that stratum and remain `NA`. If another small-stratum row is fully missing but still below that threshold, the script falls back to the corresponding global row summary.

For implementation details, assumptions, and skip behavior for small strata, read `references/algorithm.md`.

---

## Examples

### Basic Usage

```bash
Rscript scripts/main.R \
  -i tests/data/sample_expression_matrix.csv \
  -g tests/data/sample_groups.csv \
  -o tests/output/basic_run
```

### Smaller Neighborhood

```bash
Rscript scripts/main.R \
  -i tests/data/sample_expression_matrix.csv \
  -g tests/data/sample_groups.csv \
  -o tests/output/k5_run \
  -k 5
```

### Small Strata Fallback

```bash
Rscript scripts/main.R \
  -i tests/data/sample_expression_matrix.csv \
  -g tests/data/sample_groups.csv \
  -o tests/output/small_strata_run \
  -l sample \
  -m median \
  --overwrite
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input file does not exist | Check the file path |
| `SKILL_EMPTY_FILE` | Input file exists but is empty | Replace it with a valid non-empty CSV file |
| `SKILL_OUTPUT_EXISTS` | Output files already exist | Re-run with `--overwrite` or change `--output_dir` |
| `SKILL_SAMPLE_MISMATCH` | Sample names do not match between files | Verify exact sample name matching |
| `SKILL_MISSING_COLUMNS` | Requested grouping column is absent | Add that column to the group file or change `--group_column` |
| `SKILL_INVALID_PARAMETER` | Multiple grouping columns were supplied | Pass exactly one grouping column in `--group_column` |
| `SKILL_INVALID_DATA` | Matrix or group file structure is invalid | Check input format, duplicated IDs, and group completeness |
| `SKILL_DEPENDENCY_MISSING` | DMwR2 not installed | Install with: `Rscript -e "install.packages('remotes'); remotes::install_github('cran/DMwR2')"` — note: DMwR2 is not on CRAN |
| `SKILL_TIMEOUT` | Timeout limit was exceeded | Increase `--timeout_seconds` or reduce data size |

**IF error persists**, READ: `references/troubleshooting.md`

---

## Local Validation

### Validate the CLI Entrypoint

```bash
# Check help
Rscript scripts/main.R --help

# Run with sample data
Rscript scripts/main.R \
  -i tests/data/sample_expression_matrix.csv \
  -g tests/data/sample_groups.csv \
  -o tests/output/basic_run \
  --overwrite

# Run forced small-strata fallback
Rscript scripts/main.R \
  -i tests/data/sample_expression_matrix.csv \
  -g tests/data/sample_groups.csv \
  -o tests/output/small_strata_run \
  -l sample \
  -m median \
  --overwrite
```

### Output Checks

```bash
# Count lines in output
wc -l tests/output/basic_run/imputed_expression_matrix.csv

# Check output files exist
ls -la tests/output/basic_run
```

## Reference Files

| File | Purpose |
|---|---|
| `references/algorithm.md` | Group-stratified KNN method, fallback rules, and assumptions |
| `references/troubleshooting.md` | Common errors and solutions |
| `references/cli-guide.md` | CLI usage examples |
