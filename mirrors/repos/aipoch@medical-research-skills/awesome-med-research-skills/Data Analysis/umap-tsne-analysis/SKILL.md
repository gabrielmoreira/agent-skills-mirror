---
name: umap-tsne-analysis
description: "Use when performing sample-level dimensionality reduction and visualization on abundance or OTU-style matrices with a companion group file, generating UMAP and/or t-SNE coordinates and plots for group separation assessment. NOT for: differential expression testing, single-cell workflows requiring dedicated embeddings pipelines, or analyses without a sample grouping file."
license: MIT
skill-author: AIPOCH
---

# UMAP and t-SNE Analysis

## Prerequisites

Run the following before the first analysis to install all required R packages:

```bash
Rscript scripts/install_dependencies.R
```

Alternative manual installation:

```bash
Rscript -e "install.packages(c('optparse','data.table','Rtsne','umap','ggplot2','vegan','R.utils'), repos='https://cloud.r-project.org')"
```

> Note: `R.utils` is only required when `--timeout > 0`, but pre-installing it avoids environment drift across runs. `testthat` is installed by `scripts/install_dependencies.R` as the development test dependency.

**The skill cannot run until these packages are installed.** In new or bare R environments, always run the prerequisite step first.

---

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | Dimensionality reduction methods, assumptions, parameter interpretation |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --input_file ... --group_file ...` |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed CLI usage examples |
| **Need test data** | `tests/data/` | Sample input files for testing |

---

## Usage

```bash
Rscript scripts/main.R \
  --input_file ./otu_table.csv \
  --group_file ./group_info.csv \
  --output_dir ./output/ \
  --method both \
  --seed 42
```

---

## Arguments

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-i` | `--input_file` | character | **required** | Abundance / OTU matrix file |
| `-g` | `--group_file` | character | **required** | Group information file |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
| `-m` | `--method` | character | `both` | Method: `tsne`, `umap`, or `both` |
|  | `--sample_id_col` | character | first column | Sample ID column in group file |
|  | `--group_col` | character | second column | Group column in group file |
|  | `--perplexity` | numeric | `25` | t-SNE perplexity |
|  | `--theta` | numeric | `0.0` | t-SNE theta |
|  | `--pca` | logical | `FALSE` | Whether to use PCA before t-SNE |
|  | `--check_duplicates` | logical | `FALSE` | Whether t-SNE should check duplicated rows |
|  | `--normalize` | logical | `TRUE` | Whether to normalize data before UMAP |
|  | `--norm_method` | character | `hellinger` | Normalization method for `vegan::decostand()` |
|  | `--n_neighbors` | integer | `10` | UMAP neighborhood size |
| `-s` | `--seed` | integer | `42` | Random seed for reproducibility |
| `-t` | `--timeout` | integer | `0` | Timeout in seconds; `0` disables timeout |

---

## Dependency Baseline

The skill was validated with the exact package baseline recorded in `dependencies.lock.tsv`.

| Package | Tested Version |
|---------|----------------|
| `optparse` | `1.7.5` |
| `data.table` | `1.15.4` |
| `Rtsne` | `0.17` |
| `umap` | `0.2.10.0` |
| `ggplot2` | `3.4.0` |
| `vegan` | `2.7.3` |
| `R.utils` | `2.13.0` |
| `testthat` | `3.1.2` |

Use this file as the reproducibility baseline when validating a new environment.

---

## Input Format

### Abundance / OTU Matrix (`input_file`)

Features as rows, samples as columns, CSV/TSV-like tabular file with feature ID in the first column.

```csv
OTU_ID,S1,S2,S3,S4
OTU_1,10,3,0,5
OTU_2,2,8,1,0
OTU_3,0,0,6,9
```

### Group File (`group_file`)

Tabular file with at least two columns: sample ID and group label.

```csv
SampleID,Group
S1,Control
S2,Control
S3,Treatment
S4,Treatment
```

Requirements:

- At least 2 groups with at least 2 samples per group are required.
- All sample IDs in the group file must exist in the matrix columns.
- Single-group inputs will produce a `SKILL_INVALID_PARAMETER` error because dimensionality reduction without group contrast produces uninterpretable plots.

---

## Output Files

| File | Description |
|------|-------------|
| `table/tsne_coordinates.csv` | t-SNE coordinates with sample and group annotations |
| `table/umap_coordinates.csv` | UMAP coordinates with sample and group annotations |
| `plot/tsne_plot.pdf` | t-SNE scatter plot with group colors and ellipses |
| `plot/umap_plot.pdf` | UMAP scatter plot with group colors and ellipses |
| `data/session_info.txt` | R session and package version info |
| `data/analysis_data.rda` | Saved analysis object with aligned matrix, metadata, colors, and runtime parameters |

---

## Workflow

### Step 1: Validate Input
- Check that matrix file and group file exist
- Resolve sample ID and group columns
- Validate at least 2 groups and at least 2 samples per group
- Ensure all group-file sample IDs exist in the matrix
- Remove samples with zero total abundance after alignment if needed

### Step 2: Prepare Matrix
- Convert input table into numeric matrix
- Align matrix columns to sample order from the group file
- Transpose matrix so rows become samples and columns become features

