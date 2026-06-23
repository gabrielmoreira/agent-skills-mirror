# Special Programs Decoder — FTA and Preference Program Eligibility

## Overview

The "special" column in HTS data contains letter codes indicating which Free Trade Agreement (FTA) or preference program rates are available for a given subheading. This methodology decodes those codes and assesses eligibility.

---

## Decoding Process

### Step 1: Extract the Special Column
From HTS data (REST API or bulk JSON), read the `special` field:
```
Example: "Free (A+,AU,BH,CL,CO,D,E,IL,JO,KR,MA,OM,P,PA,PE,S,SG)"
```

### Step 2: Decode Each Program Code
Use `references/fta-program-codes.json` to map each letter code to its program name, authority, and qualifying countries.

### Step 3: Match to Country of Origin
Given the product's country of origin, identify which programs could apply.

### Step 4: Verify Eligibility Requirements
Each program has its own rules of origin that must be satisfied.

---

## Eligibility Assessment Framework

### For FTA Preferential Rates (AU, BH, CA, CL, CO, IL, JO, KR, MA, MX, OM, P, PA, PE, S, SG)

**Requirements for FTA rate eligibility:**

1. **Origin in an FTA partner country** — the product must originate in the FTA country per that agreement's rules of origin
2. **Rules of origin met** — typically one or more of:
   - **Tariff shift:** The product undergoes a specified change in tariff classification during production in the FTA country
   - **Regional value content (RVC):** A minimum percentage of the product's value is attributable to the FTA region
   - **Specific process:** The product undergoes a specified manufacturing operation
3. **Certification:** A valid certificate of origin or origin declaration
4. **Direct shipment:** In some FTAs, goods must ship directly between FTA countries

### For Preference Programs (A, A+, D, E, R)

**GSP (A, A+):**
- Country must be a designated GSP beneficiary developing country
- Product must be on the GSP-eligible list for that country
- Product must be the "growth, product, or manufacture" of the beneficiary country
- At least 35% of appraised value must be attributable to the beneficiary country
- **Check GSP program status** — GSP periodically expires and must be renewed by Congress

**AGOA (D):**
- Country must be a sub-Saharan African AGOA beneficiary
- Product must meet AGOA rules of origin
- Check current beneficiary list — countries can be added or removed

**CBERA/CBTPA (E, R):**
- Caribbean Basin countries
- Product must meet applicable origin rules
- CBTPA (R) provides enhanced textile/apparel preferences

---

## Presentation Format

```
SPECIAL PROGRAM ANALYSIS
HTS Subheading: {XXXX.XX.XXXX}
Country of Origin: {Country}

Special Column: "{special field text}"

| Code | Program | Qualifying Countries | Rate | Eligible? |
|------|---------|---------------------|------|-----------|
| A+ | GSP (LDC) | [list] | Free | {Yes/No/Verify} |
| S | USMCA | Canada, Mexico | Free | {Yes/No/Verify} |
| KR | KORUS | Republic of Korea | Free | {Yes/No/Verify} |
| ... | ... | ... | ... | ... |

Applicable Program: {program name or "None — General rate applies"}
Preferential Rate: {rate}
Requirements: {key rules of origin requirements}
Documentation: {required certificate or declaration}
```

---

## Common Scenarios

### Product from an FTA Country
1. Identify the applicable FTA code from the special column
2. State the preferential rate
3. Note the rules of origin that must be met
4. Note the documentation required
5. Recommend verification with a customs broker

### Product from a GSP Country
1. Confirm the `A` or `A+` code is in the special column
2. **Verify GSP is currently active** (it expires periodically)
3. Verify the country is a current GSP beneficiary for this product
4. Note the 35% value-added requirement
5. Flag if GSP status is uncertain

### Product from a Non-Qualifying Country
1. No special program codes match the country of origin
2. The Column 1 General rate applies
3. Note any Chapter 99 surcharges (Section 301, 232) that may also apply
4. Consider if the product could qualify through a third-country FTA (e.g., if assembled in an FTA country from components)

### Product from a Column 2 Country
1. Cuba, North Korea — Column 2 rate applies
2. Column 2 rates are significantly higher than Column 1
3. Additional sanctions/restrictions may apply beyond tariffs
