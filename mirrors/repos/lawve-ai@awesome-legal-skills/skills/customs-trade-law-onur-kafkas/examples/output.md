# Worked Example — Classification Memorandum

**Input prompt to the skill:**

> Classify a stainless steel insulated travel mug, double-wall vacuum construction, 16 fl oz capacity, with a plastic screw-on lid and silicone seal. Manufactured in Vietnam.

The output below is the draft work product the skill produces, populated against the `templates/classification-memo.md` shape. Values labelled `{placeholder}` would be filled by the skill from live data retrieval at run time; this worked example shows the structure and depth a real run should produce. Source URLs, dates, and revision identifiers are illustrative.

---

```
TARIFF CLASSIFICATION MEMORANDUM — DRAFT WORK PRODUCT

Date:              2026-05-12
HTS Revision:      HTS Revision 14 (2026)
HTS Source:        https://catalog.data.gov/dataset/harmonized-tariff-schedule-of-the-united-states-2026
HTS JSON URL:      https://www.usitc.gov/.../hts_2026_rev_14_json.json
Product:           Stainless steel double-wall vacuum insulated travel mug, 16 fl oz, plastic lid
Country of Origin: Vietnam
Prepared by:       AI Classification Research Assistant
Status:            DRAFT — For Attorney/Broker Review
```

---

### 1. Executive Summary

- **Recommended classification:** **7323.93.00.45** — "Table, kitchen or other household articles…of iron or steel; of stainless steel; kitchen or tableware suitable for food or drink contact; cooking and kitchen ware: other."
- **Total estimated duty:** 2.0% General + 7.5% Section 301 List 4A = **9.5% ad valorem** (Vietnam is not a List-4A-covered origin; Section 301 does **not** apply on Vietnam-origin goods — see Risk Factors). Net General rate **2.0% ad valorem** for Vietnam origin.
- **Confidence level:** **Moderate-to-High.** Heading 7323 is well-supported by GRI 1 and a long CROSS line; the residual uncertainty is whether the plastic lid changes essential character (it does not, under GRI 3(b)).
- **Key risk factors:** Lid composition (plastic + silicone) triggers an essential-character check; lab-grade verification of stainless-steel grade may be warranted for AD/CVD scoping.

---

### 2. Product Description

- **Common name / trade name:** Insulated travel mug
- **Materials and composition:** Body — 18/8 stainless steel (assumed; verify mill certificate). Lid — polypropylene with silicone gasket. Vacuum cavity — air-evacuated between the two stainless walls.
- **Function and mechanism of operation:** Holds hot or cold beverages for human consumption; vacuum insulation reduces heat transfer.
- **End use / intended purpose:** Personal use; household/kitchen drinkware.
- **Physical characteristics:** 16 fl oz capacity; height ~7 in; weight ~0.8 lb (approx — actual values not provided).
- **Country of origin and manufacturing process:** Made in Vietnam; assumed substantial transformation occurred in Vietnam (no facts on country of stainless-steel mill or BOM split). **Assumption flagged — please confirm.**

---

### 3. GRI Analysis

#### HTS Source Record

- **Catalog/source URL:** https://catalog.data.gov/dataset/harmonized-tariff-schedule-of-the-united-states-2026
- **Catalog checked / harvested:** 2026-05-12
- **Selected HTS release:** HTS Revision 14 (2026)
- **JSON download URL:** https://www.usitc.gov/.../hts_2026_rev_14_json.json
- **Analysis date:** 2026-05-12
- **Source limitations:** None — Data.gov bulk JSON retrieved successfully.

#### Candidate Headings Considered

| Heading | Description | Basis for Consideration |
|---------|-------------|------------------------|
| 7323 | Table, kitchen or other household articles of iron or steel | Primary candidate — composite article is principally stainless steel by weight, volume, and value |
| 3924 | Tableware, kitchenware, of plastics | Lid is plastic; rejected — body (stainless) dominates |
| 9617 | Vacuum flasks and other vacuum vessels | Considered — modern construction matches a vacuum vessel definition |
| 7013 | Glassware of a kind used for table, kitchen | Rejected — no glass component |

#### GRI 1 Analysis

**Heading 7323 text:** "Table, kitchen or other household articles and parts thereof, of iron or steel; iron or steel wool; pot scourers and scouring or polishing pads, gloves and the like, of iron or steel."

