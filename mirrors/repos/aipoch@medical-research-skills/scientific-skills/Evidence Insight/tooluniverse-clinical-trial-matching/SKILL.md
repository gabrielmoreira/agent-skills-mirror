---
name: tooluniverse-clinical-trial-matching
description: AI-driven patient-to-trial matching for precision medicine and oncology. Given a patient profile (disease, molecular alterations, stage, prior treatments), discovers and ranks clinical trials from ClinicalTrials.gov using multi-dimensional matching across molecular eligibility...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Clinical Trial Matching for Precision Medicine

Transform patient molecular profiles and clinical characteristics into prioritized clinical trial recommendations. Searches ClinicalTrials.gov and cross-references with molecular databases (CIViC, OpenTargets, ChEMBL, FDA) to produce evidence-graded, scored trial matches.

**KEY PRINCIPLES**:
1. **Report-first approach** - Create report file FIRST, then populate progressively
2. **Patient-centric** - Every recommendation considers the individual patient's profile
3. **Molecular-first matching** - Prioritize trials targeting patient's specific biomarkers
4. **Evidence-graded** - Every recommendation has an evidence tier (T1-T4)
5. **Quantitative scoring** - Trial Match Score (0-100) for every trial
6. **Eligibility-aware** - Parse and evaluate inclusion/exclusion criteria
7. **Actionable output** - Clear next steps, contact info, enrollment status
8. **Source-referenced** - Every statement cites the tool/database source
9. **Completeness checklist** - Mandatory section showing analysis coverage
10. **English-first queries** - Always use English terms in tool calls. Respond in user's language

---

## When to Use

Apply when user asks:
- "What clinical trials are available for my NSCLC with EGFR L858R?"
- "Patient has BRAF V600E melanoma, failed ipilimumab - what trials?"
- "Find basket trials for NTRK fusion"
- "Breast cancer with HER2 amplification, post-CDK4/6 inhibitor trials"
- "KRAS G12C colorectal cancer clinical trials"
- "Immunotherapy trials for TMB-high solid tumors"
- "Clinical trials near Boston for lung cancer"
- "What are my options after failing osimertinib for EGFR+ NSCLC?"

**NOT for** (use other skills instead):
- Single variant interpretation without trial focus -> Use `tooluniverse-cancer-variant-interpretation`
- Drug safety profiling -> Use `tooluniverse-adverse-event-detection`
- Target validation -> Use `tooluniverse-drug-target-validation`
- General disease research -> Use `tooluniverse-disease-research`

---

## Input Parsing

### Required Input
- **Disease/cancer type**: Free-text disease name (e.g., "non-small cell lung cancer", "melanoma")

### Strongly Recommended
- **Molecular alterations**: One or more biomarkers (e.g., "EGFR L858R", "KRAS G12C", "PD-L1 50%", "TMB-high")
- **Stage/grade**: Disease stage (e.g., "Stage IV", "metastatic", "locally advanced")
- **Prior treatments**: Previous therapies and outcomes (e.g., "failed platinum chemotherapy", "progressed on osimertinib")

### Optional
- **Performance status**: ECOG or Karnofsky score (e.g., "ECOG 0-1")
- **Geographic location**: City/state for proximity filtering (e.g., "Boston, MA")
- **Trial phase preference**: I, II, III, IV, or "any"
- **Intervention type**: drug, biological, device, etc.
- **Recruiting status preference**: recruiting, not yet recruiting, active

### Biomarker Parsing Quick Reference

| Input Format | Parsed As | Example |
|-------------|-----------|---------|
| Gene + amino acid change | Specific mutation | EGFR L858R |
| Gene + exon notation | Exon-level alteration | EGFR exon 19 deletion |
| Gene + fusion partner | Fusion | EML4-ALK fusion |
| Gene + amplification | Copy number gain | HER2 amplification |
| Gene + expression level | Expression biomarker | PD-L1 50% |
| Gene + status | Status biomarker | MSI-high, TMB-high |
| Gene + resistance | Resistance mutation | EGFR T790M |

### Gene Symbol Normalization

| Common Alias | Official Symbol | Notes |
|-------------|----------------|-------|
| HER2 | ERBB2 | Search both in trials |
| PD-L1 | CD274 | Often searched as "PD-L1" in trials |
| ALK | ALK | EML4-ALK is a fusion |
| VEGF | VEGFA | Often searched as "VEGF" |
| PD-1 | PDCD1 | Search as "PD-1" in trials |
| BRCA | BRCA1/BRCA2 | Specify which BRCA gene |

> Detailed parsing rules and regex patterns: see [references/parsing_and_validation.md](references/parsing_and_validation.md)

---

## Workflow Overview

