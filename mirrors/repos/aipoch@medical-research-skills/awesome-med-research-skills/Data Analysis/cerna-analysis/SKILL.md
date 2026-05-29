---
name: cerna-analysis
description: "Use when building a ceRNA regulatory network from a key gene list by combining bundled miRNA-mRNA and miRNA-lncRNA database files, with flat-file CSV exports and PDF visualization in a single output directory. NOT for: differential expression, single-cell analysis, enrichment analysis, or workflows without a key gene list."
license: MIT
skill-author: Codex
---

# ceRNA Analysis

## When to Use

Use this skill when you need to construct a ceRNA regulatory network from a known key-gene list using the bundled miRNA-mRNA and miRNA-lncRNA reference tables.

Use it for:

- Building a ceRNA network from one gene list and exporting flat CSV plus PDF outputs
- Comparing supported miRNA source modes such as `combined`, `starbase`, or pairwise overlaps
- Re-running the same local workflow with different lncRNA strictness, layout, or plotting parameters

Do not use it for:

- Differential expression, single-cell, enrichment, or survival analysis
- Workflows that do not start from a key gene list
- Cases where you want a miRNA-mRNA-only graph without a retained lncRNA ceRNA layer

## Input Validation

This skill accepts:

- A key gene list as a plain-text file (one gene symbol per line) or as a comma-separated string on the CLI
- Optional parameter overrides for dataset mode, lncRNA strictness, layout, colors, and timeout

If the user's request does not involve building a ceRNA regulatory network from a key gene list — for example, asking to run differential expression, enrichment analysis, single-cell workflows, or survival analysis — do not proceed with the workflow. Instead respond:

> "ceRNA Analysis is designed to construct a ceRNA regulatory network from a key gene list using bundled miRNA-mRNA and miRNA-lncRNA reference databases. Your request appears to be outside this scope. Please provide a key gene list and specify a supported miRNA dataset mode, or use a more appropriate skill for differential expression, enrichment analysis, or single-cell workflows."

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | ceRNA construction logic, dataset combinations, filtering rules. Includes worked examples of pairwise intersection network size vs combined mode. |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --key_genes ... --output_dir ...`. Note: `--help` requires igraph to be installed. |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed local run examples with measured outputs |
| **Need test data** | `tests/data/` | Sample key-gene input for testing |

## Usage

```bash
Rscript scripts/main.R \
  --key_genes tests/data/gene.txt \
  --output_dir ./output/ \
  --mirna_dataset combined \
  --lncrna_strictness High \
  --lncrna_freq_thresh 0 \
  --timeout_seconds 600 \
  --seed 42
```

> **Dependency note:** `--help` and all analysis modes require `igraph` to be installed. Install igraph before running any command. Use `references/troubleshooting.md` for installation guidance.

## Arguments

### Main Analysis: `scripts/main.R`

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-i` | `--key_genes` | character | **required** | Key gene file path or comma-separated gene names |
| `-o` | `--output_dir` | character | `./output/` | Output directory |
| `-m` | `--mirna_dataset` | character | `combined` | Dataset: `combined`, `starbase`, `mirdb`, `mirtarbase`, `starbase+mirdb`, `starbase+mirtarbase`, `mirdb+mirtarbase` |
| `-l` | `--lncrna_strictness` | character | `High` | lncRNA interaction strictness: `Low`, `Median`, `High` |
| `-f` | `--lncrna_freq_thresh` | integer | `0` | Minimum retained lncRNA frequency |
| `-r` | `--reference_dir` | character | `file.path(script_dir, "..", "references", "database")` | Database directory |
|  | `--plot_width` | double | `12` | PDF width in inches |
|  | `--plot_height` | double | `8` | PDF height in inches |
|  | `--layout_type` | character | `kk` | Layout: `kk`, `fr`, `nicely`, `circle`, `grid`, `randomly` |
|  | `--mrna_color` | character | `#D16BA5` | mRNA node color |
|  | `--lncrna_color` | character | `#008dcd` | lncRNA node color |
|  | `--mirna_color` | character | `#00c9a7` | miRNA node color |
|  | `--node_size_base` | double | `15` | Base node size |
|  | `--label_size` | double | `0.8` | Node label size |
|  | `--show_legend` | logical | `TRUE` | Show legend in the PDF |
| `-t` | `--timeout_seconds` | integer | `3600` | Elapsed timeout limit |
| `-s` | `--seed` | integer | `42` | Random seed for reproducibility |

## Input Format

### Key Genes (`key_genes`)

Plain-text input with one gene symbol per line, or a comma-separated string passed directly on the CLI.

```text
TP53
BRCA1
MYC
```

Rules:

- Blank lines are ignored
- Lines starting with `#` are ignored
- Duplicate genes are removed
- At least one valid gene is required