**Section XV Note 7 / Chapter 73 considerations:** Composite articles consisting partly of base metal are classified as articles of the metal predominating by weight unless context otherwise requires (Section XV Note 7). The stainless-steel body is the predominant material by weight and value.

**Heading 9617 text:** "Vacuum flasks and other vacuum vessels, complete with cases; parts thereof other than glass inners."

**Conflict:** Both 7323 and 9617 are plausible by GRI 1. **9617** specifically describes "vacuum flasks and other vacuum vessels," which is a more specific description than "household articles…of iron or steel" under GRI 3(a) (the *more specific description* rule).

**Conclusion:** GRI 1 does **not** resolve outright — GRI 3(a) is needed.

#### GRI 3(a) — More Specific Description

- **9617** describes the product *by its function* (vacuum vessel).
- **7323** describes the product *by its material* (household article of steel).
- *eo nomine* by function generally prevails over classification by material. **9617 prevails under GRI 3(a).**

Re-examined under 9617:
- Sub-headings: 9617.00.10 (vacuum flasks/vessels having a capacity not exceeding 1 liter) vs 9617.00.30 (exceeding 1 liter) vs 9617.00.60 (parts).
- 16 fl oz = ~0.47 L → **9617.00.10**.

**Revised recommendation pending CROSS check:** **9617.00.10** rather than 7323.93.00.45.

> *Implementer note:* this example shows the kind of mid-analysis correction the skill must flag when GRI 1 looks decisive at first pass but GRI 3(a) reroutes. In a real run, the skill consults CROSS at this point before finalising.

#### GRI 6: Subheading Determination

Indent hierarchy under 9617.00:
- 9617.00.10 — Vacuum flasks and other vacuum vessels, having a capacity not exceeding 1 liter
- 9617.00.30 — Vacuum flasks and other vacuum vessels, having a capacity exceeding 1 liter
- 9617.00.60 — Parts (other than glass inners)

**Recommended subheading:** **9617.00.10.00**

#### Resolving GRI

- **Classification resolved by:** GRI 1 + GRI 3(a)
- **Key determination:** 9617 prevails over 7323 as the more specific (function-based) description of a vacuum-insulated drinkware article.

---

### 4. CROSS Ruling Research

#### Relevant Rulings

**CBP Ruling NY N321456 (dated 2021-11-15)** *(illustrative)*
- Product: Double-wall stainless-steel vacuum-insulated water bottle, 24 oz, plastic lid
- Classification: **9617.00.10.00**
- GRI Applied: 1 (read with Chapter 96 notes)
- Key Reasoning: "Vacuum-insulated drinkware constructed with an evacuated cavity between two stainless-steel walls is properly classified under heading 9617 as a vacuum vessel."
- Factual Similarity: **High**
- Evidence Quality: Verified
- Status: Active

**CBP Ruling NY N289101 (dated 2018-03-22)** *(illustrative)*
- Product: Stainless tumbler, single-wall (no vacuum), 20 oz
- Classification: **7323.93.00.45**
- GRI Applied: 1
- Key Reasoning: Single-wall stainless tumblers are kitchen/household ware of stainless steel under 7323, not vacuum vessels.
- Factual Similarity: **Low** (single-wall — distinguishing fact)
- Evidence Quality: Verified
- Status: Active

#### Ruling Analysis

The CROSS line distinguishes single-wall stainless tumblers (7323.93) from double-wall vacuum-insulated drinkware (9617.00). Because the subject merchandise is double-wall with an evacuated cavity, the **9617.00.10** classification is consistent with controlling CROSS authority.

---

### 5. CIT/CAFC Case Law

No CIT or CAFC decisions directly addressing 9617 vs 7323 for vacuum-insulated drinkware were located in the slip-opinion index for 2018-2026. Heading 9617 has been the stable CBP position for this product category.

---

### 6. Duty Rate Summary

| Component | Rate | Authority | Notes |
|-----------|------|-----------|-------|
| Column 1 General | **7.2% ad val** | HTSUS 9617.00.10.00 | MFN/NTR rate |
| Special Program | n/a | — | No FTA claim asserted; Vietnam is not party to a U.S. FTA |
| Section 301 | n/a | — | Section 301 List 4A applies to China origin only |
| Section 232 | n/a | — | Steel/aluminum 232 limited to specified HTS lines (does not include 9617) |
| Section 201 | n/a | — | No safeguard order on 9617 |
| AD Duty | **Verify** | A-552-xxx (Vietnam stainless steel cookware order — scope verification needed) | Scope-ruling review recommended |
| CVD | **Verify** | — | None located for 9617 finished goods of Vietnam origin |
| **Total Estimated Duty** | **7.2% ad val (subject to AD scope verification)** | | |
| MPF | 0.3464% ad val ($31.67 min / $614.35 max as of FY2026) | 19 CFR § 24.23 | Formal entry fee — verify |
| HMF | 0.125% ad val | 26 U.S.C. § 4461 | Ocean shipments only |

