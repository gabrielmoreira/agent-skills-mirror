---
name: compute-envs-reference
description: Worked package recipes for common scientific stacks — install order, system libraries, egress needs, a validation witness, and the traps each stack hides. Consulted from compute-env-setup when assembling a user-space environment on a direct SSH context.
---

# Environment recipes

Nothing below is provisioned automatically — each entry is a tested recipe
to translate into an idempotent setup script for the selected SSH context.
Container base images and resource tiers are the conditions the recipe was
verified under, not requirements: substitute probed, user-writable paths and
the actual hardware. When done, record the activation command and the
validation evidence in the project; do not assume any environment-name
resolver exists.

Quick index (base / GPU / verified tier):

| recipe | base image | GPU | tier |
|---|---|---|---|
| dataml-cpu | python:3.12-slim | — | 4c/16G |
| bio-cpu | python:3.12-slim | — | 4c/16G |
| chem-cpu | python:3.12-slim | — | 4c/16G |
| singlecell-cpu | python:3.12-slim | — | 8c/32G |
| genomics-cpu | python:3.12-slim | — | 8c/64G |
| imaging-cpu | python:3.12-slim | — | 4c/32G |
| torch-geometric-gpu | pytorch:2.7.1-cu126-runtime | sm_90 | 1gpu/32G |

## CPU recipes

All six install in a single pip phase on `python:3.12-slim`, need no model
weights and no network egress at runtime. What varies is only the apt-level
shared libraries the wheels link against, plus any CLI binaries.

### dataml-cpu — general ML / stats

- System libs: `libgomp1 build-essential`
- Python: scikit-learn, xgboost, statsmodels, pymc, arviz, shap,
  umap-learn, networkx, dask[complete], polars, zarr, gcsfs, s3fs, aeon,
  pymoo
- Witness: RF + XGBoost fit on a 200×5 toy set scores (1.0, 1.0); polars
  DataFrame round-trips.
- Traps: on some mirrors the name `aeon` resolves to a 0.0.0 squatter —
  pin `aeon>=1.0`. The xgboost wheel drags in `nvidia-nccl-cu12`, ~200MB of
  dead weight on a CPU box.

### bio-cpu — sequence / omics toolkits

- System libs: `libgomp1 build-essential libgl1 libglib2.0-0` (the glib is
  what pyopenms's `.so` links against)
- Python: biopython, prody, biotite, scikit-bio, pyopenms, ete3, cobra,
  neurokit2, FlowIO, matchms, numpy, scipy, pandas
- Witness: ubiquitin FASTA through ProtParam → 76 aa, MW 8564.7, pI 6.56.
- Traps: none encountered.

### chem-cpu — cheminformatics

- System libs: `build-essential libxrender1 libxext6 libsm6 libgomp1`
  (the X libraries serve rdkit's 2D drawing)
- Python: rdkit, openbabel-wheel, datamol, useful_rdkit_utils, molfeat,
  PyTDC, aizynthfinder
- Weights: aizynthfinder's retrosynthesis data is *not* baked in —
  `download_public_data` stays a runtime step.
- Witness: aspirin SMILES → MolWt 180.16, Morgan fingerprint with 24
  on-bits.
- Traps: PyTDC transitively pulls torch + jupyter + scanpy (~250 packages)
  and forces sklearn to build from source — ~19 min and ~5GB. Drop it
  unless TDC datasets are actually needed.

### singlecell-cpu — scRNA-seq

- System libs: `libgomp1 build-essential`
- Python: scanpy, anndata, leidenalg, igraph, scrublet, cellxgene-census,
  samap
- Witness: scanpy normalize → PCA → neighbors → leiden on a 100×50 random
  AnnData yields one cluster.
- Traps: louvain has no py3.12 wheel (leidenalg covers the need). samap has
  historically pinned scanpy<1.10 — drop samap on conflict.

### genomics-cpu — alignment / variant stacks

- System libs: `samtools bedtools bwa spades wget bzip2 build-essential
  libgomp1 libcurl4-openssl-dev libbz2-dev liblzma-dev`
- Extra step: Debian apt only carries legacy `bwa`; fetch the bwa-mem2
  v2.2.1 static tarball into `/opt` and symlink the dispatcher plus arch
  variants into `/usr/local/bin/`.
- Python: pysam, deeptools, gtars, pydeseq2, anndata, biopython
- Witness: bwa-mem2 indexes an 800bp reference, aligns 2 reads, pysam
  parses the SAM (`2.2.1 2`).
- Traps: bwa-mem2 preallocates a fixed 3.6GB of host RAM regardless of
  reference size — the tier needs `mem_gib≥32`.

### imaging-cpu — medical / slide imaging

- System libs: `libopenslide0 libopenslide-dev libvips42 libgl1
  libglib2.0-0 build-essential`
- Python: pydicom, pylibjpeg, pylibjpeg-libjpeg, openslide-python, pillow,
  scikit-image
- Witness: sobel filter over 128×128 random uint8 → mean 0.2256; pydicom
  imports cleanly.
- Traps: histolab was dropped (pins numpy<1.22). openslide-python needs the
  apt `libopenslide0`; the wheel alone is not enough.

## GPU recipe

### torch-geometric-gpu

Isolated in its own environment for one reason: PyG's compiled wheels lag
each torch release by weeks, and their URL encodes the torch minor version
plus CUDA variant.

- Base: `pytorch/pytorch:2.7.1-cuda12.6-cudnn9-runtime`
- System libs: `git build-essential`
- Install in three ordered phases:
  1. `pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv`
     with `find_links=https://data.pyg.org/whl/torch-2.7.0+cu126.html` —
     that page is flat HTML, not PEP-503, so it must be `find_links`, never
     `extra_index`.
  2. `torch_geometric` — pure Python, no version coupling.
  3. `lightning>=2.2` — Trainer workflows are the usual PyG consumer;
     including it keeps the env self-contained.
- Egress: `github.com raw.githubusercontent.com codeload.github.com
  data.pyg.org` (`torch_geometric.datasets.*` downloads benchmark data).
- Witness: `GCNConv(8→4)` forward returns a `(4,4)` CUDA tensor; a 2-layer
  KarateClub forward+backward shows decreasing loss.
