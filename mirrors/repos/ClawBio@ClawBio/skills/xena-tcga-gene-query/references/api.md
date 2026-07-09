# API Reference

Base URL defaults to `http://biotree.top:38123/ucscxena/` (primary, fast). Fallback: `https://ucscxenatoolspy.onrender.com`.

Authentication: if configured, send `X-API-Key: <key>`.

## Endpoints

### GET /health

Returns `{ "status": "ok" }`. Use for availability checks.

### GET /api/v1/cancers

Returns available cancer codes with tumor and normal sample counts.

Important fields:
- `count`: number of cancer entries.
- `cancers[].cancer`: TCGA abbreviation such as LUAD, BRCA, KIRC.
- `cancers[].tumor_n`, `normal_n`, `has_normal`.

### GET /api/v1/diff-expr?gene=TP53&cancer=LUAD

Compares primary tumor vs normal tissue expression using Mann-Whitney U.

Important fields:
- `gene`: resolved gene symbol.
- `gene_input`: original input when alias/ID was resolved.
- `tumor.n`, `normal.n`: always mention these.
- `tumor.mean`, `normal.mean`: expression values on log2(TPM + 0.001) scale.
- `log2_fold_change`: tumor mean minus normal mean on log2 scale.
- `p_value`: statistical association, not causality.

If normal samples are insufficient, the API returns 400 with an error message.

### GET /api/v1/corr?gene1=TP53&gene2=EGFR&cancer=LUAD

Computes Spearman correlation in primary tumor samples.

Important fields:
- `n`: common tumor samples with both genes.
- `spearman_r`: rank correlation; positive means co-varying expression, negative means inverse rank trend.
- `p_value`: correlation test p-value.

### GET /api/v1/survival?gene=TP53&cancer=LUAD

Runs log-rank tests for OS, DSS, DFI, and PFI using median and exploratory optimal cutoffs.

Important fields per endpoint:
- `n_total`, `n_events`: always mention before p-values.
- `median_cutoff`: pre-specified median split; usually the primary report.
- `optimal_cutoff`: minimum-p scan across candidate cutoffs; exploratory only.
- `optimal_cutoff_note`: remind users that p-values are not adjusted for multiple cutoff testing.
- high/low group `n`, `n_events`, and `mean_survival_days`.

## Interpretation Guardrails

- TCGA associations are research signals, not clinical decisions.
- P-values are not multiple-testing corrected across genes/cancers unless the user performs additional correction.
- Survival optimal cutoffs are hypothesis-generating.
- Check sample size and event counts before emphasizing biological meaning.
- Alias resolution can change user input, e.g. HER2 -> ERBB2; mention it.
