# Chapter 99 Surcharges — Section 301/232/201 Identification

## Overview

Chapter 99 of the HTSUS contains temporary tariff modifications enacted under various trade remedy statutes. These surcharges are **in addition to** the regular Column 1 General rate and can be the **largest component** of total duty.

Use current HTS data and official status sources. Create evidence ledger entries per `references/agentic-research-protocol.md`; Chapter 99 conclusions are not current unless effective dates, exclusions, and source freshness have been checked.

---

## Section 301 — Retaliatory Tariffs (Trade Act of 1974)

### Background
Authority: 19 U.S.C. § 2411 (Section 301, Trade Act of 1974)
Primary target: China (since 2018, multiple "Lists" covering thousands of HTS subheadings)

### Identification Protocol

1. **Check HTS footnotes** for Chapter 99 cross-references:
   - Look for footnotes like "See 9903.88.15" in the REST API results
   - These indicate the subheading is covered by a Section 301 action
   - Also inspect `additionalDuties` and `addiitionalDuties` in the current HTS JSON

2. **Search for current status:**
   ```
   web_search("Section 301 tariff {HTS heading} China {current_year}")
   web_search("USTR Section 301 list {product type} {current_year}")
   web_search("9903.88 {HTS heading} Section 301")
   ```
   Prefer USTR, Federal Register, USITC, and HTS Chapter 99 sources over secondary summaries.

3. **Identify the List and rate:**

   | List | Initial Rate | Current Rate | HTS Chapter 99 |
   |------|-------------|--------------|-----------------|
   | List 1 | 25% | 25%+ | 9903.88.01-03 |
   | List 2 | 25% | 25%+ | 9903.88.04-05 |
   | List 3 | 25% | 25%+ | 9903.88.06-15 |
   | List 4A | 7.5%-25% | Varies | 9903.88.16+ |
   | List 4B | Various | Varies | 9903.88.xx |

   **Note:** Rates have been modified multiple times. Always verify the **current** rate via web_search with the current year.

4. **Check for exclusions:**
   ```
   web_search("Section 301 exclusion {product} {HTS heading} {current_year}")
   ```
   - Product-specific exclusions may reduce or eliminate the surcharge
   - Exclusions have **expiration dates** — verify current status
   - If exclusion may apply, trigger flag from `references/human-review-triggers.md`

### Country Scope
Section 301 tariffs currently target **China** as the primary country. Products of Chinese origin (country of origin for tariff purposes) are subject to applicable List surcharges.

**Critical:** Country of origin for Section 301 purposes follows standard substantial transformation analysis — not just country of manufacture.

---

## Section 232 — National Security Tariffs (Trade Expansion Act of 1962)

### Background
Authority: 19 U.S.C. § 1862 (Section 232, Trade Expansion Act of 1962)
Products: Steel and aluminum articles

### Identification Protocol

1. **Determine if the product is steel or aluminum:**
   - Steel articles: Generally Chapters 72-73 and some products in other chapters
   - Aluminum articles: Generally Chapter 76 and some products in other chapters
   - Derivative steel/aluminum articles: Some finished goods containing steel/aluminum

2. **Search for current status:**
   ```
   web_search("Section 232 tariff {product} {current_year}")
   web_search("Section 232 steel aluminum tariff rate {current_year}")
   ```
   Prefer presidential proclamations, Federal Register notices, Commerce/BIS materials, USITC, and HTS Chapter 99 sources.

3. **Standard rates:**

   | Product | Rate | HTS Chapter 99 |
   |---------|------|-----------------|
   | Steel | 25% | 9903.80.01+ |
   | Aluminum | 10% | 9903.85.01+ |

   **Note:** Rates and country coverage have been modified by presidential proclamations. Some countries have been exempted or subject to quotas instead of tariffs. Always verify current status.

4. **Check for exclusions:**
   ```
   web_search("Section 232 exclusion {product} {current_year}")
   ```
   - Product-specific exclusions available through the Commerce Department
   - Country-specific exemptions may apply (verify by country of origin)

---

## Section 201 — Safeguard Tariffs (Trade Act of 1974)

### Background
Authority: 19 U.S.C. § 2251 (Section 201, Trade Act of 1974)
Current products: Solar cells/modules, large residential washing machines

### Identification Protocol

1. **Search for current safeguard measures:**
   ```
   web_search("Section 201 safeguard tariff {product} {current_year}")
   ```
   Prefer presidential proclamations, Federal Register notices, USITC safeguard materials, and HTS Chapter 99 sources.

2. **Known active safeguards:**

   | Product | Initial Rate | Notes | HTS Chapter 99 |
   |---------|-------------|-------|-----------------|
   | Solar cells/modules | 30% (declining) | Tariff-rate quota structure | 9903.45.xx |
   | Washing machines | 20% (declining) | Tariff-rate quota structure | 9903.44.xx |

   **Note:** Section 201 rates typically **decline** over a 4-year period and may be extended. Tariff-rate quotas apply different rates above and below quantity thresholds.

3. **Section 201 applies globally** (not country-specific) but USMCA countries (Canada, Mexico) and some FTA partners may be exempted.

---

## Surcharge Stacking

Section 301, 232, and 201 surcharges can **stack** on the same product:

```
Example: Solar panel from China
  General rate:         Free (8541.40.60)
  + Section 301:       25% (List 3)
  + Section 201:       varies (safeguard on solar cells)
  + AD Duty:           varies (if from covered producer)
  + CVD:               varies (if from covered producer)
  = Total estimated duty: General + 301 + 201 + AD + CVD
```

**Important:** Not all surcharges apply to every product from every country. Each surcharge has its own scope (product coverage and country coverage).

---

## Verification Steps

For every product-country combination:

1. **Check HTS footnotes** in API results for any "See 99XX.XX.XX" references
2. **Check `additionalDuties` and `addiitionalDuties`** in the current HTS JSON
3. **Search Section 301** if origin is China (or potentially other targeted countries)
4. **Search Section 232** if product is steel, aluminum, or derivative thereof
5. **Search Section 201** if product is solar cells/modules or washing machines
6. **Check for exclusions** for each applicable surcharge
7. **Verify current rates** — surcharge rates change with presidential proclamations
8. **Document the Chapter 99 subheading** for each applicable surcharge
9. **Note effective dates and expiration dates** where applicable
10. **Record evidence label and retrieval date** for each source
