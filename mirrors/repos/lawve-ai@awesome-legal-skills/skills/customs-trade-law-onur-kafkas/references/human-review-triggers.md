# Human Attorney Review Triggers

This file defines situations where the skill **must explicitly flag** the analysis for review by a licensed attorney or licensed customs broker. These triggers reflect genuine legal risk, regulatory complexity, or factual uncertainty that exceeds the scope of AI-assisted research.

---

## Mandatory Flag Triggers

### 1. GRI 3 Classification Disputes
**Trigger:** Product is reasonably classifiable under two or more headings and GRI 1 does not resolve.
**Why:** GRI 3 analysis (specificity, essential character, last-in-order) involves subjective judgment that courts frequently disagree on. Essential character determinations are among the most litigated issues in customs law.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: This product presents a GRI 3 classification dispute. Multiple headings are plausible. The essential character determination involves subjective factors that should be reviewed by a licensed professional.`

### 2. Section 301/232 Exclusion Eligibility
**Trigger:** Product may qualify for a product-specific exclusion from Section 301 or 232 tariffs.
**Why:** Exclusion processes have strict procedural requirements, deadlines, and technical specifications. An incorrect exclusion claim can result in penalties.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: This product may be eligible for a Section 301/232 exclusion. Exclusion eligibility involves specific regulatory criteria and filing deadlines that require professional guidance.`

### 3. No CROSS Ruling History
**Trigger:** No relevant CROSS rulings found for the product or closely analogous merchandise.
**Why:** Absence of ruling history means there is no CBP guidance to rely on. Novel classifications carry higher risk of challenge.
**Flag text:** `⚠️ ATTORNEY REVIEW RECOMMENDED: No CROSS rulings were found for this product or closely analogous goods. Consider requesting a binding ruling from CBP (19 CFR Part 177) before importing.`

### 4. Changing Trade Relations
**Trigger:** Country of origin is subject to active or pending trade policy changes (new tariffs, sanctions, embargoes, trade agreement negotiations).
**Why:** Trade policy changes can alter duty rates, eligibility for preferential programs, or legality of importation with little advance notice.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: The country of origin is subject to active trade policy developments. Duty rates and import eligibility may change. Monitor Federal Register notices and USTR announcements.`

### 5. UFLPA / Forced Labor Concerns
**Trigger:** Product originates from or has supply chain connections to regions flagged under the Uyghur Forced Labor Prevention Act (UFLPA) or other forced labor enforcement actions.
**Why:** UFLPA creates a rebuttable presumption that goods from the Xinjiang Uyghur Autonomous Region (XUAR) are made with forced labor. Importers bear the burden of proof to overcome this presumption.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: This product may be subject to UFLPA enforcement. Goods with supply chain connections to the XUAR face a rebuttable presumption of forced labor. Importer must demonstrate compliance with CBP's operational guidance.`

### 6. Partner Government Agency (PGA) Requirements
**Trigger:** Product is potentially subject to regulation by a Partner Government Agency that enforces requirements at import via PGA message sets in ACE.
**Why:** PGA requirements add import compliance obligations beyond customs classification — including pre-market approval, labeling, testing, and registration. These agencies enforce at the border through CBP's Automated Commercial Environment (ACE).
**Commonly enforced at import via ACE (illustrative, not exhaustive):** FDA, EPA, CPSC, USDA/APHIS, FCC, TTB, ATF, DOT/PHMSA, NMFS, FWS. PGA requirements change — always verify current applicability for the specific product.
**Flag text:** `⚠️ ATTORNEY REVIEW RECOMMENDED: This product may be subject to Partner Government Agency requirements ({agency names}). Verify compliance with applicable PGA regulations before importation.`

### 7. Conflicting CROSS Rulings
**Trigger:** Two or more CROSS rulings reach different classifications for analogous products, and neither has been revoked or modified.
**Why:** Conflicting rulings indicate unsettled classification practice. CBP may classify the product differently depending on the port, the examiner, or the specific facts.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: Conflicting CROSS rulings exist for analogous products. {Ruling A} classifies under {heading X}; {Ruling B} classifies under {heading Y}. Consider requesting an HQ ruling to resolve the conflict.`

### 8. CIT/CAFC Decision Conflicts
**Trigger:** A CIT or CAFC decision undermines, distinguishes, or directly contradicts the CROSS ruling(s) supporting the recommended classification.
**Why:** Judicial decisions override administrative rulings. If a court has ruled against CBP's classification approach, the recommended classification may be vulnerable.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: A CIT/CAFC decision ({case citation}) conflicts with the CROSS ruling(s) supporting this classification. Judicial precedent overrides administrative rulings. Review the decision's impact on this classification.`

