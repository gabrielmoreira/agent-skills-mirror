# GEO acquisition with geokit

Use this reference for the optional R adapter within `public-data-access`.
geokit is not a bundled Wisp MCP server. Discover the current Wisp tool catalog
before choosing operations; this guide does not introduce new tool names.

## Choose the operation

| Need | Route |
|---|---|
| Search studies or inspect a few series | Existing GEO connector or NCBI E-utilities; no R required |
| Parse SOFT records for GSE/GSM/GPL/GDS | `geokit::geo_soft()` downloads and parses into GEO S4 objects |
| Build an R ExpressionSet from series matrices | `geokit::geo_matrix()`; requires Biobase |
| Prepare sample characteristics | `geokit::parse_sample_data()` on a supported loaded object |
| Acquire selected supplementary files | Inspect the directory first, then `geokit::geo_suppl()` with a reviewed filename regex |
| Build a larger metadata collection | Batch selected accessions with `geokit::geo_meta()` as a standalone Run |

`geo_search(step=...)` fetches all matches in batches: `step` is not a total
result limit. Use bounded connector queries for discovery. `geo_meta()` filters
metadata during parsing but can still download full SOFT files.
`geo_suppl()` returns paths and does not parse arbitrary attachment formats.
The chat/Shiny helpers are unnecessary for acquisition through Wisp.

## Check the selected execution context

Check Rscript and required packages in the context that will run the job, not
only on the desktop. A standalone Run can declare an R preflight with packages
`geokit` and, for ExpressionSet output, `Biobase`. Missing packages should be
reported with setup instructions; discovery should not trigger installation.

Record the installed version with `packageVersion("geokit")` and save
`sessionInfo()` alongside the analysis. The upstream installation guide offers
R-universe and GitHub installation; available binaries depend on platform/R
version. Source installation requires Rust, so check the current package
requirements before selecting it. Reuse the user's configured proxy and
package sources.

For standalone downloads, save an R script under the project and run it through
the shared Run tools. Use the returned Run id for monitoring and cancellation.
For subsequent work on objects already loaded in the persistent R runtime,
continue in that runtime; a fresh Run cannot access those objects.

## Plan and acquire

1. Inspect series, platforms, samples, and candidate files through the existing
   connector or official GEO HTTPS directories. Record the selected URLs and
   known sizes; distinguish unknown sizes from zero. A supplementary pattern
   must be checked against the actual inventory before transfer.
2. Create the usual provider-neutral plan: provider `geo`, accession as the
   identifier, and data type `soft`, `series-matrix`, or `supplementary`.
   Transport describes the network path (`https` for GEO FTP over HTTPS), not
   the package name. Populate `provenance.adapter` with `geokit`,
   `adapter_version` with the installed version, and `query_url` with the stable
   source page. Record the selected file inventory and context/Run identity in
   a companion provenance file. Preserve both that file and the plan.
3. Set an explicit accession-specific `odir` in the selected context. Keep raw
   downloads separate from derived RDS/tables. On SSH, retain large outputs as
   remote references and harvest only selected small summaries or manifests.
4. Check that the adapter can satisfy the reviewed transfer. In the reviewed
   geokit version, existing filenames are reused without integrity checks and
   new downloads use `resume = FALSE`. Use `--no-resume` in a geokit plan and
   record that limitation. Verify cached files before reuse; an interrupted or
   unverified file is not a valid cache hit. If resumability or a strict byte
   limit is required, choose a downloader that enforces it before starting.
5. Validate the plan and record the authorization for the concrete transfer
   using the shared workflow. Planner limits are not automatically passed into
   geokit. If the selected files cannot be bounded as required, resolve that
   before invoking the helper.

For `geo_matrix()`, use `add_gpl = FALSE` unless platform annotation retrieval
is part of the plan, and keep `pdata_from_soft = FALSE` unless the additional
SOFT acquisition is needed and covered. These choices avoid implicit extra
downloads but do not restrict the number of matrix files fetched. Use
`ftp_over_https = TRUE` explicitly in download scripts.

## Validate and hand off

- A GSE can have several platform matrices. Preserve separate objects and
  identify the GSE/GPL/source file for each; do not merge them automatically.
- Missing files, a zero-row matrix, download failure, and parse failure are
  different outcomes. For an absent or empty assay, inspect supplementary
  counts or SRA/ENA references before proposing a new acquisition.
- Check expression dimensions, sample IDs/order against phenotype rows, and
  feature IDs against any annotation. Preserve original characteristics along
  with cleaned columns so duplicate or ambiguous fields remain inspectable.
- Keep assay values as retrieved. `log_trans()` is a heuristic transformation,
  not part of acquisition; gene-symbol conversion, normalization and
  differential expression belong to the subsequent analysis.
- Save ExpressionSet outputs as RDS when requested, plus a bounded summary and
  sample table for inspection. Return paths or remote references, dimensions,
  and validation findings instead of printing whole matrices into chat.
- Generate the manifest with the existing planner after checking the acquired
  files. The manifest records file inventory/checksums and a digest of the plan;
  it does not copy package provenance or validate biological correctness.

## Initial evaluation

Compare the current acquisition workflow with this adapter on a single-platform
matrix, a multi-platform series, and a study whose useful counts are in
supplementary files. Include an unavailable package and an interrupted transfer.
Record completion, manual interventions, file/sample completeness, and error
clarity. Live provider checks are manual; automated regression checks use local
fixtures and fake runners without R packages or network access.

## Sources and review boundary

Reviewed geokit R package 0.0.2 at commit
`3e0157737d4d3c948d55d155b1d73730a736ed13` on 2026-09-08. Check installed-version
behavior before using flags; this reference is Wisp-specific routing guidance.

- [Upstream skill](https://github.com/WangLabCSU/geokit/blob/3e0157737d4d3c948d55d155b1d73730a736ed13/pkgdown/assets/skills/geokit/SKILL.md)
- [Download implementation](https://github.com/WangLabCSU/geokit/blob/3e0157737d4d3c948d55d155b1d73730a736ed13/R/download.R)
- [Matrix implementation](https://github.com/WangLabCSU/geokit/blob/3e0157737d4d3c948d55d155b1d73730a736ed13/R/geo-matrix.R)
- [Package requirements and installation](https://github.com/WangLabCSU/geokit/tree/3e0157737d4d3c948d55d155b1d73730a736ed13)
- [GEO download documentation](https://www.ncbi.nlm.nih.gov/geo/info/download.html)
