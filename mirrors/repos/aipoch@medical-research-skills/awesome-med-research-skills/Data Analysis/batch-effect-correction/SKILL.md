---
name: batch-effect-correction
description: Use when correcting batch effects in merged bulk expression matrices with sample-level batch metadata while preserving biological group structure and generating before-and-after QC plots. NOT for: single-cell integration, raw FASTQ processing, differential expression without batch labels, or datasets without biological groups.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Batch Effect Correction

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | ComBat workflow, assumptions, and QC logic |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --input_file ... --group_file ...` |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed CLI usage examples and baseline run record |
| **Need test data** | `tests/data/` | Sample input files for testing |

---

## Usage

```bash
Rscript scripts/main.R \
  --input_file ./expression_matrix.csv \
  --group_file ./sample_info.csv \
  --output_dir ./output/ \
  --batch_column batch \
  --group_column group \
  --sample_column sample \
  --log_transform auto \
  --timeout_seconds 600 \
  --seed 42
```

---

## Arguments

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-i` | `--input_file` | character | **required** | Expression matrix file (genes as rows, samples as columns) |
| `-g` | `--group_file` | character | **required** | Sample metadata file (sample ID, group, and batch columns) |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
| `-b` | `--batch_column` | character | `batch` | Batch column name in metadata |
| `-c` | `--group_column` | character | `group` | Biological group column name in metadata |
| `-n` | `--sample_column` | character | `sample` | Sample ID column name in metadata |
| `-l` | `--log_transform` | character | `auto` | Log transform mode: `auto`, `yes`, `no` |
| `-t` | `--timeout_seconds` | integer | `600` | Elapsed time limit in seconds; use `0` to disable |
| `-s` | `--seed` | integer | `42` | Random seed for reproducibility |

---

## Input Format

### Expression Matrix (input_file)

Genes as rows, samples as columns, CSV format with gene ID in the first column.

```csv
"","Sample01","Sample02","Sample03"
"GeneA",5.12,4.87,6.03
"GeneB",8.44,8.11,7.95
```

Requirements:
- Gene IDs must be unique and non-empty
- Sample column names must be unique and non-empty
- Expression values must be numeric and finite
- Extra expression-matrix sample columns not present in metadata are allowed and will be ignored with a warning

### Sample Metadata (group_file)

CSV with sample ID, biological group, and batch columns.

```csv
"sample","group","batch"
"Sample01","Control","Batch1"
"Sample02","Case","Batch1"
"Sample03","Case","Batch2"
```

Requirements:
- Sample IDs must be unique and non-empty
- At least 2 biological groups are required
- At least 2 batches are required
- Each group and each batch must contain at least 2 samples
- Metadata may describe a subset of expression-matrix samples; the analysis will keep only metadata-matched samples and warn about ignored expression columns

---

## Output Files

| File | Description |
|------|-------------|
| `corrected_expression_matrix.csv` | Batch-corrected expression matrix |
| `matched_sample_info.csv` | Standardized metadata used in the analysis |
| `batch_before_boxplot.pdf` | Sample distribution boxplot before correction |
| `batch_after_boxplot.pdf` | Sample distribution boxplot after correction |
| `batch_before_pca.pdf` | PCA scatter plot before correction with batch-colored points; batch ellipses are added when batch size/covariance supports stable fitting |
| `batch_after_pca.pdf` | PCA scatter plot after correction with batch-colored points; batch ellipses are added when batch size/covariance supports stable fitting |
| `batch_before_clustering.pdf` | Hierarchical clustering before correction |
| `batch_after_clustering.pdf` | Hierarchical clustering after correction |
| `session_info.txt` | R session and package version info |

---

## Workflow

### Step 1: Validate Input
- Check file existence and non-empty input files
- Validate metadata column presence
- Verify expression values are numeric and finite
- Confirm at least 2 groups, 2 batches, and at least 2 samples per group/batch

