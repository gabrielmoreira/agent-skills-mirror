---
id: single_cell_spatial_mapping
name: Single-Cell to Spatial Mapping
description: |
  Map single-cell RNA-seq data to spatial transcriptomics data using
  optimal transport (MOSCOT). Enables gene imputation and cell type transfer.
tags: [spatial, mapping, imputation, moscot]
---

# Single-Cell to Spatial Mapping with MOSCOT

This skill describes how to use [moscot](https://moscot.readthedocs.io/en/latest/)
to map single-cell data to spatial data with Optimal Transport, and how to impute
genes/features that are not observed in the spatial data.

## Prerequisites

```bash
pip install moscot
```

## Workflow

### 1. Load the Data

```python
adata_sc = ...  # single-cell data (AnnData)
adata_sp = ...  # spatial data (AnnData)
```

### 2. Pre-Mapping Checks

Before mapping, verify:

a. **Cell and gene counts**: Check dimensions of both datasets
b. **Normalization consistency**: Both datasets should be normalized equally
   (e.g., both log1p transformed). Check min/mean/max of expression values.

```python
print(f"SC: {adata_sc.shape}, SP: {adata_sp.shape}")
print(f"SC X range: {adata_sc.X.min():.2f} - {adata_sc.X.max():.2f}")
print(f"SP X range: {adata_sp.X.min():.2f} - {adata_sp.X.max():.2f}")
```

### 3. Filter Cell Cycle Genes (Optional)

Cell cycle genes can dominate the mapping. Consider filtering:

```python
s_genes = ["RRM2", "DSCC1", "PRIM1", "GMNN", "CCNE2", "E2F8", "EXO1", 
           "RAD51AP1", "WDR76", "USP1", "NASP", "CASP8AP2", "RAD51", 
           "MSH2", "PCNA", "FEN1", "RRM1", "CDC6", "CLSPN", "POLA1", 
           "TYMS", "SLBP", "CENPU", "MCM5", "TIPIN", "MCM4", "MCM6", 
           "RFC2", "UNG", "CHAF1B", "CDC45", "HELLS", "MRPL36", "POLR1B", 
           "BLM", "CDCA7", "DTL", "UHRF1", "UBR7", "MCM7", "GINS2"]

g2m_genes = ["NEK2", "CDCA8", "SMC4", "LBR", "ANP32E", "HMMR", "AURKB", 
             "CDC20", "KIF11", "RANGAP1", "CDK1", "GTSE1", "TPX2", "NDC80", 
             "CKAP2", "MKI67", "ECT2", "G2E3", "CENPE", "NCAPD2", "PIMREG", 
             "CDC25C", "CENPF", "TUBB4B", "CENPA", "BUB1", "PSRC1", "NUF2", 
             "TOP2A", "GAS2L3", "NUSAP1", "TACC3", "CBX5", "AURKA", "CDCA3", 
             "KIF2C", "BIRC5", "HMGB2", "KIF20B", "TTK", "TMPO", "UBE2C", 
             "CKS2", "DLGAP5", "CKAP2L", "ANLN", "CKAP5", "HJURP", "CCNB2", 
             "CKS1B", "CDCA2", "KIF23", "CTCF"]

cellcycle_genes = set(s_genes + g2m_genes)
cellcycle_genes = {g.upper() for g in cellcycle_genes}

# Filter to shared non-cell-cycle genes
shared_genes = adata_sc.var_names.intersection(adata_sp.var_names)
filter_genes = [g for g in shared_genes if g.upper() not in cellcycle_genes]

adata_sc_filt = adata_sc[:, filter_genes].copy()
adata_sp_filt = adata_sp[:, filter_genes].copy()
```

### 4. Perform Mapping

```python
from moscot.problems.space import MappingProblem

mp = MappingProblem(adata_sc_filt, adata_sp_filt)
mp = mp.prepare(sc_attr={"attr": "X"}, sp_attr={"attr": "X"})
mp = mp.solve(alpha=0, tau_a=1, tau_b=0.8)
```

**Parameters:**
- `alpha`: Interpolation between quadratic (1) and linear (0) terms
  - `alpha=0`: Pure linear optimal transport
  - `alpha=1`: Pure Gromov-Wasserstein
- `tau_a`: Source marginal unbalancedness (1 = balanced)
- `tau_b`: Target marginal unbalancedness (1 = balanced)

> [!TIP]
> For typical scRNA-seq to spatial mapping, start with `alpha=0, tau_a=1, tau_b=0.8`.
> Documentation: https://moscot.readthedocs.io/en/latest/user/genapi/moscot.problems.space.MappingProblem.solve.html

### 5. Get Transport Matrix

```python
# Get the transport matrix
pi = mp.solutions[('src', 'tgt')].transport_matrix
pi = np.array(pi)  # Convert to numpy if needed
```

### 6. Impute Gene Expression

Impute genes from scRNA-seq to spatial coordinates:

```python
from anndata import AnnData

# Impute all SC genes to spatial coordinates
gexp_sc = adata_sc.X
imputed_X = pi.dot(gexp_sc)

# Create new AnnData with imputed expression
adata_imputed = AnnData(
    X=imputed_X, 
    obsm=adata_sp.obsm.copy(),
    obs=adata_sp.obs.copy()
)
adata_imputed.obs_names = adata_sp.obs_names
adata_imputed.var_names = adata_sc.var_names
```

### 7. Transfer Cell Type Labels

Map cell type annotations from single-cell to spatial:

```python
import numpy as np

def map_labels_via_transport(pi, labels):
    """
    Map labels from source (SC) to target (SP) via transport matrix.
    
    Args:
        pi: Transport matrix, shape (n_sc, n_sp)
        labels: Array of labels for SC cells
    
    Returns:
        Mapped labels for SP cells, confidence scores
    """
    unique_labels, inv = np.unique(labels, return_inverse=True)
    n_labels = len(unique_labels)
    
    # One-hot encoding: M[i, k] = 1 iff labels[i] == unique_labels[k]
    M = np.eye(n_labels, dtype=pi.dtype)[inv]
    
    # Score for each label at each SP location
    # pi.T @ M: (n_sp, n_sc) @ (n_sc, n_labels) -> (n_sp, n_labels)
    scores = pi.T.dot(M)
    
    # Normalize by sum of transport weights per SP cell
    scores_normalized = scores / scores.sum(axis=1, keepdims=True)
    
    # Assign label with highest score
    best_idx = scores_normalized.argmax(axis=1)
    mapped_labels = unique_labels[best_idx]
    confidence = scores_normalized.max(axis=1)
    
    return mapped_labels, confidence

# Apply
mapped_celltypes, conf = map_labels_via_transport(
    pi, 
    adata_sc.obs['celltype'].values
)
adata_sp.obs['mapped_celltype'] = mapped_celltypes
adata_sp.obs['mapping_confidence'] = conf
```

## Large Dataset Handling

> [!WARNING]
> For large datasets (>100k cells), consider:
> - Subsampling single-cell data while preserving cell type ratios
> - Using GPU acceleration if available
> - Processing spatial data in chunks if memory-limited

```python
# Example: subsample to 50k cells per type
sc.pp.subsample(adata_sc, n_obs=50000)
```

## Quality Assessment

After mapping, visualize results:

```python
import scanpy as sc

# Visualize mapped cell types on spatial coordinates
sc.pl.spatial(adata_sp, color='mapped_celltype', spot_size=1)

# Check mapping confidence distribution
sc.pl.violin(adata_sp, 'mapping_confidence')
```
