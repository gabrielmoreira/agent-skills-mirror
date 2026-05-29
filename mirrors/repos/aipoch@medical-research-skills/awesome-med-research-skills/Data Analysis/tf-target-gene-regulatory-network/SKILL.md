---
name: tf-target-gene-regulatory-network
description: "Use when analyzing transcription factor (TF) regulatory networks using Dorothea database. Input gene list, identify regulating transcription factors, generate TF-Target network visualization. For: transcription factor enrichment analysis, gene regulatory network research."
license: MIT
skill-author: AIPOCH
---

# Transcription Factor (TF) Regulatory Network Analysis

## When to Use

- Use this skill when you have a human or mouse gene list and want to identify upstream TFs from the Dorothea database.
- Use it when you need a ready-to-export TF-target network table plus a publication-ready PDF network plot.
- Use it for reproducible CLI execution with saved session information and optional local Dorothea `.rds` databases.

## When Not to Use

- Do not use this skill for differential expression, pathway enrichment, cell type annotation, or survival analysis.
- Do not use it to infer causal direction beyond curated Dorothea TF-target relationships.
- Do not use it when your input genes are aliases or mixed-species symbols that have not been normalized first.

## Input Validation

This skill accepts: a human or mouse gene list (HGNC symbols for human, first-letter-uppercase for mouse) for TF regulatory network analysis using Dorothea.

If the user's request does not involve identifying upstream transcription factors from a gene list — for example, asking to run differential expression, pathway enrichment, cell type annotation, or multi-omics integration — do not proceed with the workflow. Instead respond:
> "tf-target-gene-regulatory-network is designed to identify upstream transcription factors from a gene list using the Dorothea database and generate a TF-target network visualization. Your request appears to be outside this scope. Please provide a gene list for TF regulatory analysis, or use a more appropriate tool for your task."

## Entry Point

- Primary CLI entry point: `scripts/main.R`
- Canonical visualization values: English tokens `fr`, `curve`, `diamond`, `triangle`, `square`

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

This creates `database/dorothea_hs.rds` (human) and `database/dorothea_mm.rds` (mouse) in the skill root directory.

### Verification

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
| `-g` | `--gene` | character | NULL | Comma-separated gene list (e.g., `"TP53,MYC,EGFR"`) — **required if `--gene_file` not provided** |
| `-f` | `--gene_file` | character | NULL | File with gene names (txt or csv, one per line or comma-separated) — **required if `--gene` not provided** |
| `-s` | `--species` | character | `human` | Species: `human` or `mouse` |
| `-o` | `--output_dir` | character | `TF_Result` | Output directory name |
|  | `--db_path` | character | NULL | Local `.rds` database file path. If not specified, auto-searches default paths |
| `-d` | `--dir` | character | NULL | Working root directory (advanced) |
|  | `--seed` | integer | `42` | Random seed for reproducibility |
|  | `--title` | character | `""` | Main plot title |

**Visualization Parameters**: For complete list (plot dimensions, colors, labels, layout, edge styles), see [`references/visualization-parameters.md`](references/visualization-parameters.md). Canonical values are English tokens: `fr` (force-directed layout), `curve` (curved edges), `diamond` / `triangle` / `square` (node shapes).

---

## Input Format

### Gene List Input

Two ways to provide input genes:

1. **Command line**: `--gene "TP53,MYC,EGFR"` (comma-separated)
2. **File input**: `--gene_file genes.txt` (one gene per line or comma-separated)

### Gene Naming Convention

- **Human genes**: All uppercase symbols (e.g., TP53, MYC, EGFR)
- **Mouse genes**: First letter uppercase only (e.g., Tp53, Myc, Egfr)
- Use official gene symbols, not aliases
- Case-sensitive for species matching

### Species Support

- `human`: Human genes (Homo sapiens)
- `mouse`: Mouse genes (Mus musculus)

### Performance Guidance

For large gene lists (> 500 genes), Dorothea database queries may take several minutes. Use a local `.rds` database (`--db_path`) for substantially faster lookups. There is currently no `--timeout_seconds` parameter; monitor progress with verbose logging if available.

---

## Output Files

| File | Description |
|------|-------------|
| `TF_Network_Plot.pdf` | TF-target network visualization |
| `tf_network.xlsx` | Network data (edges and nodes worksheets) |
| `TF_Target_Filtered_Core_<species>.xlsx` | Complete TF-target relationships table |
| `session_info.txt` | R session and package version info |
| `tf.Rdata` | R environment data |

Outputs are organized under `TF_Result/` in `data/`, `plot/`, and `table/` subdirectories.

---

## Workflow

### Step 1: Load Database
- Priority search for local database files (.rds format) in: `--db_path`, `getwd()/database/`, `script_dir/database/`, `dirname(script_dir)/database/`
- If no local file found, load from Dorothea R package
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
- **Layout algorithms**: Multiple options including `fr` (force-directed), `circle`, `grid`, `sphere`
- **Visual customization**: Full control over colors, shapes, sizes

### Local Database Feature
- Option to use pre-saved `.rds` files for faster analysis and offline use
- Priority search paths for local database files (see Step 1 above)
- Fallback to Dorothea R package if no local file found

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

| Error Code | Cause | Solution |
|------------|-------|----------|
| `SKILL_FILE_NOT_FOUND` | Input gene file does not exist | Check file path and permissions |
| `SKILL_NO_INPUT_GENES` | Empty gene list or file | Provide genes using `--gene` or `--gene_file` |
| `SKILL_INVALID_SPECIES` | Species not `human` or `mouse` | Use `human` or `mouse` only |
| `SKILL_INVALID_PARAMETER` | Invalid layout, shape, line, or legend value | Use supported values shown by `Rscript scripts/main.R --help` |
| `SKILL_EMPTY_RESULTS` | No TF-target relationships found for input genes | Check gene symbols and species; try broadening confidence levels |
| `SKILL_DEPENDENCY_MISSING` | Missing dplyr, dorothea, tidygraph, etc. | Install missing packages (see Installation section) |

### Exit Status Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Execution error (see error code for details) |
| `2` | `SKILL_EMPTY_RESULTS` — no TF-target matches found for the input genes |

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

After running, verify `tests/output_human/plot/TF_Network_Plot.pdf` and `tests/output_human/table/tf_network.xlsx` exist and are non-empty.

## Reference Files

| File | Purpose |
|---|---|
| `references/algorithm.md` | Statistical methods and Dorothea database details |
| `references/troubleshooting.md` | Common errors and solutions |
| `references/cli-guide.md` | CLI usage examples |
| `references/visualization-parameters.md` | Complete visualization parameter list |
