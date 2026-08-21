---
name: customs-trade-compliance
description: "Walks HS/HTS/TARIC classification (GRI 1-6, CROSS/BTI), FTA origin and RVC, hierarchical customs valuation, Incoterms, and restricted-party screening (SDN, Entity List, Denied Persons). Load when opening a new import/export lane, checking duty/FTA/FTZ/drawback, or adjudicating a screening hit. Never classify from a SKU name; not for domestic sales-tax engines or warehouse WMS build-out."
version: 1.0.1
risk: safe
source: https://github.com/ai-evos/agent-skills
date_added: '2026-02-27'
---

## When to Use
Use this skill when you are **planning, auditing, or remediating customs and trade compliance processes**:

- Classifying products (HS/HTS/TARIC), designing documentation flows, or implementing Incoterms for new trade lanes.
- Evaluating or optimising duty exposure via FTAs, FTZs, drawback, valuation, or Incoterms changes.
- Investigating compliance risk, penalty exposure, or restricted‑party screening issues across import/export operations.

## Prerequisites
- Access to relevant customs portals (ACE, CHIEF/CDS, ATLAS) and ERP trade management modules.
- Restricted party screening platform access.
- For detailed decision trees and templates, load the reference files located in `references/`:
  - `references/decision-frameworks.md`: Load when performing classification, FTA qualification, or valuation method selection.
  - `references/edge-cases.md`: Load when handling de minimis, transshipment, dual-use, first sale, retroactive FTA, kits, or temporary imports.
  - `references/communication-templates.md`: Load when drafting broker instructions, prior disclosures, or internal compliance alerts.

## Procedure

### 1. HS Tariff Classification
1. **Identify the good precisely:** Get the full technical specification (material composition, function, dimensions, intended use). Never classify from a product name alone.
2. **Determine the Section and Chapter:** Use Section and Chapter notes to confirm or exclude. Chapter notes override heading text.
3. **Apply GRI 1:** Read heading terms literally. If only one heading covers the good, classification is decided.
4. **Apply GRI 2 & 3 (if GRI 1 fails):** For incomplete articles (GRI 2a), mixtures (GRI 2b), or multiple candidate headings (GRI 3). GRI 3(a) most specific, GRI 3(b) essential character, GRI 3(c) last in numerical order.
5. **Validate at subheading level:** Apply GRI 6. Check subheading notes. Confirm national tariff line (8/10-digit) aligns with 6-digit determination.
6. **Check for binding rulings:** Search CBP CROSS database, EU BTI database, or WCO classification opinions.
7. **Document the rationale:** Record GRI applied, headings considered/rejected, and determining factor.

### 2. FTA Qualification Analysis
1. **Identify applicable FTAs** based on origin and destination.
2. **Determine the product-specific rule of origin** from the relevant FTA's annex.
3. **Trace all non-originating materials** through the bill of materials.
4. **Calculate RVC if required:** Choose the most favourable method (Transaction Value vs Net Cost).
5. **Apply cumulation rules:** (e.g., USMCA accumulation, EU-UK bilateral, RCEP diagonal).
6. **Prepare the certification:** Ensure all prescribed data elements are included (e.g., USMCA 9 elements). Retain supporting docs for 4-5 years.

### 3. Customs Valuation Method Selection
Apply methods in hierarchical order:
1. **Transaction Value (Method 1):** Price paid/payable, adjusted. Used for ~90% of entries.
2. **Identical Goods (Method 2):** Same goods, same origin, same commercial level.
3. **Similar Goods (Method 3):** Commercially interchangeable goods.
4. **Deductive Value (Method 4):** Resale price in importing country minus profit, transport, duties.
5. **Computed Value (Method 5):** Cost of materials, fabrication, profit, general expenses.
6. **Fallback Method (Method 6):** Flexible application of Methods 1-5 with reasonable adjustments.

### 4. Restricted Party Screening
1. **Screen all parties:** Buyer, seller, consignee, end user, freight forwarder, banks, intermediate consignees.
2. **Assess match quality:** Name match %, address correlation, country nexus, alias analysis, DOB.
3. **Verify entity identity:** Cross-reference company registrations, D&B, prior history.
4. **Check list specifics:** SDN (requires OFAC licence), Entity List (BIS licence), Denied Persons (absolute prohibition).
5. **Escalate true positives/ambiguous cases** to compliance counsel immediately.
6. **Document everything:** Tool used, date, match details, adjudication rationale, disposition. Retain 5 years.

## Pitfalls
- **Multi-function devices:** Classify by primary function per GRI 3(b), not by the most expensive component.
- **Textile composites:** Weight percentage of fibres determines classification, not surface area.
- **Software on physical media:** The medium, not the software, determines classification.
- **Incoterms misuse:** Using FOB for containerised ocean freight is technically incorrect (FCA is preferred). Incoterms do not transfer title to goods.
- **DDP circular valuation:** If the seller includes duty in the invoice price, it creates a circular valuation problem.
- **De minimis exploitation:** Multiple shipments on the same day to the same consignee may be aggregated by CBP. Section 321 does not eliminate quota, AD/CVD, or PGA requirements.
- **Transshipment circumventing AD/CVD:** "Substantial transformation" requires a new article of commerce with a different name, character, and use.
- **First sale rule:** US recognises this, but EU and most others do not. Requires demonstrating a bona fide arm's-length transaction.
- **Temporary imports becoming permanent:** If temporary import period expires without export or duty payment, the carnet guarantee is called.

## Verification
To verify compliance processes and outputs:
- **Classification Accuracy:** Cross-check HS code against CBP CROSS or EU BTI databases. Ensure GRI rationale is documented.
- **Documentation Completeness:** Verify Commercial Invoice contains all 19 CFR § 141.86 elements (seller/buyer, description, quantity, value, currency, Incoterms, origin, payment terms).
- **FTA Claims:** Confirm RVC calculation method and trace non-originating materials in BOM. Verify certification contains required data elements.
- **Screening Logs:** Ensure 5-year retention of screening results, including false positive adjudication rationale.
- **Record-keeping:** Confirm 5-year retention (US per 19 USC § 1508) or 3-10 years (EU) for all entry records.
- **Performance Metrics:** Check that classification accuracy is >98%, FTA utilisation >90%, entry rejection <2%, and CBP examination rate <3%.

## Escalation Protocols
- **CBP detention/seizure:** Notify VP and legal counsel within 1 hour.
- **Restricted party true positive:** Halt transaction, notify compliance officer and legal immediately.
- **Potential penalty > $50,000:** Notify VP Trade Compliance and General Counsel within 2 hours.
- **AD/CVD evasion investigation:** Retain outside trade counsel within 24 hours.
- **Voluntary self-disclosure:** Legal counsel approval required before filing.
