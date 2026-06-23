# CIT/CAFC Court Information

## Court of International Trade (CIT)

### Jurisdiction
**Statutory authority:** 28 U.S.C. § 1581

| Subsection | Jurisdiction | Relevance |
|------------|-------------|-----------|
| § 1581(a) | Protests of CBP decisions (classification, valuation, rate of duty, origin) | **Primary** — most tariff classification cases |
| § 1581(b) | Petitions by domestic interested parties (AD/CVD) | AD/CVD matters |
| § 1581(c) | AD/CVD determinations by Commerce or ITC | AD/CVD judicial review |
| § 1581(d) | Eligibility determinations (GSP, CBERA, AGOA) | Trade preference cases |
| § 1581(i) | Residual jurisdiction (any civil action against the U.S. arising from import transactions) | Catch-all |

**For classification work, filter for § 1581(a) cases.**

### Location and Structure
- Sole Article III court for international trade matters
- Located: New York City (One Federal Plaza)
- Nine judges appointed by the President and confirmed by the Senate
- Cases tried by a single judge (no jury)
- Appeals go to the U.S. Court of Appeals for the Federal Circuit (CAFC)

### Standards of Review
| Basis of Suit | Standard | Practical Meaning |
|--------------|----------|-------------------|
| § 1581(a) protest | De novo on law; presumption of correctness for CBP classification | CIT reviews the law independently but gives weight to CBP's factual findings |
| § 1581(c) AD/CVD | Substantial evidence on the record | More deferential — was there enough evidence to support Commerce/ITC? |

**For classification cases (§ 1581(a)):**
- The court reviews the **legal question** de novo (independently)
- CBP's classification carries a **presumption of correctness** — the importer bears the burden of proving it wrong
- The court examines the GRI analysis, heading text, section/chapter notes, and relevant authorities
- The court may consider Explanatory Notes (WCO) as persuasive (not binding) authority

### CIT Slip Opinions
- Published on: `https://www.cit.uscourts.gov/content/slip-opinions-{YYYY}`
- Format: Slip Op. YY-## (e.g., Slip Op. 25-10)
- Includes: opinion number, caption, date, docket number, judge, jurisdiction code
- Opinion PDFs available but binary — cannot be read via web_fetch

---

## Court of Appeals for the Federal Circuit (CAFC)

### Role in Trade Law
- Hears all appeals from the CIT
- CAFC decisions on trade classification are **binding** on the CIT and CBP
- CAFC decisions are the **highest judicial authority** on tariff classification (Supreme Court rarely takes certiorari on classification cases)

### Key CAFC Doctrines for Classification

**1. Jarvis Clark Standard (en banc)**
- CAFC's framework for applying the GRI hierarchy
- GRI must be applied in numerical order; do not skip to a later GRI

**2. Essential Character Tests**
- CAFC has articulated factors for GRI 3(b) essential character:
  - Bulk, quantity, weight, value
  - Role of constituent material in the use of the goods
  - Nature of the material or component
- See: *Conair Corp. v. United States*, *Alcan Food Packaging v. United States*

**3. Eo Nomine vs. Use Provisions**
- *eo nomine* = a provision describing articles by specific name
- Use provisions describe articles by their function/purpose
- When both could apply, the analysis depends on specificity under GRI 3(a)

**4. Common Meaning Doctrine**
- Tariff terms not defined by statute are construed according to their common and commercial meaning
- Sources: dictionaries, trade publications, prior CBP practice, Explanatory Notes

### Citation Format
- Published: `[Party] v. United States, [Vol.] F.3d/F.4th [Page] (Fed. Cir. [Year])`
- Unpublished/nonprecedential: Note the status — nonprecedential CAFC opinions are informative but not binding

---

## Authority Hierarchy (Enforced)

```
HTSUS legal text (heading terms, section notes, chapter notes, Additional U.S. Rules, GRIs)
  — the statute is the primary authority; everything below interprets and applies it

  > CAFC decisions (binding interpretation; controlling on CIT and CBP)
    > CIT decisions (binding on the parties and entries at issue;
      strong persuasive authority; CBP generally conforms absent contrary CAFC)
      > HQ rulings (Headquarters — national scope, complex matters)
        > NY rulings (New York — routine, port-level classifications)
          > Informed Compliance Publications (CBP guidance, not binding)
```

The HTSUS text and GRIs are the law. Courts and CBP interpret and apply that law. A judicial decision does not override the statute — it interprets it. When a decision appears to conflict with heading text, the decision is construing the statutory language in light of the specific facts.

