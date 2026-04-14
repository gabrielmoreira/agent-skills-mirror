---
id: database_access_index
name: Database Access Skills Index
description: |
  Skills for querying and downloading data from genomic, transcriptomic,
  and single-cell databases. Covers programmatic access to public repositories,
  gene annotation, sequence retrieval, and large-scale single-cell data.
---

# Database Access Skills

Tools and workflows for accessing public biological databases, retrieving
sequencing data, querying gene/protein information, and downloading
large-scale single-cell datasets.

## Available Skills

### gget — Genomic Database Querying

Python package and CLI tool with 23 interoperable modules for efficiently
querying genomic databases including Ensembl, NCBI, UniProt, ARCHS4,
Enrichr, COSMIC, OpenTargets, CellxGene, cBioPortal, PDB, and Bgee.

**Skill file**: [gget.md](./gget.md)

**When to use**:
- Fetching reference genome/annotation download links (Ensembl)
- Searching genes by keyword or retrieving gene metadata
- Running BLAST/DIAMOND sequence alignment
- Performing enrichment analysis (GO, KEGG, pathway)
- Querying cancer mutations (COSMIC) or drug-target associations (OpenTargets)
- Retrieving single-cell data from CZ CELLxGENE Discover
- Looking up protein structures (PDB, AlphaFold)
- Finding tissue expression patterns (ARCHS4, Bgee)
- Plotting cancer genomics heatmaps (cBioPortal)

---

### iSeq — Sequencing Data Download

Bash CLI tool for downloading sequencing data and metadata from five public
databases (GSA, SRA, ENA, DDBJ, GEO) through a single unified interface.
Supports parallel downloads, Aspera transfers, and automatic format conversion.

**Skill file**: [iseq.md](./iseq.md)

**When to use**:
- Downloading raw sequencing data (FASTQ/SRA) from public repositories
- Fetching metadata for projects, experiments, or runs
- Downloading from Chinese GSA database (CRA/CRR accessions)
- Batch downloading multiple accessions from a file
- Converting SRA files to FASTQ format
- Merging FASTQ files by experiment, sample, or study

---

### CZ CELLxGENE Census — Single-Cell RNA-seq Data Access

Cloud-based Python API for accessing 217M+ single-cell RNA-seq observations
from CZ CELLxGENE Discover via TileDB-SOMA. Supports flexible metadata
queries, gene filtering, and pre-computed embeddings (scVI, Geneformer).

**Skill file**: [cellxgene_census.md](./cellxgene_census.md)

**When to use**:
- Querying large-scale single-cell RNA-seq data by tissue, cell type, disease
- Downloading count matrices as AnnData objects with metadata filters
- Accessing pre-computed embeddings (scVI, Geneformer)
- Finding which datasets contain specific genes or cell types
- Working with larger-than-memory single-cell datasets via streaming
- Exploring CZ CELLxGENE Discover catalog programmatically

---

## Using Skills

1. **Identify your goal**: Determine whether you need to query gene/protein
   information (gget), download raw sequencing data (iSeq), or access
   curated single-cell datasets (CELLxGENE Census)
2. **Load skill file**: Read the full skill document for detailed guidance
3. **Follow examples**: Use the code snippets provided for your specific task
4. **Combine tools**: These tools complement each other — use gget to explore
   genes, iSeq to download raw data, and Census to access processed datasets
