# GRI Analysis — General Rules of Interpretation

## Overview

The General Rules of Interpretation (GRI 1-6) are the legally mandated framework for classifying goods under the Harmonized Tariff Schedule. They must be applied **in sequential order** — do not skip to a later GRI unless the preceding ones fail to resolve the classification.

Authority: General Note 3(a), HTSUS; 19 U.S.C. § 1202.

---

## Pre-Analysis: Gather HTS Data

Before applying any GRI, retrieve the necessary data:

1. **Resolve current HTS source record** per `references/hts-data-sources.md`:
   - Discover the latest current-year HTS JSON through Data.gov.
   - Select the highest current-year `HTS Revision N (JSON)`.
   - Record the catalog URL, catalog checked/harvest date if available, selected revision title, JSON URL, analysis date, and source limitations.
   - Use USITC Archive/current pages only as fallback and record the fallback reason.

2. **Query USITC REST API** for candidate headings:
   ```
   web_fetch("https://hts.usitc.gov/reststop/search?keyword={product_term}")
   ```
   Try 2-3 keyword variations (product name, function, material).

3. **Identify candidate 4-digit headings** from results. Look for:
   - Headings that describe the product by name
   - Headings that describe the product by function
   - Headings that describe the product by material
   - Headings that describe the product by end use

4. **Map headings to sections** using `references/section-chapter-map.json`.

5. **Obtain chapter/section notes** — these control the scope of headings under GRI 1:
   - Search: `web_search("HTS chapter {N} notes {topic}")`
   - Or retrieve/recommend the current Chapter PDF from USITC
   - Do not rely on memory for note text

6. **Build hierarchy** for candidate headings with the selected bulk JSON when GRI 6 or parent-child scope matters (use `scripts/hts-hierarchy-builder.py`).

7. **Create evidence ledger entries** per `references/agentic-research-protocol.md` for each source that supports candidate heading selection, note interpretation, and final subheading choice.

**Hard stop:** If current HTS revision cannot be identified, do not make a GRI 6 hierarchy conclusion. Use live REST results only for provisional candidate discovery and state the limitation.

---

## GRI 1: Terms of Headings and Section/Chapter Notes

**Rule:** Classification is determined by the terms of the headings and any relative section or chapter notes.

**Application:**
1. Read the **exact text** of each candidate 4-digit heading.
2. Read all **applicable Section Notes** for the section(s) containing the candidate headings.
3. Read all **applicable Chapter Notes** for the chapter(s) containing the candidate headings.
4. Pay special attention to:
   - **Exclusion notes** (e.g., "This chapter does not cover...")
   - **Definition notes** (e.g., "For the purposes of this chapter, X means...")
   - **Inclusion notes** (e.g., "This heading includes...")
   - **Additional U.S. Notes** (see `references/additional-us-rules.md`)

**Decision:** Does the product fall **clearly and unambiguously** within one heading based on its terms and the notes?
- **YES** → Classification resolved at 4-digit level. Proceed to GRI 6 for subheading determination.
- **NO** → Product fits no heading, or fits multiple headings. Proceed to GRI 2.

**Documentation:** Quote the relevant heading text and note(s). Explain why the product does or does not fit.

### Interpretive Analysis (apply before concluding GRI 1)

Before concluding whether a heading covers the product, apply the
interpretive frameworks in `references/interpretive-frameworks.md`:
1. Classify the heading type (eo nomine vs. use-based vs. mixed) —
   this determines which evidence types are relevant
2. If heading text uses undefined terms, apply the common meaning
   hierarchy (dictionaries → trade publications → EN → CBP practice)
3. Search for WCO Explanatory Notes on the candidate headings —
   ENs are the primary persuasive aid for GRI 1 heading interpretation
4. Apply relevant canons of construction if heading language is
   ambiguous (ejusdem generis, noscitur a sociis, expressio unius)

---

## GRI 2(a): Incomplete, Unfinished, Unassembled, Disassembled

**Rule:** Any reference to an article includes that article incomplete or unfinished, provided it has the essential character of the complete or finished article. Also covers articles presented unassembled or disassembled.

**Application:**
1. Is the product **incomplete or unfinished?**
   - Does it have the **essential character** of the complete article?
   - Would a reasonable person identify it as the article in its incomplete state?
2. Is the product presented **unassembled or disassembled?**
   - Articles shipped knocked-down for convenience of packing or transport are classified as assembled.

**Decision:**
- If the incomplete/unfinished article has essential character of the complete article → classify as the complete article under GRI 1.
- If not → GRI 2(a) does not apply. Proceed to GRI 2(b).

**Key consideration:** GRI 2(a) **expands** the scope of headings, it does not create new headings.

---

## GRI 2(b): Mixtures, Combinations, Composite Goods

**Rule:** Any reference to a material or substance includes that material or substance mixed or combined with other materials or substances. Any reference to goods of a given material includes goods partly of that material. Classification of goods consisting of more than one material is governed by GRI 3.

**Application:**
1. Is the product a **mixture or combination** of materials mentioned in a heading?
2. Is the product **partly** of a material mentioned in a heading?
3. If the product consists of more than one material or component, GRI 2(b) sends you to GRI 3.

**Decision:**
- Single-material mixtures → may be classified under the heading for that material
- Multi-material goods → proceed to GRI 3

