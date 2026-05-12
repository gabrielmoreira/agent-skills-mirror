---
name: lncrna-regulatory-network-construction-analysis
description: Use this bioinformatics data analysis skill to construct a database-driven lncRNA-mRNA regulatory network from target lncRNA and/or gene lists by projecting shared miRNA evidence from local ceRNA reference tables. It does not infer networks from expression matrices.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# lncRNA Regulatory Network Construction Analysis

## When to Use

Use this skill when the user wants a local-database network lookup workflow rather than expression-based inference.

Typical use cases:

- Build an lncRNA-mRNA network from target genes and the bundled ceRNA reference tables
- Start from a candidate lncRNA list and retrieve linked mRNAs through shared miRNAs
- Generate an auditable lncRNA-mRNA network table plus a tripartite evidence table
- Reuse a saved database-derived network object to regenerate a PDF plot

Do not use this skill when the user asks for:

- Expression-matrix-based network inference
- Correlation analysis between lncRNAs and mRNAs
- Causal inference or regulatory-strength estimation from expression data
- Online database querying or remote API lookups

## Execution Model

This is a hybrid skill.

1. Read `SKILL.md` to confirm that the request is database-driven.
2. Use `scripts/main.R` for actual execution.
3. Use `--mode analyze` to build tables and a saved `.rda` object.
4. Use `--mode visualize` to reuse the saved object and redraw the PDF without rebuilding the database tables.
5. Use `--mode full` to run both steps in one pass.
6. Read reference files only when more detail is needed.
7. Before `--mode visualize`, confirm that `output_dir/data/lncrna_network.rda` already exists.
8. In `visualize` mode, the saved `.rda` object is the required input; a missing or invalid `reference_dir` does not block plot reuse.
9. After execution, report the mode, output directory, key files, and either the retained network size or the surfaced skill error code.

## When to Read External Files

| Situation | File to Read | Purpose |
|-----------|--------------|---------|
| Need algorithm details | `references/algorithm.md` | Understand the shared-miRNA projection logic |
| Need troubleshooting help | `references/troubleshooting.md` | Review error codes and fixes |
| Need CLI examples or the baseline record | `references/cli-guide.md` | Review installation, examples, and the recorded run |
| Need runnable demo inputs | `tests/data/` | Use the bundled target gene and lncRNA lists |
| Need actual execution | `scripts/main.R` | Run the CLI workflow |

## Out-of-Scope Response Pattern

If the request is expression-based rather than database-driven, do not run this skill. Respond briefly with:

> This skill only projects lncRNA-mRNA links from local ceRNA reference tables using target gene and/or lncRNA lists. It does not infer networks from expression matrices or estimate causal regulatory strength. Use a different workflow for expression-based correlation or causal inference.

If the request is ambiguous between database-driven lookup and expression-based inference, ask one short clarifying question before running any command.

## Agent Response Contract

For a successful run, report:

- The selected mode and why it fits the request
- The `output_dir`
- The key output files that were generated or reused
- The retained network size from `table/network_stats.txt` when available
- A short reminder that the result is database-driven rather than expression-inferred

For a failed run, report:

- The surfaced `SKILL_*` error code
- The most likely cause based on `references/troubleshooting.md`
- The shortest actionable next step for rerunning the workflow

## Usage

```bash
Rscript scripts/main.R \
  --mode full \
  --target_genes ./target_genes.txt \
  --target_lncrna ./target_lncrna.txt \
  --mirna_dataset combined \
  --lncrna_strictness High \
  --min_shared_mirna 1 \
  --reference_dir ./references/database \
  --output_dir ./output \
  --seed 42
```

## Arguments

| Long | Type | Default | Description |
|------|------|---------|-------------|
| `--mode` | character | `full` | Run mode: `analyze`, `visualize`, or `full` |
| `--target_genes` | character | empty | Target gene list file or comma-separated gene list |
| `--target_lncrna` | character | empty | Target lncRNA list file or comma-separated lncRNA list |
| `--mirna_dataset` | character | `combined` | miRNA-mRNA dataset: `combined`, `starbase`, `mirdb`, `mirtarbase`, `starbase+mirdb`, `starbase+mirtarbase`, or `mirdb+mirtarbase` |
| `--lncrna_strictness` | character | `High` | miRNA-lncRNA strictness: `Low`, `Median`, or `High` |
| `--lncrna_freq_thresh` | integer | `0` | Minimum lncRNA degree threshold after edge aggregation |
| `--min_shared_mirna` | integer | `1` | Minimum shared miRNA count for keeping an lncRNA-mRNA edge |
| `--reference_dir` | character | `references/database` | Local directory containing the bundled ceRNA reference tables; required for `analyze` and `full` |
| `--output_dir` | character | `tests/output` | Output directory inside the skill root |
| `--plot_file` | character | `lncrna_mrna_network.pdf` | PDF file name under `plot/` |
| `--plot_title` | character | `lncRNA-mRNA Regulatory Network` | Plot title |
| `--layout_type` | character | `kk` | Plot layout: `kk`, `fr`, `circle`, or `nicely` |
| `--width` | double | `14` | Plot width in inches |
| `--height` | double | `9` | Plot height in inches |
| `--node_size_base` | double | `6` | Base node size |
| `--node_size_scale` | double | `1.5` | Node size increment per degree |
| `--lncrna_color` | character | `#1f77b4` | lncRNA node color |
| `--mrna_color` | character | `#d62728` | mRNA node color |
| `--seed` | integer | `42` | Random seed |
| `--timeout_seconds` | integer | `0` | Optional timeout in seconds; `0` disables it |