### Database Directory (`reference_dir`)

The bundled database directory is `references/database/`. Required files depend on the selected `mirna_dataset` plus the selected lncRNA strictness file.

- `combined`: `miRNA_mRNA.csv`
- `starbase`: `starbase_miRNA_mRNA.csv`
- `mirdb`: `miRDB_miRNA_mRNA.csv`
- `mirtarbase`: `miRTarbase_miRNA_mRNA.csv`
- `starbase+mirdb`: `starbase_miRNA_mRNA.csv` and `miRDB_miRNA_mRNA.csv`
- `starbase+mirtarbase`: `starbase_miRNA_mRNA.csv` and `miRTarbase_miRNA_mRNA.csv`
- `mirdb+mirtarbase`: `miRDB_miRNA_mRNA.csv` and `miRTarbase_miRNA_mRNA.csv`
- lncRNA file: one of `starbase_miRNA_lncRNA_High.csv`, `starbase_miRNA_lncRNA_Median.csv`, or `starbase_miRNA_lncRNA_Low.csv`

## Output Files

| File | Description |
|------|-------------|
| `ceRNA_network_edges.csv` | Edge table with `node1,node2` columns |
| `ceRNA_network_nodes.csv` | Node table with `node,type,degree` columns |
| `ceRNA_network.pdf` | ceRNA network visualization |
| `session_info.txt` | R session details and loaded package versions |

## Workflow

### Step 1: Validate Input
- Check key-gene input existence or parse comma-separated genes
- Validate parameter choices, numeric limits, timeout, and colors
- Verify the database directory and required files

### Step 2: Load Interaction Data
- Load the selected miRNA-mRNA dataset
- Load the selected miRNA-lncRNA dataset by strictness level
- Recompute pairwise intersections when requested

### Step 3: Filter the Network
- Retain miRNA-mRNA pairs linked to the provided key genes
- Retain miRNA-lncRNA pairs connected to the retained miRNAs
- Apply the lncRNA frequency threshold
- Stop with `SKILL_INVALID_DATA` if no lncRNA interactions remain after filtering, because the ceRNA layer has collapsed

### Step 4: Build Outputs
- Construct edge and node tables
- Save CSV, PDF, and session information in the output directory root

## Methods

### `combined`
Uses the bundled precomputed overlap across three miRNA-mRNA resources for higher-confidence interactions.

### Pairwise Intersections
`starbase+mirdb`, `starbase+mirtarbase`, and `mirdb+mirtarbase` recompute the overlap between two bundled databases. Pairwise intersections typically yield 20–40% fewer edges than `combined` mode because only interactions present in both selected databases are retained. Use pairwise modes when you need higher-confidence edges at the cost of reduced network coverage.

### lncRNA Strictness
`High`, `Median`, and `Low` select different bundled starBase evidence levels for miRNA-lncRNA interactions.

## Examples

### Basic Combined Analysis

```bash
Rscript scripts/main.R \
  -i ./key_genes.txt \
  -o ./output \
  -m combined
```

### Single Database Analysis

```bash
Rscript scripts/main.R \
  -i ./key_genes.txt \
  -o ./output_starbase \
  -m starbase \
  -l Median \
  -f 1
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input file or database file is missing | Check the file path or bundled database directory |
| `SKILL_EMPTY_FILE` | A required file exists but has no content | Replace or regenerate the file |
| `SKILL_EMPTY_DATA` | A required reference table has no usable rows | Verify the input content and regenerate the file if needed |
| `SKILL_MISSING_COLUMNS` | An input table lacks required columns | Verify the expected schema |
| `SKILL_INVALID_PARAMETER` | An invalid CLI value was provided | Use one of the documented parameter values |
| `SKILL_INVALID_DATA` | The input data cannot build a valid ceRNA network, or lncRNA filtering removes the ceRNA layer entirely | Verify the key genes and database files, then lower `--lncrna_freq_thresh` or choose a different dataset / strictness |
| `SKILL_DEPENDENCY_MISSING` | A required package is not installed (igraph required for all modes including `--help`) | Install the missing package before running any command |
| `SKILL_TIMEOUT` | The run exceeded the timeout limit | Increase `--timeout_seconds` |
| `SKILL_RUNTIME_ERROR` | An unexpected runtime failure occurred | Re-run after checking the console error message |

**IF error persists**, READ: `references/troubleshooting.md`

## Testing

### Test with Sample Data

```bash
# Run with sample data (igraph must be installed first)
Rscript scripts/main.R \
  -i tests/data/gene.txt \
  -o tests/output/
```

### Validation Commands

```bash
# Inspect edge output
wc -l tests/output/ceRNA_network_edges.csv

# Check plot exists
ls -la tests/output/ceRNA_network.pdf
```
