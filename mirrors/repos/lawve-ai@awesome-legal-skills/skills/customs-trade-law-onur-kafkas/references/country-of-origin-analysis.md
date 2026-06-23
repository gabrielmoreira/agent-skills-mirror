# Country of Origin Analysis

## Overview

Country of origin is determined differently depending on the purpose. This methodology covers three origin analyses that may apply to a single import:

1. **Marking origin** — What must the product be marked? (19 CFR Part 134)
2. **FTA origin** — Does the product qualify for preferential rates? (FTA-specific rules)
3. **TAA origin** — Is the product eligible for government procurement? (Trade Agreements Act)

Before reaching a conclusion, map all countries, processing steps, supplier/facility facts if known, and the purpose of the origin determination. Create evidence ledger entries per `references/agentic-research-protocol.md`.

---

## 1. Marking Rules (19 CFR Part 134)

### Legal Framework
- Authority: 19 U.S.C. § 1304; 19 CFR Part 134
- Requirement: Every article of foreign origin imported into the U.S. must be marked with its country of origin
- The marking must be **conspicuous**, **legible**, **indelible**, and **permanent**

### Substantial Transformation Test
The country of origin for marking is the country where the article underwent its **last substantial transformation** — a manufacturing process that transforms the article into a new and different article of commerce, with a new name, character, or use.

**Analysis steps:**
1. Map the manufacturing process across all countries involved
2. Identify where the article achieves its **essential character** or **final identity**
3. Ask: At which stage does a "new and different article of commerce" emerge?
4. The country where that transformation occurs is the marking origin

**Search for CBP guidance:**
```
web_search("CBP country of origin marking {product type}")
web_search("19 CFR 134 substantial transformation {product}")
web_fetch("https://rulings.cbp.gov/search?term=country+of+origin+{product}&collection=ALL&commodityGrouping=ALL&sortBy=DATE_DESC&pageSize=30&page=1")
```

### Special Rules
- **USMCA marking rules:** For goods from Canada/Mexico, specific USMCA marking rules may apply (19 CFR Part 102)
- **Textile/apparel:** Special origin rules under 19 CFR § 102.21
- **Pipes and fittings:** Specific substantial transformation rules
- **Assembled products:** Assembly operations may or may not constitute substantial transformation depending on complexity

### Exceptions to Marking
Certain articles are exempt from individual marking requirements (19 CFR § 134.32):
- Articles incapable of being marked
- Articles that would be injured by marking
- Crude substances
- Articles imported for the importer's own use (not resale)

---

## 2. FTA Rules of Origin

### General Framework
Each FTA has its own rules of origin that must be met for preferential tariff treatment. Common origin criteria include:

**A. Wholly Obtained or Produced**
- Products entirely grown, mined, harvested, or produced in an FTA country
- No non-originating materials

**B. Tariff Shift Rule**
- The product undergoes a specified change in tariff classification (at the chapter, heading, or subheading level) as a result of production in the FTA country
- Example: A rule requiring a "change to heading 6204 from any other chapter" means the input materials must come from outside Chapter 62

**C. Regional Value Content (RVC)**
- A minimum percentage of the product's value must originate in the FTA region
- Two calculation methods are common:
  - **Transaction value method:** RVC = (TV - VNM) / TV × 100
  - **Net cost method:** RVC = (NC - VNM) / NC × 100
- Where TV = transaction value, NC = net cost, VNM = value of non-originating materials

**D. Specific Processing Rules**
- Some FTAs require specific manufacturing operations (e.g., chemical reaction, dyeing, printing)

### USMCA (Canada/Mexico) — Key Provisions
```
web_search("USMCA rules of origin {HTS heading} tariff shift")
web_search("USMCA regional value content {product type}")
```
- Requires USMCA certificate of origin
- Automotive rules: Specific labor value content and steel/aluminum purchasing requirements
- De minimis: Generally 10% of transaction value for non-originating materials

### Other Active FTAs
Use `references/fta-program-codes.json` to identify applicable FTAs. Then:
```
web_search("{FTA name} rules of origin {HTS chapter} rule")
web_search("{FTA name} product-specific rule {heading}")
```

### Documentation
- FTA certificates of origin (format varies by agreement)
- Importer's knowledge/declaration
- Maintain records of origin determination for 5 years

---

## 3. Trade Agreements Act (TAA) — Government Procurement