## Input Format

### Target Gene List

- Plain-text file or comma-separated list
- One gene symbol per line when using a file

Example:

```text
TP53
BRCA1
MYC
```

### Target lncRNA List

- Plain-text file or comma-separated list
- One lncRNA symbol per line when using a file

Example:

```text
XIST
SNHG16
HNRNPU-AS1
```

At least one of `--target_genes` or `--target_lncrna` must be provided.

## Output Files

| File | Description |
|------|-------------|
| `table/lncrna_mrna_edges.csv` | Projected lncRNA-mRNA network with shared-miRNA counts and labels |
| `table/lncrna_mirna_mrna_evidence.csv` | Tripartite evidence table with one lncRNA-miRNA-mRNA row per evidence chain |
| `table/lncrna_mrna_nodes.csv` | Node table with node type and degree |
| `table/network_stats.txt` | Network summary statistics |
| `data/lncrna_network.rda` | Serialized R object used by visualization mode |
| `plot/lncrna_mrna_network.pdf` | Projected lncRNA-mRNA network PDF |
| `session_info.txt` | R session and package version record |
| `output_manifest.txt` | Append-only manifest of generated outputs |
| `run_record.txt` | Append-only run history with parameters, runtime, and output summary |

## Error Handling

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `SKILL_FILE_NOT_FOUND` | A required list file, reference file, or saved result object is missing | Check the path and rerun |
| `SKILL_MISSING_COLUMNS` | A required database column is absent | Validate the reference table format |
| `SKILL_EMPTY_DATA` | No target IDs, evidence rows, or final edges remained | Broaden the target list or relax filtering |
| `SKILL_INVALID_PARAMETER` | A CLI argument is missing, invalid, or unsafe | Recheck the parameter table |
| `SKILL_SAMPLE_MISMATCH` | Reserved for workflows expecting matched entities | Not expected in the database-only workflow |
| `SKILL_PACKAGE_NOT_FOUND` | Required R packages are missing | Install the packages from `references/cli-guide.md` |

## Progressive Disclosure

1. Start with `--target_genes` or `--target_lncrna`.
2. Add the second target list if a more focused subnetwork is needed.
3. Switch `--mirna_dataset` if a different miRNA-mRNA evidence source is required.
4. Adjust `--lncrna_strictness`, `--lncrna_freq_thresh`, and `--min_shared_mirna` to tighten or relax the projected network.
5. Reuse `--mode visualize` once the `.rda` object exists.

## Result Size Guidance

- Broad gene-only or lncRNA-only runs can expand quickly and may retain hundreds to thousands of edges.
- If the retained network is too large for practical review, report the edge and node totals, then increase `--min_shared_mirna`, increase `--lncrna_freq_thresh`, or provide the complementary target list.
- Start with the bundled demo inputs before moving to broader target lists.

## Examples

### Gene-Driven Network

```bash
Rscript scripts/main.R \
  --mode full \
  --target_genes ./target_genes.txt \
  --reference_dir ./references/database \
  --output_dir ./output
```

### lncRNA-Driven Network

```bash
Rscript scripts/main.R \
  --mode analyze \
  --target_lncrna ./target_lncrna.txt \
  --mirna_dataset starbase \
  --lncrna_strictness Median \
  --output_dir ./lncrna_only_output
```

### Focused Bipartite Network

```bash
Rscript scripts/main.R \
  --mode full \
  --target_genes TP53,BRCA1,MYC \
  --target_lncrna XIST,SNHG16,HNRNPU-AS1 \
  --mirna_dataset combined \
  --lncrna_strictness High \
  --min_shared_mirna 2 \
  --output_dir ./focused_output
```

### Visualization Reuse

```bash
Rscript scripts/main.R \
  --mode visualize \
  --output_dir ./focused_output \
  --plot_file reused_network.pdf \
  --layout_type fr
```

For the bundled baseline and CLI notes, read `references/cli-guide.md`.

## Testing

```bash
Rscript scripts/main.R --help

Rscript tests/run_tests.R

Rscript scripts/main.R \
  --mode full \
  --target_genes tests/data/target_genes.txt \
  --target_lncrna tests/data/target_lncrna.txt \
  --reference_dir references/database \
  --output_dir tests/output \
  --seed 42
```

Expected retained outputs after a validated run:

- `tests/output/table/lncrna_mrna_edges.csv`
- `tests/output/table/lncrna_mirna_mrna_evidence.csv`
- `tests/output/table/lncrna_mrna_nodes.csv`
- `tests/output/table/network_stats.txt`
- `tests/output/data/lncrna_network.rda`
- `tests/output/plot/lncrna_mrna_network.pdf`
- `tests/output/session_info.txt`
- `tests/output/output_manifest.txt`
- `tests/output/run_record.txt`

## Scope Limits

This skill does not infer networks from expression matrices and does not perform online queries.

If the user needs expression-based correlation or causal inference, use a different workflow.
