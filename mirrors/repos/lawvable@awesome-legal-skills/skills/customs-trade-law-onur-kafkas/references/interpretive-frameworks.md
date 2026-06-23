# Interpretive Frameworks for Heading Text Analysis

**Case Attribution Rule:** Do not quote or attribute a specific holding
to a case unless the opinion text (or a reliable secondary source such
as Justia, Google Scholar, or a court website) was retrieved in-session.
If the case was NOT retrieved, describe the doctrine generically and
label case mentions as "commonly cited for [principle]" rather than
asserting exact holdings or quoting language.

---

## Section 1: Heading Type Classification (Apply First)

Before interpreting any heading, classify its type — this determines which evidence and analytical tools are relevant.

### Eo Nomine Headings

An eo nomine heading describes an article by its **common or commercial name** (e.g., "chairs," "gloves," "screws"). These headings have a narrow scope limited to articles commercially known by that name.

**Evidence sources (in order):** dictionaries, trade publications, WCO Explanatory Notes, CBP practice.

**Key principles:**
- An eo nomine designation includes **all forms** of the named article unless section/chapter notes explicitly restrict scope. *Nidec Corp.* is commonly cited for the principle that eo nomine designations include all forms of the named article.
- An eo nomine heading does NOT extend to articles that are not commercially known by the heading's name, even if functionally similar.
- Analysis ends at **common meaning** — once you determine whether the product IS or IS NOT the named article in common commercial understanding, the eo nomine inquiry is complete.

### Use-Based Headings

A use-based heading describes an article by its **function or purpose** (e.g., "machines for working metal," "instruments for measuring"). These headings have broader scope.

**Evidence sources:** principal use of the class or kind (Additional U.S. Rule 1(a), Carborundum factors — see `references/essential-character-doctrine.md` Section 2).

**Key principles:**
- The relevant inquiry is the **principal use of the class or kind** of goods, not the actual use of the specific import.
- Use-based analysis requires applying the Carborundum factors to determine whether the product belongs to the class or kind principally used for the heading's stated purpose.
- Eo nomine analysis ends at common meaning; use-based analysis requires a **principal use inquiry**.

### Mixed/Qualified Headings

A mixed heading combines a name with a use qualifier (e.g., "rubber gloves for surgical use"). Apply eo nomine analysis for the named article, then evaluate the use qualifier.

**Approach:** First determine whether the product IS the named article (eo nomine). If yes, then determine whether it satisfies the use qualification (principal use or actual use depending on the provision's language).

---

## Section 2: Canons of Statutory Construction

Apply these interpretive tools when heading text requires interpretation. Listed roughly from most to least commonly applied.

### 1. Eo Nomine Doctrine

A heading that names an article covers **all forms** of that article. The core question is whether the product IS the named article in its common and commercial meaning. If the heading names the product, classification under that heading is strongly indicated unless a note excludes it or a more specific heading exists.

### 2. Common Meaning Hierarchy

Tariff terms not defined by statute are construed according to their **common and commercial meaning**. *Heartland By-Products v. United States* is commonly cited for establishing the evidence hierarchy for determining common meaning.

**Evidence hierarchy (search in order; first clear answer generally controls):**
1. **Dictionaries** — standard English and technical/trade dictionaries
2. **Trade publications** — industry-specific definitions and usage
3. **WCO Explanatory Notes** — persuasive interpretive aid (see Section 3 below)
4. **CBP practice** — how CBP has interpreted the term in rulings
5. **Expert evidence** — industry expert testimony or declarations

### 3. Ejusdem Generis

A general term following specific terms is limited to the **same kind or class** as the specific terms. When a heading reads "X, Y, Z, and other articles," the word "other" means articles **similar in nature** to X, Y, and Z — not any article whatsoever.

**Application:** Identify the specific terms, determine their common characteristics, then ask whether the product shares those characteristics.

### 4. Noscitur a Sociis

An ambiguous term is interpreted in the **context of surrounding terms** in the same heading or subheading. Words take meaning from their companions.

**Application:** If a term is ambiguous in isolation, look at the other terms in the same heading to determine the intended scope.

### 5. Rule of Relative Specificity (GRI 3(a) Application)

When two headings both describe a product, the heading providing the **more specific description** prevails. A provision describing an article by name prevails over a provision describing it by class. *Avenues in Leather v. United States* is commonly cited for the principle that specificity is assessed by which heading more closely describes the article as a whole, not by comparing isolated elements.

**Application:** Compare candidate headings holistically. The heading that most completely describes the product as imported — considering all its characteristics — is the more specific.

### 6. Expressio Unius Est Exclusio Alterius

The express inclusion of specific items implies the **exclusion of items not mentioned**. If a heading lists specific articles, articles not listed are presumed excluded.

**Application:** When a heading or note lists specific items, do not extend coverage to unlisted items unless the text uses inclusive language ("including but not limited to").

### 7. Contra Proferentem

Ambiguity is resolved **in favor of the importer** (the party against whom the tariff was drafted), resulting in the lower duty rate.

**⚠️ LAST RESORT CANON:** Apply contra proferentem **only after ALL other interpretive tools have been exhausted** and genuine ambiguity remains. This canon is rarely outcome-determinative and should not be used as a shortcut past rigorous analysis.

**⚠️ ATTORNEY REVIEW REQUIRED:** If the classification conclusion depends on contra proferentem to resolve the ambiguity, trigger the attorney review flag per `references/human-review-triggers.md`. A classification resting on this canon alone is inherently fragile.

---

## Section 3: WCO Explanatory Notes Methodology

### Legal Status

WCO Explanatory Notes (ENs) are **persuasive but not binding** authority for interpreting the HTSUS. The CAFC has confirmed that ENs are the "primary persuasive aid" for GRI 1 heading interpretation.

### Scope of Application

- The first **6 digits** of the HTSUS follow the international Harmonized System — ENs directly inform 4-digit heading and 6-digit subheading interpretation.
- **ENs are strongest at heading/6-digit level; use caution extrapolating to U.S.-specific 8-digit subheadings and 10-digit statistical suffixes.** EN reasoning may inform downstream analysis but is not determinative for U.S.-only breaks.

### Authority Hierarchy for ENs

```
HTSUS text > CAFC > CIT > EN > HQ rulings > NY rulings
```

### Integration Protocol

1. **Read the heading text** of each candidate heading.
2. **Search for ENs** on the candidate headings:
   ```
   web_search("WCO Explanatory Notes heading {XXXX} {product}")
   ```
3. **Cite ENs as persuasive support** for heading interpretation.

### Conflict Resolution

- **When EN and CROSS agree:** Cite both for reinforcement.
- **When EN and CROSS disagree:** The EN's position is stronger persuasive authority for heading-level interpretation (ENs sit higher in the hierarchy than CBP rulings).
- **When EN conflicts with CIT/CAFC:** The judicial decision controls.
