# CIT/CAFC Decision Analysis — Trade-Lawyer Assessment Protocol

## Overview

This methodology defines how to search for, analyze, and assess Court of International Trade (CIT) and Court of Appeals for the Federal Circuit (CAFC) decisions like a trade lawyer. The goal is not just to find decisions — it is to understand their **impact on practice**, **strategic implications**, and **position in the precedent landscape**.

---

## Scope Discipline

- Analyze **exactly** the decisions the user asks for — no extras.
- If the user says "latest 3," that means the 3 most recent slip opinions from the index — not 3 plus bonus research on related topics.
- Do **not** add related topics, adjacent litigation, IEEPA analysis, or background research the user did not request.
- Do **not** launch extra agents or research threads beyond what is needed to fulfill the stated request.

---

## Phase 1: Decision Search

### Source Priority Protocol

Sources are **not** co-equal. Follow this strict priority order:

**1. CIT Slip Opinions Index** — to identify which decisions exist
```
web_fetch("https://www.cit.uscourts.gov/content/slip-opinions-{YYYY}")
```
- Scan for cases involving the relevant HTS heading(s)
- Filter by jurisdiction code: `1581(a)` for classification cases
- This gives case metadata: slip opinion number, caption, date, docket, judge

**2. PDF Text Extraction — THIS IS THE PRIMARY SOURCE**
```
bash: python3 scripts/cit-opinion-fetcher.py {slip-op-number}
```
- Example: `python3 scripts/cit-opinion-fetcher.py 26-11`
- Downloads the PDF from `cit.uscourts.gov` and extracts full text using pymupdf
- Read the actual opinion. All analysis must be based on the court's opinion text.
- This is the authoritative source — do not skip this step.
- Label opinion text **Retrieved** when full text is extracted. Label it **Verified** when the citation, date, docket/slip number, and subsequent history/current status are checked against official sources.

**3. Fallback Sources** — only if the PDF reader is unavailable
```
web_search("site:law.justia.com Court International Trade {HTS heading} classification")
web_search("Court of International Trade {HTS heading} classification")
web_search("CAFC {product type} HTS classification appeal")
web_search("{product} v. United States tariff classification")
```
- Use Justia or Google search **only** as a fallback when direct PDF fetch fails.
- These are secondary sources, not starting points.

### Decision Selection Criteria

Prioritize decisions that are:
1. **On point:** Involving the same or similar HTS heading(s)
2. **Recent:** More recent decisions better reflect current legal standards
3. **Binding:** CAFC decisions over CIT decisions
4. **Published:** Published decisions over unpublished/nonprecedential
5. **Classification-specific:** § 1581(a) cases, not AD/CVD or other jurisdictions

---

## Phase 2: Decision Summarization

> **Source Discipline:** All analysis must be based on the court's opinion text. Do not cite or rely on news articles, blog posts, law firm commentary, or magazine coverage as sources for the court's reasoning or holding. If you cannot access the opinion text directly, state that limitation explicitly rather than substituting secondary commentary.

> **Money Quote Rule:** Do not include a "money quote" unless the opinion text was retrieved. If only metadata or a secondary summary is available, label the decision Identified or Unverified and do not attribute holdings beyond what the retrieved source supports.

For each relevant decision found, extract and synthesize:

### A. Case Information
- **Caption:** Full case name (e.g., *Acme Corp. v. United States*)
- **Court:** CIT or CAFC
- **Date:** Decision date
- **Docket/Slip Op.:** Docket number and/or slip opinion number
- **Judge:** Presiding judge (for CIT)
- **Jurisdiction:** § 1581 subsection
- **Procedural posture:** Trial, summary judgment, appeal from CIT

### B. Factual Background
- **Product at issue:** Description of the imported merchandise
- **Classification dispute:** What heading did the importer propose vs. what CBP classified?
- **Key physical/functional characteristics** relied on by the court

### C. Legal Framework
- **GRI(s) applied:** Which General Rule(s) resolved the case
- **Section/Chapter Notes cited:** Specific notes the court relied on
- **Explanatory Notes cited:** WCO Explanatory Notes referenced
- **Key legal test applied:** (e.g., essential character, common meaning, principal use)