| Phase | Name | Summary |
|-------|------|---------|
| 0 | Tool Parameter Reference | Verify all tool parameters before calling. See [references/phases_detail.md](references/phases_detail.md) |
| 1 | Patient Profile Standardization | Resolve disease→EFO ID, genes→Ensembl/Entrez IDs, classify biomarker actionability |
| 2 | Broad Trial Discovery | Disease/biomarker/intervention searches on ClinicalTrials.gov, deduplicate results |
| 3 | Trial Characterization | Batch-fetch eligibility, interventions, locations, status, descriptions for candidate NCT IDs |
| 4 | Molecular Eligibility Matching | Parse eligibility text for biomarker requirements, score patient-trial molecular match (0-40) |
| 5 | Drug-Biomarker Alignment | Identify trial drug mechanisms via OpenTargets/ChEMBL, verify target overlap with patient biomarkers |
| 6 | Evidence Assessment | FDA approval, PubMed literature, CIViC evidence, evidence tier classification (T1-T4) |
| 7 | Geographic & Feasibility | Trial site locations, enrollment status, proximity to patient location |
| 8 | Alternative Options | Basket/tumor-agnostic trials, expanded access, compassionate use programs |
| 9 | Scoring & Ranking | Calculate Trial Match Score (0-100), assign tier, rank trials |
| 10 | Report Synthesis | Generate markdown report with executive summary, ranked trials, evidence grading, checklist |

> Detailed phase execution code and tool call examples: see [references/phases_detail.md](references/phases_detail.md)

---

## Trial Match Score (0-100)

### Score Components

| Component | Max Points | Key Criteria |
|-----------|-----------|--------------|
| **Molecular Match** | 40 | Exact variant match=40, Gene-level=30, Pathway=20, No criteria=10, Excluded=0 |
| **Clinical Eligibility** | 25 | All criteria met=25, Most=18, Some=10, Ineligible=0 |
| **Evidence Strength** | 20 | FDA-approved (T1)=20, Phase III (T2)=15, Phase II (T3)=10, Phase I (T4)=5 |
| **Trial Phase** | 10 | Phase III=10, Phase II=8, Phase I/II=6, Phase I=4 |
| **Geographic Feasibility** | 5 | Patient's city=5, Same country=3, International=1, Unknown=0 |

### Recommendation Tiers

| Score | Tier | Label | Action |
|-------|------|-------|--------|
| **80-100** | Tier 1 | Optimal Match | Strongly recommend - contact site immediately |
| **60-79** | Tier 2 | Good Match | Recommend - discuss with care team |
| **40-59** | Tier 3 | Possible Match | Consider - needs further eligibility review |
| **0-39** | Tier 4 | Exploratory | Backup option - consider if Tier 1-3 unavailable |

> Detailed scoring rules, evidence tier definitions, and matching algorithms: see [references/scoring_and_matching.md](references/scoring_and_matching.md)

---

## Output Format

Report file: `clinical_trial_matching_[DISEASE]_[BIOMARKER]_[DATE].md`

### Required Sections

1. **Executive Summary** - Top 3 trial recommendations with scores
2. **Patient Profile Summary** - Standardized disease/biomarker/stage table
3. **Ranked Trial Matches** - Per-trial score breakdown, eligibility, evidence, locations
4. **Trials by Category** - Targeted/Immuno/Combination/Basket groupings
5. **Additional Testing Recommendations** - Biomarkers that unlock more trials
6. **Alternative Options** - Expanded access, off-label options
7. **Evidence Grading Summary** - T1-T4 counts
8. **Completeness Checklist** - Analysis step status tracking
9. **Disclaimer** - Research-only notice
10. **Sources** - Data source list

> Full report template with markdown structure: see [references/phases_detail.md#phase-10-report-synthesis](references/phases_detail.md)

---

## Edge Cases & Common Pitfalls

1. **ClinicalTrials.gov query complexity** - Overly specific queries often return zero results. Start simple, then combine.
2. **CIViC search limitations** - `civic_search_variants`/`civic_search_evidence_items` do NOT filter by query. Use `civic_get_variants_by_gene` with gene ID instead.
3. **No matching trials** - Broaden to gene-level → pathway-level → basket trials → suggest biomarker testing.
4. **Rare biomarkers** - Search gene-level trials, check CIViC, note rarity, suggest molecular tumor board.
5. **Multiple biomarkers** - Search independently + in combination, score by most actionable.
6. **Conflicting eligibility** - Score partial match transparently, highlight met/unmet criteria.

> Full edge case handling and use patterns: see [references/parsing_and_validation.md](references/parsing_and_validation.md)

---

## Known CIViC Gene IDs

| Gene | CIViC ID | Gene | CIViC ID |
|------|----------|------|----------|
| ALK | 1 | MET | 52 |
| ABL1 | 4 | PIK3CA | 37 |
| BRAF | 5 | ROS1 | 118 |
| EGFR | 19 | RET | 122 |
| ERBB2 | 20 | NTRK1 | 197 |
| KRAS | 30 | NTRK2 | 560 |
| TP53 | 45 | NTRK3 | 561 |

---


## Input Validation

This skill accepts requests that match the documented purpose of `tooluniverse-clinical-trial-matching` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `tooluniverse-clinical-trial-matching` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

| File | Content |
|------|---------|
| [references/phases_detail.md](references/phases_detail.md) | Phase 0-10 detailed execution code, tool call examples, parameter tables, report template |
| [references/scoring_and_matching.md](references/scoring_and_matching.md) | Scoring algorithm details, drug-biomarker alignment rules, evidence tier classification, matching logic |
| [references/parsing_and_validation.md](references/parsing_and_validation.md) | Biomarker parsing regex, eligibility text parsing, gene resolution code, edge case handling, common use patterns |
