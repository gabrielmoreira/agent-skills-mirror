---
name: clinical-trial-finder
description: Find clinical trials for a gene, variant, or condition from ClinicalTrials.gov + EUCTR, with FHIR R4 output
license: MIT
author: Duvet05 <gonzalo.galvezc@pucp.edu.pe>
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## Domain Decisions

- **Source database**: ClinicalTrials.gov API v2 (`https://clinicaltrials.gov/api/v2`) — the authoritative US registry mandated by FDAAA 801 (2007) and mirrored by WHO ICTRP. Chosen over EudraCT/EUCTR because it covers the largest global trial volume (>500 000 studies), provides a stable versioned REST API, and is the primary registry for FDA-regulated interventions. Reference: Zarin et al., *NEJM* 2011; 364:852–860.

- **Query field**: `query.cond` (condition/disease field), not `query.term` (free-text across all fields). `query.cond` is indexed against MeSH descriptors by the NLM indexing pipeline, giving substantially better recall for condition queries than unstructured text search. Reference: ClinicalTrials.gov API v2 specification, `https://clinicaltrials.gov/data-api/api`.

- **MeSH condition coding**: MeSH IDs are read from `derivedSection.conditionBrowseModule.meshes` — the NLM-curated MeSH mapping that ClinicalTrials.gov computes internally during study indexing. This avoids a separate NLM API call and uses the same vocabulary that `query.cond` is indexed against, ensuring query/result consistency. Reference: NLM Medical Subject Headings, `https://www.nlm.nih.gov/mesh/`.

- **Max results**: 20 trials per query by default (configurable with `--max-results`). Clinical actionability does not scale with result volume — a clinician reviewing >20 trials without eligibility pre-screening is unlikely to act on any. The default balances coverage with usability.

- **Status display**: All statuses returned are shown — no pre-filtering. Recruiting trials are highlighted; TERMINATED and WITHDRAWN trials are flagged with a distinct visual indicator and never omitted. Selective display of only active trials would introduce reporting bias and obscure negative evidence. Reference: Chan et al., *PLoS Med* 2004; 1:e62 (trial publication bias).

- **Phase reporting**: Phases are reported verbatim from the API and mapped to HL7 FHIR R4 `ResearchStudy.phase` codes. No lay-term substitution is made to preserve accuracy and avoid misrepresentation.

- **FHIR version**: FHIR R4, not R5. The ONC 21st Century Cures Act Final Rule (2020) mandates FHIR R4 for certified EHR systems in the US, making R4 the de facto standard for EHR interoperability with Epic, Cerner, and Oracle Health. R5 is in early adoption as of 2026 — using R5 would reduce compatibility with deployed infrastructure. Reference: 45 CFR Part 170, `https://www.healthit.gov/cures/sites/default/files/cures/2020-03/ONCCuresActFinalRule.pdf`.

- **FHIR resource type**: `ResearchStudy` — the canonical HL7 FHIR R4 resource for clinical trials. Status and phase codes map verbatim from the published R4 value sets: `research-study-status` (`http://hl7.org/fhir/research-study-status`) and `research-study-phase` (`http://terminology.hl7.org/CodeSystem/research-study-phase`).

- **Gene enrichment source**: OpenTargets Platform (`--gene` mode), not DisGeNET. DisGeNET requires a commercial API key as of 2026. OpenTargets is public, freely accessible, and aggregates evidence across GWAS, somatic mutation, differential expression, and literature sources into a single harmonised score. Reference: Ochoa et al., *Nucleic Acids Research* 2023; 51:D1353–D1359.

- **Association score threshold**: ≥ 0.6 (`--ot-min-score`). The OpenTargets overall association score is a harmonic sum across evidence types, normalised to [0, 1]. Scores < 0.5 typically reflect single-source, indirect, or low-confidence associations. The 0.6 threshold retains multi-evidence, replicated associations while excluding speculative links. Reference: Ochoa et al. 2023 (above); OpenTargets Platform scoring documentation, `https://platform-docs.opentargets.org/associations`.

- **Max diseases per gene**: 5 (`--ot-max-diseases`). Querying more diseases per gene produces diminishing returns on trial relevance and increases API load. The top-5 by association score covers the primary phenotypic spectrum of most disease genes without introducing noise from peripheral associations.

