# Classification Memorandum Template

## Structure

Generate classification memos with this structure. Follow citation and formatting conventions from `references/formatting-standards.md`.

---

### Header Block

```
TARIFF CLASSIFICATION MEMORANDUM — DRAFT WORK PRODUCT

Date:           {current date}
HTS Revision:   {revision identifier}
HTS Source:     {Data.gov catalog URL or fallback source}
HTS JSON URL:   {selected JSON download URL}
Product:        {product name/identifier}
Country of Origin: {country}
Prepared by:    AI Classification Research Assistant
Status:         DRAFT — For Attorney/Broker Review
```

---

### 1. Executive Summary

A 2-3 sentence summary containing:
- **Recommended classification:** Full HTS subheading with statistical suffix
- **Total estimated duty:** All components summed (General + surcharges + AD/CVD)
- **Confidence level:** High / Moderate / Low, with brief explanation
- **Key risk factors:** One-line summary of any flags triggered

---

### 2. Product Description

Structured description of the merchandise:
- **Common name / trade name**
- **Materials and composition** (with percentages if known)
- **Function and mechanism of operation**
- **End use / intended purpose**
- **Physical characteristics** (dimensions, weight)
- **Country of origin and manufacturing process**
- **Any additional product-specific details**

Note any information that was assumed or not provided by the user.

---

### 3. GRI Analysis

Document the step-by-step application of the General Rules of Interpretation per `references/gri-analysis.md`:

#### HTS Source Record
- **Catalog/source URL:** {Data.gov catalog URL or fallback source}
- **Catalog checked / harvested:** {date or "not available"}
- **Selected HTS release:** {revision title}
- **JSON download URL:** {URL}
- **Analysis date:** {date}
- **Source limitations:** {none / fallback used / API unavailable / notes}

#### Candidate Headings Considered
| Heading | Description | Basis for Consideration |
|---------|-------------|----------------------|
| {XXXX} | {heading text} | {why this heading was considered} |

#### GRI 1 Analysis
- Quote relevant heading text
- Quote applicable Section Notes
- Quote applicable Chapter Notes
- **Conclusion:** Does GRI 1 resolve? If yes → state which heading. If no → proceed.

#### GRI 2-5 Analysis (if needed)
- Apply only the GRI(s) necessary to resolve
- Document each step and its conclusion
- If GRI 3(b) essential character is at issue, apply the multi-factor test

#### GRI 6: Subheading Determination
- Show the indent-level hierarchy for the resolved heading
- Compare subheadings at the same indent level
- Apply GRI 1-5 principles within the heading
- **Recommended subheading:** {XXXX.XX.XXXX}

#### Resolving GRI
- **Classification resolved by:** GRI {X}
- **Key determination:** {one sentence explaining the dispositive analysis}

---

### 4. CROSS Ruling Research

Present findings per `references/cross-ruling-research.md`:

#### Relevant Rulings

For each ruling (target 3-5):
```
**CBP Ruling {NY/HQ} {Number} (dated {Date})**
- Product: {description}
- Classification: {HTS subheading}
- GRI Applied: {GRI number}
- Key Reasoning: {1-2 sentences}
- Factual Similarity: {High/Medium/Low}
- Evidence Quality: {Verified/Retrieved/Identified/Unverified}
- Status: {Active/Revoked/Modified}
```

Note: "Money quotes" (specific reasoning excerpts) require **Verified** evidence quality. See `references/cross-ruling-research.md` for the full evidence quality protocol.

#### Ruling Analysis
- Consensus classification supported by rulings
- Any outliers or conflicts
- How rulings inform the recommended classification

---

### 5. CIT/CAFC Case Law (if applicable)

If relevant judicial decisions were found per `references/cit-decision-analysis.md`:

- Case citation(s) in Bluebook format
- Brief summary of holding
- Impact on the recommended classification
- Any conflict with CROSS rulings

If no relevant decisions were found, state: "No CIT/CAFC decisions were found directly addressing the classification of this product or the candidate headings."

---

### 6. Duty Rate Summary

Per `references/duty-rate-compilation.md`:

| Component | Rate | Authority | Notes |
|-----------|------|-----------|-------|
| Column 1 General | {rate} | HTSUS {subheading} | MFN/NTR rate |
| Special Program | {rate} | {program code} | If origin qualifies |
| Section 301 | {rate} | 9903.XX.XX | If applicable |
| Section 232 | {rate} | 9903.XX.XX | If applicable |
| Section 201 | {rate} | 9903.XX.XX | If applicable (safeguard) |
| AD Duty | {rate} | A-XXX-XXX | If applicable |
| CVD | {rate} | C-XXX-XXX | If applicable |
| **Total Estimated Duty** | **{rate}** | | **Sum of all duty components** |
| MPF (fee) | {rate/min/max (verify)} | 19 CFR § 24.23 | Formal entry fee |
| HMF (fee) | {rate (verify)} | 26 U.S.C. § 4461 | Ocean shipments only |

---

### 7. Risk Factors and Recommendations

#### Flags Triggered
List any flags from `references/human-review-triggers.md` that were triggered, with the full flag text and recommended next steps.

#### Recommendations
- Whether a CBP binding ruling should be requested
- Whether existing entries should be reviewed
- Any time-sensitive considerations (expiring exclusions, pending trade actions)
- Suggested next steps for the attorney/broker

---

### 8. Evidence And Freshness Appendix

Include a compact evidence ledger for each material conclusion:

| Conclusion | Source | Authority Level | Evidence Label | Retrieved | Freshness / Revision | Limitation |
|------------|--------|-----------------|----------------|-----------|----------------------|------------|
| {classification} | {URL/title} | {HTSUS/CROSS/CIT/etc.} | {Verified/Retrieved/Identified/Unverified} | {date} | {current revision/status} | {none/notes} |

---

### 9. Disclaimer

Include the **Standard Disclaimer** from `references/disclaimers.md`, with `[DATE]` and `[REV]` populated.
