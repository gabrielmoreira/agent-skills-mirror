#!/usr/bin/env python3
"""
Regenerate the binary demo fixtures (BAM + .bai, BigWig, BigBed) for the
polars-bio skill. These are committed to the repo so tests run offline; this
script lets a maintainer reproduce them deterministically.

Generation-time deps (NOT runtime deps of the skill):
    uv pip install pysam pyBigWig pybigtools

Usage:
    python skills/polars-bio/examples/generate_fixtures.py
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).parent
CONTIGS = [("chr1", 1000), ("chr2", 1000)]


def make_bam() -> None:
    import pysam

    bam_path = HERE / "demo.bam"
    header = {
        "HD": {"VN": "1.6", "SO": "coordinate"},
        "SQ": [{"SN": name, "LN": ln} for name, ln in CONTIGS],
    }
    reads = [
        ("r1", 0, 100, "20M"),
        ("r2", 0, 110, "20M"),
        ("r3", 0, 300, "20M"),
        ("r4", 1, 500, "20M"),
        ("r5", 1, 505, "20M"),
    ]
    with pysam.AlignmentFile(str(bam_path), "wb", header=header) as out:
        for name, tid, pos, cigar in reads:
            a = pysam.AlignedSegment(out.header)
            a.query_name = name
            a.reference_id = tid
            a.reference_start = pos
            a.mapping_quality = 60
            a.cigarstring = cigar
            a.query_sequence = "ACGT" * 5
            a.query_qualities = pysam.qualitystring_to_array("I" * 20)
            a.flag = 0
            out.write(a)
    pysam.index(str(bam_path))
    # Plain-text SAM alongside the BAM (same reads).
    with pysam.AlignmentFile(str(bam_path), "rb") as src, \
            pysam.AlignmentFile(str(HERE / "demo.sam"), "w", header=src.header) as sam:
        for rec in src:
            sam.write(rec)


def make_bigwig() -> None:
    import pyBigWig

    bw = pyBigWig.open(str(HERE / "demo.bw"), "w")
    bw.addHeader([(name, ln) for name, ln in CONTIGS])
    bw.addEntries("chr1", [0, 100, 200], values=[1.0, 2.0, 3.0], span=100)
    bw.addEntries("chr2", [0, 100], values=[4.0, 5.0], span=100)
    bw.close()


def make_bigbed() -> None:
    # pyBigWig cannot write BigBed; pybigtools (Rust) can.
    import pybigtools

    writer = pybigtools.open(str(HERE / "demo.bb"), "w")
    chroms = {name: ln for name, ln in CONTIGS}
    vals = [
        ("chr1", 10, 60, "f1\t0\t+"),
        ("chr1", 200, 260, "f2\t0\t+"),
        ("chr2", 500, 560, "f3\t0\t-"),
    ]
    writer.write(chroms, vals)


def main() -> None:
    make_bam()
    make_bigwig()
    try:
        make_bigbed()
    except Exception as exc:  # pyBigWig bigbed write is version-sensitive
        print(f"WARN: BigBed generation skipped: {exc}")
    print("Fixtures written to", HERE)


if __name__ == "__main__":
    main()
