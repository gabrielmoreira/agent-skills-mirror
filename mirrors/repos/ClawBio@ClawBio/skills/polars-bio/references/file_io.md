# File I/O

polars-bio reads bioinformatics formats with `read_*` (eager) and `scan_*` (lazy,
streaming) functions, writes with `write_*`/`sink_*`, and inspects schemas with
`describe_*`. Cloud paths (`s3://`, `gs://`, `az://`) and compression (GZIP/BGZF) are
supported; the ClawBio `io` subcommand uses the `scan_*` readers.

## Reader functions, indexes & key parameters

The canonical *format list* lives in SKILL.md's **Input Formats** table; this table adds
the reader-level detail (function names, index requirements, notable parameters).

| Format | Functions | Index | Notable params |
|--------|-----------|-------|----------------|
| BED | `scan_bed` / `read_bed` / `register_bed` | — | `use_zero_based` (output representation; CLI defaults 0-based half-open, `--one-based` overrides); **>=4 cols required** |
| VCF | `scan_vcf` / `read_vcf` / `register_vcf` / `describe_vcf` | TBI/CSI | `info_fields`, `samples`; predicate pushdown |
| VCF Zarr | `scan_vcf_zarr` / `read_vcf_zarr` / `register_vcf_zarr` / `describe_vcf_zarr` | — | local Zarr directory store |
| GFF / GTF | `scan_gff` / `scan_gtf` / `register_*` | TBI/CSI (GFF) | `attr_fields` to project attributes |
| FASTA | `scan_fasta` / `register_fasta` | — | columns: name, description, sequence |
| FASTQ | `scan_fastq` / `register_fastq` | GZI | + quality_scores; multi-member gzip handled; `register_fastq` has no `parallel` kwarg |
| BAM | `scan_bam` / `read_bam` / `register_bam` / `describe_bam` | BAI/CSI | `tag_fields` for ~40 SAM tags |
| CRAM | `scan_cram` / `register_cram` / `describe_cram` | CRAI | **`reference_path` required** |
| SAM | `scan_sam` / `register_sam` / `describe_sam` | — | text alignments |
| Pairs | `scan_pairs` / `register_pairs` | TBI/CSI | Hi-C contacts |
| BigWig | `scan_bigwig` / `register_bigwig` | — | signal → chrom,start,end,value |
| BigBed | `scan_bigbed` / `register_bigbed` | — | intervals → chrom,start,end(+rest) |

**Recent additions:** BigWig + BigBed I/O, VCF Zarr describe/registration, `register_fasta`.
**Recent fixes:** FASTQ column normalization before writing; reading all members of
multi-member gzip FASTQ; correct BED 0-based half-open coordinates (#413).

## Schema inspection (`--describe`)

`describe_vcf`, `describe_bam`, `describe_cram`, `describe_sam`, `describe_vcf_zarr`
return a schema/field table **without a full read** — cheap way to learn a file's INFO/
FORMAT fields or alignment columns. The ClawBio CLI exposes this via `io --describe`
(VCF/BAM).

## BAM optional tags

`scan_bam(..., tag_fields=[...])` selectively parses ~40 common SAM tags (NM, MD, AS, RG,
CB, UB, ...) with zero overhead when unused.

## Performance tips

- Prefer `scan_*` over `read_*` for files larger than RAM (streaming + pushdown).
- Use BGZF (`.gz` via bgzip) for parallel block decompression.
- Select columns early to cut memory.
- GFF reads scale near-linearly to ~8 threads with projection/predicate pushdown
  (~20× less memory than vanilla Polars, per the docs).
