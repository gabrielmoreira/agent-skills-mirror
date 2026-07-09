# Xena TCGA Gene Query — Demo Output Example

This file shows the expected output from running:

```bash
python skills/xena-tcga-gene-query/scripts/query_tcga_api.py --demo --output /tmp/xena_demo
```

## report.md (excerpt)

```markdown
# Xena TCGA Gene Query Report

**Date**: 2026-07-06 12:00:00 UTC
**API base URL**: http://biotree.top:38123/ucscxena/
**Mode**: demo (synthetic data — no live API calls)
**Queries**: diff-expr (TP53 in LUAD), corr (TP53 vs EGFR in LUAD), survival (TP53 in LUAD)

---

## 1. Differential Expression — TP53 in LUAD

**Gene**: TP53
**Cancer**: LUAD (Lung Adenocarcinoma)
**Tumor samples**: n = 515
**Normal samples**: n = 59

| Metric | Value |
|--------|-------|
| Tumor mean (log2) | 5.12 |
| Normal mean (log2) | 4.87 |
| log2 Fold Change | 0.25 |
| Mann-Whitney p | 0.0034 |

...
```

## result.json (structure)

```json
{
  "diff_expr": {
    "gene": "TP53",
    "cancer": "LUAD",
    "cancer_full_name": "Lung Adenocarcinoma",
    "tumor": { "n": 515, "mean": 5.12, "median": 5.08, "std": 0.89 },
    "normal": { "n": 59, "mean": 4.87, "median": 4.91, "std": 0.76 },
    "log2_fold_change": 0.25,
    "p_value": 0.0034
  },
  "corr": {
    "gene1": "TP53", "gene2": "EGFR",
    "cancer": "LUAD", "n": 508,
    "spearman_r": 0.18,
    "p_value": 4.2e-05
  },
  "survival": {
    "gene": "TP53", "cancer": "LUAD",
    "survival": {
      "OS": { "n_total": 504, "n_events": 189, "median_cutoff": { "p_value": 0.042 } },
      "DSS": { "n_total": 494, "n_events": 142, "median_cutoff": { "p_value": 0.11 } },
      "DFI": { "n_total": 312, "n_events": 84, "median_cutoff": { "p_value": 0.67 } },
      "PFI": { "n_total": 504, "n_events": 218, "median_cutoff": { "p_value": 0.031 } }
    }
  }
}
```

## reproducibility/commands.sh

```sh
#!/bin/sh
BASE_URL="${UCSCXENA_API_BASE_URL:-http://biotree.top:38123/ucscxena/}"
curl "${BASE_URL}/api/v1/diff-expr?gene=TP53&cancer=LUAD"
curl "${BASE_URL}/api/v1/corr?gene1=TP53&gene2=EGFR&cancer=LUAD"
curl "${BASE_URL}/api/v1/survival?gene=TP53&cancer=LUAD"
```

## reproducibility/run.json

```json
{
  "skill": "xena-tcga-gene-query",
  "mode": "demo",
  "base_url": "http://biotree.top:38123/ucscxena/",
  "timestamp_utc": "2026-07-06T12:00:00.000000+00:00",
  "python_version": "3.10.x ..."
}
```
