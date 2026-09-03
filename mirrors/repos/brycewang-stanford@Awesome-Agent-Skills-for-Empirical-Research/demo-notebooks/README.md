# demo-notebooks — flagship pipeline demos on LaLonde / Card–Krueger

End-to-end runs of the `skills/00.x` flagship pipelines against classic
datasets. Files accumulate by *skill version*, so several generations coexist;
this index says which is which.

## Which version is current?

| Stack | Current demo | Older generations (kept for comparison) |
|---|---|---|
| StatsPAI | `StatsPAI_skill_lalonde_full_pipeline-v2-executed.ipynb` (+ `statsPAI_pipeline_5.2.py`, outputs in `_statspai_pipeline_outputs_5.2/`) | `StatsPAI_skill_lalonde_full_pipeline.ipynb`, `_statspai_pipeline_outputs/`, `_statspai_pipeline_outputs_v2/` |
| Python | `Python_skill_lalonde_full_pipeline.ipynb` (outputs in `_python_pipeline_outputs/`) | — |
| R | `R_skill_lalonde_full_pipeline.ipynb` (outputs in `_r_pipeline_outputs_5.2/`) | `_r_pipeline_outputs/` |
| Stata | `Stata_skill_lalonde_v2_pipeline.do` + `.log` (outputs in `_stata_lalonde_outputs_v5.2/`) | `Stata_skill_lalonde_full_pipeline.do` + `.log`, `_stata_lalonde_outputs/` |

Suffix conventions: `_5.2` / `v5.2` = runs against skill v5.2; `v2` = second
notebook generation; no suffix = original run. The committed Stata `.log`
files are the run evidence for the `.do` demos.

## Other contents

- `_lalonde_data.csv` — shared input data (LaLonde / NSW).
- `manuscript_docx_demo.py` + `_manuscript_docx_demo/` — the **last hop**: raw
  exhibits → a full-text Word manuscript. Every other demo here stops at tables
  and figures, and the analysis-only export that shipped with them
  (`_statspai_pipeline_outputs_5.2/replication/paper.docx`) is 5 tables, 0
  figures and no prose — a table bundle, not a paper. This script feeds the same
  committed exhibits through `skills/69-Paper-WorkFlow/scripts/assemble_manuscript_docx.py`
  and produces `_manuscript_docx_demo/09_submission/main.docx`: body + Table 2 +
  a figure + reference list in one file. It then runs all four Stage 9 gates
  (deliverable contract, three-line tables, numeric anchoring, typeset drift) and
  **exits non-zero if any fails**, so it is a gate rather than an illustration.
  Needs the `69-Paper-WorkFlow` submodule; `pandoc` is optional (without it the
  assembler uses its stdlib builtin writer).
- `card-krueger-1994/` — Card & Krueger (1994) minimum-wage DiD, replicated
  from the official raw survey file (`tests/test_ck_replication.py`).
- `card-1995-iv/` — Card (1995) returns to schooling, replicated from the
  vendored NLSYM extract with standard errors and the first stage
  (`tests/test_card1995_replication.py`).
- `nsw-lalonde-1986/` — the NSW experimental benchmark (+$1,794) derived from
  the randomized arms, next to the −$635 the same 185 treated men produce
  against the PSID comparison group in `_lalonde_data.csv`. This is where the
  literature constant in `benchmark/tasks/lalonde-recovery.toml` comes from
  (`tests/test_nsw_replication.py` pins the two together).

Both are zero-dependency scripts that **exit non-zero when a published anchor
is missed**, so they are gates rather than illustrations. They answer a
different question from `benchmark/`: the benchmark asks whether *your* pipeline
gets a known-by-construction number right, while these show that *this*
pipeline reaches a *published* number from real data.

When adding a new generation, add a row (or move the old one to the right
column) instead of leaving the reader to guess which files are current.
