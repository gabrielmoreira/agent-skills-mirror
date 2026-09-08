---
name: public-data-access
description: "Plan, validate, and document public-bioinformatics data acquisition for GEO/GSE/GSM/GPL/GDS, SRA/ENA, TCGA/GDC, GTEx, and DepMap. Covers expression matrices, raw reads, download manifests, caches, and optional geokit SOFT/Series Matrix acquisition for R workflows."
---

# Public Bioinformatics Data Access

Build a reproducible acquisition plan before downloading. Treat GEO, SRA/ENA,
GDC, GTEx, and DepMap as independent providers behind one provider-neutral
workflow. Do not require a provider-specific toolkit or machine-specific checkout.

## Workflow

1. **Clarify the dataset contract.** Identify the provider, accession/project,
   release, modality, smallest useful data product, filters, target directory,
   expected scale, and downstream analysis.
2. **Inspect before transfer.** Use available MCP/connectors or official
   metadata endpoints to list releases, files, samples, sizes, and checksums.
   Do not start a bulk transfer during discovery.
3. **Write a provider-neutral plan.** Run `scripts/public_data_plan.py init`.
   Store the plan next to the future dataset as `download-plan.json`.
4. **Validate and review.** Run `validate`, show the user the resolved provider,
   transport, filters, limits, output location, and known size. For a large,
   paid, authenticated, or overwrite-capable job, confirm that the user's
   authorization covers this concrete transfer; ask only when it does not.
5. **Select the adapter at runtime.** Prefer an already available Wisp MCP tool
   for metadata and small queries. Prefer official HTTPS/FTP or provider clients
   for bulk files. Use an external project only when it is installed and record
   its version in the plan/manifest.
6. **Acquire safely.** Reuse existing valid files, resume partial transfers when
   supported, keep raw files immutable, and never place credentials in the plan.
7. **Verify and hand off.** Check expected files, byte sizes, checksums when
   available, and sample/file counts. Generate `manifest.json` with the script.

## Provider routing

| Provider | Discovery and small queries | Bulk acquisition | Typical products |
|---|---|---|---|
| GEO | GEO metadata connector, NCBI E-utilities | NCBI GEO HTTPS/FTP; optional geokit in R | series matrix, SOFT, supplementary files |
| SRA/ENA | RunInfo or ENA Portal API | ENA HTTPS/FTP or SRA Toolkit | FASTQ, run metadata |
| GDC | GDC files/cases API | manifest + `gdc-client`, or HTTPS for bounded files | expression, mutation, CNV, clinical, methylation |
| GTEx | GTEx expression connector/API | official release files for matrices | gene/tissue queries, median or sample expression |
| DepMap | DepMap model/release metadata | official release file endpoint | model metadata, expression, mutation, dependency |
| custom | User-provided catalog/API | explicit HTTPS/FTP URLs | provider-specific files |

Read `references/provider-routing.md` before implementing or changing a
provider adapter. DepMap-specific flags or release semantics must stay inside
the DepMap adapter; they must not shape the common plan schema.

For GEO SOFT/Series Matrix parsing, sample metadata preparation, or
ExpressionSet acquisition in an R workflow, read
[references/geokit.md](references/geokit.md). geokit is optional; ordinary GEO
discovery does not require R or package installation.

## Create and validate a plan

Resolve `scripts/public_data_plan.py` against this skill's directory (the
`use_skill` result lists its path), and invoke that resolved script with a
Python 3.10+ interpreter. Keep the working directory at the project root so
relative plan/output paths belong to the project. The examples below abbreviate
the script path; quote the resolved path when it contains spaces. In an SSH/WSL
context, stage the helper there or use an existing copy in that context; a
desktop skill path is not automatically available remotely.

```bash
python scripts/public_data_plan.py init \
  --provider geo \
  --identifier GSE12345 \
  --data-type series-matrix \
  --output-dir data/public/geo/GSE12345 \
  --plan data/public/geo/GSE12345/download-plan.json

python scripts/public_data_plan.py validate \
  data/public/geo/GSE12345/download-plan.json
```

Filters are provider-specific but encoded uniformly as repeated `key=value`
pairs:

```bash
python scripts/public_data_plan.py init \
  --provider gdc \
  --identifier TCGA-BRCA \
  --data-type expression \
  --filter workflow_type="STAR - Counts" \
  --filter sample_type="Primary Tumor" \
  --max-files 20 \
  --transport gdc-client \
  --plan data/public/gdc/TCGA-BRCA/download-plan.json
```

The planner does not download data. It produces a reviewable contract. See
`references/download-plan-schema.md` for the complete schema. Validation checks
the plan structure; it does not probe URLs, enforce transfer limits, verify
installed packages, or approve a pending transfer. The selected adapter must
honor the plan's limits and resume behavior.

## Generate a manifest

After acquisition:

```bash
python scripts/public_data_plan.py manifest \
  data/public/geo/GSE12345/download-plan.json \
  --scan-dir data/public/geo/GSE12345 \
  --output data/public/geo/GSE12345/manifest.json
```

Use SHA-256 for modest datasets and provider checksums for large archives. For
very large datasets, `--checksum none` is acceptable only when official
checksums or immutable object identifiers are recorded elsewhere.

## Safety and reproducibility rules

- Default to `overwrite=false`, `resume=true`, and the minimum useful subset.
- Never translate an exploratory request into “download everything.”
- Keep provider metadata, query/filter payloads, release/version, transport,
  tool version, URLs/object identifiers, and validation results.
- Separate immutable source files from normalized/derived outputs.
- Do not treat a successful HTTP response as a valid dataset; verify content.
- Do not embed API keys, cookies, signed URLs, SSH keys, or bearer tokens.
- Use structured runs or a remote execution context for long transfers rather
  than extending an interactive shell timeout.
- If an adapter or connector cannot perform the requested transfer, stop after
  producing the validated plan and report the missing capability explicitly.

## Wisp Science integration

- Discover the live connector/tool catalog instead of assuming exact MCP tool
  names; installations can expose different provider adapters.
- Use connectors for discovery and bounded queries, then official transfer
  mechanisms for large files.
- Keep outputs under the active project, normally `data/public/<provider>/...`.
- Invoke the planner as a standalone CLI; no Python REPL helper loading is
  required. R-based acquisition can use geokit independently of the planner.
- Treat this skill as an acquisition/orchestration layer. Downstream QC,
  statistics, annotation, and visualization belong to other skills.