### D. Court's Analysis
- **Step-by-step reasoning:** How the court worked through the GRI analysis
- **Dispositive finding:** What factual or legal determination decided the case
- **The "money quote":** The key sentence or passage a practitioner would cite

### E. Holding
- **Classification determined:** The HTS subheading the court found correct
- **Which party prevailed:** Importer or government
- **Scope of ruling:** Does it apply narrowly to the specific product, or broadly to a product category?

### F. Evidence Record
- **Opinion source:** Official PDF URL or fallback source
- **Evidence label:** Verified / Retrieved / Identified / Unverified
- **Retrieval date**
- **Subsequent history checked:** yes/no and source
- **Limitations:** unavailable full text, unclear appeal status, nonprecedential status, etc.

---

## Phase 3: Impact Assessment

After summarizing, assess the decision's impact on practice:

### A. Effect on Classification Practice
- How does this decision affect classification of **similar products**?
- Does it **narrow** or **expand** the scope of a heading/subheading?
- Does it establish a **new test** or refine an existing one?
- Does it **clarify ambiguity** in heading text or notes?

### B. CROSS Ruling Alignment
- Which existing CROSS rulings does this decision **reinforce**?
- Which CROSS rulings does it **undermine or distinguish**?
- Should CBP revoke or modify any rulings in light of this decision?
- Are there outstanding rulings that are now inconsistent with the court's reasoning?

### C. Practical Scope
- Does the decision apply only to the **specific product** before the court?
- Or does it establish a **principle** applicable to a broader category?
- Could it be used as authority in disputes over **related products**?

---

## Phase 4: Strategic Analysis

Provide trade-lawyer strategic assessment:

### A. Client Advisory
- What should **importers of similar goods** do now?
- Should existing entries be **reviewed** for potential reclassification?
- Should **protests be filed** on past entries under the old classification?
- Should **prior disclosures** be made if entries were filed at the wrong rate?
- Does the decision create an opportunity for **reclassification at a lower rate**?

### B. Litigation Outlook
- Is the decision likely to be **appealed** (CIT → CAFC)?
- If a CAFC decision, is it likely to be **reconsidered en banc** or taken by the Supreme Court?
- What are the **odds of reversal** on appeal? (Consider: clarity of reasoning, factual record, applicable standard of review)
- Is this an **outlier** among CIT judges, or does it reflect the court's consensus?

### C. CBP Response
- Will CBP likely **acquiesce** to this decision?
- Will CBP issue new CROSS rulings consistent with the decision?
- Will CBP limit the decision to its **specific facts** (as it often does)?

---

## Phase 5: Precedent Mapping

Position the decision in the broader precedent landscape:

### A. Line of Cases
- What **prior decisions** does the court cite and follow?
- Does the decision **follow**, **distinguish**, or **depart** from prior CIT/CAFC authority?
- Does it **resolve** a split among CIT judges on this issue?
- Does it create a **new split** or diverge from another judge's approach?

### B. Unresolved Questions
- What issues does the court **not reach** or **leave open**?
- What **factual variations** might lead to a different result?
- What **future cases** could test or extend this decision's principles?

### C. Trend Analysis
- Is the court trending toward a **broader or narrower** interpretation of the heading?
- Is there a pattern in how the court applies GRI 3(b) essential character to this product type?
- Are there emerging **tensions** between CIT judges on classification methodology?

---

## Cross-Reference with Classification Workflow

When CIT analysis is performed as part of a classification (Workflow 1, Step 5):

1. **Search for decisions** on each candidate HTS heading
2. **Filter** for § 1581(a) classification cases
3. **Cross-reference** findings with CROSS ruling research:
   - Do court decisions support the same classification as the CROSS rulings?
   - If not, flag the conflict (per `references/human-review-triggers.md`)
4. **Adjust confidence** in the recommended classification based on judicial support:
   - CAFC support → high confidence
   - CIT support (no appeal) → moderate-high confidence
   - No judicial precedent → confidence depends on CROSS ruling consistency
   - Adverse judicial precedent → flag for attorney review
5. **Include** relevant decisions in the classification memo

---

## Output

Generate the assessment using `templates/cit-decision-brief.md`.

Append an evidence ledger for each decision and each material proposition when the analysis is used in a classification, ruling, or compliance deliverable.