---

## GRI 3: Goods Classifiable Under Two or More Headings

**Prerequisite:** The product is prima facie classifiable under two or more headings (after applying GRI 1 and 2).

### GRI 3(a): Most Specific Description

**Rule:** The heading providing the most specific description prevails over a heading providing a more general description.

**Application:**
1. Compare the candidate headings. Which one describes the product more precisely?
2. A heading naming the product is more specific than a heading naming a class.
3. A heading describing the product by its specific function is more specific than one describing it by material.
4. **Caution:** If two headings each refer to part of the materials or components of a composite good, neither is more specific — proceed to GRI 3(b).

For the specificity analysis framework — including the rule of relative
specificity and eo nomine vs. use-based distinction — see
`references/interpretive-frameworks.md` Section 2.

### GRI 3(b): Essential Character

**Rule:** Mixtures, composite goods, sets put up for retail sale — classified by the material or component that gives the good its **essential character**.

**Application — Essential Character Test:**

Consider these factors (from CIT/CAFC case law and EN guidance):
- **Bulk or weight** of the material/component
- **Value** of the material/component relative to the whole
- **Role in the use** of the finished product — which component makes the product what it is?
- **Consumer expectation** — what would a purchaser consider the defining element?
- The Explanatory Notes provide that essential character can be determined by "the nature of the material or component, its bulk, quantity, weight or value, or by the role of a constituent material in relation to the use of the goods."

**Doctrinal Framework:** For the full multi-factor analysis with case law
guidance on factor weighting (Riddell: role in use; Conair: multi-factor
sequencing; Primal Lites: sets), and burden of proof awareness, see
`references/essential-character-doctrine.md` Section 1.

**For retail sets:** The set must consist of at least two different articles classifiable in different headings, put up together for retail sale, to satisfy a particular need or carry out a specific activity.

⚠️ **FLAG: GRI 3(b) essential character disputes are among the most litigated issues in customs law. Always trigger the attorney review flag from `references/human-review-triggers.md` when GRI 3(b) is the dispositive rule.**

### GRI 3(c): Last in Numerical Order

**Rule:** When GRI 3(a) and 3(b) fail, classify under the heading that occurs **last in numerical order** among those equally meriting consideration.

**Application:** This is a rule of last resort within GRI 3. If you reach this point, document why GRI 3(a) and 3(b) were insufficient.

---

## GRI 4: Most Akin

**Rule:** Goods that cannot be classified under GRI 1-3 shall be classified under the heading appropriate to the goods to which they are most akin.

**Application:**
1. This is rare in practice — most goods can be classified under GRI 1-3.
2. Compare the product to goods already classified under various headings.
3. Consider: material, purpose, appearance, trade understanding.
4. "Most akin" is a factual determination based on the totality of characteristics.

---

## GRI 5: Containers and Packing

### GRI 5(a): Specially Shaped Containers
Containers specially shaped or fitted to contain a specific article, suitable for long-term use, presented with the article → classified with the article.

### GRI 5(b): Packing Materials
Packing materials and containers presented with the goods → classified with the goods (unless they are clearly suitable for repetitive use).

---

## GRI 6: Subheading Determination

**Rule:** Classification at the subheading level follows the same principles as GRI 1-5, applied within the resolved 4-digit heading. **Subheadings at the same level are comparable.**

**Application:**
1. Once the 4-digit heading is resolved (via GRI 1-5), look at the subheading structure.
2. Use the current HTS bulk JSON or verified REST/API output to identify the indent hierarchy.
   - Preferred: Data.gov-selected bulk JSON and `scripts/hts-hierarchy-builder.py`.
   - Fallback: REST/API output if it clearly shows the current hierarchy; record the limitation.
   - Treat empty `htsno` rows and `superior: true` rows as hierarchy labels.
3. Apply GRI 1-5 principles **within** the heading to determine the correct subheading.
4. One-dash subheadings (6-digit) are compared to other one-dash subheadings.
5. Two-dash subheadings (8-digit) are compared to other two-dash subheadings under the same parent.
6. U.S. statistical suffixes (10-digit) are determined after the 8-digit subheading.
7. Inspect `footnotes`, `additionalDuties`, and `addiitionalDuties` for Chapter 99 cross-references before carrying the subheading into duty analysis.

**Critical:** You can only compare subheadings at the **same level of indentation**. Do not compare a one-dash subheading with a two-dash subheading.

---

## Documentation Requirements

For every classification, document:

1. **Candidate headings considered** (with heading text quoted)
2. **Which GRI resolved the classification** (GRI 1, 2, 3(a), 3(b), etc.)
3. **Section/Chapter Notes relied upon** (with note text quoted)
4. **Why alternative headings were rejected**
5. **Subheading determination** (GRI 6 analysis with indent-level comparison)
6. **HTS source record:** Data.gov/fallback source, selected revision, JSON URL, analysis date
7. **Evidence ledger:** Sources supporting each material conclusion with evidence labels
8. **Risk assessment:** Flag if multiple GRIs could plausibly apply (per `references/human-review-triggers.md`)
9. **Confidence assessment:** Apply `references/classification-confidence.md`
   to assign High/Moderate/Low confidence and run the controversy
   detection checklist.