### 9. AD/CVD Order Scope Ambiguity
**Trigger:** Product may fall within the scope of an active antidumping or countervailing duty order, but scope coverage is unclear.
**Why:** AD/CVD scope determinations involve complex factual and legal analysis. Incorrect self-classification can result in substantial duty liability and penalties.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: This product may be within the scope of an active AD/CVD order on {product} from {country}. Scope coverage is ambiguous. Consider requesting a scope ruling from the Department of Commerce.`

### 10. Multi-Country Supply Chain Complexity
**Trigger:** Product has a manufacturing process spanning three or more countries, with ambiguous substantial transformation points.
**Why:** Multi-country supply chains create uncertainty in country of origin determination for marking, FTA, TAA, and Section 301 purposes. Different origin conclusions for different purposes can result in compliance failures.
**Flag text:** `⚠️ ATTORNEY REVIEW RECOMMENDED: This product has a multi-country supply chain with potentially ambiguous substantial transformation points. Origin determinations may differ for marking, FTA qualification, TAA compliance, and Section 301 applicability. Professional review of the supply chain is recommended.`

### 11. High-Value or Recurring Importation
**Trigger:** User indicates the transaction involves high value (>$250,000), high volume, or recurring importation.
**Why:** The financial exposure from an incorrect classification increases with value and volume. Binding rulings and professional review become cost-effective risk mitigation.
**Flag text:** `⚠️ ATTORNEY REVIEW RECOMMENDED: Given the value/volume of this importation, professional review and a CBP binding ruling are strongly recommended to mitigate classification risk.`

### 12. Low Classification Confidence
**Trigger:** Classification confidence assessment per
`references/classification-confidence.md` results in Low confidence,
or the controversy detection checklist scores 4+ indicators.
**Why:** Low confidence means genuine ambiguity, split essential
character factors, conflicting authorities, or absence of precedent.
**Flag text:** `⚠️ ATTORNEY REVIEW REQUIRED: This classification has been
assessed as low confidence. {specific reasons}. Professional review and
a CBP binding ruling are strongly recommended before entry.`

### 13. Current Source Or Retrieval Gap
**Trigger:** Current HTS revision, ruling text, court opinion text, AD/CVD order/scope source, Chapter 99 status, or PGA/UFLPA source cannot be retrieved or verified, and the missing source is material to the conclusion.
**Why:** Trade-law conclusions are source- and date-sensitive. A stale rate, expired exclusion, revoked ruling, superseded order, or unretrieved opinion can change the result.
**Flag text:** `⚠️ ATTORNEY/BROKER REVIEW REQUIRED: A material source could not be verified ({source gap}). This conclusion should not be relied on for entry, duty, scope, origin, admissibility, or protest decisions until the current official source is retrieved and reviewed.`

### 14. Missing Material Facts
**Trigger:** Product identity, composition, use, condition as imported, country of origin, manufacturing steps, supplier/facility identity, value, or shipment mode is missing and controls the requested conclusion.
**Why:** Customs outcomes turn on facts. Missing facts can change classification, duty, origin, AD/CVD, PGA, UFLPA, MPF/HMF, or Chapter 99 results.
**Flag text:** `⚠️ HUMAN REVIEW REQUIRED: Material facts needed for this conclusion are missing ({missing facts}). Treat any result as provisional until the facts are confirmed.`

---

## Flag Presentation

When any trigger is activated:

1. **Display the flag prominently** at the top of the relevant section
2. **Explain the specific risk** in plain language
3. **Recommend specific next steps** (binding ruling request, scope ruling, PGA consultation)
4. **Continue the analysis** — the flag does not halt the workflow, it supplements it
5. **Include all triggered flags** in the final deliverable's Risk Factors section
