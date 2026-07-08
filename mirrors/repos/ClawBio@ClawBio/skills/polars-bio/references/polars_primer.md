# Polars & the Python ecosystem — a polars-bio primer

> Citation: Wiewiórka M, Khamutou P, Zbysiński M, Gambin T. **polars-bio — fast,
> scalable, and out-of-core operations on large genomic interval datasets.**
> *Bioinformatics*, 2025, 41(12):btaf640. https://doi.org/10.1093/bioinformatics/btaf640

ClawBio has no other skill that explains Polars, so this primer establishes the
DataFrame context an agent needs before running polars-bio operations.

## What Polars is

[Polars](https://pola.rs) is a DataFrame library written in Rust:

- **Columnar + multithreaded**, built on the **Apache Arrow** memory model (zero-copy
  interchange with pyarrow, pandas ≥3.0, DuckDB, etc.).
- **Two execution modes**:
  - **`DataFrame`** — eager, like pandas: each operation runs immediately.
  - **`LazyFrame`** — lazy: you build a query plan, the optimizer rewrites it
    (predicate/projection pushdown, common-subplan elimination), and `.collect()`
    executes it, optionally with a **streaming** engine for out-of-core data.
- This lazy model is why polars-bio can process genomes larger than RAM.

## Polars vs pandas (when to reach for which)

| | pandas | Polars |
|---|---|---|
| Engine | single-threaded C/NumPy | multithreaded Rust |
| Memory | NumPy blocks | Apache Arrow |
| Laziness | eager only | eager **and** lazy/streaming |
| Big-than-RAM | no | yes (streaming) |

polars-bio ships a **pandas compatibility mode** (`pip install "polars-bio[pandas]"`,
pandas ≥3.0); functions accept and can return pandas DataFrames. Prefer native Polars
for large data; use pandas interop only at the edges of an existing pandas pipeline.

## The stack underneath polars-bio

```
        your analysis (Polars LazyFrame / DataFrame, or pandas)
                              |
                    polars-bio  (.pb accessor, genomic readers, SQL)
                              |
   Apache Arrow  --  Apache DataFusion  --  datafusion-bio-formats
  (columnar memory)   (query / SQL engine)     (BED/VCF/BAM/GFF/... readers)
                              |
                        Rust interval backends
                      (ruranges, superintervals)
```

polars-bio tracks recent Apache DataFusion releases (with a matching pyarrow floor).

## Where polars-bio fits

polars-bio extends Polars with genomics so interval work lives in the *same* pipeline
as the rest of an analysis — no detour through bedtools or pandas:

- **`.pb` accessor** on `LazyFrame` for method-chaining interval ops:
  `df.lazy().pb.overlap(other)`.
- **Genomic-aware readers**: `read_*` / `scan_*` / `register_*` for BED, VCF, GFF, GTF,
  FASTA, FASTQ, BAM, CRAM, BigWig, BigBed, VCF Zarr.
- **DataFusion SQL** over registered files via `pb.sql(...)`.

### Interop

- `df.to_pandas()` / pandas inputs (compat mode).
- Arrow hand-off to pyarrow (zero-copy).
- `output_type="polars.DataFrame"` for eager results from any operation.

## Ecosystem neighbors

polars-bio produces output comparable to **bioframe**, **pyranges1**, **pybedtools**,
and **GenomicRanges**, while being faster and able to stream. It is accelerated by the
Rust crates **`ruranges`** and **`superintervals`** under a DataFusion UDTF execution
model. Reported figures (see the paper and the polars-bio blog, dated): 6–38× faster
than bioframe on interval benchmarks; ~20–28M rows/s streaming throughput; substantially
faster VCF parsing; ~20× lower memory than vanilla Polars on GFF reads.
