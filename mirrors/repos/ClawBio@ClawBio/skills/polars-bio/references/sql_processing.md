# SQL processing (Apache DataFusion)

polars-bio registers bioinformatics files as SQL tables and queries them with the
DataFusion SQL engine. The ClawBio `sql` subcommand registers `--input` as table `t`
(by extension) and runs `--query`.

## Register functions

`register_bed`, `register_vcf`, `register_vcf_zarr`, `register_gff`, `register_gtf`,
`register_fasta`, `register_fastq`, `register_bam`, `register_cram`,
`register_sam`, `register_bigwig`, `register_bigbed`, `register_pairs`, and
`register_view` (register a custom view). `from_polars(name, df)` registers an existing
Polars DataFrame as a table.

```python
import polars_bio as pb
pb.register_vcf("samples.vcf.gz", name="variants")
pb.register_bed("regions.bed", name="regions")
result = pb.sql("SELECT chrom, start, end, ref, alt FROM variants WHERE qual > 30")
df = result.collect()        # pb.sql returns a LazyFrame
```

> **Note:** `register_fastq` does not accept a `parallel` keyword — call it without
> that argument.

## Query semantics

- `pb.sql(query)` returns a **LazyFrame**; `.collect()` to materialize.
- Indexed formats (VCF/BAM/GFF/Pairs with TBI/CSI/BAI) get **WHERE-clause predicate
  pushdown** and projection pushdown.
- Registered VCF tables expose `chrom, start, end, id, ref, alt, qual, filter` plus
  requested FORMAT/sample columns; BED tables expose `chrom, start, end, name, ...`.

## Combining SQL with interval ops

Register two files, pre-filter with SQL, then hand the LazyFrames to an interval op —
all lazy, all in one DataFusion plan:

```python
pb.register_bed("a.bed", name="a")
hits = pb.sql("SELECT * FROM a WHERE chrom = 'chr1'")     # LazyFrame
merged = pb.merge(hits, output_type="polars.DataFrame")
```