### Practical Implications
1. **If a CAFC decision addresses the classification issue** → it controls, regardless of what CROSS rulings say
2. **If a CIT decision addresses it (with no CAFC appeal)** → it is strong authority; CBP generally conforms absent contrary CAFC ruling
3. **If only CROSS rulings exist** → HQ rulings carry more weight than NY rulings
4. **If a CROSS ruling conflicts with a court decision** → the court decision prevails

---

## Key Trade Classification Cases (Landmark Decision Frameworks)

### *Jarvis Clark Co. v. United States* — CAFC (en banc)
**Issue:** GRI framework — sequential application
**Framework:** The GRI must be applied in strict numerical order. Do not skip to a later GRI unless the preceding ones fail to resolve the classification. This is the structural foundation for all classification analysis.
**Applied in:** `references/gri-analysis.md` — the sequential GRI structure follows this mandate.

### *Riddell, Inc. v. United States* — CAFC (2007)
**Issue:** GRI 3(b) — essential character factor weighting
**Framework:** The component giving an article its identity and purpose in use determines essential character, even when that component is not the heaviest or most expensive. Role in use is a strong tiebreaker when quantitative factors (weight, value) conflict.
**Applied in:** `references/essential-character-doctrine.md` Section 1 — factor conflict resolution.

### *Conair Corp. v. United States* — CIT (2005)
**Issue:** GRI 3(b) — multi-factor essential character analysis
**Framework:** No single essential character factor is automatically dispositive. Courts require reasoned analysis documenting all factors and explaining the weighting. Conclusory assertions are insufficient.
**Applied in:** `references/essential-character-doctrine.md` Section 1 — documentation requirements for factor analysis.

### *Heartland By-Products v. United States* — CIT/CAFC
**Issue:** GRI 1 — common meaning of tariff terms
**Framework:** Tariff terms not defined by statute are construed according to common and commercial meaning. Evidence hierarchy: dictionaries → trade publications → WCO Explanatory Notes → CBP practice → expert evidence.
**Applied in:** `references/interpretive-frameworks.md` Section 2 — common meaning hierarchy.

### *Avenues in Leather v. United States* — CAFC
**Issue:** GRI 3(a) — specificity test
**Framework:** Specificity under GRI 3(a) is assessed holistically — which heading more closely describes the article as a whole, considering all its characteristics. Do not compare isolated elements.
**Applied in:** `references/interpretive-frameworks.md` Section 2 — rule of relative specificity.

### *Orlando Food Corp. v. United States* — CAFC
**Issue:** Country of origin — substantial transformation
**Framework:** Substantial transformation three-part test: does the processing result in a new and different article with a distinct (1) name, (2) character, and (3) use? All three factors are considered but need not all be satisfied.
**Applied in:** `references/country-of-origin-analysis.md` — substantial transformation analysis.

### *Mead Corp. v. United States* — CAFC
**Issue:** Additional U.S. Rule 1(c) — scope of "parts" provisions
**Framework:** Two-step parts analysis: (1) Is the article solely or principally used as a part of the identified article? (2) A specific provision for the part itself prevails over a general "parts" provision. The specific-provision override prevents over-broad parts classification.
**Applied in:** `references/additional-us-rules.md` — Additional U.S. Rule 1(c) analysis.

### *United States v. Carborundum Co.* — CCPA (1976)
**Issue:** Additional U.S. Rule 1(a) — principal use determination
**Framework:** Six-factor test for principal use: (1) general physical characteristics, (2) expectation of ultimate purchasers, (3) channels of trade, (4) environment of sale, (5) use in same manner as merchandise already fitting the provision, (6) economic practicality of the use. The test applies to the class or kind, not the specific import.
**Applied in:** `references/essential-character-doctrine.md` Section 2 — Carborundum factors framework.

---

## Accessing CIT/CAFC Decisions

| Source | Method | Content Available |
|--------|--------|-------------------|
| CIT slip opinions index | `web_fetch` on CIT website | Case list (no opinion text) |
| Justia case law | `web_search` with `site:law.justia.com` | Full case text (most cases) |
| Google Scholar | `web_search` for case name | Case text and citing references |
| CAFC opinions | `web_search` for case name + "Federal Circuit" | Published opinions |
| Westlaw/Lexis | Not accessible via web_search | Full reporters (attorney access required) |
