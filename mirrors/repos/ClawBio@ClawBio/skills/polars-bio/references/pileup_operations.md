# Pileup / per-base depth

`pb.depth(path, ...)` computes per-base read depth from an alignment file with
CIGAR-aware counting. The ClawBio `pileup` subcommand wraps it.

## Signature

```python
pb.depth(
    path,
    filter_flag=1796,          # exclude unmapped/secondary/dup/QC-fail by default
    min_mapping_quality=0,     # MAPQ threshold
    binary_cigar=True,
    dense_mode="auto",
    use_zero_based=None,
    per_base=False,            # True for strict per-base rows
    output_type="polars.LazyFrame",
)
```

Output columns (observed): `contig, pos_start, pos_end, coverage`. The result is
**mosdepth-compatible**.

## Requirements & gotchas

- **Index required**: BAM needs a `.bai` (`samtools index aln.bam`); the ClawBio runner
  errors clearly if it is missing. CRAM additionally needs a `reference_path`.
- **MAPQ filtering**: raise `min_mapping_quality` (e.g. 20) to drop low-confidence reads.
- **filter_flag** defaults to 1796 (exclude unmapped, secondary, QC-fail, duplicate).
- **Large BAMs**: increase `datafusion.execution.target_partitions` for parallel region
  processing on indexed files.

## Integration

Pipe depth into interval ops — e.g. `merge` high-coverage windows, or `overlap` depth
intervals against target regions — since the output is a standard interval DataFrame.