### Step 2: Align and Prepare Matrix
- Reorder expression columns to match metadata sample order
- Keep only metadata-matched samples; warn if the expression matrix contains extra samples absent from metadata
- Decide whether log transformation is needed
- Apply `log2(x + 1)` only when required

### Step 3: Run Batch Correction
- Build the design matrix with biological group information
- Run `sva::ComBat()` to remove batch-driven variation
- Preserve modeled biological group structure during correction

### Step 4: Normalize and Export Results
- Apply `limma::normalizeBetweenArrays()` after ComBat
- Write the corrected matrix and matched metadata
- Save before/after QC plots and session information

---

## Methods

### ComBat
Empirical Bayes batch-effect correction using `sva::ComBat()`. Recommended when merged bulk expression datasets contain known batch labels and at least two biological groups.

### Log Transformation
Supports `auto`, `yes`, and `no`. The `auto` mode applies `log2(x + 1)` only when the matrix appears to be on a raw-like scale.

### normalizeBetweenArrays
Post-correction normalization with `limma::normalizeBetweenArrays()` to reduce remaining cross-sample distribution differences.

### QC Visualization
Generates paired boxplots, PCA scatter plots with conditional batch ellipses, and hierarchical clustering plots before and after correction to assess whether batch-driven structure is reduced.

---

## Examples

### Basic Usage
```bash
Rscript scripts/main.R \
  -i expression_matrix.csv \
  -g sample_info.csv \
  -o ./output
```

### With Custom Metadata Columns
```bash
Rscript scripts/main.R \
  -i expression_matrix.csv \
  -g metadata.csv \
  -o ./output \
  -n sample_id \
  -c condition \
  -b platform_batch
```

### Disable Log Transform and Timeout
```bash
Rscript scripts/main.R \
  -i expression_matrix.csv \
  -g sample_info.csv \
  -o ./output \
  -l no \
  -t 0 \
  -s 42
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input file does not exist | Check file path |
| `SKILL_EMPTY_FILE` | Input file exists but contains no data | Recreate or re-export the file |
| `SKILL_MISSING_COLUMNS` | Metadata file is missing sample, group, or batch columns | Check header names or pass custom column names |
| `SKILL_SAMPLE_MISMATCH` | Metadata sample IDs do not match expression matrix columns | Verify sample names between files |
| `SKILL_INVALID_DATA` | Dataset fails minimum design checks | Review group counts, batch counts, and ID validity |
| `SKILL_INVALID_TYPE` | Expression values are non-numeric or non-finite | Clean matrix values before running |
| `SKILL_TIMEOUT` | Run exceeded the configured time limit | Increase `--timeout_seconds` or set it to `0` |
| `SKILL_DEPENDENCY_MISSING` | Required R package is not installed | Install missing dependencies |
| `SKILL_RUNTIME_ERROR` | Runtime I/O or filesystem error occurred | Check read/write permissions and environment |

**IF error persists**, READ: `references/troubleshooting.md`

---

## Testing

### Test with Sample Data

```bash
# Check help
Rscript scripts/main.R --help

# Run with bundled test data
Rscript scripts/main.R \
  -i tests/data/expression_matrix_merged.csv \
  -g tests/data/sample_info.csv \
  -o tests/output/
```

### Validation Commands

```bash
# Check corrected matrix exists
ls -la tests/output/corrected_expression_matrix.csv

# Check matched metadata exists
ls -la tests/output/matched_sample_info.csv

# Check PCA output exists
ls -la tests/output/batch_after_pca.pdf
```

---

## Implementation Checklist

- [x] CLI parsing with `optparse`
- [x] `set.seed()` for reproducibility
- [x] `requireNamespace()` dependency checks
- [x] Session info recording
- [x] Time-limit support through `setTimeLimit()`
- [x] File reading instructions in SKILL.md
- [x] Modular script structure in `scripts/`
- [x] Test data provided
- [x] Error handling with `SKILL_*` codes
- [x] QC plots generated before and after correction
- [x] References in `references/` directory

---

*Last updated: 2026-04-20 | Version: 1.0.0*