---

### 7. Risk Factors and Recommendations

#### Flags Triggered

- **AD/CVD scope check (Vietnam stainless steel orders):** Verify whether the Commerce AD order on certain stainless-steel cookware from Vietnam (if any current) reaches finished vacuum vessels classified in 9617. Scope rulings are recommended where uncertainty exists.
- **Substantial-transformation assumption:** No facts on the country of the stainless-steel coil/sheet used to fabricate the body. If sheet was sourced from a covered origin, origin and AD/CVD analysis must be re-run.
- **Composite-article check:** The plastic lid + silicone gasket are subordinate components; classification under 9617 is not affected, but a binding ruling is advisable if the importer disagrees.

#### Recommendations

1. **Recommend CBP binding ruling** under 19 CFR Part 177 for high-volume or recurring entries — 9617 classification is well-supported but importer-specific facts (lid construction, BOM origin) should be locked in.
2. **Run an AD/CVD scope verification** against current Commerce orders covering Vietnam-origin stainless-steel cookware or drinkware before entry.
3. **Confirm origin** documentation (Certificate of Origin, manufacturing affidavit) supports Vietnam as the country of substantial transformation, not merely final assembly.
4. **Update prior entries** if the importer previously entered under 7323.93 — a Prior Disclosure under 19 USC 1592(c)(4) may be appropriate.

---

### 8. Evidence And Freshness Appendix

| Conclusion | Source | Authority Level | Evidence Label | Retrieved | Freshness / Revision | Limitation |
|------------|--------|-----------------|----------------|-----------|----------------------|------------|
| Classification 9617.00.10.00 | HTSUS 2026 Rev 14, heading 9617 | HTSUS legal text | Verified | 2026-05-12 | Current revision | None |
| GRI 3(a) precedence of 9617 over 7323 | Section XV Note 7 + GRI 3(a) | HTSUS legal text | Verified | 2026-05-12 | Current | None |
| Consistent CROSS treatment | NY N321456 (illustrative) | CBP NY ruling | Verified | 2026-05-12 | Active | Persuasive only |
| Distinguishing single-wall (7323.93) | NY N289101 (illustrative) | CBP NY ruling | Verified | 2026-05-12 | Active | Persuasive only |
| No CIT/CAFC contrary holding | CIT slip-opinion index 2018-2026 | Negative search result | Identified | 2026-05-12 | Through 2026-05-12 | Search limited to indexed PDFs |
| MPF/HMF rates | 19 CFR § 24.23; 26 USC § 4461 | Regulation/statute | Verified | 2026-05-12 | FY2026 | Rates re-set annually |

---

### 9. Disclaimer

> **DISCLAIMER — DRAFT WORK PRODUCT**
>
> This analysis is provided as legal research assistance and draft work product for review by a licensed attorney or licensed customs broker. It does not constitute legal advice, nor does it establish an attorney-client relationship.
>
> HTS classifications presented herein are not final until confirmed by U.S. Customs and Border Protection (CBP). For high-value, novel, or recurring transactions, we recommend requesting a binding ruling from CBP pursuant to 19 CFR Part 177.
>
> Duty rates shown reflect the Harmonized Tariff Schedule of the United States as of the date indicated. Additional duties may apply under Chapter 99 (Sections 201, 232, 301), antidumping/countervailing duty orders, or other programs not fully captured in this analysis.
>
> CROSS rulings cited herein are persuasive authority but are not binding on CBP unless they directly address the importer's specific merchandise. Headquarters rulings (HQ) carry greater weight than New York rulings (NY) but neither constitutes regulation or statute.
>
> Court of International Trade (CIT) and Court of Appeals for the Federal Circuit (CAFC) decisions cited herein reflect judicial interpretation as of their issuance date. Subsequent legislative changes, regulatory actions, or appellate decisions may affect their applicability.
>
> **This analysis was generated on 2026-05-12 using HTS Revision 14 (2026). Verify all rates and classifications against the current HTS before relying on this analysis for entry purposes.**
