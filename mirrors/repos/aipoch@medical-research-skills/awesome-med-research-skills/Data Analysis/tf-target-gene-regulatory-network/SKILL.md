---
name: tf-target-gene-regulatory-network
description: Use when analyzing transcription factor (TF) regulatory networks using Dorothea database. Input gene list, identify regulating transcription factors, generate TF-Target network visualization. For: transcription factor enrichment analysis, gene regulatory network research.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Transcription Factor (TF) Regulatory Network Analysis

## When to Use

- Use this skill when you have a human or mouse gene list and want to identify upstream TFs from the Dorothea database.
- Use it when you need a ready-to-export TF-target network table plus a publication-ready PDF network plot.
- Use it for reproducible CLI execution with saved session information and optional local Dorothea `.rds` databases.

## When Not to Use

- Do not use this skill for differential expression, pathway enrichment, cell type annotation, or survival analysis.
- Do not use it to infer causal direction beyond curated Dorothea TF-target relationships.
- Do not use it when your input genes are aliases or mixed-species symbols that have not been normalized first.

## Entry Point

- Primary CLI entry point: `scripts/main.R`
- Legacy localized visualization aliases such as `发散(fr)`, `曲线`, and `菱形` are accepted, but the canonical documented values are the English option names shown below.

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| **Need algorithm details** | `references/algorithm.md` | Statistical methods, Dorothea database, network analysis algorithms |
| **Need to run analysis** | `scripts/main.R` | Execute: `Rscript scripts/main.R --gene ... --species ...` |
| **Encounter errors** | `references/troubleshooting.md` | Common errors and solutions |
| **Need CLI examples** | `references/cli-guide.md` | Detailed CLI usage examples |
| **Need test data** | `tests/data/` | Sample gene lists for testing |

---

## Installation

### R Package Dependencies

This skill requires several R packages. Install them with:

```r
# CRAN packages
install.packages(c("optparse", "dplyr", "openxlsx", "tidyverse", "tidygraph", "ggraph", "showtext"))

# Bioconductor packages (optional if using local database files)
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("dorothea")
```

### Local Database Files (Recommended)

For faster analysis and offline use, generate local database files:

```bash
Rscript database/database-get.R
```

This creates `database/dorothea_hs.rds` (human) and `database/dorothea_mm.rds` (mouse).

### Verification

Test the installation:
```bash
Rscript scripts/main.R --help
```

## Usage

```bash
Rscript scripts/main.R \
  --gene "TP53,MYC,EGFR" \
  --species human \
  --output_dir ./TF_Result \
  --seed 42
```

---

## Arguments

**Note**: Either `--gene` or `--gene_file` must be provided (at least one is required).

| Short | Long | Type | Default | Description |
|-------|------|------|---------|-------------|
| `-g` | `--gene` | character | NULL | Comma-separated gene list (e.g., "TP53,MYC,EGFR") - **required if --gene_file not provided** |
| `-f` | `--gene_file` | character | NULL | File containing gene names (txt or csv, one per line or comma-separated) - **required if --gene not provided** |
| `-s` | `--species` | character | `human` | Species: `human` or `mouse` |
| `-o` | `--output_dir` | character | `TF_Result` | Output directory name |
| | `--db_path` | character | NULL | Local database file path (.rds format). If not specified, auto-search in default paths |
| `-d` | `--dir` | character | NULL | Working root directory (advanced) |
| | `--seed` | integer | 42 | Random seed for reproducibility |

**Visualization Parameters**: For complete list of visualization parameters (plot dimensions, colors, labels, layout, etc.), see [`references/visualization-parameters.md`](references/visualization-parameters.md). Canonical values are English tokens such as `fr`, `curve`, and `diamond,triangle`; legacy localized aliases are also accepted.

---

## Input Format

### Gene List Input

Two ways to provide input genes:

1. **Command line**: `--gene "TP53,MYC,EGFR"` (comma-separated, no spaces)
2. **File input**: `--gene_file genes.txt` (one gene per line or comma-separated)

### Gene Naming Convention

- **Human genes**: Uppercase symbols (e.g., TP53, MYC, EGFR)
- **Mouse genes**: First letter uppercase (e.g., Tp53, Myc, Egfr)
- Use official gene symbols, not aliases
- Case-sensitive for species matching

### Species Support

- `human`: Human genes (Homo sapiens)
- `mouse`: Mouse genes (Mus musculus)

---

## Output Files

| File | Description |
|------|-------------|
| `TF_Network_Plot.pdf` | TF-target network visualization |
| `tf_network.xlsx` | Network data (edges and nodes worksheets) |
| `TF_Target_Filtered_Core_<species>.xlsx` | Complete TF-target relationships table |
| `session_info.txt` | R session and package version info |
| `tf.Rdata` | R environment data |

