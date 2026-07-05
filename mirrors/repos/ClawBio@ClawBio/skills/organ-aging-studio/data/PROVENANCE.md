# Data provenance — Organ Aging Studio

This skill does **not** ship large public cohorts. Use the bundled synthetic demo for CI and quick runs; download real datasets separately when validating on published cohorts.

## Bundled demo (via `proteomics-clock`)

| Field | Value |
|-------|--------|
| File | `../proteomics-clock/data/demo_olink_npx.csv.gz` |
| Type | **Synthetic** — no real patients |
| Samples | 20 (`DEMO_000` … `DEMO_019`) |
| Proteins | 26 Olink-style NPX columns |
| Purpose | Pipeline demo, tests, agent walkthrough |

See `proteomics-clock/data/PROVENANCE.md` for generation details.

Run without downloading anything:

```bash
python skills/organ-aging-studio/organ_aging_studio.py --demo --output /tmp/studio
```

## Optional real-world datasets (download separately)

These are **not** required to use the skill. They are useful for hackathon validation slides and cross-omics work.

### Filbin et al. 2021 — COVID Olink proteomics (real plasma)

- **Use case**: Real Olink NPX for Goeminne organ clocks (longitudinal Day 0/3/7)
- **Download**: [Mendeley Data — nf853r8xsj](https://doi.org/10.17632/nf853r8xsj.2) (3 Excel files)
- **Ingest**: `python skills/proteomics-clock/examples/fetch_filbin.py --data-dir <download_dir> --output <out_dir>`
- **Then**: Point `--input` at the processed CSV from that script

### GEO GSE40279 — Hannum 2013 whole-blood methylation (validation only)

- **Use case**: Show DNAm clocks correlate with age (r ≈ 0.9) on blood — **not** an input to this skill
- **Download** (pick one):
  - Supplemental beta chunks (~316 MB each): [GSE40279 on GEO](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE40279) → *Supplementary file*
  - Full average beta: `GSE40279_average_beta.txt.gz` (~1.2 GB)
- **Ages**: GEO series matrix `!Sample_title` field (`"age 67y 1001"`)
- **Clock skill**: Use ClawBio `methylation-clock` with a prepared pickle/CSV — see hackathon workspace `scripts/prepare_gse40279_blood.py` as a reference ingest pattern

### GEO GSE259312 — paired Olink + cfDNA methylation (2024)

- **Use case**: Future paired proteomic + epigenetic age on the **same** individuals
- **Download**: [GSE259312 on GEO](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE259312)
- **Status**: Requires custom prep; not bundled

## What not to do

- Do not commit GEO methylation matrices or Filbin raw Excel into this skill folder.
- Do not treat synthetic demo NPX as evidence that clocks track chronological age (expected r ≈ 0).