### Step 3: Run Dimensionality Reduction
- Run t-SNE if `--method tsne` or `--method both`
- Run UMAP if `--method umap` or `--method both`
- Apply fixed random seed for reproducibility

### Step 4: Generate Visualizations
- Plot sample embeddings
- Color points by group
- Draw group ellipses when enabled
- Save PDF outputs

---

## Methods

### t-SNE
t-SNE is a non-linear dimensionality reduction method that preserves local neighborhood structure. It is useful for identifying local sample clustering patterns.

### UMAP
UMAP is a manifold learning method that aims to preserve both local and some global structure. It is often faster than t-SNE and can produce stable low-dimensional embeddings when parameters are chosen appropriately.

### Normalization
When `--normalize TRUE`, the script uses `vegan::decostand()` with the selected `--norm_method` before UMAP. This is helpful for abundance-style ecological matrices.

---

## Agent Response Contract

After a successful run, report:

1. **Method(s) run** (tsne, umap, or both)
2. **Sample count** and **group count** processed
3. **Key parameters** used (perplexity for t-SNE, n_neighbors for UMAP)
4. **Group separation quality** (describe visible clustering from coordinate ranges if accessible)
5. **Artifact paths**: coordinate CSV(s) and plot PDF(s) produced

---

## Examples

### Basic Usage
```bash
Rscript scripts/main.R \
  -i otu_table.csv \
  -g group_info.csv \
  -o ./output \
  -m both
```

### Only t-SNE
```bash
Rscript scripts/main.R \
  -i otu_table.csv \
  -g group_info.csv \
  -o ./output \
  -m tsne \
  --perplexity 10
```

### Only UMAP with Custom Group Column
```bash
Rscript scripts/main.R \
  -i otu_table.csv \
  -g metadata.csv \
  -o ./output \
  -m umap \
  --sample_id_col SampleID \
  --group_col Treatment \
  --n_neighbors 15
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input file does not exist | Check file path |
| `SKILL_MISSING_COLUMNS` | Group or matrix file lacks required columns | Verify file format |
| `SKILL_SAMPLE_MISMATCH` | Sample IDs in group file do not match matrix columns | Check sample naming consistency |
| `SKILL_EMPTY_DATA` | Matrix becomes empty after preprocessing | Check input values and filtering |
| `SKILL_INVALID_PARAMETER` | Invalid method, invalid parameter value, or single-group input | Adjust CLI arguments; ensure at least 2 groups are present |
| `SKILL_PACKAGE_NOT_FOUND` | Required R package is missing | Run `Rscript scripts/install_dependencies.R`; note that file errors will only surface after packages are installed |
| `SKILL_TIMEOUT` | Analysis exceeded the configured timeout | Increase `--timeout` or set `--timeout 0` |

**IF error persists**, READ: `references/troubleshooting.md`

**Troubleshooting note:** In environments where packages are not yet installed, `SKILL_PACKAGE_NOT_FOUND` will fire before file-validation errors. Install dependencies first, then re-run to expose any file-related errors.

---

## Input Validation

This skill accepts:
1. An abundance or OTU-style feature matrix (CSV/TSV, features as rows, samples as columns)
2. A group file with at least two groups (CSV/TSV, sample IDs and group labels)

If the user's request does not involve UMAP or t-SNE dimensionality reduction for group separation visualization — for example, asking to run differential expression testing, process single-cell RNA-seq with specialized pipelines, perform clustering without a group file, or impute missing values — do not proceed with the workflow. Instead respond:

> "UMAP and t-SNE Analysis is designed to perform sample-level dimensionality reduction and visualization on abundance or OTU-style matrices. Your request appears to be outside this scope. Please provide a feature matrix and group file for UMAP/t-SNE, or use a more appropriate tool for differential expression testing, single-cell analysis, or clustering."

---

## Testing

### Test with Sample Data

```bash
Rscript scripts/install_dependencies.R

Rscript scripts/main.R --help

Rscript scripts/main.R \
  -i tests/data/otu_table.csv \
  -g tests/data/group_info.csv \
  -o tests/output/ \
  -m both

Rscript tests/test_skill.R

Rscript tests/run_smoke_test.R
```

### Validation Commands

```bash
ls -la tests/output/
ls -la tests/output/table
ls -la tests/output/plot
ls -la tests/output/data
wc -l tests/output/table/tsne_coordinates.csv
wc -l tests/output/table/umap_coordinates.csv
```

The canonical sample data live in `tests/data/`. Use those files for examples, smoke tests, and regression checks. The canonical output layout is `output_dir/table`, `output_dir/plot`, and `output_dir/data`.

---

## Implementation Checklist

- [x] CLI parsing with `optparse`
- [x] `set.seed()` for reproducibility
- [x] `requireNamespace()` dependency checks
- [x] Dependency bootstrap script
- [x] Session info recording
- [x] File reading instructions in SKILL.md
- [x] Modular script structure
- [x] Error handling with SKILL_* codes
- [x] Test data provided in `tests/data/`
- [x] Version-pinned dependency baseline in `dependencies.lock.tsv`
- [x] Automated `testthat` coverage for validation and plotting edge cases
- [x] Scripts in `scripts/` directory
- [x] References in `references/` directory

---

*Last updated: 2026-04-27 | Version: 1.1.0*