- **Status filter** (`--status`): Optional post-fetch filter to a single recruitment status (e.g. `RECRUITING`). Applied client-side after the API call so the chart and summary always reflect unfiltered counts first — filtered output is a view, not a re-query.
- **Reproducibility outputs**: Every run writes `commands.sh` (exact CLI to reproduce) and `checksums.sha256` (SHA-256 of all outputs). This ensures results are auditable and re-runnable without ambiguity.
- **Eligibility criteria**: Not parsed. The API returns eligibility as unstructured free text. Automated parsing would require NLP and introduces a high error rate for clinical use — users must review the full trial record on ClinicalTrials.gov before making any enrollment decisions.

- **Retry with exponential backoff**: Transient failures (HTTP 429, 5xx, network timeouts) are retried up to 3 times with exponential backoff (1s, 2s, 4s). Non-retryable errors (4xx except 429) raise immediately. This follows the retry pattern recommended by CT.gov API documentation for rate-limited endpoints.

- **Multi-page pagination**: CT.gov API v2 caps `pageSize` at 1000. For queries requesting more, the skill paginates via `nextPageToken` and accumulates results until `max_results` is reached. This ensures correct behaviour for large result sets without hitting API limits.

- **Country filter** (`--country`): Uses CT.gov `query.locn` parameter to restrict results to trials in a specific country. Accepts ISO 3166-1 country names or codes. Applied at the API level (not post-fetch) to reduce bandwidth and improve relevance.

- **EU Clinical Trials Register** (`--euctr`): Secondary European source queried as a best-effort complement. The EUCTR API returns XML with no versioning guarantees and may be unavailable. Results are normalised to the same schema as CT.gov trials and merged with deduplication. All EUCTR failures degrade gracefully to an empty list — the skill never fails due to EUCTR unavailability.

- **Variant-to-trial pipeline** (`--rsid`): Queries the EBI GWAS Catalog REST API (`/singleNucleotidePolymorphisms/{rsid}/associations?projection=associationBySnp`) to resolve a dbSNP rsID to genome-wide significant disease traits (p < 5 x 10^-8), then searches CT.gov for each trait. Disease traits are ranked above biomarker measurements to maximise trial relevance. Gene symbols are extracted from `authorReportedGenes` in the association loci. Reference: Buniello et al., *Nucleic Acids Research* 2019; 47:D1005--D1012 (GWAS Catalog).

- **HTML report**: Self-contained HTML with inline CSS and JavaScript, no external dependencies. Trial cards are colour-coded by recruitment status. Interactive client-side filters (status, phase, free-text search) with a live counter allow users to narrow results without re-querying. Opens correctly from any file manager or browser without a web server.

- **CSV output**: Always generated at `tables/trials.csv`. List fields (conditions, interventions) are pipe-delimited to survive CSV parsing. Designed for direct import into Excel, R, or pandas.

- **FHIR inline validation**: When `--fhir` is used, the generated Bundle is validated against basic structural rules: required fields, status/phase value set membership, entry count consistency. This catches authoring errors before an external validator (e.g., HAPI) is needed.

## Safety Rules

- Never suggest a patient enroll in a trial — always direct them to a clinician or the trial's contact listed on ClinicalTrials.gov
- Always include the ClawBio research-use disclaimer in every report
- Do not infer efficacy or safety from trial status alone — COMPLETED does not mean the intervention worked
- Flag TERMINATED and WITHDRAWN trials clearly with a visual indicator; never omit them from results
- Never fabricate NCT IDs, trial titles, or sponsor names — report only what the API returns
- Do not extrapolate trial eligibility across populations — a trial for adults does not apply to paediatric patients

## Agent Boundary

The agent (LLM) dispatches the skill and explains results in plain language. The skill (Python) queries ClinicalTrials.gov and formats the output.

The agent must NOT:
- Invent trial data not returned by the API
- Override the 20-result default without the user explicitly requesting more
- Summarise eligibility criteria unless they appear verbatim in the API response
- Make clinical recommendations based on trial phase or status alone
- Modify the safety disclaimer or omit it from any report

## Input Validation

This skill accepts requests that match the documented purpose of `clinical-trial-finder` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `clinical-trial-finder` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
