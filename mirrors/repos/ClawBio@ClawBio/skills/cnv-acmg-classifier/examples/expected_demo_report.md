# CNV ACMG Classification Report

**Input**: `/sessions/sleepy-sharp-ritchie/mnt/Bioclaw/skills/cnv-acmg-classifier/demo_cnv_calls.csv`
**Mode**: Synthetic demo data
**Framework**: ClinGen/ACMG 2019 (Riggs et al. 2020)
**CNVs classified**: 7

| CNV | Region | Type | Genes | Score | Classification | Evidence |
|---|---|---|---:|---:|---|---|
| CNV_P_TP53del | chr17:7,660,000-7,695,000 | loss | 1 | 1.00 | Pathogenic | 1A, 2A |
| CNV_LP_TP53partial | chr17:7,680,000-7,700,000 | loss | 1 | 0.90 | Likely pathogenic | 1A, 2C-1, 3A |
| CNV_B_benign | chr1:152,030,000-152,070,000 | loss | 1 | -1.00 | Benign | 1A, 2F |
| CNV_VUS_inh | chr2:50,120,000-50,180,000 | loss | 1 | -0.30 | Variant of uncertain significance | 1A, 3A, 5B |
| CNV_LB_caseev | chr2:50,120,000-50,180,000 | loss | 1 | -0.95 | Likely benign | 1A, 3A, 4, 5B |
| CNV_P_dup22q | chr22:18,800,000-21,600,000 | gain | 3 | 1.45 | Pathogenic | 1A, 2A, 5A |
| CNV_LP_genedense | chr19:51,990,000-52,410,000 | loss | 40 | 0.90 | Likely pathogenic | 1A, 3C |

## Tier counts

- Pathogenic: 2
- Likely pathogenic: 2
- Benign: 1
- Variant of uncertain significance: 1
- Likely benign: 1

## Interpretation

Scores follow the ClinGen/ACMG copy-number point framework: Pathogenic ≥ 0.99, Likely pathogenic 0.90–0.98, VUS −0.89 to 0.89, Likely benign −0.90 to −0.98, Benign ≤ −0.99. Section 3 gene-count points apply only when no established dosage gene/region is overlapped. Sections 4 (case/literature) and 5 (inheritance) reflect analyst-supplied evidence and are never auto-generated.

ClawBio is a research and educational tool. It is not a medical device and does not provide clinical diagnoses. Consult a healthcare professional before making any medical decisions.