### Output Directory Structure

```
TF_Result/
├── data/
│   └── tf.Rdata
├── plot/
│   └── TF_Network_Plot.pdf
└── table/
    ├── tf_network.xlsx
    └── TF_Target_Filtered_Core_<species>.xlsx
```

---

## Workflow

### Step 1: Load Database
- Priority search for local database files (.rds format)
- If not found, load from Dorothea R package
- Filter for high-confidence interactions (confidence levels A, B, C)

### Step 2: Identify Regulating TFs
- Match input genes against target genes in Dorothea database
- Extract transcription factors regulating these targets
- Compute TF frequency (number of targets regulated)

### Step 3: Generate Network Data
- Create edge list (TF → Target relationships)
- Create node list with types (TF or Target)
- Save to Excel format for downstream analysis

### Step 4: Visualize Network
- Generate network graph using tidygraph and ggraph
- Apply visual customization (layout, colors, shapes)
- Save as PDF publication-ready figure

---

## Methods

### Dorothea Database
- Curated database of TF-target interactions
- Confidence levels: A (high), B (medium), C (low)
- Includes human and mouse data
- Source: https://github.com/saezlab/dorothea

### Network Analysis
- **Graph construction**: TF-target relationships as directed edges
- **Layout algorithms**: Multiple options including sphere, circle, grid, etc.
- **Visual customization**: Full control over colors, shapes, sizes

### Local Database Feature
- Option to use pre-saved .rds files for faster analysis
- Priority search paths for local database files
- Fallback to R package if local files not found

---

## Examples

### Basic Usage (Human Genes)
```bash
Rscript scripts/main.R \
  -g "TP53,MYC,EGFR" \
  -s human \
  -o ./TF_Result
```

### File Input
```bash
Rscript scripts/main.R \
  -f gene_list.txt \
  -s human \
  -o ./TF_Result
```

### Mouse Genes
```bash
Rscript scripts/main.R \
  -g "Tp53,Myc,Egfr" \
  -s mouse \
  -o ./Mouse_TF_Result
```

### Custom Styling
```bash
Rscript scripts/main.R \
  -g "PTPRC,FOXP3,CD4" \
  -s human \
  --style_layout "fr" \
  --style_line "curve" \
  --point_shape "diamond,triangle" \
  --line_color "#E64B35" \
  --title "Immune TF Network" \
  -o ./Custom_Plot
```

### Using Local Database
```bash
Rscript scripts/main.R \
  -g "TP53,MYC,EGFR" \
  -s human \
  --db_path database/dorothea_hs.rds \
  -o ./LocalDB_Result
```

---

## Error Handling

### Common Errors

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input gene file does not exist | Check file path and permissions | Verify file exists and is readable |
| `SKILL_NO_INPUT_GENES` | No valid genes provided | Empty gene list or file | Provide genes using `--gene` or `--gene_file` |
| `SKILL_INVALID_SPECIES` | Unsupported species specified | Species not 'human' or 'mouse' | Use 'human' or 'mouse' only |
| `SKILL_INVALID_PARAMETER` | Unsupported visualization or CLI parameter value | Invalid layout, shape, line, label, or legend alias | Use supported values shown by `Rscript scripts/main.R --help` |
| `SKILL_EMPTY_RESULTS` | No TF-target relationships found | Gene symbols not in database | Check gene symbols and species |
| `SKILL_DEPENDENCY_MISSING` | Required R package not installed | Missing dorothea, tidygraph, etc. | Install missing packages |

**IF error persists**, READ: `references/troubleshooting.md`

---

## Testing

### Test with Sample Data

```bash
# Check help
Rscript scripts/main.R --help

# Run with sample human genes
Rscript scripts/main.R \
  -g "TP53,MYC,EGFR" \
  -s human \
  -o tests/output_human/

# Run with sample mouse genes  
Rscript scripts/main.R \
  -g "Tp53,Myc,Egfr" \
  -s mouse \
  -o tests/output_mouse/
```

### Validation Commands

```bash
# Check output files exist
ls -la tests/output_human/

# Verify network plot generated
ls -la tests/output_human/plot/TF_Network_Plot.pdf

# Check Excel file has data
file tests/output_human/table/tf_network.xlsx
```

---

## Implementation Checklist

- [x] CLI parsing with `optparse`
- [x] `set.seed()` for reproducibility
- [x] Dependency checks with `requireNamespace()`
- [x] Session info recording
- [x] File reading instructions in SKILL.md
- [x] Modular script structure
- [x] Test data provided
- [x] Error handling with SKILL_* codes
- [x] Scripts in `scripts/` directory
- [x] References in `references/` directory
- [x] Local database support

---

*Last updated: 2026-04-15 | Version: 2.1.0*