### Legal Framework
- Authority: 19 U.S.C. § 2511-2518
- Applies to: U.S. government procurement (federal agencies must buy TAA-compliant products)
- Administered by: General Services Administration (GSA)

### TAA Substantial Transformation Test
Similar to marking origin but applied specifically for government procurement eligibility:

1. The product must be manufactured or substantially transformed in a **TAA-designated country**
2. TAA-designated countries include: U.S., FTA partners, WTO GPA countries, Caribbean Basin countries, and least-developed countries
3. **China is NOT a TAA-designated country** — products of Chinese origin are not TAA-compliant

### TAA Analysis Steps
1. Determine where the product was **substantially transformed** (same test as marking origin)
2. Check if that country is on the **TAA-designated country list**
3. If substantially transformed in a non-designated country → not TAA-compliant
4. If substantially transformed in a designated country → TAA-compliant

```
web_search("TAA designated country list {current_year}")
web_search("TAA substantial transformation {product} {country}")
web_search("Trade Agreements Act compliance {product type}")
```

### Common TAA Issues
- Products assembled in a TAA-designated country from Chinese components: TAA-compliant only if the assembly constitutes substantial transformation
- Mixed-origin supply chains: Analyze where the last substantial transformation occurs
- Software/IT products: Physical manufacturing location controls, not where software was written

---

## Multi-Country Supply Chain Analysis

For products with complex, multi-country supply chains:

### Step 1: Map the Supply Chain
Document each manufacturing step and the country where it occurs:
```
Country A: Raw materials extracted/produced
Country B: Components manufactured
Country C: Sub-assemblies produced
Country D: Final assembly and finishing
```

### Step 2: Identify Transformation Points
At each step, assess whether a substantial transformation occurs:
- Does the operation create a "new and different article of commerce"?
- Does the article receive a new name, character, or use?
- Is the operation more than simple assembly, packaging, or testing?

### Step 3: Determine Origin for Each Purpose
- **Marking:** Country of last substantial transformation
- **FTA:** Apply the specific FTA's rules of origin (tariff shift, RVC, etc.)
- **TAA:** Country of last substantial transformation — must be TAA-designated

### Step 4: Flag Complexities
Trigger `references/human-review-triggers.md` flags for:
- Multi-country supply chains with ambiguous transformation points
- Products from countries under changing trade relations
- UFLPA risk (supply chain connections to Xinjiang)
- Missing supplier/facility identity where UFLPA or PGA admissibility depends on supply-chain facts

---

## UFLPA / Forced Labor Overlay

Run this screen when origin, supply chain, product type, or user request suggests forced-labor risk:

1. Identify all countries, regions, suppliers, manufacturers, and raw-material sources provided.
2. Check official CBP/DHS UFLPA guidance, UFLPA Entity List materials, and WRO sources.
3. Treat XUAR links, listed entities, cotton, polysilicon, tomato products, and other priority sectors as elevated risk.
4. If supplier/facility data is missing, do not clear the product. State the gap and trigger human review when risk cannot be excluded.

---

## PGA Origin-Linked Screen

Some origin conclusions interact with PGA admissibility or documentation:

- Agriculture, plants, animals: USDA/APHIS and country-specific admissibility.
- Food, drugs, cosmetics, medical devices: FDA import requirements.
- Wildlife/fishery products: FWS/NMFS and protected species requirements.
- Chemicals, vehicles, engines, pesticides: EPA and DOT/NHTSA/PHMSA rules.

Use official PGA sources and present potential applicability as a flag unless the product facts are complete enough to rule it out.

---

## Output Format

Present origin analysis as:

```
COUNTRY OF ORIGIN ANALYSIS
Product: {description}
Supply Chain: {Country A → Country B → Country C}

| Purpose | Origin | Basis | Country Status |
|---------|--------|-------|----------------|
| Marking (19 CFR 134) | {Country} | Substantial transformation at {step} | N/A |
| FTA ({program}) | {Country} | {Tariff shift / RVC / specific rule} | {Eligible/Not eligible} |
| TAA (Gov. Procurement) | {Country} | Substantial transformation at {step} | {Designated/Not designated} |
| Section 301 | {Country} | Origin for tariff purposes | {Subject/Not subject} |
```

Add a compact evidence/freshness block listing the official sources used, retrieval date, source label, and unresolved supplier/facility gaps.
