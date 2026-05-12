---
name: sample-group-sankey-plot
description: Use when generating Sankey or alluvial plots from sample annotation tables where rows are samples and selected columns are categorical stages such as risk group, response status, subtype, or cohort labels. NOT for: gene network flow analysis, continuous-value trajectories, or graph-structured pathway visualization.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Sample Group Sankey Plot

Builds a reproducible Sankey/alluvial visualization from a tabular sample annotation file and exports the selected annotations, lodes-format table, plot PDF, and session metadata.

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | Alluvial transformation logic, assumptions, and plotting choices |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --input_file ... --output_dir ...` |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed CLI examples |
| **Need test data** | `tests/data/` | Sample annotation tables for smoke tests and regression checks |

---

## Usage

### Environment Setup

Install required R packages before the first run:

```bash
Rscript scripts/install_dependencies.R
```

### Basic Command

```bash
Rscript scripts/main.R \
  --input_file ./annotations.csv \
  --output_dir ./output \
  --columns risk,Responder \
  --seed 42
```

---

## Arguments

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-i` | `--input_file` | character | **required** | Input CSV/TSV annotation table |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
| `-c` | `--columns` | character | all columns | Comma-separated stage columns to include in the plot |
| `-p` | `--output_prefix` | character | `sankey_plot` | Prefix for generated output files |
|  | `--width` | numeric | `7` | Plot width in inches |
|  | `--height` | numeric | `5` | Plot height in inches |
|  | `--alpha` | numeric | `0.5` | Flow transparency between `0` and `1` |
|  | `--label_size` | numeric | `4.5` | Stratum label size |
|  | `--missing_label` | character | `Missing` | Replacement label for blank or `NA` strata |
|  | `--title` | character | empty | Optional plot title |
| `-s` | `--seed` | integer | `42` | Random seed recorded for reproducibility |
|  | `--timeout` | integer | `3600` | Maximum allowed elapsed runtime in seconds; use `0` to disable |

---

## Input Format

### Annotation Table (`input_file`)

Delimited text file where rows represent samples and each selected column is a categorical stage shown in the Sankey plot.

```csv
SampleID,risk,Responder,Subtype
S1,High,Yes,Basal
S2,Low,No,LumA
S3,High,Yes,Basal
S4,Low,No,LumB
```

**Requirements:**
- The file must contain at least 2 columns if `--columns` is omitted.
- Each selected column must exist in the file header.
- Selected columns are interpreted as categorical stages and will be converted to character values.
- Blank strings and `NA` values are replaced with `--missing_label`.
- CSV and TSV inputs are supported.

---

## Output Files

| File | Description |
|------|-------------|
| `table/selected_annotations.csv` | Filtered table containing only the plotted stage columns |
| `table/sankey_lodes.csv` | Long-format lodes table used to build the Sankey plot |
| `plot/{output_prefix}.pdf` | Sankey/alluvial plot as a PDF file; default filename is `sankey_plot.pdf` |
| `data/session_info.txt` | R session information and runtime parameters |

### selected_annotations.csv

| Column | Type | Description |
|--------|------|-------------|
| stage columns | character | One column per plotted stage in original order |

### sankey_lodes.csv

| Column | Type | Description |
|--------|------|-------------|
| `sample_id` | character | Synthetic row identifier used as the alluvium key |
| `x` | character | Stage name |
| `stratum` | character | Category label for the stage |

---

## Workflow

### Step 1: Validate Input
- Check that the input file exists and is readable.
- Detect CSV vs TSV input.
- Validate that at least 2 stage columns are available.
- Validate that user-specified columns exist.

### Step 2: Prepare Sankey Data
- Subset the selected stage columns.
- Replace missing or blank labels.
- Add a row-level `sample_id` identifier.
- Convert the table with `ggalluvial::to_lodes_form()`.

### Step 3: Generate Visualization
- Build the Sankey/alluvial plot with `geom_flow()` and `geom_stratum()`.
- Render stratum labels.
- Save the plot as PDF.

### Step 4: Record Outputs
- Save the selected annotations and lodes-format table as CSV files.
- Save `sessionInfo()` and runtime arguments for reproducibility.

---

## Examples

### Reproduce the Original Two-Column Plot

```bash
Rscript scripts/main.R \
  -i tests/data/sample_annotations.csv \
  -o tests/output \
  -c risk,Responder
```

### Plot Three Annotation Stages

```bash
Rscript scripts/main.R \
  -i tests/data/sample_annotations.csv \
  -o tests/output_three_stage \
  -c risk,Responder,Subtype \
  --title "Risk to response transitions"
```

### Use All Columns Automatically

```bash
Rscript scripts/main.R \
  -i tests/data/minimal_annotations.csv \
  -o tests/output_all_columns
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input file does not exist | Check `--input_file` |
| `SKILL_EMPTY_DATA` | The input file has zero rows or fewer than 2 usable columns | Provide a non-empty table with at least 2 stage columns |
| `SKILL_MISSING_COLUMNS` | A requested stage column is absent | Correct `--columns` or fix the input header |
| `SKILL_INVALID_PARAMETER` | Width, height, alpha, or label size is invalid | Provide valid numeric arguments |
| `SKILL_DEPENDENCY_MISSING` | A required R package is unavailable | Run `Rscript scripts/install_dependencies.R` |

**IF error persists**, READ: `references/troubleshooting.md`

---

## Testing

### Test with Sample Data

```bash
Rscript scripts/install_dependencies.R

Rscript scripts/main.R --help

Rscript scripts/main.R \
  -i tests/data/sample_annotations.csv \
  -o tests/output \
  -c risk,Responder,Subtype

Rscript tests/test_skill.R

Rscript tests/run_smoke_test.R
```

### Validation Commands

```bash
ls -la tests/output/table
ls -la tests/output/plot
ls -la tests/output/data
```

---

## References

1. Brunson JC (2020) ggalluvial: Layered Grammar for Alluvial Plots. *Journal of Open Source Software*. doi:10.21105/joss.02017
2. Wickham H (2016) *ggplot2: Elegant Graphics for Data Analysis*. Springer. doi:10.1007/978-3-319-24277-4

**For detailed algorithm**, READ: `references/algorithm.md`

---

## Implementation Checklist

- [x] CLI parsing with `optparse`
- [x] `set.seed()` for reproducibility
- [x] Only CRAN packages are used
- [x] Documented parameters match the script, including `--timeout`
- [x] `get_script_dir()` is defined before use
- [x] File reading instructions are included in `SKILL.md`
- [x] Test data are provided
- [x] Error handling is implemented
- [x] Skill is created in the current working directory

---

*Last updated: 2026-04-16 | Version: 1.0.0*
