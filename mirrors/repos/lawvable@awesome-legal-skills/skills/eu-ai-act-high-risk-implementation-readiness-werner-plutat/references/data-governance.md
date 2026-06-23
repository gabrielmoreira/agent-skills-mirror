# Data Governance (Art. 10)

## Purpose

Article 10 focuses on the quality and governance of training, validation, and testing data sets used for high-risk AI systems, where relevant. In practice, the core question is:

**Can the organization explain where its data came from, why it is suitable, what its limits are, and what it did to reduce quality and bias problems?**

This is not a theoretical fairness essay. It is an operational evidence problem.

---

## What Article 10 requires in practice

Depending on the system and data architecture, readiness should cover:
- data collection/acquisition process
- relevance to intended purpose
- representativeness relative to the use context
- completeness and possible gaps
- error handling / data quality issues
- examination for possible bias
- data preparation and labeling controls
- assumptions and limitations documentation
- governance for changes to datasets and data pipelines

Not every system uses traditional training data in the same way, but every provider should still be able to explain the data basis for performance claims and risk controls.

---

## Evidence that should exist

A strong evidence set may include:
- dataset inventory
- data source/provenance record
- legal basis / acquisition basis notes
- data specifications / datasheets
- sampling rationale
- representativeness analysis
- bias examination record
- labeling guidelines and QA checks
- data cleaning/preprocessing procedure
- validation and test dataset design documentation
- change log for key data assets

If data was “collected over time by the business” without structured documentation, this area is usually RED or AMBER.

---

## Practical implementation questions

### 1. Relevance
- Does the data reflect the actual use case?
- Is it appropriate for the intended purpose and target population?
- Is the validation/testing data meaningfully separate from training data where relevant?

### 2. Representativeness
- Does the data cover relevant subgroups, contexts, geographies, languages, or edge cases?
- Are known blind spots documented?
- Is deployment planned in settings not reflected in the source data?

### 3. Completeness and errors
- What missingness patterns exist?
- What error sources exist in labels, source records, or preprocessing?
- How are corrupted, stale, or low-confidence data points treated?

### 4. Bias examination
- What potential sources of discriminatory or systematically skewed outcomes were considered?
- Was subgroup performance tested where relevant?
- Are there proxies or features that create indirect bias risks?

### 5. Governance
- Who approves data sources?
- Who decides when a dataset or pipeline change triggers re-validation?
- What documentation is retained for audits or reviews?

---

## Readiness scoring guide

### RED
- no dataset inventory
- provenance unclear
- no written suitability rationale
- no bias examination record
- no representativeness assessment
- validation/testing data not credibly designed

### AMBER
- some dataset documentation exists
- provenance mostly known but patchy
- bias or subgroup checks performed inconsistently
- relevance and representativeness partly explained
- change governance weak or informal

### GREEN
- documented inventory and provenance exist
- suitability, limitations, and subgroup/coverage issues are recorded
- bias examination is evidence-based and tied to risk management
- validation/testing datasets are designed intentionally
- change control and re-validation triggers are defined

---

## Common pitfalls

### 1. Confusing privacy compliance with Art. 10 compliance
GDPR matters, but Article 10 is not satisfied merely because personal data handling is lawful.

### 2. Using “large dataset” as a proxy for quality
A lot of data can still be biased, stale, unrepresentative, or poorly labeled.

### 3. Ignoring deployment context drift
Data that looked fine in one geography, language, or sector may underperform elsewhere.

### 4. No documentation of limitations
Teams often know limitations informally but never write them down. That becomes a major readiness gap.

### 5. No governance for changes
If the team regularly refreshes or swaps datasets without defined review thresholds, the control environment is weak.

---

## Practical next steps

### If RED
1. Build a dataset inventory
2. Document source, purpose, and use of each key dataset
3. Write a suitability and representativeness rationale
4. Run an initial bias examination focused on the actual use case
5. Document known limitations and missing data issues
6. Establish approval/change triggers for data updates

### If AMBER
1. Strengthen subgroup and edge-case analysis
2. Improve provenance documentation and versioning
3. Add explicit data quality metrics and thresholds
4. Tie data issues into risk management and technical documentation
5. Define re-validation events for data changes

---

## Practical checklist

For each key dataset or data source, capture:
- dataset name / version
- source and acquisition method
- intended use in the system
- population/context covered
- key exclusions / blind spots
- quality checks performed
- labeling method and QA
- known bias concerns
- suitability decision
- re-validation trigger
- owner

---

## What assessors will care about

They will usually look for:
- traceable provenance
- a credible explanation of fitness for purpose
- evidence that bias and quality issues were actively examined
- enough specificity to connect data choices to real deployment conditions
- documentation that survives scrutiny, not just engineering memory

That is the operational center of Art. 10.
