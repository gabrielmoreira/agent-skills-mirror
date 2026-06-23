# Full Compliance Review Template

## Structure

Generate comprehensive compliance reviews with this structure. This template chains the outputs of Workflows 1, 4, and 6 into a unified compliance document. Follow conventions from `references/formatting-standards.md`.

---

### Header Block

```
IMPORT COMPLIANCE REVIEW — DRAFT WORK PRODUCT

Date:               {current date}
HTS Revision:       {revision identifier}
HTS Source:         {Data.gov catalog URL or fallback source}
HTS JSON URL:       {selected JSON download URL}
Product:            {product name/identifier}
Country of Origin:  {country}
Import Volume:      {estimated annual volume/value, if known}
Prepared by:        AI Classification Research Assistant
Status:             DRAFT — For Attorney/Broker Review
```

---

### 1. Executive Summary

A concise overview (3-5 sentences) covering:
- Recommended HTS classification and confidence level
- Total estimated duty rate (all components)
- Country of origin determination (marking, FTA, TAA)
- Key compliance risks identified
- Priority recommendations

---

### 2. Product Analysis

Per the intake step of Workflow 1:
- Full product description
- Materials and composition
- Function, mechanism, end use
- Physical characteristics
- Manufacturing process and supply chain
- Information gaps or assumptions

---

### 3. Tariff Classification

**Full classification memo content** per `templates/classification-memo.md`:
- Candidate headings and GRI analysis
- CROSS ruling research
- CIT/CAFC case law (if applicable)
- Recommended classification with supporting reasoning

---

### 4. Duty Rate Analysis

**Full duty compilation** per `templates/duty-rate-summary.md`:
- Column 1 General rate
- Chapter 99 surcharges (301/232/201)
- AD/CVD duties
- Special program eligibility
- Total estimated duty

---

### 5. Country of Origin Analysis

**Full origin analysis** per `references/country-of-origin-analysis.md`:

#### A. Marking Origin (19 CFR Part 134)
- Substantial transformation analysis
- Required marking
- Marking exceptions (if applicable)

#### B. FTA Origin (if applicable)
- Applicable FTA and program code
- Rules of origin assessment
- Documentation requirements

#### C. TAA Compliance (if applicable)
- Substantial transformation for TAA purposes
- TAA-designated country status
- Government procurement eligibility

---

### 6. Partner Government Agency (PGA) Screening

Assess whether the product is subject to regulation by:

| Agency | Jurisdiction | Potentially Applicable? | Basis |
|--------|-------------|------------------------|-------|
| FDA | Food, drugs, cosmetics, medical devices | {Yes/No/Check} | {reason} |
| EPA | Chemicals, pesticides, vehicles | {Yes/No/Check} | {reason} |
| CPSC | Consumer products (safety) | {Yes/No/Check} | {reason} |
| USDA/APHIS | Agriculture, plants, animals | {Yes/No/Check} | {reason} |
| FCC | Electronics (radio frequency) | {Yes/No/Check} | {reason} |
| TTB | Alcohol, tobacco | {Yes/No/Check} | {reason} |
| ATF | Firearms, explosives | {Yes/No/Check} | {reason} |
| DOT | Vehicles, hazardous materials | {Yes/No/Check} | {reason} |

If any PGA requirements are potentially applicable, flag per `references/human-review-triggers.md` and recommend verification with the relevant agency.

---

### 7. Forced Labor / UFLPA Screening

- **Supply chain origin:** {countries involved in production}
- **UFLPA risk assessment:** {risk level based on origin and product type}
- **Entity List check:** {any known entities in the supply chain on the UFLPA Entity List?}
- **Withhold Release Orders (WRO):** {any applicable WROs?}
- **Source freshness:** {official CBP/DHS/WRO source URLs and retrieval dates}
- **Data gaps:** {supplier/facility/material origin facts not provided}
- **Recommendation:** {actions needed to demonstrate compliance}

If UFLPA risk is identified, flag per `references/human-review-triggers.md`.

---

### 8. Compliance Risk Summary

#### Flags Triggered

List all flags from `references/human-review-triggers.md` that were triggered during the analysis, with full flag text and recommended actions.

#### Risk Matrix

| Risk Area | Level | Description | Recommended Action |
|-----------|-------|-------------|-------------------|
| Classification | {H/M/L} | {brief description} | {action} |
| Duty Rate | {H/M/L} | {brief description} | {action} |
| Country of Origin | {H/M/L} | {brief description} | {action} |
| Trade Remedies | {H/M/L} | {brief description} | {action} |
| PGA Compliance | {H/M/L} | {brief description} | {action} |
| UFLPA | {H/M/L} | {brief description} | {action} |

---

### 9. Recommendations

#### Immediate Actions
1. {Priority recommendation — e.g., "Request CBP binding ruling before first entry"}
2. {Second recommendation}
3. {Third recommendation}

#### Ongoing Compliance
- {Monitoring recommendations — e.g., "Monitor Section 301 exclusion renewals"}
- {Record-keeping requirements}
- {Periodic review schedule}

#### Cost Optimization Opportunities
- {FTA qualification potential}
- {Foreign Trade Zone consideration}
- {Tariff engineering possibilities (if any)}
- {First Sale valuation (for related-party transactions)}

---

### 10. Source And Evidence Appendix

| Issue | Conclusion | Source | Authority Level | Evidence Label | Retrieved | Freshness / Status | Limitation |
|-------|------------|--------|-----------------|----------------|-----------|--------------------|------------|
| HTS | {classification/rate point} | {source} | {HTSUS/USITC} | {Verified/Retrieved} | {date} | {revision} | {none} |
| CROSS | {ruling support} | {source} | {CBP HQ/NY} | {Verified/Retrieved/Identified/Unverified} | {date} | {active/revoked} | {notes} |
| Origin | {origin point} | {source} | {CBP/CFR/FTA} | {label} | {date} | {current} | {notes} |
| PGA/UFLPA | {risk point} | {source} | {agency} | {label} | {date} | {current} | {data gaps} |

---

### 11. Disclaimer

Include the **Standard Disclaimer** from `references/disclaimers.md`, with `[DATE]` and `[REV]` populated.
