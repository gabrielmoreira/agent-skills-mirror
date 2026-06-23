# Duty Rate Summary Template

## Structure

Generate duty rate summaries with this structure. Follow formatting conventions from `references/formatting-standards.md`.

---

### Header Block

```
DUTY RATE SUMMARY — DRAFT WORK PRODUCT

Date:               {current date}
HTS Revision:       {revision identifier}
HTS Source:         {Data.gov catalog URL or fallback source}
HTS JSON URL:       {selected JSON download URL}
Product:            {product name/identifier}
HTS Subheading:     {XXXX.XX.XXXX}
Country of Origin:  {country}
Prepared by:        AI Classification Research Assistant
Status:             DRAFT — For Attorney/Broker Review
```

---

### 1. Classification Basis

- **HTS Subheading:** {XXXX.XX.XXXX}, HTSUS
- **Description:** {HTS description text}
- **Unit of Quantity:** {units from HTS data}
- **Classification source:** {Workflow 1 analysis / User-provided / Assumed}
- **HTS source record:** {catalog URL, selected revision, JSON URL, analysis date}

If the classification was not performed as part of this analysis, note: "Classification was provided by the user and has not been independently verified."

---

### 2. Duty Rate Breakdown

| # | Component | Rate | Chapter 99 / Order # | Authority | Effective Date | Notes |
|---|-----------|------|----------------------|-----------|---------------|-------|
| 1 | Column 1 General (MFN) | {rate} | N/A | HTSUS {subheading} | Current revision | Standard NTR rate |
| 2 | Section 301 | {rate or N/A} | {9903.XX.XX} | Trade Act § 301 | {date} | {List #, if applicable} |
| 3 | Section 232 | {rate or N/A} | {9903.XX.XX} | Trade Expansion Act § 232 | {date} | {Steel/aluminum} |
| 4 | Section 201 | {rate or N/A} | {9903.XX.XX} | Trade Act § 201 | {date} | {Safeguard product} |
| 5 | Antidumping Duty | {rate or N/A} | {A-XXX-XXX} | 19 U.S.C. § 1673 | {date} | {Company-specific or all-others} |
| 6 | Countervailing Duty | {rate or N/A} | {C-XXX-XXX} | 19 U.S.C. § 1671 | {date} | {Company-specific or all-others} |
| | **TOTAL ESTIMATED DUTY** | **{total}** | | | | **Sum of all duty components** |
| 7 | MPF (fee) | {rate/min/max (verify)} | N/A | 19 CFR § 24.23 | Current | Formal entry fee |
| 8 | HMF (fee) | {rate (verify)} | N/A | 26 U.S.C. § 4461 | Current | Ocean shipments only |

---

### 3. Special Program Eligibility

| Program Code | Program Name | Rate | Eligible? | Requirements |
|-------------|-------------|------|-----------|-------------|
| {code} | {name from fta-program-codes.json} | {rate} | {Yes/No/Verify} | {Key origin rule} |

**Applicable special rate:** {rate and program, or "None — General rate applies"}

**Note:** Special program rates replace the Column 1 General rate but do **not** eliminate Chapter 99 surcharges or AD/CVD duties.

---

### 4. Duty Calculation Example

If the customs value is known or estimated:

```
Customs Value (Transaction Value):    ${amount}

Column 1 General:  {rate}% × ${value} = ${amount}
Section 301:       {rate}% × ${value} = ${amount}
Section 232:       {rate}% × ${value} = ${amount}
AD Duty:           {rate}% × ${value} = ${amount}
CVD:               {rate}% × ${value} = ${amount}
                                        ──────────
TOTAL ESTIMATED DUTY:                   ${total}
Effective Rate:                         {total/value}%

Fees (not included in duty total):
MPF:               {rate (verify)}% × ${value} = ${amount} (min/max per entry applies)
HMF:               {rate (verify)}% × ${value} = ${amount} (ocean shipments only)
```

If the customs value is not known: "Duty calculation requires the customs value (transaction value). Provide the commercial invoice value for a dollar-amount estimate."

---

### 5. Exclusions and Exceptions

- **Section 301 exclusions:** {applicable / not applicable / check required}
- **Section 232 exclusions:** {applicable / not applicable / check required}
- **Temporary duty suspensions:** {any applicable MTB provisions}
- **Foreign Trade Zone potential:** {relevant if high duty rate}

---

### 6. Rate Verification Notes

- [ ] Rates verified against current HTS revision ({revision date})
- [ ] Data.gov catalog or fallback source recorded
- [ ] Chapter 99 footnotes checked in HTS API results
- [ ] `additionalDuties` / `addiitionalDuties` checked in HTS JSON if available
- [ ] AD/CVD orders verified for product-country combination
- [ ] Section 301/232 status verified with current-year search
- [ ] MPF rate/min/max verified with current-year search
- [ ] HMF rate verified (ocean shipments only)
- [ ] Special program eligibility assessed

**Data sources consulted:** {list the specific searches and API calls used}

---

### 7. Evidence And Freshness Appendix

| Duty Component | Source | Evidence Label | Retrieved | Freshness / Effective Date | Limitation |
|----------------|--------|----------------|-----------|----------------------------|------------|
| Column 1 General | {HTS source} | {Verified/Retrieved} | {date} | {revision} | {none} |
| Chapter 99 | {source} | {Verified/Retrieved/Identified/Unverified} | {date} | {effective/expiration} | {notes} |
| AD/CVD | {source} | {Verified/Retrieved/Identified/Unverified} | {date} | {order/rate date} | {scope notes} |

---

### 8. Disclaimer

Include the **Condensed Disclaimer** from `references/disclaimers.md`.
